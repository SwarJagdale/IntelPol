import time
from datetime import datetime, timedelta
import pickle
from minio import Minio
import os
from io import BytesIO

minio_client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
bucket_name = "csv-uploads"
model_bucket_name = "models"
last_checked = datetime.now() - timedelta(minutes=1)

def check_new_uploads():
    global last_checked
    current_time = datetime.now()
    objects = minio_client.list_objects(bucket_name, recursive=True)
    new_files = [
        obj.object_name for obj in objects 
        if obj.last_modified.replace(tzinfo=None) > last_checked
    ]
    last_checked = current_time
    return new_files

def retrain_and_upload_model(new_files):
    if new_files:
        # Placeholder for model retraining logic, e.g., re-fitting ARIMA model on new data.
        model = retrain_model(new_files)
        
        # Save and upload model to MinIO
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        model_bytes = pickle.dumps(model)
        model_latest = f"ARIMA_MODEL_LATEST"
        model_versioned = f"ARIMA_MODEL_{timestamp}"
        
        # Upload both latest and versioned model
        for model_name in [model_latest, model_versioned]:
            minio_client.put_object(
                model_bucket_name,
                model_name,
                data=BytesIO(model_bytes),
                length=len(model_bytes),
                content_type='application/octet-stream'
            )

def retrain_model(new_files):
    # Mock retraining logic
    return "new_arima_model_instance"

while True:
    new_files = check_new_uploads()
    retrain_and_upload_model(new_files)
    time.sleep(60)  # Check every 60 seconds
