#!/usr/bin/env python3
"""
Train all 28 pairs with full polynomial features.

Uses 10% sampling for fast iteration.
User mandate: ALL polynomial features (quad, lin, const, residual, variance)
Feature Priority: #1 IDX poly, #2 IDX derived, #3 BQX poly, #4 BQX derived
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

PAIRS = [
    'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
    'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'eurcad', 'eurnzd',
    'gbpjpy', 'gbpchf', 'gbpaud', 'gbpcad', 'gbpnzd',
    'audjpy', 'audchf', 'audcad', 'audnzd',
    'nzdjpy', 'nzdchf', 'nzdcad',
    'cadjpy', 'cadchf', 'chfjpy'
]


def load_data_sampled(pair: str, split: dict, sample_pct: float = 10.0, client=None) -> tuple:
    """Load from pre-joined full polynomial table with sampling."""
    if client is None:
        client = bigquery.Client(project=PROJECT)

    def build_query(date_start, date_end, sample=True):
        sample_clause = f"TABLESAMPLE SYSTEM ({sample_pct} PERCENT)" if sample else ""
        return f"""
        SELECT *
        FROM `{PROJECT}.bqx_ml_v3_analytics_v2.training_{pair}_full_poly` {sample_clause}
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        """

    train_df = client.query(build_query(split['train']['start'], split['train']['end'], sample=True)).to_dataframe()
    val_df = client.query(build_query(split['validation']['start'], split['validation']['end'], sample=True)).to_dataframe()

    return train_df, val_df


def prepare_data(X, y):
    """Convert to numeric and handle NaN."""
    X = pd.DataFrame(X).apply(pd.to_numeric, errors='coerce').values
    y = pd.to_numeric(pd.Series(y), errors='coerce').values

    mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X_clean = X[mask]
    y_clean = y[mask]

    y_binary = (y_clean > 0).astype(int)

    return X_clean, y_binary


def train_ensemble(X_train, y_train, X_val, y_val, feature_names):
    """Train classification ensemble."""
    X_tr, y_tr = prepare_data(X_train, y_train)
    X_vl, y_vl = prepare_data(X_val, y_val)

    if len(X_tr) < 500:
        return None

    results = {}

    # LightGBM
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 50, 'lambda_l1': 0.1, 'lambda_l2': 0.1
    }
    lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=feature_names)
    lgb_val = lgb.Dataset(X_vl, label=y_vl, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=500,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(50, verbose=False)])
    lgb_prob = lgb_model.predict(X_vl)
    lgb_pred = (lgb_prob > 0.5).astype(int)
    lgb_acc = accuracy_score(y_vl, lgb_pred)
    results['lightgbm'] = float(lgb_acc)

    # XGBoost
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 6, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.6, 'seed': 42, 'verbosity': 0
    }
    dtrain = xgb.DMatrix(X_tr, label=y_tr, feature_names=feature_names)
    dval = xgb.DMatrix(X_vl, label=y_vl, feature_names=feature_names)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=500,
                          evals=[(dval, 'val')], early_stopping_rounds=50, verbose_eval=False)
    xgb_prob = xgb_model.predict(dval)
    xgb_pred = (xgb_prob > 0.5).astype(int)
    xgb_acc = accuracy_score(y_vl, xgb_pred)
    results['xgboost'] = float(xgb_acc)

    # CatBoost
    cb_model = CatBoostClassifier(
        iterations=500, learning_rate=0.03, depth=6,
        loss_function='Logloss', verbose=False, random_seed=42,
        early_stopping_rounds=50
    )
    cb_model.fit(X_tr, y_tr, eval_set=(X_vl, y_vl), verbose=False)
    cb_pred = cb_model.predict(X_vl).flatten()
    cb_acc = accuracy_score(y_vl, cb_pred)
    results['catboost'] = float(cb_acc)

    results['best'] = max(lgb_acc, xgb_acc, cb_acc)

    # Get top features
    importance = lgb_model.feature_importance()
    top_indices = np.argsort(importance)[-10:][::-1]
    results['top_features'] = [feature_names[i] for i in top_indices]

    return results


def train_pair(pair: str, split_id: int = 0, sample_pct: float = 10.0):
    """Train a single pair."""
    try:
        with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
            splits_config = json.load(f)
    except FileNotFoundError:
        return None

    split = splits_config['splits'][split_id]

    try:
        train_df, val_df = load_data_sampled(pair, split, sample_pct)
    except Exception as e:
        print(f"  {pair}: FAILED to load data - {e}")
        return None

    if len(train_df) < 1000:
        print(f"  {pair}: Insufficient data ({len(train_df)} rows)")
        return None

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values

    pair_results = {
        'pair': pair,
        'train_rows': len(train_df),
        'val_rows': len(val_df),
        'feature_count': len(feature_cols),
        'horizons': {}
    }

    best_h15 = 0

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"

        if target_col not in train_df.columns:
            continue

        y_train = train_df[target_col].values
        y_val = val_df[target_col].values

        results = train_ensemble(X_train, y_train, X_val, y_val, feature_cols)
        if results:
            pair_results['horizons'][f"h{horizon}"] = results
            if horizon == 15:
                best_h15 = results['best']

    pair_results['best_h15'] = best_h15

    return pair_results


def main():
    sample_pct = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    specific_pair = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 70)
    print(f"FULL POLYNOMIAL FEATURE Training - All Pairs ({sample_pct}% sample)")
    print("User Priority: IDX poly > IDX > BQX poly > BQX > Other")
    print("=" * 70)

    all_results = {}
    pairs_to_train = [specific_pair] if specific_pair else PAIRS

    for i, pair in enumerate(pairs_to_train):
        print(f"\n[{i+1}/{len(pairs_to_train)}] Training {pair.upper()}...")

        result = train_pair(pair, split_id=0, sample_pct=sample_pct)
        if result:
            all_results[pair] = result
            h15_acc = result.get('best_h15', 0)
            print(f"  {pair}: h15={h15_acc:.2%}, features={result['feature_count']}, "
                  f"train={result['train_rows']:,}, val={result['val_rows']:,}")
        else:
            print(f"  {pair}: SKIPPED")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - All Pairs Full Polynomial Training")
    print("=" * 70)
    print(f"{'Pair':<10} {'h15':<10} {'h30':<10} {'h45':<10} {'Features'}")
    print("-" * 50)

    sorted_pairs = sorted(all_results.items(), key=lambda x: x[1].get('best_h15', 0), reverse=True)

    for pair, result in sorted_pairs:
        h15 = result['horizons'].get('h15', {}).get('best', 0)
        h30 = result['horizons'].get('h30', {}).get('best', 0)
        h45 = result['horizons'].get('h45', {}).get('best', 0)
        print(f"{pair:<10} {h15:.2%}{'':>3} {h30:.2%}{'':>3} {h45:.2%}{'':>3} {result['feature_count']}")

    # Best performers
    if sorted_pairs:
        best_pair, best_result = sorted_pairs[0]
        print(f"\nBest pair: {best_pair.upper()} with h15={best_result['best_h15']:.2%}")

        avg_h15 = np.mean([r['best_h15'] for r in all_results.values() if r.get('best_h15', 0) > 0])
        print(f"Average h15 accuracy: {avg_h15:.2%}")

    output = {
        "approach": "full_polynomial_all_pairs",
        "sample_pct": sample_pct,
        "pairs_trained": len(all_results),
        "results": all_results,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/all_pairs_full_poly_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
