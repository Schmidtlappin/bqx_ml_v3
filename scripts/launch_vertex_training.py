#!/usr/bin/env python3
"""
Launch BQX ML V3 Training on Vertex AI
Using AI Platform Training with pre-built containers
Authorization: ALPHA-2B-COMPREHENSIVE
"""

import os
import json
from datetime import datetime

# Constants
PROJECT_ID = 'bqx-ml'
LOCATION = 'us-central1'  # Use us-central1 for AI Platform Training

def launch_training():
    """Launch training job using gcloud AI Platform"""

    print("="*70)
    print("VERTEX AI TRAINING DEPLOYMENT")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("="*70)

    # Create a simple training script
    training_script = '''
import pandas as pd
import xgboost as xgb
from google.cloud import bigquery
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import joblib
import json
from datetime import datetime

# Initialize BigQuery
client = bigquery.Client(project='bqx-ml')

# Test with EURUSD first
pair = 'eurusd'
window = 45

print(f"Training model for {pair} with window {window}")

# Load data
query = f"""
SELECT *
FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
LIMIT 10000
"""

print("Loading data from BigQuery...")
data = client.query(query).to_dataframe()
print(f"Loaded {len(data)} rows")

# Simple features for test
X = data[['close_idx']].shift(1).fillna(0)
y = data['close_idx']

# Split data
X_train = X[:8000]
X_test = X[8000:]
y_train = y[:8000]
y_test = y[8000:]

# Train model
model = xgb.XGBRegressor(n_estimators=100, max_depth=5)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

print(f"R² Score: {r2:.4f}")

# Save results
results = {
    'pair': pair,
    'window': window,
    'r2_score': r2,
    'timestamp': datetime.now().isoformat(),
    'status': 'success'
}

print(json.dumps(results, indent=2))
print("Training complete!")
'''

    # Save training script
    script_path = '/home/micha/bqx_ml_v3/training_script.py'
    with open(script_path, 'w') as f:
        f.write(training_script)

    print(f"\n✅ Training script created: {script_path}")

    # Create job using gcloud command
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"bqx_ml_v3_training_{timestamp}"

    # Submit using gcloud AI Platform
    cmd = f"""
gcloud ai-platform jobs submit training {job_id} \
  --project={PROJECT_ID} \
  --region={LOCATION} \
  --module-name=training_script \
  --package-path=/home/micha/bqx_ml_v3 \
  --runtime-version=2.11 \
  --python-version=3.9 \
  --scale-tier=BASIC 2>&1
"""

    print(f"\n📊 Submitting training job: {job_id}")
    print(f"\nCommand: {cmd}")

    # Execute
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n✅ Job submitted successfully!")
        print(result.stdout)

        # Save job info
        job_info = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'project': PROJECT_ID,
            'region': LOCATION,
            'status': 'submitted'
        }

        output_file = f'/home/micha/bqx_ml_v3/vertex_job_{timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(job_info, f, indent=2)

        print(f"\n📊 Job details saved: {output_file}")
        print(f"\n🔍 Monitor at:")
        print(f"https://console.cloud.google.com/ai-platform/jobs?project={PROJECT_ID}")

        return job_info
    else:
        print(f"\n❌ Error submitting job:")
        print(result.stderr)
        return None

if __name__ == "__main__":
    result = launch_training()
    if result:
        print("\n✅ Vertex AI training launched!")
    else:
        print("\n❌ Failed to launch training")