#!/usr/bin/env python3
"""
Merge staging tables into training tables using BigQuery SQL.

Usage:
    # Original mode (staging tables in BigQuery):
    python3 scripts/merge_in_bigquery.py --pair eurusd
    python3 scripts/merge_in_bigquery.py --pair all

    # Cloud Run mode (GCS checkpoints):
    python3 scripts/merge_in_bigquery.py eurusd
    python3 scripts/merge_in_bigquery.py eurusd --gcs-checkpoints
"""

import argparse
import sys
from google.cloud import bigquery
from google.cloud import storage

# Configuration
PROJECT = "bqx-ml"
STAGING_DATASET = "bqx_ml_v3_staging"
MODELS_DATASET = "bqx_ml_v3_models"
TEMP_DATASET = "bqx_ml_v3_temp"
GCS_CHECKPOINT_BUCKET = "bqx-ml-staging"
GCS_OUTPUT_BUCKET = "bqx-ml-output"

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


def list_gcs_checkpoint_files(pair: str) -> list:
    """List all checkpoint parquet files in GCS for a pair."""
    storage_client = storage.Client(project=PROJECT)
    bucket = storage_client.bucket(GCS_CHECKPOINT_BUCKET)

    prefix = f"checkpoints/{pair}/"
    blobs = bucket.list_blobs(prefix=prefix)

    parquet_files = [
        f"gs://{GCS_CHECKPOINT_BUCKET}/{blob.name}"
        for blob in blobs
        if blob.name.endswith('.parquet')
    ]

    return sorted(parquet_files)


def load_gcs_checkpoints_to_temp_tables(client: bigquery.Client, pair: str) -> dict:
    """
    Load GCS checkpoint parquet files into BigQuery temp tables.

    Returns dict with 'targets_table' and 'feature_tables' keys.
    """
    print(f"  Loading GCS checkpoints from gs://{GCS_CHECKPOINT_BUCKET}/checkpoints/{pair}/...")

    # Ensure temp dataset exists
    dataset_ref = bigquery.Dataset(f"{PROJECT}.{TEMP_DATASET}")
    dataset_ref.location = "us-central1"
    try:
        client.create_dataset(dataset_ref, exists_ok=True)
    except Exception:
        pass  # Dataset already exists

    # List checkpoint files
    checkpoint_files = list_gcs_checkpoint_files(pair)
    print(f"  Found {len(checkpoint_files)} checkpoint files")

    if len(checkpoint_files) == 0:
        raise ValueError(f"No checkpoint files found for {pair}")

    # Separate targets from features
    targets_file = None
    feature_files = []

    for gcs_uri in checkpoint_files:
        filename = gcs_uri.split('/')[-1]
        if filename == 'targets.parquet':
            targets_file = gcs_uri
        elif filename != '_COMPLETE':
            feature_files.append(gcs_uri)

    if not targets_file:
        raise ValueError(f"targets.parquet not found in checkpoints")

    print(f"  Loading targets + {len(feature_files)} feature files to temp tables...")

    # Load targets
    targets_table_id = f"{PROJECT}.{TEMP_DATASET}.{pair}_targets_temp"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    load_job = client.load_table_from_uri(
        targets_file,
        targets_table_id,
        job_config=job_config
    )
    load_job.result()  # Wait for completion
    print(f"    ✓ Loaded targets ({load_job.output_rows:,} rows)")

    # Load feature files
    feature_table_ids = []
    for i, gcs_uri in enumerate(feature_files, 1):
        filename = gcs_uri.split('/')[-1].replace('.parquet', '')
        table_id = f"{PROJECT}.{TEMP_DATASET}.{pair}_{filename}_temp"

        load_job = client.load_table_from_uri(
            gcs_uri,
            table_id,
            job_config=job_config
        )
        load_job.result()
        feature_table_ids.append(table_id)

        if i % 100 == 0 or i == len(feature_files):
            print(f"    Progress: {i}/{len(feature_files)} feature tables loaded")

    print(f"  ✓ All {len(checkpoint_files)} checkpoints loaded to {TEMP_DATASET}")

    return {
        "targets_table": targets_table_id,
        "feature_tables": feature_table_ids
    }


def generate_merge_sql_from_temp_tables(pair: str, targets_table: str, feature_tables: list) -> str:
    """Generate BigQuery SQL to merge temp tables (loaded from GCS checkpoints)."""

    # Build SQL - create result in temp dataset
    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{TEMP_DATASET}.training_{pair}_merged`
AS
SELECT
    t.*"""

    # Add feature table columns (excluding interval_time to avoid duplicates)
    for i, table_id in enumerate(feature_tables):
        alias = f"f{i}"
        sql += f""",
    {alias}.* EXCEPT(interval_time)"""

    # FROM clause with targets
    sql += f"""
FROM `{targets_table}` t"""

    # LEFT JOINs for each feature table
    for i, table_id in enumerate(feature_tables):
        alias = f"f{i}"
        sql += f"""
LEFT JOIN `{table_id}` {alias} USING (interval_time)"""

    return sql


def export_table_to_gcs_parquet(client: bigquery.Client, pair: str, table_id: str) -> dict:
    """Export BigQuery table to GCS as parquet."""
    destination_uri = f"gs://{GCS_OUTPUT_BUCKET}/training_{pair}.parquet"

    print(f"  Exporting merged table to {destination_uri}...")

    job_config = bigquery.ExtractJobConfig(
        destination_format=bigquery.DestinationFormat.PARQUET,
    )

    extract_job = client.extract_table(
        table_id,
        destination_uri,
        job_config=job_config
    )
    extract_job.result()  # Wait for completion

    print(f"  ✓ Export complete: {destination_uri}")

    return {"gcs_uri": destination_uri}


def cleanup_temp_tables(client: bigquery.Client, pair: str):
    """Delete all temp tables for a pair."""
    print(f"  Cleaning up temp tables...")

    # List all temp tables for this pair
    query = f"""
    SELECT table_name
    FROM `{PROJECT}.{TEMP_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE '{pair}_%'
    """

    tables = [row.table_name for row in client.query(query).result()]

    for table_name in tables:
        table_id = f"{PROJECT}.{TEMP_DATASET}.{table_name}"
        client.delete_table(table_id, not_found_ok=True)

    print(f"  ✓ Deleted {len(tables)} temp tables")


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


def merge_pair_from_gcs_checkpoints(pair: str) -> dict:
    """
    Execute BigQuery merge from GCS checkpoints (Cloud Run mode).

    CE Directive 2025-12-12: Load GCS checkpoints to BigQuery, merge in cloud,
    export to GCS parquet. Zero local memory usage.
    """
    print(f"\n{'='*70}")
    print(f"BigQuery Cloud Merge: {pair.upper()}")
    print(f"{'='*70}")
    print(f"Mode: GCS Checkpoints → BigQuery Merge → GCS Parquet")
    print(f"Memory: Zero local (all processing in BigQuery cloud)")

    client = bigquery.Client(project=PROJECT)

    try:
        # Step 1: Load GCS checkpoints to temp tables
        print(f"\n[1/4] Loading GCS checkpoints to BigQuery temp tables...")
        tables = load_gcs_checkpoints_to_temp_tables(client, pair)
        targets_table = tables["targets_table"]
        feature_tables = tables["feature_tables"]
        total_tables = len(feature_tables) + 1

        # Step 2: Generate and execute merge SQL
        print(f"\n[2/4] Executing {total_tables}-table LEFT JOIN in BigQuery...")
        sql = generate_merge_sql_from_temp_tables(pair, targets_table, feature_tables)

        job = client.query(sql)
        result = job.result()  # Wait for completion

        # Get merge stats
        bytes_processed = job.total_bytes_processed or 0
        bytes_billed = job.total_bytes_billed or 0
        cost = bytes_billed / 1e12 * 5

        print(f"  ✓ Merge complete!")
        print(f"    Tables merged: {total_tables}")
        print(f"    Bytes processed: {bytes_processed / 1e9:.2f} GB")
        print(f"    Bytes billed: {bytes_billed / 1e9:.2f} GB")
        print(f"    Cost: ${cost:.4f}")

        # Verify merged table
        merged_table_id = f"{PROJECT}.{TEMP_DATASET}.training_{pair}_merged"
        verify_query = f"""
        SELECT
            COUNT(*) as rows,
            COUNT(DISTINCT interval_time) as unique_intervals
        FROM `{merged_table_id}`
        """
        verify_result = list(client.query(verify_query).result())[0]
        print(f"  Verification:")
        print(f"    Rows: {verify_result.rows:,}")
        print(f"    Unique intervals: {verify_result.unique_intervals:,}")

        # Step 3: Export to GCS as parquet
        print(f"\n[3/4] Exporting merged table to GCS...")
        export_result = export_table_to_gcs_parquet(client, pair, merged_table_id)

        # Step 4: Cleanup temp tables
        print(f"\n[4/4] Cleaning up temp tables...")
        cleanup_temp_tables(client, pair)

        print(f"\n{'='*70}")
        print(f"✓ CLOUD MERGE COMPLETE: {pair.upper()}")
        print(f"{'='*70}")
        print(f"Output: {export_result['gcs_uri']}")
        print(f"Rows: {verify_result.rows:,}")
        print(f"Tables merged: {total_tables}")
        print(f"Cost: ${cost:.4f}")
        print(f"{'='*70}\n")

        return {
            "pair": pair,
            "status": "SUCCESS",
            "rows": verify_result.rows,
            "tables_merged": total_tables,
            "bytes_processed": bytes_processed,
            "cost": cost,
            "gcs_uri": export_result['gcs_uri']
        }

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

        # Attempt cleanup even on failure
        try:
            cleanup_temp_tables(client, pair)
        except:
            pass

        return {"pair": pair, "status": "FAILED", "error": str(e)[:200]}


def main():
    parser = argparse.ArgumentParser(description="Merge tables using BigQuery")
    parser.add_argument("pair", nargs="?", help="Currency pair (e.g., eurusd) - positional for Cloud Run compatibility")
    parser.add_argument("--pair", dest="pair_flag", help="Currency pair (e.g., eurusd) or 'all' - legacy flag mode")
    parser.add_argument("--gcs-checkpoints", action="store_true", help="Use GCS checkpoint mode (Cloud Run)")
    args = parser.parse_args()

    # Determine pair (support both positional and --pair flag)
    pair_arg = args.pair or args.pair_flag
    if not pair_arg:
        parser.error("Currency pair required (positional or --pair flag)")

    pairs = ALL_PAIRS if pair_arg.lower() == "all" else [pair_arg.lower()]

    # Determine mode: GCS checkpoints (Cloud Run) or staging tables (VM)
    # Default to GCS mode if positional argument used (Cloud Run calling convention)
    use_gcs_mode = args.gcs_checkpoints or (args.pair and not args.pair_flag)

    if use_gcs_mode:
        print(f"BigQuery Cloud Merge (GCS Checkpoints)")
        print(f"Project: {PROJECT}")
        print(f"Checkpoints: gs://{GCS_CHECKPOINT_BUCKET}/checkpoints/")
        print(f"Output: gs://{GCS_OUTPUT_BUCKET}/")
        print(f"Temp dataset: {TEMP_DATASET}")
        print(f"Pairs: {len(pairs)}")
    else:
        print(f"BigQuery Merge (Staging Tables)")
        print(f"Project: {PROJECT}")
        print(f"Staging: {STAGING_DATASET}")
        print(f"Output: {MODELS_DATASET}")
        print(f"Pairs: {len(pairs)}")

    all_results = []
    total_cost = 0

    for pair in pairs:
        if use_gcs_mode:
            result = merge_pair_from_gcs_checkpoints(pair)
        else:
            result = merge_pair(pair)

        all_results.append(result)
        if result["status"] == "SUCCESS":
            total_cost += result.get("cost", 0)

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    for r in all_results:
        if r["status"] == "SUCCESS":
            if use_gcs_mode:
                print(f"  ✓ {r['pair'].upper()}: {r['rows']:,} rows, {r['tables_merged']} tables, ${r['cost']:.4f}")
                print(f"     Output: {r.get('gcs_uri', 'N/A')}")
            else:
                print(f"  ✓ {r['pair'].upper()}: {r['rows']:,} rows, {r['tables_merged']} tables, ${r['cost']:.4f}")
        else:
            print(f"  ✗ {r['pair'].upper()}: {r.get('error', 'Unknown error')}")

    print(f"\nTotal estimated cost: ${total_cost:.4f}")

    # Exit with error if any failures
    if any(r["status"] != "SUCCESS" for r in all_results):
        sys.exit(1)


if __name__ == "__main__":
    main()
