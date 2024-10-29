import os
import json
import time
from kafka import KafkaConsumer
from google.cloud import bigquery
from minio import Minio
from datetime import datetime
import pandas as pd
time.sleep(5)

# Set the Google application credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "drilldown-439515-062f7705dec7.json"

# Initialize BigQuery client
client = bigquery.Client()

# Initialize MinIO client
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Kafka Consumer setup
consumer = KafkaConsumer(
    'file_uploaded',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='latest',  # Start from the earliest message
    enable_auto_commit=False,       # Manually commit offset
    group_id='file-processing-group'
)

print("Consumer initialized")

# Define your BigQuery table information
dataset_id = "bdeminiproject"  # Replace with your BigQuery dataset
table_id = "master"      # Replace with your BigQuery table

def upload_row_to_bigquery(row):
    table_ref = client.dataset(dataset_id).table(table_id)
    rows_to_insert = [
        {
            "Area": int(row["Area"]),
            "Rpt Dist No": int(row["Rpt Dist No"]),
            "Part 1-2": int(row["Part 1-2"]),
            "Crm Cd": int(row["Crm Cd"]),
            "Vict Age": int(row["Vict Age"]),
            "Premis Cd": int(row["Premis Cd"]),
            "Weapon Used Cd": int(row["Weapon Used Cd"]),
            "Crm Cd 1": int(row["Crm Cd 1"]),
            "Crm Cd 2": int(row["Crm Cd 2"]),
            "Lat": float(row["Lat"]),
            "Lon": float(row["Lon"])
        }
    ]
    
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"Errors while inserting rows: {errors}")
    else:
        print("Row inserted successfully.")

def process_file(file_id, filename):
    try:
        # Retrieve the file from MinIO
        response = minio_client.get_object("csv-uploads", filename)
        
        # Read file content into a DataFrame
        df = pd.read_csv(response)

        # Check if the DataFrame is empty
        if df.empty:
            print("File is empty or has no readable columns.")
            return

        # Iterate through each row and upload it to BigQuery
        for _, row in df.iterrows():
            upload_row_to_bigquery(row)
        response.close()
        response.release_conn()
        print("File processing complete.")
    except Exception as e:
        print(f"Error processing file: {e}")
        


try:
    for message in consumer:
        # Parse the Kafka message
        msg_data = json.loads(message.value.decode('utf-8'))
        file_id = msg_data['file_id']
        filename = msg_data['filename']
        print(f"Received file_id: {file_id}, filename: {filename}")

        # Process the file and upload to BigQuery
        process_file(file_id, filename)

        # Manually commit the offset after processing the message
        consumer.commit()
except Exception as e:
    print(f"Error: {e}")