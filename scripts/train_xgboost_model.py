#!/usr/bin/env python3
"""
REAL XGBoost Model Training for BQX ML V3
Trains models to achieve quality gates: R² ≥ 0.35, RMSE ≤ 0.15, Directional Accuracy ≥ 55%
"""

import os
import json
import pickle
import time
from datetime import datetime
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from google.cloud import bigquery, storage
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV

# Use application default credentials
# Already configured via gcloud

def train_xgboost_model(
    pair: str = "EURUSD",
    prediction_window: int = 45,
    project_id: str = "bqx-ml"
) -> Tuple[xgb.XGBRegressor, Dict]:
    """
    Trains XGBoost model for specific pair-window combination.
    Targets R² ≥ 0.35 as primary quality gate.

    Returns:
        Tuple of (trained_model, metrics_dict)
    """

    print(f"\n{'='*60}")
    print(f"Training XGBoost Model: {pair} - {prediction_window} intervals")
    print(f"{'='*60}")

    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # Load training data
    table_name = f"{project_id}.bqx_ml_v3_models.{pair.lower()}_{prediction_window}_train"

    print(f"\n📊 Loading data from {table_name}...")

    query = f"""
    SELECT * EXCEPT(interval_time, pair, row_num)
    FROM `{table_name}`
    """

    df = client.query(query).to_dataframe()
    print(f"  Loaded {len(df):,} rows")

    # Split into train/val/test
    train_df = df[df['split'] == 'train'].drop(columns=['split'])
    val_df = df[df['split'] == 'validation'].drop(columns=['split'])
    test_df = df[df['split'] == 'test'].drop(columns=['split'])

    print(f"\n  Data splits:")
    print(f"    - Train: {len(train_df):,} rows")
    print(f"    - Validation: {len(val_df):,} rows")
    print(f"    - Test: {len(test_df):,} rows")

    # Prepare features and target
    target_col = 'target'
    feature_cols = [col for col in train_df.columns if col != target_col]

    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df[target_col]

    X_val = val_df[feature_cols].fillna(0)
    y_val = val_df[target_col]

    X_test = test_df[feature_cols].fillna(0)
    y_test = test_df[target_col]

    print(f"\n🔧 Training XGBoost model...")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Target: {target_col}")

    # Start with CE-recommended hyperparameters
    base_params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'n_jobs': -1,
        'tree_method': 'hist'  # Faster training
    }

    # Train initial model
    start_time = time.time()

    # Add early_stopping_rounds to params for newer XGBoost versions
    base_params['early_stopping_rounds'] = 10
    base_params['eval_metric'] = 'rmse'

    model = xgb.XGBRegressor(**base_params)

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    training_time = time.time() - start_time

    # Evaluate model
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    test_pred = model.predict(X_test)

    metrics = {
        'pair': pair,
        'window': prediction_window,
        'training_time_seconds': round(training_time, 2),
        'timestamp': datetime.now().isoformat(),
        'model_params': base_params,
        'n_features': len(feature_cols),
        'splits': {
            'train': {
                'r2_score': round(r2_score(y_train, train_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_train, train_pred)), 4),
                'mae': round(mean_absolute_error(y_train, train_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_train, train_pred)
            },
            'validation': {
                'r2_score': round(r2_score(y_val, val_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_val, val_pred)), 4),
                'mae': round(mean_absolute_error(y_val, val_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_val, val_pred)
            },
            'test': {
                'r2_score': round(r2_score(y_test, test_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_test, test_pred)), 4),
                'mae': round(mean_absolute_error(y_test, test_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_test, test_pred)
            }
        }
    }

    print(f"\n📊 Initial Model Results:")
    print(f"  Training time: {training_time:.2f} seconds")
    print(f"  Validation R²: {metrics['splits']['validation']['r2_score']}")
    print(f"  Validation RMSE: {metrics['splits']['validation']['rmse']}")
    print(f"  Validation Dir. Accuracy: {metrics['splits']['validation']['directional_accuracy']:.2%}")

    # Check if we meet quality gates
    val_r2 = metrics['splits']['validation']['r2_score']
    val_rmse = metrics['splits']['validation']['rmse']
    val_dir_acc = metrics['splits']['validation']['directional_accuracy']

    quality_gates_met = (
        val_r2 >= 0.35 and
        val_rmse <= 0.15 and
        val_dir_acc >= 0.55
    )

    if not quality_gates_met and val_r2 < 0.35:
        print(f"\n⚡ R² below target ({val_r2} < 0.35). Optimizing hyperparameters...")
        model, metrics = optimize_hyperparameters(
            X_train, y_train, X_val, y_val, X_test, y_test,
            pair, prediction_window, feature_cols
        )

    # Final quality assessment
    final_r2 = metrics['splits']['validation']['r2_score']
    final_rmse = metrics['splits']['validation']['rmse']
    final_dir_acc = metrics['splits']['validation']['directional_accuracy']

    print(f"\n{'='*60}")
    print(f"🎯 FINAL MODEL PERFORMANCE:")
    print(f"{'='*60}")
    print(f"  R² Score:             {final_r2:.4f} {'✅' if final_r2 >= 0.35 else '⚠️'} (target ≥ 0.35)")
    print(f"  RMSE:                 {final_rmse:.4f} {'✅' if final_rmse <= 0.15 else '⚠️'} (target ≤ 0.15)")
    print(f"  Directional Accuracy: {final_dir_acc:.2%} {'✅' if final_dir_acc >= 0.55 else '⚠️'} (target ≥ 55%)")

    # Add quality gate status to metrics
    metrics['quality_gates'] = {
        'r2_achieved': final_r2 >= 0.35,
        'rmse_achieved': final_rmse <= 0.15,
        'directional_accuracy_achieved': final_dir_acc >= 0.55,
        'all_gates_passed': all([
            final_r2 >= 0.35,
            final_rmse <= 0.15,
            final_dir_acc >= 0.55
        ])
    }

    return model, metrics


def calculate_directional_accuracy(y_true, y_pred):
    """
    Calculate directional accuracy (% of correct direction predictions)
    """
    # For BQX predictions, direction is whether value increases or decreases
    # Since we're predicting future BQX values
    direction_correct = np.sign(y_true) == np.sign(y_pred)
    return np.mean(direction_correct)


def optimize_hyperparameters(X_train, y_train, X_val, y_val, X_test, y_test,
                            pair, prediction_window, feature_cols):
    """
    Optimize hyperparameters using RandomizedSearchCV to achieve R² ≥ 0.35
    """

    param_distributions = {
        'max_depth': [3, 4, 5, 6, 7, 8, 10],
        'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2],
        'n_estimators': [50, 100, 150, 200, 300],
        'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0],
        'min_child_weight': [1, 3, 5, 7],
        'gamma': [0, 0.1, 0.2, 0.3],
        'reg_alpha': [0, 0.01, 0.1, 1],
        'reg_lambda': [0, 0.01, 0.1, 1]
    }

    print("\n🔍 Running hyperparameter optimization (up to 100 trials)...")

    base_model = xgb.XGBRegressor(
        objective='reg:squarederror',
        random_state=42,
        n_jobs=-1,
        tree_method='hist'
    )

    random_search = RandomizedSearchCV(
        base_model,
        param_distributions,
        n_iter=100,  # CE specified 100 trials
        scoring='r2',
        cv=3,
        verbose=1,
        n_jobs=-1,
        random_state=42
    )

    start_time = time.time()
    random_search.fit(X_train, y_train)
    optimization_time = time.time() - start_time

    best_model = random_search.best_estimator_

    print(f"\n✅ Optimization complete in {optimization_time:.2f} seconds")
    print(f"  Best parameters: {random_search.best_params_}")
    print(f"  Best CV R²: {random_search.best_score_:.4f}")

    # Re-evaluate with best model
    train_pred = best_model.predict(X_train)
    val_pred = best_model.predict(X_val)
    test_pred = best_model.predict(X_test)

    metrics = {
        'pair': pair,
        'window': prediction_window,
        'training_time_seconds': round(optimization_time, 2),
        'timestamp': datetime.now().isoformat(),
        'model_params': random_search.best_params_,
        'n_features': len(feature_cols),
        'optimization_trials': 100,
        'splits': {
            'train': {
                'r2_score': round(r2_score(y_train, train_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_train, train_pred)), 4),
                'mae': round(mean_absolute_error(y_train, train_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_train, train_pred)
            },
            'validation': {
                'r2_score': round(r2_score(y_val, val_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_val, val_pred)), 4),
                'mae': round(mean_absolute_error(y_val, val_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_val, val_pred)
            },
            'test': {
                'r2_score': round(r2_score(y_test, test_pred), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_test, test_pred)), 4),
                'mae': round(mean_absolute_error(y_test, test_pred), 4),
                'directional_accuracy': calculate_directional_accuracy(y_test, test_pred)
            }
        }
    }

    return best_model, metrics


def save_model_to_gcs(model, metrics, pair="EURUSD", window=45, version="v1"):
    """
    Save model and metadata to GCS in hierarchical structure
    """

    print(f"\n💾 Saving model to GCS...")

    storage_client = storage.Client()
    bucket_name = "bqx-ml-v3-models"

    # Get existing bucket
    bucket = storage_client.get_bucket(bucket_name)
    print(f"  Using bucket: gs://{bucket_name}/")

    # Save model
    model_path = f"{pair.lower()}/{window}/{version}/model.pkl"
    model_blob = bucket.blob(model_path)

    model_bytes = pickle.dumps(model)
    model_blob.upload_from_string(model_bytes)
    print(f"  ✅ Model saved: gs://{bucket_name}/{model_path}")

    # Save metrics
    metrics_path = f"{pair.lower()}/{window}/{version}/metrics.json"
    metrics_blob = bucket.blob(metrics_path)
    metrics_blob.upload_from_string(json.dumps(metrics, indent=2))
    print(f"  ✅ Metrics saved: gs://{bucket_name}/{metrics_path}")

    # Save metadata
    metadata = {
        'model_type': 'XGBoost',
        'pair': pair,
        'prediction_window': window,
        'version': version,
        'created': metrics['timestamp'],
        'training_time_seconds': metrics['training_time_seconds'],
        'quality_gates_passed': metrics.get('quality_gates', {}).get('all_gates_passed', False)
    }

    metadata_path = f"{pair.lower()}/{window}/{version}/metadata.json"
    metadata_blob = bucket.blob(metadata_path)
    metadata_blob.upload_from_string(json.dumps(metadata, indent=2))
    print(f"  ✅ Metadata saved: gs://{bucket_name}/{metadata_path}")

    # Save config (hyperparameters)
    config_path = f"{pair.lower()}/{window}/{version}/config.json"
    config_blob = bucket.blob(config_path)
    config_blob.upload_from_string(json.dumps(metrics['model_params'], indent=2))
    print(f"  ✅ Config saved: gs://{bucket_name}/{config_path}")

    print(f"\n✅ Model package saved to gs://{bucket_name}/{pair.lower()}/{window}/{version}/")

    return f"gs://{bucket_name}/{model_path}"


if __name__ == "__main__":
    print("\n" + "="*60)
    print("BQX ML V3 - XGBoost Model Training")
    print("Target: R² ≥ 0.35, RMSE ≤ 0.15, Dir. Accuracy ≥ 55%")
    print("="*60)

    # Train model for EURUSD-45
    model, metrics = train_xgboost_model(
        pair="EURUSD",
        prediction_window=45
    )

    # Save to GCS
    gcs_path = save_model_to_gcs(model, metrics)

    # Save metrics locally for reporting
    with open('/home/micha/bqx_ml_v3/.claude/sandbox/eurusd_45_model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ MODEL TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Model location: {gcs_path}")
    print(f"Validation R²: {metrics['splits']['validation']['r2_score']}")
    print(f"Quality gates passed: {metrics.get('quality_gates', {}).get('all_gates_passed', False)}")