#!/usr/bin/env python3
"""
Generate VAR tables for USD currency.
Creates var_agg_idx_usd, var_agg_bqx_usd, var_align_idx_usd, var_align_bqx_usd
"""

import subprocess
import sys

PROJECT = "bqx-ml"
DATASET = "bqx_ml_v3_features_v2"

USD_PAIRS = ['eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd']

WINDOWS_AGG = [45, 90, 180, 360, 720, 1440, 2880]
WINDOWS_ALIGN = [45, 90, 180, 360, 720, 1440]  # align tables don't have 2880

# AGG features
AGG_FEATURES = ['mean', 'std', 'min', 'max', 'range', 'cv', 'position', 'sum', 'count']

# ALIGN features (actual column names: dir_, pos_, zscore_)
ALIGN_FEATURES = ['dir', 'pos', 'zscore']


def generate_var_sql(feature_type: str, variant: str) -> str:
    """Generate SQL for variance aggregation."""

    prefix = f"{feature_type}_bqx" if variant == "bqx" else feature_type
    output_table = f"var_{feature_type}_{variant}_usd"

    # Build UNION ALL for all USD pairs
    union_parts = []
    for pair in USD_PAIRS:
        source_table = f"{prefix}_{pair}"
        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair, * EXCEPT(interval_time, pair)
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    # Get features and windows for this type
    features = AGG_FEATURES if feature_type == "agg" else ALIGN_FEATURES
    windows = WINDOWS_AGG if feature_type == "agg" else WINDOWS_ALIGN

    # Build variance aggregation columns
    var_cols = []
    for w in windows:
        for feat in features:
            # AGG columns: agg_mean_45, ALIGN columns: dir_45 (no prefix)
            if feature_type == "agg":
                col_name = f"{feature_type}_{feat}_{w}"
            else:
                col_name = f"{feat}_{w}"
            var_cols.append(f"""
        SAFE_DIVIDE(VAR_POP({col_name}), 1) AS var_{feat}_{w},
        AVG({col_name}) AS avg_{feat}_{w}""")

    var_sql = ",\n".join(var_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
CLUSTER BY currency_family
AS
WITH all_pairs AS (
    {union_sql}
)
SELECT
    interval_time,
    'USD' AS currency_family,
    COUNT(DISTINCT pair) AS pairs_in_family,
    {var_sql}
FROM all_pairs
GROUP BY interval_time
"""
    return sql, output_table


def execute_bq(sql: str, table_name: str) -> bool:
    """Execute BigQuery SQL."""
    print(f"Creating {table_name}...")
    result = subprocess.run(
        ['bq', 'query', '--use_legacy_sql=false', '--nouse_cache'],
        input=sql,
        capture_output=True,
        text=True,
        timeout=300
    )
    if result.returncode != 0:
        print(f"  ✗ FAILED: {result.stderr or result.stdout}")
        return False
    print(f"  ✓ {table_name}")
    return True


def main():
    results = {'success': 0, 'failed': 0}

    # Generate all 4 VAR tables for USD
    for feature_type in ['agg', 'align']:
        for variant in ['idx', 'bqx']:
            sql, table_name = generate_var_sql(feature_type, variant)
            if execute_bq(sql, table_name):
                results['success'] += 1
            else:
                results['failed'] += 1

    print(f"\nVAR USD Complete: {results['success']}/4 success, {results['failed']}/4 failed")
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
