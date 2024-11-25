from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from minio import Minio
import pickle
from io import BytesIO
from google.cloud import bigquery

import os
import telebot
from pyspark.sql import SparkSession
# Define your BigQuery query as a string
QUERY = """
    SELECT * FROM `your_project.your_dataset.your_table` LIMIT 10
"""



def load_data(**kwargs):
    # Simulate loading data
    print("Loading training data...")

def preprocess_data(**kwargs):
    print("Preprocessing data...")

def train_model(**kwargs):
    
    print("Training model...")
    spark = SparkSession.builder.master("local").appName("ModelTraining").getOrCreate()
    print("Model training completed.")

def save_model(**kwargs):
    print("Saving the model...")

def send_telegram_message():
    bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")
    bot.send_message(chat_id="6495459701", text="Model retraining completed!")
    bigquery_task()


def bigquery_task(**kwargs):
    bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
    client = bq_hook.get_client()
    bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")
    result = client.query(QUERY)
    for row in result:
        bot.send_message(chat_id="6495459701", text=str(row))
        break
    
    
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

bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")




def incrementally_train_model():
    client = bigquery.Client.from_service_account_json("servicekey.json")
    bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")
    try:
        # BigQuery client setup
        
        # Pull data from BigQuery
        query = query = """
SELECT `Date Occ`, COUNT(*) AS Occurrences
FROM `drilldown-439515.bdeminiproject.master`
WHERE `Date Occ` >= DATE(TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR))
GROUP BY `Date Occ`
ORDER BY `Date Occ` ASC;
"""

        query_job = client.query(query)
        data = query_job.result().to_dataframe()

        # Ensure 'Date_Occ' is a datetime type and sort the data
        data['Date Occ'] = pd.to_datetime(data['Date Occ'])
        data.sort_values(by='Date Occ', inplace=True)
        
        # Load the existing ARIMA model from MinIO
        try:
            model_data = minio_client.get_object(model_bucket_name, "ARIMA_MODEL_LATEST")
            model = pickle.load(BytesIO(model_data.read()))
        except Exception as e:
            bot.send_message(chat_id="6495459701", text=f"No existing model found. Creating a new one. Error: {e}")
            print(f"No existing model found. Creating a new one: {e}")
            model = None

        # Prepare data for training
        occurrences = data['Occurrences'].to_numpy(dtype='int64')

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
            f"ARIMA_MODEL_{data['Date Occ'].max().strftime('%Y-%m-%d')}",
            model_buffer,
            length=model_buffer.getbuffer().nbytes,
        )

        print("Model training completed and saved to MinIO.")
        
        
        bot.send_message(chat_id="6495459701", text="Model retraining completed finally!")
        

    except Exception as e:
        print(f"Error during model training: {e}")
        bot.send_message(chat_id="6495459701", text=f"Error during model training: {str(e)}")


# Define the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 11, 1),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="incremental",
    default_args=default_args,
    schedule_interval=timedelta(seconds=120),
    catchup=False,
) as dag:

    # task_load_data = PythonOperator(
    #     task_id="load_data",
    #     python_callable=load_data,
    # )

    # task_preprocess_data = PythonOperator(
    #     task_id="preprocess_data",
    #     python_callable=preprocess_data,
    # )

    # task_train_model = PythonOperator(
    #     task_id="train_model",
    #     python_callable=train_model,
    # )

    # task_save_model = PythonOperator(
    #     task_id="save_model",
    #     python_callable=save_model,
    # )

    # task_send_telegram_message = PythonOperator(
    #     task_id="send_telegram_message",
    #     python_callable=send_telegram_message,
    # )

    # Add BigQuery task to your DAG
    task_bigquery = PythonOperator(
        task_id='run_bigquery_query',
        python_callable=bigquery_task,
    )
    
    task_incrementally_train_model = PythonOperator(
        task_id="incrementally_train_model",
        python_callable=incrementally_train_model,
    )
#task_load_data >> task_preprocess_data >> task_train_model >> task_save_model >> task_send_telegram_message >>
    task_incrementally_train_model
