import os
import pandas as pd
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
from kafka import KafkaProducer
# from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.arima.model import ARIMA
import json
from flask_cors import CORS
import uuid
from prometheus_flask_exporter import PrometheusMetrics
from datetime import datetime
app = Flask(__name__)
CORS(app)
# Initialize MinIO client
# minio_client = Minio(
#     "minio:9000",  # Your MinIO endpoint (localhost for local, otherwise your MinIO server address)
#     access_key="minioadmin",  # Your MinIO access key
#     secret_key="minioadmin",  # Your MinIO secret key
#     secure=False  # Set to True if using HTTPS
# )

# bucket_name = 'csv-uploads'  # MinIO bucket name

# # Create the bucket if it doesn't exist
# if not minio_client.bucket_exists(bucket_name):
#     minio_client.make_bucket(bucket_name)

# print("MinIO client initialized.")

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',

    max_request_size=1200000000,
    retries=5,  # Increase the number of retries
    request_timeout_ms=30000  # Timeout for waiting for an ack (30 seconds)
)

print(101)
producer.send(topic='file_uploaded',value=b'Hello there')
print(102)

metrics = PrometheusMetrics(app)
@metrics.counter('requests_total', 'Total number of requests')
def count_requests():
    return 1

@app.before_request
def before_request():
    count_requests()


# def process_crime_data(data):
#     # Drop rows with missing values
#     data.dropna(inplace=True)

#     # Convert the 'Date' column to datetime
#     data['Date'] = pd.to_datetime(data['Date'])

#     # Set the 'Date' column as the index
#     data.set_index('Date', inplace=True)

#     # Resample the data by month and sum the values
#     data = data.resample('M').sum()

#     # Check for stationarity
#     #pick random column
#     rand_col = data.columns[1]
    
    
#     stationarity = check_stationarity(data[rand_col])

#     # Perform prediction
#     prediction = perform_prediction(data[rand_col])
#     print("existed")
#     return {
#         'stationarity': stationarity,
#         'prediction': prediction
#     }
    


# def check_stationarity(data):
#     # Perform the Augmented Dickey-Fuller test
#     result = adfuller(data)
#     return {
#         'ADF Statistic': result[0],
#         'p-value': result[1],
#         'Critical Values': result[4],
#         'Stationary': result[1] < 0.05  # If p-value is less than 0.05, data is stationary
#     }

# def perform_prediction(data, order=(5, 1, 0)):
#     # Fit the ARIMA model
#     model = ARIMA(data, order=order)
#     model_fit = model.fit()
#     print('omdel has fitted')
#     # Make prediction
#     prediction = model_fit.forecast(steps=5)  # Predict the next 5 time steps
#     return prediction.tolist()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request."}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file."}), 400

    # Determine if the file is CSV or Excel
    if file and (file.content_type == 'text/csv' or file.content_type == 'application/vnd.ms-excel'):
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file.filename}_{file_id}"

        # try:
        #     # Upload to MinIO
        #     minio_client.put_object(
        #         bucket_name,
        #         filename,
        #         file.stream,
        #         length=-1,  # Since the length is unknown, we set -1
        #         part_size=10*1024*1024,  # Chunk size (10 MB), adjust as needed
        #         content_type=file.content_type
        #     )
        # except S3Error as e:
        #     return jsonify({"message": f"Failed to upload to MinIO: {str(e)}"}), 500

        # Reset file pointer and load the data into a Pandas DataFrame
        file.seek(0)
        if file.content_type == 'text/csv':
            df = pd.read_csv(file)
        elif file.content_type == 'application/vnd.ms-excel':
            df = pd.read_csv(file)

        # Process the crime dataset
        # processed_data = process_crime_data(df)

        # Example: Let's just return the first 5 rows for demonstration
        # result = processed_data.head().to_dict(orient='records')
        # result = processed_data
        print('here')
        # Publish events to Kafka
        time = datetime.now().isoformat()
        producer.send('file_uploaded', value=json.dumps({'file_id': str(file_id), 'filename': str(filename), 'time': str(time)}).encode('utf-8'))


        producer.flush()  # Ensure the message is sent
        # producer.send('data_processed', {'file_id': file_id, 'data': result})
        # producer.flush()  # Ensure the second message is sent

        print("temlee")
        return jsonify({
            "message": "File uploaded and processed successfully.",
            "file_id": file_id
        }), 200
    else:
        return jsonify({"message": "Invalid file type. Only CSV and Excel files are allowed."}), 400


@app.route('/')
def home():
    return "CSV Prediction Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000,debug=True)
