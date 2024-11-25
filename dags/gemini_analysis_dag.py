from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add the gemini directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'gemini'))

from try import download_pdfs, extract_text_from_pdf, analyze_pdf, structure_response, save_results

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'gemini_analysis_dag',
    default_args=default_args,
    description='A DAG to analyze PDFs using Gemini API',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define the tasks
def download_pdfs_task(**kwargs):
    url = "https://nandedpolice.gov.in/publish/13"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    pdf_files = download_pdfs(url, headers)
    kwargs['ti'].xcom_push(key='pdf_files', value=pdf_files)

def analyze_pdfs_task(**kwargs):
    pdf_files = kwargs['ti'].xcom_pull(key='pdf_files', task_ids='download_pdfs')
    all_results = pd.DataFrame()
    for pdf_file in pdf_files:
        pdf_content = extract_text_from_pdf(pdf_file)
        if pdf_content:
            results = analyze_pdf(None, pdf_content)  # Pass the model if needed
            all_results = pd.concat([all_results, results], ignore_index=True)
    kwargs['ti'].xcom_push(key='all_results', value=all_results)

def save_results_task(**kwargs):
    all_results = kwargs['ti'].xcom_pull(key='all_results', task_ids='analyze_pdfs')
    if not all_results.empty:
        save_results(all_results)
    else:
        print("No results to save.")

# Create the tasks
download_pdfs = PythonOperator(
    task_id='download_pdfs',
    python_callable=download_pdfs_task,
    provide_context=True,
    dag=dag,
)

analyze_pdfs = PythonOperator(
    task_id='analyze_pdfs',
    python_callable=analyze_pdfs_task,
    provide_context=True,
    dag=dag,
)

save_results = PythonOperator(
    task_id='save_results',
    python_callable=save_results_task,
    provide_context=True,
    dag=dag,
)

# Set the task dependencies
download_pdfs >> analyze_pdfs >> save_results