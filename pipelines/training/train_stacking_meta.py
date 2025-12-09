#!/usr/bin/env python3
"""
Stacking Meta-Learner for BQX ML V3

Uses out-of-fold predictions from base models (LGB, XGB, CB) to train
a meta-learner for improved ensemble performance.

Architecture:
  Level 1: LightGBM + XGBoost + CatBoost (base learners)
  Level 2: Logistic Regression / Ridge Regression (meta-learner)
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def load_data(pair: str, split: dict) -> tuple:
    """Load training and validation data."""
    client = bigquery.Client(project=PROJECT)

    def build_query(date_start, date_end):
        return f"""
        WITH
        base AS (
            SELECT interval_time, bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
            FROM `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        lag45 AS (
            SELECT interval_time, bqx_close as lag45_bqx_close, bqx_lag_45 as lag45_bqx_lag,
                   return_lag_45 as lag45_return, sma_45 as lag45_sma, ema_45 as lag45_ema,
                   volatility_45 as lag45_volatility, hl_range_45 as lag45_hl_range,
                   momentum_45 as lag45_momentum, positive_ratio_45 as lag45_positive_ratio
            FROM `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_45`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        lag90 AS (
            SELECT interval_time, bqx_close as lag90_bqx_close, bqx_lag_90 as lag90_bqx_lag,
                   return_lag_90 as lag90_return, sma_90 as lag90_sma, ema_90 as lag90_ema,
                   volatility_90 as lag90_volatility, hl_range_90 as lag90_hl_range,
                   momentum_90 as lag90_momentum, positive_ratio_90 as lag90_positive_ratio
            FROM `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_90`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        regime45 AS (
            SELECT interval_time, volatility_45 as reg45_volatility, hl_range_45 as reg45_hl_range,
                   return_lag_45 as reg45_return, momentum_45 as reg45_momentum,
                   volatility_regime_code as reg45_vol_regime, range_regime_code as reg45_range_regime,
                   return_regime_code as reg45_return_regime, momentum_regime_code as reg45_momentum_regime
            FROM `{PROJECT}.{FEATURES_DATASET}.regime_bqx_{pair}_45`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        agg AS (
            SELECT interval_time,
                   agg_mean_45, agg_std_45, agg_min_45, agg_max_45, agg_range_45, agg_cv_45,
                   agg_mean_90, agg_std_90, agg_min_90, agg_max_90, agg_range_90, agg_cv_90,
                   agg_mean_180, agg_std_180, agg_min_180, agg_max_180, agg_range_180, agg_cv_180,
                   agg_mean_360, agg_std_360, agg_min_360, agg_max_360, agg_range_360, agg_cv_360
            FROM `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ),
        targets AS (
            SELECT interval_time,
                   target_bqx45_h15, target_bqx45_h30, target_bqx45_h45,
                   target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105
            FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        )
        SELECT base.*, lag45.* EXCEPT(interval_time), lag90.* EXCEPT(interval_time),
               regime45.* EXCEPT(interval_time), agg.* EXCEPT(interval_time),
               targets.* EXCEPT(interval_time)
        FROM base
        JOIN lag45 ON base.interval_time = lag45.interval_time
        JOIN lag90 ON base.interval_time = lag90.interval_time
        JOIN regime45 ON base.interval_time = regime45.interval_time
        JOIN agg ON base.interval_time = agg.interval_time
        JOIN targets ON base.interval_time = targets.interval_time
        WHERE targets.target_bqx45_h15 IS NOT NULL
        """

    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()

    return train_df, val_df


def calculate_directional_accuracy(y_true, y_pred):
    """Calculate directional accuracy."""
    return np.mean(np.sign(y_true) == np.sign(y_pred))


def get_oof_predictions(X, y, n_folds=5):
    """Generate out-of-fold predictions from base models."""
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)

    oof_lgb = np.zeros(len(X))
    oof_xgb = np.zeros(len(X))
    oof_cb = np.zeros(len(X))

    for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
        X_tr, X_vl = X[train_idx], X[val_idx]
        y_tr, y_vl = y[train_idx], y[val_idx]

        # LightGBM
        lgb_params = {'objective': 'regression', 'metric': 'rmse', 'num_leaves': 63,
                      'learning_rate': 0.05, 'feature_fraction': 0.8, 'verbose': -1, 'seed': 42}
        lgb_train = lgb.Dataset(X_tr, label=y_tr)
        lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=200)
        oof_lgb[val_idx] = lgb_model.predict(X_vl)

        # XGBoost
        xgb_params = {'objective': 'reg:squarederror', 'max_depth': 6, 'learning_rate': 0.05,
                      'subsample': 0.8, 'colsample_bytree': 0.8, 'seed': 42, 'verbosity': 0}
        dtrain = xgb.DMatrix(X_tr, label=y_tr)
        xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=200)
        oof_xgb[val_idx] = xgb_model.predict(xgb.DMatrix(X_vl))

        # CatBoost
        cb_model = CatBoostRegressor(iterations=200, learning_rate=0.05, depth=6,
                                      loss_function='RMSE', verbose=False, random_seed=42)
        cb_model.fit(X_tr, y_tr, verbose=False)
        oof_cb[val_idx] = cb_model.predict(X_vl)

    return np.column_stack([oof_lgb, oof_xgb, oof_cb])


def train_stacking_for_horizon(X_train, y_train, X_val, y_val, horizon):
    """Train stacking ensemble for a single horizon."""
    # Convert to float and clean data
    X_train = X_train.astype(np.float64)
    X_val = X_val.astype(np.float64)
    y_train = y_train.astype(np.float64)
    y_val = y_val.astype(np.float64)

    train_mask = ~(np.isnan(X_train).any(axis=1) | np.isnan(y_train))
    val_mask = ~(np.isnan(X_val).any(axis=1) | np.isnan(y_val))

    X_tr = X_train[train_mask]
    y_tr = y_train[train_mask]
    X_vl = X_val[val_mask]
    y_vl = y_val[val_mask]

    if len(X_tr) < 1000:
        return None

    print(f"    Generating OOF predictions (5-fold)...")
    oof_train = get_oof_predictions(X_tr, y_tr, n_folds=5)

    # Train base models on full training data for validation predictions
    print(f"    Training base models on full train data...")

    # LightGBM
    lgb_train = lgb.Dataset(X_tr, label=y_tr)
    lgb_model = lgb.train({'objective': 'regression', 'metric': 'rmse', 'num_leaves': 63,
                           'learning_rate': 0.05, 'feature_fraction': 0.8, 'verbose': -1}, lgb_train, 300)
    lgb_val_pred = lgb_model.predict(X_vl)

    # XGBoost
    dtrain = xgb.DMatrix(X_tr, label=y_tr)
    xgb_model = xgb.train({'objective': 'reg:squarederror', 'max_depth': 6, 'learning_rate': 0.05,
                           'subsample': 0.8, 'verbosity': 0}, dtrain, 300)
    xgb_val_pred = xgb_model.predict(xgb.DMatrix(X_vl))

    # CatBoost
    cb_model = CatBoostRegressor(iterations=300, learning_rate=0.05, depth=6,
                                  loss_function='RMSE', verbose=False)
    cb_model.fit(X_tr, y_tr, verbose=False)
    cb_val_pred = cb_model.predict(X_vl)

    val_meta_features = np.column_stack([lgb_val_pred, xgb_val_pred, cb_val_pred])

    # Train meta-learner (Ridge regression)
    print(f"    Training meta-learner (Ridge)...")
    meta_model = Ridge(alpha=1.0)
    meta_model.fit(oof_train, y_tr)

    # Stacked predictions
    stacked_pred = meta_model.predict(val_meta_features)

    # Calculate metrics
    lgb_acc = calculate_directional_accuracy(y_vl, lgb_val_pred)
    xgb_acc = calculate_directional_accuracy(y_vl, xgb_val_pred)
    cb_acc = calculate_directional_accuracy(y_vl, cb_val_pred)
    avg_pred = (lgb_val_pred + xgb_val_pred + cb_val_pred) / 3
    avg_acc = calculate_directional_accuracy(y_vl, avg_pred)
    stacked_acc = calculate_directional_accuracy(y_vl, stacked_pred)

    results = {
        'lightgbm': {'accuracy': float(lgb_acc)},
        'xgboost': {'accuracy': float(xgb_acc)},
        'catboost': {'accuracy': float(cb_acc)},
        'avg_ensemble': {'accuracy': float(avg_acc)},
        'stacked': {'accuracy': float(stacked_acc)},
        'meta_weights': list(meta_model.coef_)
    }

    print(f"    LGB: {lgb_acc:.2%}, XGB: {xgb_acc:.2%}, CB: {cb_acc:.2%}")
    print(f"    Avg: {avg_acc:.2%}, Stacked: {stacked_acc:.2%}")
    print(f"    Meta weights: LGB={meta_model.coef_[0]:.3f}, XGB={meta_model.coef_[1]:.3f}, CB={meta_model.coef_[2]:.3f}")

    return results


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 60)
    print(f"Stacking Meta-Learner Training")
    print(f"Pair: {pair.upper()}, Split: {split_id}")
    print("=" * 60)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nLoading data for split {split_id}...")
    train_df, val_df = load_data(pair, split)
    print(f"  Train: {len(train_df):,} rows, Val: {len(val_df):,} rows")

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values

    all_results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n{'='*50}")
        print(f"Horizon h{horizon}")
        print(f"{'='*50}")

        y_train = train_df[target_col].values
        y_val = val_df[target_col].values

        results = train_stacking_for_horizon(X_train, y_train, X_val, y_val, horizon)
        if results:
            all_results[f"h{horizon}"] = results

    # Summary
    print("\n" + "=" * 60)
    print("STACKING RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Avg':<10} {'Stacked':<10}")
    print("-" * 58)

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            print(f"h{h:<7} {r['lightgbm']['accuracy']:.2%}{'':>3} "
                  f"{r['xgboost']['accuracy']:.2%}{'':>3} "
                  f"{r['catboost']['accuracy']:.2%}{'':>3} "
                  f"{r['avg_ensemble']['accuracy']:.2%}{'':>3} "
                  f"{r['stacked']['accuracy']:.2%}")

            if r['stacked']['accuracy'] > best_acc:
                best_acc = r['stacked']['accuracy']
                best_horizon = key

    print(f"\nBest stacked: {best_horizon} with {best_acc:.2%} accuracy")

    output = {
        "pair": pair, "split_id": split_id,
        "results": all_results, "best_horizon": best_horizon,
        "best_accuracy": best_acc, "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/stacking_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
