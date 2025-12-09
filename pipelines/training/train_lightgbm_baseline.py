#!/usr/bin/env python3
"""
LightGBM Baseline Training for BQX ML V3

Trains LightGBM models for all 7 prediction horizons using walk-forward validation.
Target: 95%+ directional accuracy for the farthest possible horizon.
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
from sklearn.metrics import accuracy_score, mean_squared_error

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# All 7 horizons to train
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# BQX windows for target columns
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]


def load_training_data(pair: str, split: dict) -> tuple:
    """Load training and validation data for a split."""
    client = bigquery.Client(project=PROJECT)

    # Use the same feature query structure as feature_selection_shap.py
    # but filtered by date range
    def build_query(date_start, date_end):
        return f"""
        WITH
        base AS (
            SELECT
                interval_time,
                bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
            FROM `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
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
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
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
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
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
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        agg AS (
            SELECT
                interval_time,
                agg_mean_45, agg_std_45, agg_min_45, agg_max_45, agg_range_45, agg_cv_45,
                agg_mean_90, agg_std_90, agg_min_90, agg_max_90, agg_range_90, agg_cv_90,
                agg_mean_180, agg_std_180, agg_min_180, agg_max_180, agg_range_180, agg_cv_180,
                agg_mean_360, agg_std_360, agg_min_360, agg_max_360, agg_range_360, agg_cv_360
            FROM `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        targets AS (
            SELECT
                interval_time,
                target_bqx45_h15, target_bqx45_h30, target_bqx45_h45,
                target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105,
                target_bqx90_h15, target_bqx90_h30, target_bqx90_h45,
                target_bqx90_h60, target_bqx90_h75, target_bqx90_h90, target_bqx90_h105
            FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        )
        SELECT
            base.interval_time,
            base.bqx_45, base.bqx_90, base.bqx_180, base.bqx_360,
            base.bqx_720, base.bqx_1440, base.bqx_2880,
            lag45.lag45_bqx_close, lag45.lag45_bqx_lag, lag45.lag45_return,
            lag45.lag45_sma, lag45.lag45_ema, lag45.lag45_volatility,
            lag45.lag45_hl_range, lag45.lag45_momentum, lag45.lag45_positive_ratio,
            lag90.lag90_bqx_close, lag90.lag90_bqx_lag, lag90.lag90_return,
            lag90.lag90_sma, lag90.lag90_ema, lag90.lag90_volatility,
            lag90.lag90_hl_range, lag90.lag90_momentum, lag90.lag90_positive_ratio,
            regime45.reg45_volatility, regime45.reg45_hl_range, regime45.reg45_return,
            regime45.reg45_momentum, regime45.reg45_vol_regime, regime45.reg45_range_regime,
            regime45.reg45_return_regime, regime45.reg45_momentum_regime,
            agg.agg_mean_45, agg.agg_std_45, agg.agg_min_45, agg.agg_max_45,
            agg.agg_range_45, agg.agg_cv_45,
            agg.agg_mean_90, agg.agg_std_90, agg.agg_min_90, agg.agg_max_90,
            agg.agg_range_90, agg.agg_cv_90,
            agg.agg_mean_180, agg.agg_std_180, agg.agg_min_180, agg.agg_max_180,
            agg.agg_range_180, agg.agg_cv_180,
            agg.agg_mean_360, agg.agg_std_360, agg.agg_min_360, agg.agg_max_360,
            agg.agg_range_360, agg.agg_cv_360,
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

    print(f"  Loading training data: {split['train']['start']} to {split['train']['end']}...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train rows: {len(train_df):,}")

    print(f"  Loading validation data: {split['validation']['start']} to {split['validation']['end']}...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val rows: {len(val_df):,}")

    return train_df, val_df


def calculate_directional_accuracy(y_true, y_pred, y_current):
    """
    Calculate directional accuracy - the key metric for trading.

    Direction is correct if:
    - Predicted direction (sign of y_pred) matches actual direction (sign of y_true)
    - Or if both predict continuation of current value
    """
    # Direction: positive means BQX will increase, negative means decrease
    actual_direction = np.sign(y_true)
    pred_direction = np.sign(y_pred)

    # Directional accuracy
    correct = (actual_direction == pred_direction)
    return np.mean(correct)


def train_horizon_model(X_train, y_train, X_val, y_val, horizon: int):
    """Train LightGBM for a single horizon."""

    # Clean data
    train_mask = ~(X_train.isna().any(axis=1) | y_train.isna())
    val_mask = ~(X_val.isna().any(axis=1) | y_val.isna())

    X_train_clean = X_train[train_mask].copy()
    y_train_clean = y_train[train_mask].copy()
    X_val_clean = X_val[val_mask].copy()
    y_val_clean = y_val[val_mask].copy()

    if len(X_train_clean) < 1000 or len(X_val_clean) < 100:
        return None, {"error": "Insufficient data"}

    # LightGBM parameters
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 63,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'seed': 42
    }

    train_data = lgb.Dataset(X_train_clean, label=y_train_clean)
    val_data = lgb.Dataset(X_val_clean, label=y_val_clean, reference=train_data)

    # Train with early stopping
    model = lgb.train(
        params,
        train_data,
        num_boost_round=500,
        valid_sets=[val_data],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )

    # Predictions
    y_pred = model.predict(X_val_clean)

    # Metrics
    rmse = np.sqrt(mean_squared_error(y_val_clean, y_pred))

    # Directional accuracy (key metric!)
    dir_acc = calculate_directional_accuracy(y_val_clean, y_pred, X_val_clean['bqx_45'])

    metrics = {
        "horizon": f"h{horizon}",
        "train_rows": len(X_train_clean),
        "val_rows": len(X_val_clean),
        "rmse": float(rmse),
        "directional_accuracy": float(dir_acc),
        "best_iteration": model.best_iteration
    }

    return model, metrics


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 60)
    print(f"LightGBM Baseline Training for {pair.upper()}")
    print(f"Training on split {split_id}")
    print("=" * 60)

    # Load split configuration
    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)

    split = splits_config['splits'][split_id]
    print(f"\nSplit {split_id}:")
    print(f"  Train: {split['train']['start']} to {split['train']['end']}")
    print(f"  Val:   {split['validation']['start']} to {split['validation']['end']}")

    # Load data
    train_df, val_df = load_training_data(pair, split)

    # Identify feature and target columns
    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Targets: {len(target_cols)}")

    X_train = train_df[feature_cols]
    X_val = val_df[feature_cols]

    # Train for each horizon
    results = []

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n--- Training for h{horizon} ---")

        if target_col not in train_df.columns:
            print(f"  Target column {target_col} not found, skipping...")
            continue

        y_train = train_df[target_col]
        y_val = val_df[target_col]

        model, metrics = train_horizon_model(X_train, y_train, X_val, y_val, horizon)

        if model is None:
            print(f"  FAILED: {metrics.get('error', 'Unknown error')}")
            continue

        print(f"  RMSE: {metrics['rmse']:.6f}")
        print(f"  Directional Accuracy: {metrics['directional_accuracy']:.2%}")
        print(f"  Best Iteration: {metrics['best_iteration']}")

        results.append(metrics)

        # Check if we hit 95%!
        if metrics['directional_accuracy'] >= 0.95:
            print(f"  *** ACHIEVED 95%+ ACCURACY! ***")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Horizon':<10} {'Dir Acc':<12} {'RMSE':<12} {'Status'}")
    print("-" * 50)

    best_horizon = None
    best_acc = 0

    for r in results:
        status = "PASS" if r['directional_accuracy'] >= 0.95 else ""
        print(f"{r['horizon']:<10} {r['directional_accuracy']:.2%}{'':>6} {r['rmse']:.6f}{'':>3} {status}")

        if r['directional_accuracy'] > best_acc:
            best_acc = r['directional_accuracy']
            best_horizon = r['horizon']

    print(f"\nBest horizon: {best_horizon} with {best_acc:.2%} accuracy")

    # Save results
    output = {
        "pair": pair,
        "split_id": split_id,
        "split": split,
        "results": results,
        "best_horizon": best_horizon,
        "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/lightgbm_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
