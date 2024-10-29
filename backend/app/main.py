import os
import pandas as pd
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
from kafka import KafkaProducer

import json
from flask_cors import CORS
import uuid
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime
app = Flask(__name__)
CORS(app)
# Initialize MinIO client
minio_client = Minio(
    "minio:9000",  # Your MinIO endpoint (localhost for local, otherwise your MinIO server address)
    access_key="minioadmin",  # Your MinIO access key
    secret_key="minioadmin",  # Your MinIO secret key
    secure=False  # Set to True if using HTTPS
)

bucket_name = 'csv-uploads'  # MinIO bucket name
print(minio_client.bucket_exists(bucket_name))
# Create the bucket if it doesn't exist
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

print("MinIO client initialized.")

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',

    max_request_size=1200000000,
    retries=5,  # Increase the number of retries
    request_timeout_ms=30000  # Timeout for waiting for an ack (30 seconds)
)


print(102)

metrics = PrometheusMetrics(app)
@metrics.counter('requests_total', 'Total number of requests')
def count_requests():
    return 1

@app.before_request
def before_request():
    count_requests()

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
            minio_client.put_object(
                bucket_name,
                filename,
                file.stream,
                length=file.content_length,
                part_size=10*1024*1024,
                content_type=file.content_type
            )
            print("File uploaded to MinIO successfully.")
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            return jsonify({"message": f"Failed to upload to MinIO: {str(e)}"}), 500

        file.seek(0)
        if file.content_type == 'text/csv':
            df = pd.read_csv(file)
        elif file.content_type == 'application/vnd.ms-excel':
            df = pd.read_csv(file)

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
    app.run(host='0.0.0.0', port=8000,debug=True)
