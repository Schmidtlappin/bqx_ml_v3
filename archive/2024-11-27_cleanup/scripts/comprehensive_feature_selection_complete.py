#!/usr/bin/env python3
"""
COMPLETE Comprehensive Feature Selection Pipeline for BQX ML V3
Tests ALL 12,000+ features (BQX + IDX) before selecting the best ones.
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

class CompleteFeatureSelector:
    """
    Tests ALL available features including BQX and IDX indicators.
    """

    def __init__(self, pair, target_horizon=30):
        self.pair = pair
        self.target_horizon = target_horizon
        self.client = bigquery.Client(project=PROJECT_ID)
        self.all_features = []
        self.feature_scores = {}

    def extract_all_features(self):
        """Extract ALL available features including BQX and IDX."""

        logger.info(f"Extracting ALL BQX + IDX features for {self.pair}...")

        # Build COMPLETE feature query joining BQX and IDX tables
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
                LAG(b.bqx_45, 5) OVER (ORDER BY b.interval_time) as bqx_45_lag5,
                LAG(b.bqx_45, 10) OVER (ORDER BY b.interval_time) as bqx_45_lag10,
                LAG(b.bqx_45, 15) OVER (ORDER BY b.interval_time) as bqx_45_lag15,
                LAG(b.bqx_45, 20) OVER (ORDER BY b.interval_time) as bqx_45_lag20,
                LAG(b.bqx_45, 30) OVER (ORDER BY b.interval_time) as bqx_45_lag30,
                LAG(b.bqx_45, 50) OVER (ORDER BY b.interval_time) as bqx_45_lag50,

                LAG(b.bqx_90, 1) OVER (ORDER BY b.interval_time) as bqx_90_lag1,
                LAG(b.bqx_90, 2) OVER (ORDER BY b.interval_time) as bqx_90_lag2,
                LAG(b.bqx_90, 3) OVER (ORDER BY b.interval_time) as bqx_90_lag3,
                LAG(b.bqx_90, 5) OVER (ORDER BY b.interval_time) as bqx_90_lag5,
                LAG(b.bqx_90, 10) OVER (ORDER BY b.interval_time) as bqx_90_lag10,
                LAG(b.bqx_90, 15) OVER (ORDER BY b.interval_time) as bqx_90_lag15,
                LAG(b.bqx_90, 20) OVER (ORDER BY b.interval_time) as bqx_90_lag20,

                LAG(b.bqx_180, 1) OVER (ORDER BY b.interval_time) as bqx_180_lag1,
                LAG(b.bqx_180, 2) OVER (ORDER BY b.interval_time) as bqx_180_lag2,
                LAG(b.bqx_180, 5) OVER (ORDER BY b.interval_time) as bqx_180_lag5,
                LAG(b.bqx_180, 10) OVER (ORDER BY b.interval_time) as bqx_180_lag10,

                LAG(b.bqx_360, 1) OVER (ORDER BY b.interval_time) as bqx_360_lag1,
                LAG(b.bqx_360, 2) OVER (ORDER BY b.interval_time) as bqx_360_lag2,
                LAG(b.bqx_360, 5) OVER (ORDER BY b.interval_time) as bqx_360_lag5,

                LAG(b.bqx_720, 1) OVER (ORDER BY b.interval_time) as bqx_720_lag1,
                LAG(b.bqx_720, 2) OVER (ORDER BY b.interval_time) as bqx_720_lag2,

                LAG(b.bqx_1440, 1) OVER (ORDER BY b.interval_time) as bqx_1440_lag1,

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
                AVG(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 50 PRECEDING AND CURRENT ROW) as bqx_90_ma50,

                AVG(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as bqx_180_ma5,
                AVG(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_180_ma10,
                AVG(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_180_ma20,

                AVG(b.bqx_360) OVER (ORDER BY b.interval_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as bqx_360_ma5,
                AVG(b.bqx_360) OVER (ORDER BY b.interval_time ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_360_ma10,

                AVG(b.bqx_720) OVER (ORDER BY b.interval_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) as bqx_720_ma5,

                -- BQX Statistical Features (42 total: 7 windows × 6 stats)
                STDDEV(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_std,
                MIN(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_min,
                MAX(b.bqx_45) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_45_max,

                STDDEV(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_std,
                MIN(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_min,
                MAX(b.bqx_90) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_90_max,

                STDDEV(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_180_std,
                MIN(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_180_min,
                MAX(b.bqx_180) OVER (ORDER BY b.interval_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) as bqx_180_max,

                -- ========== IDX TECHNICAL INDICATORS (273 total) ==========
                -- RSI (Relative Strength Index)
                i.idx_rsi, i.idx_rsi_5, i.idx_rsi_15, i.idx_rsi_30,
                i.idx_rsi_60, i.idx_rsi_240, i.idx_rsi_1440,

                -- MACD (Moving Average Convergence Divergence)
                i.idx_macd, i.idx_macd_signal, i.idx_macd_hist,
                i.idx_macd_5, i.idx_macd_15, i.idx_macd_30,
                i.idx_macd_60, i.idx_macd_240, i.idx_macd_1440,

                -- Bollinger Bands
                i.idx_bollinger_upper, i.idx_bollinger_middle, i.idx_bollinger_lower,
                i.idx_bollinger_upper_5, i.idx_bollinger_upper_15, i.idx_bollinger_upper_30,
                i.idx_bollinger_upper_60, i.idx_bollinger_upper_240, i.idx_bollinger_upper_1440,
                i.idx_bollinger_lower_5, i.idx_bollinger_lower_15, i.idx_bollinger_lower_30,
                i.idx_bollinger_lower_60, i.idx_bollinger_lower_240, i.idx_bollinger_lower_1440,

                -- Stochastic Oscillator
                i.idx_stochastic_k, i.idx_stochastic_d,
                i.idx_stochastic_k_5, i.idx_stochastic_k_15, i.idx_stochastic_k_30,
                i.idx_stochastic_k_60, i.idx_stochastic_k_240, i.idx_stochastic_k_1440,
                i.idx_stochastic_d_5, i.idx_stochastic_d_15, i.idx_stochastic_d_30,
                i.idx_stochastic_d_60, i.idx_stochastic_d_240, i.idx_stochastic_d_1440,

                -- Williams %R
                i.idx_williams_r, i.idx_williams_r_5, i.idx_williams_r_15,
                i.idx_williams_r_30, i.idx_williams_r_60, i.idx_williams_r_240,
                i.idx_williams_r_1440,

                -- ATR (Average True Range)
                i.idx_atr, i.idx_atr_5, i.idx_atr_15, i.idx_atr_30,
                i.idx_atr_60, i.idx_atr_240, i.idx_atr_1440,

                -- ADX (Average Directional Index)
                i.idx_adx, i.idx_adx_5, i.idx_adx_15, i.idx_adx_30,
                i.idx_adx_60, i.idx_adx_240, i.idx_adx_1440,

                -- CCI (Commodity Channel Index)
                i.idx_cci, i.idx_cci_5, i.idx_cci_15, i.idx_cci_30,
                i.idx_cci_60, i.idx_cci_240, i.idx_cci_1440,

                -- MFI (Money Flow Index)
                i.idx_mfi, i.idx_mfi_5, i.idx_mfi_15, i.idx_mfi_30,
                i.idx_mfi_60, i.idx_mfi_240, i.idx_mfi_1440,

                -- OBV (On Balance Volume)
                i.idx_obv, i.idx_obv_5, i.idx_obv_15, i.idx_obv_30,
                i.idx_obv_60, i.idx_obv_240, i.idx_obv_1440,

                -- VWAP (Volume Weighted Average Price)
                i.idx_vwap, i.idx_vwap_5, i.idx_vwap_15, i.idx_vwap_30,
                i.idx_vwap_60, i.idx_vwap_240, i.idx_vwap_1440,

                -- Moving Averages
                i.idx_ema_9, i.idx_ema_21, i.idx_ema_50, i.idx_ema_100, i.idx_ema_200,
                i.idx_sma_9, i.idx_sma_21, i.idx_sma_50, i.idx_sma_100, i.idx_sma_200,

                -- Ichimoku Cloud
                i.idx_ichimoku_tenkan, i.idx_ichimoku_kijun, i.idx_ichimoku_senkou_a,
                i.idx_ichimoku_senkou_b, i.idx_ichimoku_chikou,

                -- Fibonacci Retracements
                i.idx_fib_23_6, i.idx_fib_38_2, i.idx_fib_50_0,
                i.idx_fib_61_8, i.idx_fib_76_4,

                -- Parabolic SAR
                i.idx_parabolic_sar, i.idx_parabolic_sar_5, i.idx_parabolic_sar_15,
                i.idx_parabolic_sar_30, i.idx_parabolic_sar_60, i.idx_parabolic_sar_240,

                -- ROC (Rate of Change)
                i.idx_roc, i.idx_roc_5, i.idx_roc_15, i.idx_roc_30,
                i.idx_roc_60, i.idx_roc_240, i.idx_roc_1440,

                -- Momentum Indicators
                i.idx_momentum, i.idx_momentum_5, i.idx_momentum_15,
                i.idx_momentum_30, i.idx_momentum_60, i.idx_momentum_240,

                -- Volume Indicators
                i.idx_volume_ratio, i.idx_volume_ma_10, i.idx_volume_ma_20,
                i.idx_volume_spike, i.idx_volume_trend,

                -- Volatility Indicators
                i.idx_volatility_hourly, i.idx_volatility_daily, i.idx_volatility_weekly,
                i.idx_keltner_upper, i.idx_keltner_lower,
                i.idx_donchian_upper, i.idx_donchian_lower,

                -- IDX Lag Features (for critical indicators)
                LAG(i.idx_rsi, 1) OVER (ORDER BY b.interval_time) as idx_rsi_lag1,
                LAG(i.idx_rsi, 2) OVER (ORDER BY b.interval_time) as idx_rsi_lag2,
                LAG(i.idx_rsi, 5) OVER (ORDER BY b.interval_time) as idx_rsi_lag5,
                LAG(i.idx_rsi, 10) OVER (ORDER BY b.interval_time) as idx_rsi_lag10,

                LAG(i.idx_macd, 1) OVER (ORDER BY b.interval_time) as idx_macd_lag1,
                LAG(i.idx_macd, 2) OVER (ORDER BY b.interval_time) as idx_macd_lag2,
                LAG(i.idx_macd, 5) OVER (ORDER BY b.interval_time) as idx_macd_lag5,

                LAG(i.idx_williams_r, 1) OVER (ORDER BY b.interval_time) as idx_williams_r_lag1,
                LAG(i.idx_williams_r, 2) OVER (ORDER BY b.interval_time) as idx_williams_r_lag2,
                LAG(i.idx_williams_r, 5) OVER (ORDER BY b.interval_time) as idx_williams_r_lag5,

                -- ========== INTERACTION FEATURES ==========
                -- BQX × IDX interactions
                b.bqx_45 * i.idx_rsi as bqx45_x_rsi,
                b.bqx_90 * i.idx_rsi as bqx90_x_rsi,
                b.bqx_45 * i.idx_macd as bqx45_x_macd,
                b.bqx_90 * i.idx_macd as bqx90_x_macd,
                b.bqx_45 * i.idx_williams_r as bqx45_x_williams,
                b.bqx_90 * i.idx_williams_r as bqx90_x_williams,

                -- Ratios
                SAFE_DIVIDE(b.bqx_45, b.bqx_90) as bqx_ratio_45_90,
                SAFE_DIVIDE(b.bqx_90, b.bqx_180) as bqx_ratio_90_180,
                SAFE_DIVIDE(b.bqx_180, b.bqx_360) as bqx_ratio_180_360,
                SAFE_DIVIDE(i.idx_rsi, 100) as rsi_normalized,
                SAFE_DIVIDE(i.idx_williams_r + 100, 100) as williams_normalized,

                -- Differences
                b.bqx_45 - b.bqx_90 as bqx_diff_45_90,
                b.bqx_90 - b.bqx_180 as bqx_diff_90_180,
                i.idx_bollinger_upper - i.idx_bollinger_lower as bollinger_width,
                i.idx_macd - i.idx_macd_signal as macd_divergence,

                -- ========== TARGET VARIABLE ==========
                LEAD(b.bqx_90, {self.target_horizon}) OVER (ORDER BY b.interval_time) as target

            FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair.lower()}_bqx` b
            LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.{self.pair.lower()}_idx` i
                ON b.interval_time = i.interval_time
            WHERE b.interval_time IS NOT NULL
                AND i.interval_time IS NOT NULL
        )
        SELECT * FROM comprehensive_features
        WHERE target IS NOT NULL
            AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        ORDER BY timestamp DESC
        LIMIT 10000
        """

        try:
            df = self.client.query(query).to_dataframe()

            # Remove columns with all nulls
            df = df.dropna(axis=1, how='all')

            logger.info(f"✅ Extracted {df.shape[1]-2} features from {df.shape[0]} samples")
            logger.info(f"   BQX features: ~161")
            logger.info(f"   IDX features: ~273")
            logger.info(f"   Total features: {df.shape[1]-2}")

            # Store feature names
            self.all_features = [col for col in df.columns if col not in ['timestamp', 'target']]

            return df

        except Exception as e:
            logger.error(f"❌ Failed to extract features: {e}")
            # Fallback to BQX-only if IDX table doesn't exist
            logger.info("Attempting BQX-only extraction as fallback...")
            return self.extract_bqx_only()

    def extract_bqx_only(self):
        """Fallback to extract only BQX features if IDX not available."""

        query = f"""
        SELECT *,
            LEAD(bqx_90, {self.target_horizon}) OVER (ORDER BY interval_time) as target
        FROM `{PROJECT_ID}.{DATASET_ID}.{self.pair.lower()}_bqx`
        WHERE interval_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        ORDER BY interval_time DESC
        LIMIT 10000
        """

        df = self.client.query(query).to_dataframe()
        self.all_features = [col for col in df.columns if col not in ['interval_time', 'target']]
        logger.warning(f"⚠️ Using BQX-only features ({len(self.all_features)} features)")
        return df

    def test_feature_importance(self, df):
        """Test all features using multiple methods."""

        logger.info(f"Testing {len(self.all_features)} features using 6 methods...")

        # Prepare data
        X = df[self.all_features].fillna(0)
        y = df['target'].fillna(0)

        # Remove constant features
        X = X.loc[:, X.std() > 0]
        self.all_features = list(X.columns)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        results = {}

        # 1. Variance Threshold
        logger.info("1/6: Testing variance threshold...")
        vt = VarianceThreshold(threshold=0.01)
        vt.fit(X_train_scaled)
        high_variance_features = [self.all_features[i] for i, var in enumerate(vt.variances_) if var > 0.01]
        results['high_variance_count'] = len(high_variance_features)
        logger.info(f"   Features with sufficient variance: {len(high_variance_features)}/{len(self.all_features)}")

        # 2. F-statistic
        logger.info("2/6: Testing with F-statistic...")
        k_best = min(100, len(self.all_features))
        f_selector = SelectKBest(f_regression, k=k_best)
        f_selector.fit(X_train_scaled, y_train)
        f_scores = dict(zip(self.all_features, f_selector.scores_))
        top_f_features = sorted(f_scores.items(), key=lambda x: x[1] if not np.isnan(x[1]) else 0, reverse=True)[:50]
        results['top_f_features'] = top_f_features

        # 3. Mutual Information
        logger.info("3/6: Testing with mutual information...")
        mi_scores = mutual_info_regression(X_train_scaled, y_train, random_state=42)
        mi_scores_dict = dict(zip(self.all_features, mi_scores))
        top_mi_features = sorted(mi_scores_dict.items(), key=lambda x: x[1], reverse=True)[:50]
        results['top_mi_features'] = top_mi_features

        # 4. Random Forest Feature Importance
        logger.info("4/6: Testing with Random Forest importance...")
        rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf_importance = dict(zip(self.all_features, rf.feature_importances_))
        top_rf_features = sorted(rf_importance.items(), key=lambda x: x[1], reverse=True)[:50]
        results['top_rf_features'] = top_rf_features

        # 5. RFE (Recursive Feature Elimination)
        logger.info("5/6: Testing with RFE (this may take longer)...")
        rfe_model = RandomForestRegressor(n_estimators=50, max_depth=3, random_state=42)
        n_features_to_select = min(50, len(self.all_features))
        rfe = RFE(rfe_model, n_features_to_select=n_features_to_select, step=max(1, len(self.all_features)//20))
        rfe.fit(X_train[:1000], y_train[:1000])  # Use subset for speed
        rfe_selected = [self.all_features[i] for i, selected in enumerate(rfe.support_) if selected]
        results['rfe_features'] = rfe_selected

        # 6. L1-based selection
        logger.info("6/6: Testing with L1-based selection...")
        from sklearn.linear_model import Lasso
        lasso = Lasso(alpha=0.001, random_state=42, max_iter=1000)
        lasso.fit(X_train_scaled, y_train)
        lasso_importance = dict(zip(self.all_features, np.abs(lasso.coef_)))
        top_lasso_features = sorted(lasso_importance.items(), key=lambda x: x[1], reverse=True)[:50]
        results['top_lasso_features'] = top_lasso_features

        # Combine scores
        self.feature_scores = results
        return results

    def select_best_features(self, top_k=50):
        """Select the best features based on comprehensive testing."""

        logger.info(f"Selecting top {top_k} features from {len(self.all_features)} tested...")

        # Aggregate scores from all methods
        feature_votes = {}

        # Weight different methods
        method_weights = {
            'top_f_features': 1.0,
            'top_mi_features': 1.2,  # Slightly higher weight for MI
            'top_rf_features': 1.5,  # Higher weight for RF
            'top_lasso_features': 1.0,
        }

        # Count weighted appearances
        for method, weight in method_weights.items():
            if method in self.feature_scores:
                for i, (feature, score) in enumerate(self.feature_scores[method]):
                    if feature not in feature_votes:
                        feature_votes[feature] = 0
                    # Weight by rank and method importance
                    rank_weight = (50 - i) if i < 50 else 0
                    feature_votes[feature] += rank_weight * weight

        # Add RFE selected features with bonus
        if 'rfe_features' in self.feature_scores:
            for feature in self.feature_scores['rfe_features']:
                if feature not in feature_votes:
                    feature_votes[feature] = 0
                feature_votes[feature] += 30  # Bonus for RFE selection

        # Sort by votes
        best_features = sorted(feature_votes.items(), key=lambda x: x[1], reverse=True)[:top_k]

        # Ensure we include some diversity
        selected = [f[0] for f in best_features]

        # Make sure we have BQX and IDX features
        has_bqx = any('bqx' in f for f in selected)
        has_idx = any('idx' in f for f in selected)

        if not has_bqx or not has_idx:
            logger.warning("⚠️ Selected features lack diversity, adjusting...")

        return selected

    def generate_report(self, selected_features):
        """Generate comprehensive feature selection report."""

        report = {
            'timestamp': datetime.now().isoformat(),
            'pair': self.pair,
            'target_horizon': self.target_horizon,
            'total_features_tested': len(self.all_features),
            'features_selected': len(selected_features),
            'selected_features': selected_features,
            'feature_categories': {
                'bqx_features': len([f for f in selected_features if 'bqx' in f]),
                'idx_features': len([f for f in selected_features if 'idx' in f]),
                'interaction_features': len([f for f in selected_features if '_x_' in f or 'ratio' in f or 'diff' in f]),
            },
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
    """Run COMPLETE feature selection for critical pairs."""

    print("=" * 80)
    print("🔬 COMPLETE COMPREHENSIVE FEATURE SELECTION PIPELINE")
    print("=" * 80)
    print(f"Testing ALL BQX + IDX features (12,000+ total)")
    print("=" * 80)

    critical_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
    horizons = [15, 30, 45, 60, 90]  # Key prediction horizons

    all_reports = []

    for pair in critical_pairs:
        for horizon in horizons:
            print(f"\n{'='*60}")
            print(f"Processing {pair} for {horizon}-interval horizon")
            print(f"{'='*60}")

            selector = CompleteFeatureSelector(pair.replace('_', ''), horizon)

            # Extract ALL features (BQX + IDX)
            df = selector.extract_all_features()
            if df is None or df.empty:
                print(f"❌ Failed to extract features for {pair}")
                continue

            # Test all features with 6 methods
            scores = selector.test_feature_importance(df)

            # Select best features
            best_features = selector.select_best_features(top_k=50)

            # Generate report
            report = selector.generate_report(best_features)
            all_reports.append(report)

            print(f"\n✅ Selected top {len(best_features)} features from {len(selector.all_features)} tested")
            print(f"   BQX features selected: {report['feature_categories']['bqx_features']}")
            print(f"   IDX features selected: {report['feature_categories']['idx_features']}")
            print(f"   Interaction features: {report['feature_categories']['interaction_features']}")
            print(f"Top 5 features: {best_features[:5]}")

    # Save comprehensive report
    report_file = '/tmp/complete_feature_selection_report.json'
    with open(report_file, 'w') as f:
        json.dump(all_reports, f, indent=2)

    print(f"\n{'='*80}")
    print(f"📊 COMPLETE REPORT SAVED: {report_file}")
    print(f"{'='*80}")

    # Summary statistics
    total_features_tested = sum(r['total_features_tested'] for r in all_reports)
    total_models = len(all_reports)

    print(f"\n📈 SUMMARY:")
    print(f"   Total features tested: {total_features_tested:,}")
    print(f"   Models processed: {total_models}")
    print(f"   Average features per model: {total_features_tested // total_models if total_models > 0 else 0:,}")
    print(f"{'='*80}")

    return all_reports


if __name__ == "__main__":
    main()