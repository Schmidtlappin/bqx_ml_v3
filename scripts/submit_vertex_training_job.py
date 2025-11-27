#!/usr/bin/env python3
"""
Submit BQX ML V3 Training Jobs to Vertex AI
Direct execution without custom containers
Authorization: ALPHA-2B-COMPREHENSIVE
"""

import os
from datetime import datetime
from google.cloud import aiplatform
from google.cloud import bigquery
import json

# Constants
PROJECT_ID = 'bqx-ml'
LOCATION = 'us-east1'
STAGING_BUCKET = 'gs://bqx-ml-bqx-ml-artifacts'
SERVICE_ACCOUNT = 'vertex-ai-bqx@bqx-ml.iam.gserviceaccount.com'

# Currency pairs for 196 models
CURRENCY_PAIRS = [
    'eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad', 'nzdusd', 'usdchf',
    'eurjpy', 'eurgbp', 'eurchf', 'gbpjpy', 'audjpy', 'cadjpy', 'euraud'
]

# BQX windows
WINDOWS = [45, 90]

def create_training_script():
    """Create the training script for Vertex AI"""

    script_content = '''
import sys
import json
import pandas as pd
import xgboost as xgb
from google.cloud import bigquery, storage
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
import joblib
from datetime import datetime

# Parse arguments
pair = sys.argv[1]
window = int(sys.argv[2])
features = sys.argv[3].split(',') if len(sys.argv) > 3 else ['smart_dual']

print(f"Training model for {pair} with window {window}")
print(f"Using features: {features}")

# Initialize BigQuery client
client = bigquery.Client(project='bqx-ml')

# Load data with best features discovered
query = f"""
WITH idx_data AS (
    SELECT
        interval_time,
        close_idx,
        LAG(close_idx, 1) OVER (ORDER BY interval_time) as idx_lag_1,
        LAG(close_idx, 2) OVER (ORDER BY interval_time) as idx_lag_2,
        LAG(close_idx, 3) OVER (ORDER BY interval_time) as idx_lag_3,
        LAG(close_idx, 5) OVER (ORDER BY interval_time) as idx_lag_5,
        LAG(close_idx, 8) OVER (ORDER BY interval_time) as idx_lag_8,
        LAG(close_idx, 13) OVER (ORDER BY interval_time) as idx_lag_13,
        LAG(close_idx, 21) OVER (ORDER BY interval_time) as idx_lag_21,
        LAG(close_idx, 34) OVER (ORDER BY interval_time) as idx_lag_34,
        LAG(close_idx, 55) OVER (ORDER BY interval_time) as idx_lag_55
    FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
    WHERE interval_time >= '2024-01-01'
    ORDER BY interval_time
),
bqx_data AS (
    SELECT
        interval_time,
        {pair}_bqx_{window} as target,
        LAG({pair}_bqx_{window}, 1) OVER (ORDER BY interval_time) as bqx_lag_1,
        LAG({pair}_bqx_{window}, 2) OVER (ORDER BY interval_time) as bqx_lag_2,
        LAG({pair}_bqx_{window}, 3) OVER (ORDER BY interval_time) as bqx_lag_3,
        LAG({pair}_bqx_{window}, 5) OVER (ORDER BY interval_time) as bqx_lag_5,
        LAG({pair}_bqx_{window}, 8) OVER (ORDER BY interval_time) as bqx_lag_8
    FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
    WHERE interval_time >= '2024-01-01'
    ORDER BY interval_time
)
SELECT
    idx.*,
    bqx.target,
    bqx.bqx_lag_1,
    bqx.bqx_lag_2,
    bqx.bqx_lag_3,
    bqx.bqx_lag_5,
    bqx.bqx_lag_8
FROM idx_data idx
JOIN bqx_data bqx ON idx.interval_time = bqx.interval_time
WHERE idx.idx_lag_55 IS NOT NULL
ORDER BY idx.interval_time
LIMIT 50000
"""

print("Loading data from BigQuery...")
data = client.query(query).to_dataframe()
print(f"Loaded {len(data)} rows")

# Prepare features and target
feature_cols = [col for col in data.columns if col not in ['interval_time', 'target']]
X = data[feature_cols]
y = data['target']

# Remove NaN values
mask = ~y.isna()
X = X[mask]
y = y[mask]

# Split data (80/20)
split_idx = int(len(X) * 0.8)
X_train = X[:split_idx]
X_test = X[split_idx:]
y_train = y[:split_idx]
y_test = y[split_idx:]

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Train XGBoost model
model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

print("Training model...")
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

# Calculate directional accuracy
y_test_direction = (y_test > 0).astype(int)
pred_direction = (predictions > 0).astype(int)
accuracy = accuracy_score(y_test_direction, pred_direction)

print(f"R² Score: {r2:.4f}")
print(f"Directional Accuracy: {accuracy:.4f}")

# Save model to GCS
storage_client = storage.Client()
bucket = storage_client.bucket('bqx-ml-bqx-ml-models')
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

model_filename = f'/tmp/model_{pair}_{window}.pkl'
joblib.dump(model, model_filename)

blob_name = f'vertex_models/{pair}_{window}_{timestamp}.pkl'
blob = bucket.blob(blob_name)
blob.upload_from_filename(model_filename)

print(f"Model saved to gs://bqx-ml-bqx-ml-models/{blob_name}")

# Save metrics
metrics = {
    'pair': pair,
    'window': window,
    'r2_score': r2,
    'directional_accuracy': accuracy,
    'features_used': feature_cols,
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'timestamp': datetime.now().isoformat()
}

metrics_blob = bucket.blob(f'vertex_metrics/{pair}_{window}_{timestamp}.json')
metrics_blob.upload_from_string(json.dumps(metrics, indent=2))

print("Training complete!")
print(json.dumps(metrics, indent=2))
'''

    # Save training script
    with open('/home/micha/bqx_ml_v3/scripts/vertex_training_script.py', 'w') as f:
        f.write(script_content)

    return '/home/micha/bqx_ml_v3/scripts/vertex_training_script.py'

def submit_training_jobs():
    """Submit training jobs to Vertex AI"""

    # Initialize Vertex AI
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    # Create training script
    script_path = create_training_script()
    print(f"Training script created: {script_path}")

    jobs = []
    job_count = 0

    # Submit jobs for each pair and window combination
    for pair in CURRENCY_PAIRS:
        for window in WINDOWS:
            job_count += 1

            # Define the custom job
            job_display_name = f'bqx-ml-v3-{pair}-{window}-{datetime.now().strftime("%Y%m%d%H%M%S")}'

            # Create custom job using pre-built container
            job = aiplatform.CustomJob(
                display_name=job_display_name,
                worker_pool_specs=[
                    {
                        "machine_spec": {
                            "machine_type": "n1-standard-4",
                        },
                        "replica_count": 1,
                        "container_spec": {
                            "image_uri": "gcr.io/cloud-aiplatform/training/tf-cpu.2-11:latest",
                            "command": ["python3"],
                            "args": [
                                "vertex_training_script.py",
                                pair,
                                str(window),
                                "smart_dual,extended_lags,triangulation"
                            ],
                        },
                    }
                ],
                staging_bucket=STAGING_BUCKET,
            )

            # Submit the job
            print(f"Submitting job {job_count}/196: {pair}_{window}")
            job.submit(
                service_account=SERVICE_ACCOUNT,
                network=f"projects/{PROJECT_ID}/global/networks/default",
            )

            jobs.append({
                'job_name': job_display_name,
                'pair': pair,
                'window': window,
                'job_id': job.name
            })

            # Save job info
            if job_count % 10 == 0:
                with open(f'/home/micha/bqx_ml_v3/vertex_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                    json.dump(jobs, f, indent=2)
                print(f"Saved job info for {job_count} jobs")

    # Save final job list
    final_output = {
        'submission_time': datetime.now().isoformat(),
        'total_jobs': len(jobs),
        'jobs': jobs,
        'project': PROJECT_ID,
        'location': LOCATION
    }

    output_file = f'/home/micha/bqx_ml_v3/vertex_training_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"\n{'='*70}")
    print(f"VERTEX AI TRAINING JOBS SUBMITTED")
    print(f"{'='*70}")
    print(f"Total jobs: {len(jobs)}")
    print(f"Currency pairs: {len(CURRENCY_PAIRS)}")
    print(f"Windows: {len(WINDOWS)}")
    print(f"Jobs list saved to: {output_file}")
    print(f"Monitor at: https://console.cloud.google.com/vertex-ai/training/custom-jobs?project={PROJECT_ID}")
    print(f"{'='*70}")

    return jobs

if __name__ == "__main__":
    # Create training script first
    script_path = create_training_script()
    print(f"Training script created at: {script_path}")
    print("\nTo submit training jobs, uncomment the next line:")
    print("# submit_training_jobs()")
    print("\nOr run: python submit_vertex_training_job.py --submit")