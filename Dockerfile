FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY src/ /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Python path setup - using default empty value to avoid undefined variable warning
ENV PYTHONPATH=/app:${PYTHONPATH:-}

# This is a base image, no CMD
