import os
import pandas as pd
# from flask import Flask, request, jsonify
from minio import Minio
from kafka import KafkaProducer, KafkaConsumer
import json
# from flask_cors import CORS
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# MinIO client setup
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
   
)

bucket_name = 'csv-uploads'
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

print("MinIO client initialized.")

# Kafka Consumer setup
consumer = KafkaConsumer(
    'file_uploaded',
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
     group_id='file-processing-group'
    
)

print(consumer.topics)

# Kafka Producer setup
# producer = KafkaProducer(
#     bootstrap_servers=['localhost:9092'],
#     value_serializer=lambda x: json.dumps(x).encode('utf-8')
# )

# def process_file(file_id, filename):
#     response = minio_client.get_object('uploads', filename)
#     spark = SparkSession.builder.appName("FileProcessor").getOrCreate()
#     df = spark.read.csv(response, header=True, inferSchema=True)
#     df = df.withColumn('forecast', col('data_column') * 1.05)
#     result_file = f"tmp/{file_id}_result.csv"
#     df.write.csv(result_file, header=True)
#     spark.stop()
#     minio_client.fput_object('processed', result_file, result_file)
#     producer.send('data_processed', {
#         'file_id': file_id,
#         'result_file': result_file,
#         'status': 'Processed Successfully'
#     })
#     producer.flush()

try:
    for message in consumer:
        print("Received message")
        file_data = json.loads(message.value)  # Deserialize message
        file_id = file_data['file_id']
        filename = file_data['filename']
        print(f"Processing file: {filename}")
        # process_file(file_id, filename)
except Exception as e:
    print(f"Error: {e}")
