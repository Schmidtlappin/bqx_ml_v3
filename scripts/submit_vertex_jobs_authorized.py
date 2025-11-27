#!/usr/bin/env python3
"""
Submit BQX ML V3 Training Jobs to Vertex AI
AUTHORIZED DEPLOYMENT - ALPHA-2B-COMPREHENSIVE
"""

import os
import sys
from datetime import datetime
from google.cloud import aiplatform
from google.cloud import bigquery
import json

# Constants
PROJECT_ID = 'bqx-ml'
LOCATION = 'us-east1'
STAGING_BUCKET = 'gs://bqx-ml-bqx-ml-artifacts'
SERVICE_ACCOUNT = 'vertex-ai-bqx@bqx-ml.iam.gserviceaccount.com'

# First batch of pairs to test
CURRENCY_PAIRS = ['eurusd', 'gbpusd', 'usdjpy', 'audusd']  # Start with 4 pairs for initial test
WINDOWS = [45, 90]

def main():
    """Submit training jobs to Vertex AI"""

    print("="*70)
    print("VERTEX AI DEPLOYMENT - AUTHORIZED")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("="*70)

    # Initialize Vertex AI
    print("\nInitializing Vertex AI...")
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    jobs = []
    job_count = 0

    # First, let's submit a single test job to verify everything works
    print("\n📊 Submitting test job for EURUSD-45...")

    test_job_name = f'bqx-ml-v3-test-eurusd-45-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    # Create a simple training script inline
    training_code = '''
import sys
import json
from datetime import datetime

print("Vertex AI Training Job Started")
print(f"Arguments: {sys.argv}")
print(f"Timestamp: {datetime.now().isoformat()}")

# For now, just test the job submission
pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
window = sys.argv[2] if len(sys.argv) > 2 else "45"

print(f"Training model for {pair} with window {window}")
print("Job completed successfully (test mode)")

# Save a test result
result = {
    "pair": pair,
    "window": window,
    "status": "test_complete",
    "timestamp": datetime.now().isoformat()
}

print(json.dumps(result, indent=2))
'''

    # Save training script
    script_path = '/home/micha/bqx_ml_v3/scripts/vertex_test_script.py'
    with open(script_path, 'w') as f:
        f.write(training_code)

    print(f"Training script saved: {script_path}")

    # Create custom job
    job = aiplatform.CustomJob(
        display_name=test_job_name,
        worker_pool_specs=[
            {
                "machine_spec": {
                    "machine_type": "n1-standard-2",  # Smaller instance for test
                },
                "replica_count": 1,
                "container_spec": {
                    "image_uri": "gcr.io/deeplearning-platform-release/base-cpu:latest",
                    "command": ["python3", "-c", training_code],
                    "args": ["eurusd", "45", "test_mode"],
                },
            }
        ],
        staging_bucket=STAGING_BUCKET,
    )

    print(f"Submitting test job: {test_job_name}")

    try:
        job.submit(
            service_account=SERVICE_ACCOUNT,
            timeout=1800,  # 30 minutes timeout
        )

        print(f"✅ Test job submitted successfully!")
        print(f"Job Name: {job.display_name}")
        print(f"Job Resource: {job.resource_name}")

        # Save job info
        job_info = {
            'submission_time': datetime.now().isoformat(),
            'job_name': test_job_name,
            'type': 'test',
            'pair': 'eurusd',
            'window': 45,
            'status': 'submitted',
            'resource_name': job.resource_name,
            'project': PROJECT_ID,
            'location': LOCATION
        }

        output_file = f'/home/micha/bqx_ml_v3/vertex_test_job_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(job_info, f, indent=2)

        print(f"\n📊 Job details saved to: {output_file}")
        print(f"\n🔍 Monitor at:")
        print(f"https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={PROJECT_ID}")

        print("\n" + "="*70)
        print("TEST JOB SUBMITTED SUCCESSFULLY")
        print("="*70)

        print("\n⚡ Next Steps:")
        print("1. Verify test job completes successfully")
        print("2. Submit remaining 195 production jobs")
        print("3. Monitor training progress")
        print("4. Deploy models to endpoints")

        return job_info

    except Exception as e:
        print(f"❌ Error submitting job: {str(e)}")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print("\n✅ Vertex AI deployment initiated successfully!")
    else:
        print("\n❌ Deployment failed - check errors above")