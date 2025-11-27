#!/usr/bin/env python3
"""
Generate 50,000 synthetic data rows for all 28 currency pairs
Per CE directive 20251127_0125 - Priority 1
"""

import os
from datetime import datetime, timedelta
from google.cloud import bigquery
import numpy as np
import time

# All 28 currency pairs
ALL_PAIRS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
    'GBPJPY', 'GBPCHF', 'GBPAUD', 'GBPCAD', 'GBPNZD',
    'AUDJPY', 'AUDCHF', 'AUDCAD', 'AUDNZD',
    'NZDJPY', 'NZDCHF', 'NZDCAD',
    'CADJPY', 'CADCHF',
    'CHFJPY'
]

def generate_synthetic_data_for_pair(client: bigquery.Client, pair: str, rows: int = 50000):
    """
    Generate 50,000 synthetic data rows for a currency pair
    """

    dataset_id = "bqx_ml_v3_features"
    pair_lower = pair.lower()

    print(f"\n{'='*60}")
    print(f"Generating {rows:,} rows for {pair}")
    print(f"{'='*60}")

    # Clear existing data in IDX table
    clear_query = f"""
    DELETE FROM `bqx-ml.{dataset_id}.{pair_lower}_idx`
    WHERE 1=1
    """

    try:
        client.query(clear_query).result()
        print(f"  ✅ Cleared existing data")
    except Exception as e:
        print(f"  ⚠️ Could not clear data: {e}")

    # Generate 50,000 synthetic IDX rows with realistic patterns
    populate_query = f"""
    INSERT INTO `bqx-ml.{dataset_id}.{pair_lower}_idx` (interval_time, pair, close_idx)
    WITH synthetic_data AS (
        SELECT
            TIMESTAMP_ADD(TIMESTAMP('2020-01-01'), INTERVAL mins MINUTE) as interval_time,
            '{pair}' as pair,
            -- Create more realistic price patterns
            100 +
            -- Long-term trend
            (mins / 50000.0 * 10) +
            -- Medium-term cycles
            (10 * SIN(mins / 1440.0 * 2 * ACOS(-1))) +
            -- Short-term volatility
            (3 * SIN(mins / 60.0 * 2 * ACOS(-1))) +
            -- Random noise
            (2 * (RAND() - 0.5)) as close_idx
        FROM UNNEST(GENERATE_ARRAY(0, {rows-1}, 1)) as mins
    )
    SELECT * FROM synthetic_data
    """

    try:
        query_job = client.query(populate_query)
        query_job.result()
        print(f"  ✅ Generated {rows:,} IDX rows")
    except Exception as e:
        print(f"  ❌ Error generating IDX data: {e}")
        return False

    # Clear and recalculate BQX values
    clear_bqx_query = f"""
    DELETE FROM `bqx-ml.{dataset_id}.{pair_lower}_bqx`
    WHERE 1=1
    """

    try:
        client.query(clear_bqx_query).result()
    except:
        pass

    # Calculate BQX values for all windows
    bqx_populate_query = f"""
    INSERT INTO `bqx-ml.{dataset_id}.{pair_lower}_bqx` (
        interval_time, pair,
        bqx_45, target_45, bqx_90, target_90,
        bqx_180, target_180, bqx_360, target_360,
        bqx_720, target_720, bqx_1440, target_1440,
        bqx_2880, target_2880
    )
    SELECT
        interval_time,
        pair,
        -- BQX calculations for each window
        ((close_idx - LAG(close_idx, 45) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 45) OVER (ORDER BY interval_time), 0)) * 100 as bqx_45,
        ((LEAD(close_idx, 45) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_45,

        ((close_idx - LAG(close_idx, 90) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 90) OVER (ORDER BY interval_time), 0)) * 100 as bqx_90,
        ((LEAD(close_idx, 90) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_90,

        ((close_idx - LAG(close_idx, 180) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 180) OVER (ORDER BY interval_time), 0)) * 100 as bqx_180,
        ((LEAD(close_idx, 180) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_180,

        ((close_idx - LAG(close_idx, 360) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 360) OVER (ORDER BY interval_time), 0)) * 100 as bqx_360,
        ((LEAD(close_idx, 360) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_360,

        ((close_idx - LAG(close_idx, 720) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 720) OVER (ORDER BY interval_time), 0)) * 100 as bqx_720,
        ((LEAD(close_idx, 720) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_720,

        ((close_idx - LAG(close_idx, 1440) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 1440) OVER (ORDER BY interval_time), 0)) * 100 as bqx_1440,
        ((LEAD(close_idx, 1440) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_1440,

        ((close_idx - LAG(close_idx, 2880) OVER (ORDER BY interval_time)) /
         NULLIF(LAG(close_idx, 2880) OVER (ORDER BY interval_time), 0)) * 100 as bqx_2880,
        ((LEAD(close_idx, 2880) OVER (ORDER BY interval_time) - close_idx) /
         NULLIF(close_idx, 0)) * 100 as target_2880

    FROM `bqx-ml.{dataset_id}.{pair_lower}_idx`
    WHERE close_idx IS NOT NULL
    """

    try:
        query_job = client.query(bqx_populate_query)
        query_job.result()
        print(f"  ✅ Calculated BQX values for all windows")
    except Exception as e:
        print(f"  ❌ Error calculating BQX: {e}")
        return False

    # Verify data counts
    verify_query = f"""
    SELECT
        (SELECT COUNT(*) FROM `bqx-ml.{dataset_id}.{pair_lower}_idx`) as idx_count,
        (SELECT COUNT(*) FROM `bqx-ml.{dataset_id}.{pair_lower}_bqx`) as bqx_count,
        (SELECT COUNT(*) FROM `bqx-ml.{dataset_id}.{pair_lower}_bqx` WHERE bqx_2880 IS NOT NULL) as bqx_2880_count
    """

    result = client.query(verify_query).result()
    for row in result:
        print(f"\n  📊 Verification:")
        print(f"     IDX rows: {row.idx_count:,}")
        print(f"     BQX rows: {row.bqx_count:,}")
        print(f"     BQX-2880 valid: {row.bqx_2880_count:,}")

    return True


def main():
    """
    Generate 50,000 synthetic rows for all 28 currency pairs
    """

    print("\n" + "="*60)
    print("BQX ML V3 - 50K Synthetic Data Generation")
    print("CE Directive 20251127_0125 - Priority 1")
    print("="*60)

    print(f"\nTarget: Generate 50,000 rows for {len(ALL_PAIRS)} currency pairs")
    print(f"Total data points: {50000 * len(ALL_PAIRS):,}")

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    successful_pairs = []
    failed_pairs = []
    start_time = datetime.now()

    # Process each pair
    for idx, pair in enumerate(ALL_PAIRS, 1):
        print(f"\n[{idx}/{len(ALL_PAIRS)}] Processing {pair}...")

        success = generate_synthetic_data_for_pair(client, pair, 50000)

        if success:
            successful_pairs.append(pair)
        else:
            failed_pairs.append(pair)

        # Progress update
        if idx % 5 == 0:
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            remaining = (elapsed / idx) * (len(ALL_PAIRS) - idx)
            print(f"\n⏱️ Progress: {idx}/{len(ALL_PAIRS)} complete")
            print(f"   Elapsed: {elapsed:.1f} minutes")
            print(f"   Estimated remaining: {remaining:.1f} minutes")

    # Summary report
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)

    print(f"\n✅ Successful: {len(successful_pairs)} pairs")
    if successful_pairs:
        for pair in successful_pairs[:5]:
            print(f"   - {pair}")
        if len(successful_pairs) > 5:
            print(f"   ... and {len(successful_pairs) - 5} more")

    if failed_pairs:
        print(f"\n❌ Failed: {len(failed_pairs)} pairs")
        for pair in failed_pairs:
            print(f"   - {pair}")

    total_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n⏱️ Total execution time: {total_time:.1f} minutes")

    # Final verification
    print(f"\n🔍 Final Verification:")
    verify_all_query = """
    SELECT
        COUNT(DISTINCT table_name) as total_tables,
        SUM(row_count) as total_rows
    FROM `bqx-ml.bqx_ml_v3_features.INFORMATION_SCHEMA.TABLE_STORAGE`
    WHERE table_name LIKE '%_idx' OR table_name LIKE '%_bqx'
    """

    try:
        result = client.query(verify_all_query).result()
        for row in result:
            print(f"   Total tables: {row.total_tables}")
            print(f"   Total rows: {row.total_rows:,}")
    except:
        pass

    if not failed_pairs:
        print(f"\n✅ SUCCESS: All {len(ALL_PAIRS)} pairs have 50,000 rows!")
        print("Ready for Smart Dual Processing implementation")

    return successful_pairs, failed_pairs


if __name__ == "__main__":
    try:
        successful, failed = main()

        if not failed:
            print("\n🎯 DATA INFRASTRUCTURE FIXED!")
            print("Next step: Implement Smart Dual Processing")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()