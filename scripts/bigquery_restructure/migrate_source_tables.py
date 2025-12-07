#!/usr/bin/env python3
"""
Migrate source tables from bqx_bq_uscen1 to bqx_bq_uscen1_v2.
Creates partitioned tables with standardized naming.

Source table categories:
- train_*: Training datasets (28 tables, ~1 TB)
- m1_*: Minute-level data (2016 tables, ~11 GB)
- bqx_*: BQX oscillator data (56 tables, ~20 GB)
- idx_*: Price index data (36 tables, ~3 GB)
- reg_*: Regression features (101 tables, ~97 GB)
- lag_*: Lag features (36 tables, ~21 GB)
- momentum_*: Momentum features (28 tables, ~9 GB)
- agg_*: Aggregation tables (28 tables, ~4 GB)
- microstructure_*: Microstructure features (28 tables, ~4 GB)
"""

from google.cloud import bigquery
import time
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_bq_uscen1'
NEW_DATASET = 'bqx_bq_uscen1_v2'

# Process specific category if provided
CATEGORY = sys.argv[1] if len(sys.argv) > 1 else 'all'


def get_table_schema(client, dataset, table_name):
    """Get table schema to determine partitioning columns."""
    try:
        table = client.get_table(f"{PROJECT}.{dataset}.{table_name}")
        columns = {field.name for field in table.schema}
        return columns
    except Exception:
        return set()


def get_timestamp_column(columns):
    """Determine the best timestamp column for partitioning."""
    # Priority order
    for col in ['interval_time', 'time', 'timestamp', 'datetime', 'date']:
        if col in columns:
            return col
    return None


def migrate_table(client, old_table, new_table, ts_col=None, cluster_col=None):
    """Migrate a single table with partitioning."""

    if ts_col and cluster_col:
        sql = f"""
        CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
        PARTITION BY DATE({ts_col})
        CLUSTER BY {cluster_col}
        AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
        """
    elif ts_col:
        sql = f"""
        CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
        PARTITION BY DATE({ts_col})
        AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
        """
    else:
        sql = f"""
        CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
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
    print(f"SOURCE DATA MIGRATION - Category: {CATEGORY}")
    print("=" * 70)

    # Get list of tables
    if CATEGORY == 'all':
        query = f"""
        SELECT table_id, row_count
        FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
        ORDER BY table_id
        """
    else:
        query = f"""
        SELECT table_id, row_count
        FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
        WHERE table_id LIKE '{CATEGORY}%'
        ORDER BY table_id
        """

    tables = list(client.query(query).result())
    print(f"Found {len(tables)} tables to migrate\n")

    success = 0
    failed = 0
    skipped = 0

    for i, row in enumerate(tables, 1):
        old_name = row.table_id
        new_name = old_name  # Keep same name, different dataset

        # Check if already exists
        try:
            client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_name}")
            print(f"  [{i}/{len(tables)}] SKIP {old_name} (already exists)")
            skipped += 1
            continue
        except:
            pass

        # Get schema for partitioning decision
        columns = get_table_schema(client, OLD_DATASET, old_name)
        ts_col = get_timestamp_column(columns)
        cluster_col = 'pair' if 'pair' in columns else None

        print(f"[{i}/{len(tables)}] Migrating {old_name}...", end=" ", flush=True)

        ok, result = migrate_table(client, old_name, new_name, ts_col, cluster_col)

        if ok:
            print(f"OK ({result:,} rows)")
            success += 1
        else:
            print(f"FAILED: {result}")
            failed += 1

        # Progress update
        if i % 50 == 0:
            print(f"\n>>> Progress: {i}/{len(tables)} ({100*i/len(tables):.1f}%) - {success} success, {failed} failed\n")

        # Small delay
        time.sleep(0.3)

    print("\n" + "=" * 70)
    print(f"MIGRATION COMPLETE: {success} success, {failed} failed, {skipped} skipped")
    print("=" * 70)

    # Log results
    with open('/tmp/migration_source_log.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Source migration ({CATEGORY}): {success} success, {failed} failed, {skipped} skipped\n")


if __name__ == "__main__":
    main()
