import os
import pandas as pd
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
from kafka import KafkaProducer
import io
import json
from flask_cors import CORS
import uuid
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = 'csv-uploads'
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    max_request_size=1200000000,
    retries=5,
    request_timeout_ms=30000
)

# Define the expected columns
EXPECTED_COLUMNS = [
    'Area', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 'Vict Age',
    'Premis Cd', 'Weapon Used Cd', 'Crm Cd 1', 'Crm Cd 2', 'Lat', 'Lon'
]

def validate_csv_structure(df):
    # Check if all expected columns are present
    if not all(col in df.columns for col in EXPECTED_COLUMNS):
        return False, f"Missing columns: {', '.join([col for col in EXPECTED_COLUMNS if col not in df.columns])}"
    
    # Ensure 'Vict Age' is of integer type
    if not pd.api.types.is_integer_dtype(df['Vict Age']):
        return False, "'Vict Age' must be of integer type."
    
    return True, ""

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received request at /upload")
    if 'file' not in request.files:
        print("No file part in the request.")
        return jsonify({"message": "No file part in the request."}), 400

    file = request.files['file']
    print("File received:", file.filename)

    if file.filename == '':
        print("No selected file.")
        return jsonify({"message": "No selected file."}), 400

    if file and (file.content_type == 'text/csv' or file.content_type == 'application/vnd.ms-excel'):
        file_id = str(uuid.uuid4())
        filename = f"{file.filename}_{file_id}"
        print("Generated filename:", filename)

        try:
            file_content = file.read()
            if not file_content:
                print("Empty file content.")
                return jsonify({"message": "The file is empty."}), 400

            # Upload to MinIO
            minio_client.put_object(
                bucket_name,
                filename,
                data=io.BytesIO(file_content),
                length=len(file_content),
                part_size=10*1024*1024,
                content_type=file.content_type
            )
            print("File uploaded to MinIO successfully.")
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            return jsonify({"message": f"Failed to upload to MinIO: {str(e)}"}), 500

        print("Publishing to Kafka...")
        time = datetime.now().isoformat()
        producer.send('file_uploaded', value=json.dumps({
            'file_id': file_id,
            'filename': filename,
            'time': time
        }).encode('utf-8'))
        producer.flush()

        print("Kafka message sent.")
        return jsonify({"message": "File uploaded and processed successfully.", "file_id": file_id}), 200
    else:
        print("Invalid file type.")
        return jsonify({"message": "Invalid file type. Only CSV and Excel files are allowed."}), 400

@app.route('/')
def home():
    return "CSV Prediction Service is running!"
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
