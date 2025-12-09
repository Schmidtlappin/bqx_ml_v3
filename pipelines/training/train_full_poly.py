#!/usr/bin/env python3
"""
Full Polynomial Feature Training for BQX ML V3

Uses ALL polynomial features per user mandate:
- quad_term, lin_term, const_term, residual (core polynomial)
- total_var, resid_var (variance features)
- r2, rmse, zscore, acceleration, forecast, etc.

Feature Priority (per user):
  #1 IDX polynomial (reg_idx)
  #2 IDX polynomial derived
  #3 IDX (base_idx)
  #4 IDX derived
  #5 BQX
  #6 BQX derived
  #7 All other
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
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def load_data(pair: str, split: dict) -> tuple:
    """Load from pre-joined full polynomial materialized table."""
    client = bigquery.Client(project=PROJECT)

    def build_query(date_start, date_end):
        return f"""
        SELECT *
        FROM `{PROJECT}.bqx_ml_v3_analytics_v2.training_{pair}_full_poly`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        """

    print(f"  Loading training data (full polynomial features)...")
    train_df = client.query(build_query(split['train']['start'], split['train']['end'])).to_dataframe()
    print(f"    Train: {len(train_df):,} rows, {len(train_df.columns)} columns")

    print(f"  Loading validation data...")
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'])).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def categorize_features(feature_cols):
    """Categorize features by user priority."""
    categories = {
        'idx_poly': [],      # #1: IDX polynomial (quad, lin, const, resid, var, r2, etc.)
        'idx_poly_derived': [],  # #2: IDX poly derived
        'idx_base': [],      # #3: IDX base (open, high, low, close, volume)
        'idx_derived': [],   # #4: IDX derived
        'bqx_base': [],      # #5: BQX base
        'bqx_derived': [],   # #6: BQX derived
        'other': []          # #7: Other
    }

    for col in feature_cols:
        if col.startswith('idx_'):
            # IDX polynomial features
            if any(x in col for x in ['quad', 'lin', 'const', 'resid', 'var', 'r2', 'rmse',
                                       'accel', 'trend', 'fcst', 'curv', 'ci', 'rnorm',
                                       'rkurt', 'rskew', 'mean', 'std', 'min', 'max',
                                       'first', 'slope', 'dir', 'dev', 'zscore', 'rpct']):
                categories['idx_poly'].append(col)
            else:
                categories['idx_base'].append(col)
        elif col.startswith('bqx_'):
            # BQX polynomial features
            if any(x in col for x in ['quad', 'lin', 'const', 'resid', 'var', 'r2', 'rmse',
                                       'accel', 'trend', 'fcst', 'curv', 'ci', 'rnorm',
                                       'rkurt', 'rskew', 'mean', 'std', 'min', 'max',
                                       'first', 'slope', 'dir', 'dev', 'zscore', 'rpct']):
                categories['bqx_derived'].append(col)
            else:
                categories['bqx_base'].append(col)
        else:
            categories['other'].append(col)

    return categories


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


def train_ensemble(X_train, y_train, X_val, y_val, horizon, feature_names):
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
    lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=feature_names)
    lgb_val = lgb.Dataset(X_vl, label=y_vl, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=2000,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(150, verbose=False)])
    lgb_prob = lgb_model.predict(X_vl)
    lgb_pred = (lgb_prob > 0.5).astype(int)
    lgb_acc = accuracy_score(y_vl, lgb_pred)
    results['lightgbm'] = {'accuracy': float(lgb_acc)}
    print(f"      LGB: {lgb_acc:.2%}")

    # Get top features from LightGBM
    importance = lgb_model.feature_importance()
    top_indices = np.argsort(importance)[-20:][::-1]
    top_features = [(feature_names[i], importance[i]) for i in top_indices]
    results['top_features'] = top_features

    # XGBoost
    print(f"    Training XGBoost...")
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 8, 'learning_rate': 0.02,
        'subsample': 0.8, 'colsample_bytree': 0.5, 'seed': 42, 'verbosity': 0,
        'reg_alpha': 0.1, 'reg_lambda': 0.1
    }
    dtrain = xgb.DMatrix(X_tr, label=y_tr, feature_names=feature_names)
    dval = xgb.DMatrix(X_vl, label=y_vl, feature_names=feature_names)
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
    print(f"FULL POLYNOMIAL FEATURE Training for {pair.upper()}")
    print("User Priority: IDX poly > IDX > BQX poly > BQX > Other")
    print("=" * 70)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    train_df, val_df = load_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    # Categorize features by priority
    categories = categorize_features(feature_cols)

    print(f"\nFeature Categories (by user priority):")
    print(f"  #1 IDX Polynomial: {len(categories['idx_poly'])} features")
    print(f"  #2 IDX Poly Derived: {len(categories['idx_poly_derived'])} features")
    print(f"  #3 IDX Base: {len(categories['idx_base'])} features")
    print(f"  #4 IDX Derived: {len(categories['idx_derived'])} features")
    print(f"  #5 BQX Base: {len(categories['bqx_base'])} features")
    print(f"  #6 BQX Derived: {len(categories['bqx_derived'])} features")
    print(f"  #7 Other: {len(categories['other'])} features")
    print(f"  TOTAL: {len(feature_cols)} features")

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

        results = train_ensemble(X_train, y_train, X_val, y_val, horizon, feature_cols)
        if results:
            all_results[f"h{horizon}"] = results

    # Summary
    print("\n" + "=" * 70)
    print("FULL POLYNOMIAL FEATURE RESULTS")
    print("=" * 70)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Weighted':<10} {'vs 77.51%'}")
    print("-" * 60)

    prev_best = {'h15': 0.7751, 'h30': 0.6632, 'h45': 0.5427, 'h60': 0.5327,
                 'h75': 0.5254, 'h90': 0.5225, 'h105': 0.5247}

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

    # Show top features for best horizon
    if best_horizon and 'top_features' in all_results[best_horizon]:
        print(f"\nTop 20 Features for {best_horizon}:")
        for i, (feat, imp) in enumerate(all_results[best_horizon]['top_features'][:20], 1):
            prefix = "IDX_POLY" if feat.startswith('idx_') and any(x in feat for x in ['quad', 'lin', 'const', 'resid']) else \
                     "IDX" if feat.startswith('idx_') else \
                     "BQX_POLY" if feat.startswith('bqx_') and any(x in feat for x in ['quad', 'lin', 'const', 'resid']) else \
                     "BQX" if feat.startswith('bqx_') else "OTHER"
            print(f"  {i:2}. [{prefix:8}] {feat}: {imp}")

    if best_acc >= 0.80:
        print("\n*** BREAKTHROUGH: 80%+ accuracy achieved! ***")
    if best_acc >= 0.85:
        print("*** EXCELLENT: 85%+ accuracy achieved! ***")
    if best_acc >= 0.90:
        print("*** OUTSTANDING: 90%+ accuracy achieved! ***")
    if best_acc >= 0.95:
        print("*** TARGET MET: 95%+ accuracy achieved! ***")

    output = {
        "pair": pair, "split_id": split_id, "approach": "full_polynomial",
        "feature_count": len(feature_cols),
        "feature_categories": {k: len(v) for k, v in categories.items()},
        "results": all_results,
        "best_horizon": best_horizon, "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/full_poly_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
