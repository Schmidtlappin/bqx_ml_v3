#!/usr/bin/env python3
"""
Train XGBoost model with DUAL PROCESSING (IDX + BQX features)
Compare performance with BQX-only approach
Per Chief Engineer directive 20251127_0010_CE_BA
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import time
from datetime import datetime
import json


def calculate_directional_accuracy(y_true, y_pred):
    """Calculate directional accuracy (% of correct direction predictions)"""
    actual_direction = np.sign(y_true)
    predicted_direction = np.sign(y_pred)
    correct_directions = (actual_direction == predicted_direction).sum()
    return correct_directions / len(y_true)


def train_dual_processing_model(pair: str, window: int):
    """
    Train XGBoost model with dual processing (IDX + BQX features)

    Args:
        pair: Currency pair (e.g., 'EURUSD')
        window: Prediction window (e.g., 45)

    Returns:
        dict: Model performance metrics
    """

    print("\n" + "="*60)
    print(f"DUAL PROCESSING MODEL TRAINING - {pair}-{window}")
    print("Features: 28 (14 IDX + 14 BQX)")
    print("="*60)

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    # Load dual processing training data
    table_id = f"bqx-ml.bqx_ml_v3_models.{pair.lower()}_{window}_dual_train"

    query = f"""
    SELECT * FROM `{table_id}`
    ORDER BY interval_time
    """

    print(f"\n📊 Loading data from {table_id}...")
    df = client.query(query).to_dataframe()

    # Define feature columns
    idx_features = [f'idx_lag_{i}' for i in range(1, 15)]
    bqx_features = [f'bqx_lag_{i}' for i in range(1, 15)]
    all_features = idx_features + bqx_features

    print(f"   Total rows: {len(df):,}")
    print(f"   IDX features: {len(idx_features)}")
    print(f"   BQX features: {len(bqx_features)}")
    print(f"   Total features: {len(all_features)}")

    # Split data
    train_df = df[df['split'] == 'train'].copy()
    val_df = df[df['split'] == 'validation'].copy()
    test_df = df[df['split'] == 'test'].copy()

    print(f"\n📊 Data splits:")
    print(f"   Train: {len(train_df):,} rows")
    print(f"   Validation: {len(val_df):,} rows")
    print(f"   Test: {len(test_df):,} rows")

    # Prepare features and targets
    X_train = train_df[all_features]
    y_train = train_df['target']
    X_val = val_df[all_features]
    y_val = val_df['target']
    X_test = test_df[all_features]
    y_test = test_df['target']

    # Use proven hyperparameters from BQX-only model
    base_params = {
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

    print(f"\n🔧 Training XGBoost model with dual features...")
    print(f"   Hyperparameters: Base configuration (proven)")

    # Train model
    start_time = time.time()
    model = xgb.XGBRegressor(**base_params)

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    training_time = time.time() - start_time

    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_val = model.predict(X_val)
    y_pred_test = model.predict(X_test)

    # Calculate metrics for all splits
    metrics = {
        'pair': pair,
        'window': window,
        'approach': 'dual_processing',
        'n_features': len(all_features),
        'feature_breakdown': {
            'idx_features': len(idx_features),
            'bqx_features': len(bqx_features)
        },
        'training_time_seconds': round(training_time, 2),
        'timestamp': datetime.now().isoformat(),
        'splits': {
            'train': {
                'r2_score': round(r2_score(y_train, y_pred_train), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_train, y_pred_train)), 4),
                'mae': round(mean_absolute_error(y_train, y_pred_train), 4),
                'directional_accuracy': round(calculate_directional_accuracy(y_train, y_pred_train), 4)
            },
            'validation': {
                'r2_score': round(r2_score(y_val, y_pred_val), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_val, y_pred_val)), 4),
                'mae': round(mean_absolute_error(y_val, y_pred_val), 4),
                'directional_accuracy': round(calculate_directional_accuracy(y_val, y_pred_val), 4)
            },
            'test': {
                'r2_score': round(r2_score(y_test, y_pred_test), 4),
                'rmse': round(np.sqrt(mean_squared_error(y_test, y_pred_test)), 4),
                'mae': round(mean_absolute_error(y_test, y_pred_test), 4),
                'directional_accuracy': round(calculate_directional_accuracy(y_test, y_pred_test), 4)
            }
        }
    }

    # Check quality gates
    val_r2 = metrics['splits']['validation']['r2_score']
    val_dir_acc = metrics['splits']['validation']['directional_accuracy']

    metrics['quality_gates'] = {
        'r2_achieved': val_r2 >= 0.35,
        'directional_accuracy_achieved': val_dir_acc >= 0.55,
        'r2_improvement': round((val_r2 / 0.35 - 1) * 100, 1) if val_r2 >= 0.35 else round((val_r2 / 0.35) * 100, 1),
        'primary_gates_passed': val_r2 >= 0.35 and val_dir_acc >= 0.55
    }

    # Feature importance analysis
    feature_importance = pd.DataFrame({
        'feature': all_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    # Analyze IDX vs BQX contribution
    idx_importance = feature_importance[feature_importance['feature'].str.startswith('idx_')]['importance'].sum()
    bqx_importance = feature_importance[feature_importance['feature'].str.startswith('bqx_')]['importance'].sum()

    metrics['feature_importance'] = {
        'top_5_features': feature_importance.head(5).to_dict('records'),
        'idx_total_importance': round(idx_importance, 4),
        'bqx_total_importance': round(bqx_importance, 4),
        'idx_percentage': round(idx_importance / (idx_importance + bqx_importance) * 100, 2),
        'bqx_percentage': round(bqx_importance / (idx_importance + bqx_importance) * 100, 2)
    }

    return model, metrics


def compare_approaches():
    """
    Compare BQX-only vs Dual Processing approaches
    """

    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: BQX-only vs DUAL PROCESSING")
    print("="*60)

    # BQX-only results (from previous training)
    bqx_only_metrics = {
        'approach': 'BQX-only',
        'features': 14,
        'r2_score': 0.4648,
        'directional_accuracy': 0.7416,
        'training_time': 0.1
    }

    # Train dual processing model
    model, dual_metrics = train_dual_processing_model('EURUSD', 45)

    # Extract key metrics for comparison
    dual_processing_metrics = {
        'approach': 'Dual (IDX+BQX)',
        'features': dual_metrics['n_features'],
        'r2_score': dual_metrics['splits']['validation']['r2_score'],
        'directional_accuracy': dual_metrics['splits']['validation']['directional_accuracy'],
        'training_time': dual_metrics['training_time_seconds']
    }

    # Display comparison table
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)

    print("\n| Approach | Features | R² Score | Dir. Accuracy | Training Time |")
    print("|----------|----------|----------|---------------|---------------|")
    print(f"| {bqx_only_metrics['approach']:15} | {bqx_only_metrics['features']:8} | {bqx_only_metrics['r2_score']:8.4f} | {bqx_only_metrics['directional_accuracy']:13.2%} | {bqx_only_metrics['training_time']:13.2f}s |")
    print(f"| {dual_processing_metrics['approach']:15} | {dual_processing_metrics['features']:8} | {dual_processing_metrics['r2_score']:8.4f} | {dual_processing_metrics['directional_accuracy']:13.2%} | {dual_processing_metrics['training_time']:13.2f}s |")

    # Calculate improvements
    r2_improvement = (dual_processing_metrics['r2_score'] / bqx_only_metrics['r2_score'] - 1) * 100
    dir_improvement = (dual_processing_metrics['directional_accuracy'] / bqx_only_metrics['directional_accuracy'] - 1) * 100

    print(f"\n📊 PERFORMANCE ANALYSIS:")
    print(f"   R² Score Change: {r2_improvement:+.1f}%")
    print(f"   Directional Accuracy Change: {dir_improvement:+.1f}%")

    if dual_processing_metrics['r2_score'] > bqx_only_metrics['r2_score']:
        print(f"\n✅ DUAL PROCESSING IMPROVES PERFORMANCE!")
        print(f"   Recommendation: Use dual processing for all 196 models")
    elif dual_processing_metrics['r2_score'] < bqx_only_metrics['r2_score'] * 0.95:
        print(f"\n⚠️ Dual processing shows lower performance")
        print(f"   Recommendation: Further investigation needed")
    else:
        print(f"\n➡️ Performance is comparable")
        print(f"   Recommendation: Consider computational cost vs benefit")

    # Feature importance insights
    print(f"\n🔍 FEATURE IMPORTANCE INSIGHTS:")
    print(f"   IDX features contribution: {dual_metrics['feature_importance']['idx_percentage']:.1f}%")
    print(f"   BQX features contribution: {dual_metrics['feature_importance']['bqx_percentage']:.1f}%")

    print(f"\n📝 Top 5 Most Important Features:")
    for i, feat in enumerate(dual_metrics['feature_importance']['top_5_features'], 1):
        print(f"   {i}. {feat['feature']:15} - {feat['importance']:.4f}")

    # Save comparison results
    comparison_results = {
        'timestamp': datetime.now().isoformat(),
        'pair': 'EURUSD',
        'window': 45,
        'bqx_only': bqx_only_metrics,
        'dual_processing': dual_processing_metrics,
        'improvement': {
            'r2_score': f"{r2_improvement:+.1f}%",
            'directional_accuracy': f"{dir_improvement:+.1f}%"
        },
        'recommendation': 'USE_DUAL_PROCESSING' if r2_improvement > 0 else 'INVESTIGATE_FURTHER',
        'feature_importance': dual_metrics['feature_importance']
    }

    # Save to file
    output_file = '/home/micha/bqx_ml_v3/scripts/dual_processing_comparison.json'
    with open(output_file, 'w') as f:
        json.dump(comparison_results, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    return comparison_results


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXECUTING DUAL PROCESSING DIRECTIVE")
    print("Chief Engineer Message: 20251127_0010_CE_BA")
    print("User Preference: Dual Processing (IDX + BQX)")
    print("="*60)

    try:
        # Run comparison
        results = compare_approaches()

        print("\n" + "="*60)
        print("✅ DUAL PROCESSING EVALUATION COMPLETE")
        print("="*60)

        if results['recommendation'] == 'USE_DUAL_PROCESSING':
            print("\n🚀 Ready to scale dual processing to all 196 models!")
        else:
            print("\n📋 Further analysis recommended before scaling")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()