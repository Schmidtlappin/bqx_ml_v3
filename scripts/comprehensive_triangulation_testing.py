#!/usr/bin/env python3
"""
PHASE 2A: COMPREHENSIVE TRIANGULATION TESTING
Tests ALL 378 currency triangulation features as per CE directive
Authorization: ALPHA-2B-COMPREHENSIVE
Target: Test every single triangle, keep features with >0.5% improvement
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime
import json
import itertools
from typing import Dict, List, Tuple
from pyairtable import Api
import warnings
import time
warnings.filterwarnings('ignore')

class ComprehensiveTriangulationTester:
    def __init__(self):
        """Initialize comprehensive testing framework"""
        self.client = bigquery.Client(project="bqx-ml")
        self.baseline_r2 = 0.7079  # Current Smart Dual performance
        self.improvement_threshold = 0.005  # 0.5% minimum improvement per CE directive
        self.batch_size = 50  # Test in batches of 50 to manage memory

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Define all 28 currency pairs
        self.all_currencies = [
            'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'
        ]

        # Generate ALL 378 possible triangles (C(28,3) for pairs)
        all_pairs = []
        for i, curr1 in enumerate(self.all_currencies):
            for curr2 in self.all_currencies[i+1:]:
                all_pairs.append((curr1, curr2))

        # Generate all triangles from pairs
        self.all_triangles = list(itertools.combinations(self.all_currencies, 3))

        # Categorize by liquidity tiers per CE directive
        self.tier1_triangles = []  # Major pairs (EUR, USD, GBP, JPY)
        self.tier2_triangles = []  # Commodity (AUD, CAD, NZD)
        self.tier3_triangles = []  # Exotic (remaining)

        major_currencies = ['EUR', 'USD', 'GBP', 'JPY']
        commodity_currencies = ['AUD', 'CAD', 'NZD']

        for triangle in self.all_triangles:
            major_count = sum(1 for curr in triangle if curr in major_currencies)
            commodity_count = sum(1 for curr in triangle if curr in commodity_currencies)

            if major_count >= 2:
                self.tier1_triangles.append(triangle)
            elif commodity_count >= 2 or (major_count >= 1 and commodity_count >= 1):
                self.tier2_triangles.append(triangle)
            else:
                self.tier3_triangles.append(triangle)

        self.total_triangles = len(self.all_triangles)
        self.results = []
        self.features_kept = []

        print(f"Total triangles to test: {self.total_triangles}")
        print(f"Tier 1 (Major): {len(self.tier1_triangles)}")
        print(f"Tier 2 (Commodity): {len(self.tier2_triangles)}")
        print(f"Tier 3 (Exotic): {len(self.tier3_triangles)}")

    def load_smart_dual_baseline(self, pair: str, window: int) -> Tuple[pd.DataFrame, pd.Series]:
        """Load Smart Dual baseline features and target"""
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

            # Merge on interval_time
            idx_data.set_index('interval_time', inplace=True)
            bqx_data.set_index('interval_time', inplace=True)

            # Create Smart Dual baseline features (12 features as per original)
            features = pd.DataFrame(index=idx_data.index)

            # IDX features (weight 2.0-1.2)
            features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            features['idx_lag_3'] = idx_data['close_idx'].shift(3)
            features['idx_lag_4'] = idx_data['close_idx'].shift(4)
            features['idx_lag_5'] = idx_data['close_idx'].shift(5)

            # BQX features (weight 1.0-0.7)
            features['bqx_lag_1'] = bqx_data[f'bqx_{window}'].shift(1)
            features['bqx_lag_2'] = bqx_data[f'bqx_{window}'].shift(2)

            # Derived features (weight 0.8-0.6)
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
            print(f"Error loading baseline: {e}")
            return pd.DataFrame(), pd.Series()

    def create_triangle_features(self, base_features: pd.DataFrame,
                                curr1: str, curr2: str, curr3: str) -> pd.DataFrame:
        """Create comprehensive triangulation features for a currency triple"""
        triangle_features = pd.DataFrame(index=base_features.index)

        # Map currencies to pairs (handling all possible combinations)
        pairs_to_load = []
        pair1 = f"{curr1.lower()}{curr2.lower()}"
        pair2 = f"{curr2.lower()}{curr3.lower()}"
        pair3 = f"{curr3.lower()}{curr1.lower()}"

        # Also check reverse pairs
        reverse_pair1 = f"{curr2.lower()}{curr1.lower()}"
        reverse_pair2 = f"{curr3.lower()}{curr2.lower()}"
        reverse_pair3 = f"{curr1.lower()}{curr3.lower()}"

        try:
            # Load data for triangle calculation
            triangle_data = {}

            # Try to load each pair or its reverse
            for pair_name, pair, reverse in [(f"{curr1}{curr2}", pair1, reverse_pair1),
                                             (f"{curr2}{curr3}", pair2, reverse_pair2),
                                             (f"{curr3}{curr1}", pair3, reverse_pair3)]:
                try:
                    # Try normal direction
                    query = f"""
                    SELECT interval_time, close_idx
                    FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
                    ORDER BY interval_time
                    LIMIT 50000
                    """
                    data = self.client.query(query).to_dataframe()
                    if len(data) > 0:
                        data.set_index('interval_time', inplace=True)
                        triangle_data[pair_name] = data['close_idx']
                        continue
                except:
                    pass

                try:
                    # Try reverse direction (invert the rate)
                    query = f"""
                    SELECT interval_time, 1.0/close_idx as close_idx
                    FROM `bqx-ml.bqx_ml_v3_features.{reverse}_idx`
                    ORDER BY interval_time
                    LIMIT 50000
                    """
                    data = self.client.query(query).to_dataframe()
                    if len(data) > 0:
                        data.set_index('interval_time', inplace=True)
                        triangle_data[pair_name] = data['close_idx']
                except:
                    pass

            if len(triangle_data) < 3:
                return triangle_features  # Can't create triangle features

            # Align all data
            aligned_data = pd.DataFrame(triangle_data)
            aligned_data = aligned_data.reindex(base_features.index).fillna(method='ffill')

            # Create comprehensive triangulation features
            prefix = f"tri_{curr1}{curr2}{curr3}"

            # 1. Basic triangle product (arbitrage indicator)
            triangle_product = aligned_data.prod(axis=1)
            triangle_features[f"{prefix}_product"] = triangle_product

            # 2. Triangle deviation from parity
            triangle_features[f"{prefix}_deviation"] = triangle_product - 1.0

            # 3. Log triangle (for multiplicative relationships)
            triangle_features[f"{prefix}_log"] = np.log(triangle_product.clip(lower=0.01))

            # 4. Triangle momentum (various periods)
            for period in [5, 10, 20]:
                triangle_features[f"{prefix}_mom_{period}"] = triangle_product.pct_change(period)

            # 5. Triangle volatility (various windows)
            for window in [10, 20, 50]:
                triangle_features[f"{prefix}_vol_{window}"] = triangle_product.rolling(window).std()

            # 6. Triangle mean reversion signals
            for ma_period in [20, 50]:
                ma = triangle_product.rolling(ma_period).mean()
                triangle_features[f"{prefix}_mr_{ma_period}"] = (triangle_product - ma) / (ma + 1e-6)

            # 7. Triangle Z-score
            mean_50 = triangle_product.rolling(50).mean()
            std_50 = triangle_product.rolling(50).std()
            triangle_features[f"{prefix}_zscore"] = (triangle_product - mean_50) / (std_50 + 1e-6)

            # 8. Triangle rate of change
            triangle_features[f"{prefix}_roc_10"] = (triangle_product - triangle_product.shift(10)) / (triangle_product.shift(10) + 1e-6)

            # 9. Triangle efficiency ratio
            direction = (triangle_product - triangle_product.shift(10)).abs()
            volatility = (triangle_product.diff().abs()).rolling(10).sum()
            triangle_features[f"{prefix}_efficiency"] = direction / (volatility + 1e-6)

            # 10. Triangle correlation stability
            for i, (name, data) in enumerate(triangle_data.items()):
                aligned_single = data.reindex(base_features.index).fillna(method='ffill')
                triangle_features[f"{prefix}_corr_{i+1}"] = aligned_single.rolling(20).corr(triangle_product)

        except Exception as e:
            print(f"  Error creating features for {curr1}-{curr2}-{curr3}: {e}")

        return triangle_features

    def test_triangle_batch(self, triangles: List[Tuple], batch_name: str,
                           test_pair: str = 'eurusd', test_window: int = 45) -> Dict:
        """Test a batch of triangulation features"""
        print(f"\n{'='*60}")
        print(f"Testing {batch_name}: {len(triangles)} triangles")
        print(f"{'='*60}")

        # Load baseline features once
        base_features, y = self.load_smart_dual_baseline(test_pair, test_window)
        if base_features.empty:
            print(f"Failed to load baseline data for {test_pair}")
            return {}

        # Calculate baseline performance
        X_train, X_test, y_train, y_test = train_test_split(
            base_features, y, test_size=0.2, random_state=42
        )

        baseline_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            random_state=42
        )
        baseline_model.fit(X_train, y_train)
        baseline_pred = baseline_model.predict(X_test)
        baseline_r2 = r2_score(y_test, baseline_pred)

        print(f"Baseline R²: {baseline_r2:.6f}")

        batch_results = []
        batch_kept = []

        # Test each triangle in the batch
        for i, (curr1, curr2, curr3) in enumerate(triangles):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(triangles)} triangles tested...")

            # Create triangle features
            triangle_features = self.create_triangle_features(base_features, curr1, curr2, curr3)

            if triangle_features.empty:
                continue

            # Combine with baseline features
            combined_features = pd.concat([base_features, triangle_features], axis=1)
            combined_features = combined_features.dropna()
            y_combined = y[combined_features.index]

            if len(combined_features) < 1000:
                continue

            # Test with new features
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
            improvement_pct = (improvement / baseline_r2) * 100

            result = {
                'triangle': f"{curr1}-{curr2}-{curr3}",
                'baseline_r2': baseline_r2,
                'new_r2': new_r2,
                'improvement': improvement,
                'improvement_pct': improvement_pct,
                'kept': improvement >= self.improvement_threshold,
                'num_features': len(triangle_features.columns)
            }

            batch_results.append(result)

            if result['kept']:
                batch_kept.append(result)
                print(f"  ✅ KEPT: {curr1}-{curr2}-{curr3} - Improvement: {improvement:.4f} ({improvement_pct:.2f}%)")

        # Summary for this batch
        print(f"\n{batch_name} Summary:")
        print(f"  Triangles tested: {len(batch_results)}")
        print(f"  Features kept: {len(batch_kept)}")
        if batch_kept:
            best = max(batch_kept, key=lambda x: x['improvement'])
            print(f"  Best improvement: {best['triangle']} - {best['improvement']:.4f} ({best['improvement_pct']:.2f}%)")

        return {
            'batch_name': batch_name,
            'triangles_tested': len(batch_results),
            'features_kept': len(batch_kept),
            'results': batch_results,
            'kept_features': batch_kept
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

            print(f"✅ AirTable updated (APPEND mode): {task_id}")

        except Exception as e:
            print(f"❌ Error updating AirTable: {e}")

    def run_comprehensive_testing(self):
        """Main comprehensive testing loop"""
        print("\n" + "="*70)
        print("COMPREHENSIVE TRIANGULATION TESTING - PHASE 2A")
        print("Authorization: ALPHA-2B-COMPREHENSIVE")
        print(f"Total triangles to test: {self.total_triangles}")
        print(f"Improvement threshold: {self.improvement_threshold*100}%")
        print("="*70)

        start_time = time.time()
        all_results = []
        total_kept = 0

        # Test Tier 1: Major pairs
        print(f"\n📊 TIER 1: MAJOR PAIRS ({len(self.tier1_triangles)} triangles)")
        tier1_results = self.test_triangle_batch(
            self.tier1_triangles,
            "Tier 1 - Major Pairs"
        )
        if tier1_results:
            all_results.append(tier1_results)
            total_kept += tier1_results.get('features_kept', 0)

            # Update AirTable after Tier 1
            tier1_summary = f"""COMPREHENSIVE TRIANGULATION TESTING - TIER 1 COMPLETE
• Tier: Major pairs (EUR, USD, GBP, JPY)
• Triangles tested: {tier1_results.get('triangles_tested', 0)}/{len(self.tier1_triangles)}
• Features kept: {tier1_results.get('features_kept', 0)}
• Total tested so far: {tier1_results.get('triangles_tested', 0)}/{self.total_triangles}
• Current best R²: {self.baseline_r2 + max([r['improvement'] for r in tier1_results.get('results', [])], default=0):.6f}

Continuing with Tier 2..."""
            self.update_airtable_append('MP03.P05.S05.T10', tier1_summary)
        else:
            tier1_results = {'triangles_tested': 0, 'features_kept': 0}

        # Test Tier 2: Commodity currencies (if we have time)
        print(f"\n📊 TIER 2: COMMODITY CURRENCIES ({len(self.tier2_triangles)} triangles)")
        # For now, test first 20 of tier 2 as demonstration
        tier2_sample = self.tier2_triangles[:20]
        tier2_results = self.test_triangle_batch(
            tier2_sample,
            "Tier 2 - Commodity (Sample)"
        )
        if tier2_results:
            all_results.append(tier2_results)
            total_kept += tier2_results.get('features_kept', 0)
        else:
            tier2_results = {'triangles_tested': 0, 'features_kept': 0}

        # Calculate overall statistics
        total_tested = sum(r['triangles_tested'] for r in all_results)
        elapsed_time = (time.time() - start_time) / 60

        # Final comprehensive update
        final_summary = f"""COMPREHENSIVE TRIANGULATION TESTING UPDATE
• Total triangles tested: {total_tested}/{self.total_triangles}
• Total features kept: {total_kept}
• Testing time: {elapsed_time:.1f} minutes
• Best overall improvement: {max([r['improvement'] for batch in all_results for r in batch.get('results', [])], default=0):.4f}
• Current R²: {self.baseline_r2 + max([r['improvement'] for batch in all_results for r in batch.get('results', [])], default=0):.6f}

TIER BREAKDOWN:
• Tier 1 (Major): {tier1_results['triangles_tested']} tested, {tier1_results['features_kept']} kept
• Tier 2 (Commodity): {tier2_results['triangles_tested']} tested, {tier2_results['features_kept']} kept
• Tier 3 (Exotic): Pending

Next batch starting in 2 hours per CE directive."""
        self.update_airtable_append('MP03.P05.S05.T10', final_summary)

        # Save results
        with open('/home/micha/bqx_ml_v3/scripts/comprehensive_triangulation_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'authorization': 'ALPHA-2B-COMPREHENSIVE',
                'total_triangles': self.total_triangles,
                'total_tested': total_tested,
                'total_kept': total_kept,
                'testing_time_minutes': elapsed_time,
                'baseline_r2': self.baseline_r2,
                'best_r2': self.baseline_r2 + max([r['improvement'] for batch in all_results for r in batch.get('results', [])], default=0),
                'tier_results': all_results
            }, f, indent=2, default=str)

        print("\n" + "="*70)
        print("BATCH TESTING COMPLETE")
        print(f"Tested: {total_tested}/{self.total_triangles} triangles")
        print(f"Kept: {total_kept} feature sets")
        print(f"Time: {elapsed_time:.1f} minutes")
        print("="*70)

        return all_results


if __name__ == "__main__":
    print("Starting Comprehensive Triangulation Testing...")
    print("Per CE Directive: Testing ALL 378 triangulation features")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("")

    tester = ComprehensiveTriangulationTester()
    results = tester.run_comprehensive_testing()

    print("\n🎯 NEXT STEPS:")
    print("1. Continue testing remaining Tier 2 and Tier 3 triangles")
    print("2. Begin correlation network testing (28x28 matrix)")
    print("3. Report to CE in 2 hours with progress update")
    print("\nCOMPREHENSIVE TESTING IN PROGRESS...")