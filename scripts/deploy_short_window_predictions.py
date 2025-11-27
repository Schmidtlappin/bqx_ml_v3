#!/usr/bin/env python3
"""
Deploy SHORT WINDOW predictions for forex trading
Focuses on 15, 30, 45, 60 minute predictions for optimal trading outcomes
These shorter windows are more practical for real forex trading decisions
"""

import os
from google.cloud import aiplatform, bigquery, storage
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle
import time
from datetime import datetime

# Configuration
PROJECT_ID = 'bqx-ml-v3'
DATASET_ID = 'bqx_features'
BUCKET_NAME = 'bqx-ml-vertex-models'
REGION = 'us-central1'

# Initialize
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)

# CRITICAL: Use prebuilt sklearn container
SKLEARN_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"

# SHORT WINDOW MODELS - More practical for forex trading
CRITICAL_MODELS = [
    ('EUR_USD', 15),  # 15-minute predictions - ultra short term
    ('EUR_USD', 30),  # 30-minute predictions - short term
    ('EUR_USD', 45),  # 45-minute predictions - medium short
    ('GBP_USD', 30),  # Focus on major pairs
    ('USD_JPY', 30),  # Most liquid pairs
]

def create_short_term_features(df, window):
    """
    Create features optimized for short-term forex predictions
    Short windows need different features than long windows
    """
    print(f"  🔧 Engineering short-term features for {window}-minute window...")

    # BQX columns
    bqx_col = f'bqx_{window}'

    # For short windows, focus on recent momentum
    if window <= 30:
        # Ultra short-term features (1-5 candles back)
        for lag in [1, 2, 3, 4, 5]:
            df[f'bqx_lag_{lag}'] = df[bqx_col].shift(lag)

        # Quick moving averages
        for ma in [3, 5, 8]:
            df[f'bqx_ma_{ma}'] = df[bqx_col].rolling(window=ma).mean()

        # Immediate momentum
        df['bqx_momentum_1'] = df[bqx_col] - df[bqx_col].shift(1)
        df['bqx_momentum_3'] = df[bqx_col] - df[bqx_col].shift(3)

    else:  # 45-60 minute windows
        # Medium-term features
        for lag in [1, 2, 3, 5, 10, 15]:
            df[f'bqx_lag_{lag}'] = df[bqx_col].shift(lag)

        # Broader moving averages
        for ma in [5, 10, 15, 20]:
            df[f'bqx_ma_{ma}'] = df[bqx_col].rolling(window=ma).mean()

        # Medium momentum
        df['bqx_momentum_5'] = df[bqx_col] - df[bqx_col].shift(5)
        df['bqx_momentum_10'] = df[bqx_col] - df[bqx_col].shift(10)

    # Volatility (critical for short-term)
    df['bqx_volatility'] = df[bqx_col].rolling(window=min(10, window//3)).std()

    # Price action patterns
    df['bqx_high_low_ratio'] = df[bqx_col].rolling(window=min(5, window//3)).max() / df[bqx_col].rolling(window=min(5, window//3)).min()

    # Trading session features (very important for forex)
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    df['minute'] = pd.to_datetime(df['timestamp']).dt.minute
    df['is_london_open'] = ((df['hour'] == 8) & (df['minute'] < 30)).astype(int)
    df['is_ny_open'] = ((df['hour'] == 13) & (df['minute'] < 30)).astype(int)
    df['is_overlap'] = ((df['hour'] >= 13) & (df['hour'] <= 16)).astype(int)

    # Drop NaN
    df = df.dropna()

    print(f"    ✅ Created {len(df.columns)} features optimized for {window}-minute predictions")
    return df

def train_short_window_model(pair, window):
    """
    Train model optimized for short-term predictions
    """
    print(f"\n{'='*60}")
    print(f"🎯 Training {pair} {window}-minute prediction model")
    print(f"{'='*60}")

    # Load recent data (short windows need fresh data)
    query = f"""
    WITH recent_data AS (
        SELECT
            timestamp,
            bqx_{window} as bqx_{window},
            LEAD(bqx_{window}, 1) OVER (ORDER BY timestamp) as target_{window}
        FROM `{PROJECT_ID}.{DATASET_ID}.{pair.lower()}_features_bqx`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        ORDER BY timestamp DESC
        LIMIT 20000
    )
    SELECT * FROM recent_data
    WHERE target_{window} IS NOT NULL
    """

    try:
        df = bq_client.query(query).to_dataframe()
        print(f"  ✅ Loaded {len(df)} rows of recent data")
    except Exception as e:
        print(f"  ❌ Failed to load data: {e}")
        return None, 0, []

    # Engineer features
    df = create_short_term_features(df, window)

    # Prepare for training
    target_col = f'target_{window}'
    feature_cols = [col for col in df.columns if col not in ['timestamp', target_col]]

    X = df[feature_cols]
    y = df[target_col]

    # Split data (no shuffle for time series)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Train model (lighter for short windows - need speed)
    if window <= 30:
        # Faster model for ultra-short predictions
        model = RandomForestRegressor(
            n_estimators=100,  # Fewer trees for speed
            max_depth=10,      # Shallower for speed
            min_samples_split=20,
            n_jobs=-1,
            random_state=42
        )
    else:
        # More complex model for 45-60 min
        model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_split=15,
            n_jobs=-1,
            random_state=42
        )

    # Train
    model.fit(X_train, y_train)

    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print(f"  📊 Training R²: {train_score:.4f}")
    print(f"  📊 Testing R²: {test_score:.4f}")

    # For short windows, directional accuracy is more important than R²
    y_pred = model.predict(X_test)
    direction_accuracy = np.mean((y_pred > 0) == (y_test > 0))
    print(f"  🎯 Directional Accuracy: {direction_accuracy:.2%}")

    return model, test_score, feature_cols

def deploy_model(model, pair, window, feature_cols):
    """
    Deploy model to Vertex AI
    """
    model_name = f"{pair}_{window}"
    print(f"\n  🚀 Deploying {model_name}...")

    try:
        # Save model
        model_dir = f"/tmp/{model_name}"
        os.makedirs(model_dir, exist_ok=True)

        with open(f"{model_dir}/model.pkl", 'wb') as f:
            pickle.dump(model, f, protocol=4)

        with open(f"{model_dir}/features.pkl", 'wb') as f:
            pickle.dump(feature_cols, f)

        # Upload to GCS
        bucket = storage_client.bucket(BUCKET_NAME)
        for file in ['model.pkl', 'features.pkl']:
            blob = bucket.blob(f"{model_name}/{file}")
            blob.upload_from_filename(f"{model_dir}/{file}")

        print(f"    ✅ Uploaded to gs://{BUCKET_NAME}/{model_name}/")

        # Upload to Vertex AI
        vertex_model = aiplatform.Model.upload(
            display_name=f"bqx-{model_name}-short",
            artifact_uri=f"gs://{BUCKET_NAME}/{model_name}/",
            serving_container_image_uri=SKLEARN_CONTAINER,
            sync=False
        )

        # Create endpoint
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_name}-endpoint",
            sync=False
        )

        # Deploy
        endpoint.deploy(
            model=vertex_model,
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=2,
            traffic_percentage=100,
            sync=False
        )

        print(f"    ✅ Deployment initiated")
        return True

    except Exception as e:
        print(f"    ❌ Deployment failed: {e}")
        return False

def main():
    """
    Main deployment for short-window predictions
    """
    print("="*80)
    print("🚀 SHORT-WINDOW FOREX PREDICTION DEPLOYMENT")
    print("="*80)
    print("Focus: 15, 30, 45, 60 minute predictions")
    print("Purpose: Real-time forex trading decisions")
    print("Container: Prebuilt SKLearn (Google-maintained)")
    print("="*80)

    results = []

    for pair, window in CRITICAL_MODELS:
        # Train model
        model, r2_score, feature_cols = train_short_window_model(pair, window)

        if model is None:
            continue

        # Deploy
        success = deploy_model(model, pair, window, feature_cols)

        results.append({
            'pair': pair,
            'window': window,
            'r2_score': r2_score,
            'deployed': success
        })

        # Brief pause
        time.sleep(5)

    # Summary
    print("\n" + "="*80)
    print("📊 DEPLOYMENT SUMMARY")
    print("="*80)

    for result in results:
        status = "✅" if result['deployed'] else "❌"
        print(f"{status} {result['pair']}_{result['window']}min: R²={result['r2_score']:.4f}")

    print("\n💡 Why short windows?")
    print("  • 15-min: Scalping and high-frequency trading")
    print("  • 30-min: Day trading sweet spot")
    print("  • 45-min: Intraday swing trading")
    print("  • 60-min: Short-term trend following")

    print("\n📈 Trading Applications:")
    print("  • Entry/exit timing for forex positions")
    print("  • Stop-loss and take-profit optimization")
    print("  • Risk management for open positions")
    print("  • Automated trading signal generation")

    print(f"\n✅ Deployment completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()