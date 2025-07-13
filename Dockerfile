FROM python:3.12-slim

WORKDIR /app

# Copy the entire substrate directory
COPY substrate /app

# Install the package
RUN pip install --no-cache-dir -e .

# Environment
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "-m", "substrate"]
