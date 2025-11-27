#!/usr/bin/env python3
"""
Simplified Multi-Horizon BQX Prediction Models
Uses existing BQX tables to predict multiple future horizons
"""

import os
import pickle
import pandas as pd
import numpy as np
from google.cloud import bigquery, storage, aiplatform
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'bqx-ml'  # Using accessible project
DATASET_ID = 'bqx_ml_v3_features'  # Correct dataset name
BUCKET_NAME = 'bqx-ml-vertex-models'
REGION = 'us-central1'

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)

# Multi-Horizon Configuration
FEATURE_WINDOWS = [45, 90]  # BQX windows to use as features
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # Future intervals to predict

# Critical models for real-time deployment
CRITICAL_PAIRS = ['EUR_USD', 'GBP_USD', 'USD_JPY']

# Prebuilt sklearn container for deployment
SKLEARN_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"

def load_bqx_data(pair, bqx_window):
    """
    Load data from BQX table with simplified query
    """
    pair_name = pair.lower().replace('_', '')
    print(f"\n📥 Loading data for {pair} using bqx_{bqx_window} features...")

    # Build query for multiple horizon targets
    horizon_targets = ', '.join([
        f"LEAD(bqx_{bqx_window}, {h}) OVER (ORDER BY interval_time) as target_h{h}"
        for h in PREDICTION_HORIZONS
    ])

    query = f"""
    WITH features AS (
        SELECT
            interval_time,
            -- BQX features
            bqx_45,
            bqx_90,
            bqx_180,
            bqx_360,
            bqx_720,
            bqx_1440,
            bqx_2880,

            -- Lagged BQX values for momentum
            LAG(bqx_{bqx_window}, 1) OVER (ORDER BY interval_time) as bqx_lag_1,
            LAG(bqx_{bqx_window}, 2) OVER (ORDER BY interval_time) as bqx_lag_2,
            LAG(bqx_{bqx_window}, 3) OVER (ORDER BY interval_time) as bqx_lag_3,
            LAG(bqx_{bqx_window}, 5) OVER (ORDER BY interval_time) as bqx_lag_5,
            LAG(bqx_{bqx_window}, 10) OVER (ORDER BY interval_time) as bqx_lag_10,

            -- Multiple horizon targets
            {horizon_targets}

        FROM `{PROJECT_ID}.{DATASET_ID}.{pair_name}_bqx`
        ORDER BY interval_time DESC
        LIMIT 10000
    )
    SELECT * FROM features
    WHERE target_h{PREDICTION_HORIZONS[-1]} IS NOT NULL
    """

    try:
        df = bq_client.query(query).to_dataframe()
        print(f"  ✅ Loaded {len(df)} rows with {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"  ❌ Failed to load data: {str(e)}")
        return None

def train_multi_horizon_models(pair, bqx_window):
    """
    Train models for multiple prediction horizons
    """
    # Load data
    df = load_bqx_data(pair, bqx_window)
    if df is None or df.empty:
        print(f"  ⚠️ Skipping {pair} bqx_{bqx_window} due to data loading failure")
        return []

    print(f"\n🔧 Training models for {pair} with bqx_{bqx_window} features...")

    # Prepare features (exclude targets and time)
    feature_cols = [col for col in df.columns
                   if not col.startswith('target_') and col != 'interval_time']

    # Drop rows with NaN in features
    df = df.dropna(subset=feature_cols)

    X = df[feature_cols].values

    results = []

    # Train model for each horizon
    for horizon in PREDICTION_HORIZONS:
        target_col = f'target_h{horizon}'

        if target_col not in df.columns:
            print(f"  ⚠️ Target {target_col} not found, skipping")
            continue

        y = df[target_col].values

        # Remove NaN targets
        valid_mask = ~np.isnan(y)
        X_valid = X[valid_mask]
        y_valid = y[valid_mask]

        if len(X_valid) < 100:
            print(f"  ⚠️ Insufficient data for horizon {horizon}, skipping")
            continue

        print(f"\n  🔄 Training model for {horizon}-interval horizon...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_valid, y_valid, test_size=0.2, random_state=42
        )

        # Train model (simplified for speed)
        model = RandomForestRegressor(
            n_estimators=50,  # Reduced for speed
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        # Calculate directional accuracy
        if len(y_test) > 1:
            actual_direction = np.diff(y_test) > 0
            pred_direction = np.diff(y_pred) > 0
            dir_accuracy = np.mean(actual_direction == pred_direction)
        else:
            dir_accuracy = 0.5

        print(f"    📊 Model: {pair}_bqx{bqx_window}_h{horizon}")
        print(f"       R²: {r2:.4f}")
        print(f"       RMSE: {rmse:.4f}")
        print(f"       MAE: {mae:.4f}")
        print(f"       Dir Accuracy: {dir_accuracy:.2%}")

        # Save model if performance is acceptable
        if r2 > 0.15:  # Lower threshold for short horizons
            model_name = f"{pair}_bqx{bqx_window}_h{horizon}"
            save_model_to_gcs(model, model_name, feature_cols)

            results.append({
                'pair': pair,
                'bqx_window': bqx_window,
                'horizon': horizon,
                'test_r2': r2,
                'rmse': rmse,
                'mae': mae,
                'directional_accuracy': dir_accuracy,
                'model_name': model_name,
                'saved': True
            })
        else:
            print(f"       ⚠️ R² below threshold (0.15), not saving")
            results.append({
                'pair': pair,
                'bqx_window': bqx_window,
                'horizon': horizon,
                'test_r2': r2,
                'rmse': rmse,
                'mae': mae,
                'directional_accuracy': dir_accuracy,
                'model_name': f"{pair}_bqx{bqx_window}_h{horizon}",
                'saved': False
            })

    return results

def save_model_to_gcs(model, model_name, feature_columns):
    """
    Save model and metadata to GCS
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)

        # Save model
        model_blob = bucket.blob(f"{model_name}/model.pkl")
        model_bytes = pickle.dumps(model, protocol=4)
        model_blob.upload_from_string(model_bytes)

        # Save feature columns
        features_blob = bucket.blob(f"{model_name}/features.pkl")
        features_bytes = pickle.dumps(feature_columns, protocol=4)
        features_blob.upload_from_string(features_bytes)

        print(f"       ✅ Saved to gs://{BUCKET_NAME}/{model_name}/")
        return True
    except Exception as e:
        print(f"       ❌ Failed to save: {str(e)}")
        return False

def main():
    """
    Main implementation function
    """
    print("="*80)
    print("🎯 SIMPLIFIED MULTI-HORIZON BQX PREDICTION MODELS")
    print("="*80)
    print(f"📅 {datetime.now().isoformat()}")
    print(f"🔧 Feature Windows: {FEATURE_WINDOWS}")
    print(f"🎯 Prediction Horizons: {PREDICTION_HORIZONS}")
    print(f"📊 Critical Pairs: {CRITICAL_PAIRS}")
    print("="*80)

    all_results = []

    # Process each pair and window combination
    for pair in CRITICAL_PAIRS:
        for bqx_window in FEATURE_WINDOWS:
            print(f"\n{'='*60}")
            print(f"Processing {pair} with bqx_{bqx_window} features")
            print(f"{'='*60}")

            results = train_multi_horizon_models(pair, bqx_window)
            all_results.extend(results)

    # Create results DataFrame
    results_df = pd.DataFrame(all_results)

    # Save results
    results_df.to_csv('/tmp/multi_horizon_results.csv', index=False)

    # Print summary
    print("\n" + "="*80)
    print("📊 MULTI-HORIZON MODEL SUMMARY")
    print("="*80)

    if not results_df.empty:
        print(f"\n🏆 Models Trained: {len(results_df)}")
        print(f"✅ Models Saved: {results_df['saved'].sum()}")

        # Best models by horizon
        for horizon in PREDICTION_HORIZONS:
            horizon_results = results_df[results_df['horizon'] == horizon]
            if not horizon_results.empty:
                best = horizon_results.nlargest(1, 'test_r2').iloc[0]
                print(f"\nHorizon {horizon}:")
                print(f"  Best: {best['model_name']} (R²={best['test_r2']:.4f})")
                print(f"  Avg R²: {horizon_results['test_r2'].mean():.4f}")
                print(f"  Avg Dir Acc: {horizon_results['directional_accuracy'].mean():.2%}")
    else:
        print("❌ No models were successfully trained")

    print("\n📈 Results saved to: /tmp/multi_horizon_results.csv")
    print("="*80)
    print("✅ IMPLEMENTATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()