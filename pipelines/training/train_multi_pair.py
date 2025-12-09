#!/usr/bin/env python3
"""
Multi-Pair Training Pipeline for BQX ML V3

Trains models for multiple currency pairs in sequence.
Per roadmap: Start with 5 major pairs, then scale to all 28.

Major pairs: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD
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
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# Major pairs to train first
MAJOR_PAIRS = ["eurusd", "gbpusd", "usdjpy", "audusd", "usdcad"]

# All 28 pairs
ALL_PAIRS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
    "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
    "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
    "audjpy", "audchf", "audcad", "audnzd",
    "nzdjpy", "nzdchf", "nzdcad",
    "cadjpy", "cadchf",
    "chfjpy"
]

HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def load_training_data(pair: str, split: dict, sample_limit: int = 80000) -> tuple:
    """Load training data for a pair."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        reg_idx.interval_time,
        -- IDX Polynomial Features
        reg_idx.reg_quad_term_45 as idx_quad_45, reg_idx.reg_lin_term_45 as idx_lin_45,
        reg_idx.reg_total_var_45 as idx_tvar_45, reg_idx.reg_slope_45 as idx_slope_45,
        reg_idx.reg_trend_45 as idx_trend_45, reg_idx.reg_dev_45 as idx_dev_45,
        reg_idx.reg_zscore_45 as idx_zscore_45,
        reg_idx.reg_quad_term_90 as idx_quad_90, reg_idx.reg_lin_term_90 as idx_lin_90,
        reg_idx.reg_total_var_90 as idx_tvar_90, reg_idx.reg_slope_90 as idx_slope_90,
        reg_idx.reg_quad_term_180 as idx_quad_180, reg_idx.reg_lin_term_180 as idx_lin_180,
        reg_idx.reg_total_var_180 as idx_tvar_180, reg_idx.reg_slope_180 as idx_slope_180,
        reg_idx.reg_quad_term_360 as idx_quad_360, reg_idx.reg_lin_term_360 as idx_lin_360,
        reg_idx.reg_total_var_360 as idx_tvar_360, reg_idx.reg_slope_360 as idx_slope_360,
        reg_idx.reg_quad_term_720 as idx_quad_720, reg_idx.reg_lin_term_720 as idx_lin_720,
        reg_idx.reg_total_var_720 as idx_tvar_720, reg_idx.reg_slope_720 as idx_slope_720,
        reg_idx.reg_quad_term_1440 as idx_quad_1440, reg_idx.reg_lin_term_1440 as idx_lin_1440,
        reg_idx.reg_total_var_1440 as idx_tvar_1440, reg_idx.reg_slope_1440 as idx_slope_1440,

        -- BQX Polynomial Features
        reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
        reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_slope_45 as bqx_slope_45,
        reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
        reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_slope_90 as bqx_slope_90,
        reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
        reg_bqx.reg_total_var_180 as bqx_tvar_180,
        reg_bqx.reg_quad_term_360 as bqx_quad_360, reg_bqx.reg_lin_term_360 as bqx_lin_360,
        reg_bqx.reg_total_var_360 as bqx_tvar_360,

        -- BQX Base features
        base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,
        base_bqx.bqx_720, base_bqx.bqx_1440, base_bqx.bqx_2880,

        -- Aggregation features
        agg_idx.agg_mean_45 as idx_mean_45, agg_idx.agg_std_45 as idx_std_45,
        agg_idx.agg_range_45 as idx_range_45,

        -- Targets
        targets.target_bqx45_h15, targets.target_bqx45_h30, targets.target_bqx45_h45,
        targets.target_bqx45_h60, targets.target_bqx45_h75, targets.target_bqx45_h90,
        targets.target_bqx45_h105

    FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` reg_idx
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` reg_bqx
        ON reg_idx.interval_time = reg_bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base_bqx
        ON reg_idx.interval_time = base_bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.agg_idx_{pair}` agg_idx
        ON reg_idx.interval_time = agg_idx.interval_time
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON reg_idx.interval_time = targets.interval_time
    WHERE DATE(reg_idx.interval_time) BETWEEN '{split['train']['start']}' AND '{split['train']['end']}'
    AND targets.target_bqx45_h15 IS NOT NULL
    LIMIT {sample_limit}
    """

    train_df = client.query(query).to_dataframe()

    # Load validation data
    val_query = query.replace(
        f"'{split['train']['start']}' AND '{split['train']['end']}'",
        f"'{split['validation']['start']}' AND '{split['validation']['end']}'"
    ).replace(f"LIMIT {sample_limit}", f"LIMIT {sample_limit // 2}")

    val_df = client.query(val_query).to_dataframe()

    return train_df, val_df


def prepare_data(X, y):
    """Convert to numeric and handle NaN."""
    X = pd.DataFrame(X).apply(pd.to_numeric, errors='coerce').values
    y = pd.to_numeric(pd.Series(y), errors='coerce').values
    mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    return X[mask], (y[mask] > 0).astype(int)


def train_ensemble(X_train, y_train, X_val, y_val, feature_names):
    """Train LGB + XGB + CB ensemble with meta-learner."""
    results = {}

    # LightGBM
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 50
    }
    lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
    lgb_val = lgb.Dataset(X_val, label=y_val, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=500,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(50, verbose=False)])
    lgb_prob_train = lgb_model.predict(X_train)
    lgb_prob_val = lgb_model.predict(X_val)
    lgb_acc = accuracy_score(y_val, (lgb_prob_val > 0.5).astype(int))
    results['lightgbm'] = {'accuracy': lgb_acc, 'prob_train': lgb_prob_train, 'prob_val': lgb_prob_val}

    # XGBoost
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 6, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.6, 'seed': 42, 'verbosity': 0
    }
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dval = xgb.DMatrix(X_val, label=y_val, feature_names=feature_names)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=500,
                          evals=[(dval, 'val')], early_stopping_rounds=50, verbose_eval=False)
    xgb_prob_train = xgb_model.predict(xgb.DMatrix(X_train, feature_names=feature_names))
    xgb_prob_val = xgb_model.predict(dval)
    xgb_acc = accuracy_score(y_val, (xgb_prob_val > 0.5).astype(int))
    results['xgboost'] = {'accuracy': xgb_acc, 'prob_train': xgb_prob_train, 'prob_val': xgb_prob_val}

    # CatBoost
    cb_model = CatBoostClassifier(
        iterations=500, learning_rate=0.03, depth=6,
        loss_function='Logloss', verbose=False, random_seed=42,
        early_stopping_rounds=50
    )
    cb_model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
    cb_prob_train = cb_model.predict_proba(X_train)[:, 1]
    cb_prob_val = cb_model.predict_proba(X_val)[:, 1]
    cb_acc = accuracy_score(y_val, cb_model.predict(X_val).flatten())
    results['catboost'] = {'accuracy': cb_acc, 'prob_train': cb_prob_train, 'prob_val': cb_prob_val}

    # Meta-Learner
    meta_X_train = np.column_stack([lgb_prob_train, xgb_prob_train, cb_prob_train])
    meta_X_val = np.column_stack([lgb_prob_val, xgb_prob_val, cb_prob_val])
    meta_model = LogisticRegression(random_state=42, max_iter=1000)
    meta_model.fit(meta_X_train, y_train)
    meta_acc = accuracy_score(y_val, meta_model.predict(meta_X_val))
    results['meta_learner'] = {'accuracy': meta_acc}

    results['best_accuracy'] = max(lgb_acc, xgb_acc, cb_acc, meta_acc)

    return results


def train_pair(pair: str, split_id: int = 0):
    """Train all horizons for a single pair."""
    print(f"\n{'='*70}")
    print(f"Training {pair.upper()}")
    print(f"{'='*70}")

    # Load split config
    try:
        with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
            splits_config = json.load(f)
    except FileNotFoundError:
        # Use EURUSD splits as template
        with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_eurusd.json") as f:
            splits_config = json.load(f)

    split = splits_config['splits'][split_id]
    print(f"Split {split_id}: {split['train']['start']} to {split['test']['end']}")

    # Load data
    try:
        train_df, val_df = load_training_data(pair, split)
        print(f"  Data: {len(train_df):,} train, {len(val_df):,} val")
    except Exception as e:
        print(f"  ERROR loading data: {e}")
        return None

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    all_results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        if target_col not in train_df.columns:
            continue

        X_train, y_train = prepare_data(train_df[feature_cols], train_df[target_col])
        X_val, y_val = prepare_data(val_df[feature_cols], val_df[target_col])

        if len(X_train) < 1000:
            print(f"  h{horizon}: Insufficient data")
            continue

        results = train_ensemble(X_train, y_train, X_val, y_val, feature_cols)

        print(f"  h{horizon}: LGB {results['lightgbm']['accuracy']:.2%}, "
              f"XGB {results['xgboost']['accuracy']:.2%}, "
              f"CB {results['catboost']['accuracy']:.2%}, "
              f"Meta {results['meta_learner']['accuracy']:.2%}, "
              f"Best {results['best_accuracy']:.2%}")

        all_results[f"h{horizon}"] = {
            'lightgbm': {'accuracy': float(results['lightgbm']['accuracy'])},
            'xgboost': {'accuracy': float(results['xgboost']['accuracy'])},
            'catboost': {'accuracy': float(results['catboost']['accuracy'])},
            'meta_learner': {'accuracy': float(results['meta_learner']['accuracy'])},
            'best_accuracy': float(results['best_accuracy'])
        }

    # Find best horizon
    best_horizon = None
    best_acc = 0
    for h, r in all_results.items():
        if r['best_accuracy'] > best_acc:
            best_acc = r['best_accuracy']
            best_horizon = h

    return {
        'pair': pair,
        'split_id': split_id,
        'feature_count': len(feature_cols),
        'results': all_results,
        'best_horizon': best_horizon,
        'best_accuracy': float(best_acc)
    }


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "major"  # "major" or "all"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    pairs = MAJOR_PAIRS if mode == "major" else ALL_PAIRS

    print("=" * 70)
    print(f"MULTI-PAIR TRAINING PIPELINE")
    print(f"Mode: {mode} ({len(pairs)} pairs)")
    print("=" * 70)

    all_pair_results = {}

    for pair in pairs:
        result = train_pair(pair, split_id)
        if result:
            all_pair_results[pair] = result

    # Summary
    print("\n" + "=" * 70)
    print("MULTI-PAIR TRAINING SUMMARY")
    print("=" * 70)
    print(f"{'Pair':<10} {'Best Horizon':<12} {'Best Accuracy':<15} {'h15 Acc':<10}")
    print("-" * 50)

    for pair, result in all_pair_results.items():
        h15_acc = result['results'].get('h15', {}).get('best_accuracy', 0)
        print(f"{pair.upper():<10} {result['best_horizon']:<12} {result['best_accuracy']:.2%}{'':>8} {h15_acc:.2%}")

    # Save results
    output = {
        "mode": mode,
        "split_id": split_id,
        "pairs_trained": len(all_pair_results),
        "timestamp": datetime.now().isoformat(),
        "results": all_pair_results
    }

    output_file = f"/tmp/multi_pair_results_{mode}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
