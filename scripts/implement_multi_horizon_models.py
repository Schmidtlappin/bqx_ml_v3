#!/usr/bin/env python3
"""
Implementation of Multi-Horizon BQX Prediction Models
Uses existing BQX features to predict multiple future horizons
Focuses on trading-relevant intervals: 15, 30, 45, 60, 75, 90, 105
"""

import os
import pickle
import pandas as pd
import numpy as np
from google.cloud import bigquery, storage, aiplatform
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT_ID = 'bqx-ml'  # Using accessible project
DATASET_ID = 'bqx_ml_v3_features'  # Correct dataset name
BUCKET_NAME = 'bqx-ml-vertex-models'
REGION = 'us-central1'

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
aiplatform.init(project=PROJECT_ID, location=REGION)

# Multi-Horizon Configuration
FEATURE_WINDOWS = [45, 90]  # BQX windows to use as features (start with best 2)
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # Future intervals to predict

# Critical models for real-time deployment
CRITICAL_PAIRS = ['EUR_USD', 'GBP_USD', 'USD_JPY']

# Prebuilt sklearn container for deployment
SKLEARN_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"

class MultiHorizonBQXPredictor:
    """
    Multi-horizon prediction system using existing BQX features
    """

    def __init__(self, pair, bqx_window):
        self.pair = pair
        self.bqx_window = bqx_window
        self.models = {}
        self.feature_columns = None
        self.performance_metrics = {}

    def load_data(self):
        """
        Load data with BQX features and multiple horizon targets
        """
        print(f"\n📥 Loading data for {self.pair} using bqx_{self.bqx_window} features...")

        # Build query with multiple LEAD targets for different horizons
        horizon_targets = ', '.join([
            f"LEAD(bqx_{self.bqx_window}, {h}) OVER (ORDER BY timestamp) as target_h{h}"
            for h in PREDICTION_HORIZONS
        ])

        query = f"""
        WITH features AS (
            SELECT
                timestamp,
                -- Current BQX values
                bqx_45,
                bqx_90,
                bqx_180,
                bqx_360,
                bqx_720,
                bqx_1440,
                bqx_2880,

                -- Lagged BQX values for momentum
                LAG(bqx_{self.bqx_window}, 1) OVER (ORDER BY timestamp) as bqx_lag_1,
                LAG(bqx_{self.bqx_window}, 2) OVER (ORDER BY timestamp) as bqx_lag_2,
                LAG(bqx_{self.bqx_window}, 3) OVER (ORDER BY timestamp) as bqx_lag_3,
                LAG(bqx_{self.bqx_window}, 5) OVER (ORDER BY timestamp) as bqx_lag_5,
                LAG(bqx_{self.bqx_window}, 10) OVER (ORDER BY timestamp) as bqx_lag_10,

                -- IDX technical indicators (if using dual table)
                idx_rsi,
                idx_macd,
                idx_bollinger_upper,
                idx_bollinger_lower,
                idx_stochastic,
                idx_williams_r,
                idx_atr,
                idx_obv,
                idx_ema_12,
                idx_ema_26,
                idx_sma_50,
                idx_sma_200,
                idx_momentum,
                idx_roc,

                -- Multiple horizon targets
                {horizon_targets}

            FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair.lower()}_features_dual`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 DAY)
            ORDER BY timestamp DESC
            LIMIT 30000
        )
        SELECT * FROM features
        WHERE target_h{PREDICTION_HORIZONS[-1]} IS NOT NULL
        """

        try:
            df = bq_client.query(query).to_dataframe()
            print(f"  ✅ Loaded {len(df)} rows with {len(df.columns)} columns")

            # Engineer additional features
            df = self._engineer_features(df)

            return df

        except Exception as e:
            print(f"  ❌ Failed to load data: {e}")
            return None

    def _engineer_features(self, df):
        """
        Engineer additional features from BQX values
        """
        print(f"  🔧 Engineering multi-horizon features...")

        # BQX momentum features (different speeds)
        df[f'bqx_{self.bqx_window}_momentum_fast'] = df[f'bqx_{self.bqx_window}'] - df[f'bqx_{self.bqx_window}'].shift(5)
        df[f'bqx_{self.bqx_window}_momentum_medium'] = df[f'bqx_{self.bqx_window}'] - df[f'bqx_{self.bqx_window}'].shift(10)
        df[f'bqx_{self.bqx_window}_momentum_slow'] = df[f'bqx_{self.bqx_window}'] - df[f'bqx_{self.bqx_window}'].shift(20)

        # BQX volatility
        df[f'bqx_{self.bqx_window}_volatility'] = df[f'bqx_{self.bqx_window}'].rolling(window=20).std()

        # Relative strength between different BQX windows
        if 'bqx_45' in df.columns and 'bqx_90' in df.columns:
            df['bqx_45_90_ratio'] = df['bqx_45'] / df['bqx_90']

        if 'bqx_90' in df.columns and 'bqx_180' in df.columns:
            df['bqx_90_180_ratio'] = df['bqx_90'] / df['bqx_180']

        # Time-based features (important for forex)
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_london_session'] = ((df['hour'] >= 8) & (df['hour'] <= 16)).astype(int)
        df['is_ny_session'] = ((df['hour'] >= 13) & (df['hour'] <= 21)).astype(int)
        df['is_asia_session'] = ((df['hour'] >= 23) | (df['hour'] <= 7)).astype(int)
        df['is_session_overlap'] = ((df['hour'] >= 13) & (df['hour'] <= 16)).astype(int)

        # Drop NaN rows
        df = df.dropna()

        print(f"    ✅ Engineered features, final shape: {df.shape}")
        return df

    def train_multi_horizon_models(self, df):
        """
        Train separate models for each prediction horizon
        """
        print(f"\n🎯 Training multi-horizon models for {self.pair} bqx_{self.bqx_window}...")

        # Define feature columns (exclude targets and metadata)
        exclude_cols = ['timestamp'] + [f'target_h{h}' for h in PREDICTION_HORIZONS]
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]

        X = df[self.feature_columns]

        # Train model for each horizon
        for horizon in PREDICTION_HORIZONS:
            print(f"\n  🔄 Training model for {horizon}-interval horizon...")

            target_col = f'target_h{horizon}'
            if target_col not in df.columns:
                print(f"    ⚠️ Target column {target_col} not found, skipping...")
                continue

            y = df[target_col]

            # Time series split (no shuffle for time series!)
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # Choose model based on horizon
            if horizon <= 30:
                # Lighter model for short horizons (speed matters)
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=20,
                    max_features='sqrt',
                    n_jobs=-1,
                    random_state=42
                )
            elif horizon <= 60:
                # Medium complexity for medium horizons
                model = RandomForestRegressor(
                    n_estimators=150,
                    max_depth=12,
                    min_samples_split=15,
                    max_features='sqrt',
                    n_jobs=-1,
                    random_state=42
                )
            else:
                # More complex for longer horizons
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=8,
                    learning_rate=0.1,
                    subsample=0.8,
                    random_state=42
                )

            # Train the model
            model.fit(X_train, y_train)

            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)

            # Predictions for additional metrics
            y_pred = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)

            # Directional accuracy (more important for trading)
            y_test_direction = (y_test > y_test.iloc[0]).astype(int)
            y_pred_direction = (y_pred > y_test.iloc[0]).astype(int)
            directional_accuracy = np.mean(y_test_direction == y_pred_direction)

            # Store model and metrics
            model_name = f"{self.pair}_bqx{self.bqx_window}_h{horizon}"
            self.models[horizon] = model
            self.performance_metrics[horizon] = {
                'train_r2': train_score,
                'test_r2': test_score,
                'rmse': rmse,
                'mae': mae,
                'directional_accuracy': directional_accuracy
            }

            print(f"    📊 Model: {model_name}")
            print(f"       Training R²: {train_score:.4f}")
            print(f"       Testing R²: {test_score:.4f}")
            print(f"       RMSE: {rmse:.4f}")
            print(f"       MAE: {mae:.4f}")
            print(f"       Directional Accuracy: {directional_accuracy:.2%}")

            # Feature importance for shortest and longest horizons
            if horizon in [15, 105] and hasattr(model, 'feature_importances_'):
                top_features = pd.DataFrame({
                    'feature': self.feature_columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False).head(5)

                print(f"       Top 5 features:")
                for _, row in top_features.iterrows():
                    print(f"         • {row['feature']}: {row['importance']:.4f}")

    def save_models(self):
        """
        Save trained models to GCS
        """
        print(f"\n💾 Saving multi-horizon models for {self.pair} bqx_{self.bqx_window}...")

        for horizon, model in self.models.items():
            model_name = f"{self.pair}_bqx{self.bqx_window}_h{horizon}"
            model_dir = f"/tmp/{model_name}"
            os.makedirs(model_dir, exist_ok=True)

            # Save model
            with open(f"{model_dir}/model.pkl", 'wb') as f:
                pickle.dump(model, f, protocol=4)

            # Save feature columns
            with open(f"{model_dir}/features.pkl", 'wb') as f:
                pickle.dump(self.feature_columns, f)

            # Save metadata
            metadata = {
                'pair': self.pair,
                'bqx_window': self.bqx_window,
                'horizon': horizon,
                'metrics': self.performance_metrics[horizon],
                'trained_at': datetime.now().isoformat()
            }
            with open(f"{model_dir}/metadata.json", 'w') as f:
                import json
                json.dump(metadata, f, indent=2)

            # Upload to GCS
            bucket = storage_client.bucket(BUCKET_NAME)
            for file in ['model.pkl', 'features.pkl', 'metadata.json']:
                blob = bucket.blob(f"{model_name}/{file}")
                blob.upload_from_filename(f"{model_dir}/{file}")

            print(f"  ✅ Saved {model_name} to gs://{BUCKET_NAME}/{model_name}/")

    def deploy_critical_models(self):
        """
        Deploy critical short-horizon models to Vertex AI endpoints
        """
        critical_horizons = [15, 30, 60]  # Most trading-relevant

        if self.pair not in CRITICAL_PAIRS:
            print(f"  ℹ️ {self.pair} not in critical pairs, skipping endpoint deployment")
            return

        print(f"\n🚀 Deploying critical models for {self.pair} bqx_{self.bqx_window}...")

        for horizon in critical_horizons:
            if horizon not in self.models:
                continue

            model_name = f"{self.pair}_bqx{self.bqx_window}_h{horizon}"

            # Only deploy if performance meets threshold
            if self.performance_metrics[horizon]['test_r2'] < 0.20:
                print(f"  ⚠️ {model_name} R² too low ({self.performance_metrics[horizon]['test_r2']:.4f}), skipping deployment")
                continue

            try:
                print(f"  📦 Deploying {model_name} to Vertex AI...")

                # Upload model to Vertex AI
                vertex_model = aiplatform.Model.upload(
                    display_name=model_name,
                    artifact_uri=f"gs://{BUCKET_NAME}/{model_name}/",
                    serving_container_image_uri=SKLEARN_CONTAINER,
                    sync=False
                )

                print(f"    ✅ Model uploaded: {model_name}")

                # For critical models only, create endpoint
                if horizon == 30:  # Deploy only 30-interval as endpoint initially
                    endpoint = aiplatform.Endpoint.create(
                        display_name=f"{model_name}-endpoint",
                        sync=False
                    )

                    endpoint.deploy(
                        model=vertex_model,
                        machine_type="n1-standard-2",
                        min_replica_count=1,
                        max_replica_count=2,
                        traffic_percentage=100,
                        sync=False
                    )

                    print(f"    ✅ Endpoint deployment initiated for {model_name}")

            except Exception as e:
                print(f"    ❌ Deployment failed: {e}")


def main():
    """
    Main execution for multi-horizon model implementation
    """
    print("="*80)
    print("🎯 MULTI-HORIZON BQX PREDICTION MODEL IMPLEMENTATION")
    print("="*80)
    print(f"📅 {datetime.now().isoformat()}")
    print(f"🔧 Feature Windows: {FEATURE_WINDOWS}")
    print(f"🎯 Prediction Horizons: {PREDICTION_HORIZONS}")
    print(f"📊 Critical Pairs: {CRITICAL_PAIRS}")
    print("="*80)

    # Track overall results
    all_results = []

    # Process each pair and window combination
    for pair in CRITICAL_PAIRS:
        for bqx_window in FEATURE_WINDOWS:
            print(f"\n{'='*60}")
            print(f"Processing {pair} with bqx_{bqx_window} features")
            print(f"{'='*60}")

            # Initialize predictor
            predictor = MultiHorizonBQXPredictor(pair, bqx_window)

            # Load data
            df = predictor.load_data()
            if df is None:
                print(f"  ⚠️ Skipping {pair} bqx_{bqx_window} due to data loading failure")
                continue

            # Train models
            predictor.train_multi_horizon_models(df)

            # Save models
            predictor.save_models()

            # Deploy critical models
            predictor.deploy_critical_models()

            # Store results
            for horizon, metrics in predictor.performance_metrics.items():
                all_results.append({
                    'pair': pair,
                    'bqx_window': bqx_window,
                    'horizon': horizon,
                    **metrics
                })

    # Summary report
    print("\n" + "="*80)
    print("📊 MULTI-HORIZON MODEL SUMMARY")
    print("="*80)

    results_df = pd.DataFrame(all_results)

    # Best models by horizon
    print("\n🏆 Best Models by Horizon:")
    for horizon in PREDICTION_HORIZONS:
        horizon_results = results_df[results_df['horizon'] == horizon]
        if not horizon_results.empty:
            best = horizon_results.loc[horizon_results['test_r2'].idxmax()]
            print(f"  h{horizon}: {best['pair']}_bqx{best['bqx_window']} (R²={best['test_r2']:.4f}, Dir={best['directional_accuracy']:.2%})")

    # Average performance by horizon
    print("\n📈 Average Performance by Horizon:")
    avg_by_horizon = results_df.groupby('horizon')[['test_r2', 'directional_accuracy']].mean()
    print(avg_by_horizon)

    # Models ready for deployment
    print("\n✅ Models Ready for Production (R² > 0.25):")
    good_models = results_df[results_df['test_r2'] > 0.25]
    for _, row in good_models.iterrows():
        print(f"  {row['pair']}_bqx{row['bqx_window']}_h{row['horizon']}: R²={row['test_r2']:.4f}")

    print(f"\n🏁 Multi-horizon implementation completed at {datetime.now().isoformat()}")
    print(f"📦 Total models trained: {len(all_results)}")
    print(f"✅ Models meeting threshold: {len(good_models)}")

    # Save results to CSV for analysis
    results_df.to_csv('/tmp/multi_horizon_results.csv', index=False)
    print(f"📊 Results saved to /tmp/multi_horizon_results.csv")


if __name__ == "__main__":
    main()