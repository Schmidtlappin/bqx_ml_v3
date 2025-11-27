
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
