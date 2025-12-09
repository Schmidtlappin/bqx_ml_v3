#!/usr/bin/env python3
"""
Simplified Polynomial Feature Training - Key Features Only

Uses the most predictive polynomial features:
- residual: y - (quad + lin + const)
- r2: fit quality
- zscore: standardized measure
- forecast_5: 5-step prediction
- acceleration: second derivative
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
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]


def load_poly_data(pair: str, split: dict) -> tuple:
    """Load data with KEY polynomial features only."""
    client = bigquery.Client(project=PROJECT)

    # Only key polynomial features (5 per window × 7 windows × 2 types = 70 features)
    poly_features = []

    for w in WINDOWS:
        # BQX key features
        poly_features.extend([
            f"bqx.reg_residual_{w} as bqx_resid_{w}",
            f"bqx.reg_r2_{w} as bqx_r2_{w}",
            f"bqx.reg_zscore_{w} as bqx_zscore_{w}",
            f"bqx.reg_forecast_5_{w} as bqx_fcst_{w}",
            f"bqx.reg_acceleration_{w} as bqx_accel_{w}",
        ])
        # IDX key features
        poly_features.extend([
            f"idx.reg_residual_{w} as idx_resid_{w}",
            f"idx.reg_r2_{w} as idx_r2_{w}",
            f"idx.reg_zscore_{w} as idx_zscore_{w}",
            f"idx.reg_forecast_5_{w} as idx_fcst_{w}",
            f"idx.reg_acceleration_{w} as idx_accel_{w}",
        ])

    poly_select = ",\n        ".join(poly_features)

    def build_query(date_start, date_end):
        return f"""
    SELECT
        base.interval_time,
        -- Base BQX (7 features)
        base.bqx_45, base.bqx_90, base.bqx_180, base.bqx_360, base.bqx_720, base.bqx_1440, base.bqx_2880,
        -- Lag features (18)
        lag45.bqx_close as lag45_close, lag45.bqx_lag_45 as lag45_lag, lag45.return_lag_45 as lag45_ret,
        lag45.sma_45 as lag45_sma, lag45.ema_45 as lag45_ema, lag45.volatility_45 as lag45_vol,
        lag45.hl_range_45 as lag45_hlr, lag45.momentum_45 as lag45_mom, lag45.positive_ratio_45 as lag45_pr,
        lag90.bqx_close as lag90_close, lag90.bqx_lag_90 as lag90_lag, lag90.return_lag_90 as lag90_ret,
        lag90.sma_90 as lag90_sma, lag90.ema_90 as lag90_ema, lag90.volatility_90 as lag90_vol,
        lag90.hl_range_90 as lag90_hlr, lag90.momentum_90 as lag90_mom, lag90.positive_ratio_90 as lag90_pr,
        -- Regime features (8)
        reg.volatility_45 as reg_vol, reg.hl_range_45 as reg_hlr, reg.return_lag_45 as reg_ret, reg.momentum_45 as reg_mom,
        reg.volatility_regime_code as reg_vol_code, reg.range_regime_code as reg_range_code,
        reg.return_regime_code as reg_ret_code, reg.momentum_regime_code as reg_mom_code,
        -- Agg features (24)
        agg.agg_mean_45, agg.agg_std_45, agg.agg_min_45, agg.agg_max_45, agg.agg_range_45, agg.agg_cv_45,
        agg.agg_mean_90, agg.agg_std_90, agg.agg_min_90, agg.agg_max_90, agg.agg_range_90, agg.agg_cv_90,
        agg.agg_mean_180, agg.agg_std_180, agg.agg_min_180, agg.agg_max_180, agg.agg_range_180, agg.agg_cv_180,
        agg.agg_mean_360, agg.agg_std_360, agg.agg_min_360, agg.agg_max_360, agg.agg_range_360, agg.agg_cv_360,
        -- KEY Polynomial features (70 = 5 × 7 windows × 2 types)
        {poly_select},
        -- Targets
        tgt.target_bqx45_h15, tgt.target_bqx45_h30, tgt.target_bqx45_h45,
        tgt.target_bqx45_h60, tgt.target_bqx45_h75, tgt.target_bqx45_h90, tgt.target_bqx45_h105
    FROM `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base
    JOIN `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_45` lag45 ON base.interval_time = lag45.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.lag_bqx_{pair}_90` lag90 ON base.interval_time = lag90.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.regime_bqx_{pair}_45` reg ON base.interval_time = reg.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}` agg ON base.interval_time = agg.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` bqx ON base.interval_time = bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` idx ON base.interval_time = idx.interval_time
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` tgt ON base.interval_time = tgt.interval_time
    WHERE DATE(base.interval_time) BETWEEN '{date_start}' AND '{date_end}'
    AND tgt.target_bqx45_h15 IS NOT NULL
    """

    print(f"  Loading training data with KEY polynomial features...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train: {len(train_df):,} rows, {len(train_df.columns)} columns")

    print(f"  Loading validation data...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def prepare_data(X, y):
    """Convert to numeric and handle NaN."""
    X = pd.DataFrame(X).apply(pd.to_numeric, errors='coerce').values
    y = pd.to_numeric(pd.Series(y), errors='coerce').values

    mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X_clean = X[mask]
    y_clean = y[mask]

    # Binary classification target
    y_binary = (y_clean > 0).astype(int)

    return X_clean, y_binary


def train_ensemble(X_train, y_train, X_val, y_val, horizon):
    """Train classification ensemble."""
    X_tr, y_tr = prepare_data(X_train, y_train)
    X_vl, y_vl = prepare_data(X_val, y_val)

    if len(X_tr) < 1000:
        return None

    print(f"    Train: {len(X_tr):,} rows, Val: {len(X_vl):,} rows")
    print(f"    Class balance: {y_tr.mean():.2%} positive")

    results = {}

    # LightGBM
    print(f"    Training LightGBM...")
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 255, 'learning_rate': 0.02, 'feature_fraction': 0.5,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 100, 'lambda_l1': 0.1, 'lambda_l2': 0.1
    }
    lgb_train = lgb.Dataset(X_tr, label=y_tr)
    lgb_val = lgb.Dataset(X_vl, label=y_vl, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=2000,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(150, verbose=False)])
    lgb_prob = lgb_model.predict(X_vl)
    lgb_pred = (lgb_prob > 0.5).astype(int)
    lgb_acc = accuracy_score(y_vl, lgb_pred)
    results['lightgbm'] = {'accuracy': float(lgb_acc)}
    print(f"      LGB: {lgb_acc:.2%}")

    # XGBoost
    print(f"    Training XGBoost...")
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 8, 'learning_rate': 0.02,
        'subsample': 0.8, 'colsample_bytree': 0.5, 'seed': 42, 'verbosity': 0,
        'reg_alpha': 0.1, 'reg_lambda': 0.1
    }
    dtrain = xgb.DMatrix(X_tr, label=y_tr)
    dval = xgb.DMatrix(X_vl, label=y_vl)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=2000,
                          evals=[(dval, 'val')], early_stopping_rounds=150, verbose_eval=False)
    xgb_prob = xgb_model.predict(dval)
    xgb_pred = (xgb_prob > 0.5).astype(int)
    xgb_acc = accuracy_score(y_vl, xgb_pred)
    results['xgboost'] = {'accuracy': float(xgb_acc)}
    print(f"      XGB: {xgb_acc:.2%}")

    # CatBoost
    print(f"    Training CatBoost...")
    cb_model = CatBoostClassifier(
        iterations=2000, learning_rate=0.02, depth=8,
        loss_function='Logloss', verbose=False, random_seed=42,
        l2_leaf_reg=3, early_stopping_rounds=150
    )
    cb_model.fit(X_tr, y_tr, eval_set=(X_vl, y_vl), verbose=False)
    cb_prob = cb_model.predict_proba(X_vl)[:, 1]
    cb_pred = cb_model.predict(X_vl).flatten()
    cb_acc = accuracy_score(y_vl, cb_pred)
    results['catboost'] = {'accuracy': float(cb_acc)}
    print(f"      CB:  {cb_acc:.2%}")

    # Weighted ensemble
    weights = np.array([lgb_acc, xgb_acc, cb_acc])
    weights = weights / weights.sum()
    weighted_prob = weights[0] * lgb_prob + weights[1] * xgb_prob + weights[2] * cb_prob
    weighted_pred = (weighted_prob > 0.5).astype(int)
    weighted_acc = accuracy_score(y_vl, weighted_pred)
    results['weighted_ensemble'] = {'accuracy': float(weighted_acc), 'weights': weights.tolist()}
    print(f"      Weighted: {weighted_acc:.2%}")

    best_acc = max(lgb_acc, xgb_acc, cb_acc, weighted_acc)
    results['best_accuracy'] = best_acc

    return results


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 70)
    print(f"KEY POLYNOMIAL FEATURE Training for {pair.upper()}")
    print("Using: residual, r2, zscore, forecast_5, acceleration")
    print("=" * 70)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    train_df, val_df = load_poly_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nTotal features: {len(feature_cols)}")
    print(f"  - Base + Lag + Regime + Agg: 57")
    print(f"  - BQX Poly (5 key × 7 windows): 35")
    print(f"  - IDX Poly (5 key × 7 windows): 35")

    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values

    all_results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n{'='*60}")
        print(f"Horizon h{horizon}")
        print(f"{'='*60}")

        y_train = train_df[target_col].values
        y_val = val_df[target_col].values

        results = train_ensemble(X_train, y_train, X_val, y_val, horizon)
        if results:
            all_results[f"h{horizon}"] = results

    # Summary
    print("\n" + "=" * 70)
    print("KEY POLYNOMIAL FEATURE RESULTS (BQX + IDX)")
    print("=" * 70)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Weighted':<10} {'vs Basic'}")
    print("-" * 60)

    prev_best = {'h15': 0.7563, 'h30': 0.6358, 'h45': 0.5374, 'h60': 0.5325,
                 'h75': 0.5388, 'h90': 0.5259, 'h105': 0.50}

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            prev = prev_best.get(key, 0.5)
            best_this = r['best_accuracy']
            diff = best_this - prev

            print(f"h{h:<7} {r['lightgbm']['accuracy']:.2%}{'':>3} "
                  f"{r['xgboost']['accuracy']:.2%}{'':>3} "
                  f"{r['catboost']['accuracy']:.2%}{'':>3} "
                  f"{r['weighted_ensemble']['accuracy']:.2%}{'':>3} "
                  f"{'+' if diff > 0 else ''}{diff:.2%}")

            if best_this > best_acc:
                best_acc = best_this
                best_horizon = key

    print(f"\nBest: {best_horizon} with {best_acc:.2%} accuracy")

    if best_acc >= 0.80:
        print("*** BREAKTHROUGH: 80%+ accuracy achieved! ***")
    if best_acc >= 0.85:
        print("*** EXCELLENT: 85%+ accuracy achieved! ***")
    if best_acc >= 0.90:
        print("*** OUTSTANDING: 90%+ accuracy achieved! ***")
    if best_acc >= 0.95:
        print("*** TARGET MET: 95%+ accuracy achieved! ***")

    output = {
        "pair": pair, "split_id": split_id, "approach": "key_polynomial",
        "feature_count": len(feature_cols), "results": all_results,
        "best_horizon": best_horizon, "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/poly_key_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
