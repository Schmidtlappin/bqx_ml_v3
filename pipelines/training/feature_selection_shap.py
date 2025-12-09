#!/usr/bin/env python3
"""
SHAP-based Feature Selection for BQX ML V3

Strategy:
1. Load core EURUSD features from BigQuery (10% sample)
2. Train quick LightGBM on each horizon target
3. Extract SHAP values
4. Select top 500-1000 features based on mean |SHAP|
"""

import sys
import json
import numpy as np
import pandas as pd
from google.cloud import bigquery
import lightgbm as lgb
import shap
from datetime import datetime

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# BQX windows and prediction horizons
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def get_feature_query(pair: str, sample_pct: float = 10.0) -> str:
    """Generate query to fetch EURUSD features joined with targets."""

    # Core feature tables to join
    query = f"""
    WITH
    -- Base BQX features
    base AS (
        SELECT
            interval_time,
            bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
        FROM `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}`
        WHERE RAND() < {sample_pct / 100.0}
    ),

    -- Lag features (45 and 90 minute windows)
    lag45 AS (
        SELECT
            interval_time,
            bqx_close as lag45_bqx_close,
            bqx_lag_45 as lag45_bqx_lag,
            return_lag_45 as lag45_return,
            sma_45 as lag45_sma,
            ema_45 as lag45_ema,
            volatility_45 as lag45_volatility,
            hl_range_45 as lag45_hl_range,
            momentum_45 as lag45_momentum,
            positive_ratio_45 as lag45_positive_ratio
        FROM `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_45`
    ),

    lag90 AS (
        SELECT
            interval_time,
            bqx_close as lag90_bqx_close,
            bqx_lag_90 as lag90_bqx_lag,
            return_lag_90 as lag90_return,
            sma_90 as lag90_sma,
            ema_90 as lag90_ema,
            volatility_90 as lag90_volatility,
            hl_range_90 as lag90_hl_range,
            momentum_90 as lag90_momentum,
            positive_ratio_90 as lag90_positive_ratio
        FROM `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_90`
    ),

    -- Regime features (45 minute window)
    regime45 AS (
        SELECT
            interval_time,
            volatility_45 as reg45_volatility,
            hl_range_45 as reg45_hl_range,
            return_lag_45 as reg45_return,
            momentum_45 as reg45_momentum,
            volatility_regime_code as reg45_vol_regime,
            range_regime_code as reg45_range_regime,
            return_regime_code as reg45_return_regime,
            momentum_regime_code as reg45_momentum_regime
        FROM `{PROJECT}.{FEATURES_DATASET}.regime_bqx_{pair}_45`
    ),

    -- Aggregation features
    agg AS (
        SELECT
            interval_time,
            agg_mean_45, agg_std_45, agg_min_45, agg_max_45, agg_range_45, agg_cv_45,
            agg_mean_90, agg_std_90, agg_min_90, agg_max_90, agg_range_90, agg_cv_90,
            agg_mean_180, agg_std_180, agg_min_180, agg_max_180, agg_range_180, agg_cv_180,
            agg_mean_360, agg_std_360, agg_min_360, agg_max_360, agg_range_360, agg_cv_360
        FROM `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}`
    ),

    -- Targets
    targets AS (
        SELECT
            interval_time,
            target_bqx45_h15, target_bqx45_h30, target_bqx45_h45, target_bqx45_h60,
            target_bqx45_h75, target_bqx45_h90, target_bqx45_h105,
            target_bqx90_h15, target_bqx90_h30, target_bqx90_h45, target_bqx90_h60,
            target_bqx90_h75, target_bqx90_h90, target_bqx90_h105
        FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    )

    SELECT
        base.interval_time,
        -- Base BQX features
        base.bqx_45, base.bqx_90, base.bqx_180, base.bqx_360,
        base.bqx_720, base.bqx_1440, base.bqx_2880,
        -- Lag 45 features
        lag45.lag45_bqx_close, lag45.lag45_bqx_lag, lag45.lag45_return,
        lag45.lag45_sma, lag45.lag45_ema, lag45.lag45_volatility,
        lag45.lag45_hl_range, lag45.lag45_momentum, lag45.lag45_positive_ratio,
        -- Lag 90 features
        lag90.lag90_bqx_close, lag90.lag90_bqx_lag, lag90.lag90_return,
        lag90.lag90_sma, lag90.lag90_ema, lag90.lag90_volatility,
        lag90.lag90_hl_range, lag90.lag90_momentum, lag90.lag90_positive_ratio,
        -- Regime features
        regime45.reg45_volatility, regime45.reg45_hl_range, regime45.reg45_return,
        regime45.reg45_momentum, regime45.reg45_vol_regime, regime45.reg45_range_regime,
        regime45.reg45_return_regime, regime45.reg45_momentum_regime,
        -- Aggregation features
        agg.agg_mean_45, agg.agg_std_45, agg.agg_min_45, agg.agg_max_45,
        agg.agg_range_45, agg.agg_cv_45,
        agg.agg_mean_90, agg.agg_std_90, agg.agg_min_90, agg.agg_max_90,
        agg.agg_range_90, agg.agg_cv_90,
        agg.agg_mean_180, agg.agg_std_180, agg.agg_min_180, agg.agg_max_180,
        agg.agg_range_180, agg.agg_cv_180,
        agg.agg_mean_360, agg.agg_std_360, agg.agg_min_360, agg.agg_max_360,
        agg.agg_range_360, agg.agg_cv_360,
        -- Targets
        targets.target_bqx45_h15, targets.target_bqx45_h30, targets.target_bqx45_h45,
        targets.target_bqx45_h60, targets.target_bqx45_h75, targets.target_bqx45_h90,
        targets.target_bqx45_h105
    FROM base
    JOIN lag45 ON base.interval_time = lag45.interval_time
    JOIN lag90 ON base.interval_time = lag90.interval_time
    JOIN regime45 ON base.interval_time = regime45.interval_time
    JOIN agg ON base.interval_time = agg.interval_time
    JOIN targets ON base.interval_time = targets.interval_time
    WHERE targets.target_bqx45_h15 IS NOT NULL
    """

    return query


def load_features(pair: str, sample_pct: float = 10.0) -> pd.DataFrame:
    """Load features from BigQuery."""
    print(f"Loading {sample_pct}% sample of {pair} features...")

    client = bigquery.Client(project=PROJECT)
    query = get_feature_query(pair, sample_pct)

    df = client.query(query).to_dataframe()
    print(f"  Loaded {len(df):,} rows with {len(df.columns)} columns")

    return df


def train_lightgbm_shap(X: pd.DataFrame, y: pd.Series, target_name: str) -> dict:
    """Train LightGBM and extract SHAP values."""
    print(f"\nTraining LightGBM for {target_name}...")

    # Remove NaN rows
    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].copy()
    y_clean = y[mask].copy()

    print(f"  Clean rows: {len(X_clean):,} (removed {(~mask).sum():,} NaN rows)")

    if len(X_clean) < 1000:
        print(f"  Warning: Only {len(X_clean)} rows, skipping...")
        return {}

    # Train LightGBM
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'seed': 42
    }

    train_data = lgb.Dataset(X_clean, label=y_clean)
    model = lgb.train(params, train_data, num_boost_round=100)

    # Extract SHAP values
    print("  Extracting SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_clean)

    # Calculate mean absolute SHAP value per feature
    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    feature_importance = dict(zip(X_clean.columns, mean_abs_shap))

    # Sort by importance
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

    print(f"  Top 5 features:")
    for feat, imp in sorted_features[:5]:
        print(f"    {feat}: {imp:.6f}")

    return feature_importance


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    sample_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    print("=" * 60)
    print(f"SHAP-based Feature Selection for {pair.upper()}")
    print(f"Sample: {sample_pct}%")
    print("=" * 60)

    # Load features
    df = load_features(pair, sample_pct)

    # Identify feature and target columns
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Targets: {len(target_cols)}")

    X = df[feature_cols]

    # Train for each target (horizon)
    all_importance = {}

    for target_col in target_cols[:7]:  # First 7 horizons (bqx45)
        y = df[target_col]
        importance = train_lightgbm_shap(X, y, target_col)

        for feat, imp in importance.items():
            if feat not in all_importance:
                all_importance[feat] = []
            all_importance[feat].append(imp)

    # Average importance across horizons
    avg_importance = {feat: np.mean(imps) for feat, imps in all_importance.items()}
    sorted_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)

    # Save results
    output = {
        "pair": pair,
        "sample_pct": sample_pct,
        "total_features": len(feature_cols),
        "timestamp": datetime.now().isoformat(),
        "feature_importance": [{"feature": f, "mean_abs_shap": float(v)} for f, v in sorted_features]
    }

    output_file = f"/tmp/shap_features_{pair}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total features analyzed: {len(feature_cols)}")
    print(f"\nTop 20 features by mean |SHAP|:")
    for i, (feat, imp) in enumerate(sorted_features[:20], 1):
        print(f"  {i:2d}. {feat}: {imp:.6f}")

    print(f"\nResults saved to: {output_file}")

    # Return top 500 features
    top_500 = [f for f, _ in sorted_features[:500]]
    print(f"\nTop 500 features saved for training pipeline")


if __name__ == "__main__":
    main()
