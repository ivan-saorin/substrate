# Substrate MCP Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /substrate

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml README.md LICENSE ./

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/

# Install the package
RUN pip install --no-cache-dir .

# This image is meant to be used as a base
# It doesn't have a CMD as it's not meant to run standalone
