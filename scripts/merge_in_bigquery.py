#!/usr/bin/env python3
"""
Merge staging tables into training tables using BigQuery SQL.

Usage:
    python3 scripts/merge_in_bigquery.py --pair eurusd
    python3 scripts/merge_in_bigquery.py --pair all
"""

import argparse
import sys
from google.cloud import bigquery

# Configuration
PROJECT = "bqx-ml"
STAGING_DATASET = "bqx_ml_v3_staging"
MODELS_DATASET = "bqx_ml_v3_models"

# All 28 currency pairs
ALL_PAIRS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
    "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
    "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
    "audjpy", "audchf", "audcad", "audnzd",
    "nzdjpy", "nzdchf", "nzdcad",
    "cadjpy", "cadchf",
    "chfjpy"
]


def get_staging_tables(client: bigquery.Client, pair: str) -> list:
    """Get list of staging tables for a pair."""
    query = f"""
    SELECT table_name
    FROM `{PROJECT}.{STAGING_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE '{pair}_%'
    ORDER BY table_name
    """
    result = client.query(query).result()
    return [row.table_name for row in result]


def generate_merge_sql(pair: str, table_names: list) -> str:
    """Generate BigQuery SQL to merge all staging tables."""

    # Separate targets from feature tables
    targets_table = f"{pair}_targets"
    feature_tables = [t for t in table_names if t != targets_table]

    if targets_table not in table_names:
        raise ValueError(f"Targets table not found: {targets_table}")

    # Build SQL with explicit column selection to avoid duplicates
    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{MODELS_DATASET}.training_{pair}`
PARTITION BY DATE(interval_time)
CLUSTER BY interval_time
AS
SELECT
    t.*"""

    # Add feature table columns (excluding interval_time to avoid duplicates)
    for i, table in enumerate(feature_tables):
        alias = f"f{i}"
        sql += f""",
    {alias}.* EXCEPT(interval_time)"""

    # FROM clause with targets
    sql += f"""
FROM `{PROJECT}.{STAGING_DATASET}.{targets_table}` t"""

    # LEFT JOINs for each feature table
    for i, table in enumerate(feature_tables):
        alias = f"f{i}"
        sql += f"""
LEFT JOIN `{PROJECT}.{STAGING_DATASET}.{table}` {alias} USING (interval_time)"""

    return sql


def merge_pair(pair: str) -> dict:
    """Execute BigQuery merge for a pair."""
    print(f"\n{'='*60}")
    print(f"Merging {pair.upper()}")
    print(f"{'='*60}")

    client = bigquery.Client(project=PROJECT)

    # Ensure models dataset exists
    dataset_ref = bigquery.Dataset(f"{PROJECT}.{MODELS_DATASET}")
    dataset_ref.location = "us-central1"
    try:
        client.create_dataset(dataset_ref, exists_ok=True)
    except Exception as e:
        print(f"Dataset setup: {e}")

    # Get staging tables
    print(f"  Fetching staging tables...")
    tables = get_staging_tables(client, pair)
    print(f"  Found {len(tables)} staging tables")

    if len(tables) == 0:
        return {"pair": pair, "status": "FAILED", "error": "No staging tables found"}

    # Generate merge SQL
    print(f"  Generating merge SQL...")
    try:
        sql = generate_merge_sql(pair, tables)
    except ValueError as e:
        return {"pair": pair, "status": "FAILED", "error": str(e)}

    # Execute merge
    print(f"  Executing merge query...")
    print(f"    Target: {MODELS_DATASET}.training_{pair}")

    try:
        job = client.query(sql)
        result = job.result()  # Wait for completion

        # Get stats
        bytes_processed = job.total_bytes_processed or 0
        bytes_billed = job.total_bytes_billed or 0

        print(f"  Merge complete!")
        print(f"    Bytes processed: {bytes_processed / 1e9:.2f} GB")
        print(f"    Bytes billed: {bytes_billed / 1e9:.2f} GB")
        print(f"    Cost: ${bytes_billed / 1e12 * 5:.4f}")

        # Verify result
        verify_query = f"""
        SELECT
            COUNT(*) as rows,
            COUNT(DISTINCT interval_time) as unique_intervals
        FROM `{PROJECT}.{MODELS_DATASET}.training_{pair}`
        """
        verify_result = list(client.query(verify_query).result())[0]

        print(f"  Verification:")
        print(f"    Rows: {verify_result.rows:,}")
        print(f"    Unique intervals: {verify_result.unique_intervals:,}")

        return {
            "pair": pair,
            "status": "SUCCESS",
            "rows": verify_result.rows,
            "tables_merged": len(tables),
            "bytes_processed": bytes_processed,
            "cost": bytes_billed / 1e12 * 5
        }

    except Exception as e:
        print(f"  ERROR: {str(e)[:100]}")
        return {"pair": pair, "status": "FAILED", "error": str(e)[:100]}


def main():
    parser = argparse.ArgumentParser(description="Merge staging tables in BigQuery")
    parser.add_argument("--pair", required=True, help="Currency pair (e.g., eurusd) or 'all'")
    args = parser.parse_args()

    pairs = ALL_PAIRS if args.pair.lower() == "all" else [args.pair.lower()]

    print(f"BigQuery Merge")
    print(f"Project: {PROJECT}")
    print(f"Staging: {STAGING_DATASET}")
    print(f"Output: {MODELS_DATASET}")
    print(f"Pairs: {len(pairs)}")

    all_results = []
    total_cost = 0

    for pair in pairs:
        result = merge_pair(pair)
        all_results.append(result)
        if result["status"] == "SUCCESS":
            total_cost += result.get("cost", 0)

    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    for r in all_results:
        if r["status"] == "SUCCESS":
            print(f"  ✓ {r['pair'].upper()}: {r['rows']:,} rows, {r['tables_merged']} tables, ${r['cost']:.4f}")
        else:
            print(f"  ✗ {r['pair'].upper()}: {r.get('error', 'Unknown error')}")

    print(f"\nTotal estimated cost: ${total_cost:.4f}")

    # Exit with error if any failures
    if any(r["status"] != "SUCCESS" for r in all_results):
        sys.exit(1)


if __name__ == "__main__":
    main()
