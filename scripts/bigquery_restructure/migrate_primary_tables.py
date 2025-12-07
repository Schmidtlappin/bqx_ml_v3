#!/usr/bin/env python3
"""
Migrate P1 Primary Tables to new dataset with partitioning.
Tables: reg, agg, align, vol, mom, der, div, mrt (448 tables, ~418 GB)
"""

from google.cloud import bigquery
import time
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'

PAIRS = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd',
    'usdcad', 'usdchf', 'usdjpy'
]

# P1 feature types
FEATURE_TYPES = ['reg', 'agg', 'align', 'vol', 'mom', 'der', 'div', 'mrt']


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


def migrate_table(client, old_table, new_table, dry_run=False):
    """Migrate a single table with partitioning."""

    # Check if new table already exists
    try:
        client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_table}")
        print(f"  SKIP: {new_table} already exists")
        return True, "already_exists"
    except:
        pass

    # Get old table info
    old_rows, old_bytes = get_table_info(client, OLD_DATASET, old_table)

    if old_rows == 0:
        print(f"  SKIP: {old_table} has 0 rows")
        return True, "empty"

    # Create new table with partitioning
    sql = f"""
    CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair
    AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
    """

    if dry_run:
        print(f"  DRY RUN: Would create {new_table} from {old_table} ({old_rows:,} rows, {old_bytes/1024/1024:.1f} MB)")
        return True, "dry_run"

    try:
        print(f"  Creating {new_table} from {old_table} ({old_rows:,} rows)...", end=" ", flush=True)
        job = client.query(sql)
        job.result()  # Wait for completion

        # Validate row count
        new_rows, new_bytes = get_table_info(client, NEW_DATASET, new_table)

        if new_rows == old_rows:
            print(f"OK ({new_rows:,} rows)")
            return True, "success"
        else:
            print(f"MISMATCH! Old: {old_rows}, New: {new_rows}")
            return False, f"row_mismatch_{old_rows}_{new_rows}"

    except Exception as e:
        print(f"ERROR: {e}")
        return False, str(e)


def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("DRY RUN MODE - No tables will be created")

    client = bigquery.Client(project=PROJECT, location='us-central1')

    results = {
        'success': [],
        'failed': [],
        'skipped': [],
    }

    total_tables = len(FEATURE_TYPES) * len(PAIRS) * 2  # IDX + BQX
    current = 0

    for ftype in FEATURE_TYPES:
        print(f"\n{'='*60}")
        print(f"Migrating {ftype.upper()} tables")
        print(f"{'='*60}")

        for pair in PAIRS:
            # IDX variant
            current += 1
            old_name = f"{ftype}_{pair}"
            new_name = f"{ftype}_idx_{pair}"
            print(f"\n[{current}/{total_tables}] {old_name} -> {new_name}")

            success, status = migrate_table(client, old_name, new_name, dry_run)
            if success:
                if 'skip' in status.lower() or status == 'already_exists':
                    results['skipped'].append(new_name)
                else:
                    results['success'].append(new_name)
            else:
                results['failed'].append((new_name, status))

            # BQX variant
            current += 1
            old_name = f"{ftype}_bqx_{pair}"
            new_name = f"{ftype}_bqx_{pair}"
            print(f"[{current}/{total_tables}] {old_name} -> {new_name}")

            success, status = migrate_table(client, old_name, new_name, dry_run)
            if success:
                if 'skip' in status.lower() or status == 'already_exists':
                    results['skipped'].append(new_name)
                else:
                    results['success'].append(new_name)
            else:
                results['failed'].append((new_name, status))

    # Summary
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {len(results['success'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed tables:")
        for name, error in results['failed']:
            print(f"  - {name}: {error}")

    return results


if __name__ == "__main__":
    main()
