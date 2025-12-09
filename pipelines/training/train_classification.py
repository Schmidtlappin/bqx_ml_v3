#!/usr/bin/env python3
"""
Classification Training for BQX ML V3

Instead of regression (predicting exact values), directly predict
the direction (sign) of BQX movement using classification models.

This optimizes directly for directional accuracy.
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Related pairs for covariance features
RELATED_PAIRS = ['gbpusd', 'usdjpy', 'usdchf', 'eurgbp', 'eurjpy']


def load_data(pair: str, split: dict) -> tuple:
    """Load training and validation data with expanded features."""
    client = bigquery.Client(project=PROJECT)

    def build_query(date_start, date_end):
        # Build covariance feature JOINs
        cov_ctes = []
        cov_selects = []
        cov_joins = []

        for i, related in enumerate(RELATED_PAIRS):
            if pair < related:
                table_name = f"cov_agg_bqx_{pair}_{related}"
            else:
                table_name = f"cov_agg_bqx_{related}_{pair}"

            alias = f"cov{i}"
            cov_ctes.append(f"""
    {alias} AS (
        SELECT interval_time,
               spread as {alias}_spread,
               ratio as {alias}_ratio,
               spread_zscore as {alias}_zscore,
               sign_agreement as {alias}_sign_agree,
               mean_reversion_signal as {alias}_mr_signal
        FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    )""")
            cov_selects.extend([
                f"{alias}.{alias}_spread", f"{alias}.{alias}_ratio",
                f"{alias}.{alias}_zscore", f"{alias}.{alias}_sign_agree",
                f"{alias}.{alias}_mr_signal"
            ])
            cov_joins.append(f"LEFT JOIN {alias} ON base.interval_time = {alias}.interval_time")

        cov_ctes_sql = ",\n".join(cov_ctes)
        cov_selects_sql = ",\n        ".join(cov_selects)
        cov_joins_sql = "\n    ".join(cov_joins)

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
    ),
    {cov_ctes_sql}

    SELECT
        base.interval_time,
        base.bqx_45, base.bqx_90, base.bqx_180, base.bqx_360, base.bqx_720, base.bqx_1440, base.bqx_2880,
        lag45.lag45_bqx_close, lag45.lag45_bqx_lag, lag45.lag45_return, lag45.lag45_sma, lag45.lag45_ema,
        lag45.lag45_volatility, lag45.lag45_hl_range, lag45.lag45_momentum, lag45.lag45_positive_ratio,
        lag90.lag90_bqx_close, lag90.lag90_bqx_lag, lag90.lag90_return, lag90.lag90_sma, lag90.lag90_ema,
        lag90.lag90_volatility, lag90.lag90_hl_range, lag90.lag90_momentum, lag90.lag90_positive_ratio,
        regime45.reg45_volatility, regime45.reg45_hl_range, regime45.reg45_return, regime45.reg45_momentum,
        regime45.reg45_vol_regime, regime45.reg45_range_regime, regime45.reg45_return_regime, regime45.reg45_momentum_regime,
        agg.agg_mean_45, agg.agg_std_45, agg.agg_min_45, agg.agg_max_45, agg.agg_range_45, agg.agg_cv_45,
        agg.agg_mean_90, agg.agg_std_90, agg.agg_min_90, agg.agg_max_90, agg.agg_range_90, agg.agg_cv_90,
        agg.agg_mean_180, agg.agg_std_180, agg.agg_min_180, agg.agg_max_180, agg.agg_range_180, agg.agg_cv_180,
        agg.agg_mean_360, agg.agg_std_360, agg.agg_min_360, agg.agg_max_360, agg.agg_range_360, agg.agg_cv_360,
        {cov_selects_sql},
        targets.target_bqx45_h15, targets.target_bqx45_h30, targets.target_bqx45_h45,
        targets.target_bqx45_h60, targets.target_bqx45_h75, targets.target_bqx45_h90, targets.target_bqx45_h105
    FROM base
    JOIN lag45 ON base.interval_time = lag45.interval_time
    JOIN lag90 ON base.interval_time = lag90.interval_time
    JOIN regime45 ON base.interval_time = regime45.interval_time
    JOIN agg ON base.interval_time = agg.interval_time
    JOIN targets ON base.interval_time = targets.interval_time
    {cov_joins_sql}
    WHERE targets.target_bqx45_h15 IS NOT NULL
    """

    print(f"  Loading training data...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train: {len(train_df):,} rows")

    print(f"  Loading validation data...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def prepare_classification_data(X, y):
    """Convert regression targets to binary classification (direction)."""
    X = pd.DataFrame(X).apply(pd.to_numeric, errors='coerce').values
    y = pd.to_numeric(pd.Series(y), errors='coerce').values

    # Remove NaN rows
    mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X_clean = X[mask]
    y_clean = y[mask]

    # Convert to binary: 1 if positive, 0 if negative/zero
    y_binary = (y_clean > 0).astype(int)

    return X_clean, y_binary


def train_classification_ensemble(X_train, y_train, X_val, y_val, horizon):
    """Train classification ensemble for a single horizon."""
    X_tr, y_tr = prepare_classification_data(X_train, y_train)
    X_vl, y_vl = prepare_classification_data(X_val, y_val)

    if len(X_tr) < 1000:
        return None

    print(f"    Train: {len(X_tr):,} rows, Val: {len(X_vl):,} rows")
    print(f"    Class balance - Train: {y_tr.mean():.2%} positive, Val: {y_vl.mean():.2%} positive")

    results = {}

    # LightGBM Classifier
    print(f"    Training LightGBM classifier...")
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.7,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 100, 'is_unbalance': True
    }
    lgb_train = lgb.Dataset(X_tr, label=y_tr)
    lgb_val = lgb.Dataset(X_vl, label=y_vl, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=1000,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(100, verbose=False)])
    lgb_pred = (lgb_model.predict(X_vl) > 0.5).astype(int)
    lgb_acc = accuracy_score(y_vl, lgb_pred)
    results['lightgbm'] = {'accuracy': float(lgb_acc)}
    print(f"      LGB: {lgb_acc:.2%}")

    # XGBoost Classifier
    print(f"    Training XGBoost classifier...")
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 6, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.7, 'seed': 42, 'verbosity': 0,
        'scale_pos_weight': (1 - y_tr.mean()) / y_tr.mean()
    }
    dtrain = xgb.DMatrix(X_tr, label=y_tr)
    dval = xgb.DMatrix(X_vl, label=y_vl)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=1000,
                          evals=[(dval, 'val')], early_stopping_rounds=100, verbose_eval=False)
    xgb_pred = (xgb_model.predict(dval) > 0.5).astype(int)
    xgb_acc = accuracy_score(y_vl, xgb_pred)
    results['xgboost'] = {'accuracy': float(xgb_acc)}
    print(f"      XGB: {xgb_acc:.2%}")

    # CatBoost Classifier
    print(f"    Training CatBoost classifier...")
    cb_model = CatBoostClassifier(
        iterations=1000, learning_rate=0.03, depth=6,
        loss_function='Logloss', verbose=False, random_seed=42,
        auto_class_weights='Balanced', early_stopping_rounds=100
    )
    cb_model.fit(X_tr, y_tr, eval_set=(X_vl, y_vl), verbose=False)
    cb_pred = cb_model.predict(X_vl).flatten()
    cb_acc = accuracy_score(y_vl, cb_pred)
    results['catboost'] = {'accuracy': float(cb_acc)}
    print(f"      CB:  {cb_acc:.2%}")

    # Simple average ensemble (voting)
    lgb_prob = lgb_model.predict(X_vl)
    xgb_prob = xgb_model.predict(dval)
    cb_prob = cb_model.predict_proba(X_vl)[:, 1]
    avg_prob = (lgb_prob + xgb_prob + cb_prob) / 3
    avg_pred = (avg_prob > 0.5).astype(int)
    avg_acc = accuracy_score(y_vl, avg_pred)
    results['avg_ensemble'] = {'accuracy': float(avg_acc)}
    print(f"      Avg: {avg_acc:.2%}")

    # Stacking with Logistic Regression
    print(f"    Training stacked meta-learner...")
    meta_features_train = np.column_stack([
        lgb_model.predict(X_tr),
        xgb_model.predict(xgb.DMatrix(X_tr)),
        cb_model.predict_proba(X_tr)[:, 1]
    ])
    meta_features_val = np.column_stack([lgb_prob, xgb_prob, cb_prob])

    meta_model = LogisticRegression(C=1.0, max_iter=1000)
    meta_model.fit(meta_features_train, y_tr)
    stacked_pred = meta_model.predict(meta_features_val)
    stacked_acc = accuracy_score(y_vl, stacked_pred)
    results['stacked'] = {'accuracy': float(stacked_acc)}
    print(f"      Stacked: {stacked_acc:.2%}")

    # Best result
    best_method = max(results.keys(), key=lambda k: results[k]['accuracy'])
    results['best_method'] = best_method
    results['best_accuracy'] = results[best_method]['accuracy']

    return results


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 60)
    print(f"CLASSIFICATION Training for {pair.upper()}")
    print("Directly predicting direction (sign) instead of regression")
    print("=" * 60)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    train_df, val_df = load_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nFeatures: {len(feature_cols)}")

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

        results = train_classification_ensemble(X_train, y_train, X_val, y_val, horizon)
        if results:
            all_results[f"h{horizon}"] = results

    # Summary
    print("\n" + "=" * 60)
    print("CLASSIFICATION RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Avg':<10} {'Stacked':<10} {'Best':<10}")
    print("-" * 68)

    # Compare with regression results
    regression_results = {'h15': 0.7509, 'h30': 0.6292, 'h45': 0.5008, 'h60': 0.4788,
                          'h75': 0.5219, 'h90': 0.5089, 'h105': 0.5098}

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            reg_acc = regression_results.get(key, 0.5)
            best_class = r['best_accuracy']
            diff = best_class - reg_acc

            print(f"h{h:<7} {r['lightgbm']['accuracy']:.2%}{'':>3} "
                  f"{r['xgboost']['accuracy']:.2%}{'':>3} "
                  f"{r['catboost']['accuracy']:.2%}{'':>3} "
                  f"{r['avg_ensemble']['accuracy']:.2%}{'':>3} "
                  f"{r['stacked']['accuracy']:.2%}{'':>3} "
                  f"{best_class:.2%} ({'+' if diff > 0 else ''}{diff:.2%})")

            if best_class > best_acc:
                best_acc = best_class
                best_horizon = key

    print(f"\nBest: {best_horizon} with {best_acc:.2%} accuracy")

    output = {
        "pair": pair, "split_id": split_id, "approach": "classification",
        "feature_count": len(feature_cols), "results": all_results,
        "best_horizon": best_horizon, "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/classification_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
