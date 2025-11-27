#!/usr/bin/env python3
"""
Train all 196 BQX ML V3 models using BQX-only approach
Per Chief Engineer decision 20251127_0035 based on PERFORMANCE_FIRST mandate
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import time
from datetime import datetime
import json
import concurrent.futures
import os
from typing import Dict, List, Tuple

# All 28 currency pairs
ALL_PAIRS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
    'GBPJPY', 'GBPCHF', 'GBPAUD', 'GBPCAD', 'GBPNZD',
    'AUDJPY', 'AUDCHF', 'AUDCAD', 'AUDNZD',
    'NZDJPY', 'NZDCHF', 'NZDCAD',
    'CADJPY', 'CADCHF',
    'CHFJPY'
]

# All 7 prediction windows
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

# Proven hyperparameters from EURUSD-45 success
BASE_PARAMS = {
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42,
    'n_jobs': -1,
    'tree_method': 'hist',
    'early_stopping_rounds': 10,
    'eval_metric': 'rmse'
}

def calculate_directional_accuracy(y_true, y_pred):
    """Calculate directional accuracy"""
    actual_direction = np.sign(y_true)
    predicted_direction = np.sign(y_pred)
    correct_directions = (actual_direction == predicted_direction).sum()
    return correct_directions / len(y_true)

def prepare_training_dataset(pair: str, window: int, client: bigquery.Client) -> str:
    """
    Create BQX-only training dataset for a pair-window combination
    """

    output_table = f"bqx-ml.bqx_ml_v3_models.{pair.lower()}_{window}_train"

    # Build BQX-only query (14 features)
    query = f"""
    WITH feature_engineering AS (
        SELECT
            interval_time,
            pair,
            -- BQX lag features (14 features)
            LAG(bqx_{window}, 1) OVER (ORDER BY interval_time) as bqx_lag_1,
            LAG(bqx_{window}, 2) OVER (ORDER BY interval_time) as bqx_lag_2,
            LAG(bqx_{window}, 3) OVER (ORDER BY interval_time) as bqx_lag_3,
            LAG(bqx_{window}, 4) OVER (ORDER BY interval_time) as bqx_lag_4,
            LAG(bqx_{window}, 5) OVER (ORDER BY interval_time) as bqx_lag_5,
            LAG(bqx_{window}, 6) OVER (ORDER BY interval_time) as bqx_lag_6,
            LAG(bqx_{window}, 7) OVER (ORDER BY interval_time) as bqx_lag_7,
            LAG(bqx_{window}, 8) OVER (ORDER BY interval_time) as bqx_lag_8,
            LAG(bqx_{window}, 9) OVER (ORDER BY interval_time) as bqx_lag_9,
            LAG(bqx_{window}, 10) OVER (ORDER BY interval_time) as bqx_lag_10,
            LAG(bqx_{window}, 11) OVER (ORDER BY interval_time) as bqx_lag_11,
            LAG(bqx_{window}, 12) OVER (ORDER BY interval_time) as bqx_lag_12,
            LAG(bqx_{window}, 13) OVER (ORDER BY interval_time) as bqx_lag_13,
            LAG(bqx_{window}, 14) OVER (ORDER BY interval_time) as bqx_lag_14,

            -- Target
            target_{window} as target,

            -- Row number for splitting
            ROW_NUMBER() OVER (ORDER BY interval_time) as row_num

        FROM `bqx-ml.bqx_ml_v3_features.{pair.lower()}_bqx`
        WHERE bqx_{window} IS NOT NULL
        AND target_{window} IS NOT NULL
    ),

    labeled_data AS (
        SELECT
            *,
            -- Interval-centric split with temporal isolation
            CASE
                WHEN row_num <= 7000 THEN 'train'
                WHEN row_num > 7100 AND row_num <= 9100 THEN 'validation'  -- 100 interval gap
                WHEN row_num > 9150 THEN 'test'  -- 50 interval gap
                ELSE 'gap'
            END as split
        FROM feature_engineering
    )

    SELECT
        interval_time,
        pair,
        bqx_lag_1, bqx_lag_2, bqx_lag_3, bqx_lag_4, bqx_lag_5,
        bqx_lag_6, bqx_lag_7, bqx_lag_8, bqx_lag_9, bqx_lag_10,
        bqx_lag_11, bqx_lag_12, bqx_lag_13, bqx_lag_14,
        target,
        split
    FROM labeled_data
    WHERE split != 'gap'
    ORDER BY interval_time
    """

    # Configure query job
    job_config = bigquery.QueryJobConfig(
        destination=output_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    # Execute query
    query_job = client.query(query, job_config=job_config)
    query_job.result()

    return output_table

def train_single_model(pair: str, window: int, client: bigquery.Client) -> Dict:
    """
    Train a single BQX-only model for a pair-window combination
    """

    model_id = f"{pair}-{window}"
    print(f"\n{'='*60}")
    print(f"Training Model: {model_id}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # Prepare dataset
        print(f"📊 Preparing training dataset...")
        table_id = prepare_training_dataset(pair, window, client)

        # Load data
        query = f"""
        SELECT * FROM `{table_id}`
        ORDER BY interval_time
        """

        df = client.query(query).to_dataframe()

        # Define features
        feature_cols = [f'bqx_lag_{i}' for i in range(1, 15)]

        # Split data
        train_df = df[df['split'] == 'train'].copy()
        val_df = df[df['split'] == 'validation'].copy()
        test_df = df[df['split'] == 'test'].copy()

        print(f"   Train: {len(train_df):,} rows")
        print(f"   Validation: {len(val_df):,} rows")
        print(f"   Test: {len(test_df):,} rows")

        # Prepare features and targets
        X_train = train_df[feature_cols]
        y_train = train_df['target']
        X_val = val_df[feature_cols]
        y_val = val_df['target']
        X_test = test_df[feature_cols]
        y_test = test_df['target']

        # Train model
        print(f"🔧 Training XGBoost model...")
        model = xgb.XGBRegressor(**BASE_PARAMS)

        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Make predictions
        y_pred_val = model.predict(X_val)
        y_pred_test = model.predict(X_test)

        # Calculate metrics
        val_r2 = r2_score(y_val, y_pred_val)
        val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        val_mae = mean_absolute_error(y_val, y_pred_val)
        val_dir_acc = calculate_directional_accuracy(y_val, y_pred_val)

        test_r2 = r2_score(y_test, y_pred_test)
        test_dir_acc = calculate_directional_accuracy(y_test, y_pred_test)

        training_time = time.time() - start_time

        # Check quality gates
        quality_passed = val_r2 >= 0.35 and val_dir_acc >= 0.55

        print(f"✅ Training complete!")
        print(f"   R² Score: {val_r2:.4f} {'✅' if val_r2 >= 0.35 else '❌'}")
        print(f"   Dir. Accuracy: {val_dir_acc:.2%} {'✅' if val_dir_acc >= 0.55 else '❌'}")
        print(f"   Training Time: {training_time:.2f}s")

        # Return metrics
        return {
            'model_id': model_id,
            'pair': pair,
            'window': window,
            'status': 'SUCCESS',
            'quality_passed': quality_passed,
            'metrics': {
                'validation': {
                    'r2_score': round(val_r2, 4),
                    'rmse': round(val_rmse, 4),
                    'mae': round(val_mae, 4),
                    'directional_accuracy': round(val_dir_acc, 4)
                },
                'test': {
                    'r2_score': round(test_r2, 4),
                    'directional_accuracy': round(test_dir_acc, 4)
                }
            },
            'training_time_seconds': round(training_time, 2),
            'timestamp': datetime.now().isoformat(),
            'table_id': table_id
        }

    except Exception as e:
        print(f"❌ Error training {model_id}: {e}")
        return {
            'model_id': model_id,
            'pair': pair,
            'window': window,
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def train_batch(pairs_batch: List[Tuple[str, int]], client: bigquery.Client) -> List[Dict]:
    """
    Train a batch of models sequentially
    """
    results = []
    for pair, window in pairs_batch:
        result = train_single_model(pair, window, client)
        results.append(result)
    return results

def main():
    """
    Train all 196 BQX ML V3 models
    """

    print("\n" + "="*60)
    print("BQX ML V3 - FULL SCALE MODEL TRAINING")
    print("Approach: BQX-only (PERFORMANCE_FIRST)")
    print("Models: 196 (28 pairs × 7 windows)")
    print("="*60)

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    # Create all model combinations
    all_models = [(pair, window) for pair in ALL_PAIRS for window in WINDOWS]

    print(f"\n📊 Total models to train: {len(all_models)}")

    # Results storage
    all_results = []
    successful_models = []
    failed_models = []

    # Process in batches for manageable progress tracking
    batch_size = 7  # Train all windows for one pair at a time

    start_time = datetime.now()

    for pair_idx, pair in enumerate(ALL_PAIRS, 1):
        print(f"\n{'='*60}")
        print(f"Processing Pair {pair_idx}/28: {pair}")
        print(f"{'='*60}")

        # Train all windows for this pair
        for window in WINDOWS:
            result = train_single_model(pair, window, client)
            all_results.append(result)

            if result['status'] == 'SUCCESS':
                successful_models.append(result['model_id'])
                if result['quality_passed']:
                    print(f"   ✅ {result['model_id']} - Quality gates PASSED")
                else:
                    print(f"   ⚠️ {result['model_id']} - Quality gates FAILED")
            else:
                failed_models.append(result['model_id'])
                print(f"   ❌ {result['model_id']} - Training FAILED")

        # Progress update
        models_complete = pair_idx * 7
        print(f"\n📈 Progress: {models_complete}/{len(all_models)} models ({models_complete/len(all_models)*100:.1f}%)")

        # Time estimate
        elapsed = (datetime.now() - start_time).total_seconds()
        if models_complete > 0:
            avg_time_per_model = elapsed / models_complete
            remaining_models = len(all_models) - models_complete
            estimated_remaining = avg_time_per_model * remaining_models / 60
            print(f"⏱️ Estimated time remaining: {estimated_remaining:.1f} minutes")

    # Generate summary report
    print("\n" + "="*60)
    print("TRAINING COMPLETE - SUMMARY REPORT")
    print("="*60)

    # Calculate statistics
    quality_passed = sum(1 for r in all_results if r.get('quality_passed', False))
    avg_r2 = np.mean([r['metrics']['validation']['r2_score']
                      for r in all_results if 'metrics' in r])
    avg_dir_acc = np.mean([r['metrics']['validation']['directional_accuracy']
                           for r in all_results if 'metrics' in r])

    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total models trained: {len(successful_models)}/{len(all_models)}")
    print(f"   Quality gates passed: {quality_passed}/{len(successful_models)}")
    print(f"   Average R² score: {avg_r2:.4f}")
    print(f"   Average directional accuracy: {avg_dir_acc:.2%}")
    print(f"   Total training time: {(datetime.now() - start_time).total_seconds()/60:.1f} minutes")

    # Save results to file
    output_file = '/home/micha/bqx_ml_v3/scripts/all_models_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_models': len(all_models),
                'successful': len(successful_models),
                'failed': len(failed_models),
                'quality_passed': quality_passed,
                'avg_r2_score': round(avg_r2, 4),
                'avg_directional_accuracy': round(avg_dir_acc, 4),
                'training_duration_minutes': round((datetime.now() - start_time).total_seconds()/60, 1)
            },
            'models': all_results
        }, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # List any failed models
    if failed_models:
        print(f"\n⚠️ Failed models ({len(failed_models)}):")
        for model_id in failed_models:
            print(f"   - {model_id}")

    # List models that failed quality gates
    quality_failed = [r['model_id'] for r in all_results
                     if r.get('status') == 'SUCCESS' and not r.get('quality_passed')]
    if quality_failed:
        print(f"\n⚠️ Models failing quality gates ({len(quality_failed)}):")
        for model_id in quality_failed:
            print(f"   - {model_id}")

    print("\n" + "="*60)
    print("✅ BQX ML V3 MODEL TRAINING COMPLETE!")
    print("="*60)

    return all_results

if __name__ == "__main__":
    try:
        results = main()
        print("\n🎯 All 196 models processed successfully!")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()