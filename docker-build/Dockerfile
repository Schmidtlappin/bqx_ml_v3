# Dockerfile for BQX ML V3 Comprehensive Testing
# Optimized for Vertex AI execution

FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy testing scripts
COPY scripts/ ./scripts/
COPY configs/ ./configs/

# Copy saved test results from GCS (will be mounted at runtime)
# VOLUME ["/app/results"]

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-sa-key.json

# Entry point for Vertex AI
ENTRYPOINT ["python", "-u"]