# Use Python base image
FROM python:3.8-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install required Python build tools
RUN pip install --upgrade pip setuptools wheel

# Copy the requirements.txt first to cache dependencies
COPY app/requirements.txt .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy wait-for-it script and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Copy the application code
COPY app /app/app

EXPOSE 8000

# Run the Flask app
CMD ["python", "app/main.py"]
