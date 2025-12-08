#!/usr/bin/env python3
"""
Batched covariance table migration - runs as one of N parallel batches.
Usage: python migrate_covariance_batched.py <batch_num> <total_batches>
Example: python migrate_covariance_batched.py 1 4  # Run batch 1 of 4
"""

from google.cloud import bigquery
import time
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'

# Get batch parameters
BATCH_NUM = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TOTAL_BATCHES = int(sys.argv[2]) if len(sys.argv) > 2 else 4


def migrate_table(client, old_table, new_table):
    """Migrate a single covariance table with partitioning."""
    # Covariance tables have pair1/pair2 columns, not pair
    sql = f"""
    CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair1
    AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
    """

    try:
        job = client.query(sql)
        job.result()

        # Verify row count
        verify = client.query(f"""
            SELECT
                (SELECT COUNT(*) FROM `{PROJECT}.{OLD_DATASET}.{old_table}`) as old_count,
                (SELECT COUNT(*) FROM `{PROJECT}.{NEW_DATASET}.{new_table}`) as new_count
        """)
        result = list(verify.result())[0]

        if result.old_count == result.new_count:
            return True, result.new_count
        else:
            return False, f"Count mismatch: {result.old_count} vs {result.new_count}"

    except Exception as e:
        return False, str(e)


def main():
    client = bigquery.Client(project=PROJECT)

    print("=" * 70)
    print(f"COVARIANCE MIGRATION - Batch {BATCH_NUM} of {TOTAL_BATCHES}")
    print("=" * 70)

    # Get all cov_ tables from source
    query = f"""
    SELECT table_id
    FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'cov_%'
    ORDER BY table_id
    """
    all_tables = [row.table_id for row in client.query(query).result()]

    # Calculate this batch's slice
    batch_size = len(all_tables) // TOTAL_BATCHES
    start_idx = (BATCH_NUM - 1) * batch_size
    end_idx = start_idx + batch_size if BATCH_NUM < TOTAL_BATCHES else len(all_tables)

    tables = all_tables[start_idx:end_idx]

    print(f"Total cov_ tables: {len(all_tables)}")
    print(f"This batch: tables {start_idx+1} to {end_idx} ({len(tables)} tables)")
    print()

    success = 0
    failed = 0
    skipped = 0

    for i, old_name in enumerate(tables, 1):
        # Keep same name for covariance tables
        new_name = old_name

        # Check if already exists
        try:
            client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_name}")
            skipped += 1
            continue
        except:
            pass

        print(f"[B{BATCH_NUM}:{i}/{len(tables)}] {old_name}...", end=" ", flush=True)

        ok, result = migrate_table(client, old_name, new_name)

        if ok:
            print(f"OK ({result:,} rows)")
            success += 1
        else:
            print(f"FAILED: {result}")
            failed += 1

        # Progress update every 100 tables
        if i % 100 == 0:
            print(f"\n>>> Batch {BATCH_NUM} Progress: {i}/{len(tables)} ({100*i/len(tables):.1f}%)\n")

        time.sleep(0.2)

    print("\n" + "=" * 70)
    print(f"BATCH {BATCH_NUM} COMPLETE: {success} success, {failed} failed, {skipped} skipped")
    print("=" * 70)


if __name__ == "__main__":
    main()
