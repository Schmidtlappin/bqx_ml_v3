#!/usr/bin/env python3 -u
"""
Complete V2 Migration - Migrate all remaining tables from v1 to v2
Uses parallel processing for efficiency
"""
import subprocess
import sys
import time
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Configuration
SOURCE_DATASET = "bqx_ml_v3_features"
TARGET_DATASET = "bqx_ml_v3_features_v2"
PROJECT = "bqx-ml"
MAX_WORKERS = 8  # Parallel migrations

def get_missing_tables():
    """Get list of tables in v1 but not in v2"""
    try:
        with open('/tmp/missing_feature_tables.txt', 'r') as f:
            tables = [line.strip() for line in f if line.strip()]
        return tables
    except FileNotFoundError:
        print("Error: /tmp/missing_feature_tables.txt not found. Run comparison first.")
        sys.exit(1)

def get_cluster_column(table_name):
    """Determine the cluster column based on table type"""
    if table_name.startswith('cov_') or table_name.startswith('corr_'):
        return 'pair1'
    else:
        return 'pair'

def migrate_table(table_name):
    """Migrate a single table from v1 to v2 with partitioning and clustering"""
    cluster_col = get_cluster_column(table_name)

    # Check if table has interval_time column
    schema_cmd = ['bq', 'show', '--schema', '--format=json',
                  f'{PROJECT}:{SOURCE_DATASET}.{table_name}']
    result = subprocess.run(schema_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return (table_name, False, f"Cannot get schema")

    schema = result.stdout
    has_interval_time = 'interval_time' in schema
    has_cluster_col = cluster_col in schema

    # Build SQL query
    src = f'`{PROJECT}.{SOURCE_DATASET}.{table_name}`'
    dst = f'`{PROJECT}.{TARGET_DATASET}.{table_name}`'

    if not has_interval_time:
        sql = f"CREATE OR REPLACE TABLE {dst} AS SELECT * FROM {src}"
    elif not has_cluster_col:
        sql = f"CREATE OR REPLACE TABLE {dst} PARTITION BY DATE(interval_time) AS SELECT * FROM {src}"
    else:
        sql = f"CREATE OR REPLACE TABLE {dst} PARTITION BY DATE(interval_time) CLUSTER BY {cluster_col} AS SELECT * FROM {src}"

    # Run query using list args (no shell)
    cmd = ['bq', 'query', '--use_legacy_sql=false', '--location=us-central1', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return (table_name, True, "OK")
    else:
        err = result.stderr[:80] if result.stderr else "Unknown error"
        return (table_name, False, err)

def main():
    print("=" * 60)
    print("COMPLETE V2 MIGRATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tables = get_missing_tables()
    total = len(tables)
    print(f"\nTables to migrate: {total}")
    print(f"Parallel workers: {MAX_WORKERS}")
    print(f"Estimated time: ~{total * 30 // MAX_WORKERS // 60} minutes")
    print()

    completed = 0
    failed = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(migrate_table, table): table for table in tables}

        for future in as_completed(futures):
            table_name, success, message = future.result()
            completed += 1

            if success:
                print(f"[{completed}/{total}] ✓ {table_name}")
            else:
                failed.append((table_name, message))
                print(f"[{completed}/{total}] ✗ {table_name}: {message}")

            # Progress update every 50 tables
            if completed % 50 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed * 60
                remaining = (total - completed) / rate if rate > 0 else 0
                print(f"\n--- Progress: {completed}/{total} ({completed*100//total}%) | "
                      f"Rate: {rate:.1f}/min | ETA: {remaining:.1f} min ---\n")

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Total tables: {total}")
    print(f"Successful: {total - len(failed)}")
    print(f"Failed: {len(failed)}")
    print(f"Duration: {elapsed/60:.1f} minutes")

    if failed:
        print("\nFailed tables:")
        for table, msg in failed[:20]:
            print(f"  - {table}: {msg}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")

    # Verify final count
    result = subprocess.run(['bq', 'ls', '--max_results=10000',
                           f'{PROJECT}:{TARGET_DATASET}'],
                          capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    final_count = len([l for l in lines if l.strip()]) - 2  # subtract header lines
    print(f"\nFinal v2 table count: {final_count}")

    return 0 if not failed else 1

if __name__ == '__main__':
    sys.exit(main())
