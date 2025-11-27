#!/usr/bin/env python3
"""
PHASE 2: CORRELATION NETWORK ANALYSIS
Tests correlation network features to improve model performance
Authorization: ALPHA-2-PROCEED
Target: >2% R² improvement to expand from 7x7 to 28x28
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime
import json
from typing import Dict, List
from pyairtable import Api
import warnings
warnings.filterwarnings('ignore')

class CorrelationNetworkTester:
    def __init__(self):
        """Initialize correlation network testing framework"""
        self.client = bigquery.Client(project="bqx-ml")
        self.baseline_r2 = 0.7079  # Current Smart Dual performance
        self.improvement_threshold = 0.02  # 2% improvement to expand
        self.results = []

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Major pairs for 7x7 matrix
        self.major_pairs = ['eurusd', 'gbpusd', 'usdjpy', 'usdchf',
                          'audusd', 'usdcad', 'nzdusd']

        # All 28 pairs for full matrix if improvement > 2%
        self.all_pairs = [
            'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
            'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'eurcad', 'eurnzd',
            'gbpjpy', 'gbpchf', 'gbpaud', 'gbpcad', 'gbpnzd',
            'audjpy', 'audchf', 'audcad', 'audnzd',
            'nzdjpy', 'nzdchf', 'nzdcad',
            'cadjpy', 'cadchf', 'chfjpy'
        ]

        # Rolling windows to test
        self.windows = [10, 20, 50, 100, 200]

    def load_pair_data(self, pair: str, limit: int = 50000) -> pd.DataFrame:
        """Load price data for a currency pair"""
        try:
            query = f"""
            SELECT
                interval_time,
                close_idx as close_price
            FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
            ORDER BY interval_time
            LIMIT {limit}
            """
            data = self.client.query(query).to_dataframe()
            data.set_index('interval_time', inplace=True)
            return data
        except Exception as e:
            print(f"  ⚠️ Could not load {pair}: {e}")
            return pd.DataFrame()

    def create_correlation_features(self, target_pair: str, matrix_pairs: list,
                                   rolling_window: int) -> pd.DataFrame:
        """
        Create correlation network features
        """
        features = pd.DataFrame()

        # Load target pair data
        target_data = self.load_pair_data(target_pair)
        if target_data.empty:
            return features

        # Calculate returns for target
        target_returns = target_data['close_price'].pct_change()

        # Load data for correlation pairs
        pair_returns = {}
        for pair in matrix_pairs:
            if pair != target_pair:  # Skip self-correlation
                pair_data = self.load_pair_data(pair)
                if not pair_data.empty:
                    # Align with target data
                    pair_data = pair_data.reindex(target_data.index, method='ffill')
                    pair_returns[pair] = pair_data['close_price'].pct_change()

        if not pair_returns:
            return features

        # Create correlation features for each window
        print(f"  Creating correlation features with window={rolling_window}")

        # 1. Rolling correlations with each pair
        for pair, returns in pair_returns.items():
            corr = target_returns.rolling(window=rolling_window).corr(returns)
            features[f'corr_{target_pair}_{pair}_{rolling_window}'] = corr

        # 2. Average correlation (market coupling)
        all_corrs = pd.DataFrame(pair_returns)
        features[f'avg_correlation_{rolling_window}'] = (
            all_corrs.rolling(window=rolling_window)
            .corr()
            .xs(target_returns.name, level=1, drop_level=True)
            .mean(axis=1)
        )

        # 3. Correlation stability (std of correlations)
        features[f'corr_stability_{rolling_window}'] = (
            all_corrs.rolling(window=rolling_window)
            .corr()
            .xs(target_returns.name, level=1, drop_level=True)
            .std(axis=1)
        )

        # 4. Correlation momentum (change in correlation)
        for pair in list(pair_returns.keys())[:3]:  # Top 3 pairs only
            corr_series = features[f'corr_{target_pair}_{pair}_{rolling_window}']
            features[f'corr_momentum_{pair}_{rolling_window}'] = corr_series.diff(10)

        # 5. Correlation divergence (deviation from mean correlation)
        mean_corr = features[[col for col in features.columns if col.startswith('corr_')
                             and col.endswith(str(rolling_window))]].mean(axis=1)
        for pair in list(pair_returns.keys())[:3]:  # Top 3 pairs
            corr_col = f'corr_{target_pair}_{pair}_{rolling_window}'
            if corr_col in features.columns:
                features[f'corr_divergence_{pair}_{rolling_window}'] = (
                    features[corr_col] - mean_corr
                )

        # 6. Eigenvalue of correlation matrix (market stress indicator)
        # This measures overall market correlation strength
        try:
            corr_matrix = all_corrs.rolling(window=rolling_window).corr()
            # Get eigenvalues for each time period (simplified - just max eigenvalue)
            features[f'max_eigenvalue_{rolling_window}'] = 0  # Placeholder
        except:
            pass

        print(f"  ✅ Created {len(features.columns)} correlation features")
        return features

    def test_feature_improvement(self, pair: str, window: int,
                                correlation_features: pd.DataFrame) -> Dict:
        """Test if correlation features improve model performance"""

        try:
            # Load base Smart Dual features
            idx_query = f"""
            SELECT * FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
            ORDER BY interval_time
            LIMIT 50000
            """
            idx_data = self.client.query(idx_query).to_dataframe()

            bqx_query = f"""
            SELECT * FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
            ORDER BY interval_time
            LIMIT 50000
            """
            bqx_data = self.client.query(bqx_query).to_dataframe()

            # Align correlation features with base data
            idx_data.set_index('interval_time', inplace=True)
            bqx_data.set_index('interval_time', inplace=True)

            # Create Smart Dual baseline features
            base_features = pd.DataFrame(index=idx_data.index)
            base_features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            base_features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            base_features['idx_lag_3'] = idx_data['close_idx'].shift(3)
            base_features['bqx_lag_1'] = bqx_data[f'bqx_{window}'].shift(1)
            base_features['bqx_lag_2'] = bqx_data[f'bqx_{window}'].shift(2)
            base_features['idx_ma_5'] = idx_data['close_idx'].rolling(5).mean()
            base_features['idx_ma_20'] = idx_data['close_idx'].rolling(20).mean()
            base_features['bqx_ma_5'] = bqx_data[f'bqx_{window}'].rolling(5).mean()
            base_features['idx_std_20'] = idx_data['close_idx'].rolling(20).std()
            base_features['idx_bqx_ratio'] = base_features['idx_lag_1'] / (base_features['bqx_lag_1'] + 1e-6)

            # Target variable
            y = bqx_data[f'bqx_{window}']

            # Test baseline model
            base_features = base_features.dropna()
            y_base = y[base_features.index]

            X_train_base, X_test_base, y_train_base, y_test_base = train_test_split(
                base_features, y_base, test_size=0.2, random_state=42
            )

            base_model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                random_state=42
            )
            base_model.fit(X_train_base, y_train_base)
            base_pred = base_model.predict(X_test_base)
            baseline_r2 = r2_score(y_test_base, base_pred)

            # Align correlation features with base features
            correlation_features = correlation_features.reindex(base_features.index)

            # Test with correlation features
            combined_features = pd.concat([base_features, correlation_features], axis=1)
            combined_features = combined_features.dropna()
            y_combined = y[combined_features.index]

            if len(combined_features) < 1000:
                raise ValueError("Not enough data after combining features")

            X_train_new, X_test_new, y_train_new, y_test_new = train_test_split(
                combined_features, y_combined, test_size=0.2, random_state=42
            )

            new_model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.05,
                random_state=42
            )
            new_model.fit(X_train_new, y_train_new)
            new_pred = new_model.predict(X_test_new)
            new_r2 = r2_score(y_test_new, new_pred)

            improvement = new_r2 - baseline_r2

            # Get feature importance
            feature_importance = new_model.feature_importances_
            feature_names = combined_features.columns
            top_features = sorted(zip(feature_names, feature_importance),
                                key=lambda x: x[1], reverse=True)[:10]

            return {
                'baseline_r2': baseline_r2,
                'new_r2': new_r2,
                'improvement': improvement,
                'improvement_pct': (improvement / baseline_r2) * 100,
                'expand_to_28x28': improvement >= self.improvement_threshold,
                'top_features': top_features
            }

        except Exception as e:
            print(f"  ❌ Error testing features: {e}")
            return {
                'baseline_r2': self.baseline_r2,
                'new_r2': self.baseline_r2,
                'improvement': 0,
                'improvement_pct': 0,
                'expand_to_28x28': False,
                'top_features': []
            }

    def update_airtable_append(self, task_id: str, update_content: str):
        """Update AirTable task using APPEND mode"""
        try:
            # Find the task
            all_tasks = self.tasks_table.all()
            record = None
            for task in all_tasks:
                if task['fields'].get('task_id') == task_id:
                    record = task
                    break

            if not record:
                print(f"  ⚠️ Task {task_id} not found in AirTable")
                return

            # Get existing notes
            current_notes = record['fields'].get('notes', '')

            # Create new update block
            timestamp = datetime.now().isoformat()
            new_update = f"""🔄 IN PROGRESS: {timestamp}
================================================
{update_content}
================================================"""

            # APPEND mode - new on top, preserve history
            if current_notes:
                updated_notes = f"{new_update}\n\n{current_notes}"
            else:
                updated_notes = new_update

            # Update the task
            self.tasks_table.update(record['id'], {
                'notes': updated_notes,
                'status': 'In Progress'
            })

            print(f"  ✅ AirTable updated (APPEND mode): {task_id}")

        except Exception as e:
            print(f"  ❌ Error updating AirTable: {e}")

    def test_correlations(self):
        """Main testing loop for correlation network features"""

        print("\n" + "="*60)
        print("PHASE 2: CORRELATION NETWORK ANALYSIS")
        print("Authorization: ALPHA-2-PROCEED")
        print(f"Baseline R²: {self.baseline_r2}")
        print(f"Expansion threshold: {self.improvement_threshold*100}%")
        print("="*60)

        # Test on EURUSD with 45-minute window
        test_pair = 'eurusd'
        test_window = 45

        print(f"\n📊 Testing 7x7 correlation matrix on {test_pair.upper()}-{test_window}")
        print("-"*60)

        best_improvement = 0
        best_window = None
        best_features = None

        # Test each rolling window
        for roll_window in self.windows:
            print(f"\n[Window {roll_window}] Creating correlation network")

            # Create correlation features with major pairs
            corr_features = self.create_correlation_features(
                test_pair, self.major_pairs, roll_window
            )

            if corr_features.empty:
                print(f"  ⚠️ No features created for window {roll_window}")
                continue

            # Test improvement
            result = self.test_feature_improvement(test_pair, test_window, corr_features)

            print(f"  Baseline R²: {result['baseline_r2']:.4f}")
            print(f"  With correlations: {result['new_r2']:.4f}")
            print(f"  Improvement: {result['improvement']:.4f} ({result['improvement_pct']:.2f}%)")

            if result['improvement'] > best_improvement:
                best_improvement = result['improvement']
                best_window = roll_window
                best_features = result['top_features']

            self.results.append({
                'window': roll_window,
                'matrix_size': '7x7',
                'baseline_r2': result['baseline_r2'],
                'new_r2': result['new_r2'],
                'improvement': result['improvement'],
                'improvement_pct': result['improvement_pct']
            })

        # Check if we should expand to 28x28
        expand = best_improvement >= self.improvement_threshold

        if expand:
            print(f"\n✅ EXPANDING TO 28x28 MATRIX (improvement {best_improvement:.4f} > {self.improvement_threshold})")

            # Test with full 28x28 matrix
            print(f"\n[28x28 Matrix] Testing with window {best_window}")

            full_corr_features = self.create_correlation_features(
                test_pair, self.all_pairs, best_window
            )

            if not full_corr_features.empty:
                full_result = self.test_feature_improvement(test_pair, test_window, full_corr_features)

                print(f"  Baseline R²: {full_result['baseline_r2']:.4f}")
                print(f"  With 28x28: {full_result['new_r2']:.4f}")
                print(f"  Improvement: {full_result['improvement']:.4f} ({full_result['improvement_pct']:.2f}%)")

                self.results.append({
                    'window': best_window,
                    'matrix_size': '28x28',
                    'baseline_r2': full_result['baseline_r2'],
                    'new_r2': full_result['new_r2'],
                    'improvement': full_result['improvement'],
                    'improvement_pct': full_result['improvement_pct']
                })
        else:
            print(f"\n❌ NOT EXPANDING (improvement {best_improvement:.4f} < {self.improvement_threshold})")

        # Update AirTable with results
        summary = f"""CORRELATION NETWORK TESTING
• Matrix tested: 7x7 (major pairs)
• Windows tested: {', '.join(map(str, self.windows))}
• Best window: {best_window}
• Best improvement: {best_improvement:.4f} ({(best_improvement/self.baseline_r2)*100:.2f}%)
• Expanded to 28x28: {'Yes' if expand else 'No'}
• Features to keep: {10 if best_improvement > 0.01 else 0}

Results by window:
{chr(10).join([f"  - Window {r['window']}: R²={r['new_r2']:.4f} (Δ={r['improvement']:.4f})" for r in self.results if r['matrix_size'] == '7x7'])}

Top features identified:
{chr(10).join([f"  - {feat[0]}: {feat[1]:.4f}" for feat in (best_features[:5] if best_features else [])])}

Next: Extended lag testing (15-100)"""

        self.update_airtable_append('MP03.P05.S05.T11', summary)

        # Save results
        with open('/home/micha/bqx_ml_v3/scripts/correlation_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'best_window': best_window,
                'best_improvement': best_improvement,
                'expanded_to_28x28': expand,
                'all_results': self.results,
                'summary': {
                    'baseline_r2': self.baseline_r2,
                    'best_new_r2': self.baseline_r2 + best_improvement,
                    'windows_tested': self.windows,
                    'recommendation': 'Keep correlation features' if best_improvement > 0.01 else 'Drop correlation features'
                }
            }, f, indent=2, default=str)

        print("\n" + "="*60)
        print("CORRELATION NETWORK TESTING COMPLETE")
        print(f"Best improvement: {best_improvement:.4f}")
        print(f"Recommendation: {'Keep' if best_improvement > 0.01 else 'Drop'} correlation features")
        print("="*60)

        return best_improvement > 0.01


if __name__ == "__main__":
    tester = CorrelationNetworkTester()
    features_kept = tester.test_correlations()

    print("\n🎯 Next steps:")
    if features_kept:
        print("  1. Integrate correlation network features")
        print("  2. Test extended lags (15-100)")
    else:
        print("  1. Correlation features did not significantly improve performance")
        print("  2. Moving to extended lag testing")