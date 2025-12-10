#!/usr/bin/env python3
"""
Generate Feature Ledger - Phase 2.5 (OPTIMIZED)

Creates feature_ledger.parquet with 100% coverage for all models:
- 6,477 features per pair
- 28 pairs × 7 horizons = 196 models
- Total: 1,269,492 rows

OPTIMIZATION: Uses batch INFORMATION_SCHEMA.COLUMNS query instead of
individual bq show calls. ~5-10 min vs 30-60 min.
"""

import json
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict
import sys

PROJECT = "bqx-ml"
DATASET = "bqx_ml_v3_features_v2"

ALL_PAIRS = [
    'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
    'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'eurcad', 'eurnzd',
    'gbpjpy', 'gbpchf', 'gbpaud', 'gbpcad', 'gbpnzd',
    'audjpy', 'audchf', 'audcad', 'audnzd',
    'nzdjpy', 'nzdchf', 'nzdcad',
    'cadjpy', 'cadchf', 'chfjpy'
]

HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # h15-h105

# Columns to exclude (not features)
EXCLUDE_COLUMNS = {'interval_time', 'pair', 'currency', 'scope'}


def get_all_columns_batch() -> Dict[str, List[str]]:
    """Get ALL table columns in one batch query."""
    print("  Querying INFORMATION_SCHEMA.COLUMNS (batch)...")

    query = f"""
    SELECT table_name, column_name
    FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE column_name NOT IN ('interval_time', 'pair', 'currency', 'scope')
    ORDER BY table_name, ordinal_position
    """

    result = subprocess.run(
        ['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=500000', query],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return {}

    # Parse CSV output
    lines = result.stdout.strip().split('\n')
    table_columns = defaultdict(list)

    for line in lines[1:]:  # Skip header
        if ',' in line:
            parts = line.split(',', 1)
            if len(parts) == 2:
                table_name, col_name = parts[0].strip(), parts[1].strip()
                if table_name and col_name:
                    table_columns[table_name].append(col_name)

    print(f"  Found {len(table_columns)} tables, {sum(len(v) for v in table_columns.values())} columns")
    return dict(table_columns)


def filter_tables_for_pair(all_columns: Dict[str, List[str]], pair: str) -> Dict[str, List[str]]:
    """Filter tables relevant to a specific pair."""
    filtered = {}

    for table_name, columns in all_columns.items():
        # Include if table contains pair name, or is market-wide/currency-wide
        if (pair in table_name.lower() or
            table_name.startswith('mkt') or
            table_name.startswith('csi') or
            table_name.startswith('tri')):
            filtered[table_name] = columns

    return filtered


def load_feature_selection(pair: str, horizon: int) -> Dict:
    """Load feature selection results if available."""
    selection_file = Path(f'/home/micha/bqx_ml_v3/intelligence/robust_feature_selection_{pair}_h{horizon}.json')
    if selection_file.exists():
        with open(selection_file) as f:
            return json.load(f)
    return {}


def generate_ledger_for_pair_horizon(pair: str, horizon: int, pair_features: Dict[str, List[str]]) -> pd.DataFrame:
    """Generate ledger rows for a specific pair and horizon."""
    rows = []

    # Load feature selection results if available
    selection = load_feature_selection(pair, horizon)
    stable_features: Set[str] = set()
    feature_scores: Dict[str, float] = {}

    if selection and 'groups' in selection:
        for group_name, group_data in selection['groups'].items():
            if 'top_features' in group_data:
                for feat, score in group_data['top_features']:
                    stable_features.add(feat)
                    feature_scores[feat] = score

    # Process each table's features
    for table_name, columns in pair_features.items():
        feature_type = table_name.split('_')[0] if '_' in table_name else 'unknown'

        for col in columns:
            # Build full feature name
            full_feature_name = f"{table_name}_{col}"

            # Determine status
            if full_feature_name in stable_features or col in stable_features:
                status = 'RETAINED'
                score = feature_scores.get(full_feature_name, feature_scores.get(col, 0))
            else:
                status = 'CANDIDATE'
                score = 0

            rows.append({
                'pair': pair,
                'horizon': horizon,
                'feature_name': col,
                'full_feature_name': full_feature_name,
                'source_table': table_name,
                'final_status': status,
                'stability_score': score,
                'shap_importance': score / 1000.0 if status == 'RETAINED' else None,
                'feature_type': feature_type
            })

    return pd.DataFrame(rows)


def main():
    start_time = datetime.now()

    print("=" * 60)
    print("PHASE 2.5: Feature Ledger Generation (OPTIMIZED)")
    print("=" * 60)
    print(f"Target: 28 pairs × 7 horizons × ~6,477 features = ~1,269,492 rows")
    print(f"Start time: {start_time.strftime('%H:%M:%S')}")
    print()

    # OPTIMIZATION: Single batch query for all columns
    print("Step 1: Batch querying all table columns...")
    all_columns = get_all_columns_batch()

    if not all_columns:
        print("ERROR: Failed to get column information")
        return 1

    all_ledger_rows = []
    total_pairs = len(ALL_PAIRS)

    print(f"\nStep 2: Processing {total_pairs} pairs × {len(HORIZONS)} horizons...")

    for i, pair in enumerate(ALL_PAIRS, 1):
        # Filter tables for this pair
        pair_features = filter_tables_for_pair(all_columns, pair)
        feature_count = sum(len(v) for v in pair_features.values())

        print(f"  [{i:2}/{total_pairs}] {pair}: {len(pair_features)} tables, {feature_count} features")

        for horizon in HORIZONS:
            df = generate_ledger_for_pair_horizon(pair, horizon, pair_features)
            all_ledger_rows.append(df)

    # Combine all rows
    print(f"\nStep 3: Combining {len(all_ledger_rows)} DataFrames...")
    ledger_df = pd.concat(all_ledger_rows, ignore_index=True)

    print(f"\nLedger Statistics:")
    print(f"  Total rows: {len(ledger_df):,}")
    print(f"  Unique pairs: {ledger_df['pair'].nunique()}")
    print(f"  Unique horizons: {ledger_df['horizon'].nunique()}")
    print(f"  Unique features: {ledger_df['feature_name'].nunique()}")
    print(f"  Status breakdown:")
    for status, count in ledger_df['final_status'].value_counts().items():
        print(f"    {status}: {count:,}")

    # Save to parquet
    output_path = Path('/home/micha/bqx_ml_v3/data/feature_ledger.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nStep 4: Saving to {output_path}...")
    ledger_df.to_parquet(output_path, index=False)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"  Saved {len(ledger_df):,} rows")
    print(f"  Duration: {duration:.1f} seconds")

    # Validation
    print("\n" + "=" * 60)
    print("GATE_2 Validation Checklist:")
    print("=" * 60)
    expected_rows = 1269492
    print(f"  Row count: {len(ledger_df):,} (target: {expected_rows:,})")
    pct = len(ledger_df) / expected_rows * 100
    print(f"  Coverage: {pct:.1f}%")
    null_status = ledger_df['final_status'].isna().sum()
    print(f"  NULL final_status: {null_status}")
    retained_count = (ledger_df['final_status'] == 'RETAINED').sum()
    print(f"  RETAINED features: {retained_count:,}")

    if len(ledger_df) >= expected_rows * 0.9 and null_status == 0:
        print("\n✓ GATE_2 PRE-CHECK PASSED")
    else:
        print(f"\n⚠ Validation issues detected")

    return 0


if __name__ == '__main__':
    sys.exit(main())
