#!/usr/bin/env python3
"""
Meta-Learner Stacking for BQX ML V3

Trains 3 base models (LightGBM, XGBoost, CatBoost) and stacks their predictions
using a Logistic Regression meta-learner for improved accuracy.

Per roadmap:
- Expected boost: +5-8% accuracy from stacking
- Architecture: LGB + XGB + CB -> LogReg meta-learner
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
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def load_training_data(pair: str, split: dict, sample_limit: int = 100000) -> tuple:
    """Load training data from V2 tables."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        reg_idx.interval_time,
        -- IDX Polynomial Features (priority #1)
        reg_idx.reg_quad_term_45 as idx_quad_45, reg_idx.reg_lin_term_45 as idx_lin_45,
        reg_idx.reg_const_term_45 as idx_const_45, reg_idx.reg_total_var_45 as idx_tvar_45,
        reg_idx.reg_slope_45 as idx_slope_45, reg_idx.reg_acceleration_45 as idx_accel_45,
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

        -- BQX Polynomial Features (priority #3)
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
        agg_idx.agg_mean_90 as idx_mean_90, agg_idx.agg_std_90 as idx_std_90,

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

    print(f"  Loading training data...")
    train_df = client.query(query).to_dataframe()
    print(f"    Train: {len(train_df):,} rows, {len(train_df.columns)} columns")

    # Load validation data
    val_query = query.replace(
        f"'{split['train']['start']}' AND '{split['train']['end']}'",
        f"'{split['validation']['start']}' AND '{split['validation']['end']}'"
    ).replace(f"LIMIT {sample_limit}", f"LIMIT {sample_limit // 2}")

    print(f"  Loading validation data...")
    val_df = client.query(val_query).to_dataframe()
    print(f"    Val: {len(val_df):,} rows")

    return train_df, val_df


def prepare_data(X, y):
    """Convert to numeric and handle NaN, create binary target."""
    X = pd.DataFrame(X).apply(pd.to_numeric, errors='coerce').values
    y = pd.to_numeric(pd.Series(y), errors='coerce').values

    mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X_clean = X[mask]
    y_clean = y[mask]

    # Binary classification target
    y_binary = (y_clean > 0).astype(int)

    return X_clean, y_binary


def train_base_models(X_train, y_train, X_val, y_val, feature_names):
    """Train base models: LightGBM, XGBoost, CatBoost."""
    results = {}

    # LightGBM
    print("    Training LightGBM...")
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 50, 'lambda_l1': 0.1, 'lambda_l2': 0.1
    }
    lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
    lgb_val = lgb.Dataset(X_val, label=y_val, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=1000,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(100, verbose=False)])
    lgb_prob_train = lgb_model.predict(X_train)
    lgb_prob_val = lgb_model.predict(X_val)
    lgb_acc = accuracy_score(y_val, (lgb_prob_val > 0.5).astype(int))
    results['lightgbm'] = {'model': lgb_model, 'prob_train': lgb_prob_train, 'prob_val': lgb_prob_val, 'accuracy': lgb_acc}
    print(f"      LGB: {lgb_acc:.2%}")

    # XGBoost
    print("    Training XGBoost...")
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 6, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.6, 'seed': 42, 'verbosity': 0,
        'reg_alpha': 0.1, 'reg_lambda': 0.1
    }
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dval = xgb.DMatrix(X_val, label=y_val, feature_names=feature_names)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=1000,
                          evals=[(dval, 'val')], early_stopping_rounds=100, verbose_eval=False)
    xgb_prob_train = xgb_model.predict(xgb.DMatrix(X_train, feature_names=feature_names))
    xgb_prob_val = xgb_model.predict(dval)
    xgb_acc = accuracy_score(y_val, (xgb_prob_val > 0.5).astype(int))
    results['xgboost'] = {'model': xgb_model, 'prob_train': xgb_prob_train, 'prob_val': xgb_prob_val, 'accuracy': xgb_acc}
    print(f"      XGB: {xgb_acc:.2%}")

    # CatBoost
    print("    Training CatBoost...")
    cb_model = CatBoostClassifier(
        iterations=1000, learning_rate=0.03, depth=6,
        loss_function='Logloss', verbose=False, random_seed=42,
        l2_leaf_reg=3, early_stopping_rounds=100
    )
    cb_model.fit(X_train, y_train, eval_set=(X_val, y_val), verbose=False)
    cb_prob_train = cb_model.predict_proba(X_train)[:, 1]
    cb_prob_val = cb_model.predict_proba(X_val)[:, 1]
    cb_acc = accuracy_score(y_val, cb_model.predict(X_val).flatten())
    results['catboost'] = {'model': cb_model, 'prob_train': cb_prob_train, 'prob_val': cb_prob_val, 'accuracy': cb_acc}
    print(f"      CB:  {cb_acc:.2%}")

    return results


def train_meta_learner(base_results, y_train, y_val):
    """Train meta-learner on base model predictions."""
    print("    Training Meta-Learner (Logistic Regression)...")

    # Stack base model predictions as meta-features
    meta_X_train = np.column_stack([
        base_results['lightgbm']['prob_train'],
        base_results['xgboost']['prob_train'],
        base_results['catboost']['prob_train']
    ])

    meta_X_val = np.column_stack([
        base_results['lightgbm']['prob_val'],
        base_results['xgboost']['prob_val'],
        base_results['catboost']['prob_val']
    ])

    # Train logistic regression meta-learner
    meta_model = LogisticRegression(random_state=42, max_iter=1000)
    meta_model.fit(meta_X_train, y_train)

    # Predict
    meta_prob_val = meta_model.predict_proba(meta_X_val)[:, 1]
    meta_pred = meta_model.predict(meta_X_val)
    meta_acc = accuracy_score(y_val, meta_pred)

    print(f"      Meta-Learner: {meta_acc:.2%}")

    # Compare to weighted average
    weights = np.array([
        base_results['lightgbm']['accuracy'],
        base_results['xgboost']['accuracy'],
        base_results['catboost']['accuracy']
    ])
    weights = weights / weights.sum()
    weighted_prob = (
        weights[0] * base_results['lightgbm']['prob_val'] +
        weights[1] * base_results['xgboost']['prob_val'] +
        weights[2] * base_results['catboost']['prob_val']
    )
    weighted_acc = accuracy_score(y_val, (weighted_prob > 0.5).astype(int))
    print(f"      Weighted Avg: {weighted_acc:.2%}")

    return {
        'model': meta_model,
        'accuracy': meta_acc,
        'weighted_accuracy': weighted_acc,
        'coefficients': meta_model.coef_.tolist(),
        'intercept': float(meta_model.intercept_[0])
    }


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    print("=" * 70)
    print(f"META-LEARNER STACKING Training for {pair.upper()}")
    print("Architecture: LightGBM + XGBoost + CatBoost -> LogReg Meta-Learner")
    print("=" * 70)

    # Load split config
    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    # Load data
    train_df, val_df = load_training_data(pair, split)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    print(f"\nFeatures: {len(feature_cols)}")

    all_results = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        print(f"\n{'='*60}")
        print(f"Horizon h{horizon}")
        print(f"{'='*60}")

        X_train, y_train = prepare_data(train_df[feature_cols], train_df[target_col])
        X_val, y_val = prepare_data(val_df[feature_cols], val_df[target_col])

        if len(X_train) < 1000:
            print(f"  Insufficient data, skipping...")
            continue

        print(f"    Train: {len(X_train):,} rows, Val: {len(X_val):,} rows")
        print(f"    Class balance: {y_train.mean():.2%} positive")

        # Train base models
        base_results = train_base_models(X_train, y_train, X_val, y_val, feature_cols)

        # Train meta-learner
        meta_results = train_meta_learner(base_results, y_train, y_val)

        # Compile results
        horizon_results = {
            'lightgbm': {'accuracy': float(base_results['lightgbm']['accuracy'])},
            'xgboost': {'accuracy': float(base_results['xgboost']['accuracy'])},
            'catboost': {'accuracy': float(base_results['catboost']['accuracy'])},
            'meta_learner': {
                'accuracy': float(meta_results['accuracy']),
                'coefficients': meta_results['coefficients'],
                'intercept': meta_results['intercept']
            },
            'weighted_ensemble': {'accuracy': float(meta_results['weighted_accuracy'])},
            'best_accuracy': max(
                base_results['lightgbm']['accuracy'],
                base_results['xgboost']['accuracy'],
                base_results['catboost']['accuracy'],
                meta_results['accuracy'],
                meta_results['weighted_accuracy']
            )
        }

        all_results[f"h{horizon}"] = horizon_results

    # Summary
    print("\n" + "=" * 70)
    print("META-LEARNER STACKING RESULTS")
    print("=" * 70)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Meta':<10} {'Weighted':<10} {'Best':<10}")
    print("-" * 70)

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            best_this = r['best_accuracy']

            print(f"h{h:<7} {r['lightgbm']['accuracy']:.2%}{'':>3} "
                  f"{r['xgboost']['accuracy']:.2%}{'':>3} "
                  f"{r['catboost']['accuracy']:.2%}{'':>3} "
                  f"{r['meta_learner']['accuracy']:.2%}{'':>3} "
                  f"{r['weighted_ensemble']['accuracy']:.2%}{'':>3} "
                  f"{best_this:.2%}")

            if best_this > best_acc:
                best_acc = best_this
                best_horizon = key

    print(f"\nBest: {best_horizon} with {best_acc:.2%} accuracy")

    # Compare to baseline
    print("\nMeta-Learner Impact Analysis:")
    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            base_best = max(r['lightgbm']['accuracy'], r['xgboost']['accuracy'], r['catboost']['accuracy'])
            meta_acc = r['meta_learner']['accuracy']
            improvement = meta_acc - base_best
            print(f"  h{h}: Meta {meta_acc:.2%} vs Base Best {base_best:.2%} = {'+' if improvement > 0 else ''}{improvement:.2%}")

    # Save results
    output = {
        "pair": pair,
        "split_id": split_id,
        "approach": "meta_learner_stacking",
        "feature_count": len(feature_cols),
        "results": all_results,
        "best_horizon": best_horizon,
        "best_accuracy": float(best_acc),
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/meta_learner_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
