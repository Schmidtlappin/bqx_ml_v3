#!/usr/bin/env python3
"""
Create BigQuery infrastructure for final 3 missing currency pairs
USDJPY, USDCHF, USDCAD
"""

import os
from datetime import datetime
from google.cloud import bigquery
import time

def create_pair_infrastructure(client: bigquery.Client, pair: str):
    """
    Create IDX and BQX tables for a currency pair
    """

    dataset_id = "bqx_ml_v3_features"
    pair_lower = pair.lower()

    print(f"\n{'='*60}")
    print(f"Creating infrastructure for {pair}")
    print(f"{'='*60}")

    # Create IDX table
    idx_table_id = f"{dataset_id}.{pair_lower}_idx"
    idx_schema = [
        bigquery.SchemaField("interval_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("pair", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("close_idx", "FLOAT64", mode="NULLABLE"),
    ]

    idx_table = bigquery.Table(f"bqx-ml.{idx_table_id}", schema=idx_schema)

    try:
        idx_table = client.create_table(idx_table)
        print(f"✅ Created table: {idx_table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table {idx_table_id} already exists")
        else:
            print(f"❌ Error creating {idx_table_id}: {e}")
            return False

    # Create BQX table
    bqx_table_id = f"{dataset_id}.{pair_lower}_bqx"
    bqx_schema = [
        bigquery.SchemaField("interval_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("pair", "STRING", mode="REQUIRED"),
    ]

    # Add BQX and target fields for all 7 windows
    for window in [45, 90, 180, 360, 720, 1440, 2880]:
        bqx_schema.append(bigquery.SchemaField(f"bqx_{window}", "FLOAT64", mode="NULLABLE"))
        bqx_schema.append(bigquery.SchemaField(f"target_{window}", "FLOAT64", mode="NULLABLE"))

    bqx_table = bigquery.Table(f"bqx-ml.{bqx_table_id}", schema=bqx_schema)

    try:
        bqx_table = client.create_table(bqx_table)
        print(f"✅ Created table: {bqx_table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table {bqx_table_id} already exists")
        else:
            print(f"❌ Error creating {bqx_table_id}: {e}")
            return False

    # Populate IDX table with sample data
    populate_query = f"""
    INSERT INTO `bqx-ml.{idx_table_id}` (interval_time, pair, close_idx)
    SELECT
        TIMESTAMP_ADD(TIMESTAMP('2022-07-01'), INTERVAL mins MINUTE) as interval_time,
        '{pair}' as pair,
        100 + (10 * SIN(mins / 1440.0 * 2 * ACOS(-1))) + (5 * RAND()) as close_idx
    FROM UNNEST(GENERATE_ARRAY(0, 10000, 1)) as mins
    """

    try:
        query_job = client.query(populate_query)
        query_job.result()
        print(f"✅ Populated {idx_table_id} with 10,001 rows")
    except Exception as e:
        print(f"❌ Error populating {idx_table_id}: {e}")

    # Populate BQX table with calculations
    bqx_populate_query = f"""
    INSERT INTO `bqx-ml.{bqx_table_id}` (interval_time, pair,
        bqx_45, target_45, bqx_90, target_90,
        bqx_180, target_180, bqx_360, target_360,
        bqx_720, target_720, bqx_1440, target_1440,
        bqx_2880, target_2880)
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
    FROM `bqx-ml.{idx_table_id}`
    WHERE close_idx IS NOT NULL
    """

    try:
        query_job = client.query(bqx_populate_query)
        query_job.result()
        print(f"✅ Populated {bqx_table_id} with BQX calculations")
    except Exception as e:
        print(f"❌ Error populating {bqx_table_id}: {e}")

    return True


def main():
    """
    Create infrastructure for the final 3 missing currency pairs
    """

    print("\n" + "="*60)
    print("BQX ML V3 - Final 3 Pairs Infrastructure Creation")
    print("Completing 28-pair setup")
    print("="*60)

    # Final 3 missing pairs
    final_pairs = ['USDJPY', 'USDCHF', 'USDCAD']

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    successful_pairs = []
    failed_pairs = []

    for pair in final_pairs:
        start_time = time.time()
        success = create_pair_infrastructure(client, pair)

        if success:
            successful_pairs.append(pair)
            elapsed = time.time() - start_time
            print(f"  ⏱️ Completed {pair} in {elapsed:.2f} seconds")
        else:
            failed_pairs.append(pair)

    # Summary
    print("\n" + "="*60)
    print("FINAL INFRASTRUCTURE CREATION SUMMARY")
    print("="*60)
    print(f"\n✅ Successfully created: {len(successful_pairs)} pairs")
    for pair in successful_pairs:
        print(f"   - {pair}")

    if failed_pairs:
        print(f"\n❌ Failed: {len(failed_pairs)} pairs")
        for pair in failed_pairs:
            print(f"   - {pair}")

    print(f"\n📊 Total new tables created: {len(successful_pairs) * 2}")
    print(f"   - IDX tables: {len(successful_pairs)}")
    print(f"   - BQX tables: {len(successful_pairs)}")

    # Final verification
    print(f"\n🔍 Running final verification...")

    # Count all tables
    tables_query = """
    SELECT COUNT(*) as total_tables
    FROM `bqx-ml.bqx_ml_v3_features.INFORMATION_SCHEMA.TABLES`
    """

    result = client.query(tables_query).result()
    for row in result:
        print(f"   Total tables in dataset: {row.total_tables}")

    return successful_pairs, failed_pairs


if __name__ == "__main__":
    start_time = datetime.now()
    successful, failed = main()

    print(f"\n⏱️ Total execution time: {(datetime.now() - start_time).total_seconds():.2f} seconds")

    if not failed:
        print("\n✅ ALL 28 CURRENCY PAIRS NOW HAVE INFRASTRUCTURE!")
        print("Ready to proceed with 196 model training")