#!/usr/bin/env python3
"""
PHASE 2: TRIANGULATION FEATURE TESTING
Tests currency triangulation features to improve model performance
Authorization: ALPHA-2-PROCEED
Target: >1% R² improvement per feature to keep
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from datetime import datetime
import json
import itertools
from typing import Dict, List, Tuple
from pyairtable import Api
import warnings
warnings.filterwarnings('ignore')

class TriangulationTester:
    def __init__(self):
        """Initialize triangulation testing framework"""
        self.client = bigquery.Client(project="bqx-ml")
        self.baseline_r2 = 0.7079  # Current Smart Dual performance
        self.improvement_threshold = 0.01  # 1% minimum improvement to keep
        self.results = []

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Define major currencies for triangulation
        self.major_currencies = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']

        # Generate all possible triangles (C(8,3) = 56 major triangles)
        self.triangles = list(itertools.combinations(self.major_currencies, 3))

    def create_triangulation_features(self, base_features: pd.DataFrame,
                                     curr1: str, curr2: str, curr3: str) -> pd.DataFrame:
        """
        Create triangulation features for a currency triple
        Triangle arbitrage: curr1/curr2 * curr2/curr3 * curr3/curr1 should equal 1
        """
        features = base_features.copy()

        # Define pair mappings
        pair1 = f"{curr1.lower()}{curr2.lower()}"
        pair2 = f"{curr2.lower()}{curr3.lower()}"
        pair3 = f"{curr3.lower()}{curr1.lower()}"

        # Reverse pairs if needed (handle both directions)
        reverse_pair1 = f"{curr2.lower()}{curr1.lower()}"
        reverse_pair2 = f"{curr3.lower()}{curr2.lower()}"
        reverse_pair3 = f"{curr1.lower()}{curr3.lower()}"

        try:
            # Load data for each pair in the triangle
            data_loaded = {}
            for pair, reverse in [(pair1, reverse_pair1),
                                 (pair2, reverse_pair2),
                                 (pair3, reverse_pair3)]:
                try:
                    # Try normal direction
                    query = f"""
                    SELECT interval_id, close_idx
                    FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
                    ORDER BY interval_id
                    LIMIT 50000
                    """
                    data = self.client.query(query).to_dataframe()
                    if len(data) > 0:
                        data_loaded[pair] = data
                        continue
                except:
                    pass

                try:
                    # Try reverse direction
                    query = f"""
                    SELECT interval_id, 1.0/close_idx as close_idx
                    FROM `bqx-ml.bqx_ml_v3_features.{reverse}_idx`
                    ORDER BY interval_id
                    LIMIT 50000
                    """
                    data = self.client.query(query).to_dataframe()
                    if len(data) > 0:
                        data_loaded[pair] = data
                except:
                    return features  # Skip if pair not available

            if len(data_loaded) < 3:
                return features  # Need all three pairs

            # Align data by interval_id
            merged = None
            for i, (pair, data) in enumerate(data_loaded.items()):
                data = data.rename(columns={'close_idx': f'close_{i+1}'})
                if merged is None:
                    merged = data
                else:
                    merged = merged.merge(data, on='interval_id', how='inner')

            if len(merged) < 1000:
                return features  # Not enough data

            # Create triangulation features
            # 1. Triangle product (should be close to 1 in efficient markets)
            features[f'triangle_{curr1}_{curr2}_{curr3}_product'] = (
                merged['close_1'] * merged['close_2'] * merged['close_3']
            )

            # 2. Triangle deviation from parity
            features[f'triangle_{curr1}_{curr2}_{curr3}_deviation'] = (
                features[f'triangle_{curr1}_{curr2}_{curr3}_product'] - 1.0
            )

            # 3. Log triangle (for multiplicative relationships)
            features[f'triangle_{curr1}_{curr2}_{curr3}_log'] = np.log(
                features[f'triangle_{curr1}_{curr2}_{curr3}_product'].clip(lower=0.01)
            )

            # 4. Triangle momentum (change in triangle over time)
            features[f'triangle_{curr1}_{curr2}_{curr3}_momentum'] = (
                features[f'triangle_{curr1}_{curr2}_{curr3}_product'].pct_change(periods=10)
            )

            # 5. Triangle volatility
            features[f'triangle_{curr1}_{curr2}_{curr3}_volatility'] = (
                features[f'triangle_{curr1}_{curr2}_{curr3}_product'].rolling(20).std()
            )

            # 6. Triangle mean reversion signal
            triangle_ma = features[f'triangle_{curr1}_{curr2}_{curr3}_product'].rolling(50).mean()
            features[f'triangle_{curr1}_{curr2}_{curr3}_mean_reversion'] = (
                (features[f'triangle_{curr1}_{curr2}_{curr3}_product'] - triangle_ma) / triangle_ma
            )

            print(f"  ✅ Created 6 features for {curr1}-{curr2}-{curr3} triangle")

        except Exception as e:
            print(f"  ⚠️ Could not create features for {curr1}-{curr2}-{curr3}: {e}")

        return features

    def test_feature_improvement(self, pair: str, window: int,
                                new_features: pd.DataFrame) -> Dict:
        """Test if new features improve model performance"""

        # Load base Smart Dual features
        try:
            # Get the baseline model data
            idx_query = f"""
            SELECT * FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
            ORDER BY interval_id
            LIMIT 50000
            """
            idx_data = self.client.query(idx_query).to_dataframe()

            bqx_query = f"""
            SELECT * FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
            ORDER BY interval_id
            LIMIT 50000
            """
            bqx_data = self.client.query(bqx_query).to_dataframe()

            # Recreate Smart Dual features (simplified)
            base_features = pd.DataFrame(index=idx_data.index)
            base_features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            base_features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            base_features['bqx_lag_1'] = bqx_data[f'bqx_{window}'].shift(1)
            base_features['bqx_lag_2'] = bqx_data[f'bqx_{window}'].shift(2)
            base_features['idx_ma_5'] = idx_data['close_idx'].rolling(5).mean()
            base_features['bqx_ma_5'] = bqx_data[f'bqx_{window}'].rolling(5).mean()

            # Target variable
            y = bqx_data[f'bqx_{window}']

            # Test baseline model
            base_features = base_features.dropna()
            y_base = y[base_features.index]

            X_train_base, X_test_base, y_train_base, y_test_base = train_test_split(
                base_features, y_base, test_size=0.2, random_state=42
            )

            base_model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.05,
                random_state=42
            )
            base_model.fit(X_train_base, y_train_base)
            base_pred = base_model.predict(X_test_base)
            baseline_r2 = r2_score(y_test_base, base_pred)

            # Test with new features
            combined_features = pd.concat([base_features, new_features], axis=1)
            combined_features = combined_features.dropna()
            y_combined = y[combined_features.index]

            X_train_new, X_test_new, y_train_new, y_test_new = train_test_split(
                combined_features, y_combined, test_size=0.2, random_state=42
            )

            new_model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.05,
                random_state=42
            )
            new_model.fit(X_train_new, y_train_new)
            new_pred = new_model.predict(X_test_new)
            new_r2 = r2_score(y_test_new, new_pred)

            improvement = new_r2 - baseline_r2

            return {
                'baseline_r2': baseline_r2,
                'new_r2': new_r2,
                'improvement': improvement,
                'improvement_pct': (improvement / baseline_r2) * 100,
                'keep_features': improvement >= self.improvement_threshold
            }

        except Exception as e:
            print(f"  ❌ Error testing features: {e}")
            return {
                'baseline_r2': self.baseline_r2,
                'new_r2': self.baseline_r2,
                'improvement': 0,
                'improvement_pct': 0,
                'keep_features': False
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

    def test_triangulations(self):
        """Main testing loop for triangulation features"""

        print("\n" + "="*60)
        print("PHASE 2: TRIANGULATION FEATURE TESTING")
        print("Authorization: ALPHA-2-PROCEED")
        print(f"Baseline R²: {self.baseline_r2}")
        print(f"Improvement threshold: {self.improvement_threshold*100}%")
        print("="*60)

        # Start with EUR-GBP-USD (most liquid)
        priority_triangles = [
            ('EUR', 'GBP', 'USD'),
            ('EUR', 'USD', 'JPY'),
            ('USD', 'JPY', 'GBP'),
            ('EUR', 'JPY', 'CHF'),
            ('USD', 'CHF', 'GBP'),
            ('EUR', 'AUD', 'USD'),
            ('GBP', 'JPY', 'CHF'),
            ('USD', 'CAD', 'JPY'),
            ('EUR', 'CAD', 'GBP'),
            ('AUD', 'NZD', 'USD')
        ]

        # Test on EURUSD pair with 45-minute window first
        test_pair = 'eurusd'
        test_window = 45

        print(f"\n📊 Testing on {test_pair.upper()} with {test_window}-minute window")
        print("-"*60)

        kept_features = []
        tested_count = 0

        for triangle in priority_triangles[:10]:  # First 10 as required
            tested_count += 1
            curr1, curr2, curr3 = triangle

            print(f"\n[{tested_count}/10] Testing {curr1}-{curr2}-{curr3} triangle")

            # Create base features dataframe
            base_features = pd.DataFrame(index=range(50000))

            # Add triangulation features
            new_features = self.create_triangulation_features(
                base_features, curr1, curr2, curr3
            )

            # Test improvement
            result = self.test_feature_improvement(test_pair, test_window, new_features)

            print(f"  Baseline R²: {result['baseline_r2']:.4f}")
            print(f"  With triangle: {result['new_r2']:.4f}")
            print(f"  Improvement: {result['improvement']:.4f} ({result['improvement_pct']:.2f}%)")

            if result['keep_features']:
                print(f"  ✅ KEEPING: Exceeds {self.improvement_threshold*100}% threshold")
                kept_features.append({
                    'triangle': f"{curr1}-{curr2}-{curr3}",
                    'improvement': result['improvement'],
                    'new_r2': result['new_r2']
                })
            else:
                print(f"  ❌ DROPPING: Below threshold")

            self.results.append({
                'triangle': f"{curr1}-{curr2}-{curr3}",
                'baseline_r2': result['baseline_r2'],
                'new_r2': result['new_r2'],
                'improvement': result['improvement'],
                'improvement_pct': result['improvement_pct'],
                'kept': result['keep_features']
            })

        # Update AirTable with results
        summary = f"""TRIANGULATION TESTING - FIRST 10 TRIANGLES
• Triangles tested: {tested_count}/378
• Features kept: {len(kept_features)}
• Best improvement: {max([r['improvement'] for r in self.results]):.4f}
• Average R² with kept features: {np.mean([f['new_r2'] for f in kept_features]) if kept_features else self.baseline_r2:.4f}
• Current overall R²: {np.mean([f['new_r2'] for f in kept_features]) if kept_features else self.baseline_r2:.4f}

Triangles tested:
{chr(10).join([f"  - {r['triangle']}: {'✅ KEPT' if r['kept'] else '❌ DROPPED'} (Δ={r['improvement']:.4f})" for r in self.results])}

Next: Testing triangles 11-20"""

        self.update_airtable_append('MP03.P05.S05.T10', summary)

        # Save results
        with open('/home/micha/bqx_ml_v3/scripts/triangulation_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'tested_count': tested_count,
                'kept_features': kept_features,
                'all_results': self.results,
                'summary': {
                    'baseline_r2': self.baseline_r2,
                    'best_improvement': max([r['improvement'] for r in self.results]) if self.results else 0,
                    'features_kept': len(kept_features),
                    'average_new_r2': np.mean([f['new_r2'] for f in kept_features]) if kept_features else self.baseline_r2
                }
            }, f, indent=2, default=str)

        print("\n" + "="*60)
        print("TRIANGULATION TESTING - PHASE 1 COMPLETE")
        print(f"Tested: {tested_count} triangles")
        print(f"Kept: {len(kept_features)} feature sets")
        print(f"Best R² achieved: {max([r['new_r2'] for r in self.results]) if self.results else self.baseline_r2:.4f}")
        print("="*60)

        return kept_features


if __name__ == "__main__":
    tester = TriangulationTester()
    kept_features = tester.test_triangulations()

    print("\n🎯 Next steps:")
    if kept_features:
        print(f"  1. Integrate {len(kept_features)} kept triangulation features")
        print("  2. Test triangles 11-378")
        print("  3. Move to correlation network analysis")
    else:
        print("  1. Triangulation features did not improve performance")
        print("  2. Moving directly to correlation network analysis")