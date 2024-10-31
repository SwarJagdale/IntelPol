import os
import json
import time
from kafka import KafkaConsumer
from google.cloud import bigquery
from minio import Minio
import pandas as pd
from datetime import datetime

# Wait for other services to initialize
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
    auto_offset_reset='latest',
    enable_auto_commit=False,
    group_id='file-processing-group'
)

print("Consumer initialized")

# Define your BigQuery table information
dataset_id = "bdeminiproject"  # Replace with your BigQuery dataset
table_id = "master_new"            # Replace with your BigQuery table


def format_date(date_str):
    # List of common date formats to attempt parsing
    date_formats = [
        "%Y-%m-%d",       # 2023-10-31
        "%m/%d/%Y",       # 10/31/2023
        "%d-%m-%Y",       # 31-10-2023
        "%d/%m/%Y",       # 31/10/2023
        "%Y/%m/%d",       # 2023/10/31
        "%Y.%m.%d",       # 2023.10.31
        "%m-%d-%Y",       # 10-31-2023
        "%d %B %Y",       # 31 October 2023
        "%B %d, %Y",      # October 31, 2023
        "%d %b %Y",       # 31 Oct 2023
        "%b %d, %Y",      # Oct 31, 2023
        "%Y %b %d",       # 2023 Oct 31
        "%b %d %Y",       # Oct 31 2023
        "%Y %B %d",       # 2023 October 31
        "%d-%b-%Y",       # 31-Oct-2023
        "%d.%m.%Y",       # 31.10.2023
        "%d %m %Y"        # 31 10 2023
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    print(f"Invalid date format: {date_str}")
    return None

def format_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M:%S")
    except ValueError:
        # Handle cases where the time format is different
        try:
            return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M:%S")
        except ValueError:
            print(f"Invalid time format: {time_str}")
            return None

def upload_row_to_bigquery(row):
    table_ref = client.dataset(dataset_id).table(table_id)
    
    # Format date and time columns
    date_rptd = format_date(row["Date Rptd"])
    date_occ = format_date(row["Date Occ"])
    time_occ = format_time(row["Time Occ"])

    rows_to_insert = [
        {
            "Date Rptd": date_rptd,
            "Date Occ": date_occ,
            "Time Occ": time_occ,
            "Area": int(row["Area"]),
            "Area Name": row["Area Name"],
            "Rpt Dist No": int(row["Rpt Dist No"]),
            "Part 1-2": int(row["Part 1-2"]),
            "Crm Cd": int(row["Crm Cd"]),
            "Crm Cd Desc": row["Crm Cd Desc"],
            "Mo Codes": row["Mo Codes"],
            "Vict Age": int(row["Vict Age"]),
            "Vict Sex": row["Vict Sex"],
            "Vict Descent": row["Vict Descent"],
            "Premis Cd": int(row["Premis Cd"]),
            "Premis Desc": row["Premis Desc"],
            "Weapon Used Cd": row.get("Weapon Used Cd", None),
            "Weapon Desc": row["Weapon Desc"],
            "Status": row["Status"],
            "Status Desc": row["Status Desc"],
            "Crm Cd 1": int(row["Crm Cd 1"]),
            "Crm Cd 2": int(row["Crm Cd 2"]),
            "Location": row["Location"],
            "Cross Street": row["Cross Street"],
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
            validate_and_upload_row(row)
        
        response.close()
        response.release_conn()
        print("File processing complete.")
        
    except Exception as e:
        print(f"Error processing file: {e}")
def validate_and_upload_row(row):
    # Required fields check
    if pd.isnull(row["Date Rptd"]) or pd.isnull(row["Date Occ"]):
        print("Missing required date fields; skipping row.")
        return False
    
    # Format dates and times
    date_rptd = format_date(row["Date Rptd"])
    date_occ = format_date(row["Date Occ"])
    time_occ = format_time(row["Time Occ"])

    # If formatting fails, skip row
    if date_rptd is None or date_occ is None or time_occ is None:
        print("Date/Time formatting issue; skipping row.")
        return False

    # Additional data validations (e.g., integer/floats)
    # Replace NaN values with None
    row = row.where(pd.notnull(row), None)
    def validate_type(value, expected_type):
        if pd.isnull(value):
            return True  # Allow null values for nullable fields
        try:
            if expected_type == "INTEGER":
                int(value)
            elif expected_type == "FLOAT":
                float(value)
            elif expected_type == "STRING":
                str(value)
            elif expected_type == "DATE" or expected_type == "TIME":
                return True  # Date and Time are already formatted
            return True
        except (ValueError, TypeError):
            return False

    # Define the expected types for each field
    field_types = {
        "Date Rptd": "DATE", "Date Occ": "DATE", "Time Occ": "TIME",
        "Area": "INTEGER", "Area Name": "STRING", "Rpt Dist No": "INTEGER",
        "Part 1-2": "INTEGER", "Crm Cd": "INTEGER", "Crm Cd Desc": "STRING",
        "Mo Codes": "STRING", "Vict Age": "INTEGER", "Vict Sex": "STRING",
        "Vict Descent": "STRING", "Premis Cd": "INTEGER", "Premis Desc": "STRING",
        "Weapon Used Cd": "STRING", "Weapon Desc": "STRING", "Status": "STRING",
        "Status Desc": "STRING", "Crm Cd 1": "INTEGER", "Crm Cd 2": "INTEGER",
        "Location": "STRING", "Cross Street": "STRING", "Lat": "FLOAT", "Lon": "FLOAT"
    }

    # Validate each field's type
    for field, expected_type in field_types.items():
        if not validate_type(row[field], expected_type):
            print(f"Type mismatch for field {field}; expected {expected_type}, skipping row.")
            return False

    # Prepare the row for BigQuery insertion
    rows_to_insert = [
        {
            "Date Rptd": date_rptd,
            "Date Occ": date_occ,
            "Time Occ": time_occ,
            "Area": int(row["Area"]) if not pd.isnull(row["Area"]) else None,
            "Area Name": row["Area Name"] if not pd.isnull(row["Area Name"]) else None,
            "Rpt Dist No": int(row["Rpt Dist No"]) if not pd.isnull(row["Rpt Dist No"]) else None,
            "Part 1-2": int(row["Part 1-2"]) if not pd.isnull(row["Part 1-2"]) else None,
            "Crm Cd": int(row["Crm Cd"]) if not pd.isnull(row["Crm Cd"]) else None,
            "Crm Cd Desc": row["Crm Cd Desc"] if not pd.isnull(row["Crm Cd Desc"]) else None,
            "Mo Codes": row["Mo Codes"] if not pd.isnull(row["Mo Codes"]) else None,
            "Vict Age": int(row["Vict Age"]) if not pd.isnull(row["Vict Age"]) else None,
            "Vict Sex": row["Vict Sex"] if not pd.isnull(row["Vict Sex"]) else None,
            "Vict Descent": row["Vict Descent"] if not pd.isnull(row["Vict Descent"]) else None,
            "Premis Cd": int(row["Premis Cd"]) if not pd.isnull(row["Premis Cd"]) else None,
            "Premis Desc": row["Premis Desc"] if not pd.isnull(row["Premis Desc"]) else None,
            "Weapon Used Cd": row.get("Weapon Used Cd", None),
            "Weapon Desc": row["Weapon Desc"] if not pd.isnull(row["Weapon Desc"]) else None,
            "Status": row["Status"] if not pd.isnull(row["Status"]) else None,
            "Status Desc": row["Status Desc"] if not pd.isnull(row["Status Desc"]) else None,
            "Crm Cd 1": int(row["Crm Cd 1"]) if not pd.isnull(row["Crm Cd 1"]) else None,
            "Crm Cd 2": int(row["Crm Cd 2"]) if not pd.isnull(row["Crm Cd 2"]) else None,
            "Location": row["Location"] if not pd.isnull(row["Location"]) else None,
            "Cross Street": row["Cross Street"] if not pd.isnull(row["Cross Street"]) else None,
            "Lat": float(row["Lat"]) if not pd.isnull(row["Lat"]) else None,
            "Lon": float(row["Lon"]) if not pd.isnull(row["Lon"]) else None
        }
    ]

    # Insert into BigQuery
    table_ref = client.dataset(dataset_id).table(table_id)
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"Errors while inserting rows: {errors}")
        print(f"Row with data: {row}")
        return False
    else:
        print("Row inserted successfully.")
        return True

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