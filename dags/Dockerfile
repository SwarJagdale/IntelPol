FROM apache/airflow:2.6.1-python3.8

USER root

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file from the 'dags' folder
COPY /requirements.txt /requirements.txt
USER airflow
# Install the Python dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAG files to Airflow's DAGs folder
COPY ./ /opt/airflow/dags
