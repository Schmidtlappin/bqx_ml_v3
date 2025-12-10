#!/usr/bin/env python3
"""
SHAP Value Generation for EURUSD h15
USER MANDATE: 100,000+ samples minimum (BINDING)

Generates TreeSHAP values for all base models and updates feature ledger.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier
import shap
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# USER MANDATE: BINDING
SHAP_SAMPLE_SIZE = 100_000


def load_training_data(pair: str, horizon: int, sample_limit: int = 120000):
    """Load training data for SHAP calculation."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        reg_idx.interval_time,
        -- Polynomial IDX
        reg_idx.reg_quad_term_45, reg_idx.reg_lin_term_45, reg_idx.reg_total_var_45,
        reg_idx.reg_slope_45, reg_idx.reg_trend_str_45, reg_idx.reg_deviation_45, reg_idx.reg_zscore_45,
        reg_idx.reg_quad_term_90, reg_idx.reg_lin_term_90, reg_idx.reg_total_var_90,
        reg_idx.reg_slope_90, reg_idx.reg_trend_str_90, reg_idx.reg_deviation_90, reg_idx.reg_zscore_90,
        reg_idx.reg_quad_term_180, reg_idx.reg_lin_term_180, reg_idx.reg_total_var_180,
        reg_idx.reg_slope_180, reg_idx.reg_trend_str_180, reg_idx.reg_deviation_180, reg_idx.reg_zscore_180,
        reg_idx.reg_quad_term_360, reg_idx.reg_lin_term_360, reg_idx.reg_total_var_360,
        reg_idx.reg_slope_360, reg_idx.reg_trend_str_360,
        reg_idx.reg_quad_term_720, reg_idx.reg_lin_term_720, reg_idx.reg_total_var_720,
        reg_idx.reg_slope_720, reg_idx.reg_trend_str_720,
        reg_idx.reg_quad_term_1440, reg_idx.reg_lin_term_1440, reg_idx.reg_total_var_1440,
        reg_idx.reg_slope_1440, reg_idx.reg_trend_str_1440,

        -- Polynomial BQX
        reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
        reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_slope_45 as bqx_slope_45,
        reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
        reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_slope_90 as bqx_slope_90,
        reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
        reg_bqx.reg_total_var_180 as bqx_tvar_180,

        -- Base BQX
        base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,

        -- Regime indicators
        agg_bqx.agg_std_45 as regime_vol_45, agg_bqx.agg_std_90 as regime_vol_90,
        agg_bqx.agg_cv_45 as regime_cv_45, agg_bqx.agg_cv_90 as regime_cv_90,

        -- Derivative features
        der_bqx.der_v1_45 as regime_der1_45, der_bqx.der_v1_90 as regime_der1_90,
        der_bqx.der_v2_45 as regime_der2_45, der_bqx.der_v2_90 as regime_der2_90,

        -- Target
        targets.target_bqx45_h{horizon}

    FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` reg_idx
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` reg_bqx
        ON reg_idx.interval_time = reg_bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base_bqx
        ON reg_idx.interval_time = base_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}` agg_bqx
        ON reg_idx.interval_time = agg_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.der_bqx_{pair}` der_bqx
        ON reg_idx.interval_time = der_bqx.interval_time
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON reg_idx.interval_time = targets.interval_time
    WHERE targets.target_bqx45_h{horizon} IS NOT NULL
    ORDER BY reg_idx.interval_time
    LIMIT {sample_limit}
    """

    return client.query(query).to_dataframe()


def train_models_for_shap(X, y, feature_names):
    """Train models specifically for SHAP calculation."""
    from xgboost import XGBClassifier
    models = {}

    # LightGBM
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 63, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1,
        'seed': 42, 'min_data_in_leaf': 50
    }
    lgb_train = lgb.Dataset(X, label=y, feature_name=feature_names)
    models['lightgbm'] = lgb.train(lgb_params, lgb_train, num_boost_round=300)

    # XGBoost (sklearn API for SHAP compatibility)
    models['xgboost'] = XGBClassifier(
        objective='binary:logistic', max_depth=5, learning_rate=0.03,
        subsample=0.8, colsample_bytree=0.6, random_state=42, verbosity=0,
        n_estimators=300, use_label_encoder=False, eval_metric='logloss'
    )
    models['xgboost'].fit(X, y)

    # CatBoost
    models['catboost'] = CatBoostClassifier(
        iterations=300, learning_rate=0.03, depth=5,
        loss_function='Logloss', verbose=False, random_seed=42
    )
    models['catboost'].fit(X, y, verbose=False)

    return models


def calculate_shap_values(models, X, feature_names, sample_size=SHAP_SAMPLE_SIZE):
    """Calculate SHAP values for all models."""

    # Ensure we have enough samples
    if len(X) < sample_size:
        print(f"  WARNING: Only {len(X)} samples available, using all")
        sample_size = len(X)

    # Sample data for SHAP
    np.random.seed(42)
    indices = np.random.choice(len(X), size=sample_size, replace=False)
    X_sample = X[indices]

    shap_results = {}

    print(f"  Calculating SHAP for {sample_size:,} samples...")

    # LightGBM SHAP
    print("    LightGBM TreeSHAP...")
    lgb_explainer = shap.TreeExplainer(models['lightgbm'])
    lgb_shap = lgb_explainer.shap_values(X_sample)
    if isinstance(lgb_shap, list):
        lgb_shap = lgb_shap[1]  # Take positive class
    shap_results['lightgbm'] = np.abs(lgb_shap).mean(axis=0)

    # XGBoost TreeSHAP (XGBoost 2.1.0 compatible)
    print("    XGBoost TreeSHAP...")
    xgb_explainer = shap.TreeExplainer(models['xgboost'])
    xgb_shap = xgb_explainer.shap_values(X_sample)
    if isinstance(xgb_shap, list):
        xgb_shap = xgb_shap[1]  # Take positive class for binary classification
    shap_results['xgboost'] = np.abs(xgb_shap).mean(axis=0)
    print("      XGBoost TreeSHAP: SUCCESS")

    # CatBoost SHAP
    print("    CatBoost TreeSHAP...")
    cb_explainer = shap.TreeExplainer(models['catboost'])
    cb_shap = cb_explainer.shap_values(X_sample)
    shap_results['catboost'] = np.abs(cb_shap).mean(axis=0)

    # Ensemble average (3 TreeSHAP models: LGB, XGB, CB)
    ensemble_shap = (shap_results['lightgbm'] + shap_results['xgboost'] + shap_results['catboost']) / 3

    # Create feature importance DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'lgb_shap': shap_results['lightgbm'],
        'xgb_shap': shap_results['xgboost'],
        'cb_shap': shap_results['catboost'],
        'ensemble_shap': ensemble_shap
    }).sort_values('ensemble_shap', ascending=False)

    return importance_df, sample_size


def main():
    pair = "eurusd"
    horizon = 15

    print("=" * 70)
    print("SHAP VALUE GENERATION - EURUSD h15")
    print(f"USER MANDATE: {SHAP_SAMPLE_SIZE:,}+ samples (BINDING)")
    print("=" * 70)

    # Load data
    print("\nStep 1: Loading training data...")
    df = load_training_data(pair, horizon, sample_limit=120000)
    print(f"  Loaded {len(df):,} rows")

    # Prepare features
    target_col = f'target_bqx45_h{horizon}'
    feature_cols = [c for c in df.columns if c not in [target_col, 'interval_time', 'pair']]

    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values
    y = (df[target_col] > 0).astype(int).values

    print(f"  Features: {len(feature_cols)}")
    print(f"  Samples: {len(X):,}")

    # Train models
    print("\nStep 2: Training models for SHAP...")
    models = train_models_for_shap(X, y, feature_cols)
    print("  Models trained: LightGBM, XGBoost, CatBoost")

    # Calculate SHAP
    print("\nStep 3: Calculating TreeSHAP values...")
    importance_df, actual_samples = calculate_shap_values(models, X, feature_cols)

    # Validate mandate compliance
    print("\n" + "=" * 70)
    print("SHAP MANDATE VALIDATION")
    print("=" * 70)
    print(f"  Required samples: {SHAP_SAMPLE_SIZE:,}")
    print(f"  Actual samples: {actual_samples:,}")

    if actual_samples >= SHAP_SAMPLE_SIZE:
        print("  STATUS: MANDATE COMPLIANT")
    else:
        print("  STATUS: MANDATE VIOLATION - Insufficient samples")

    # Top 20 features
    print("\nTop 20 Features by Ensemble SHAP:")
    print("-" * 50)
    for i, row in importance_df.head(20).iterrows():
        print(f"  {row['feature']:30s} {row['ensemble_shap']:.6f}")

    # Save results
    output = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'shap_sample_size': actual_samples,
        'mandate_compliant': actual_samples >= SHAP_SAMPLE_SIZE,
        'feature_count': len(feature_cols),
        'top_20_features': importance_df.head(20)[['feature', 'ensemble_shap']].to_dict('records'),
        'all_features': importance_df[['feature', 'ensemble_shap', 'lgb_shap', 'xgb_shap', 'cb_shap']].to_dict('records')
    }

    output_file = f"/home/micha/bqx_ml_v3/intelligence/shap_eurusd_h15.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Summary
    print("\n" + "=" * 70)
    print("SHAP GENERATION COMPLETE")
    print("=" * 70)
    print(f"  Samples used: {actual_samples:,}")
    print(f"  Features analyzed: {len(feature_cols)}")
    print(f"  Mandate compliance: {'YES' if actual_samples >= SHAP_SAMPLE_SIZE else 'NO'}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
