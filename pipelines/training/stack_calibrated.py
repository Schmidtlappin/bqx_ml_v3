#!/usr/bin/env python3
"""
Calibrated Probability Stacking Pipeline

Implements the Enhanced Stacking Architecture:
1. Walk-forward OOF predictions (prevents leakage)
2. Calibration before stacking (Platt scaling)
3. Regime-aware meta-learner
4. Confidence gating (called signal accuracy)

Target: 85-95% called accuracy with 30-50% coverage
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
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Embargo gap between train/val to prevent leakage
EMBARGO_INTERVALS = 30


def load_selected_features(pair: str, horizon: int) -> list:
    """Load stable features from robust selection."""
    try:
        with open(f"/home/micha/bqx_ml_v3/intelligence/robust_feature_selection_{pair}_h{horizon}.json") as f:
            selection = json.load(f)
        # Get top features from each group
        all_features = []
        for group_name, group_data in selection.get('groups', {}).items():
            for feat, score in group_data.get('top_features', []):
                all_features.append((feat, score, group_name))
        # Sort by score and take top 400
        all_features.sort(key=lambda x: -x[1])
        return [f[0] for f in all_features[:400]]
    except FileNotFoundError:
        return None


def create_walk_forward_splits(df: pd.DataFrame, n_folds: int = 5, embargo: int = EMBARGO_INTERVALS):
    """
    Create walk-forward time series splits with embargo gap.

    Train [0..T1] → Val (T1+embargo..T2)
    Train [0..T2] → Val (T2+embargo..T3)
    ...
    """
    df = df.sort_values('interval_time').reset_index(drop=True)
    n = len(df)
    fold_size = n // (n_folds + 1)

    splits = []
    for i in range(n_folds):
        train_end = fold_size * (i + 1)
        val_start = train_end + embargo
        val_end = fold_size * (i + 2)

        if val_end > n:
            val_end = n
        if val_start >= val_end:
            continue

        splits.append({
            'train_idx': list(range(0, train_end)),
            'val_idx': list(range(val_start, val_end))
        })

    return splits


def calibrate_probabilities(y_true, y_prob, method='platt'):
    """
    Calibrate probabilities using Platt scaling or isotonic regression.
    Returns calibrated probabilities.
    """
    if method == 'platt':
        calibrator = LogisticRegression(random_state=42, max_iter=1000)
        calibrator.fit(y_prob.reshape(-1, 1), y_true)
        return calibrator.predict_proba(y_prob.reshape(-1, 1))[:, 1], calibrator
    else:
        calibrator = IsotonicRegression(out_of_bounds='clip')
        calibrator.fit(y_prob, y_true)
        return calibrator.predict(y_prob), calibrator


def extract_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract regime descriptor features for meta-learner.
    """
    regime_cols = []

    # Volatility regime
    if 'vol_bqx_eurusd_source_value' in df.columns:
        regime_cols.append('vol_bqx_eurusd_source_value')

    # Trend strength (use regression slope features if available)
    for col in df.columns:
        if 'reg_slope' in col or 'reg_trend' in col:
            regime_cols.append(col)
            if len(regime_cols) > 5:
                break

    # Momentum regime
    for col in df.columns:
        if 'mom_rsi' in col or 'mom_macd' in col:
            regime_cols.append(col)
            if len(regime_cols) > 8:
                break

    if not regime_cols:
        return None

    return df[regime_cols].copy()


def train_base_models_oof(X_train, y_train, X_val, feature_names, seed=42):
    """
    Train base models and return OOF predictions.
    """
    results = {}

    # LightGBM
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 63, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1,
        'seed': seed, 'min_data_in_leaf': 50
    }
    lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
    lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=300)
    lgb_prob = lgb_model.predict(X_val)
    results['lightgbm'] = {'model': lgb_model, 'prob': lgb_prob}

    # XGBoost
    xgb_params = {
        'objective': 'binary:logistic', 'max_depth': 5, 'learning_rate': 0.03,
        'subsample': 0.8, 'colsample_bytree': 0.6, 'seed': seed, 'verbosity': 0
    }
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dval = xgb.DMatrix(X_val, feature_names=feature_names)
    xgb_model = xgb.train(xgb_params, dtrain, num_boost_round=300)
    xgb_prob = xgb_model.predict(dval)
    results['xgboost'] = {'model': xgb_model, 'prob': xgb_prob}

    # CatBoost
    cb_model = CatBoostClassifier(
        iterations=300, learning_rate=0.03, depth=5,
        loss_function='Logloss', verbose=False, random_seed=seed
    )
    cb_model.fit(X_train, y_train, verbose=False)
    cb_prob = cb_model.predict_proba(X_val)[:, 1]
    results['catboost'] = {'model': cb_model, 'prob': cb_prob}

    # ElasticNet (for diversity)
    en_model = LogisticRegression(
        penalty='elasticnet', solver='saga', l1_ratio=0.5,
        random_state=seed, max_iter=1000
    )
    en_model.fit(X_train, y_train)
    en_prob = en_model.predict_proba(X_val)[:, 1]
    results['elasticnet'] = {'model': en_model, 'prob': en_prob}

    return results


def train_calibrated_stack(df, feature_cols, target_col, n_folds=5, verbose=True):
    """
    Full calibrated stacking pipeline with walk-forward OOF.

    Returns:
    - Calibrated meta-learner
    - Base model ensemble
    - Performance metrics
    """
    target_series = df[target_col]
    y = (target_series > 0).astype(int).values

    # Get features
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values

    # Get regime features if available
    regime_df = extract_regime_features(df)

    # Create walk-forward splits
    splits = create_walk_forward_splits(df, n_folds=n_folds)

    if verbose:
        print(f"  Created {len(splits)} walk-forward folds with {EMBARGO_INTERVALS} interval embargo")

    # Collect OOF predictions
    oof_lgb = np.zeros(len(df))
    oof_xgb = np.zeros(len(df))
    oof_cb = np.zeros(len(df))
    oof_en = np.zeros(len(df))
    oof_y = np.zeros(len(df))
    oof_mask = np.zeros(len(df), dtype=bool)

    regime_features_oof = []

    for fold_idx, split in enumerate(splits):
        train_idx = split['train_idx']
        val_idx = split['val_idx']

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Handle NaN
        train_mask = ~(np.isnan(X_train).any(axis=1) | np.isnan(y_train))
        val_mask = ~(np.isnan(X_val).any(axis=1) | np.isnan(y_val))

        X_train_clean = X_train[train_mask]
        y_train_clean = y_train[train_mask]
        X_val_clean = X_val[val_mask]

        if len(X_train_clean) < 1000 or len(X_val_clean) < 100:
            continue

        # Train base models
        base_results = train_base_models_oof(
            X_train_clean, y_train_clean, X_val_clean, feature_cols
        )

        # Store OOF predictions
        val_idx_clean = [val_idx[i] for i, m in enumerate(val_mask) if m]
        for i, idx in enumerate(val_idx_clean):
            oof_lgb[idx] = base_results['lightgbm']['prob'][i]
            oof_xgb[idx] = base_results['xgboost']['prob'][i]
            oof_cb[idx] = base_results['catboost']['prob'][i]
            oof_en[idx] = base_results['elasticnet']['prob'][i]
            oof_y[idx] = y[idx]
            oof_mask[idx] = True

        # Store regime features for this fold
        if regime_df is not None:
            regime_features_oof.append(regime_df.iloc[val_idx_clean].values)

        if verbose:
            print(f"    Fold {fold_idx+1}: train={len(X_train_clean)}, val={len(X_val_clean)}")

    # Use only samples with OOF predictions
    oof_indices = np.where(oof_mask)[0]

    if len(oof_indices) < 500:
        print("  ERROR: Insufficient OOF samples")
        return None

    # Extract OOF data
    lgb_oof = oof_lgb[oof_indices]
    xgb_oof = oof_xgb[oof_indices]
    cb_oof = oof_cb[oof_indices]
    en_oof = oof_en[oof_indices]
    y_oof = oof_y[oof_indices].astype(int)

    # Calibrate each base model's probabilities
    if verbose:
        print("  Calibrating base model probabilities...")

    lgb_cal, lgb_calibrator = calibrate_probabilities(y_oof, lgb_oof, method='platt')
    xgb_cal, xgb_calibrator = calibrate_probabilities(y_oof, xgb_oof, method='platt')
    cb_cal, cb_calibrator = calibrate_probabilities(y_oof, cb_oof, method='platt')
    en_cal, en_calibrator = calibrate_probabilities(y_oof, en_oof, method='platt')

    # Stack calibrated probabilities
    meta_X = np.column_stack([lgb_cal, xgb_cal, cb_cal, en_cal])

    # Add regime features if available
    if regime_df is not None and len(regime_features_oof) > 0:
        regime_oof = np.vstack(regime_features_oof)
        if len(regime_oof) == len(meta_X):
            meta_X = np.hstack([meta_X, regime_oof])
            if verbose:
                print(f"  Added {regime_oof.shape[1]} regime features to meta-learner")

    # Train meta-learner (logistic regression for simplicity and stability)
    if verbose:
        print("  Training meta-learner...")

    meta_model = LogisticRegression(random_state=42, max_iter=1000)
    meta_model.fit(meta_X, y_oof)

    # Get final calibrated probabilities
    final_prob = meta_model.predict_proba(meta_X)[:, 1]

    # Evaluate
    overall_acc = accuracy_score(y_oof, (final_prob > 0.5).astype(int))
    overall_auc = roc_auc_score(y_oof, final_prob)

    # Confidence gating metrics
    thresholds = [0.55, 0.60, 0.65, 0.70]
    gating_results = {}

    for tau in thresholds:
        called_mask = (final_prob >= tau) | (final_prob <= 1 - tau)
        if called_mask.sum() > 0:
            called_acc = accuracy_score(y_oof[called_mask], (final_prob[called_mask] > 0.5).astype(int))
            coverage = called_mask.sum() / len(y_oof)
            gating_results[f"tau_{int(tau*100)}"] = {
                'accuracy': float(called_acc),
                'coverage': float(coverage),
                'n_signals': int(called_mask.sum())
            }

    results = {
        'overall_accuracy': float(overall_acc),
        'overall_auc': float(overall_auc),
        'oof_samples': len(y_oof),
        'gating_results': gating_results,
        'base_model_aucs': {
            'lightgbm': float(roc_auc_score(y_oof, lgb_cal)),
            'xgboost': float(roc_auc_score(y_oof, xgb_cal)),
            'catboost': float(roc_auc_score(y_oof, cb_cal)),
            'elasticnet': float(roc_auc_score(y_oof, en_cal))
        },
        'calibrators': {
            'lightgbm': lgb_calibrator,
            'xgboost': xgb_calibrator,
            'catboost': cb_calibrator,
            'elasticnet': en_calibrator
        },
        'meta_model': meta_model
    }

    if verbose:
        print(f"\n  RESULTS:")
        print(f"    Overall accuracy: {overall_acc:.2%}")
        print(f"    Overall AUC: {overall_auc:.4f}")
        print(f"    OOF samples: {len(y_oof)}")
        print(f"\n  Confidence gating:")
        for tau, res in gating_results.items():
            print(f"    {tau}: acc={res['accuracy']:.2%}, coverage={res['coverage']:.2%}, n={res['n_signals']}")

    return results


def load_training_data_with_features(pair: str, split: dict, feature_list: list, sample_limit: int = 100000):
    """Load training data with selected features."""
    client = bigquery.Client(project=PROJECT)

    # Group features by source table
    table_features = {}
    for feat in feature_list:
        # Parse table from feature name (e.g., "agg_bqx_eurusd_..." -> "agg_bqx")
        parts = feat.split('_')
        if len(parts) >= 3:
            # Handle different naming patterns
            if parts[0] in ['agg', 'reg', 'mom', 'der', 'vol', 'div', 'align', 'base', 'lag', 'mrt', 'ext', 'cyc', 'corr', 'cov']:
                table_type = f"{parts[0]}_{parts[1]}"
            else:
                table_type = 'other'

            if table_type not in table_features:
                table_features[table_type] = []
            table_features[table_type].append(feat)

    # Build query with limited features to avoid BigQuery limits
    select_parts = ["t.interval_time"]

    # Take first 100 features to start
    limited_features = feature_list[:100]
    for feat in limited_features:
        select_parts.append(f"t.{feat}")

    # Add targets
    for h in HORIZONS:
        select_parts.append(f"targets.target_bqx45_h{h}")

    query = f"""
    WITH features AS (
        SELECT * FROM `{PROJECT}.{ANALYTICS_DATASET}.training_{pair}_selected`
        WHERE DATE(interval_time) BETWEEN '{split['train']['start']}' AND '{split['train']['end']}'
    )
    SELECT {', '.join(select_parts)}
    FROM features t
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON t.interval_time = targets.interval_time
    WHERE targets.target_bqx45_h15 IS NOT NULL
    ORDER BY t.interval_time
    LIMIT {sample_limit}
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Query failed: {e}")
        return None


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    print("=" * 70)
    print("CALIBRATED PROBABILITY STACKING PIPELINE")
    print(f"Pair: {pair.upper()}, Horizon: h{horizon}")
    print("=" * 70)

    # Load selected features
    features = load_selected_features(pair, horizon)
    if features:
        print(f"Loaded {len(features)} selected features from robust selection")
    else:
        print("No feature selection found, using default features")
        features = None

    # Load split config
    try:
        with open(f"/home/micha/bqx_ml_v3/configs/walk_forward_splits_{pair}.json") as f:
            splits_config = json.load(f)
    except FileNotFoundError:
        with open("/home/micha/bqx_ml_v3/configs/walk_forward_splits_eurusd.json") as f:
            splits_config = json.load(f)

    split = splits_config['splits'][0]
    print(f"Split: {split['train']['start']} to {split['test']['end']}")

    # Load data
    print("\nLoading training data...")
    client = bigquery.Client(project=PROJECT)

    # Use V2 schema with correct column names
    query = f"""
    SELECT
        reg_idx.interval_time,
        -- Polynomial IDX (priority) - using V2 column names
        reg_idx.reg_quad_term_45, reg_idx.reg_lin_term_45, reg_idx.reg_total_var_45,
        reg_idx.reg_slope_45, reg_idx.reg_trend_str_45, reg_idx.reg_deviation_45, reg_idx.reg_zscore_45,
        reg_idx.reg_quad_term_90, reg_idx.reg_lin_term_90, reg_idx.reg_total_var_90,
        reg_idx.reg_slope_90, reg_idx.reg_trend_str_90, reg_idx.reg_deviation_90, reg_idx.reg_zscore_90,
        reg_idx.reg_quad_term_180, reg_idx.reg_lin_term_180, reg_idx.reg_total_var_180,
        reg_idx.reg_slope_180, reg_idx.reg_trend_str_180, reg_idx.reg_deviation_180, reg_idx.reg_zscore_180,
        reg_idx.reg_quad_term_360, reg_idx.reg_lin_term_360, reg_idx.reg_total_var_360,
        reg_idx.reg_slope_360, reg_idx.reg_trend_str_360,
        reg_idx.reg_quad_term_720, reg_idx.reg_lin_term_720, reg_idx.reg_total_var_720,
        reg_idx.reg_slope_720, reg_idx.reg_trend_str_720,
        reg_idx.reg_quad_term_1440, reg_idx.reg_lin_term_1440, reg_idx.reg_total_var_1440,
        reg_idx.reg_slope_1440, reg_idx.reg_trend_str_1440,

        -- Polynomial BQX
        reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
        reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_slope_45 as bqx_slope_45,
        reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
        reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_slope_90 as bqx_slope_90,
        reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
        reg_bqx.reg_total_var_180 as bqx_tvar_180,

        -- Base BQX
        base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,

        -- Regime indicators from agg_bqx (std as volatility proxy)
        agg_bqx.agg_std_45 as regime_vol_45, agg_bqx.agg_std_90 as regime_vol_90,
        agg_bqx.agg_cv_45 as regime_cv_45, agg_bqx.agg_cv_90 as regime_cv_90,

        -- Derivative features (momentum indicators)
        der_bqx.der_v1_45 as regime_der1_45, der_bqx.der_v1_90 as regime_der1_90,
        der_bqx.der_v2_45 as regime_der2_45, der_bqx.der_v2_90 as regime_der2_90,

        -- Targets
        targets.target_bqx45_h15, targets.target_bqx45_h30, targets.target_bqx45_h45,
        targets.target_bqx45_h60, targets.target_bqx45_h75, targets.target_bqx45_h90,
        targets.target_bqx45_h105

    FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` reg_idx
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` reg_bqx
        ON reg_idx.interval_time = reg_bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base_bqx
        ON reg_idx.interval_time = base_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}` agg_bqx
        ON reg_idx.interval_time = agg_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.der_bqx_{pair}` der_bqx
        ON reg_idx.interval_time = der_bqx.interval_time
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON reg_idx.interval_time = targets.interval_time
    WHERE DATE(reg_idx.interval_time) BETWEEN '{split['train']['start']}' AND '{split['validation']['end']}'
    AND targets.target_bqx45_h{horizon} IS NOT NULL
    ORDER BY reg_idx.interval_time
    LIMIT 80000
    """

    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")

    # Identify feature and target columns
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    target_col = f'target_bqx45_h{horizon}'

    print(f"\n=== Training Calibrated Stack for h{horizon} ===")
    print(f"Features: {len(feature_cols)}")

    results = train_calibrated_stack(df, feature_cols, target_col, n_folds=5, verbose=True)

    if results is None:
        print("ERROR: Stack training failed")
        return

    # Summary
    print("\n" + "=" * 70)
    print("CALIBRATED STACK SUMMARY")
    print("=" * 70)
    print(f"Overall Accuracy: {results['overall_accuracy']:.2%}")
    print(f"Overall AUC: {results['overall_auc']:.4f}")
    print(f"\nBase Model AUCs:")
    for name, auc in results['base_model_aucs'].items():
        print(f"  {name}: {auc:.4f}")

    print(f"\nConfidence Gating (Direction Accuracy):")
    best_tau = None
    best_acc = 0
    for tau, res in results['gating_results'].items():
        print(f"  {tau}: {res['accuracy']:.2%} acc, {res['coverage']:.2%} coverage, {res['n_signals']} signals")
        if res['accuracy'] > best_acc and res['coverage'] >= 0.20:
            best_acc = res['accuracy']
            best_tau = tau

    if best_tau:
        print(f"\n  Recommended threshold: {best_tau} ({best_acc:.2%} accuracy)")

    # Save results
    output = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'overall_accuracy': results['overall_accuracy'],
        'overall_auc': results['overall_auc'],
        'base_model_aucs': results['base_model_aucs'],
        'gating_results': results['gating_results'],
        'recommended_threshold': best_tau,
        'oof_samples': results['oof_samples']
    }

    output_file = f"/tmp/calibrated_stack_{pair}_h{horizon}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
