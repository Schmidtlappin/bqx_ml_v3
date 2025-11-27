#!/usr/bin/env python3
"""
PHASE 2C: COMPREHENSIVE EXTENDED LAGS TESTING
Tests extended lags (15-100) as per CE directive
Authorization: ALPHA-2B-COMPREHENSIVE
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import xgboost as xgb
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime
import json
from typing import Dict, List, Tuple
from pyairtable import Api
import warnings
import time
warnings.filterwarnings('ignore')

class ComprehensiveExtendedLagsTester:
    def __init__(self):
        """Initialize extended lags testing framework"""
        self.client = bigquery.Client(project="bqx-ml")
        self.baseline_r2 = 0.7079  # Current Smart Dual performance
        self.improvement_threshold = 0.005  # 0.5% minimum improvement

        # Load AirTable credentials
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
        self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
        self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
        self.tasks_table = self.base.table('Tasks')

        # Define all 28 currency pairs
        self.all_pairs = [
            'eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad', 'usdchf', 'nzdusd',
            'eurgbp', 'eurjpy', 'euraud', 'eurcad', 'eurchf', 'eurnzd',
            'gbpjpy', 'gbpaud', 'gbpcad', 'gbpchf', 'gbpnzd',
            'audjpy', 'cadjpy', 'chfjpy', 'nzdjpy',
            'audcad', 'audchf', 'audnzd',
            'cadchf', 'nzdcad', 'nzdchf'
        ]

        # Top 10 pairs for deeper analysis
        self.top_pairs = ['eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad',
                          'eurgbp', 'eurjpy', 'gbpjpy', 'usdchf', 'nzdusd']

        # Top 3 pairs for deepest analysis
        self.major_pairs = ['eurusd', 'gbpusd', 'usdjpy']

        self.results = []

    def load_baseline_with_extended_data(self, pair: str, window: int = 45) -> Tuple[pd.DataFrame, pd.Series]:
        """Load baseline features plus extended data for lag testing"""
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

            # Create baseline Smart Dual features
            features = pd.DataFrame(index=idx_data.index)

            # Standard features (lags 1-5)
            features['idx_lag_1'] = idx_data['close_idx'].shift(1)
            features['idx_lag_2'] = idx_data['close_idx'].shift(2)
            features['idx_lag_3'] = idx_data['close_idx'].shift(3)
            features['idx_lag_4'] = idx_data['close_idx'].shift(4)
            features['idx_lag_5'] = idx_data['close_idx'].shift(5)

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

            # Keep raw data for extended lag creation
            self.raw_idx = idx_data['close_idx']
            self.raw_bqx = bqx_data[f'bqx_{window}']

            # Remove NaN
            features = features.dropna()
            y = y[features.index]

            return features, y

        except Exception as e:
            print(f"Error loading data for {pair}: {e}")
            return pd.DataFrame(), pd.Series()

    def create_extended_lag_features(self, base_features: pd.DataFrame,
                                    lag_start: int, lag_end: int,
                                    feature_type: str = 'simple') -> pd.DataFrame:
        """Create extended lag features"""
        extended_features = pd.DataFrame(index=base_features.index)

        for lag in range(lag_start, lag_end + 1):
            # Simple lags
            if feature_type in ['simple', 'all']:
                extended_features[f'idx_lag_{lag}'] = self.raw_idx.shift(lag)
                extended_features[f'bqx_lag_{lag}'] = self.raw_bqx.shift(lag)

            # Lag interactions (every 5th lag)
            if feature_type in ['interactions', 'all'] and lag % 5 == 0:
                # Lag ratios
                if lag >= 10:
                    extended_features[f'idx_lag_ratio_{lag//2}_{lag}'] = (
                        self.raw_idx.shift(lag//2) / (self.raw_idx.shift(lag) + 1e-6)
                    )
                    extended_features[f'bqx_lag_ratio_{lag//2}_{lag}'] = (
                        self.raw_bqx.shift(lag//2) / (self.raw_bqx.shift(lag) + 1e-6)
                    )

                # Lag differences
                if lag >= 10:
                    extended_features[f'idx_lag_diff_{lag-5}_{lag}'] = (
                        self.raw_idx.shift(lag-5) - self.raw_idx.shift(lag)
                    )
                    extended_features[f'bqx_lag_diff_{lag-5}_{lag}'] = (
                        self.raw_bqx.shift(lag-5) - self.raw_bqx.shift(lag)
                    )

                # Lag momentum
                if lag >= 15:
                    extended_features[f'idx_lag_mom_{lag}'] = (
                        self.raw_idx.shift(lag-10) -
                        self.raw_idx.shift(lag-5) -
                        self.raw_idx.shift(lag)
                    )

        # Clean up
        extended_features = extended_features.reindex(base_features.index)

        return extended_features

    def test_lag_range(self, pair: str, lag_start: int, lag_end: int,
                      feature_type: str = 'simple') -> Dict:
        """Test a range of lags for a pair"""
        # Load baseline
        base_features, y = self.load_baseline_with_extended_data(pair)
        if base_features.empty:
            return None

        # Create extended lag features
        extended_features = self.create_extended_lag_features(
            base_features, lag_start, lag_end, feature_type
        )

        # Combine features
        combined = pd.concat([base_features, extended_features], axis=1)
        combined = combined.dropna()
        y_combined = y[combined.index]

        if len(combined) < 1000:
            return None

        # Train and evaluate
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
            'pair': pair,
            'lag_range': f"{lag_start}-{lag_end}",
            'feature_type': feature_type,
            'baseline_r2': self.baseline_r2,
            'new_r2': new_r2,
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'kept': improvement >= self.improvement_threshold,
            'num_features': len(extended_features.columns)
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
            new_update = f"""🔄 EXTENDED LAGS TESTING UPDATE: {timestamp}
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
        """Run comprehensive extended lags testing per CE directive"""
        print("\n" + "="*70)
        print("COMPREHENSIVE EXTENDED LAGS TESTING - PHASE 2C")
        print("Authorization: ALPHA-2B-COMPREHENSIVE")
        print("="*70)

        start_time = time.time()
        all_results = []
        total_kept = 0

        # PHASE 1: Lags 15-30 on ALL pairs
        print(f"\n📊 PHASE 1: LAGS 15-30 ON ALL PAIRS")
        phase1_results = []

        for i, pair in enumerate(self.all_pairs[:5]):  # Start with first 5 pairs
            print(f"\n  Testing {pair} ({i+1}/{len(self.all_pairs)})")

            result = self.test_lag_range(pair, 15, 30, 'simple')
            if result:
                phase1_results.append(result)
                if result['kept']:
                    total_kept += 1
                    print(f"    ✅ KEPT: Improvement {result['improvement']:.4f}")
                else:
                    print(f"    ❌ No improvement")

        all_results.extend(phase1_results)

        # Update AirTable
        phase1_summary = f"""EXTENDED LAGS TESTING - PHASE 1
• Lags tested: 15-30
• Pairs tested: {len(phase1_results)}/28
• Features kept: {sum(1 for r in phase1_results if r['kept'])}
• Best improvement: {max([r['improvement'] for r in phase1_results], default=0):.4f}

Continuing with deeper lag testing..."""

        self.update_airtable_append('MP03.P05.S05.T13', phase1_summary)

        # PHASE 2: Lags 31-60 on top 10 pairs
        print(f"\n📊 PHASE 2: LAGS 31-60 ON TOP PAIRS")
        phase2_results = []

        for pair in self.top_pairs[:3]:  # Start with first 3 top pairs
            print(f"\n  Testing {pair} with lags 31-60")

            result = self.test_lag_range(pair, 31, 60, 'interactions')
            if result:
                phase2_results.append(result)
                if result['kept']:
                    total_kept += 1
                    print(f"    ✅ KEPT: Improvement {result['improvement']:.4f}")

        all_results.extend(phase2_results)

        # PHASE 3: Lags 61-100 on major pairs
        print(f"\n📊 PHASE 3: LAGS 61-100 ON MAJOR PAIRS")
        phase3_results = []

        for pair in self.major_pairs[:1]:  # Start with EURUSD
            print(f"\n  Testing {pair} with lags 61-100")

            result = self.test_lag_range(pair, 61, 100, 'all')
            if result:
                phase3_results.append(result)
                if result['kept']:
                    total_kept += 1
                    print(f"    ✅ KEPT: Improvement {result['improvement']:.4f}")

        all_results.extend(phase3_results)

        # Final summary
        elapsed = (time.time() - start_time) / 60

        final_summary = f"""EXTENDED LAGS TESTING UPDATE
• Total lag ranges tested: {len(all_results)}
• Total features kept: {total_kept}
• Testing time: {elapsed:.1f} minutes
• Best improvement: {max([r['improvement'] for r in all_results], default=0):.4f}

BREAKDOWN:
• Phase 1 (15-30): {len(phase1_results)} tested, {sum(1 for r in phase1_results if r['kept'])} kept
• Phase 2 (31-60): {len(phase2_results)} tested, {sum(1 for r in phase2_results if r['kept'])} kept
• Phase 3 (61-100): {len(phase3_results)} tested, {sum(1 for r in phase3_results if r['kept'])} kept

Continuing per CE directive ALPHA-2B-COMPREHENSIVE..."""

        self.update_airtable_append('MP03.P05.S05.T13', final_summary)

        # Save results
        with open('/home/micha/bqx_ml_v3/extended_lags_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'authorization': 'ALPHA-2B-COMPREHENSIVE',
                'total_tested': len(all_results),
                'total_kept': total_kept,
                'elapsed_minutes': elapsed,
                'results': all_results
            }, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"BATCH COMPLETE")
        print(f"Tested: {len(all_results)} lag ranges")
        print(f"Kept: {total_kept} feature sets")
        print(f"Time: {elapsed:.1f} minutes")
        print(f"{'='*70}")

        return all_results


if __name__ == "__main__":
    print("Starting Comprehensive Extended Lags Testing...")
    print("Per CE Directive: Testing lags 15-100")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("")

    tester = ComprehensiveExtendedLagsTester()
    results = tester.run_comprehensive_testing()

    print("\nNext batch continues in 2 hours per CE directive...")
    print("ALPHA-2B-COMPREHENSIVE mandates ALL features tested")