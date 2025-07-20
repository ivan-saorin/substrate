# Multi-stage build for substrate MCP server
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY main.py .

# Copy documentation
COPY docs/ ./docs/

# Create data directory
RUN mkdir -p /app/data/refs

# Environment variables for instance configuration
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio
ENV INSTANCE_TYPE=substrate
ENV INSTANCE_DESCRIPTION="Cognitive manipulation substrate"
ENV DATA_DIR=/app/data
ENV LOG_LEVEL=INFO

# Run the server
CMD ["python", "main.py"]
