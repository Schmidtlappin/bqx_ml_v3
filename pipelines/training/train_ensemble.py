#!/usr/bin/env python3
"""
Ensemble Training for BQX ML V3

Trains LightGBM, XGBoost, and CatBoost models for all 7 horizons.
Generates out-of-fold predictions for meta-learner stacking.
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
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def load_training_data(pair: str, split: dict) -> tuple:
    """Load training and validation data for a split."""
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

    print(f"  Loading training data...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train: {len(train_df):,} rows")

    print(f"  Loading validation data...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def calculate_directional_accuracy(y_true, y_pred):
    """Calculate directional accuracy."""
    actual_dir = np.sign(y_true)
    pred_dir = np.sign(y_pred)
    return np.mean(actual_dir == pred_dir)


def train_lightgbm(X_train, y_train, X_val, y_val):
    """Train LightGBM model."""
    params = {
        'objective': 'regression', 'metric': 'rmse', 'boosting_type': 'gbdt',
        'num_leaves': 63, 'learning_rate': 0.05, 'feature_fraction': 0.8,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42
    }
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    model = lgb.train(params, train_data, num_boost_round=500, valid_sets=[val_data],
                      callbacks=[lgb.early_stopping(50, verbose=False)])
    return model


def train_xgboost(X_train, y_train, X_val, y_val):
    """Train XGBoost model."""
    params = {
        'objective': 'reg:squarederror', 'max_depth': 6, 'learning_rate': 0.05,
        'subsample': 0.8, 'colsample_bytree': 0.8, 'seed': 42, 'verbosity': 0
    }
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    model = xgb.train(params, dtrain, num_boost_round=500, evals=[(dval, 'val')],
                      early_stopping_rounds=50, verbose_eval=False)
    return model


def train_catboost(X_train, y_train, X_val, y_val):
    """Train CatBoost model."""
    model = CatBoostRegressor(
        iterations=500, learning_rate=0.05, depth=6, loss_function='RMSE',
        early_stopping_rounds=50, verbose=False, random_seed=42
    )
    model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
    return model


def train_ensemble_for_horizon(X_train, y_train, X_val, y_val, horizon):
    """Train all 3 models for a single horizon."""
    # Clean data
    train_mask = ~(X_train.isna().any(axis=1) | y_train.isna())
    val_mask = ~(X_val.isna().any(axis=1) | y_val.isna())

    X_tr = X_train[train_mask].values
    y_tr = y_train[train_mask].values
    X_vl = X_val[val_mask].values
    y_vl = y_val[val_mask].values

    if len(X_tr) < 1000 or len(X_vl) < 100:
        return None

    results = {}

    # LightGBM
    print(f"    Training LightGBM...", end=" ")
    lgb_model = train_lightgbm(X_tr, y_tr, X_vl, y_vl)
    lgb_pred = lgb_model.predict(X_vl)
    lgb_acc = calculate_directional_accuracy(y_vl, lgb_pred)
    lgb_rmse = np.sqrt(mean_squared_error(y_vl, lgb_pred))
    print(f"Acc: {lgb_acc:.2%}")
    results['lightgbm'] = {'accuracy': lgb_acc, 'rmse': lgb_rmse, 'predictions': lgb_pred}

    # XGBoost
    print(f"    Training XGBoost...", end=" ")
    xgb_model = train_xgboost(X_tr, y_tr, X_vl, y_vl)
    xgb_pred = xgb_model.predict(xgb.DMatrix(X_vl))
    xgb_acc = calculate_directional_accuracy(y_vl, xgb_pred)
    xgb_rmse = np.sqrt(mean_squared_error(y_vl, xgb_pred))
    print(f"Acc: {xgb_acc:.2%}")
    results['xgboost'] = {'accuracy': xgb_acc, 'rmse': xgb_rmse, 'predictions': xgb_pred}

    # CatBoost
    print(f"    Training CatBoost...", end=" ")
    cb_model = train_catboost(X_tr, y_tr, X_vl, y_vl)
    cb_pred = cb_model.predict(X_vl)
    cb_acc = calculate_directional_accuracy(y_vl, cb_pred)
    cb_rmse = np.sqrt(mean_squared_error(y_vl, cb_pred))
    print(f"Acc: {cb_acc:.2%}")
    results['catboost'] = {'accuracy': cb_acc, 'rmse': cb_rmse, 'predictions': cb_pred}

    # Simple average ensemble
    avg_pred = (lgb_pred + xgb_pred + cb_pred) / 3
    avg_acc = calculate_directional_accuracy(y_vl, avg_pred)
    avg_rmse = np.sqrt(mean_squared_error(y_vl, avg_pred))
    print(f"    Avg Ensemble: Acc: {avg_acc:.2%}")
    results['ensemble_avg'] = {'accuracy': avg_acc, 'rmse': avg_rmse}

    results['y_true'] = y_vl
    return results


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 60)
    print(f"Ensemble Training: LightGBM + XGBoost + CatBoost")
    print(f"Pair: {pair.upper()}, Split: {split_id}")
    print("=" * 60)

    # Load split config
    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    # Load data
    train_df, val_df = load_training_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nFeatures: {len(feature_cols)}, Targets: {len(target_cols)}")

    X_train = train_df[feature_cols]
    X_val = val_df[feature_cols]

    all_results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n{'='*40}")
        print(f"Horizon h{horizon}")
        print(f"{'='*40}")

        y_train = train_df[target_col]
        y_val = val_df[target_col]

        results = train_ensemble_for_horizon(X_train, y_train, X_val, y_val, horizon)
        if results:
            all_results[f"h{horizon}"] = {
                'lightgbm': {'accuracy': results['lightgbm']['accuracy'], 'rmse': results['lightgbm']['rmse']},
                'xgboost': {'accuracy': results['xgboost']['accuracy'], 'rmse': results['xgboost']['rmse']},
                'catboost': {'accuracy': results['catboost']['accuracy'], 'rmse': results['catboost']['rmse']},
                'ensemble_avg': results['ensemble_avg']
            }

    # Summary
    print("\n" + "=" * 60)
    print("ENSEMBLE RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Horizon':<8} {'LightGBM':<12} {'XGBoost':<12} {'CatBoost':<12} {'Ensemble':<12}")
    print("-" * 56)

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            lgb_acc = r['lightgbm']['accuracy']
            xgb_acc = r['xgboost']['accuracy']
            cb_acc = r['catboost']['accuracy']
            ens_acc = r['ensemble_avg']['accuracy']
            print(f"h{h:<7} {lgb_acc:.2%}{'':>5} {xgb_acc:.2%}{'':>5} {cb_acc:.2%}{'':>5} {ens_acc:.2%}")

            if ens_acc > best_acc:
                best_acc = ens_acc
                best_horizon = key

    print(f"\nBest ensemble: {best_horizon} with {best_acc:.2%} accuracy")

    # Save results
    output = {
        "pair": pair,
        "split_id": split_id,
        "results": all_results,
        "best_horizon": best_horizon,
        "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/ensemble_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=float)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
