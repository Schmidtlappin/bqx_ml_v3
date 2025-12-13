#!/usr/bin/env python3
"""
Generate MKT (market-wide) tables.
Creates mkt_vol, mkt_dispersion, mkt_regime, mkt_sentiment (IDX and BQX variants)
"""

import subprocess
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

WINDOWS = [45, 90, 180, 360, 720]


def generate_mkt_vol_sql(variant: str) -> tuple:
    """Generate SQL for mkt_vol - market-wide volatility."""
    prefix = "vol_bqx" if variant == "bqx" else "vol"
    output_table = f"mkt_vol{'_bqx' if variant == 'bqx' else ''}"

    # Build UNION ALL for all pairs
    union_parts = []
    for pair in ALL_PAIRS:
        source_table = f"{prefix}_{pair}"
        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair, * EXCEPT(interval_time, pair)
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    # Aggregate volatility across all pairs
    agg_cols = []
    for w in WINDOWS:
        agg_cols.append(f"""
        AVG(vol_realized_{w}) AS mkt_vol_realized_{w},
        AVG(vol_atr_{w}) AS mkt_vol_atr_{w},
        AVG(vol_normalized_{w}) AS mkt_vol_normalized_{w},
        STDDEV(vol_realized_{w}) AS mkt_vol_dispersion_{w}""")

    agg_sql = ",\n".join(agg_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
AS
WITH all_pairs AS (
    {union_sql}
)
SELECT
    interval_time,
    'MARKET' AS scope,
    COUNT(DISTINCT pair) AS pairs_count,
    {agg_sql}
FROM all_pairs
GROUP BY interval_time
"""
    return sql, output_table


def generate_mkt_dispersion_sql(variant: str) -> tuple:
    """Generate SQL for mkt_dispersion - spread between strongest/weakest."""
    prefix = "agg_bqx" if variant == "bqx" else "agg"
    output_table = f"mkt_dispersion{'_bqx' if variant == 'bqx' else ''}"

    # Build UNION ALL for all pairs
    union_parts = []
    for pair in ALL_PAIRS:
        source_table = f"{prefix}_{pair}"
        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair, * EXCEPT(interval_time, pair)
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    # Calculate dispersion (max - min) across pairs
    disp_cols = []
    for w in WINDOWS:
        disp_cols.append(f"""
        MAX(agg_mean_{w}) - MIN(agg_mean_{w}) AS mkt_dispersion_mean_{w},
        MAX(agg_position_{w}) - MIN(agg_position_{w}) AS mkt_dispersion_position_{w},
        STDDEV(agg_mean_{w}) AS mkt_spread_std_{w}""")

    disp_sql = ",\n".join(disp_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
AS
WITH all_pairs AS (
    {union_sql}
)
SELECT
    interval_time,
    'MARKET' AS scope,
    COUNT(DISTINCT pair) AS pairs_count,
    {disp_sql}
FROM all_pairs
GROUP BY interval_time
"""
    return sql, output_table


def generate_mkt_regime_sql(variant: str) -> tuple:
    """Generate SQL for mkt_regime - aggregate regime states from reg_* tables."""
    prefix = "reg_bqx" if variant == "bqx" else "reg"
    output_table = f"mkt_regime{'_bqx' if variant == 'bqx' else ''}"

    # Build UNION ALL for all pairs
    union_parts = []
    for pair in ALL_PAIRS:
        source_table = f"{prefix}_{pair}"
        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair, * EXCEPT(interval_time, pair)
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
AS
WITH all_pairs AS (
    {union_sql}
)
SELECT
    interval_time,
    'MARKET' AS scope,
    COUNT(DISTINCT pair) AS pairs_count,
    AVG(reg_direction_45) AS mkt_direction_45,
    AVG(reg_direction_90) AS mkt_direction_90,
    AVG(reg_slope_45) AS mkt_slope_45,
    AVG(reg_slope_90) AS mkt_slope_90,
    COUNTIF(reg_direction_45 > 0) AS pairs_trending_up_45,
    COUNTIF(reg_direction_45 < 0) AS pairs_trending_down_45
FROM all_pairs
GROUP BY interval_time
"""
    return sql, output_table


def generate_mkt_sentiment_sql(variant: str) -> tuple:
    """Generate SQL for mkt_sentiment - net directional bias."""
    prefix = "mom_bqx" if variant == "bqx" else "mom"
    output_table = f"mkt_sentiment{'_bqx' if variant == 'bqx' else ''}"

    # Build UNION ALL for all pairs
    union_parts = []
    for pair in ALL_PAIRS:
        source_table = f"{prefix}_{pair}"
        union_parts.append(f"""
        SELECT interval_time, '{pair}' as pair, * EXCEPT(interval_time, pair)
        FROM `{PROJECT}.{DATASET}.{source_table}`""")

    union_sql = "\nUNION ALL".join(union_parts)

    # Calculate sentiment from momentum
    sent_cols = []
    for w in WINDOWS:
        sent_cols.append(f"""
        SUM(SIGN(mom_roc_{w})) AS mkt_net_direction_{w},
        AVG(mom_roc_{w}) AS mkt_avg_momentum_{w},
        AVG(mom_strength_{w}) AS mkt_avg_strength_{w}""")

    sent_sql = ",\n".join(sent_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}`
PARTITION BY DATE(interval_time)
AS
WITH all_pairs AS (
    {union_sql}
)
SELECT
    interval_time,
    'MARKET' AS scope,
    COUNT(DISTINCT pair) AS pairs_count,
    {sent_sql}
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

    # Generate all 8 MKT tables
    generators = [
        generate_mkt_vol_sql,
        generate_mkt_dispersion_sql,
        generate_mkt_regime_sql,
        generate_mkt_sentiment_sql
    ]

    for gen_func in generators:
        for variant in ['idx', 'bqx']:
            try:
                sql, table_name = gen_func(variant)
                if execute_bq(sql, table_name):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                results['failed'] += 1

    print(f"\nMKT Tables Complete: {results['success']}/8 success, {results['failed']}/8 failed")
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
