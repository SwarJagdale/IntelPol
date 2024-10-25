FROM python:3.8-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run the consumer script
CMD ["python", "consumer.py"]
