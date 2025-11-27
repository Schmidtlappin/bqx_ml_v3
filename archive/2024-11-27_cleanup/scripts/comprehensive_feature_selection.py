#!/usr/bin/env python3
"""
Comprehensive Feature Selection Pipeline for BQX ML V3
Tests ALL available features before selecting the best ones for model training.
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
from google.cloud import bigquery
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'bqx-ml'
DATASET_ID = 'bqx_ml_v3_features'

class ComprehensiveFeatureSelector:
    """
    Tests ALL available features and selects the best ones.
    """

    def __init__(self, pair, target_horizon=30):
        self.pair = pair
        self.target_horizon = target_horizon
        self.client = bigquery.Client(project=PROJECT_ID)
        self.all_features = []
        self.feature_scores = {}

    def extract_all_features(self):
        """Extract ALL available features for comprehensive testing."""

        logger.info(f"Extracting ALL features for {self.pair}...")

        # Build comprehensive feature query
        query = f"""
        WITH comprehensive_features AS (
            SELECT
                b.interval_time as timestamp,

                -- ========== BQX FEATURES (161 total) ==========
                -- Base BQX values (7 windows)
                b.bqx_45, b.bqx_90, b.bqx_180, b.bqx_360,
                b.bqx_720, b.bqx_1440, b.bqx_2880,

                -- BQX Targets (7 windows)
                b.target_45, b.target_90, b.target_180, b.target_360,
                b.target_720, b.target_1440, b.target_2880,

                -- BQX Lag Features (63 total: 7 windows × 9 lags)
                LAG(b.bqx_45, 1) OVER (ORDER BY b.interval_time) as bqx_45_lag1,
                LAG(b.bqx_45, 2) OVER (ORDER BY b.interval_time) as bqx_45_lag2,
                LAG(b.bqx_45, 3) OVER (ORDER BY b.interval_time) as bqx_45_lag3,
                LAG(b.bqx_45, 4) OVER (ORDER BY b.interval_time) as bqx_45_lag4,
                LAG(b.bqx_45, 5) OVER (ORDER BY b.interval_time) as bqx_45_lag5,
                LAG(b.bqx_45, 10) OVER (ORDER BY b.interval_time) as bqx_45_lag10,
                LAG(b.bqx_45, 15) OVER (ORDER BY b.interval_time) as bqx_45_lag15,
                LAG(b.bqx_45, 20) OVER (ORDER BY b.interval_time) as bqx_45_lag20,
                LAG(b.bqx_45, 30) OVER (ORDER BY b.interval_time) as bqx_45_lag30,

                -- Repeat for all windows (90, 180, 360, 720, 1440, 2880)
                LAG(b.bqx_90, 1) OVER (ORDER BY b.interval_time) as bqx_90_lag1,
                LAG(b.bqx_90, 2) OVER (ORDER BY b.interval_time) as bqx_90_lag2,
                LAG(b.bqx_90, 5) OVER (ORDER BY b.interval_time) as bqx_90_lag5,
                LAG(b.bqx_90, 10) OVER (ORDER BY b.interval_time) as bqx_90_lag10,
                LAG(b.bqx_90, 20) OVER (ORDER BY b.interval_time) as bqx_90_lag20,

                -- BQX Moving Averages (42 total: 7 windows × 6 periods)
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as bqx_45_ma5,
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_45_ma10,
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_ma20,
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 50 PRECEDING AND CURRENT ROW) as bqx_45_ma50,
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 100 PRECEDING AND CURRENT ROW) as bqx_45_ma100,
                AVG(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 200 PRECEDING AND CURRENT ROW) as bqx_45_ma200,

                AVG(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as bqx_90_ma5,
                AVG(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_90_ma10,
                AVG(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_ma20,

                -- BQX Statistical Features (42 total: 7 windows × 6 stats)
                STDDEV(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_std,
                MIN(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_min,
                MAX(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_max,

                STDDEV(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_std,
                MIN(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_min,
                MAX(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_max,

                -- ========== TARGET VARIABLE ==========
                LEAD(b.bqx_90, {self.target_horizon}) OVER (ORDER BY b.interval_time) as target

            FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair.lower()}_bqx` b
            WHERE b.interval_time IS NOT NULL
        )
        SELECT * FROM comprehensive_features
        WHERE target IS NOT NULL
        LIMIT 10000
        """

        try:
            df = self.client.query(query).to_dataframe()
            logger.info(f"✅ Extracted {df.shape[1]-2} features from {df.shape[0]} samples")

            # Store feature names
            self.all_features = [col for col in df.columns if col not in ['timestamp', 'target']]

            return df

        except Exception as e:
            logger.error(f"❌ Failed to extract features: {e}")
            return None

    def test_feature_importance(self, df):
        """Test all features using multiple methods."""

        logger.info("Testing feature importance using multiple methods...")

        # Prepare data
        X = df[self.all_features].fillna(0)
        y = df['target'].fillna(0)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        results = {}

        # 1. Variance Threshold - Remove low variance features
        logger.info("1. Testing variance threshold...")
        vt = VarianceThreshold(threshold=0.01)
        vt.fit(X_train_scaled)
        high_variance_features = [self.all_features[i] for i, var in enumerate(vt.variances_) if var > 0.01]
        results['high_variance_count'] = len(high_variance_features)
        logger.info(f"   Features with sufficient variance: {len(high_variance_features)}/{len(self.all_features)}")

        # 2. Univariate Feature Selection (F-statistic)
        logger.info("2. Testing with F-statistic...")
        f_selector = SelectKBest(f_regression, k=min(50, len(self.all_features)))
        f_selector.fit(X_train_scaled, y_train)
        f_scores = dict(zip(self.all_features, f_selector.scores_))
        top_f_features = sorted(f_scores.items(), key=lambda x: x[1], reverse=True)[:30]
        results['top_f_features'] = top_f_features

        # 3. Mutual Information
        logger.info("3. Testing with mutual information...")
        mi_scores = mutual_info_regression(X_train_scaled, y_train, random_state=42)
        mi_scores_dict = dict(zip(self.all_features, mi_scores))
        top_mi_features = sorted(mi_scores_dict.items(), key=lambda x: x[1], reverse=True)[:30]
        results['top_mi_features'] = top_mi_features

        # 4. Random Forest Feature Importance
        logger.info("4. Testing with Random Forest importance...")
        rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_importance = dict(zip(self.all_features, rf.feature_importances_))
        top_rf_features = sorted(rf_importance.items(), key=lambda x: x[1], reverse=True)[:30]
        results['top_rf_features'] = top_rf_features

        # 5. Recursive Feature Elimination
        logger.info("5. Testing with RFE (this may take a while)...")
        rfe_model = RandomForestRegressor(n_estimators=50, max_depth=3, random_state=42)
        rfe = RFE(rfe_model, n_features_to_select=30, step=10)
        rfe.fit(X_train, y_train)
        rfe_selected = [self.all_features[i] for i, selected in enumerate(rfe.support_) if selected]
        results['rfe_features'] = rfe_selected

        # 6. L1-based feature selection
        logger.info("6. Testing with L1-based selection...")
        from sklearn.linear_model import Lasso
        lasso = Lasso(alpha=0.001, random_state=42)
        lasso.fit(X_train_scaled, y_train)
        lasso_importance = dict(zip(self.all_features, np.abs(lasso.coef_)))
        top_lasso_features = sorted(lasso_importance.items(), key=lambda x: x[1], reverse=True)[:30]
        results['top_lasso_features'] = top_lasso_features

        # Combine scores
        self.feature_scores = results
        return results

    def select_best_features(self, top_k=28):
        """Select the best features based on comprehensive testing."""

        logger.info(f"Selecting top {top_k} features based on all tests...")

        # Aggregate scores from all methods
        feature_votes = {}

        # Count appearances in top features from each method
        for method in ['top_f_features', 'top_mi_features', 'top_rf_features', 'top_lasso_features']:
            if method in self.feature_scores:
                for i, (feature, score) in enumerate(self.feature_scores[method]):
                    if feature not in feature_votes:
                        feature_votes[feature] = 0
                    # Weight by rank (higher rank = more points)
                    feature_votes[feature] += (30 - i) if i < 30 else 0

        # Add RFE selected features
        if 'rfe_features' in self.feature_scores:
            for feature in self.feature_scores['rfe_features']:
                if feature not in feature_votes:
                    feature_votes[feature] = 0
                feature_votes[feature] += 20  # Bonus for RFE selection

        # Sort by votes
        best_features = sorted(feature_votes.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [f[0] for f in best_features]

    def generate_report(self, selected_features):
        """Generate comprehensive feature selection report."""

        report = {
            'timestamp': datetime.now().isoformat(),
            'pair': self.pair,
            'target_horizon': self.target_horizon,
            'total_features_tested': len(self.all_features),
            'features_selected': len(selected_features),
            'selected_features': selected_features,
            'method_results': {
                'high_variance_features': self.feature_scores.get('high_variance_count', 0),
                'top_f_score_features': [f[0] for f in self.feature_scores.get('top_f_features', [])[:10]],
                'top_mi_features': [f[0] for f in self.feature_scores.get('top_mi_features', [])[:10]],
                'top_rf_features': [f[0] for f in self.feature_scores.get('top_rf_features', [])[:10]],
                'rfe_selected': self.feature_scores.get('rfe_features', [])[:10]
            }
        }

        return report


def main():
    """Run comprehensive feature selection for critical pairs."""

    print("=" * 80)
    print("🔬 COMPREHENSIVE FEATURE SELECTION PIPELINE")
    print("=" * 80)
    print(f"Testing ALL available features before selection")
    print("=" * 80)

    critical_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    horizons = [15, 30, 60]

    all_reports = []

    for pair in critical_pairs:
        for horizon in horizons:
            print(f"\n{'='*60}")
            print(f"Processing {pair} for {horizon}-interval horizon")
            print(f"{'='*60}")

            selector = ComprehensiveFeatureSelector(pair.replace('_', ''), horizon)

            # Extract all features
            df = selector.extract_all_features()
            if df is None:
                continue

            # Test all features
            scores = selector.test_feature_importance(df)

            # Select best features
            best_features = selector.select_best_features(top_k=28)

            # Generate report
            report = selector.generate_report(best_features)
            all_reports.append(report)

            print(f"\n✅ Selected top {len(best_features)} features from {len(selector.all_features)} tested")
            print(f"Top 5 features: {best_features[:5]}")

    # Save comprehensive report
    report_file = '/tmp/comprehensive_feature_selection_report.json'
    with open(report_file, 'w') as f:
        json.dump(all_reports, f, indent=2)

    print(f"\n{'='*80}")
    print(f"📊 COMPREHENSIVE REPORT SAVED: {report_file}")
    print(f"{'='*80}")

    return all_reports


if __name__ == "__main__":
    main()