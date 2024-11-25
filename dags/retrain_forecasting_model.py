from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import telebot    
import requests


bot = telebot.TeleBot("7190598149:AAFqya0tP0tF9wcn-EwpCzecDUwB_I_zqjg")




def incrementally_train_model():
    try:
        requests.get("http://backend:8000/retrain_forecasting_model")
        
        bot.send_message(chat_id="6495459701", text="Model retraining completed finally!")
        

    except Exception as e:
        print(f"Error during model training: {e}")
        bot.send_message(chat_id="6495459701", text=f"Error during model training: {str(e)}")


# Define the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 11, 1),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="incremental",
    default_args=default_args,
    schedule_interval=timedelta(seconds=60*60*12),
    catchup=False,
) as dag:

    
    
    
    task_incrementally_train_model = PythonOperator(
        task_id="incrementally_train_model",
        python_callable=incrementally_train_model,
    )
#task_load_data >> task_preprocess_data >> task_train_model >> task_save_model >> task_send_telegram_message >>
    task_incrementally_train_model
