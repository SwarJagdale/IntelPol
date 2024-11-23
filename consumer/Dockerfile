FROM python:3.8-slim

WORKDIR /app
COPY . /app

COPY servicekey.json /app/servicekey.json

# Install dependencies
RUN pip install -r requirements.txt



# Run the consumer script
CMD ["python", "consumer.py"]
