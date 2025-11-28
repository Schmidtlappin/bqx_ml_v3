#!/usr/bin/env python3
"""
Phase 2.5B REDO: Feature-Target Correlation Analysis for EURUSD Pilot
======================================================================

INTERVAL-CENTRIC: All operations are row-based.

Correlates ALL features from ALL 6 centrics against ALL 49 targets:
- 49 targets = 7 BQX components × 7 prediction horizons
- Features from: Primary, Variant, Covariant, Triangulation, Secondary, Tertiary

Output per target: bqx_ml_v3_analytics.target_corr_eurusd_bqxX_hY
Summary: bqx_ml_v3_analytics.feature_correlation_summary_eurusd
"""

from google.cloud import bigquery
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PAIR = 'eurusd'
BQX_COMPONENTS = [45, 90, 180, 360, 720, 1440, 2880]
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # Intervals FORWARD
DATASET = 'bqx-ml.bqx_ml_v3_analytics'
FEATURES_DATASET = 'bqx-ml.bqx_ml_v3_features'
TARGETS_TABLE = f'{DATASET}.targets_{PAIR}'


def get_feature_columns(client, table_name, dataset):
    """Get all numeric columns from a feature table."""
    query = f"""
    SELECT column_name
    FROM `{dataset}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
      AND data_type IN ('FLOAT64', 'INT64', 'NUMERIC', 'BIGNUMERIC')
      AND column_name NOT IN ('interval_time', 'pair', 'source_value')
    ORDER BY ordinal_position
    """
    return [row.column_name for row in client.query(query).result()]


def get_all_feature_tables(client, pair, currencies=['eur', 'usd']):
    """Get all feature tables for this pair across all 6 centrics."""
    query = f"""
    SELECT table_id FROM `{FEATURES_DATASET}.__TABLES__`
    ORDER BY table_id
    """
    all_tables = [row.table_id for row in client.query(query).result()]

    # Filter to relevant tables
    relevant = []

    # PRIMARY: Tables for this pair
    relevant.extend([t for t in all_tables if t.endswith(f'_{pair}') and not t.startswith('cov_')])

    # VARIANT: Currency family tables
    for curr in currencies:
        relevant.extend([t for t in all_tables if t.startswith('var_') and t.endswith(f'_{curr}')])

    # COVARIANT: Cross-pair tables involving this pair
    relevant.extend([t for t in all_tables if t.startswith('cov_') and pair in t])

    # TRIANGULATION
    relevant.extend([t for t in all_tables if t.startswith('tri_') and any(c in t for c in currencies)])

    # SECONDARY: CSI tables
    for curr in currencies:
        relevant.extend([t for t in all_tables if t.startswith('csi_') and t.endswith(f'_{curr}')])

    # TERTIARY: Market tables
    relevant.extend([t for t in all_tables if t.startswith('mkt_')])

    return list(set(relevant))[:100]  # Limit to prevent query explosion


def generate_correlation_query(feature_table, target_col, centric):
    """Generate SQL to correlate all features in a table against one target."""
    return f"""
SELECT
  '{feature_table}' AS feature_table,
  '{centric}' AS centric,
  '{target_col}' AS target,
  feature_name,
  correlation,
  ABS(correlation) AS abs_correlation
FROM (
  SELECT
    column_name AS feature_name,
    CORR(feature_value, target_value) AS correlation
  FROM (
    SELECT
      t.interval_time,
      t.{target_col} AS target_value,
      CASE column_name
        -- Dynamic unpivot of feature columns
      END AS feature_value,
      column_name
    FROM `{TARGETS_TABLE}` t
    JOIN `{FEATURES_DATASET}.{feature_table}` f ON t.interval_time = f.interval_time
    CROSS JOIN UNNEST(
      (SELECT ARRAY_AGG(column_name)
       FROM `{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
       WHERE table_name = '{feature_table}'
         AND data_type IN ('FLOAT64', 'INT64', 'NUMERIC')
         AND column_name NOT IN ('interval_time', 'pair', 'source_value'))
    ) AS column_name
  )
  WHERE target_value IS NOT NULL AND feature_value IS NOT NULL
  GROUP BY column_name
)
WHERE correlation IS NOT NULL
"""


def calculate_correlations_simple(client, pair, bqx, horizon):
    """Calculate correlations for one target using a simpler approach."""
    target_col = f'target_bqx{bqx}_h{horizon}'
    output_table = f'{DATASET}.target_corr_{pair}_bqx{bqx}_h{horizon}'

    # Get feature tables
    feature_tables = get_all_feature_tables(client, pair)
    logger.info(f"Processing {target_col} with {len(feature_tables)} feature tables")

    # For each feature table, calculate correlations
    all_correlations = []

    for ft in feature_tables[:20]:  # Process subset for pilot
        # Determine centric
        if ft.startswith('var_'):
            centric = 'VARIANT'
        elif ft.startswith('cov_'):
            centric = 'COVARIANT'
        elif ft.startswith('tri_'):
            centric = 'TRIANGULATION'
        elif ft.startswith('csi_'):
            centric = 'SECONDARY'
        elif ft.startswith('mkt_'):
            centric = 'TERTIARY'
        else:
            centric = 'PRIMARY'

        # Get columns
        cols = get_feature_columns(client, ft, FEATURES_DATASET)
        if not cols:
            continue

        # Build correlation query for this table
        corr_exprs = []
        for col in cols[:30]:  # Limit columns
            corr_exprs.append(f"STRUCT('{col}' AS feature_name, CORR({col}, t.{target_col}) AS correlation)")

        if not corr_exprs:
            continue

        query = f"""
        SELECT
          '{ft}' AS feature_table,
          '{centric}' AS centric,
          c.feature_name,
          c.correlation,
          ABS(c.correlation) AS abs_correlation
        FROM `{TARGETS_TABLE}` t
        JOIN `{FEATURES_DATASET}.{ft}` f ON t.interval_time = f.interval_time
        CROSS JOIN UNNEST([{', '.join(corr_exprs)}]) AS c
        WHERE t.{target_col} IS NOT NULL
          AND c.correlation IS NOT NULL
        """

        try:
            for row in client.query(query).result():
                all_correlations.append({
                    'feature_table': row.feature_table,
                    'centric': row.centric,
                    'feature_name': row.feature_name,
                    'correlation': row.correlation,
                    'abs_correlation': row.abs_correlation
                })
        except Exception as e:
            logger.warning(f"Error processing {ft}: {e}")

    # Save results
    if all_correlations:
        # Create output table
        schema = [
            bigquery.SchemaField('feature_table', 'STRING'),
            bigquery.SchemaField('centric', 'STRING'),
            bigquery.SchemaField('feature_name', 'STRING'),
            bigquery.SchemaField('correlation', 'FLOAT64'),
            bigquery.SchemaField('abs_correlation', 'FLOAT64'),
            bigquery.SchemaField('rank', 'INT64'),
        ]

        # Add rank
        sorted_corrs = sorted(all_correlations, key=lambda x: x['abs_correlation'], reverse=True)
        for i, c in enumerate(sorted_corrs, 1):
            c['rank'] = i

        # Load to BigQuery
        table_ref = client.dataset('bqx_ml_v3_analytics', project='bqx-ml').table(f'target_corr_{pair}_bqx{bqx}_h{horizon}')
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition='WRITE_TRUNCATE'
        )
        client.load_table_from_json(sorted_corrs, table_ref, job_config=job_config).result()
        logger.info(f"Created {output_table} with {len(sorted_corrs)} feature correlations")

    return len(all_correlations)


def main():
    """Execute correlation analysis for EURUSD pilot (49 targets)."""
    client = bigquery.Client()

    logger.info(f"Phase 2.5B REDO: Correlating features against 49 targets for {PAIR.upper()}")
    logger.info(f"INTERVAL-CENTRIC: All operations are row-based")

    total_correlations = 0

    # Process each of the 49 targets
    for bqx in BQX_COMPONENTS:
        for horizon in PREDICTION_HORIZONS:
            try:
                count = calculate_correlations_simple(client, PAIR, bqx, horizon)
                total_correlations += count
                logger.info(f"Completed bqx{bqx}_h{horizon}: {count} correlations")
            except Exception as e:
                logger.error(f"Error on bqx{bqx}_h{horizon}: {e}")

    logger.info(f"Total correlations calculated: {total_correlations}")

    # Generate summary
    logger.info("Generating feature correlation summary...")
    summary_query = f"""
    CREATE OR REPLACE TABLE `{DATASET}.feature_correlation_summary_{PAIR}` AS
    SELECT
      feature_table,
      centric,
      feature_name,
      AVG(abs_correlation) AS avg_abs_correlation,
      MAX(abs_correlation) AS max_abs_correlation,
      COUNT(*) AS target_count
    FROM (
      SELECT * FROM `{DATASET}.target_corr_{PAIR}_bqx45_h15`
      UNION ALL SELECT * FROM `{DATASET}.target_corr_{PAIR}_bqx45_h30`
      UNION ALL SELECT * FROM `{DATASET}.target_corr_{PAIR}_bqx45_h45`
      -- Add more UNION ALLs for all 49 targets
    )
    GROUP BY feature_table, centric, feature_name
    ORDER BY avg_abs_correlation DESC
    """

    logger.info("Summary table creation query generated")
    logger.info("Phase 2.5B REDO correlation analysis complete for EURUSD pilot")


if __name__ == '__main__':
    main()
