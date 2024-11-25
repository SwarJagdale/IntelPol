import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from minio import Minio
import pickle
from io import BytesIO
from google.cloud import bigquery

# MinIO client setup
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

model_bucket_name = "models"

def incrementally_train_model():
    try:
        # BigQuery client setup
        client = bigquery.Client.from_service_account_json("servicekey.json")

        # Pull data from BigQuery
        query = """
        SELECT Date_Occ, COUNT(*) AS Occurrences
        FROM `drilldown-439515.bdeminiproject.master`
        GROUP BY `Date Occ`
        ORDER BY `Date Occ` ASC
        """
        query_job = client.query(query)
        data = query_job.result().to_dataframe()

        # Ensure 'Date_Occ' is a datetime type and sort the data
        data['Date_Occ'] = pd.to_datetime(data['Date_Occ'])
        data.sort_values(by='Date_Occ', inplace=True)

        # Load the existing ARIMA model from MinIO
        try:
            model_data = minio_client.get_object(model_bucket_name, "ARIMA_MODEL_LATEST")
            model = pickle.load(BytesIO(model_data.read()))
        except Exception as e:
            print(f"No existing model found. Creating a new one: {e}")
            model = None

        # Prepare data for training
        occurrences = data['Occurrences'].values

        # If a model exists, update it incrementally
        if model:
            print("Updating existing model...")
            model = model.append(occurrences, refit=True)
        else:
            # Create and fit a new ARIMA model
            print("Creating a new ARIMA model...")
            model = ARIMA(occurrences, order=(5, 1, 0))
            model = model.fit()

        # Save the updated model back to MinIO
        model_buffer = BytesIO()
        pickle.dump(model, model_buffer)
        model_buffer.seek(0)
        minio_client.put_object(
            model_bucket_name,
            "ARIMA_MODEL_LATEST",
            model_buffer,
            length=model_buffer.getbuffer().nbytes,
        )
        minio_client.put_object(
            model_bucket_name,
            f"ARIMA_MODEL_{data['Date_Occ'].max().strftime('%Y-%m-%d')}",
            model_buffer,
            length=model_buffer.getbuffer().nbytes,
        )

        print("Model training completed and saved to MinIO.")

    except Exception as e:
        print(f"Error during model training: {e}")
