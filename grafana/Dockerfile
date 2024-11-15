FROM grafana/grafana:latest

# Install the Google BigQuery data source plugin
RUN grafana-cli plugins install grafana-bigquery-datasource

# Copy the Grafana configuration file
COPY grafana.ini /etc/grafana/grafana.ini

# Copy the service account key for BigQuery
# COPY servicekey.json /etc/grafana/servicekey.json
COPY consumer/drilldown-439515-95dc6c76a452.json /etc/grafana/servicekey.json


# Copy the dashboard JSON file
COPY dashboard.json /etc/grafana/dashboards/dashboard.json

# Copy the dashboards configuration file
COPY dashboards.yaml /etc/grafana/dashboards/dashboards.yaml

# Copy the data sources configuration file
COPY datasources.yaml /etc/grafana/datasources.yaml