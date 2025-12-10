#!/usr/bin/env python3
"""
Re-Serialize h15 with Full Calibrated Stack Pipeline
CE Directive: 20251210_0320

Creates h15_ensemble_v2.joblib with:
- Base models (LGB, XGB, CB)
- Calibrators (3x Platt scaling)
- Meta-learner (LogReg)
- Regime features
- EA-003 compatibility placeholders
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery, storage
import lightgbm as lgb
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
GCS_BUCKET = "bqx-ml-v3-models"
EMBARGO_INTERVALS = 30


def load_training_data(pair: str, horizon: int, sample_limit: int = 80000):
    """Load training data with regime features."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        reg_idx.interval_time,
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
        reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
        reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_slope_45 as bqx_slope_45,
        reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
        reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_slope_90 as bqx_slope_90,
        reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
        reg_bqx.reg_total_var_180 as bqx_tvar_180,
        base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,
        agg_bqx.agg_std_45 as regime_vol_45, agg_bqx.agg_std_90 as regime_vol_90,
        agg_bqx.agg_cv_45 as regime_cv_45, agg_bqx.agg_cv_90 as regime_cv_90,
        der_bqx.der_v1_45 as regime_der1_45, der_bqx.der_v1_90 as regime_der1_90,
        der_bqx.der_v2_45 as regime_der2_45, der_bqx.der_v2_90 as regime_der2_90,
        targets.target_bqx45_h{horizon}
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
    WHERE targets.target_bqx45_h{horizon} IS NOT NULL
    ORDER BY reg_idx.interval_time
    LIMIT {sample_limit}
    """

    return client.query(query).to_dataframe()


def create_walk_forward_splits(n_samples: int, n_folds: int = 5, embargo: int = EMBARGO_INTERVALS):
    """Create walk-forward time series splits with embargo gap."""
    fold_size = n_samples // (n_folds + 1)
    splits = []

    for i in range(n_folds):
        train_end = fold_size * (i + 1)
        val_start = train_end + embargo
        val_end = fold_size * (i + 2)

        if val_end > n_samples:
            val_end = n_samples
        if val_start >= val_end:
            continue

        splits.append({
            'train_idx': list(range(0, train_end)),
            'val_idx': list(range(val_start, val_end))
        })

    return splits


def train_full_pipeline(X, y, feature_names, regime_features, n_folds=5):
    """Train full calibrated stack pipeline with walk-forward OOF."""
    print("\n  Training full calibrated stack pipeline...")

    n_samples = len(X)
    splits = create_walk_forward_splits(n_samples, n_folds)
    print(f"  Created {len(splits)} walk-forward folds with {EMBARGO_INTERVALS} interval embargo")

    # Collect OOF predictions
    oof_lgb = np.zeros(n_samples)
    oof_xgb = np.zeros(n_samples)
    oof_cb = np.zeros(n_samples)
    oof_y = np.zeros(n_samples)
    oof_mask = np.zeros(n_samples, dtype=bool)
    oof_regime = np.zeros((n_samples, regime_features.shape[1] if regime_features is not None else 0))

    # Store models from last fold for final artifact
    final_models = {}

    for fold_idx, split in enumerate(splits):
        train_idx = split['train_idx']
        val_idx = split['val_idx']

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # LightGBM
        lgb_params = {
            'objective': 'binary', 'metric': 'binary_logloss',
            'num_leaves': 63, 'learning_rate': 0.03, 'feature_fraction': 0.6,
            'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1,
            'seed': 42, 'min_data_in_leaf': 50
        }
        lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
        lgb_model = lgb.train(lgb_params, lgb_train, num_boost_round=300)
        lgb_prob = lgb_model.predict(X_val)

        # XGBoost
        xgb_model = XGBClassifier(
            objective='binary:logistic', max_depth=5, learning_rate=0.03,
            subsample=0.8, colsample_bytree=0.6, random_state=42, verbosity=0,
            n_estimators=300, use_label_encoder=False, eval_metric='logloss'
        )
        xgb_model.fit(X_train, y_train)
        xgb_prob = xgb_model.predict_proba(X_val)[:, 1]

        # CatBoost
        cb_model = CatBoostClassifier(
            iterations=300, learning_rate=0.03, depth=5,
            loss_function='Logloss', verbose=False, random_seed=42
        )
        cb_model.fit(X_train, y_train, verbose=False)
        cb_prob = cb_model.predict_proba(X_val)[:, 1]

        # Store OOF predictions
        for i, idx in enumerate(val_idx):
            oof_lgb[idx] = lgb_prob[i]
            oof_xgb[idx] = xgb_prob[i]
            oof_cb[idx] = cb_prob[i]
            oof_y[idx] = y[idx]
            oof_mask[idx] = True
            if regime_features is not None:
                oof_regime[idx] = regime_features[idx]

        # Save models from last fold
        if fold_idx == len(splits) - 1:
            final_models = {
                'lightgbm': lgb_model,
                'xgboost': xgb_model,
                'catboost': cb_model
            }

        print(f"    Fold {fold_idx+1}: train={len(train_idx)}, val={len(val_idx)}")

    # Filter to OOF samples only
    oof_indices = np.where(oof_mask)[0]
    oof_lgb_valid = oof_lgb[oof_mask]
    oof_xgb_valid = oof_xgb[oof_mask]
    oof_cb_valid = oof_cb[oof_mask]
    oof_y_valid = oof_y[oof_mask]

    print(f"  OOF samples: {len(oof_indices)}")

    # Calibrate probabilities (Platt scaling)
    print("  Calibrating probabilities (Platt scaling)...")
    calibrators = {}

    # LightGBM calibrator
    lgb_calibrator = LogisticRegression(random_state=42, max_iter=1000)
    lgb_calibrator.fit(oof_lgb_valid.reshape(-1, 1), oof_y_valid)
    oof_lgb_cal = lgb_calibrator.predict_proba(oof_lgb_valid.reshape(-1, 1))[:, 1]
    calibrators['lightgbm'] = lgb_calibrator

    # XGBoost calibrator
    xgb_calibrator = LogisticRegression(random_state=42, max_iter=1000)
    xgb_calibrator.fit(oof_xgb_valid.reshape(-1, 1), oof_y_valid)
    oof_xgb_cal = xgb_calibrator.predict_proba(oof_xgb_valid.reshape(-1, 1))[:, 1]
    calibrators['xgboost'] = xgb_calibrator

    # CatBoost calibrator
    cb_calibrator = LogisticRegression(random_state=42, max_iter=1000)
    cb_calibrator.fit(oof_cb_valid.reshape(-1, 1), oof_y_valid)
    oof_cb_cal = cb_calibrator.predict_proba(oof_cb_valid.reshape(-1, 1))[:, 1]
    calibrators['catboost'] = cb_calibrator

    # Train meta-learner
    print("  Training meta-learner (LogReg + regime features)...")

    # Stack calibrated predictions
    if regime_features is not None:
        oof_regime_valid = oof_regime[oof_mask]
        meta_features = np.column_stack([oof_lgb_cal, oof_xgb_cal, oof_cb_cal, oof_regime_valid])
    else:
        meta_features = np.column_stack([oof_lgb_cal, oof_xgb_cal, oof_cb_cal])

    meta_learner = LogisticRegression(random_state=42, max_iter=1000)
    meta_learner.fit(meta_features, oof_y_valid)

    # Calculate final metrics
    meta_probs = meta_learner.predict_proba(meta_features)[:, 1]

    # Gating results
    thresholds = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    gating_results = {}

    for tau in thresholds:
        mask = meta_probs >= tau
        if mask.sum() > 0:
            predictions = (meta_probs[mask] >= 0.5).astype(int)
            accuracy = (predictions == oof_y_valid[mask]).mean()
            coverage = mask.sum() / len(meta_probs)
            gating_results[f'tau_{int(tau*100)}'] = {
                'accuracy': round(accuracy, 4),
                'coverage': round(coverage, 4),
                'n_signals': int(mask.sum())
            }
            print(f"    τ={tau}: accuracy={accuracy:.4f}, coverage={coverage:.4f}")

    return {
        'base_models': final_models,
        'calibrators': calibrators,
        'meta_learner': meta_learner,
        'oof_samples': len(oof_indices),
        'gating_results': gating_results
    }


def upload_to_gcs(local_path, gcs_path):
    """Upload file to GCS."""
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    return f"gs://{GCS_BUCKET}/{gcs_path}"


def main():
    pair = "eurusd"
    horizon = 15

    print("=" * 70)
    print("RE-SERIALIZE H15 WITH FULL CALIBRATED STACK PIPELINE")
    print("CE Directive: 20251210_0320")
    print("=" * 70)

    # Load data
    print("\nStep 1: Loading training data...")
    df = load_training_data(pair, horizon)
    print(f"  Loaded {len(df):,} rows")

    # Prepare features
    target_col = f'target_bqx45_h{horizon}'
    exclude_cols = [target_col, 'interval_time', 'pair']
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    # Identify regime features
    regime_cols = [c for c in feature_cols if any(x in c for x in ['regime_', 'vol_', 'der_'])]

    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values
    y = (df[target_col] > 0).astype(int).values

    regime_features = df[regime_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values if regime_cols else None

    print(f"  Features: {len(feature_cols)}")
    print(f"  Regime features: {len(regime_cols)}")
    print(f"  Samples: {len(X):,}")

    # Train full pipeline
    print("\nStep 2: Training full pipeline...")
    pipeline = train_full_pipeline(X, y, feature_cols, regime_features)

    # Prepare artifact
    print("\nStep 3: Creating artifact...")
    artifact = {
        # Core models
        'base_models': pipeline['base_models'],
        'calibrators': pipeline['calibrators'],
        'meta_learner': pipeline['meta_learner'],

        # Feature configuration
        'feature_names': feature_cols,
        'regime_features': regime_cols,

        # EA-003 compatibility placeholders
        'feature_views': None,
        'view_config': {
            'mode': 'shared',
            'views': None
        },

        # Metadata
        'metadata': {
            'pair': pair,
            'horizon': horizon,
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'enhancements': ['EA-001', 'EA-002'],
            'ensemble_size': 3,
            'threshold': 0.85,
            'accuracy': pipeline['gating_results'].get('tau_85', {}).get('accuracy', 0),
            'coverage': pipeline['gating_results'].get('tau_85', {}).get('coverage', 0),
            'oof_samples': pipeline['oof_samples'],
            'training_config': {
                'walk_forward_folds': 5,
                'embargo_intervals': EMBARGO_INTERVALS,
                'calibration_method': 'platt'
            },
            'gating_results': pipeline['gating_results']
        }
    }

    # Save locally
    print("\nStep 4: Saving model artifact...")
    local_dir = f"/home/micha/bqx_ml_v3/models/{pair}"
    os.makedirs(local_dir, exist_ok=True)
    local_path = f"{local_dir}/h{horizon}_ensemble_v2.joblib"
    joblib.dump(artifact, local_path)
    file_size = os.path.getsize(local_path) / (1024 * 1024)
    print(f"  Local: {local_path} ({file_size:.2f} MiB)")

    # Upload to GCS
    print("\nStep 5: Uploading to GCS...")
    gcs_path = f"models/{pair}/h{horizon}_ensemble_v2.joblib"
    gcs_uri = upload_to_gcs(local_path, gcs_path)
    print(f"  GCS: {gcs_uri}")

    # Summary
    print("\n" + "=" * 70)
    print("RE-SERIALIZATION COMPLETE")
    print("=" * 70)
    print(f"  Artifact: h{horizon}_ensemble_v2.joblib")
    print(f"  Version: 2.0.0")
    print(f"  Base models: {list(artifact['base_models'].keys())}")
    print(f"  Calibrators: {list(artifact['calibrators'].keys())}")
    print(f"  Meta-learner: {type(artifact['meta_learner']).__name__}")
    print(f"  Features: {len(feature_cols)}")
    print(f"  Regime features: {len(regime_cols)}")
    print(f"  OOF samples: {pipeline['oof_samples']}")
    print(f"  τ=0.85 accuracy: {artifact['metadata']['accuracy']}")
    print(f"  τ=0.85 coverage: {artifact['metadata']['coverage']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
