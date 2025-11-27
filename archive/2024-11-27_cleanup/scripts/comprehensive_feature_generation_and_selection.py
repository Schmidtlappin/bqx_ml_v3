#!/usr/bin/env python3
"""
Comprehensive Feature Generation and Selection for BQX ML V3
Generates ALL possible features from base data and selects the best ones.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import (
    SelectKBest, f_regression, mutual_info_regression,
    RFE, SelectFromModel, VarianceThreshold
)
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.linear_model import LassoCV
from google.cloud import bigquery
import logging
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'bqx-ml'
DATASET_ID = 'bqx_ml_v3_features'

class ComprehensiveFeatureGenerator:
    """Generates ALL possible features from base data."""

    def __init__(self, pair='EUR_USD'):
        self.pair = pair
        self.pair_name = pair.lower().replace('_', '')
        self.client = bigquery.Client(project=PROJECT_ID)

    def load_base_data(self):
        """Load base BQX and IDX data."""
        logger.info(f"Loading base data for {self.pair}...")

        # Load BQX data
        bqx_query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair_name}_bqx`
        ORDER BY interval_time DESC
        LIMIT 20000
        """

        # Load IDX data
        idx_query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair_name}_idx`
        ORDER BY interval_time DESC
        LIMIT 20000
        """

        try:
            bqx_df = self.client.query(bqx_query).to_dataframe()
            idx_df = self.client.query(idx_query).to_dataframe()

            # Merge on interval_time
            df = pd.merge(bqx_df, idx_df, on='interval_time', suffixes=('_bqx', '_idx'))
            df = df.sort_values('interval_time')

            logger.info(f"Loaded {len(df)} rows with {len(df.columns)} base columns")
            return df

        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            return None

    def generate_lag_features(self, df, column, lags=[1, 2, 3, 5, 10, 20, 30, 60, 120]):
        """Generate lag features for a column."""
        features = {}
        for lag in lags:
            features[f'{column}_lag_{lag}'] = df[column].shift(lag)
        return pd.DataFrame(features, index=df.index)

    def generate_rolling_features(self, df, column, windows=[5, 10, 20, 30, 60, 120]):
        """Generate rolling window statistics."""
        features = {}
        for window in windows:
            features[f'{column}_ma_{window}'] = df[column].rolling(window).mean()
            features[f'{column}_std_{window}'] = df[column].rolling(window).std()
            features[f'{column}_min_{window}'] = df[column].rolling(window).min()
            features[f'{column}_max_{window}'] = df[column].rolling(window).max()
            features[f'{column}_skew_{window}'] = df[column].rolling(window).skew()
            features[f'{column}_kurt_{window}'] = df[column].rolling(window).kurt()
        return pd.DataFrame(features, index=df.index)

    def generate_difference_features(self, df, column):
        """Generate difference features."""
        features = {}
        features[f'{column}_diff_1'] = df[column].diff(1)
        features[f'{column}_diff_2'] = df[column].diff(2)
        features[f'{column}_diff_5'] = df[column].diff(5)
        features[f'{column}_diff_10'] = df[column].diff(10)
        features[f'{column}_pct_change_1'] = df[column].pct_change(1)
        features[f'{column}_pct_change_5'] = df[column].pct_change(5)
        features[f'{column}_pct_change_10'] = df[column].pct_change(10)
        return pd.DataFrame(features, index=df.index)

    def generate_interaction_features(self, df, col1, col2):
        """Generate interaction features between two columns."""
        features = {}
        features[f'{col1}_x_{col2}'] = df[col1] * df[col2]
        features[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-10)
        features[f'{col1}_plus_{col2}'] = df[col1] + df[col2]
        features[f'{col1}_minus_{col2}'] = df[col1] - df[col2]
        return pd.DataFrame(features, index=df.index)

    def generate_all_features(self):
        """Generate ALL possible features."""
        logger.info("Generating comprehensive feature set...")

        # Load base data
        df = self.load_base_data()
        if df is None:
            return None

        all_features = []
        feature_count = 0

        # BQX columns
        bqx_cols = [col for col in df.columns if 'bqx_' in col and 'target' not in col]

        # For each BQX column
        for col in bqx_cols:
            if col in df.columns:
                # Lag features (9 lags each)
                lag_df = self.generate_lag_features(df, col)
                all_features.append(lag_df)
                feature_count += len(lag_df.columns)

                # Rolling features (6 windows x 6 stats = 36 features)
                roll_df = self.generate_rolling_features(df, col)
                all_features.append(roll_df)
                feature_count += len(roll_df.columns)

                # Difference features (7 features)
                diff_df = self.generate_difference_features(df, col)
                all_features.append(diff_df)
                feature_count += len(diff_df.columns)

        # Generate interactions between BQX columns
        for i, col1 in enumerate(bqx_cols):
            for col2 in bqx_cols[i+1:]:
                if col1 in df.columns and col2 in df.columns:
                    int_df = self.generate_interaction_features(df, col1, col2)
                    all_features.append(int_df)
                    feature_count += len(int_df.columns)

        # Add original features
        all_features.append(df[bqx_cols])

        # Combine all features
        feature_df = pd.concat(all_features, axis=1)

        # Add target (future BQX value)
        target_horizon = 30
        feature_df['target'] = df['bqx_90'].shift(-target_horizon)

        # Remove rows with NaN
        feature_df = feature_df.dropna()

        logger.info(f"Generated {feature_count} features from {len(bqx_cols)} base columns")
        logger.info(f"Final dataset: {len(feature_df)} rows x {len(feature_df.columns)-1} features")

        return feature_df

class FeatureSelector:
    """Tests and selects best features using multiple methods."""

    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.feature_scores = {}

    def test_variance_threshold(self, threshold=0.01):
        """Remove low-variance features."""
        logger.info("Testing variance threshold...")
        selector = VarianceThreshold(threshold=threshold)
        selector.fit(self.X)
        selected = selector.get_support()
        scores = selector.variances_

        for i, col in enumerate(self.X.columns):
            if col not in self.feature_scores:
                self.feature_scores[col] = {}
            self.feature_scores[col]['variance'] = scores[i]
            self.feature_scores[col]['variance_selected'] = selected[i]

        logger.info(f"Variance threshold selected {sum(selected)}/{len(selected)} features")

    def test_univariate_selection(self, k=50):
        """Test univariate feature selection."""
        logger.info("Testing univariate selection (f-statistic)...")
        selector = SelectKBest(f_regression, k=k)
        selector.fit(self.X, self.y)
        scores = selector.scores_

        for i, col in enumerate(self.X.columns):
            if col not in self.feature_scores:
                self.feature_scores[col] = {}
            self.feature_scores[col]['f_score'] = scores[i]

        logger.info(f"Top univariate score: {max(scores):.2f}")

    def test_mutual_information(self):
        """Test mutual information."""
        logger.info("Testing mutual information...")
        scores = mutual_info_regression(self.X, self.y, random_state=42)

        for i, col in enumerate(self.X.columns):
            if col not in self.feature_scores:
                self.feature_scores[col] = {}
            self.feature_scores[col]['mi_score'] = scores[i]

        logger.info(f"Top MI score: {max(scores):.4f}")

    def test_random_forest_importance(self):
        """Test random forest feature importance."""
        logger.info("Testing random forest importance...")

        # Use smaller model for speed
        rf = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        rf.fit(self.X, self.y)
        importances = rf.feature_importances_

        for i, col in enumerate(self.X.columns):
            if col not in self.feature_scores:
                self.feature_scores[col] = {}
            self.feature_scores[col]['rf_importance'] = importances[i]

        logger.info(f"Top RF importance: {max(importances):.4f}")

    def test_lasso_selection(self):
        """Test L1-based selection."""
        logger.info("Testing L1-based selection (Lasso)...")

        # Scale features for Lasso
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(self.X)

        lasso = LassoCV(cv=5, random_state=42, max_iter=1000)
        lasso.fit(X_scaled, self.y)

        coefs = np.abs(lasso.coef_)

        for i, col in enumerate(self.X.columns):
            if col not in self.feature_scores:
                self.feature_scores[col] = {}
            self.feature_scores[col]['lasso_coef'] = coefs[i]

        logger.info(f"Lasso selected {sum(coefs > 0)}/{len(coefs)} features")

    def select_best_features(self, top_n=50):
        """Combine scores and select best features."""
        logger.info("Selecting best features based on combined scores...")

        # Calculate combined score
        combined_scores = {}
        for col in self.feature_scores:
            scores = self.feature_scores[col]
            # Normalize each score type
            combined = 0
            if 'f_score' in scores:
                combined += scores['f_score'] / 1000  # Normalize f-score
            if 'mi_score' in scores:
                combined += scores['mi_score'] * 10  # Scale MI score
            if 'rf_importance' in scores:
                combined += scores['rf_importance'] * 100  # Scale RF importance
            if 'lasso_coef' in scores:
                combined += scores['lasso_coef'] * 10  # Scale Lasso coef

            combined_scores[col] = combined

        # Sort and select top features
        sorted_features = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_features = [f[0] for f in sorted_features[:top_n]]

        logger.info(f"Selected top {top_n} features")
        logger.info(f"Top 5 features: {top_features[:5]}")

        return top_features, self.feature_scores

def main():
    """Run comprehensive feature generation and selection."""
    print("="*80)
    print("COMPREHENSIVE FEATURE GENERATION AND SELECTION")
    print("="*80)

    # Generate features
    generator = ComprehensiveFeatureGenerator('EUR_USD')
    feature_df = generator.generate_all_features()

    if feature_df is None:
        logger.error("Failed to generate features")
        return

    # Prepare data
    X = feature_df.drop('target', axis=1)
    y = feature_df['target']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Run feature selection
    selector = FeatureSelector(X_train, y_train)

    # Test all methods
    selector.test_variance_threshold()
    selector.test_univariate_selection()
    selector.test_mutual_information()
    selector.test_random_forest_importance()
    selector.test_lasso_selection()

    # Select best features
    best_features, all_scores = selector.select_best_features(top_n=50)

    # Train model with selected features
    logger.info("\nTraining model with selected features...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train[best_features], y_train)

    # Evaluate
    y_pred = rf.predict(X_test[best_features])
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Total features generated: {len(X.columns)}")
    print(f"Features selected: {len(best_features)}")
    print(f"Test R²: {r2:.4f}")
    print(f"Test MAE: {mae:.4f}")
    print("\nTop 10 selected features:")
    for i, feat in enumerate(best_features[:10], 1):
        print(f"  {i}. {feat}")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'pair': 'EUR_USD',
        'total_features': len(X.columns),
        'selected_features': best_features,
        'test_r2': r2,
        'test_mae': mae,
        'feature_scores': all_scores
    }

    with open('/tmp/feature_selection_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.info("\nResults saved to /tmp/feature_selection_results.json")

if __name__ == "__main__":
    main()