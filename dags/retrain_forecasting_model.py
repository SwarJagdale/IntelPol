from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from minio import Minio
import pickle
from io import BytesIO
import telebot
import os

# Default args for Airflow
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
dag = DAG(
    'retrain_forecasting_model',
    default_args=default_args,
    description='DAG for automating model retraining with BigQuery and MinIO',
    schedule_interval='@daily',
    start_date=datetime(2024, 11, 23),
    catchup=False,
)

# Spark and MinIO Initialization
spark = SparkSession.builder.appName("AirflowModelRetraining").getOrCreate()
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)
model_bucket = 'models'

# Define Python tasks
def preprocess_data():
    # Dummy preprocessing logic (add your transformation here)
    data = [{"raw_col": 10}, {"raw_col": 20}]
    df = spark.createDataFrame(data)
    df = df.withColumn("processed_col", col("raw_col") + 1)
    return df.toPandas().to_json()

def retrain_model(**kwargs):
    ti = kwargs['ti']
    preprocessed_data = ti.xcom_pull(task_ids='preprocess_data')
    preprocessed_df = spark.read.json(BytesIO(preprocessed_data.encode())).toPandas()

    model_data = minio_client.get_object(model_bucket, "ARIMA_MODEL_LATEST")
    model = pickle.load(BytesIO(model_data.read()))

    model.fit(preprocessed_df['processed_col'])

    model_bytes = BytesIO()
    pickle.dump(model, model_bytes)
    model_bytes.seek(0)
    minio_client.put_object(model_bucket, "ARIMA_MODEL_LATEST", model_bytes, len(model_bytes.getbuffer()))
    print("Model retrained and uploaded.")

def send_telegram_message():
    bot = telebot.TeleBot("your_telegram_token")
    bot.send_message(chat_id="your_chat_id", text="Model retraining completed!")

# BigQuery task
bq_task = BigQueryInsertJobOperator(
    task_id='run_bigquery_query',
    configuration={
        "query": {
            "query": "SELECT * FROM `your_project.your_dataset.your_table` LIMIT 1000",
            "useLegacySql": False,
        }
    },
    dag=dag,
)

# PythonOperator tasks
preprocess_data_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

retrain_model_task = PythonOperator(
    task_id='retrain_model',
    python_callable=retrain_model,
    provide_context=True,
    dag=dag,
)

send_message_task = PythonOperator(
    task_id='send_message',
    python_callable=send_telegram_message,
    dag=dag,
)

# Task dependencies
bq_task >> preprocess_data_task >> retrain_model_task >> send_message_task
