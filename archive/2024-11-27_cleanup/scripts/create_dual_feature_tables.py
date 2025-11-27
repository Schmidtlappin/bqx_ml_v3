#!/usr/bin/env python3
"""
Create dual feature tables by joining BQX and IDX tables.
These tables will contain both feature sets for multi-horizon model training.
"""

from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = 'bqx-ml'
DATASET_ID = 'bqx_ml_v3_features'

# Critical pairs for initial implementation
CRITICAL_PAIRS = {
    'EUR_USD': 'eurusd',
    'GBP_USD': 'gbpusd',
    'USD_JPY': 'usdjpy'
}

def create_dual_table(client, pair_key, table_prefix):
    """Create a dual feature table by joining BQX and IDX tables."""

    source_dataset = f"{PROJECT_ID}.{DATASET_ID}"
    bqx_table = f"{source_dataset}.{table_prefix}_bqx"
    idx_table = f"{source_dataset}.{table_prefix}_idx"
    dual_table = f"{source_dataset}.{table_prefix.replace(table_prefix, pair_key.lower())}_features_dual"

    # Create the query to join BQX and IDX features
    query = f"""
    CREATE OR REPLACE TABLE {dual_table} AS
    WITH aligned_data AS (
        SELECT
            -- Use BQX timestamp as the primary timestamp
            b.timestamp,

            -- BQX features (14 features)
            b.bqx_45,
            b.bqx_90,
            b.bqx_180,
            b.bqx_360,
            b.bqx_720,
            b.bqx_1440,
            b.bqx_2880,
            LAG(b.bqx_45, 1) OVER (ORDER BY b.timestamp) as bqx_45_lag1,
            LAG(b.bqx_45, 5) OVER (ORDER BY b.timestamp) as bqx_45_lag5,
            LAG(b.bqx_90, 1) OVER (ORDER BY b.timestamp) as bqx_90_lag1,
            LAG(b.bqx_90, 5) OVER (ORDER BY b.timestamp) as bqx_90_lag5,
            LAG(b.bqx_180, 1) OVER (ORDER BY b.timestamp) as bqx_180_lag1,
            AVG(b.bqx_45) OVER (ORDER BY b.timestamp ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_45_ma,
            AVG(b.bqx_90) OVER (ORDER BY b.timestamp ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_90_ma,

            -- IDX features (14 technical indicators)
            i.idx_rsi,
            i.idx_macd,
            i.idx_macd_signal,
            i.idx_bollinger_upper,
            i.idx_bollinger_lower,
            i.idx_bollinger_width,
            i.idx_stochastic_k,
            i.idx_stochastic_d,
            i.idx_atr,
            i.idx_obv,
            i.idx_ema_12,
            i.idx_ema_26,
            i.idx_adx,
            i.idx_cci,

            -- Add future targets for multi-horizon predictions
            LEAD(b.bqx_90, 15) OVER (ORDER BY b.timestamp) as target_h15,
            LEAD(b.bqx_90, 30) OVER (ORDER BY b.timestamp) as target_h30,
            LEAD(b.bqx_90, 45) OVER (ORDER BY b.timestamp) as target_h45,
            LEAD(b.bqx_90, 60) OVER (ORDER BY b.timestamp) as target_h60,
            LEAD(b.bqx_90, 75) OVER (ORDER BY b.timestamp) as target_h75,
            LEAD(b.bqx_90, 90) OVER (ORDER BY b.timestamp) as target_h90,
            LEAD(b.bqx_90, 105) OVER (ORDER BY b.timestamp) as target_h105

        FROM {bqx_table} b
        LEFT JOIN {idx_table} i
            ON b.timestamp = i.timestamp
        WHERE b.timestamp IS NOT NULL
            AND i.timestamp IS NOT NULL
    )
    SELECT * FROM aligned_data
    WHERE target_h105 IS NOT NULL  -- Ensure we have all future targets
    ORDER BY timestamp
    """

    try:
        logger.info(f"Creating dual table for {pair_key}...")
        query_job = client.query(query)
        query_job.result()  # Wait for the query to complete

        # Get the row count
        count_query = f"SELECT COUNT(*) as row_count FROM {dual_table}"
        count_result = client.query(count_query).result()
        row_count = list(count_result)[0].row_count

        logger.info(f"✅ Created {dual_table} with {row_count:,} rows")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create dual table for {pair_key}: {e}")
        return False

def main():
    """Create dual feature tables for critical currency pairs."""

    print("=" * 80)
    print("🔧 CREATING DUAL FEATURE TABLES FOR MULTI-HORIZON MODELS")
    print("=" * 80)

    client = bigquery.Client(project=PROJECT_ID)

    success_count = 0
    failed_count = 0

    for pair_key, table_prefix in CRITICAL_PAIRS.items():
        print(f"\nProcessing {pair_key}...")

        if create_dual_table(client, pair_key, table_prefix):
            success_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully created: {success_count} dual tables")
    print(f"❌ Failed: {failed_count} tables")

    if success_count > 0:
        print("\n🎯 Next Step: Run the multi-horizon implementation script")
        print("python3 scripts/implement_multi_horizon_models.py")

if __name__ == "__main__":
    main()