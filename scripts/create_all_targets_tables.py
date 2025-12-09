#!/usr/bin/env python3
"""
Create targets tables for all 28 currency pairs following the BQX Target Formula Mandate.

Mandate: /mandate/BQX_TARGET_FORMULA_MANDATE.md
Formula: target_bqx{window}_h{horizon} = LEAD(bqx_{window}, horizon)

Creates 49 target columns per pair (7 BQX windows × 7 prediction horizons)
"""

import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# All 28 currency pairs
ALL_PAIRS = [
    'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
    'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'eurcad', 'eurnzd',
    'gbpjpy', 'gbpchf', 'gbpaud', 'gbpcad', 'gbpnzd',
    'audjpy', 'audchf', 'audcad', 'audnzd',
    'nzdjpy', 'nzdchf', 'nzdcad',
    'cadjpy', 'cadchf',
    'chfjpy'
]

BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def generate_targets_sql(pair: str) -> str:
    """Generate SQL to create targets table for a pair following the mandate."""

    # Build target columns for all window/horizon combinations
    target_columns = []
    for window in BQX_WINDOWS:
        for horizon in HORIZONS:
            col = f"LEAD(bqx_{window}, {horizon}) OVER (ORDER BY interval_time) as target_bqx{window}_h{horizon}"
            target_columns.append(col)

    target_cols_sql = ",\n        ".join(target_columns)

    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair
    AS
    WITH source AS (
        SELECT
            interval_time,
            pair,
            bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
        FROM `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}`
        WHERE bqx_45 IS NOT NULL
    )
    SELECT
        interval_time,
        pair,
        -- Base BQX values (features for autoregressive modeling)
        bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
        -- Targets: Future BQX values at each prediction horizon
        {target_cols_sql}
    FROM source
    """
    return sql


def create_targets_table(pair: str) -> dict:
    """Create targets table for a single pair."""
    print(f"  Creating targets_{pair}...")

    sql = generate_targets_sql(pair)

    # Write SQL to temp file
    sql_file = f"/tmp/targets_{pair}.sql"
    with open(sql_file, "w") as f:
        f.write(sql)

    # Execute query
    cmd = ["bq", "query", "--use_legacy_sql=false", "--max_rows=0"]
    result = subprocess.run(cmd, stdin=open(sql_file), capture_output=True, text=True)

    if result.returncode != 0:
        return {"pair": pair, "status": "FAILED", "error": result.stderr[:200]}

    # Verify row count
    verify_cmd = [
        "bq", "query", "--use_legacy_sql=false", "--format=csv", "--max_rows=1",
        f"SELECT COUNT(*) as cnt FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`"
    ]
    verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)

    try:
        row_count = int(verify_result.stdout.strip().split('\n')[-1])
    except:
        row_count = 0

    return {"pair": pair, "status": "SUCCESS", "row_count": row_count}


def main():
    print("=" * 60)
    print("BQX ML V3 - Create Targets Tables for All Pairs")
    print("Following mandate: /mandate/BQX_TARGET_FORMULA_MANDATE.md")
    print("=" * 60)

    # Check command line arguments for force rebuild
    force_rebuild = "--force" in sys.argv or "-f" in sys.argv
    skip_eurusd = "--skip-eurusd" in sys.argv

    # Check which pairs already have targets tables
    check_cmd = [
        "bq", "--location=us-central1", "query", "--use_legacy_sql=false", "--format=csv",
        f"SELECT table_name FROM `{PROJECT}.{ANALYTICS_DATASET}.INFORMATION_SCHEMA.TABLES` WHERE table_name LIKE 'targets_%'"
    ]
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)
    existing = set(check_result.stdout.strip().split('\n')[1:])  # Skip header

    print(f"\nExisting targets tables: {len(existing)}")
    for t in sorted(existing)[:10]:
        print(f"  - {t}")
    if len(existing) > 10:
        print(f"  ... and {len(existing) - 10} more")

    # Determine which pairs to process
    if force_rebuild:
        pairs_to_process = [p for p in ALL_PAIRS if not (skip_eurusd and p == 'eurusd')]
        print(f"\nFORCE REBUILD: Will recreate {len(pairs_to_process)} targets tables")
    else:
        pairs_to_process = []
        for pair in ALL_PAIRS:
            table_name = f"targets_{pair}"
            if table_name not in existing:
                pairs_to_process.append(pair)
        print(f"\nPairs needing targets tables: {len(pairs_to_process)}")

    if not pairs_to_process:
        print("\nAll pairs already have targets tables!")
        print("Use --force to rebuild all tables, or --force --skip-eurusd to rebuild all except eurusd")
        return

    # Ask for confirmation
    print(f"\nWill create targets tables for: {', '.join(pairs_to_process)}")

    # Process pairs (can run in parallel, but sequential is safer for BigQuery)
    results = []
    start_time = time.time()

    for i, pair in enumerate(pairs_to_process, 1):
        print(f"\n[{i}/{len(pairs_to_process)}] Processing {pair}...")
        result = create_targets_table(pair)
        results.append(result)

        if result["status"] == "SUCCESS":
            print(f"    SUCCESS: {result['row_count']:,} rows")
        else:
            print(f"    FAILED: {result['error']}")

        # Small delay between pairs to avoid rate limiting
        time.sleep(1)

    # Summary
    elapsed = time.time() - start_time
    successful = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total processed: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Time elapsed: {elapsed:.1f} seconds")

    if failed:
        print("\nFailed pairs:")
        for r in failed:
            print(f"  - {r['pair']}: {r['error']}")

    if successful:
        total_rows = sum(r.get('row_count', 0) for r in successful)
        print(f"\nTotal rows created: {total_rows:,}")


if __name__ == "__main__":
    main()
