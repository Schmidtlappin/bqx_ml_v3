#!/usr/bin/env python3
"""
Train and Save EURUSD h15 Model to GCS
GATE_3 Requirement: Model artifacts saved to GCS

Trains the calibrated 3-model ensemble and saves to:
- Local: /models/eurusd/h15_ensemble.joblib
- GCS: gs://bqx-ml-v3-models/models/eurusd/h15_ensemble.joblib
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


def load_training_data(pair: str, horizon: int, sample_limit: int = 80000):
    """Load training data."""
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


def train_ensemble(X, y, feature_names):
    """Train the 3-model ensemble."""
    models = {}

    # LightGBM
    print("  Training LightGBM...")
    lgb_params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 63, 'learning_rate': 0.03, 'feature_fraction': 0.6,
        'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1,
        'seed': 42, 'min_data_in_leaf': 50
    }
    lgb_train = lgb.Dataset(X, label=y, feature_name=feature_names)
    models['lightgbm'] = lgb.train(lgb_params, lgb_train, num_boost_round=300)

    # XGBoost
    print("  Training XGBoost...")
    models['xgboost'] = XGBClassifier(
        objective='binary:logistic', max_depth=5, learning_rate=0.03,
        subsample=0.8, colsample_bytree=0.6, random_state=42, verbosity=0,
        n_estimators=300, use_label_encoder=False, eval_metric='logloss'
    )
    models['xgboost'].fit(X, y)

    # CatBoost
    print("  Training CatBoost...")
    models['catboost'] = CatBoostClassifier(
        iterations=300, learning_rate=0.03, depth=5,
        loss_function='Logloss', verbose=False, random_seed=42
    )
    models['catboost'].fit(X, y, verbose=False)

    return models


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
    print("TRAIN AND SAVE EURUSD h15 ENSEMBLE")
    print("GATE_3 Requirement: Model artifacts to GCS")
    print("=" * 70)

    # Load data
    print("\nStep 1: Loading training data...")
    df = load_training_data(pair, horizon)
    print(f"  Loaded {len(df):,} rows")

    # Prepare features
    target_col = f'target_bqx45_h{horizon}'
    feature_cols = [c for c in df.columns if c not in [target_col, 'interval_time', 'pair']]

    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values
    y = (df[target_col] > 0).astype(int).values

    print(f"  Features: {len(feature_cols)}")
    print(f"  Samples: {len(X):,}")

    # Train models
    print("\nStep 2: Training ensemble...")
    models = train_ensemble(X, y, feature_cols)
    print("  Ensemble trained: LightGBM, XGBoost, CatBoost")

    # Prepare model artifact
    artifact = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'feature_names': feature_cols,
        'models': models,
        'training_samples': len(X),
        'version': '1.0.0'
    }

    # Save locally
    print("\nStep 3: Saving model artifacts...")
    local_dir = f"/home/micha/bqx_ml_v3/models/{pair}"
    os.makedirs(local_dir, exist_ok=True)
    local_path = f"{local_dir}/h{horizon}_ensemble.joblib"
    joblib.dump(artifact, local_path)
    print(f"  Local: {local_path}")

    # Upload to GCS
    print("\nStep 4: Uploading to GCS...")
    gcs_path = f"models/{pair}/h{horizon}_ensemble.joblib"
    gcs_uri = upload_to_gcs(local_path, gcs_path)
    print(f"  GCS: {gcs_uri}")

    # Save metadata
    metadata = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'local_path': local_path,
        'gcs_uri': gcs_uri,
        'feature_count': len(feature_cols),
        'training_samples': len(X),
        'models': ['lightgbm', 'xgboost', 'catboost']
    }
    metadata_path = f"{local_dir}/h{horizon}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata: {metadata_path}")

    # Summary
    print("\n" + "=" * 70)
    print("MODEL SERIALIZATION COMPLETE")
    print("=" * 70)
    print(f"  Local: {local_path}")
    print(f"  GCS: {gcs_uri}")
    print(f"  Models: LightGBM, XGBoost, CatBoost")
    print(f"  Features: {len(feature_cols)}")
    print("\n  GATE_3 Requirement: Model artifacts to GCS - COMPLETE")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
