# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get -y install netcat-openbsd gcc \
    && apt-get clean


RUN apt-get update \
    && apt-get -y install netcat-openbsd gcc cmake libopenblas-dev liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]