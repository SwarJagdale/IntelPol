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
import pickle
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Initialize MinIO client
minio_client = Minio(
    "minio:9000",
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

metrics = PrometheusMetrics(app)

@metrics.counter('requests_total', 'Total number of requests')
def count_requests():
    return 1

@app.before_request
def before_request():
    count_requests()

# Define the expected columns
EXPECTED_COLUMNS = [
    'Area', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 'Vict Age',
    'Premis Cd', 'Weapon Used Cd', 'Crm Cd 1', 'Crm Cd 2', 'Lat', 'Lon'
]

def validate_csv_structure(df):
    # Check if all expected columns are present
    if not all(col in df.columns for col in EXPECTED_COLUMNS):
        return False, f"Missing columns: {', '.join([col for col in EXPECTED_COLUMNS if col not in df.columns])}"
    
    # Optional: Add further validation for column types if needed
    # Example: Ensure 'Vict Age' is of type int
    if not pd.api.types.is_integer_dtype(df['Vict Age']):
        return False, "'Vict Age' must be of integer type."
    
    # Add more type checks as needed...

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
            # Read the file content to ensure it's not empty
            file_content = file.read()
            if not file_content:
                print("Empty file content.")
                return jsonify({"message": "The file is empty."}), 400

            # Upload to MinIO
            minio_client.put_object(
                bucket_name,
                filename,
                data=io.BytesIO(file_content),  # Use BytesIO to ensure correct stream format
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
    
    
model_bucket_name = 'models'
if not minio_client.bucket_exists(model_bucket_name):
    minio_client.make_bucket(model_bucket_name)

def save_model_to_minio(model, model_name="ARIMA_MODEL_LATEST"):
    """Save a pickled model to MinIO"""
    try:
        # Serialize model to bytes
        model_bytes = BytesIO()
        pickle.dump(model, model_bytes)
        model_bytes.seek(0)  # Reset buffer pointer to beginning
        
        # Upload to MinIO
        minio_client.put_object(
            model_bucket_name,
            model_name,
            data=model_bytes,
            length=model_bytes.getbuffer().nbytes,
            content_type="application/octet-stream"
        )
        print(f"Model '{model_name}' uploaded to MinIO successfully.")
    except S3Error as e:
        print(f"Failed to upload model to MinIO: {e}")
        raise e
    
@app.route('/forecast', methods=['POST'])
def forecast():
    """Endpoint to perform forecasting using the latest ARIMA model."""
    try:
        model_data = minio_client.get_object(bucket_name, "ARIMA_MODEL_LATEST")
        model = pickle.load(BytesIO(model_data.read()))
        
        # Assuming data needed for forecasting is sent in the request body
        request_data = request.get_json()
        future_steps = request_data.get("future_steps", 10)  # Default to 10 steps if not provided
        
        # Perform forecasting (assuming model has a forecast method)
        forecasted_values = model.forecast(steps=future_steps)
        
        return jsonify({"forecast": forecasted_values.tolist()}), 200
    except S3Error as e:
        return jsonify({"message": f"Failed to load model: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Forecasting error: {str(e)}"}), 500

@app.route('/')
def home():
    return "CSV Prediction Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)