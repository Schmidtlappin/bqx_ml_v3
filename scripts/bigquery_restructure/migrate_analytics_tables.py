#!/usr/bin/env python3
"""
Migrate analytics/target tables to bqx_ml_v3_analytics_v2.
Creates partitioned, clustered tables with standardized naming.
"""

from google.cloud import bigquery
import time

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_analytics'
NEW_DATASET = 'bqx_ml_v3_analytics_v2'

PAIRS = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd',
    'usdcad', 'usdchf', 'usdjpy'
]


def get_table_schema(client, dataset, table_name):
    """Get table schema to determine if it has interval_time and pair."""
    try:
        table = client.get_table(f"{PROJECT}.{dataset}.{table_name}")
        columns = {field.name for field in table.schema}
        return columns
    except Exception:
        return set()


def migrate_table(client, old_table, new_table, has_interval_time=True, has_pair=True):
    """Migrate a single table with partitioning."""

    # Build CREATE statement based on available columns
    if has_interval_time and has_pair:
        sql = f"""
        CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
        PARTITION BY DATE(interval_time)
        CLUSTER BY pair
        AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
        """
    elif has_interval_time:
        sql = f"""
        CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
        PARTITION BY DATE(interval_time)
        AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
        """
    else:
        # No partitioning for tables without interval_time
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
    print("ANALYTICS/TARGETS MIGRATION")
    print("=" * 70)

    # Get list of tables
    query = f"""
    SELECT table_id, row_count
    FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    ORDER BY table_id
    """
    tables = list(client.query(query).result())

    print(f"Found {len(tables)} tables to migrate\n")

    success = 0
    failed = 0
    skipped = 0

    for row in tables:
        old_name = row.table_id
        new_name = old_name  # Keep same name for analytics

        # Check if already exists
        try:
            client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_name}")
            print(f"  SKIP {old_name} (already exists)")
            skipped += 1
            continue
        except:
            pass

        # Get schema to check for interval_time and pair
        columns = get_table_schema(client, OLD_DATASET, old_name)
        has_interval_time = 'interval_time' in columns
        has_pair = 'pair' in columns

        print(f"Migrating {old_name}...", end=" ", flush=True)

        ok, result = migrate_table(client, old_name, new_name, has_interval_time, has_pair)

        if ok:
            print(f"OK ({result:,} rows)")
            success += 1
        else:
            print(f"FAILED: {result}")
            failed += 1

        # Small delay to avoid rate limits
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print(f"MIGRATION COMPLETE: {success} success, {failed} failed, {skipped} skipped")
    print("=" * 70)

    # Log results
    with open('/tmp/migration_analytics_log.txt', 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Analytics migration: {success} success, {failed} failed, {skipped} skipped\n")


if __name__ == "__main__":
    main()
