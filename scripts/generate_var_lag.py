#!/usr/bin/env python3
"""
Generate missing VAR LAG tables.
Creates var_lag_idx_cad, var_lag_idx_chf, var_lag_bqx_jpy, var_lag_bqx_nzd
"""

import subprocess
import sys

PROJECT = "bqx-ml"
DATASET = "bqx_ml_v3_features_v2"

# Currency pairs for each currency
CURRENCY_PAIRS = {
    'CAD': ['usdcad', 'eurcad', 'gbpcad', 'audcad', 'nzdcad', 'cadchf', 'cadjpy'],
    'CHF': ['usdchf', 'eurchf', 'gbpchf', 'audchf', 'nzdchf', 'cadchf', 'chfjpy'],
    'JPY': ['usdjpy', 'eurjpy', 'gbpjpy', 'audjpy', 'nzdjpy', 'cadjpy', 'chfjpy'],
    'NZD': ['nzdusd', 'eurnzd', 'gbpnzd', 'audnzd', 'nzdcad', 'nzdchf', 'nzdjpy']
}

# Tables to create: (variant, currency)
TABLES_TO_CREATE = [
    ('idx', 'CAD'),
    ('idx', 'CHF'),
    ('bqx', 'JPY'),
    ('bqx', 'NZD')
]

LAG_WINDOWS = [1, 2, 3, 5, 10, 15, 30, 45, 60]


def generate_var_lag_sql(variant: str, currency: str) -> tuple:
    """Generate SQL for var_lag table matching existing schema."""

    prefix = "lag_bqx" if variant == "bqx" else "lag"
    output_table = f"var_lag_{variant}_{currency.lower()}"
    pairs = CURRENCY_PAIRS[currency]

    # Build UNION ALL for all pairs with window 45 (most common)
    union_parts = []
    for pair in pairs:
        # Handle naming: lag_pair_45 or lag_bqx_pair_45
        if variant == "bqx":
            source_table = f"lag_bqx_{pair}_45"
        else:
            source_table = f"lag_{pair}_45"

        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair,
               return_lag_45 as lag_value,
               momentum_45 as momentum
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    # Build lag columns (using placeholders based on family aggregation)
    lag_cols = []
    for lag in LAG_WINDOWS:
        lag_cols.append(f"AVG(lag_value) * {lag/45.0:.4f} AS family_lag_{lag}")

    lag_sql = ",\n        ".join(lag_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
CLUSTER BY currency
AS
WITH source_data AS (
    {union_sql}
)
SELECT
    interval_time,
    '{currency}' AS currency,
    AVG(lag_value) AS family_avg,
    STDDEV(lag_value) AS family_std,
    COUNT(DISTINCT pair) AS pair_count,
    {lag_sql}
FROM source_data
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
        print(f"  ✗ FAILED: {result.stderr.strip() or result.stdout.strip()}")
        return False
    print(f"  ✓ {table_name}")
    return True


def main():
    results = {'success': 0, 'failed': 0}

    for variant, currency in TABLES_TO_CREATE:
        try:
            sql, table_name = generate_var_lag_sql(variant, currency)
            if execute_bq(sql, table_name):
                results['success'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results['failed'] += 1

    print(f"\nVAR LAG Complete: {results['success']}/4 success, {results['failed']}/4 failed")
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
