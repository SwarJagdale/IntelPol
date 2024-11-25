from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from minio import Minio
import pickle
from io import BytesIO
from google.cloud import bigquery

import os
import telebot
from pyspark.sql import SparkSession
# Define your BigQuery query as a string
QUERY = """
    SELECT * FROM `your_project.your_dataset.your_table` LIMIT 10
"""



def load_data(**kwargs):
    # Simulate loading data
    print("Loading training data...")

def preprocess_data(**kwargs):
    print("Preprocessing data...")

def train_model(**kwargs):
    
    print("Training model...")
    spark = SparkSession.builder.master("local").appName("ModelTraining").getOrCreate()
    print("Model training completed.")

def save_model(**kwargs):
    print("Saving the model...")

def send_telegram_message():
    bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")
    bot.send_message(chat_id="6495459701", text="Model retraining completed!")
    bigquery_task()


def bigquery_task(**kwargs):
    bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
    client = bq_hook.get_client()
    bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")
    result = client.query(QUERY)
    for row in result:
        bot.send_message(chat_id="6495459701", text=str(row))
        break

# Define the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 11, 1),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="model_retraining_pipeline",
    default_args=default_args,
    schedule_interval=timedelta(seconds=20),
    catchup=False,
) as dag:

    task_load_data = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    task_preprocess_data = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_data,
    )

    task_train_model = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    task_save_model = PythonOperator(
        task_id="save_model",
        python_callable=save_model,
    )

    task_send_telegram_message = PythonOperator(
        task_id="send_telegram_message",
        python_callable=send_telegram_message,
    )

    # Add BigQuery task to your DAG
    task_bigquery = PythonOperator(
        task_id='run_bigquery_query',
        python_callable=bigquery_task,
    )
#task_load_data >> task_preprocess_data >> task_train_model >> task_save_model >> task_send_telegram_message >>
    task_send_telegram_message 
