import os
import json
import time
import logging
from kafka import KafkaConsumer
from google.cloud import bigquery
import pandas as pd
from datetime import datetime
import boto3
import dotenv
dotenv.load_dotenv()

# Initialize s3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='ap-south-1'
)





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
    'file_uploaded',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=False,
    group_id='file-processing-group'
)

logger.info("Consumer initialized")

# BigQuery table configuration
dataset_id = "bdeminiproject"
table_id = "master"

def format_date(date_str):
    # List of common date formats to attempt parsing
    date_str=str(date_str)
    date_formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d",
        "%Y.%m.%d", "%m-%d-%Y", "%d %B %Y", "%B %d, %Y", "%d %b %Y",
        "%b %d, %Y", "%Y %b %d", "%b %d %Y", "%Y %B %d", "%d-%b-%Y",
        "%d.%m.%Y", "%d %m %Y"
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    logger.warning(f"Invalid date format: {date_str}")
    return None

def format_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M:%S")
        except ValueError:
            logger.warning(f"Invalid time format: {time_str}")
            return None

def validate_and_upload_row(row):
    if pd.isnull(row["Date Rptd"]) or pd.isnull(row["Date Occ"]):
        logger.warning("Missing required date fields; skipping row.")
        return False

    date_rptd = format_date(row["Date Rptd"])
    date_occ = format_date(row["Date Occ"])
    time_occ = format_time(row["Time Occ"])

    if date_rptd is None or date_occ is None or time_occ is None:
        logger.warning("Date/Time formatting issue; skipping row.")
        return False

    row = row.where(pd.notnull(row), None)
    rows_to_insert = [
        {
            "Date Rptd": date_rptd,
            "Date Occ": date_occ,
            "Time Occ": time_occ,
            "Area": int(row["Area"]) if row["Area"] else None,
            "Area Name": row["Area Name"],
            "Rpt Dist No": int(row["Rpt Dist No"]) if row["Rpt Dist No"] else None,
            "Part 1-2": int(row["Part 1-2"]) if row["Part 1-2"] else None,
            "Crm Cd": int(row["Crm Cd"]) if row["Crm Cd"] else None,
            "Crm Cd Desc": row["Crm Cd Desc"],
            "Mo Codes": row["Mo Codes"],
            "Vict Age": int(row["Vict Age"]) if row["Vict Age"] else None,
            "Vict Sex": row["Vict Sex"],
            "Vict Descent": row["Vict Descent"],
            "Premis Cd": int(row["Premis Cd"]) if row["Premis Cd"] else None,
            "Premis Desc": row["Premis Desc"],
            "Weapon Used Cd": row.get("Weapon Used Cd", None),
            "Weapon Desc": row["Weapon Desc"],
            "Status": row["Status"],
            "Status Desc": row["Status Desc"],
            "Crm Cd 1": int(row["Crm Cd 1"]) if row["Crm Cd 1"] else None,
            "Crm Cd 2": int(row["Crm Cd 2"]) if row["Crm Cd 2"] else None,
            "Location": row["Location"],
            "Cross Street": row["Cross Street"],
            "Lat": float(row["Lat"]) if row["Lat"] else None,
            "Lon": float(row["Lon"]) if row["Lon"] else None
        }
    ]

    table_ref = client.dataset(dataset_id).table(table_id)
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        logger.error(f"Errors while inserting rows: {errors}")
        
        return False
    else:
        logger.info("Row inserted successfully.")
        
        return True

def process_file(file_id, filename):
    try:
        
        
        s3_client.download_file("schwarzbde", r"uploads/"+filename, filename)
        
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
