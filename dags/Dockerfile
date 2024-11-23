FROM apache/airflow:2.6.1

# Install required Python packages
RUN pip install google-cloud-bigquery pyspark minio pandas pyTelegramBotAPI

# Add the service account key for BigQuery
COPY service-account-key.json /opt/airflow/service-account-key.json
