#!/usr/bin/env python3
"""
Migrate P3 Secondary Tables to new dataset with partitioning.
Tables: rev, lag, regime, cyc, ext, base (raw pair tables)
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

WINDOWS = ['45', '90']  # For lag tables


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


def migrate_table(client, old_table, new_table, cluster_cols='pair', dry_run=False):
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
    CLUSTER BY {cluster_cols}
    AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
    """

    if dry_run:
        print(f"  DRY RUN: Would create {new_table} from {old_table} ({old_rows:,} rows, {old_bytes/1024/1024:.1f} MB)")
        return True, "dry_run"

    try:
        print(f"  Creating {new_table} from {old_table} ({old_rows:,} rows)...", end=" ", flush=True)
        job = client.query(sql)
        job.result()

        new_rows, _ = get_table_info(client, NEW_DATASET, new_table)

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

    results = {'success': [], 'failed': [], 'skipped': []}
    current = 0

    # REV tables (28 IDX + 28 BQX)
    print(f"\n{'='*60}\nMigrating REV tables\n{'='*60}")
    for pair in PAIRS:
        current += 1
        old, new = f"rev_{pair}", f"rev_idx_{pair}"
        print(f"\n[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

        current += 1
        old, new = f"rev_bqx_{pair}", f"rev_bqx_{pair}"
        print(f"[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

    # REGIME tables (56 IDX + 56 BQX)
    print(f"\n{'='*60}\nMigrating REGIME tables\n{'='*60}")
    for pair in PAIRS:
        current += 1
        old, new = f"regime_{pair}", f"regime_idx_{pair}"
        print(f"\n[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

        current += 1
        old, new = f"regime_bqx_{pair}", f"regime_bqx_{pair}"
        print(f"[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

    # LAG tables (with window in name - 56 IDX + 56 BQX)
    print(f"\n{'='*60}\nMigrating LAG tables\n{'='*60}")
    for pair in PAIRS:
        for window in WINDOWS:
            current += 1
            old = f"lag_{pair}_{window}"
            new = f"lag_idx_{pair}_w{window}"
            print(f"\n[{current}] {old} -> {new}")
            s, st = migrate_table(client, old, new, dry_run=dry_run)
            if not s:
                results['failed'].append((new, st))
            elif st == 'already_exists':
                results['skipped'].append(new)
            else:
                results['success'].append(new)

            current += 1
            old = f"lag_bqx_{pair}_{window}"
            new = f"lag_bqx_{pair}_w{window}"
            print(f"[{current}] {old} -> {new}")
            s, st = migrate_table(client, old, new, dry_run=dry_run)
            if not s:
                results['failed'].append((new, st))
            elif st == 'already_exists':
                results['skipped'].append(new)
            else:
                results['success'].append(new)

    # CYC tables (BQX only - 28)
    print(f"\n{'='*60}\nMigrating CYC tables (BQX only)\n{'='*60}")
    for pair in PAIRS:
        current += 1
        old, new = f"cyc_bqx_{pair}", f"cyc_bqx_{pair}"
        print(f"\n[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

    # EXT tables (BQX only - 28)
    print(f"\n{'='*60}\nMigrating EXT tables (BQX only)\n{'='*60}")
    for pair in PAIRS:
        current += 1
        old, new = f"ext_bqx_{pair}", f"ext_bqx_{pair}"
        print(f"\n[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

    # BASE tables (raw pair tables - 28 IDX + 28 BQX)
    print(f"\n{'='*60}\nMigrating BASE tables (raw pair data)\n{'='*60}")
    for pair in PAIRS:
        current += 1
        old, new = f"{pair}_idx", f"base_idx_{pair}"
        print(f"\n[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

        current += 1
        old, new = f"{pair}_bqx", f"base_bqx_{pair}"
        print(f"[{current}] {old} -> {new}")
        s, st = migrate_table(client, old, new, dry_run=dry_run)
        (results['success'] if s and st != 'already_exists' else results['skipped']).append(new)

    # Summary
    print(f"\n{'='*60}\nMIGRATION SUMMARY\n{'='*60}")
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
