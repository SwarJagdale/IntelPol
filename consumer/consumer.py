# import os
# import json
# import time
# from kafka import KafkaConsumer
# from google.cloud import bigquery
# from minio import Minio
# from datetime import datetime
# import pandas as pd
# time.sleep(5)

# # Set the Google application credentials environment variable
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "drilldown-439515-062f7705dec7.json"

# # Initialize BigQuery client
# client = bigquery.Client()

# # Initialize MinIO client
# minio_client = Minio(
#     "minio:9000",
#     access_key="minioadmin",
#     secret_key="minioadmin",
#     secure=False
# )

# # Kafka Consumer setup
# consumer = KafkaConsumer(
#     'file_uploaded',
#     bootstrap_servers=['kafka:9092'],
#     auto_offset_reset='latest',  # Start from the earliest message
#     enable_auto_commit=False,       # Manually commit offset
#     group_id='file-processing-group'
# )

# print("Consumer initialized")

# # Define your BigQuery table information
# dataset_id = "bdeminiproject"  # Replace with your BigQuery dataset
# table_id = "master"      # Replace with your BigQuery table

# def upload_row_to_bigquery(row):
#     table_ref = client.dataset(dataset_id).table(table_id)
#     rows_to_insert = [
#         {
#             "Area": int(row["Area"]),
#             "Rpt Dist No": int(row["Rpt Dist No"]),
#             "Part 1-2": int(row["Part 1-2"]),
#             "Crm Cd": int(row["Crm Cd"]),
#             "Vict Age": int(row["Vict Age"]),
#             "Premis Cd": int(row["Premis Cd"]),
#             "Weapon Used Cd": int(row["Weapon Used Cd"]),
#             "Crm Cd 1": int(row["Crm Cd 1"]),
#             "Crm Cd 2": int(row["Crm Cd 2"]),
#             "Lat": float(row["Lat"]),
#             "Lon": float(row["Lon"])
#         }
#     ]
    
#     errors = client.insert_rows_json(table_ref, rows_to_insert)
#     if errors:
#         print(f"Errors while inserting rows: {errors}")
#     else:
#         print("Row inserted successfully.")

# def process_file(file_id, filename):
#     try:
#         # Retrieve the file from MinIO
#         response = minio_client.get_object("csv-uploads", filename)
        
#         # Read file content into a DataFrame
#         df = pd.read_csv(response)

#         # Check if the DataFrame is empty
#         if df.empty:
#             print("File is empty or has no readable columns.")
#             return

#         # Iterate through each row and upload it to BigQuery
#         for _, row in df.iterrows():
#             upload_row_to_bigquery(row)
#         response.close()
#         response.release_conn()
#         print("File processing complete.")
#     except Exception as e:
#         print(f"Error processing file: {e}")
        

# try:
#     for message in consumer:
#         # Parse the Kafka message
#         msg_data = json.loads(message.value.decode('utf-8'))
#         file_id = msg_data['file_id']
#         filename = msg_data['filename']
#         print(f"Received file_id: {file_id}, filename: {filename}")

#         # Process the file and upload to BigQuery
#         process_file(file_id, filename)

#         # Manually commit the offset after processing the message
#         consumer.commit()
# except Exception as e:
#     print(f"Error: {e}")


import os
import json
import time
import joblib
from kafka import KafkaConsumer, errors
from google.cloud import bigquery
from minio import Minio
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

time.sleep(5)

# Set up environment variables and clients
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "drilldown-439515-062f7705dec7.json"
client = bigquery.Client()
minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

# Kafka Consumer setup
def create_consumer():
    return KafkaConsumer(
        'file_uploaded',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='file-processing-group'
    )

consumer = create_consumer()
print("Consumer initialized")

# BigQuery Table
dataset_id = "bdeminiproject"
table_id = "master"

# Model Saving Settings
MODEL_FILE = "arima_model.pkl"
BUCKET_NAME = "models"

# Load data (for now, this loads a CSV but could be changed to load from BigQuery)
def load_data():
    # Placeholder: Replace this with actual BigQuery loading code
    return pd.read_csv('path_to_data.csv')

# Save the model to MinIO
def save_model_to_minio(model):
    joblib.dump(model, MODEL_FILE)
    with open(MODEL_FILE, 'rb') as file_data:
        minio_client.put_object(BUCKET_NAME, MODEL_FILE, file_data, file_data.getbuffer().nbytes)

# Incrementally train the model
def incrementally_train_model():
    data = load_data()
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    model = ARIMA(data['Count'], order=(5, 1, 0))
    model_fit = model.fit()
    save_model_to_minio(model_fit)

def upload_row_to_bigquery(row):
    table_ref = client.dataset(dataset_id).table(table_id)
    rows_to_insert = [
        { "Area": int(row["Area"]), "Rpt Dist No": int(row["Rpt Dist No"]),
          "Part 1-2": int(row["Part 1-2"]), "Crm Cd": int(row["Crm Cd"]),
          "Vict Age": int(row["Vict Age"]), "Premis Cd": int(row["Premis Cd"]),
          "Weapon Used Cd": int(row["Weapon Used Cd"]), "Crm Cd 1": int(row["Crm Cd 1"]),
          "Crm Cd 2": int(row["Crm Cd 2"]), "Lat": float(row["Lat"]), "Lon": float(row["Lon"]) }
    ]
    max_retries = 5
    for attempt in range(max_retries):
        try:
            errors = client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                print(f"Errors while inserting rows: {errors}")
            else:
                print("Row inserted successfully.")
            break
        except Exception as e:
            print(f"Error inserting row into BigQuery on attempt {attempt + 1}/{max_retries}: {e}")
            time.sleep(2 ** attempt)

def process_file(file_id, filename):
    try:
        response = minio_client.get_object("csv-uploads", filename)
        df = pd.read_csv(response)
        if df.empty:
            print("File is empty or has no readable columns.")
            return
        for _, row in df.iterrows():
            upload_row_to_bigquery(row)
        response.close()
        response.release_conn()
        print("File processing complete.")

        # Incrementally train and save model after file processing
        incrementally_train_model()

    except Exception as e:
        print(f"Error processing file: {e}")

while True:
    try:
        for message in consumer:
            msg_data = json.loads(message.value.decode('utf-8'))
            file_id = msg_data['file_id']
            filename = msg_data['filename']
            print(f"Received file_id: {file_id}, filename: {filename}")
            process_file(file_id, filename)
            consumer.commit()
    except errors.IllegalStateError:
        print("Consumer lost connection, retrying...")
        time.sleep(5)
        consumer = create_consumer()
    except Exception as e:
        print(f"Unexpected error: {e}")
