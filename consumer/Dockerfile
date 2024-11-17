FROM python:3.8-slim

WORKDIR /app
COPY . /app

COPY drilldown-439515-95dc6c76a452.json /app/drilldown-439515-95dc6c76a452.json

# Install dependencies
RUN pip install -r requirements.txt



# Run the consumer script
CMD ["python", "consumer.py"]
