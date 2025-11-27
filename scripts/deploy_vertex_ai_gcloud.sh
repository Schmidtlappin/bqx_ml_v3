#!/bin/bash

# VERTEX AI DEPLOYMENT USING GCLOUD CLI
# Since Python SDK fails but gcloud works, using CLI directly
# Based on CE Resolution: 20251127_0505_CE_BA_RESOLUTION

echo "======================================================================="
echo "🚀 VERTEX AI DEPLOYMENT VIA GCLOUD CLI"
echo "Using gcloud since Python SDK has permission issues"
echo "======================================================================="

# Configuration
PROJECT="bqx-ml"
REGION="us-central1"  # CE directive: use us-central1
SERVICE_ACCOUNT="vertex-ai-bqx@bqx-ml.iam.gserviceaccount.com"
BUCKET="gs://bqx-ml-bqx-ml-artifacts"

# Currency pairs and windows
PAIRS=("eurusd" "gbpusd")  # Start with 2 for testing
WINDOWS=(45 90)

# Counter for jobs
JOB_COUNT=0
SUCCESSFUL_JOBS=0
FAILED_JOBS=0

# First verify we can submit jobs
echo -e "\n✅ Testing permissions with simple job..."
gcloud ai custom-jobs create \
  --region=$REGION \
  --display-name="permission-test-$(date +%s)" \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=gcr.io/deeplearning-platform-release/base-cpu.py310 \
  --command='["echo", "Permissions work via gcloud CLI"]' \
  --service-account=$SERVICE_ACCOUNT \
  --project=$PROJECT 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Permission test successful!"
else
    echo "❌ Permission test failed. Exiting."
    exit 1
fi

echo -e "\n📊 Submitting training jobs for BQX ML V3 models..."

# Loop through pairs and windows
for PAIR in "${PAIRS[@]}"; do
    for WINDOW in "${WINDOWS[@]}"; do
        JOB_COUNT=$((JOB_COUNT + 1))
        JOB_NAME="bqx-ml-v3-${PAIR}-${WINDOW}-$(date +%Y%m%d%H%M%S)"

        echo -e "\n🚀 Job $JOB_COUNT: ${PAIR^^}-$WINDOW"
        echo "  Table: bqx_ml_v3_features.${PAIR}_bqx"
        echo "  Columns: bqx_$WINDOW, target_$WINDOW (CORRECTED)"

        # Create Python training script for this specific model
        cat > /tmp/train_${PAIR}_${WINDOW}.py << 'EOF'
import sys
import pandas as pd
import numpy as np
from google.cloud import bigquery, storage
import xgboost as xgb
from sklearn.metrics import r2_score, accuracy_score
import joblib
import os

# Get environment variables set by gcloud
pair = os.environ.get('PAIR', 'eurusd')
window = int(os.environ.get('WINDOW', '45'))

print(f"Training {pair.upper()}-{window} on Vertex AI")
print("Using CORRECTED BigQuery schema: bqx_{window}, target_{window}")

# Initialize clients
client = bigquery.Client(project='bqx-ml')
storage_client = storage.Client(project='bqx-ml')

# CORRECTED QUERY with actual column names
query = f"""
SELECT
    interval_time,
    bqx_{window} as feature,
    target_{window} as target
FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
WHERE target_{window} IS NOT NULL
LIMIT 10000
"""

print(f"Querying: {query[:100]}...")

try:
    data = client.query(query).to_dataframe()
    print(f"✅ Loaded {len(data)} rows")

    if len(data) > 100:
        # Simple model training
        X = data[['feature']].values
        y = data['target'].values

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Train XGBoost
        model = xgb.XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate
        predictions = model.predict(X_test)
        r2 = r2_score(y_test, predictions)
        print(f"✅ R² Score: {r2:.4f}")

        # Save model
        model_filename = f'model_{pair}_{window}.pkl'
        joblib.dump(model, f'/tmp/{model_filename}')

        # Upload to GCS
        bucket = storage_client.bucket('bqx-ml-bqx-ml-models')
        blob = bucket.blob(f'vertex_gcloud/{model_filename}')
        blob.upload_from_filename(f'/tmp/{model_filename}')

        print(f"✅ Model saved to GCS: gs://bqx-ml-bqx-ml-models/vertex_gcloud/{model_filename}")
        print(f"✅ SUCCESS: {pair.upper()}-{window} training complete!")
    else:
        print(f"⚠️ Not enough data: {len(data)} rows")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF

        # Submit job using gcloud CLI
        echo "  Submitting to Vertex AI via gcloud..."

        gcloud ai custom-jobs create \
          --region=$REGION \
          --display-name=$JOB_NAME \
          --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=gcr.io/deeplearning-platform-release/base-cpu.py310 \
          --command='["python3", "/tmp/train_'${PAIR}'_'${WINDOW}'.py"]' \
          --service-account=$SERVICE_ACCOUNT \
          --project=$PROJECT \
          --env="PAIR=${PAIR},WINDOW=${WINDOW}" \
          --async 2>&1

        if [ $? -eq 0 ]; then
            echo "  ✅ Job submitted successfully!"
            SUCCESSFUL_JOBS=$((SUCCESSFUL_JOBS + 1))
        else
            echo "  ❌ Job submission failed!"
            FAILED_JOBS=$((FAILED_JOBS + 1))
        fi

        # Small delay between submissions
        sleep 2
    done
done

echo -e "\n======================================================================="
echo "🚀 DEPLOYMENT SUMMARY"
echo "======================================================================="
echo "Total jobs: $JOB_COUNT"
echo "✅ Successful: $SUCCESSFUL_JOBS"
echo "❌ Failed: $FAILED_JOBS"
echo ""
echo "Monitor jobs at:"
echo "https://console.cloud.google.com/vertex-ai/training/custom-jobs?project=$PROJECT"
echo ""
echo "Or via CLI:"
echo "gcloud ai custom-jobs list --region=$REGION --project=$PROJECT"
echo "======================================================================="