#!/usr/bin/env python3
"""
Expanded Feature Training for BQX ML V3

Adds covariance features from related pairs to improve accuracy.
Target: Move from 75% to 85%+ with cross-pair relationships.
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Key related pairs for EURUSD covariance features
RELATED_PAIRS = ['gbpusd', 'usdjpy', 'usdchf', 'eurgbp', 'eurjpy']


def load_expanded_data(pair: str, split: dict) -> tuple:
    """Load expanded feature set including covariance features."""
    client = bigquery.Client(project=PROJECT)

    def build_query(date_start, date_end):
        # Build covariance feature JOINs for related pairs
        cov_ctes = []
        cov_selects = []
        cov_joins = []

        for i, related in enumerate(RELATED_PAIRS):
            # Determine table name (eurusd is always first in pair ordering)
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
               spread_ma_45 as {alias}_spread_ma45,
               spread_ma_180 as {alias}_spread_ma180,
               spread_std_45 as {alias}_spread_std45,
               spread_zscore as {alias}_zscore,
               sign_agreement as {alias}_sign_agree,
               rolling_agreement_45 as {alias}_roll_agree,
               mean_reversion_signal as {alias}_mr_signal
        FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    )""")
            cov_selects.extend([
                f"{alias}.{alias}_spread", f"{alias}.{alias}_ratio",
                f"{alias}.{alias}_spread_ma45", f"{alias}.{alias}_spread_ma180",
                f"{alias}.{alias}_spread_std45", f"{alias}.{alias}_zscore",
                f"{alias}.{alias}_sign_agree", f"{alias}.{alias}_roll_agree",
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
        -- Base BQX
        base.bqx_45, base.bqx_90, base.bqx_180, base.bqx_360, base.bqx_720, base.bqx_1440, base.bqx_2880,
        -- Lag features
        lag45.lag45_bqx_close, lag45.lag45_bqx_lag, lag45.lag45_return, lag45.lag45_sma, lag45.lag45_ema,
        lag45.lag45_volatility, lag45.lag45_hl_range, lag45.lag45_momentum, lag45.lag45_positive_ratio,
        lag90.lag90_bqx_close, lag90.lag90_bqx_lag, lag90.lag90_return, lag90.lag90_sma, lag90.lag90_ema,
        lag90.lag90_volatility, lag90.lag90_hl_range, lag90.lag90_momentum, lag90.lag90_positive_ratio,
        -- Regime features
        regime45.reg45_volatility, regime45.reg45_hl_range, regime45.reg45_return, regime45.reg45_momentum,
        regime45.reg45_vol_regime, regime45.reg45_range_regime, regime45.reg45_return_regime, regime45.reg45_momentum_regime,
        -- Aggregation features
        agg.agg_mean_45, agg.agg_std_45, agg.agg_min_45, agg.agg_max_45, agg.agg_range_45, agg.agg_cv_45,
        agg.agg_mean_90, agg.agg_std_90, agg.agg_min_90, agg.agg_max_90, agg.agg_range_90, agg.agg_cv_90,
        agg.agg_mean_180, agg.agg_std_180, agg.agg_min_180, agg.agg_max_180, agg.agg_range_180, agg.agg_cv_180,
        agg.agg_mean_360, agg.agg_std_360, agg.agg_min_360, agg.agg_max_360, agg.agg_range_360, agg.agg_cv_360,
        -- Covariance features (cross-pair relationships)
        {cov_selects_sql},
        -- Targets
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

    print(f"  Loading expanded training data...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train: {len(train_df):,} rows, {len(train_df.columns)} columns")

    print(f"  Loading validation data...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def calculate_directional_accuracy(y_true, y_pred):
    """Calculate directional accuracy."""
    return np.mean(np.sign(y_true) == np.sign(y_pred))


def train_lightgbm(X_train, y_train, X_val, y_val):
    """Train LightGBM with expanded features."""
    # Convert to float, handling NA values
    X_train = pd.DataFrame(X_train).apply(pd.to_numeric, errors='coerce').values
    X_val = pd.DataFrame(X_val).apply(pd.to_numeric, errors='coerce').values
    y_train = pd.to_numeric(pd.Series(y_train), errors='coerce').values
    y_val = pd.to_numeric(pd.Series(y_val), errors='coerce').values

    train_mask = ~(np.isnan(X_train).any(axis=1) | np.isnan(y_train))
    val_mask = ~(np.isnan(X_val).any(axis=1) | np.isnan(y_val))

    X_tr = X_train[train_mask]
    y_tr = y_train[train_mask]
    X_vl = X_val[val_mask]
    y_vl = y_val[val_mask]

    if len(X_tr) < 1000:
        return None, None, None

    params = {
        'objective': 'regression', 'metric': 'rmse', 'boosting_type': 'gbdt',
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.7,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 100, 'lambda_l1': 0.1, 'lambda_l2': 0.1
    }

    train_data = lgb.Dataset(X_tr, label=y_tr)
    val_data = lgb.Dataset(X_vl, label=y_vl, reference=train_data)

    model = lgb.train(params, train_data, num_boost_round=1000, valid_sets=[val_data],
                      callbacks=[lgb.early_stopping(100, verbose=False)])

    y_pred = model.predict(X_vl)
    acc = calculate_directional_accuracy(y_vl, y_pred)
    rmse = np.sqrt(mean_squared_error(y_vl, y_pred))

    return model, acc, rmse


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 60)
    print(f"Expanded Feature Training for {pair.upper()}")
    print(f"Adding covariance features from: {', '.join(RELATED_PAIRS)}")
    print("=" * 60)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    train_df, val_df = load_expanded_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nTotal features: {len(feature_cols)} (was 57, now with covariance)")

    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values

    results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n--- Horizon h{horizon} ---")

        y_train = train_df[target_col].values
        y_val = val_df[target_col].values

        model, acc, rmse = train_lightgbm(X_train, y_train, X_val, y_val)

        if model is None:
            print("  FAILED: Insufficient data")
            continue

        print(f"  Accuracy: {acc:.2%}, RMSE: {rmse:.6f}")
        results[f"h{horizon}"] = {"accuracy": float(acc), "rmse": float(rmse)}

        if acc >= 0.95:
            print(f"  *** ACHIEVED 95%+! ***")

    # Summary
    print("\n" + "=" * 60)
    print("EXPANDED FEATURE RESULTS")
    print("=" * 60)
    print(f"{'Horizon':<10} {'Accuracy':<12} {'RMSE':<12} {'vs Basic'}")
    print("-" * 50)

    # Compare with basic (hardcoded from previous results)
    basic_results = {'h15': 0.7507, 'h30': 0.6296, 'h45': 0.5001, 'h60': 0.4852,
                     'h75': 0.5026, 'h90': 0.5038, 'h105': 0.4995}

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in results:
            acc = results[key]['accuracy']
            basic = basic_results.get(key, 0.5)
            diff = acc - basic
            symbol = "+" if diff > 0 else ""
            print(f"h{h:<9} {acc:.2%}{'':>5} {results[key]['rmse']:.6f}{'':>3} {symbol}{diff:.2%}")

            if acc > best_acc:
                best_acc = acc
                best_horizon = key

    print(f"\nBest: {best_horizon} with {best_acc:.2%}")

    output = {
        "pair": pair, "split_id": split_id, "feature_count": len(feature_cols),
        "results": results, "best_horizon": best_horizon, "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/expanded_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
