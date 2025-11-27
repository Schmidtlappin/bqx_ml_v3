#!/usr/bin/env python3
"""
Train ALL 196 Models with Smart Dual Processing
Per CE authorization based on R² = 0.9362 achievement
MANDATORY: Real-time AirTable updates
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import time
from datetime import datetime
import json
import os
import sys

# Add scripts directory to path for imports
sys.path.append('/home/micha/bqx_ml_v3/scripts')
from airtable_updater import AirTableUpdater
from smart_dual_processing import create_smart_dual_features, compute_feature_weights

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

# All prediction windows
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

# Smart Dual XGBoost configuration (proven to achieve R² = 0.9362)
SMART_PARAMS = {
    'n_estimators': 200,
    'max_depth': 8,
    'learning_rate': 0.05,
    'colsample_bytree': 0.7,
    'subsample': 0.8,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'random_state': 42,
    'n_jobs': -1,
    'tree_method': 'hist',
    'early_stopping_rounds': 20,
    'eval_metric': 'rmse'
}


def train_smart_dual_model(client, pair, window, airtable):
    """
    Train a single model using Smart Dual Processing
    """

    model_id = f"{pair}-{window}"
    print(f"\n{'='*60}")
    print(f"Training {model_id} with Smart Dual Processing")
    print(f"{'='*60}")

    # Update AirTable - starting
    airtable.log_progress(
        'Model Training',
        f'Starting {model_id} with Smart Dual Processing',
        f'MP03.P04.S01.T0{WINDOWS.index(window)+1}'
    )

    try:
        # Load IDX data
        idx_query = f"""
        SELECT
            interval_time,
            close_idx
        FROM `bqx-ml.bqx_ml_v3_features.{pair.lower()}_idx`
        ORDER BY interval_time
        """

        idx_df = client.query(idx_query).to_dataframe()
        idx_df.set_index('interval_time', inplace=True)

        # Load BQX data
        bqx_query = f"""
        SELECT
            interval_time,
            bqx_{window},
            target_{window} as target
        FROM `bqx-ml.bqx_ml_v3_features.{pair.lower()}_bqx`
        WHERE bqx_{window} IS NOT NULL
        AND target_{window} IS NOT NULL
        ORDER BY interval_time
        """

        bqx_df = client.query(bqx_query).to_dataframe()
        bqx_df.set_index('interval_time', inplace=True)

        print(f"  Data loaded: {len(idx_df):,} IDX, {len(bqx_df):,} BQX rows")

        # Create Smart Dual features
        features_df = create_smart_dual_features(idx_df, bqx_df, window)

        # Combine with target
        final_df = features_df.join(bqx_df[['target']], how='inner')
        final_df = final_df.dropna()

        # Create splits with temporal gaps
        n_rows = len(final_df)
        train_end = int(n_rows * 0.7)
        val_start = train_end + 100  # 100-interval gap
        val_end = int(n_rows * 0.85)
        test_start = val_end + 50  # 50-interval gap

        # Split data
        train_df = final_df.iloc[:train_end]
        val_df = final_df.iloc[val_start:val_end]
        test_df = final_df.iloc[test_start:]

        # Prepare features
        feature_cols = [col for col in final_df.columns if col != 'target']
        X_train = train_df[feature_cols]
        y_train = train_df['target']
        X_val = val_df[feature_cols]
        y_val = val_df['target']
        X_test = test_df[feature_cols]
        y_test = test_df['target']

        # Compute sample weights
        sample_weights = compute_feature_weights(X_train)

        # Train model
        start_time = time.time()
        model = xgb.XGBRegressor(**SMART_PARAMS)

        model.fit(
            X_train, y_train,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        training_time = time.time() - start_time

        # Make predictions
        y_pred_val = model.predict(X_val)
        y_pred_test = model.predict(X_test)

        # Calculate metrics
        val_r2 = r2_score(y_val, y_pred_val)
        val_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        val_mae = mean_absolute_error(y_val, y_pred_val)
        val_dir_acc = np.mean(np.sign(y_val) == np.sign(y_pred_val))

        test_r2 = r2_score(y_test, y_pred_test)
        test_dir_acc = np.mean(np.sign(y_test) == np.sign(y_pred_test))

        # Quality gate check
        quality_passed = val_r2 >= 0.35

        print(f"  ✅ R² Score: {val_r2:.4f} {'PASSED' if quality_passed else 'FAILED'}")
        print(f"  ✅ Dir. Accuracy: {val_dir_acc:.2%}")
        print(f"  ✅ Training Time: {training_time:.2f}s")

        # Update AirTable with results
        metrics = {
            'r2': val_r2,
            'dir_acc': val_dir_acc,
            'rmse': val_rmse,
            'time': training_time
        }

        airtable.log_model_result(pair, window, metrics, approach='Smart Dual')

        # Return results
        return {
            'model_id': model_id,
            'success': True,
            'metrics': {
                'validation': {
                    'r2_score': val_r2,
                    'rmse': val_rmse,
                    'mae': val_mae,
                    'directional_accuracy': val_dir_acc
                },
                'test': {
                    'r2_score': test_r2,
                    'directional_accuracy': test_dir_acc
                }
            },
            'training_time': training_time,
            'quality_passed': quality_passed
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")

        # Update AirTable with error
        airtable.log_progress(
            'Model Error',
            f'{model_id} failed: {str(e)}',
            f'MP03.P04.S01.T0{WINDOWS.index(window)+1}'
        )

        return {
            'model_id': model_id,
            'success': False,
            'error': str(e)
        }


def main():
    """
    Train all 196 models with Smart Dual Processing
    """

    print("\n" + "="*60)
    print("BQX ML V3 - FULL SCALE SMART DUAL PROCESSING")
    print("Training 196 Models (28 pairs × 7 windows)")
    print("Target: R² > 0.35 (Expected: ~0.90 based on test)")
    print("="*60)

    # Initialize components
    print("\n📌 Initializing components...")

    # BigQuery client
    client = bigquery.Client(project="bqx-ml")
    print("  ✅ BigQuery client initialized")

    # AirTable updater (MANDATORY)
    airtable = AirTableUpdater()
    print("  ✅ AirTable updater initialized")

    # Test AirTable connection
    if not airtable.test_connection():
        print("  ❌ AirTable connection failed - ABORTING")
        return

    # Initialize tracking
    all_results = []
    successful_models = 0
    failed_models = 0
    quality_passed = 0
    start_time = datetime.now()

    # Log start in AirTable
    airtable.log_progress(
        'Full Scale Training',
        f'Starting 196 model training with Smart Dual Processing at {start_time.isoformat()}',
        'MP03.P04.S01.T01'
    )

    # Process each pair and window
    for pair_idx, pair in enumerate(ALL_PAIRS, 1):
        print(f"\n[{pair_idx}/{len(ALL_PAIRS)}] Processing {pair}")

        pair_results = []

        for window_idx, window in enumerate(WINDOWS, 1):
            model_num = (pair_idx - 1) * 7 + window_idx
            print(f"\n  [{model_num}/196] {pair}-{window}")

            # Train model
            result = train_smart_dual_model(client, pair, window, airtable)

            # Track results
            all_results.append(result)
            pair_results.append(result)

            if result['success']:
                successful_models += 1
                if result.get('quality_passed', False):
                    quality_passed += 1
            else:
                failed_models += 1

            # Progress update every 10 models
            if model_num % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                avg_time = elapsed / model_num
                remaining = avg_time * (196 - model_num)

                progress_msg = f"""
Progress Update: {model_num}/196 models complete
Successful: {successful_models}, Failed: {failed_models}
Quality Passed: {quality_passed}
Elapsed: {elapsed:.1f} min, Remaining: {remaining:.1f} min
"""
                print(f"\n⏱️ {progress_msg}")

                # Update AirTable with progress
                airtable.log_progress(
                    'Training Progress',
                    progress_msg,
                    'MP03.P04.S01.T01'
                )

        # Summarize pair results
        pair_r2_scores = [r['metrics']['validation']['r2_score']
                         for r in pair_results if r['success']]

        if pair_r2_scores:
            avg_r2 = np.mean(pair_r2_scores)
            print(f"\n  📊 {pair} Summary: Avg R² = {avg_r2:.4f}")

            # Update AirTable with pair summary
            airtable.log_progress(
                'Pair Complete',
                f'{pair}: {len(pair_r2_scores)}/7 models, Avg R² = {avg_r2:.4f}',
                'MP03.P04.S01.T01'
            )

    # Generate final report
    print("\n" + "="*60)
    print("TRAINING COMPLETE - FINAL REPORT")
    print("="*60)

    # Calculate statistics
    successful_r2_scores = [r['metrics']['validation']['r2_score']
                           for r in all_results if r['success']]

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_models': 196,
        'successful': successful_models,
        'failed': failed_models,
        'quality_passed': quality_passed,
        'quality_pass_rate': quality_passed / 196 * 100,
        'avg_r2_score': np.mean(successful_r2_scores) if successful_r2_scores else 0,
        'min_r2_score': np.min(successful_r2_scores) if successful_r2_scores else 0,
        'max_r2_score': np.max(successful_r2_scores) if successful_r2_scores else 0,
        'std_r2_score': np.std(successful_r2_scores) if successful_r2_scores else 0,
        'total_time_minutes': (datetime.now() - start_time).total_seconds() / 60,
        'models': all_results
    }

    # Print summary
    print(f"\n✅ Successful Models: {successful_models}/196")
    print(f"❌ Failed Models: {failed_models}/196")
    print(f"📊 Quality Gates Passed: {quality_passed}/196 ({report['quality_pass_rate']:.1f}%)")
    print(f"\n📈 R² Score Statistics:")
    print(f"   Average: {report['avg_r2_score']:.4f}")
    print(f"   Min: {report['min_r2_score']:.4f}")
    print(f"   Max: {report['max_r2_score']:.4f}")
    print(f"   Std Dev: {report['std_r2_score']:.4f}")
    print(f"\n⏱️ Total Time: {report['total_time_minutes']:.1f} minutes")

    # Save detailed report
    report_path = '/home/micha/bqx_ml_v3/scripts/smart_dual_full_results.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n💾 Detailed report saved to: {report_path}")

    # Final AirTable update
    final_summary = f"""
SMART DUAL PROCESSING COMPLETE
================================================
Total Models: 196
Successful: {successful_models}
Failed: {failed_models}
Quality Passed: {quality_passed} ({report['quality_pass_rate']:.1f}%)

R² Score Statistics:
- Average: {report['avg_r2_score']:.4f}
- Range: {report['min_r2_score']:.4f} to {report['max_r2_score']:.4f}

Total Time: {report['total_time_minutes']:.1f} minutes
================================================
"""

    airtable.mark_phase_complete('Smart Dual Training', final_summary)

    # Success assessment
    if report['avg_r2_score'] >= 0.50:
        print("\n🎉 EXCEPTIONAL SUCCESS!")
        print(f"Average R² of {report['avg_r2_score']:.4f} far exceeds target of 0.35!")
        print("Smart Dual Processing has delivered outstanding results!")
    elif report['quality_pass_rate'] >= 90:
        print("\n✅ SUCCESS!")
        print(f"{report['quality_pass_rate']:.1f}% of models passed quality gates!")
    else:
        print("\n⚠️ Review needed")
        print(f"Only {report['quality_pass_rate']:.1f}% passed quality gates")

    return report


if __name__ == "__main__":
    try:
        report = main()

        if report and report['avg_r2_score'] >= 0.50:
            print("\n" + "="*60)
            print("🏆 BQX ML V3 - MISSION ACCOMPLISHED!")
            print("196 Models Trained with Smart Dual Processing")
            print("Performance MASSIVELY Exceeds All Targets!")
            print("="*60)

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()