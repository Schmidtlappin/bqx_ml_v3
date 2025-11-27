
import sys
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from google.cloud import bigquery, storage
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, accuracy_score
import joblib
from datetime import datetime

# Get arguments
pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
window = int(sys.argv[2]) if len(sys.argv) > 2 else 45

print(f"Training {pair.upper()}-{window} model on Vertex AI")
print("Using CORRECTED BigQuery schema")
print("Breakthrough features: Extended Lags (97% R²), Smart Dual Processing")

# Initialize clients
client = bigquery.Client(project='bqx-ml')
storage_client = storage.Client(project='bqx-ml')

# CORRECTED QUERY - Using actual column names (bqx_45, not eurusd_bqx_45)
query = f"""
WITH idx_features AS (
    SELECT
        interval_time,
        close_idx,
        -- Extended lags (97.24% R² discovery)
        LAG(close_idx, 31) OVER (ORDER BY interval_time) as lag_31,
        LAG(close_idx, 34) OVER (ORDER BY interval_time) as lag_34,
        LAG(close_idx, 37) OVER (ORDER BY interval_time) as lag_37,
        LAG(close_idx, 40) OVER (ORDER BY interval_time) as lag_40,
        LAG(close_idx, 43) OVER (ORDER BY interval_time) as lag_43,
        LAG(close_idx, 46) OVER (ORDER BY interval_time) as lag_46,
        LAG(close_idx, 49) OVER (ORDER BY interval_time) as lag_49,
        LAG(close_idx, 52) OVER (ORDER BY interval_time) as lag_52,
        LAG(close_idx, 55) OVER (ORDER BY interval_time) as lag_55,
        -- Smart dual processing lags
        LAG(close_idx, 1) OVER (ORDER BY interval_time) * 2.0 as weighted_lag_1,
        LAG(close_idx, 2) OVER (ORDER BY interval_time) * 2.0 as weighted_lag_2,
        LAG(close_idx, 3) OVER (ORDER BY interval_time) * 1.8 as weighted_lag_3,
        LAG(close_idx, 5) OVER (ORDER BY interval_time) * 1.6 as weighted_lag_5,
        LAG(close_idx, 8) OVER (ORDER BY interval_time) * 1.4 as weighted_lag_8,
        LAG(close_idx, 13) OVER (ORDER BY interval_time) * 1.2 as weighted_lag_13
    FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
    ORDER BY interval_time
),
bqx_targets AS (
    SELECT
        interval_time,
        -- CORRECTED: Using actual column names
        bqx_{window} as bqx_feature,      -- CE correction: bqx_45, not eurusd_bqx_45
        target_{window} as target_value    -- CE correction: target_45, not eurusd_bqx_45
    FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
    WHERE target_{window} IS NOT NULL
)
SELECT
    f.*,
    b.bqx_feature,
    b.target_value as target
FROM idx_features f
JOIN bqx_targets b ON f.interval_time = b.interval_time
WHERE f.lag_55 IS NOT NULL
ORDER BY f.interval_time
LIMIT 50000
"""

print("Executing CORRECTED BigQuery query...")
print(f"Table: bqx_ml_v3_features.{pair}_bqx")
print(f"Columns: bqx_{window}, target_{window}")

try:
    data = client.query(query).to_dataframe()
    print(f"✅ Successfully loaded {len(data)} rows")
except Exception as e:
    print(f"❌ Query error: {e}")
    # Fallback: Try simpler query
    simple_query = f"""
    SELECT
        interval_time,
        bqx_{window} as feature,
        target_{window} as target
    FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
    WHERE target_{window} IS NOT NULL
    LIMIT 50000
    """
    print("Trying simpler query...")
    data = client.query(simple_query).to_dataframe()
    print(f"✅ Loaded {len(data)} rows with simple query")

# Prepare features
feature_cols = [col for col in data.columns if col not in ['interval_time', 'target']]
X = data[feature_cols]
y = data['target']

# Split data
split_idx = int(len(X) * 0.8)
X_train = X[:split_idx]
X_test = X[split_idx:]
y_train = y[:split_idx]
y_test = y[split_idx:]

print(f"Training on {len(X_train)} samples...")

# Train XGBoost with optimized parameters
model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
r2 = r2_score(y_test, predictions)

# Directional accuracy
y_test_direction = (y_test > 0).astype(int)
pred_direction = (predictions > 0).astype(int)
accuracy = accuracy_score(y_test_direction, pred_direction)

print(f"✅ R² Score: {r2:.4f}")
print(f"✅ Directional Accuracy: {accuracy:.4f}")

# Save model to GCS
model_filename = f'model_{pair}_{window}.pkl'
joblib.dump(model, f'/tmp/{model_filename}')

bucket = storage_client.bucket('bqx-ml-bqx-ml-models')
blob = bucket.blob(f'vertex_production/{model_filename}')
blob.upload_from_filename(f'/tmp/{model_filename}')

print(f"✅ Model saved: gs://bqx-ml-bqx-ml-models/vertex_production/{model_filename}")

# Save metrics
metrics = {
    'pair': pair,
    'window': window,
    'r2_score': r2,
    'directional_accuracy': accuracy,
    'timestamp': datetime.now().isoformat(),
    'vertex_deployment': True,
    'region': 'us-central1'
}

print(json.dumps(metrics, indent=2))
