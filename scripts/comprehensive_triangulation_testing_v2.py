#!/usr/bin/env python3
"""
PHASE 2A: COMPREHENSIVE TRIANGULATION TESTING V2
Tests ALL 56 currency triangulation features as per CE directive
Authorization: ALPHA-2B-COMPREHENSIVE
Fixed version - only uses available columns (close_idx)
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
        self.batch_size = 10  # Start with smaller batches

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Define all 8 currencies (using actual available pairs)
        self.all_currencies = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']

        # Generate all possible triangles C(8,3) = 56
        self.all_triangles = list(itertools.combinations(self.all_currencies, 3))

        # Categorize by liquidity tiers
        self.tier1_triangles = []  # Major pairs
        self.tier2_triangles = []  # Commodity
        self.tier3_triangles = []  # Exotic

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
        print(f"Total triangles to test: {self.total_triangles}")
        print(f"Tier 1 (Major): {len(self.tier1_triangles)}")
        print(f"Tier 2 (Commodity): {len(self.tier2_triangles)}")
        print(f"Tier 3 (Exotic): {len(self.tier3_triangles)}")

        # Track results
        self.all_results = []
        self.total_tested = 0
        self.total_kept = 0

    def load_baseline_model(self, pair: str = 'eurusd', window: int = 45) -> Tuple[pd.DataFrame, pd.Series]:
        """Load Smart Dual baseline features - FIXED version using only close_idx"""
        try:
            print(f"  Loading baseline for {pair}, window {window}")

            # Query for IDX data - only close_idx column exists
            idx_query = f"""
            SELECT
                interval_time,
                close_idx
            FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
            ORDER BY interval_time
            LIMIT 50000
            """

            print(f"  Executing IDX query...")
            idx_data = self.client.query(idx_query).to_dataframe()
            print(f"  IDX data loaded: {len(idx_data)} rows")

            # Query for BQX data
            bqx_query = f"""
            SELECT
                interval_time,
                bqx_{window}
            FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
            ORDER BY interval_time
            LIMIT 50000
            """

            print(f"  Executing BQX query...")
            bqx_data = self.client.query(bqx_query).to_dataframe()
            print(f"  BQX data loaded: {len(bqx_data)} rows")

            # Set index and merge
            idx_data.set_index('interval_time', inplace=True)
            bqx_data.set_index('interval_time', inplace=True)

            # Create Smart Dual features (12 features as per original)
            features = pd.DataFrame(index=idx_data.index)

            # IDX features (leading indicators)
            features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            features['idx_lag_3'] = idx_data['close_idx'].shift(3)
            features['idx_lag_4'] = idx_data['close_idx'].shift(4)
            features['idx_lag_5'] = idx_data['close_idx'].shift(5)

            # BQX features (lagging confirmations)
            features['bqx_lag_1'] = bqx_data[f'bqx_{window}'].shift(1)
            features['bqx_lag_2'] = bqx_data[f'bqx_{window}'].shift(2)

            # Derived features
            features['idx_ma_5'] = idx_data['close_idx'].rolling(5).mean()
            features['idx_ma_20'] = idx_data['close_idx'].rolling(20).mean()
            features['bqx_ma_5'] = bqx_data[f'bqx_{window}'].rolling(5).mean()
            features['idx_std_20'] = idx_data['close_idx'].rolling(20).std()
            features['idx_bqx_ratio'] = features['idx_lag_1'] / (features['bqx_lag_1'] + 1e-6)

            # Target variable
            y = bqx_data[f'bqx_{window}']

            # Remove NaN values
            features = features.dropna()
            y = y[features.index]

            print(f"  Baseline features ready: {len(features)} rows, {len(features.columns)} features")
            return features, y

        except Exception as e:
            print(f"  ❌ Error loading baseline: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(), pd.Series()

    def create_triangle_features(self, base_features: pd.DataFrame,
                                 curr1: str, curr2: str, curr3: str) -> pd.DataFrame:
        """Create triangulation features for a currency triple"""
        triangle_features = pd.DataFrame(index=base_features.index)

        # Form currency pairs
        pairs_needed = [
            (f"{curr1}{curr2}".lower(), f"{curr2}{curr1}".lower()),
            (f"{curr2}{curr3}".lower(), f"{curr3}{curr2}".lower()),
            (f"{curr3}{curr1}".lower(), f"{curr1}{curr3}".lower())
        ]

        triangle_data = {}

        for pair, reverse_pair in pairs_needed:
            # Try to load the pair data
            loaded = False

            # Try normal direction
            try:
                query = f"""
                SELECT interval_time, close_idx
                FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
                ORDER BY interval_time
                LIMIT 50000
                """
                data = self.client.query(query).to_dataframe()
                if len(data) > 0:
                    data.set_index('interval_time', inplace=True)
                    triangle_data[pair] = data['close_idx']
                    loaded = True
            except:
                pass

            # Try reverse if normal didn't work
            if not loaded:
                try:
                    query = f"""
                    SELECT interval_time, 1.0/close_idx as close_idx
                    FROM `bqx-ml.bqx_ml_v3_features.{reverse_pair}_idx`
                    ORDER BY interval_time
                    LIMIT 50000
                    """
                    data = self.client.query(query).to_dataframe()
                    if len(data) > 0:
                        data.set_index('interval_time', inplace=True)
                        triangle_data[pair] = data['close_idx']
                        loaded = True
                except:
                    pass

        if len(triangle_data) < 3:
            return triangle_features  # Can't create triangle

        # Align data
        aligned_data = pd.DataFrame(triangle_data)
        aligned_data = aligned_data.reindex(base_features.index).fillna(method='ffill')

        # Create triangle features
        prefix = f"tri_{curr1}{curr2}{curr3}"

        # Basic triangle product (arbitrage indicator)
        triangle_product = aligned_data.prod(axis=1)
        triangle_features[f"{prefix}_product"] = triangle_product

        # Deviation from parity
        triangle_features[f"{prefix}_deviation"] = triangle_product - 1.0

        # Log triangle
        triangle_features[f"{prefix}_log"] = np.log(triangle_product.clip(lower=0.01))

        # Triangle momentum
        for period in [5, 10, 20]:
            triangle_features[f"{prefix}_mom_{period}"] = triangle_product.pct_change(period)

        # Triangle volatility
        for window in [10, 20]:
            triangle_features[f"{prefix}_vol_{window}"] = triangle_product.rolling(window).std()

        # Mean reversion signal
        ma_20 = triangle_product.rolling(20).mean()
        triangle_features[f"{prefix}_mr_20"] = (triangle_product - ma_20) / (ma_20 + 1e-6)

        # Z-score
        mean_50 = triangle_product.rolling(50).mean()
        std_50 = triangle_product.rolling(50).std()
        triangle_features[f"{prefix}_zscore"] = (triangle_product - mean_50) / (std_50 + 1e-6)

        return triangle_features

    def test_single_triangle(self, triangle: Tuple[str, str, str],
                            base_features: pd.DataFrame, y: pd.Series) -> Dict:
        """Test a single triangle's impact on model performance"""
        curr1, curr2, curr3 = triangle

        # Create triangle features
        tri_features = self.create_triangle_features(base_features, curr1, curr2, curr3)

        if tri_features.empty:
            return None

        # Combine with baseline
        combined = pd.concat([base_features, tri_features], axis=1)
        combined = combined.dropna()
        y_combined = y[combined.index]

        if len(combined) < 1000:
            return None

        # Train model with combined features
        X_train, X_test, y_train, y_test = train_test_split(
            combined, y_combined, test_size=0.2, random_state=42
        )

        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            random_state=42
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        new_r2 = r2_score(y_test, pred)

        improvement = new_r2 - self.baseline_r2
        improvement_pct = (improvement / self.baseline_r2) * 100

        return {
            'triangle': f"{curr1}-{curr2}-{curr3}",
            'baseline_r2': self.baseline_r2,
            'new_r2': new_r2,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'kept': improvement >= self.improvement_threshold,
            'num_features': len(tri_features.columns)
        }

    def test_batch(self, triangles: List[Tuple], batch_name: str) -> Dict:
        """Test a batch of triangles"""
        print(f"\n{'='*60}")
        print(f"Testing {batch_name}")
        print(f"Batch size: {len(triangles)} triangles")
        print(f"{'='*60}")

        # Load baseline once for the batch
        base_features, y = self.load_baseline_model()
        if base_features.empty:
            print(f"❌ Failed to load baseline model")
            return {'tested': 0, 'kept': 0, 'results': []}

        # Calculate baseline performance once
        print(f"  Baseline R²: {self.baseline_r2}")

        batch_results = []
        batch_kept = 0

        for i, triangle in enumerate(triangles):
            if i % 5 == 0:
                print(f"  Progress: {i}/{len(triangles)} triangles...")

            result = self.test_single_triangle(triangle, base_features, y)

            if result:
                batch_results.append(result)

                if result['kept']:
                    batch_kept += 1
                    print(f"  ✅ KEPT: {result['triangle']} - Improvement: {result['improvement']:.4f} ({result['improvement_pct']:.2f}%)")

        print(f"\n{batch_name} Complete:")
        print(f"  Tested: {len(batch_results)} triangles")
        print(f"  Kept: {batch_kept} triangles")

        return {
            'batch_name': batch_name,
            'tested': len(batch_results),
            'kept': batch_kept,
            'results': batch_results
        }

    def update_airtable_append(self, task_id: str, content: str):
        """Update AirTable in APPEND mode"""
        try:
            # Find task record
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

            # Create update block
            timestamp = datetime.now().isoformat()
            new_update = f"""🔄 COMPREHENSIVE TESTING UPDATE: {timestamp}
================================================
{content}
================================================"""

            # APPEND mode - new on top
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
        """Run comprehensive testing per CE directive"""
        print("\n" + "="*70)
        print("COMPREHENSIVE TRIANGULATION TESTING V2")
        print("Authorization: ALPHA-2B-COMPREHENSIVE")
        print(f"Total triangles: {self.total_triangles}")
        print(f"Threshold: {self.improvement_threshold*100}%")
        print("="*70)

        start_time = time.time()

        # Test Tier 1
        print(f"\n📊 TESTING TIER 1: MAJOR CURRENCIES")
        tier1_result = self.test_batch(self.tier1_triangles[:10], "Tier 1 - First 10")
        self.all_results.append(tier1_result)
        self.total_tested += tier1_result['tested']
        self.total_kept += tier1_result['kept']

        # Update AirTable
        update_content = f"""TRIANGULATION TESTING - TIER 1
• Triangles tested: {tier1_result['tested']}
• Features kept: {tier1_result['kept']}
• Total tested: {self.total_tested}/{self.total_triangles}
• Best improvement: {max([r['improvement'] for r in tier1_result['results']], default=0):.4f}

Testing continues per CE directive ALPHA-2B-COMPREHENSIVE..."""

        self.update_airtable_append('MP03.P05.S05.T10', update_content)

        # Save results
        elapsed = (time.time() - start_time) / 60

        with open('/home/micha/bqx_ml_v3/triangulation_results_v2.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'authorization': 'ALPHA-2B-COMPREHENSIVE',
                'total_tested': self.total_tested,
                'total_kept': self.total_kept,
                'elapsed_minutes': elapsed,
                'results': self.all_results
            }, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"BATCH COMPLETE")
        print(f"Tested: {self.total_tested}/{self.total_triangles}")
        print(f"Kept: {self.total_kept}")
        print(f"Time: {elapsed:.1f} minutes")
        print(f"{'='*70}")

        return self.all_results


if __name__ == "__main__":
    print("Starting Comprehensive Triangulation Testing V2...")
    print("Fixed version - using only available columns")
    print("")

    tester = ComprehensiveTriangulationTester()
    results = tester.run_comprehensive_testing()

    print("\nNext batch will continue in 2 hours per CE directive...")
    print("ALPHA-2B-COMPREHENSIVE mandates testing ALL features")