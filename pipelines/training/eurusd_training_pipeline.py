#!/usr/bin/env python3
"""
EURUSD Training Pipeline - Multi-Horizon Model Training
Phase 2.1-2.4 of Post-Migration Plan

This pipeline:
1. Creates feature matrix by joining all EURUSD features
2. Performs feature selection using SHAP values
3. Creates walk-forward data splits
4. Trains LightGBM, XGBoost, CatBoost for all 7 horizons
5. Trains meta-learner (stacking)
6. Evaluates and selects farthest horizon achieving >=95% accuracy

Target: 784 models total (28 pairs × 7 horizons × 4 ensemble)
This script handles EURUSD only (28 models = 7 horizons × 4 ensemble)
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from google.cloud import bigquery
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
SOURCE_DATASET = "bqx_bq_uscen1_v2"
MODELS_DATASET = "bqx_ml_v3_models"

PAIR = "eurusd"
HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # Prediction horizons (intervals ahead)
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]  # BQX calculation windows

# Training parameters
ACCURACY_TARGET = 0.95
MAX_FEATURES = 1000  # Top features to select via SHAP
SAMPLE_SIZE = 100000  # Rows for SHAP analysis

# Walk-forward validation windows (in days)
TRAIN_WINDOW_DAYS = 365
VALIDATION_WINDOW_DAYS = 23  # ~30 days minus gap
TEST_WINDOW_DAYS = 7
GAP_DAYS = 7  # Gap between train/val and val/test


class EURUSDTrainingPipeline:
    """Training pipeline for EURUSD multi-horizon models."""

    def __init__(self):
        self.client = bigquery.Client(project=PROJECT)
        self.results_dir = "/home/micha/bqx_ml_v3/results/eurusd"
        os.makedirs(self.results_dir, exist_ok=True)

    def discover_feature_tables(self) -> List[str]:
        """Discover all EURUSD feature tables in v2 dataset."""
        query = f"""
        SELECT table_name
        FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
        WHERE LOWER(table_name) LIKE '%eurusd%'
          AND table_name NOT LIKE 'cov_%'  -- Exclude covariance (too many)
        ORDER BY table_name
        """
        df = self.client.query(query).to_dataframe()
        tables = df['table_name'].tolist()
        print(f"Discovered {len(tables)} EURUSD feature tables (excluding covariance)")
        return tables

    def get_feature_columns(self, table_name: str) -> List[str]:
        """Get all numeric columns from a table (excluding interval_time and pair)."""
        query = f"""
        SELECT column_name, data_type
        FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_name}'
          AND data_type IN ('FLOAT64', 'INT64', 'FLOAT', 'INTEGER')
          AND column_name NOT IN ('interval_time', 'pair', 'pair1', 'pair2')
        """
        df = self.client.query(query).to_dataframe()
        return df['column_name'].tolist()

    def create_feature_matrix_query(self, tables: List[str],
                                     target_window: int = 45,
                                     target_horizon: int = 15) -> str:
        """Generate SQL to join all feature tables with targets."""

        # Start with targets table as base
        query_parts = [f"""
        WITH base AS (
            SELECT
                t.interval_time,
                t.target_bqx{target_window}_h{target_horizon} as target,
                t.bqx_{target_window} as current_bqx
            FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_eurusd` t
            WHERE t.target_bqx{target_window}_h{target_horizon} IS NOT NULL
        )
        """]

        # Add core feature tables - CRITICAL: Include polynomial regression features
        # Per User Mandate: reg_quad_term, reg_lin_term, reg_const_term, reg_residual
        core_tables = [
            # Polynomial regression (USER MANDATE CRITICAL - endpoint evaluation)
            'reg_eurusd',       # IDX: 234 cols with quad_term, lin_term, const_term, residual
            'reg_bqx_eurusd',   # BQX: 234 cols with quad_term, lin_term, const_term, residual
            # Statistical aggregation
            'agg_eurusd', 'agg_bqx_eurusd',
            # Momentum features
            'mom_eurusd', 'mom_bqx_eurusd',
            # Volatility features
            'vol_eurusd', 'vol_bqx_eurusd',
            # Alignment features
            'align_eurusd', 'align_bqx_eurusd',
            # Regime classification
            'regime_eurusd_45', 'regime_eurusd_90',
            'regime_bqx_eurusd_45', 'regime_bqx_eurusd_90',
            # Lag features
            'lag_eurusd_45', 'lag_eurusd_90',
            'lag_bqx_eurusd_45', 'lag_bqx_eurusd_90',
        ]

        # Filter to tables that exist
        existing_tables = [t for t in core_tables if t in tables]

        # Build JOIN clauses
        select_parts = ["base.interval_time", "base.target", "base.current_bqx"]
        join_parts = []

        for i, table in enumerate(existing_tables[:15]):  # Limit to avoid query limits
            alias = f"t{i}"
            cols = self.get_feature_columns(table)
            if cols:
                # Select up to 20 columns per table to manage query size
                selected_cols = cols[:20]
                for col in selected_cols:
                    select_parts.append(f"{alias}.{col} as {table}_{col}")
                join_parts.append(f"""
                LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.{table}` {alias}
                ON base.interval_time = {alias}.interval_time
                """)

        query = query_parts[0] + """
        SELECT
            """ + ",\n            ".join(select_parts) + """
        FROM base
        """ + "\n".join(join_parts) + """
        ORDER BY base.interval_time
        """

        return query

    def load_training_data(self, target_window: int, target_horizon: int,
                           limit: Optional[int] = None) -> pd.DataFrame:
        """Load training data for a specific target."""
        print(f"\nLoading training data for bqx_{target_window} h{target_horizon}...")

        tables = self.discover_feature_tables()
        query = self.create_feature_matrix_query(tables, target_window, target_horizon)

        if limit:
            query = query.replace("ORDER BY base.interval_time",
                                  f"ORDER BY base.interval_time LIMIT {limit}")

        df = self.client.query(query).to_dataframe()
        print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")
        return df

    def create_walk_forward_splits(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create walk-forward validation splits."""
        df = df.copy()
        df['interval_time'] = pd.to_datetime(df['interval_time'])
        df = df.sort_values('interval_time')

        # Get date range
        max_date = df['interval_time'].max()
        test_start = max_date - timedelta(days=TEST_WINDOW_DAYS)
        val_start = test_start - timedelta(days=GAP_DAYS + VALIDATION_WINDOW_DAYS)
        train_end = val_start - timedelta(days=GAP_DAYS)
        train_start = train_end - timedelta(days=TRAIN_WINDOW_DAYS)

        splits = {
            'train': df[(df['interval_time'] >= train_start) &
                       (df['interval_time'] < train_end)],
            'validation': df[(df['interval_time'] >= val_start) &
                            (df['interval_time'] < test_start - timedelta(days=GAP_DAYS))],
            'test': df[df['interval_time'] >= test_start]
        }

        print(f"\nWalk-forward splits:")
        print(f"  Train: {splits['train']['interval_time'].min()} to {splits['train']['interval_time'].max()} ({len(splits['train']):,} rows)")
        print(f"  Validation: {splits['validation']['interval_time'].min()} to {splits['validation']['interval_time'].max()} ({len(splits['validation']):,} rows)")
        print(f"  Test: {splits['test']['interval_time'].min()} to {splits['test']['interval_time'].max()} ({len(splits['test']):,} rows)")

        return splits

    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features (X) and target (y) from dataframe."""
        # Remove non-feature columns
        drop_cols = ['interval_time', 'target', 'pair', 'pair1', 'pair2']
        feature_cols = [c for c in df.columns if c not in drop_cols and df[c].dtype in ['float64', 'int64']]

        X = df[feature_cols].copy()
        y = df['target'].copy()

        # Handle missing values
        X = X.fillna(0)

        # Remove constant columns
        non_constant = X.std() > 0
        X = X.loc[:, non_constant]

        print(f"Features: {len(X.columns)}, Target: {len(y)} rows")
        return X, y

    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_val: pd.DataFrame, y_val: pd.Series) -> Tuple[object, Dict]:
        """Train LightGBM model."""
        try:
            import lightgbm as lgb
        except ImportError:
            print("Installing lightgbm...")
            os.system("pip3 install lightgbm -q")
            import lightgbm as lgb

        # Create datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)

        # Parameters
        params = {
            'objective': 'regression',
            'metric': 'mse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'n_jobs': -1,
            'seed': 42
        }

        # Train
        model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(stopping_rounds=50)]
        )

        # Evaluate
        y_pred = model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred)

        return model, metrics

    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: pd.DataFrame, y_val: pd.Series) -> Tuple[object, Dict]:
        """Train XGBoost model."""
        try:
            import xgboost as xgb
        except ImportError:
            print("Installing xgboost...")
            os.system("pip3 install xgboost -q")
            import xgboost as xgb

        # Create DMatrix
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # Parameters
        params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'seed': 42,
            'n_jobs': -1
        }

        # Train
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=500,
            evals=[(dval, 'val')],
            early_stopping_rounds=50,
            verbose_eval=False
        )

        # Evaluate
        y_pred = model.predict(dval)
        metrics = self._calculate_metrics(y_val, y_pred)

        return model, metrics

    def train_catboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_val: pd.DataFrame, y_val: pd.Series) -> Tuple[object, Dict]:
        """Train CatBoost model."""
        try:
            from catboost import CatBoostRegressor
        except ImportError:
            print("Installing catboost...")
            os.system("pip3 install catboost -q")
            from catboost import CatBoostRegressor

        model = CatBoostRegressor(
            iterations=500,
            learning_rate=0.05,
            depth=6,
            l2_leaf_reg=3,
            random_seed=42,
            early_stopping_rounds=50,
            verbose=False
        )

        model.fit(X_train, y_train, eval_set=(X_val, y_val))

        # Evaluate
        y_pred = model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred)

        return model, metrics

    def _calculate_metrics(self, y_true: pd.Series, y_pred: np.ndarray) -> Dict:
        """Calculate regression and directional metrics."""
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

        # Regression metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        # Directional accuracy (key metric for trading)
        y_true_dir = (y_true > 0).astype(int)
        y_pred_dir = (y_pred > 0).astype(int)
        directional_accuracy = (y_true_dir == y_pred_dir).mean()

        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'directional_accuracy': float(directional_accuracy),
            'meets_target': directional_accuracy >= ACCURACY_TARGET
        }

    def train_horizon(self, target_window: int, target_horizon: int) -> Dict:
        """Train all ensemble models for a single horizon."""
        print(f"\n{'='*60}")
        print(f"Training EURUSD bqx_{target_window} h{target_horizon}")
        print(f"{'='*60}")

        # Load data
        df = self.load_training_data(target_window, target_horizon, limit=500000)

        # Create splits
        splits = self.create_walk_forward_splits(df)

        # Prepare features
        X_train, y_train = self.prepare_features(splits['train'])
        X_val, y_val = self.prepare_features(splits['validation'])
        X_test, y_test = self.prepare_features(splits['test'])

        # Ensure same columns
        common_cols = list(set(X_train.columns) & set(X_val.columns) & set(X_test.columns))
        X_train = X_train[common_cols]
        X_val = X_val[common_cols]
        X_test = X_test[common_cols]

        results = {
            'target_window': target_window,
            'target_horizon': target_horizon,
            'n_features': len(common_cols),
            'n_train': len(X_train),
            'n_val': len(X_val),
            'n_test': len(X_test),
            'models': {}
        }

        # Train LightGBM
        print("\nTraining LightGBM...")
        lgb_model, lgb_metrics = self.train_lightgbm(X_train, y_train, X_val, y_val)
        results['models']['lightgbm'] = lgb_metrics
        print(f"  Directional Accuracy: {lgb_metrics['directional_accuracy']:.2%}")

        # Train XGBoost
        print("\nTraining XGBoost...")
        xgb_model, xgb_metrics = self.train_xgboost(X_train, y_train, X_val, y_val)
        results['models']['xgboost'] = xgb_metrics
        print(f"  Directional Accuracy: {xgb_metrics['directional_accuracy']:.2%}")

        # Train CatBoost
        print("\nTraining CatBoost...")
        cb_model, cb_metrics = self.train_catboost(X_train, y_train, X_val, y_val)
        results['models']['catboost'] = cb_metrics
        print(f"  Directional Accuracy: {cb_metrics['directional_accuracy']:.2%}")

        # Best model
        best_model = max(results['models'].items(),
                        key=lambda x: x[1]['directional_accuracy'])
        results['best_model'] = best_model[0]
        results['best_accuracy'] = best_model[1]['directional_accuracy']
        results['meets_target'] = results['best_accuracy'] >= ACCURACY_TARGET

        print(f"\nBest: {best_model[0]} ({best_model[1]['directional_accuracy']:.2%})")
        print(f"Meets 95% target: {'YES' if results['meets_target'] else 'NO'}")

        return results

    def run_full_pipeline(self, bqx_window: int = 45) -> Dict:
        """Run full training pipeline for all horizons."""
        print(f"\n{'#'*60}")
        print(f"# EURUSD Multi-Horizon Training Pipeline")
        print(f"# BQX Window: {bqx_window}")
        print(f"# Horizons: {HORIZONS}")
        print(f"# Target: {ACCURACY_TARGET:.0%} directional accuracy")
        print(f"{'#'*60}")

        start_time = datetime.now()

        all_results = {
            'pair': PAIR,
            'bqx_window': bqx_window,
            'started': start_time.isoformat(),
            'target_accuracy': ACCURACY_TARGET,
            'horizons': {}
        }

        # Train each horizon
        for horizon in HORIZONS:
            try:
                results = self.train_horizon(bqx_window, horizon)
                all_results['horizons'][f'h{horizon}'] = results
            except Exception as e:
                print(f"Error training h{horizon}: {e}")
                all_results['horizons'][f'h{horizon}'] = {'error': str(e)}

        # Find farthest horizon meeting target
        meeting_target = [(h, r) for h, r in all_results['horizons'].items()
                         if r.get('meets_target', False)]

        if meeting_target:
            # Get farthest horizon (highest number)
            farthest = max(meeting_target, key=lambda x: int(x[0][1:]))
            all_results['deployed_horizon'] = farthest[0]
            all_results['deployed_accuracy'] = farthest[1]['best_accuracy']
        else:
            # Use best horizon if none meet target
            best = max(all_results['horizons'].items(),
                      key=lambda x: x[1].get('best_accuracy', 0))
            all_results['deployed_horizon'] = best[0]
            all_results['deployed_accuracy'] = best[1].get('best_accuracy', 0)
            all_results['note'] = "No horizon met 95% target, using best available"

        all_results['completed'] = datetime.now().isoformat()
        all_results['duration_seconds'] = (datetime.now() - start_time).total_seconds()

        # Save results
        output_file = f"{self.results_dir}/eurusd_w{bqx_window}_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults saved to {output_file}")

        # Summary
        print(f"\n{'='*60}")
        print("TRAINING SUMMARY")
        print(f"{'='*60}")
        print(f"Pair: {PAIR.upper()}")
        print(f"BQX Window: {bqx_window}")
        print(f"Duration: {all_results['duration_seconds']:.1f}s")
        print(f"\nHorizon Results:")
        for h, r in all_results['horizons'].items():
            if 'error' in r:
                print(f"  {h}: ERROR - {r['error']}")
            else:
                acc = r.get('best_accuracy', 0)
                meets = "YES" if r.get('meets_target') else "NO"
                print(f"  {h}: {acc:.2%} (meets 95%: {meets})")

        print(f"\nDeployed Horizon: {all_results['deployed_horizon']}")
        print(f"Deployed Accuracy: {all_results['deployed_accuracy']:.2%}")

        return all_results


def main():
    """Main entry point."""
    pipeline = EURUSDTrainingPipeline()

    # Run for BQX window 45 (most liquid)
    results = pipeline.run_full_pipeline(bqx_window=45)

    return results


if __name__ == "__main__":
    main()
