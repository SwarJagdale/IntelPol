FROM python:3.8-slim

WORKDIR /app
COPY . /app

COPY drilldown-439515-062f7705dec7.json /app/drilldown-439515-062f7705dec7.json

# Install dependencies
RUN pip install -r requirements.txt


# Run the consumer script
CMD ["python", "consumer.py"]



