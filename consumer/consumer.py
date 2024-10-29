print("Consumer started")
import os
import pandas as pd
from minio import Minio
from kafka import KafkaConsumer
import json
import time

time.sleep(5)

# MinIO client setup
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
    auto_offset_reset='latest',  # 'earliest' to read from start, 'latest' for new messages
    enable_auto_commit=False,     # Set to False to manually commit
    group_id='file-processing-group'  # Use a consistent group ID
)
print('Consumer initialized')

try:
    for message in consumer:
        print("Received message")
        print(f"{message.key}: {message.value.decode('utf-8')}")
        # Process the message here as needed

        # Manually commit the offset after processing the message
        consumer.commit()
except Exception as e:
    print(f"Error: {e}")
