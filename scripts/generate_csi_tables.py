#!/usr/bin/env python3
"""
CSI (Currency Strength Index) Table Generator
==============================================
Generates currency strength features by aggregating pair features for each currency.

For each currency, aggregates features from all pairs containing that currency
with directional adjustment:
- When currency is BASE (e.g., USD in USDJPY): direction = +1
- When currency is QUOTE (e.g., USD in EURUSD): direction = -1

Usage:
    python generate_csi_tables.py --currency USD --feature-type agg --variant idx
    python generate_csi_tables.py --currency USD --all-types --all-variants
"""

import argparse
import subprocess
import sys
import time
from typing import Dict, List, Tuple

# Currency to pair mappings with direction
# Direction: +1 when currency is BASE, -1 when currency is QUOTE
CURRENCY_PAIRS = {
    'USD': {
        'base': ['usdjpy', 'usdchf', 'usdcad'],  # direction = +1
        'quote': ['eurusd', 'gbpusd', 'audusd', 'nzdusd']  # direction = -1
    },
    'EUR': {
        'base': ['eurusd', 'eurjpy', 'eurgbp', 'eurchf', 'eurcad', 'euraud', 'eurnzd'],
        'quote': []
    },
    'GBP': {
        'base': ['gbpusd', 'gbpjpy', 'gbpchf', 'gbpcad', 'gbpaud', 'gbpnzd'],
        'quote': ['eurgbp']
    },
    'JPY': {
        'base': [],
        'quote': ['usdjpy', 'eurjpy', 'gbpjpy', 'chfjpy', 'cadjpy', 'audjpy', 'nzdjpy']
    },
    'CHF': {
        'base': ['chfjpy'],
        'quote': ['usdchf', 'eurchf', 'gbpchf', 'audchf', 'nzdchf', 'cadchf']
    },
    'CAD': {
        'base': ['cadjpy', 'cadchf'],
        'quote': ['usdcad', 'eurcad', 'gbpcad', 'audcad', 'nzdcad']
    },
    'AUD': {
        'base': ['audusd', 'audjpy', 'audchf', 'audcad', 'audnzd'],
        'quote': ['euraud', 'gbpaud']
    },
    'NZD': {
        'base': ['nzdusd', 'nzdjpy', 'nzdchf', 'nzdcad'],
        'quote': ['eurnzd', 'gbpnzd', 'audnzd']
    }
}

# Feature types with their column patterns
FEATURE_TYPES = {
    'agg': {
        'columns': ['mean', 'std', 'min', 'max', 'range', 'cv', 'position'],
        'windows': [45, 90, 180, 360, 720, 1440, 2880],
        'directional_cols': ['mean', 'position'],  # Columns that need directional adjustment
        'absolute_cols': ['std', 'min', 'max', 'range', 'cv']  # Columns that are always positive
    },
    'mom': {
        'columns': ['roc', 'diff', 'dir', 'roc_smooth', 'zscore', 'pos_count', 'strength'],
        'windows': [45, 90, 180, 360, 720, 1440],
        'directional_cols': ['roc', 'diff', 'dir', 'roc_smooth', 'zscore'],
        'absolute_cols': ['pos_count', 'strength']
    },
    'vol': {
        'columns': ['realized', 'atr', 'normalized', 'range_pct', 'of_vol', 'zscore'],
        'windows': [45, 90, 180, 360, 720],
        'directional_cols': [],  # Volatility is non-directional
        'absolute_cols': ['realized', 'atr', 'normalized', 'range_pct', 'of_vol', 'zscore']
    },
    'reg': {
        'columns': ['slope', 'intercept', 'r2', 'quad', 'lin_term', 'quad_term', 'resid', 'forecast'],
        'windows': [45, 90, 180, 360, 720, 1440, 2880],
        'directional_cols': ['slope', 'quad', 'lin_term', 'quad_term', 'forecast'],
        'absolute_cols': ['intercept', 'r2', 'resid']
    },
    'lag': {
        'columns': ['1', '2', '3', '5', '10', '15'],  # lag periods
        'windows': [45, 90],  # base windows
        'directional_cols': ['1', '2', '3', '5', '10', '15'],
        'absolute_cols': []
    },
    'align': {
        'columns': ['ratio', 'diff', 'zscore', 'coherence', 'divergence', 'consistency'],
        'windows': [45, 90, 180, 360, 720],
        'directional_cols': ['ratio', 'diff', 'zscore'],
        'absolute_cols': ['coherence', 'divergence', 'consistency']
    },
    'der': {
        'columns': ['v1', 'v2', 'accel'],
        'windows': [45, 90, 180, 360, 720],
        'directional_cols': ['v1', 'v2', 'accel'],
        'absolute_cols': []
    },
    'rev': {
        'columns': ['signal', 'strength', 'exhaustion'],
        'windows': [45, 90, 180, 360, 720],
        'directional_cols': ['signal'],
        'absolute_cols': ['strength', 'exhaustion']
    },
    'div': {
        'columns': ['short_long', 'price_mom', 'cross'],
        'windows': [45, 90, 180],
        'directional_cols': ['short_long', 'price_mom', 'cross'],
        'absolute_cols': []
    },
    'mrt': {
        'columns': ['zscore', 'tension', 'reversion'],
        'windows': [45, 90, 180, 360, 720],
        'directional_cols': ['zscore', 'tension', 'reversion'],
        'absolute_cols': []
    },
    'cyc': {
        'columns': ['position'],
        'windows': [45, 90, 180, 360],
        'directional_cols': ['position'],
        'absolute_cols': []
    },
    'ext': {
        'columns': ['zscore', 'percentile', 'distance_zero', 'sigma_band'],
        'windows': [45, 90, 180, 360, 720, 1440, 2880],
        'directional_cols': ['zscore'],
        'absolute_cols': ['percentile', 'distance_zero', 'sigma_band']
    }
}

def get_source_table_name(feature_type: str, pair: str, is_bqx: bool) -> str:
    """Get the source table name for a feature type and pair."""
    if is_bqx:
        return f"{feature_type}_bqx_{pair}"
    else:
        return f"{feature_type}_{pair}"

def get_csi_table_name(feature_type: str, currency: str, is_bqx: bool) -> str:
    """Get the CSI output table name."""
    if is_bqx:
        return f"csi_{feature_type}_bqx_{currency.lower()}"
    else:
        return f"csi_{feature_type}_{currency.lower()}"

# Global cache for table names
_table_cache = None

def _load_table_cache(dataset: str) -> set:
    """Load all table names from dataset into cache."""
    global _table_cache
    if _table_cache is not None:
        return _table_cache

    print("Loading table cache from BigQuery...")
    result = subprocess.run(
        ['bq', 'query', '--use_legacy_sql=false', '--format=csv', '--max_rows=10000',
         f"SELECT table_name FROM `{dataset}.INFORMATION_SCHEMA.TABLES`"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Warning: Could not load table cache: {result.stderr}")
        return set()

    lines = result.stdout.strip().split('\n')
    _table_cache = set(lines[1:]) if len(lines) > 1 else set()  # Skip header
    print(f"Loaded {len(_table_cache)} tables into cache")
    return _table_cache

def check_table_exists(dataset: str, table: str) -> bool:
    """Check if a BigQuery table exists using cached lookup."""
    cache = _load_table_cache(dataset)
    return table in cache

def get_table_columns(dataset: str, table: str) -> List[str]:
    """Get column names from a BigQuery table."""
    result = subprocess.run(
        ['bq', 'query', '--use_legacy_sql=false', '--format=csv',
         f"SELECT column_name FROM `{dataset}.INFORMATION_SCHEMA.COLUMNS` "
         f"WHERE table_name = '{table}' ORDER BY ordinal_position"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    lines = result.stdout.strip().split('\n')
    return lines[1:] if len(lines) > 1 else []  # Skip header

def generate_csi_sql(feature_type: str, currency: str, is_bqx: bool) -> str:
    """Generate SQL to create a CSI table for a currency and feature type."""

    dataset = "bqx-ml.bqx_ml_v3_features_v2"
    pairs_config = CURRENCY_PAIRS.get(currency.upper(), {})
    base_pairs = pairs_config.get('base', [])
    quote_pairs = pairs_config.get('quote', [])

    if not base_pairs and not quote_pairs:
        raise ValueError(f"No pairs found for currency {currency}")

    # Get columns from first available source table
    all_pairs = base_pairs + quote_pairs
    sample_table = get_source_table_name(feature_type, all_pairs[0], is_bqx)
    columns = get_table_columns(dataset, sample_table)

    # Filter to feature columns only (exclude metadata)
    feature_columns = [c for c in columns if c not in ['interval_time', 'pair', 'source_value']]

    if not feature_columns:
        raise ValueError(f"No feature columns found in {sample_table}")

    # Build UNION ALL for all pairs
    union_parts = []

    for pair in base_pairs:
        table_name = get_source_table_name(feature_type, pair, is_bqx)
        if check_table_exists(dataset, table_name):
            union_parts.append(f"""
    SELECT
        interval_time,
        '{pair}' as pair,
        1 as direction,
        {', '.join(feature_columns)}
    FROM `{dataset}.{table_name}`""")

    for pair in quote_pairs:
        table_name = get_source_table_name(feature_type, pair, is_bqx)
        if check_table_exists(dataset, table_name):
            union_parts.append(f"""
    SELECT
        interval_time,
        '{pair}' as pair,
        -1 as direction,
        {', '.join(feature_columns)}
    FROM `{dataset}.{table_name}`""")

    if not union_parts:
        raise ValueError(f"No source tables found for {feature_type} {currency}")

    union_sql = " UNION ALL ".join(union_parts)

    # Build aggregation columns
    # For directional columns: AVG(direction * column)
    # For absolute columns: AVG(column)
    ft_config = FEATURE_TYPES.get(feature_type, {})
    directional_cols = ft_config.get('directional_cols', [])

    agg_columns = []
    for col in feature_columns:
        # Check if this column is directional
        is_directional = any(d in col for d in directional_cols)

        if is_directional:
            agg_columns.append(f"AVG(direction * {col}) as csi_{col}")
        else:
            agg_columns.append(f"AVG({col}) as csi_{col}")

    output_table = get_csi_table_name(feature_type, currency, is_bqx)

    agg_cols_str = ',\n    '.join(agg_columns)

    sql = f"""
CREATE OR REPLACE TABLE `{dataset}.{output_table}`
PARTITION BY DATE(interval_time)
CLUSTER BY currency
AS
WITH source_data AS (
    {union_sql}
)
SELECT
    interval_time,
    '{currency.upper()}' as currency,
    {agg_cols_str}
FROM source_data
GROUP BY interval_time
"""

    return sql

def create_csi_table(feature_type: str, currency: str, is_bqx: bool, dry_run: bool = False) -> Tuple[bool, str]:
    """Create a single CSI table."""

    output_table = get_csi_table_name(feature_type, currency, is_bqx)
    variant = "BQX" if is_bqx else "IDX"

    print(f"Creating {output_table} ({variant})...")

    try:
        sql = generate_csi_sql(feature_type, currency, is_bqx)

        if dry_run:
            print(f"DRY RUN - SQL for {output_table}:")
            print(sql[:500] + "..." if len(sql) > 500 else sql)
            return True, "DRY RUN"

        # Execute SQL
        result = subprocess.run(
            ['bq', 'query', '--use_legacy_sql=false', '--nouse_cache'],
            input=sql,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, error_msg

        return True, "SUCCESS"

    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='Generate CSI tables')
    parser.add_argument('--currency', type=str, help='Currency code (USD, EUR, etc.)')
    parser.add_argument('--feature-type', type=str, help='Feature type (agg, mom, vol, etc.)')
    parser.add_argument('--variant', type=str, choices=['idx', 'bqx', 'both'], default='both',
                        help='Variant to generate')
    parser.add_argument('--all-currencies', action='store_true', help='Generate for all currencies')
    parser.add_argument('--all-types', action='store_true', help='Generate for all feature types')
    parser.add_argument('--dry-run', action='store_true', help='Print SQL without executing')
    parser.add_argument('--max-retries', type=int, default=3, help='Max retries per table')

    args = parser.parse_args()

    # Determine currencies to process
    currencies = list(CURRENCY_PAIRS.keys()) if args.all_currencies else [args.currency]
    if not currencies or currencies == [None]:
        print("Error: Specify --currency or --all-currencies")
        sys.exit(1)

    # Determine feature types to process
    feature_types = list(FEATURE_TYPES.keys()) if args.all_types else [args.feature_type]
    if not feature_types or feature_types == [None]:
        print("Error: Specify --feature-type or --all-types")
        sys.exit(1)

    # Determine variants
    variants = []
    if args.variant in ['idx', 'both']:
        variants.append(False)  # IDX
    if args.variant in ['bqx', 'both']:
        variants.append(True)   # BQX

    # Process all combinations
    results = {'success': 0, 'failed': 0, 'errors': []}
    total = len(currencies) * len(feature_types) * len(variants)

    print(f"\nGenerating {total} CSI tables...")
    print(f"Currencies: {currencies}")
    print(f"Feature types: {feature_types}")
    print(f"Variants: {'IDX + BQX' if len(variants) == 2 else ('BQX' if variants[0] else 'IDX')}")
    print("-" * 60)

    for currency in currencies:
        for ft in feature_types:
            for is_bqx in variants:
                for attempt in range(args.max_retries):
                    success, message = create_csi_table(ft, currency, is_bqx, args.dry_run)

                    if success:
                        results['success'] += 1
                        print(f"  ✓ {get_csi_table_name(ft, currency, is_bqx)}")
                        break
                    else:
                        if attempt < args.max_retries - 1:
                            print(f"  ⚠ Retry {attempt + 1}/{args.max_retries} for {get_csi_table_name(ft, currency, is_bqx)}")
                            time.sleep(30)
                        else:
                            results['failed'] += 1
                            results['errors'].append({
                                'table': get_csi_table_name(ft, currency, is_bqx),
                                'error': message
                            })
                            print(f"  ✗ FAILED: {get_csi_table_name(ft, currency, is_bqx)}: {message[:100]}")

    # Summary
    print("\n" + "=" * 60)
    print(f"CSI Table Generation Complete")
    print(f"  Success: {results['success']}/{total}")
    print(f"  Failed:  {results['failed']}/{total}")

    if results['errors']:
        print("\nFailed tables:")
        for err in results['errors']:
            print(f"  - {err['table']}: {err['error'][:100]}")

    return 0 if results['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
