#!/usr/bin/env python3
"""
Phase 2.5B REDO: Target Generation for EURUSD Pilot
===================================================

INTERVAL-CENTRIC: All LEAD operations are row-based (not time-based).
- LEAD(bqx_45, 15) = bqx_45 at row+15 in interval sequence
- Horizons [15, 30, 45, 60, 75, 90, 105] are INTERVAL counts

Generates 49 target columns:
- 7 BQX components × 7 prediction horizons = 49 targets
- BQX components: [bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880]
- Prediction horizons: [15, 30, 45, 60, 75, 90, 105] intervals FORWARD (row-based, NOT time-based)

Output: bqx_ml_v3_analytics.targets_eurusd
"""

from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - INTERVAL-CENTRIC
BQX_COMPONENTS = [45, 90, 180, 360, 720, 1440, 2880]
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # Intervals FORWARD (not minutes!)
PAIR = 'eurusd'
SOURCE_TABLE = f'bqx-ml.bqx_ml_v3_features.{PAIR}_bqx'
TARGET_TABLE = f'bqx-ml.bqx_ml_v3_analytics.targets_{PAIR}'

def generate_target_query():
    """Generate SQL for creating 49 target columns using LEAD (interval-centric)."""

    # Build LEAD columns for all 49 targets
    lead_columns = []
    for bqx in BQX_COMPONENTS:
        for h in PREDICTION_HORIZONS:
            # INTERVAL-CENTRIC: LEAD(column, N) operates on row position
            col_name = f'target_bqx{bqx}_h{h}'
            lead_expr = f'LEAD(bqx_{bqx}, {h}) OVER (ORDER BY interval_time) AS {col_name}'
            lead_columns.append(lead_expr)

    lead_sql = ',\n  '.join(lead_columns)

    query = f"""
-- Phase 2.5B REDO: Target Generation for {PAIR.upper()} Pilot
-- INTERVAL-CENTRIC: LEAD operations are row-based, not time-based
-- 49 targets = 7 BQX components × 7 prediction horizons

CREATE OR REPLACE TABLE `{TARGET_TABLE}` AS
SELECT
  interval_time,
  pair,
  -- Current BQX values (for reference only, NOT features for prediction)
  bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
  -- TARGETS: Future BQX values at each prediction horizon
  -- LEAD(bqx_X, H) = bqx_X value H intervals into the FUTURE
  {lead_sql}
FROM `{SOURCE_TABLE}`
WHERE pair = '{PAIR.upper()}'
ORDER BY interval_time
"""
    return query

def main():
    """Execute target generation for EURUSD pilot."""
    client = bigquery.Client()

    logger.info(f"Phase 2.5B REDO: Generating 49 targets for {PAIR.upper()}")
    logger.info(f"BQX components: {BQX_COMPONENTS}")
    logger.info(f"Prediction horizons: {PREDICTION_HORIZONS}")
    logger.info(f"INTERVAL-CENTRIC: LEAD operations are row-based")

    query = generate_target_query()
    logger.info("Generated SQL query:")
    print(query)

    # Execute query
    logger.info(f"Creating target table: {TARGET_TABLE}")
    job = client.query(query)
    result = job.result()

    # Verify row count
    verify_query = f"SELECT COUNT(*) as cnt FROM `{TARGET_TABLE}`"
    verify_result = list(client.query(verify_query).result())[0]
    logger.info(f"Target table created with {verify_result.cnt:,} rows")

    # Sample targets to verify
    sample_query = f"""
    SELECT
        interval_time,
        bqx_45,
        target_bqx45_h15,
        target_bqx45_h30,
        target_bqx2880_h105
    FROM `{TARGET_TABLE}`
    WHERE target_bqx45_h15 IS NOT NULL
    LIMIT 5
    """
    logger.info("Sample target values:")
    for row in client.query(sample_query).result():
        print(f"  interval={row.interval_time}, bqx_45={row.bqx_45:.4f}, "
              f"h15={row.target_bqx45_h15:.4f}, h30={row.target_bqx45_h30:.4f}")

    logger.info("Target generation complete for EURUSD pilot")
    return TARGET_TABLE

if __name__ == '__main__':
    main()
