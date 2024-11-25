import os
import json
import time
import logging
from kafka import KafkaConsumer
from google.cloud import bigquery

import pandas as pd
from datetime import datetime
import dotenv
dotenv.load_dotenv()
import boto3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='ap-south-1'
)

# Initialize Prometheus metrics

import requests



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for other services to initialize
time.sleep(5)

# Set Google application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "servicekey.json"

# Initialize BigQuery client
client = bigquery.Client()



# Kafka Consumer setup
consumer = KafkaConsumer(
    'crawled_data',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=False,
    group_id='crawled-data-processing-group'
)

logger.info("Crawled data consumer initialized")

# BigQuery table configuration
dataset_id = "bdeminiproject"
table_id = "Maharashtra"

def process_file(file_id, filename):
    try:
        
        s3_client.download_file("schwarzbde", f"uploads_crawled/"+filename, filename)
        
        df = pd.read_csv(filename)

        if df.empty:
            logger.warning("File is empty or has no readable columns.")
            return

        for _, row in df.iterrows():
            validate_and_upload_row(row)
        
        # response.close()
        # response.release_conn()
        logger.info("File processing complete.")
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")

def validate_and_upload_row(row):
    try:
        # Add your validation and upload logic here
        # Example: Insert row into BigQuery
        
        
        # Prepare the row for BigQuery
        formatted_row = {
            "Case Number": str(row.get("Case Number")),
            "Section of Law": str(row.get("Section of Law")),
            "Date": pd.to_datetime(str(row.get("Date"))).strftime("%Y-%m-%d") if pd.notnull(row.get("Date")) else None,
            "Location": str(row.get("Location")),
            "Complainant": str(row.get("Complainant")),
            "Accused": str(row.get("Accused")),
            "Important Details": str(row.get("Important Details")),
        }
        row = formatted_row
        
        
        table_ref = client.dataset(dataset_id).table(table_id)
        errors = client.insert_rows_json(table_ref, [row])
        if errors:
            logger.error(f"Failed to insert row: {errors}")
            
        
    except Exception as e:
        logger.error(f"Error validating/uploading row: {e}")
        

try:
    for message in consumer:
        msg_data = json.loads(message.value.decode('utf-8'))
        file_id = msg_data['file_id']
        filename = msg_data['filename']
        logger.info(f"Received file_id: {file_id}, filename: {filename}")
        
        process_file(file_id, filename)
        consumer.commit()
except Exception as e:
    logger.error(f"Consumer error: {e}")