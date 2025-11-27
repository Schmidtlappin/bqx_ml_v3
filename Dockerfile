# BQX ML V3 Vertex AI Optimized Container
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY system_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r system_requirements.txt

# Install Vertex AI SDK
RUN pip install --no-cache-dir google-cloud-aiplatform==1.38.0

# Copy entire project
COPY . .

# Copy current results to preserve progress (if they exist)
COPY extended_lags_results.json /app/ 2>/dev/null || :
COPY triangulation_results_v2.json /app/ 2>/dev/null || :

# Set environment variables for GCP and Vertex AI
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-sa-key.json
ENV PYTHONPATH=/app
ENV VERTEX_AI_PROJECT=bqx-ml
ENV VERTEX_AI_LOCATION=us-east1
ENV PYTHONUNBUFFERED=1

# Create the comprehensive testing orchestrator script
RUN echo '#!/usr/bin/env python3\n\
import os\n\
import subprocess\n\
import json\n\
import time\n\
from datetime import datetime\n\
\n\
def run_comprehensive_testing():\n\
    """Run all testing phases with maximum parallelization"""\n\
    print(f"Starting comprehensive testing at {datetime.now()}")\n\
    \n\
    # Phase 1: Complete triangulation testing\n\
    print("Phase 1: Triangulation testing...")\n\
    subprocess.run(["python3", "scripts/comprehensive_triangulation_testing.py"])\n\
    \n\
    # Phase 2: Correlation networks\n\
    print("Phase 2: Correlation network testing...")\n\
    subprocess.run(["python3", "scripts/test_correlation_network.py"])\n\
    \n\
    # Phase 3: Extended lags (if not complete)\n\
    print("Phase 3: Extended lag testing...")\n\
    subprocess.run(["python3", "scripts/comprehensive_extended_lags_testing.py"])\n\
    \n\
    # Phase 4: Algorithm comparison\n\
    print("Phase 4: Algorithm comparison...")\n\
    subprocess.run(["python3", "scripts/comprehensive_algorithm_testing.py"])\n\
    \n\
    print(f"Testing completed at {datetime.now()}")\n\
    \n\
    # Upload results to GCS\n\
    os.system("gsutil cp *results*.json gs://bqx-ml/test-results/")\n\
    print("Results uploaded to GCS")\n\
\n\
if __name__ == "__main__":\n\
    run_comprehensive_testing()\n\
' > /app/run_all_tests.py

RUN chmod +x /app/run_all_tests.py

# Default command
CMD ["python3", "/app/run_all_tests.py"]