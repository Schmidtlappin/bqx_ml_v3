#!/usr/bin/env python3
"""
Training using V2 feature tables directly.

Uses JOINs against: reg_idx_*, reg_bqx_*, agg_idx_*, base_idx_*, targets_*
User mandate: ALL polynomial features (quad, lin, const, residual, variance)
Feature Priority: #1 IDX poly, #2 IDX base, #3 BQX poly, #4 BQX base
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


def load_data(pair: str, split: dict, limit: int = None) -> tuple:
    """Load training data by joining V2 feature tables."""
    client = bigquery.Client(project=PROJECT)

    limit_clause = f"LIMIT {limit}" if limit else ""

    def build_query(date_start, date_end):
        return f"""
        SELECT
            reg_idx.interval_time,
            -- IDX Polynomial Features (user priority #1)
            reg_idx.reg_quad_term_45 as idx_quad_45, reg_idx.reg_lin_term_45 as idx_lin_45,
            reg_idx.reg_const_term_45 as idx_const_45, reg_idx.reg_residual_45 as idx_resid_45,
            reg_idx.reg_total_var_45 as idx_tvar_45, reg_idx.reg_resid_var_45 as idx_rvar_45,
            reg_idx.reg_r2_45 as idx_r2_45, reg_idx.reg_rmse_45 as idx_rmse_45,
            reg_idx.reg_slope_45 as idx_slope_45, reg_idx.reg_acceleration_45 as idx_accel_45,
            reg_idx.reg_forecast_5_45 as idx_fcst_45, reg_idx.reg_zscore_45 as idx_zscore_45,
            reg_idx.reg_deviation_45 as idx_dev_45, reg_idx.reg_trend_str_45 as idx_trend_45,

            reg_idx.reg_quad_term_90 as idx_quad_90, reg_idx.reg_lin_term_90 as idx_lin_90,
            reg_idx.reg_const_term_90 as idx_const_90, reg_idx.reg_residual_90 as idx_resid_90,
            reg_idx.reg_total_var_90 as idx_tvar_90, reg_idx.reg_resid_var_90 as idx_rvar_90,
            reg_idx.reg_r2_90 as idx_r2_90, reg_idx.reg_rmse_90 as idx_rmse_90,
            reg_idx.reg_slope_90 as idx_slope_90, reg_idx.reg_acceleration_90 as idx_accel_90,

            reg_idx.reg_quad_term_180 as idx_quad_180, reg_idx.reg_lin_term_180 as idx_lin_180,
            reg_idx.reg_const_term_180 as idx_const_180, reg_idx.reg_residual_180 as idx_resid_180,
            reg_idx.reg_total_var_180 as idx_tvar_180, reg_idx.reg_resid_var_180 as idx_rvar_180,
            reg_idx.reg_r2_180 as idx_r2_180, reg_idx.reg_slope_180 as idx_slope_180,

            reg_idx.reg_quad_term_360 as idx_quad_360, reg_idx.reg_lin_term_360 as idx_lin_360,
            reg_idx.reg_const_term_360 as idx_const_360, reg_idx.reg_residual_360 as idx_resid_360,
            reg_idx.reg_total_var_360 as idx_tvar_360, reg_idx.reg_r2_360 as idx_r2_360,
            reg_idx.reg_slope_360 as idx_slope_360,

            reg_idx.reg_quad_term_720 as idx_quad_720, reg_idx.reg_lin_term_720 as idx_lin_720,
            reg_idx.reg_const_term_720 as idx_const_720, reg_idx.reg_residual_720 as idx_resid_720,
            reg_idx.reg_total_var_720 as idx_tvar_720, reg_idx.reg_r2_720 as idx_r2_720,
            reg_idx.reg_slope_720 as idx_slope_720,

            reg_idx.reg_quad_term_1440 as idx_quad_1440, reg_idx.reg_lin_term_1440 as idx_lin_1440,
            reg_idx.reg_const_term_1440 as idx_const_1440, reg_idx.reg_residual_1440 as idx_resid_1440,
            reg_idx.reg_total_var_1440 as idx_tvar_1440, reg_idx.reg_r2_1440 as idx_r2_1440,
            reg_idx.reg_slope_1440 as idx_slope_1440,

            -- BQX Polynomial Features (user priority #3)
            reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
            reg_bqx.reg_const_term_45 as bqx_const_45, reg_bqx.reg_residual_45 as bqx_resid_45,
            reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_resid_var_45 as bqx_rvar_45,
            reg_bqx.reg_r2_45 as bqx_r2_45, reg_bqx.reg_rmse_45 as bqx_rmse_45,
            reg_bqx.reg_slope_45 as bqx_slope_45, reg_bqx.reg_zscore_45 as bqx_zscore_45,

            reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
            reg_bqx.reg_const_term_90 as bqx_const_90, reg_bqx.reg_residual_90 as bqx_resid_90,
            reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_r2_90 as bqx_r2_90,
            reg_bqx.reg_slope_90 as bqx_slope_90,

            reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
            reg_bqx.reg_const_term_180 as bqx_const_180, reg_bqx.reg_residual_180 as bqx_resid_180,
            reg_bqx.reg_total_var_180 as bqx_tvar_180, reg_bqx.reg_r2_180 as bqx_r2_180,

            reg_bqx.reg_quad_term_360 as bqx_quad_360, reg_bqx.reg_lin_term_360 as bqx_lin_360,
            reg_bqx.reg_residual_360 as bqx_resid_360, reg_bqx.reg_total_var_360 as bqx_tvar_360,

            -- IDX Base features (user priority #2)
            base_idx.open_idx, base_idx.high_idx, base_idx.low_idx, base_idx.close_idx,

            -- BQX Base features (user priority #4)
            base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,
            base_bqx.bqx_720, base_bqx.bqx_1440, base_bqx.bqx_2880,

            -- Aggregation features
            agg_idx.agg_mean_45 as idx_mean_45, agg_idx.agg_std_45 as idx_std_45,
            agg_idx.agg_min_45 as idx_min_45, agg_idx.agg_max_45 as idx_max_45,
            agg_idx.agg_range_45 as idx_range_45, agg_idx.agg_cv_45 as idx_cv_45,
            agg_idx.agg_mean_90 as idx_mean_90, agg_idx.agg_std_90 as idx_std_90,

            agg_bqx.agg_mean_45 as bqx_mean_45, agg_bqx.agg_std_45 as bqx_std_45,
            agg_bqx.agg_min_45 as bqx_min_45, agg_bqx.agg_max_45 as bqx_max_45,
            agg_bqx.agg_range_45 as bqx_range_45, agg_bqx.agg_cv_45 as bqx_cv_45,

            -- Targets
            tgt.target_bqx45_h15, tgt.target_bqx45_h30, tgt.target_bqx45_h45,
            tgt.target_bqx45_h60, tgt.target_bqx45_h75, tgt.target_bqx45_h90, tgt.target_bqx45_h105
        FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` reg_idx
        JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` reg_bqx ON reg_idx.interval_time = reg_bqx.interval_time
        JOIN `{PROJECT}.{FEATURES_DATASET}.base_idx_{pair}` base_idx ON reg_idx.interval_time = base_idx.interval_time
        JOIN `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base_bqx ON reg_idx.interval_time = base_bqx.interval_time
        JOIN `{PROJECT}.{FEATURES_DATASET}.agg_idx_{pair}` agg_idx ON reg_idx.interval_time = agg_idx.interval_time
        JOIN `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}` agg_bqx ON reg_idx.interval_time = agg_bqx.interval_time
        JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` tgt ON reg_idx.interval_time = tgt.interval_time
        WHERE DATE(reg_idx.interval_time) BETWEEN '{date_start}' AND '{date_end}'
        AND tgt.target_bqx45_h15 IS NOT NULL
        {limit_clause}
        """

    print(f"  Loading training data with polynomial features...")
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

    y_binary = (y_clean > 0).astype(int)

    return X_clean, y_binary


def train_ensemble(X_train, y_train, X_val, y_val, feature_names):
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
        'num_leaves': 127, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1, 'seed': 42,
        'min_data_in_leaf': 50, 'lambda_l1': 0.1, 'lambda_l2': 0.1
    }
    lgb_train = lgb.Dataset(X_tr, label=y_tr, feature_name=feature_names)
    lgb_val = lgb.Dataset(X_vl, label=y_vl, reference=lgb_train)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=1000,
                          valid_sets=[lgb_val], callbacks=[lgb.early_stopping(100, verbose=False)])
    lgb_prob = lgb_model.predict(X_vl)
    lgb_pred = (lgb_prob > 0.5).astype(int)
    lgb_acc = accuracy_score(y_vl, lgb_pred)
    results['lightgbm'] = {'accuracy': float(lgb_acc)}
    print(f"      LGB: {lgb_acc:.2%}")

    # Feature importance
    importance = lgb_model.feature_importance()
    top_indices = np.argsort(importance)[-20:][::-1]
    results['top_features'] = [(feature_names[i], int(importance[i])) for i in top_indices]

    # XGBoost
    print(f"    Training XGBoost...")
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 6, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.6, 'seed': 42, 'verbosity': 0
    }
    dtrain = xgb.DMatrix(X_tr, label=y_tr, feature_names=feature_names)
    dval = xgb.DMatrix(X_vl, label=y_vl, feature_names=feature_names)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=1000,
                          evals=[(dval, 'val')], early_stopping_rounds=100, verbose_eval=False)
    xgb_prob = xgb_model.predict(dval)
    xgb_pred = (xgb_prob > 0.5).astype(int)
    xgb_acc = accuracy_score(y_vl, xgb_pred)
    results['xgboost'] = {'accuracy': float(xgb_acc)}
    print(f"      XGB: {xgb_acc:.2%}")

    # CatBoost
    print(f"    Training CatBoost...")
    cb_model = CatBoostClassifier(
        iterations=1000, learning_rate=0.03, depth=6,
        loss_function='Logloss', verbose=False, random_seed=42,
        early_stopping_rounds=100
    )
    cb_model.fit(X_tr, y_tr, eval_set=(X_vl, y_vl), verbose=False)
    cb_pred = cb_model.predict(X_vl).flatten()
    cb_acc = accuracy_score(y_vl, cb_pred)
    results['catboost'] = {'accuracy': float(cb_acc)}
    print(f"      CB:  {cb_acc:.2%}")

    results['best_accuracy'] = max(lgb_acc, xgb_acc, cb_acc)

    return results


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    split_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

    print("=" * 70)
    print(f"V2 TABLE Training for {pair.upper()}")
    print("User Mandate: ALL poly features (quad, lin, const, residual, var)")
    print("Feature Priority: IDX poly > IDX base > BQX poly > BQX base")
    print("=" * 70)

    with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
        splits_config = json.load(f)
    split = splits_config['splits'][split_id]

    print(f"\nSplit {split_id}: {split['train']['start']} to {split['test']['end']}")

    train_df, val_df = load_data(pair, split, limit)

    target_cols = [c for c in train_df.columns if c.startswith('target_')]
    feature_cols = [c for c in train_df.columns if c not in target_cols and c != 'interval_time']

    # Count feature types
    idx_poly = [c for c in feature_cols if c.startswith('idx_') and any(x in c for x in ['quad', 'lin', 'const', 'resid', 'tvar', 'rvar', 'r2', 'rmse', 'slope', 'accel', 'fcst', 'zscore', 'dev', 'trend'])]
    bqx_poly = [c for c in feature_cols if c.startswith('bqx_') and any(x in c for x in ['quad', 'lin', 'const', 'resid', 'tvar', 'rvar', 'r2', 'rmse', 'slope'])]
    other = [c for c in feature_cols if c not in idx_poly and c not in bqx_poly]

    print(f"\nFeature Categories:")
    print(f"  IDX Polynomial: {len(idx_poly)} features")
    print(f"  BQX Polynomial: {len(bqx_poly)} features")
    print(f"  Other (base/agg): {len(other)} features")
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

        results = train_ensemble(X_train, y_train, X_val, y_val, feature_cols)
        if results:
            all_results[f"h{horizon}"] = results

    # Summary
    print("\n" + "=" * 70)
    print("V2 TABLE TRAINING RESULTS")
    print("=" * 70)
    print(f"{'Horizon':<8} {'LGB':<10} {'XGB':<10} {'CB':<10} {'Best'}")
    print("-" * 50)

    best_horizon = None
    best_acc = 0

    for h in HORIZONS:
        key = f"h{h}"
        if key in all_results:
            r = all_results[key]
            print(f"h{h:<7} {r['lightgbm']['accuracy']:.2%}{'':>3} "
                  f"{r['xgboost']['accuracy']:.2%}{'':>3} "
                  f"{r['catboost']['accuracy']:.2%}{'':>3} "
                  f"{r['best_accuracy']:.2%}")

            if r['best_accuracy'] > best_acc:
                best_acc = r['best_accuracy']
                best_horizon = key

    print(f"\nBest: {best_horizon} with {best_acc:.2%} accuracy")

    # Show top features
    if best_horizon and 'top_features' in all_results[best_horizon]:
        print(f"\nTop 20 Features for {best_horizon}:")
        idx_count = 0
        bqx_count = 0
        for i, (feat, imp) in enumerate(all_results[best_horizon]['top_features'][:20], 1):
            if feat.startswith('idx_'):
                idx_count += 1
                prefix = "IDX"
            elif feat.startswith('bqx_'):
                bqx_count += 1
                prefix = "BQX"
            else:
                prefix = "OTH"
            print(f"  {i:2}. [{prefix}] {feat}: {imp}")
        print(f"\n  IDX: {idx_count}, BQX: {bqx_count}")

    output = {
        "pair": pair, "split_id": split_id, "approach": "v2_tables_join",
        "feature_count": len(feature_cols),
        "feature_breakdown": {"idx_poly": len(idx_poly), "bqx_poly": len(bqx_poly), "other": len(other)},
        "results": all_results,
        "best_horizon": best_horizon, "best_accuracy": best_acc,
        "timestamp": datetime.now().isoformat()
    }

    output_file = f"/tmp/v2_training_results_{pair}_split{split_id}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
