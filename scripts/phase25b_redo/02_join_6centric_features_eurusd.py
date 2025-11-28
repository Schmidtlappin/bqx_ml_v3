#!/usr/bin/env python3
"""
Phase 2.5B REDO: 6-Centric Feature Joiner for EURUSD Pilot
==========================================================

INTERVAL-CENTRIC: All joins are on interval_time (row-based sequence).

Joins features from ALL 6 centrics for EURUSD:
1. PRIMARY: reg_eurusd, agg_eurusd, mom_eurusd, vol_eurusd, align_eurusd, lag_eurusd, regime_eurusd, corr_eurusd
   + BQX variants: reg_bqx_eurusd, agg_bqx_eurusd, etc.
2. VARIANT: var_*_eur, var_*_usd (currency family features)
3. COVARIANT: cov_*_eurusd_* (cross-pair relationships)
4. TRIANGULATION: tri_*_eur_usd_* (arbitrage triangle features)
5. SECONDARY: csi_*_eur, csi_*_usd (currency strength indices)
6. TERTIARY: mkt_* (global market features)

Output: bqx_ml_v3_analytics.features_6centric_eurusd
"""

from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PAIR = 'eurusd'
CURRENCIES = ['eur', 'usd']
DATASET = 'bqx-ml.bqx_ml_v3_features'
OUTPUT_TABLE = f'bqx-ml.bqx_ml_v3_analytics.features_6centric_{PAIR}'

# Feature table prefixes by centric
PRIMARY_PREFIXES = ['reg', 'agg', 'mom', 'vol', 'align', 'lag', 'regime', 'corr']
VARIANT_PREFIXES = ['var_reg', 'var_agg', 'var_mom', 'var_vol', 'var_align', 'var_lag', 'var_regime', 'var_corr']
COVARIANT_PREFIXES = ['cov_reg', 'cov_agg', 'cov_mom', 'cov_vol', 'cov_align', 'cov_lag', 'cov_regime', 'cov_corr']
SECONDARY_PREFIXES = ['csi_reg', 'csi_agg', 'csi_mom', 'csi_vol', 'csi_align', 'csi_lag', 'csi_regime', 'csi_corr']
TERTIARY_PREFIXES = ['mkt_reg', 'mkt_agg', 'mkt_mom', 'mkt_vol', 'mkt_align', 'mkt_lag', 'mkt_regime', 'mkt_corr']


def get_tables_for_pair(client, pair, currencies):
    """Get all feature tables relevant to this pair across all 6 centrics."""
    tables = {}

    # Query all table names
    query = f"""
    SELECT table_id FROM `{DATASET}.__TABLES__`
    ORDER BY table_id
    """
    all_tables = [row.table_id for row in client.query(query).result()]

    # 1. PRIMARY: Tables ending with pair name (e.g., reg_eurusd, reg_bqx_eurusd)
    tables['PRIMARY'] = [t for t in all_tables if t.endswith(f'_{pair}') or t.endswith(f'_bqx_{pair}')]
    # Filter to only known feature types
    tables['PRIMARY'] = [t for t in tables['PRIMARY'] if any(t.startswith(p) for p in PRIMARY_PREFIXES)]

    # 2. VARIANT: Tables with currency suffixes (e.g., var_reg_eur, var_reg_bqx_eur)
    tables['VARIANT'] = []
    for curr in currencies:
        variant_tables = [t for t in all_tables if t.endswith(f'_{curr}') or t.endswith(f'_bqx_{curr}')]
        variant_tables = [t for t in variant_tables if t.startswith('var_')]
        tables['VARIANT'].extend(variant_tables)

    # 3. COVARIANT: Tables with pair in name (e.g., cov_reg_eurusd_gbpusd)
    tables['COVARIANT'] = [t for t in all_tables if f'_{pair}_' in t or t.startswith(f'cov_') and pair in t]
    tables['COVARIANT'] = [t for t in tables['COVARIANT'] if t.startswith('cov_')]

    # 4. TRIANGULATION: Tables with currency triangles
    tables['TRIANGULATION'] = [t for t in all_tables if t.startswith('tri_')]
    # Filter to triangles involving our currencies
    tables['TRIANGULATION'] = [t for t in tables['TRIANGULATION'] if
                               any(curr in t for curr in currencies)]

    # 5. SECONDARY: CSI tables for our currencies
    tables['SECONDARY'] = []
    for curr in currencies:
        csi_tables = [t for t in all_tables if t.startswith('csi_') and t.endswith(f'_{curr}')]
        tables['SECONDARY'].extend(csi_tables)

    # 6. TERTIARY: Market-wide tables
    tables['TERTIARY'] = [t for t in all_tables if t.startswith('mkt_')]

    return tables


def get_numeric_columns(client, table_name):
    """Get all numeric columns from a table (excluding keys)."""
    query = f"""
    SELECT column_name, data_type
    FROM `{DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
      AND data_type IN ('FLOAT64', 'INT64', 'NUMERIC', 'BIGNUMERIC')
      AND column_name NOT IN ('interval_time', 'pair', 'source_value')
    ORDER BY ordinal_position
    """
    return [(row.column_name, row.data_type) for row in client.query(query).result()]


def generate_join_query(client, pair, currencies):
    """Generate SQL to join all 6-centric features."""
    tables_by_centric = get_tables_for_pair(client, pair, currencies)

    # Log table counts
    for centric, tbl_list in tables_by_centric.items():
        logger.info(f"{centric}: {len(tbl_list)} tables")

    # Build SELECT columns and JOIN clauses
    select_cols = ['base.interval_time']
    join_clauses = []
    table_idx = 0

    for centric, tbl_list in tables_by_centric.items():
        for tbl in tbl_list[:30]:  # Limit to 30 per centric to avoid query limits
            table_idx += 1
            alias = f't{table_idx}'

            # Get numeric columns
            cols = get_numeric_columns(client, tbl)
            if not cols:
                continue

            # Add columns with unique prefixes
            for col_name, _ in cols[:50]:  # Limit columns per table
                unique_name = f'{tbl}_{col_name}'
                select_cols.append(f'{alias}.{col_name} AS {unique_name}')

            # Add JOIN
            join_clauses.append(f'LEFT JOIN `{DATASET}.{tbl}` {alias} ON base.interval_time = {alias}.interval_time')

    # Use targets table as base (has all intervals)
    base_table = f'bqx-ml.bqx_ml_v3_analytics.targets_{pair}'

    query = f"""
-- Phase 2.5B REDO: 6-Centric Feature Join for {pair.upper()}
-- INTERVAL-CENTRIC: All joins on interval_time (row sequence)

CREATE OR REPLACE TABLE `{OUTPUT_TABLE}` AS
SELECT
  {',\n  '.join(select_cols)}
FROM `{base_table}` base
{chr(10).join(join_clauses)}
"""
    return query, len(select_cols) - 1, table_idx


def main():
    """Execute 6-centric feature join for EURUSD pilot."""
    client = bigquery.Client()

    logger.info(f"Phase 2.5B REDO: Joining 6-centric features for {PAIR.upper()}")
    logger.info(f"INTERVAL-CENTRIC: All joins on interval_time")

    # Generate and execute query
    query, col_count, table_count = generate_join_query(client, PAIR, CURRENCIES)

    logger.info(f"Joining {table_count} tables with {col_count} feature columns")
    logger.info("Sample of generated SQL (first 2000 chars):")
    print(query[:2000])

    # Due to BigQuery query limits, we may need to do this in chunks
    # For now, just print the query for review
    logger.info("Query generated. Execute manually or in chunks if needed.")

    # Optionally execute
    # job = client.query(query)
    # result = job.result()

    return query


if __name__ == '__main__':
    main()
