import os
import pandas as pd
from flask import Flask, request, jsonify


from kafka import KafkaProducer
import io
import json
from flask_cors import CORS
import uuid
import os
from datetime import datetime
import pickle
from io import BytesIO
import boto3
import dotenv
dotenv.load_dotenv()



app = Flask(__name__)
CORS(app)





# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    max_request_size=1200000000,
    retries=5,
    request_timeout_ms=30000
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='ap-south-1'
)







EXPECTED_COLUMNS = [
    'Area', 'Rpt Dist No', 'Part 1-2', 'Crm Cd', 'Vict Age',
    'Premis Cd', 'Weapon Used Cd', 'Crm Cd 1', 'Crm Cd 2', 'Lat', 'Lon'
]

def validate_csv_structure(df):
    if not all(col in df.columns for col in EXPECTED_COLUMNS):
        return False, f"Missing columns: {', '.join([col for col in EXPECTED_COLUMNS if col not in df.columns])}"

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
            # Read the file content to ensure it's not empty
            file_content = file.read()
            if not file_content:
                print("Empty file content.")
                return jsonify({"message": "The file is empty."}), 400
            
            s3_client.upload_fileobj(io.BytesIO(file_content), 'schwarzbde', r"uploads/"+filename)
            
            print("File uploaded to s3 successfully.")
        except Exception as e:
            print(f"S3 upload error: {e}")
            return jsonify({"message": f"Failed to upload to S3: {str(e)}"}), 500

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
if True:
    
    try:
        s3_client.download_file('schwarzbde', r"models/ARIMA_MODEL_LATEST", 'app/arima_model.pkl')
        print(f"Model uploaded successfully as ARIMA_MODEL_LATEST.")
    except Exception as e:
        print(f"Error uploading model: {e}")

def save_model_to_s3(model, model_name="ARIMA_MODEL_LATEST"):

    try:
        # Serialize model to bytes
        model_bytes = BytesIO()
        pickle.dump(model, model_bytes)
        model_bytes.seek(0)  # Reset buffer pointer to beginning

        
        
        s3_client.upload_fileobj(model_bytes, 'schwarzbde', r"models/"+model_name)
        
        
        print(f"Model '{model_name}' uploaded to S3 successfully.")
    except Exception as e:
        print(f"Failed to upload model to S3: {e}")
        raise e
    
@app.route('/forecast', methods=['POST'])
def forecast():
    """Endpoint to perform forecasting using the latest ARIMA model."""
    try:

        model = pickle.load(open('app/arima_model.pkl', 'rb'))
        # If no history is provided, use the fitted values (in-sample predictions)
        request_data = request.get_json()
        history = request_data.get("history")  # History sent by the user
        
        # If no history is provided in the request, use the fitted values from the model
        if not history:
            history = model.fittedvalues.tolist()  # Get the fitted values from the model
        
        future_steps = request_data.get("future_steps", 10)  # Default to 10 steps if not provided

        # Perform forecasting using the ARIMA model
        forecasted_values = model.forecast(steps=future_steps)

        # Combine the history (fitted values) with the forecasted values
        complete_data = history + forecasted_values.tolist()

        # Return both the historical data and the forecasted values
        return jsonify({
            "history": history,
            "forecast": forecasted_values.tolist(),
            "complete_curve": complete_data  # Combined history and forecast
        }), 200

    except Exception as e:
        return jsonify({"message": f"Failed to load model: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Forecasting error: {str(e)}"}), 500
    
    


##Add another endpoint to handle upload but for another topic 'crawled_data'
@app.route('/upload_crawled_data', methods=['POST'])
def upload_crawled_data():
    print("Received request at /upload_crawled_data")
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

            
            
            
            s3_client.upload_fileobj(io.BytesIO(file_content), 'schwarzbde', r"uploads_crawled/"+filename)
            
            
            print("File uploaded to s3 successfully.")
        except Exception as e:
            print(f"s3 upload error: {e}")
            return jsonify({"message": f"Failed to upload to s3: {str(e)}"}), 500

        print("Publishing to Kafka...")
        time = datetime.now().isoformat()
        producer.send('crawled_data', value=json.dumps({
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



    
@app.route('/upload', methods=['POST'])
def upload_file_or_form():
    print("Received request at /upload")
    # Check if the request contains a file
    if 'file' in request.files:
        file = request.files['file']
        print("File received:", file.filename)

        if file.filename == '':
            return jsonify({"message": "No selected file."}), 400

        if file and (file.content_type == 'text/csv' or file.content_type == 'application/vnd.ms-excel'):
            return process_csv(file)
        else:
            return jsonify({"message": "Invalid file type. Only CSV and Excel files are allowed."}), 400

    # Check if JSON form data is provided
    elif request.json:
        form_data = request.get_json()
        return process_form(form_data)

    else:
        return jsonify({"message": "No file or form data provided."}), 400

def process_csv(file):
    file_id = str(uuid.uuid4())
    filename = f"{file.filename}_{file_id}"

    try:
        file_content = file.read()
        if not file_content:
            return jsonify({"message": "The file is empty."}), 400

        s3_client.upload_fileobj(io.BytesIO(file_content), 'schwarzbde', r"uploads/"+filename)
        # Publish to Kafka
        time = datetime.now().isoformat()
        producer.send('file_uploaded', value=json.dumps({
            'file_id': file_id,
            'filename': filename,
            'time': time
        }).encode('utf-8'))
        producer.flush()

        return jsonify({"message": "File uploaded and processed successfully.", "file_id": file_id}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to upload to S3: {str(e)}"}), 500


def process_form(form_data):
    try:
        # Convert form data to DataFrame for validation
        df = pd.DataFrame([form_data])
        is_valid, error_message = validate_csv_structure(df)
        if not is_valid:
            return jsonify({"message": f"Validation error: {error_message}"}), 400

        
        file_id = str(uuid.uuid4())
        filename = f"form_data_{file_id}.csv"
        csv_data = df.to_csv(index=False).encode('utf-8')

        
        s3_client.upload_fileobj(io.BytesIO(csv_data), 'schwarzbde', r"uploads/"+filename)
        # Publish to Kafka
        time = datetime.now().isoformat()
        producer.send('form_uploaded', value=json.dumps({
            'file_id': file_id,
            'filename': filename,
            'time': time
        }).encode('utf-8'))
        producer.flush()

        return jsonify({"message": "Form data uploaded and processed successfully.", "file_id": file_id}), 200

    except Exception as e:
        return jsonify({"message": f"Form processing error: {str(e)}"}), 500
    
    
@app.route('/')
def home():
    return "CSV Prediction Service is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)



