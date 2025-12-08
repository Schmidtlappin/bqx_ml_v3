#!/usr/bin/env python3
"""
Migrate regime_ (volatility regime) tables to new dataset with partitioning.
Tables: regime_{pair}_{lookback}, regime_bqx_{pair}_{lookback} (112 tables)

These contain volatility regime classification features.
"""

from google.cloud import bigquery
import time

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'


def migrate_table(client, old_table, new_table):
    """Migrate a single regime table with partitioning."""
    sql = f"""
    CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair
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
    print("REGIME TABLE MIGRATION")
    print("=" * 70)

    # Get all regime_ tables from source
    query = f"""
    SELECT table_id, row_count
    FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'regime_%'
    ORDER BY table_id
    """
    tables = list(client.query(query).result())

    print(f"Found {len(tables)} regime tables to migrate\n")

    success = 0
    failed = 0
    skipped = 0

    for i, row in enumerate(tables, 1):
        old_name = row.table_id
        new_name = old_name  # Keep same name

        # Check if already exists
        try:
            client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_name}")
            print(f"  [{i}/{len(tables)}] SKIP {old_name} (already exists)")
            skipped += 1
            continue
        except:
            pass

        print(f"[{i}/{len(tables)}] {old_name}...", end=" ", flush=True)

        ok, result = migrate_table(client, old_name, new_name)

        if ok:
            print(f"OK ({result:,} rows)")
            success += 1
        else:
            print(f"FAILED: {result}")
            failed += 1

        # Progress update
        if i % 20 == 0:
            print(f"\n>>> Progress: {i}/{len(tables)} ({100*i/len(tables):.1f}%)\n")

        time.sleep(0.3)

    print("\n" + "=" * 70)
    print(f"COMPLETE: {success} success, {failed} failed, {skipped} skipped")
    print("=" * 70)


if __name__ == "__main__":
    main()
