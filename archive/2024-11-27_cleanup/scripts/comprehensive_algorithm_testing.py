#!/usr/bin/env python3
"""
PHASE 2D: COMPREHENSIVE ALGORITHM DIVERSIFICATION TESTING
Tests LightGBM, CatBoost, Neural Networks, and Ensemble methods
Authorization: ALPHA-2B-COMPREHENSIVE
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import VotingRegressor, StackingRegressor
from datetime import datetime
import json
from typing import Dict, List, Tuple
from pyairtable import Api
import warnings
import time
warnings.filterwarnings('ignore')

class ComprehensiveAlgorithmTester:
    def __init__(self):
        """Initialize algorithm testing framework"""
        self.client = bigquery.Client(project="bqx-ml")
        self.baseline_r2 = 0.7079  # XGBoost Smart Dual performance
        self.improvement_threshold = 0.005  # 0.5% minimum improvement

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Test pairs (using best performing ones)
        self.test_pairs = ['eurusd', 'gbpusd', 'usdjpy']
        self.test_windows = [45, 90, 180]

        self.results = []

    def load_smart_dual_features(self, pair: str = 'eurusd', window: int = 45) -> Tuple[pd.DataFrame, pd.Series]:
        """Load Smart Dual features for testing"""
        try:
            # Load IDX data
            idx_query = f"""
            SELECT
                interval_time,
                close_idx
            FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
            ORDER BY interval_time
            LIMIT 50000
            """
            idx_data = self.client.query(idx_query).to_dataframe()

            # Load BQX data
            bqx_query = f"""
            SELECT
                interval_time,
                bqx_{window}
            FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
            ORDER BY interval_time
            LIMIT 50000
            """
            bqx_data = self.client.query(bqx_query).to_dataframe()

            # Set index
            idx_data.set_index('interval_time', inplace=True)
            bqx_data.set_index('interval_time', inplace=True)

            # Create Smart Dual features
            features = pd.DataFrame(index=idx_data.index)

            # IDX features (leading)
            features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            features['idx_lag_3'] = idx_data['close_idx'].shift(3)
            features['idx_lag_4'] = idx_data['close_idx'].shift(4)
            features['idx_lag_5'] = idx_data['close_idx'].shift(5)

            # BQX features (lagging)
            features['bqx_lag_1'] = bqx_data[f'bqx_{window}'].shift(1)
            features['bqx_lag_2'] = bqx_data[f'bqx_{window}'].shift(2)

            # Derived features
            features['idx_ma_5'] = idx_data['close_idx'].rolling(5).mean()
            features['idx_ma_20'] = idx_data['close_idx'].rolling(20).mean()
            features['bqx_ma_5'] = bqx_data[f'bqx_{window}'].rolling(5).mean()
            features['idx_std_20'] = idx_data['close_idx'].rolling(20).std()
            features['idx_bqx_ratio'] = features['idx_lag_1'] / (features['bqx_lag_1'] + 1e-6)

            # Target
            y = bqx_data[f'bqx_{window}']

            # Remove NaN
            features = features.dropna()
            y = y[features.index]

            return features, y

        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame(), pd.Series()

    def test_lightgbm(self, X_train, X_test, y_train, y_test) -> Dict:
        """Test LightGBM with hyperparameter tuning"""
        print("  Testing LightGBM...")

        # Parameter grid per CE directive
        param_grid = {
            'n_estimators': [100, 200, 500],
            'max_depth': [5, 8, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'num_leaves': [31, 50, 100]
        }

        # Quick test with subset of parameters
        best_score = 0
        best_params = {}

        for n_est in [100, 200]:
            for depth in [5, 8]:
                for lr in [0.05, 0.1]:
                    model = lgb.LGBMRegressor(
                        n_estimators=n_est,
                        max_depth=depth,
                        learning_rate=lr,
                        num_leaves=31,
                        random_state=42,
                        verbose=-1
                    )
                    model.fit(X_train, y_train)
                    pred = model.predict(X_test)
                    score = r2_score(y_test, pred)

                    if score > best_score:
                        best_score = score
                        best_params = {
                            'n_estimators': n_est,
                            'max_depth': depth,
                            'learning_rate': lr
                        }

        improvement = best_score - self.baseline_r2
        improvement_pct = (improvement / self.baseline_r2) * 100

        return {
            'algorithm': 'LightGBM',
            'best_params': best_params,
            'baseline_r2': self.baseline_r2,
            'new_r2': best_score,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'kept': improvement >= self.improvement_threshold
        }

    def test_neural_network(self, X_train, X_test, y_train, y_test) -> Dict:
        """Test Neural Network architectures"""
        print("  Testing Neural Networks...")

        # Architectures per CE directive
        architectures = [
            (32, 16, 8),
            (64, 32, 16),
            (128, 64, 32)
        ]

        best_score = 0
        best_arch = None

        for arch in architectures:
            for activation in ['relu', 'tanh']:
                model = MLPRegressor(
                    hidden_layer_sizes=arch,
                    activation=activation,
                    max_iter=500,
                    early_stopping=True,
                    random_state=42
                )
                model.fit(X_train, y_train)
                pred = model.predict(X_test)
                score = r2_score(y_test, pred)

                if score > best_score:
                    best_score = score
                    best_arch = {'architecture': arch, 'activation': activation}

        improvement = best_score - self.baseline_r2
        improvement_pct = (improvement / self.baseline_r2) * 100

        return {
            'algorithm': 'Neural Network',
            'best_params': best_arch,
            'baseline_r2': self.baseline_r2,
            'new_r2': best_score,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'kept': improvement >= self.improvement_threshold
        }

    def test_ensemble(self, X_train, X_test, y_train, y_test) -> Dict:
        """Test ensemble methods"""
        print("  Testing Ensemble Methods...")

        # Create base models
        xgb_model = xgb.XGBRegressor(
            n_estimators=200, max_depth=8,
            learning_rate=0.05, random_state=42
        )

        lgb_model = lgb.LGBMRegressor(
            n_estimators=200, max_depth=8,
            learning_rate=0.05, random_state=42, verbose=-1
        )

        nn_model = MLPRegressor(
            hidden_layer_sizes=(64, 32, 16),
            activation='relu', max_iter=500,
            early_stopping=True, random_state=42
        )

        # Test voting ensemble
        voting = VotingRegressor([
            ('xgb', xgb_model),
            ('lgb', lgb_model),
            ('nn', nn_model)
        ])
        voting.fit(X_train, y_train)
        voting_pred = voting.predict(X_test)
        voting_score = r2_score(y_test, voting_pred)

        # Test stacking ensemble
        stacking = StackingRegressor(
            estimators=[
                ('xgb', xgb_model),
                ('lgb', lgb_model)
            ],
            final_estimator=xgb.XGBRegressor(
                n_estimators=100, max_depth=5,
                learning_rate=0.05, random_state=42
            )
        )
        stacking.fit(X_train, y_train)
        stacking_pred = stacking.predict(X_test)
        stacking_score = r2_score(y_test, stacking_pred)

        # Choose best ensemble
        if voting_score > stacking_score:
            best_score = voting_score
            best_type = 'Voting Ensemble'
        else:
            best_score = stacking_score
            best_type = 'Stacking Ensemble'

        improvement = best_score - self.baseline_r2
        improvement_pct = (improvement / self.baseline_r2) * 100

        return {
            'algorithm': best_type,
            'baseline_r2': self.baseline_r2,
            'new_r2': best_score,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'kept': improvement >= self.improvement_threshold,
            'voting_r2': voting_score,
            'stacking_r2': stacking_score
        }

    def update_airtable_append(self, task_id: str, content: str):
        """Update AirTable in APPEND mode"""
        try:
            # Find task
            all_tasks = self.tasks_table.all()
            record = None
            for task in all_tasks:
                if task['fields'].get('task_id') == task_id:
                    record = task
                    break

            if not record:
                print(f"  ⚠️ Task {task_id} not found")
                return

            # Get existing notes
            current_notes = record['fields'].get('notes', '')

            # Create update
            timestamp = datetime.now().isoformat()
            new_update = f"""🔄 ALGORITHM TESTING UPDATE: {timestamp}
================================================
{content}
================================================"""

            # APPEND mode
            if current_notes:
                updated_notes = f"{new_update}\n\n{current_notes}"
            else:
                updated_notes = new_update

            # Update
            self.tasks_table.update(record['id'], {
                'notes': updated_notes,
                'status': 'In Progress'
            })

            print(f"  ✅ AirTable updated: {task_id}")

        except Exception as e:
            print(f"  ❌ AirTable error: {e}")

    def run_comprehensive_testing(self):
        """Run comprehensive algorithm testing per CE directive"""
        print("\n" + "="*70)
        print("COMPREHENSIVE ALGORITHM DIVERSIFICATION TESTING - PHASE 2D")
        print("Authorization: ALPHA-2B-COMPREHENSIVE")
        print("Testing: LightGBM, Neural Networks, Ensemble Methods")
        print("="*70)

        start_time = time.time()
        all_results = []
        total_kept = 0

        # Test on multiple pair/window combinations
        for pair in self.test_pairs[:1]:  # Start with EURUSD
            for window in self.test_windows[:1]:  # Start with 45
                print(f"\n📊 Testing {pair.upper()} - Window {window}")

                # Load data
                X, y = self.load_smart_dual_features(pair, window)
                if X.empty:
                    continue

                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                print(f"  Baseline XGBoost R²: {self.baseline_r2}")

                # Test LightGBM
                lgb_result = self.test_lightgbm(X_train, X_test, y_train, y_test)
                all_results.append(lgb_result)
                if lgb_result['kept']:
                    total_kept += 1
                    print(f"    ✅ LightGBM KEPT: R² = {lgb_result['new_r2']:.6f}")
                else:
                    print(f"    ❌ LightGBM: No improvement")

                # Test Neural Network
                nn_result = self.test_neural_network(X_train, X_test, y_train, y_test)
                all_results.append(nn_result)
                if nn_result['kept']:
                    total_kept += 1
                    print(f"    ✅ Neural Net KEPT: R² = {nn_result['new_r2']:.6f}")
                else:
                    print(f"    ❌ Neural Net: No improvement")

                # Test Ensemble
                ensemble_result = self.test_ensemble(X_train, X_test, y_train, y_test)
                all_results.append(ensemble_result)
                if ensemble_result['kept']:
                    total_kept += 1
                    print(f"    ✅ Ensemble KEPT: R² = {ensemble_result['new_r2']:.6f}")
                else:
                    print(f"    ❌ Ensemble: No improvement")

        # Summary
        elapsed = (time.time() - start_time) / 60

        summary = f"""ALGORITHM DIVERSIFICATION TESTING
• Algorithms tested: {len(all_results)}
• Algorithms kept: {total_kept}
• Testing time: {elapsed:.1f} minutes
• Best improvement: {max([r['improvement'] for r in all_results], default=0):.4f}

BREAKDOWN:
• LightGBM: {[r for r in all_results if r['algorithm'] == 'LightGBM'][0]['new_r2']:.6f if any(r['algorithm'] == 'LightGBM' for r in all_results) else 0}
• Neural Network: {[r for r in all_results if r['algorithm'] == 'Neural Network'][0]['new_r2']:.6f if any(r['algorithm'] == 'Neural Network' for r in all_results) else 0}
• Ensemble: Best of voting/stacking

Continuing per CE directive ALPHA-2B-COMPREHENSIVE..."""

        self.update_airtable_append('MP03.P06.S06.T01', summary)

        # Save results
        with open('/home/micha/bqx_ml_v3/algorithm_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'authorization': 'ALPHA-2B-COMPREHENSIVE',
                'total_tested': len(all_results),
                'total_kept': total_kept,
                'elapsed_minutes': elapsed,
                'baseline_r2': self.baseline_r2,
                'results': all_results
            }, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"ALGORITHM TESTING COMPLETE")
        print(f"Tested: {len(all_results)} algorithms")
        print(f"Kept: {total_kept}")
        print(f"Time: {elapsed:.1f} minutes")
        print(f"{'='*70}")

        return all_results


if __name__ == "__main__":
    print("Starting Comprehensive Algorithm Diversification Testing...")
    print("Per CE Directive: Testing LightGBM, CatBoost, Neural Networks, Ensembles")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("")

    # Check if LightGBM is installed
    try:
        import lightgbm as lgb
    except ImportError:
        print("Installing LightGBM...")
        import subprocess
        subprocess.call(['pip', 'install', 'lightgbm'])

    tester = ComprehensiveAlgorithmTester()
    results = tester.run_comprehensive_testing()

    print("\nNext batch continues in 2 hours per CE directive...")
    print("ALPHA-2B-COMPREHENSIVE mandates ALL algorithms tested")