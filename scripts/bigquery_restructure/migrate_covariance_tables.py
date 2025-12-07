#!/usr/bin/env python3
"""
Migrate P2 Covariance Tables to new dataset with partitioning.
Tables: cov_* (2,352 tables, ~515 GB)
These are cross-pair covariance tables: cov_{source}_{pair1}_{pair2}
"""

from google.cloud import bigquery
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'


def get_table_info(client, dataset, table_name):
    """Get row count and size for a table."""
    query = f"""
    SELECT row_count, size_bytes
    FROM `{PROJECT}.{dataset}.__TABLES__`
    WHERE table_id = '{table_name}'
    """
    result = list(client.query(query).result())
    if result:
        return result[0].row_count, result[0].size_bytes
    return 0, 0


def parse_cov_table_name(name):
    """Parse cov table name to extract components."""
    # Examples:
    # cov_agg_eurusd_gbpusd -> cov_agg_idx_eurusd_gbpusd
    # cov_agg_bqx_eurusd_gbpusd -> cov_agg_bqx_eurusd_gbpusd (already has bqx)
    # cov_reg_eurusd_gbpusd -> cov_reg_idx_eurusd_gbpusd

    parts = name.split('_')

    if len(parts) < 4:
        return None, None

    # cov_{source}_{bqx?}_{pair1}_{pair2}
    source = parts[1]

    if parts[2] == 'bqx':
        variant = 'bqx'
        pair1 = parts[3]
        pair2 = parts[4] if len(parts) > 4 else None
    else:
        variant = 'idx'
        pair1 = parts[2]
        pair2 = parts[3] if len(parts) > 3 else None

    if variant == 'idx':
        new_name = f"cov_{source}_idx_{pair1}_{pair2}"
    else:
        new_name = name  # Keep as is for BQX

    return name, new_name


def migrate_table(client, old_table, new_table, dry_run=False):
    """Migrate a single table with partitioning."""

    # Check if new table already exists
    try:
        client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_table}")
        return True, "already_exists"
    except:
        pass

    # Get old table info
    old_rows, old_bytes = get_table_info(client, OLD_DATASET, old_table)

    if old_rows == 0:
        return True, "empty"

    # For cov tables, cluster by pair1, pair2 (if they exist as columns)
    # Otherwise just cluster by first available column
    sql = f"""
    CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
    """

    if dry_run:
        print(f"  DRY: {new_table} ({old_rows:,} rows, {old_bytes/1024/1024:.1f} MB)")
        return True, "dry_run"

    try:
        job = client.query(sql)
        job.result()

        new_rows, _ = get_table_info(client, NEW_DATASET, new_table)

        if new_rows == old_rows:
            return True, "success"
        else:
            return False, f"row_mismatch_{old_rows}_{new_rows}"

    except Exception as e:
        return False, str(e)


def main():
    dry_run = '--dry-run' in sys.argv
    batch_size = 50  # Process in batches for progress reporting

    if dry_run:
        print("DRY RUN MODE - No tables will be created")

    client = bigquery.Client(project=PROJECT, location='us-central1')

    # Get all cov tables
    query = f"""
    SELECT table_id
    FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'cov_%'
    ORDER BY table_id
    """
    cov_tables = [row.table_id for row in client.query(query).result()]
    print(f"Found {len(cov_tables)} covariance tables to migrate")

    results = {'success': 0, 'failed': [], 'skipped': 0}

    for i, old_name in enumerate(cov_tables):
        # Parse and generate new name
        _, new_name = parse_cov_table_name(old_name)

        if not new_name:
            print(f"  WARN: Could not parse {old_name}")
            results['skipped'] += 1
            continue

        success, status = migrate_table(client, old_name, new_name, dry_run)

        if success:
            if status == 'already_exists' or status == 'empty':
                results['skipped'] += 1
            else:
                results['success'] += 1
        else:
            results['failed'].append((new_name, status))

        # Progress report
        if (i + 1) % batch_size == 0:
            print(f"Progress: {i+1}/{len(cov_tables)} ({results['success']} success, {results['skipped']} skip, {len(results['failed'])} fail)")

    # Final summary
    print(f"\n{'='*60}")
    print("COVARIANCE MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {len(cov_tables)}")
    print(f"Successful: {results['success']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed tables (first 20):")
        for name, error in results['failed'][:20]:
            print(f"  - {name}: {error}")

    return results


if __name__ == "__main__":
    main()
