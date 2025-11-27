#!/usr/bin/env python3
"""
Smart Dual Processing Implementation
Per CE directive 20251127_0052 - Critical Priority
Combines IDX (leading indicators) with BQX (lagging context) using weighted features
Target: R² > 0.50
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import time
from datetime import datetime
import json


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def create_smart_dual_features(idx_data, bqx_data, window):
    """
    Create 12-15 carefully selected and weighted features
    Per CE directive 20251127_0052
    """

    features = pd.DataFrame(index=idx_data.index)

    # CRITICAL: Recent IDX (Leading Indicators) - Weight 2.0-1.2
    features['idx_lag_1'] = idx_data['close_idx'].shift(1)  # Weight: 2.0
    features['idx_lag_2'] = idx_data['close_idx'].shift(2)  # Weight: 1.8
    features['idx_lag_3'] = idx_data['close_idx'].shift(3)  # Weight: 1.5
    features['idx_lag_5'] = idx_data['close_idx'].shift(5)  # Weight: 1.2

    # IMPORTANT: BQX Trends (Momentum Context) - Weight 1.0-0.7
    bqx_col = f'bqx_{window}'
    if bqx_col in bqx_data.columns:
        features['bqx_lag_1'] = bqx_data[bqx_col].shift(1)  # Weight: 1.0
        features['bqx_lag_3'] = bqx_data[bqx_col].shift(3)  # Weight: 0.9
        features['bqx_lag_7'] = bqx_data[bqx_col].shift(7)  # Weight: 0.8
        features['bqx_lag_14'] = bqx_data[bqx_col].shift(14)  # Weight: 0.7

    # CONTEXTUAL: Derived Features - Weight 0.6-0.8
    features['idx_ma_ratio'] = idx_data['close_idx'] / idx_data['close_idx'].rolling(20).mean()
    features['idx_volatility'] = idx_data['close_idx'].rolling(20).std()

    if bqx_col in bqx_data.columns:
        features['bqx_acceleration'] = bqx_data[bqx_col].diff()

    features['idx_rsi'] = calculate_rsi(idx_data['close_idx'], 14)

    # Feature count should be 12-15
    print(f"  📊 Smart Dual Features Created: {len(features.columns)} features")

    return features


def compute_feature_weights(X):
    """
    Apply importance weights to features
    Per CE directive - emphasize leading indicators
    """

    weights_map = {
        'idx_lag_1': 2.0,
        'idx_lag_2': 1.8,
        'idx_lag_3': 1.5,
        'idx_lag_5': 1.2,
        'bqx_lag_1': 1.0,
        'bqx_lag_3': 0.9,
        'bqx_lag_7': 0.8,
        'bqx_lag_14': 0.7,
        'idx_ma_ratio': 0.8,
        'idx_volatility': 0.7,
        'bqx_acceleration': 0.6,
        'idx_rsi': 0.7
    }

    # Create base sample weights
    sample_weights = np.ones(len(X))

    # Apply feature-based weighting
    for col in X.columns:
        if col in weights_map:
            # Normalize feature values
            feature_vals = X[col].fillna(0)
            feature_norm = np.abs(feature_vals) / (np.abs(feature_vals).max() + 1e-6)

            # Apply weight
            sample_weights += weights_map[col] * feature_norm

    # Normalize weights
    sample_weights = sample_weights / sample_weights.mean()

    return sample_weights


def train_smart_dual_model(pair: str, window: int):
    """
    Train XGBoost model using Smart Dual Processing
    Target: R² > 0.50
    """

    print(f"\n{'='*60}")
    print(f"SMART DUAL PROCESSING - {pair}-{window}")
    print(f"Target R² > 0.50")
    print(f"{'='*60}")

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    # Load IDX data
    idx_query = f"""
    SELECT
        interval_time,
        close_idx
    FROM `bqx-ml.bqx_ml_v3_features.{pair.lower()}_idx`
    ORDER BY interval_time
    """

    print(f"\n📊 Loading data...")
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

    # Merge datasets
    df = idx_df.join(bqx_df, how='inner')

    print(f"   IDX rows: {len(idx_df):,}")
    print(f"   BQX rows: {len(bqx_df):,}")
    print(f"   Merged rows: {len(df):,}")

    # Create Smart Dual features
    features_df = create_smart_dual_features(idx_df, bqx_df, window)

    # Combine with target
    final_df = features_df.join(bqx_df[['target']], how='inner')

    # Remove NaN rows
    final_df = final_df.dropna()

    # Create splits (with temporal gaps)
    n_rows = len(final_df)
    train_end = int(n_rows * 0.7)
    val_start = train_end + 100  # 100-interval gap
    val_end = int(n_rows * 0.85)
    test_start = val_end + 50  # 50-interval gap

    # Split data
    train_df = final_df.iloc[:train_end]
    val_df = final_df.iloc[val_start:val_end]
    test_df = final_df.iloc[test_start:]

    print(f"\n📊 Data splits:")
    print(f"   Train: {len(train_df):,} rows")
    print(f"   Validation: {len(val_df):,} rows")
    print(f"   Test: {len(test_df):,} rows")

    # Prepare features and targets
    feature_cols = [col for col in final_df.columns if col != 'target']
    X_train = train_df[feature_cols]
    y_train = train_df['target']
    X_val = val_df[feature_cols]
    y_val = val_df['target']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    # Smart Dual XGBoost configuration (per CE directive)
    smart_params = {
        'n_estimators': 200,      # More trees for complex patterns
        'max_depth': 8,           # Capture IDX/BQX interactions
        'learning_rate': 0.05,    # Slower, stable learning
        'colsample_bytree': 0.7,  # Feature sampling
        'subsample': 0.8,
        'reg_alpha': 0.1,         # L1 regularization
        'reg_lambda': 1.0,        # L2 regularization
        'random_state': 42,
        'n_jobs': -1,
        'tree_method': 'hist',
        'early_stopping_rounds': 20,
        'eval_metric': 'rmse'
    }

    print(f"\n🔧 Training Smart Dual XGBoost model...")

    # Compute sample weights
    sample_weights = compute_feature_weights(X_train)

    # Train model
    start_time = time.time()
    model = xgb.XGBRegressor(**smart_params)

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

    # Directional accuracy
    val_dir_acc = np.mean(np.sign(y_val) == np.sign(y_pred_val))

    test_r2 = r2_score(y_test, y_pred_test)
    test_dir_acc = np.mean(np.sign(y_test) == np.sign(y_pred_test))

    # Feature importance analysis
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    # Calculate importance by category
    idx_importance = feature_importance[feature_importance['feature'].str.startswith('idx_')]['importance'].sum()
    bqx_importance = feature_importance[feature_importance['feature'].str.startswith('bqx_')]['importance'].sum()
    derived_importance = 1.0 - idx_importance - bqx_importance

    print(f"\n📊 RESULTS:")
    print(f"   R² Score (Val): {val_r2:.4f} {'✅ EXCEEDS 0.50!' if val_r2 > 0.50 else '⚠️ Below 0.50'}")
    print(f"   Directional Accuracy: {val_dir_acc:.2%} {'✅' if val_dir_acc > 0.75 else ''}")
    print(f"   RMSE: {val_rmse:.4f}")
    print(f"   Training Time: {training_time:.2f}s")

    print(f"\n🔍 Feature Importance Distribution:")
    print(f"   IDX features: {idx_importance:.1%} (Target: 40-50%)")
    print(f"   BQX features: {bqx_importance:.1%} (Target: 30-40%)")
    print(f"   Derived features: {derived_importance:.1%} (Target: 10-20%)")

    print(f"\n📝 Top 5 Features:")
    for i, row in enumerate(feature_importance.head(5).itertuples(), 1):
        print(f"   {i}. {row.feature}: {row.importance:.4f}")

    # Success criteria check
    success_criteria = {
        'r2_exceeds_50': val_r2 > 0.50,
        'feature_count_12_15': 12 <= len(feature_cols) <= 15,
        'idx_importance_40_50': 0.40 <= idx_importance <= 0.50,
        'bqx_importance_30_40': 0.30 <= bqx_importance <= 0.40,
        'training_under_0_5s': training_time < 0.5
    }

    print(f"\n✅ Success Criteria:")
    for criteria, passed in success_criteria.items():
        print(f"   {criteria}: {'✅ PASSED' if passed else '❌ FAILED'}")

    # Return comprehensive results
    return {
        'model_id': f'{pair}-{window}',
        'approach': 'smart_dual',
        'n_features': len(feature_cols),
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
        'feature_importance': {
            'idx_percentage': round(idx_importance * 100, 1),
            'bqx_percentage': round(bqx_importance * 100, 1),
            'derived_percentage': round(derived_importance * 100, 1),
            'top_5': feature_importance.head(5).to_dict('records')
        },
        'training_time_seconds': round(training_time, 2),
        'success_criteria': success_criteria,
        'timestamp': datetime.now().isoformat()
    }


def main():
    """
    Test Smart Dual Processing on EURUSD-45
    Per CE directive: Achieve R² > 0.50
    """

    print("\n" + "="*60)
    print("SMART DUAL PROCESSING IMPLEMENTATION")
    print("CE Directive 20251127_0052 - CRITICAL PRIORITY")
    print("="*60)

    print("\n📌 Key Insights:")
    print("   - BQX values are LAGGED indicators")
    print("   - IDX provides LEADING indicators")
    print("   - Smart Dual uses weighted 12-15 features")
    print("   - Target: R² > 0.50")

    # Test with EURUSD-45 first
    try:
        results = train_smart_dual_model('EURUSD', 45)

        # Save results
        output_file = '/home/micha/bqx_ml_v3/scripts/smart_dual_results.json'
        with open(output_file, 'w') as f:
            # Convert numpy types to Python types for JSON serialization
            json_safe_results = json.loads(json.dumps(results, default=str))
            json.dump(json_safe_results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Final assessment
        if results['metrics']['validation']['r2_score'] > 0.50:
            print("\n🎉 SUCCESS! Smart Dual Processing achieves R² > 0.50!")
            print("Ready to scale to all 196 models")
        else:
            print("\n⚠️ R² below 0.50 target. May need parameter tuning.")

        return results

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()

    if results:
        print("\n" + "="*60)
        print("SMART DUAL PROCESSING TEST COMPLETE")
        print("Report to CE immediately with results")
        print("="*60)