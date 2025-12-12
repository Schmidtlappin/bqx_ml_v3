#!/usr/bin/env python3
"""
Iterative BigQuery JOIN merge - BA Option 2 Optimized
Loads all parquets from GCS and merges in batches to avoid 668-JOIN limit
"""
import subprocess
import time
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

# Configuration
PAIR = "eurusd"
GCS_BUCKET = "gs://bqx-ml-staging"
PROJECT = "bqx-ml"
STAGING_DATASET = "bqx_ml_v3_staging"
MODELS_DATASET = "bqx_ml_v3_models"
BATCH_SIZE = 50  # JOIN this many tables per iteration

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_parquets_from_gcs():
    """Load all parquet files from GCS to BigQuery staging tables"""
    log(f"Loading parquet files from {GCS_BUCKET}/{PAIR}/")

    # Get list of all parquet files in GCS
    result = subprocess.run(
        [f"gsutil", "ls", f"{GCS_BUCKET}/{PAIR}/*.parquet"],
        capture_output=True,
        text=True
    )

    gcs_files = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    log(f"Found {len(gcs_files)} parquet files in GCS")

    # Load each file as a separate table
    processes = []
    for i, gcs_path in enumerate(gcs_files):
        filename = Path(gcs_path).stem  # Remove .parquet extension
        table_name = f"{PAIR}_{filename}"
        table_id = f"{PROJECT}:{STAGING_DATASET}.{table_name}"

        # Start load job in background
        proc = subprocess.Popen(
            ["bq", "load", "--source_format=PARQUET", "--replace", table_id, gcs_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append((table_name, proc))

        # Limit concurrent jobs to 50
        if len(processes) >= 50:
            # Wait for one to finish
            for name, p in processes:
                p.wait()
            processes = []

        if (i + 1) % 100 == 0:
            log(f"Started {i+1}/{len(gcs_files)} load jobs")

    # Wait for remaining jobs
    for name, p in processes:
        p.wait()

    log(f"All {len(gcs_files)} parquet files loaded to BigQuery")
    return gcs_files

def get_staging_tables():
    """Get list of all staging tables for this pair"""
    client = bigquery.Client(project=PROJECT)
    tables = list(client.list_tables(f"{PROJECT}.{STAGING_DATASET}"))
    pair_tables = [t.table_id for t in tables if t.table_id.startswith(f"{PAIR}_")]
    log(f"Found {len(pair_tables)} staging tables for {PAIR}")
    return sorted(pair_tables)

def iterative_merge(table_names):
    """Merge tables iteratively in batches to avoid JOIN limit"""
    log(f"Starting iterative merge of {len(table_names)} tables")
    log(f"Batch size: {BATCH_SIZE} tables per iteration")

    client = bigquery.Client(project=PROJECT)

    # Separate targets from features
    targets_table = f"{PAIR}_targets"
    if targets_table not in table_names:
        targets_table = f"{PAIR}_tmp_{PAIR}"

    feature_tables = [t for t in table_names if t not in [f"{PAIR}_targets", f"{PAIR}_tmp_{PAIR}"]]
    log(f"Target table: {targets_table}")
    log(f"Feature tables: {len(feature_tables)}")

    # Start with targets
    temp_table = f"{PROJECT}.{STAGING_DATASET}.{PAIR}_temp_merge"
    log(f"Creating initial temp table from {targets_table}")

    query = f"""
    CREATE OR REPLACE TABLE `{temp_table}`
    AS SELECT * FROM `{PROJECT}.{STAGING_DATASET}.{targets_table}`
    """
    client.query(query).result()
    log(f"Initial table created")

    # Iteratively JOIN feature tables in batches
    num_batches = (len(feature_tables) + BATCH_SIZE - 1) // BATCH_SIZE
    log(f"Will process {num_batches} batches of features")

    for batch_idx in range(num_batches):
        start_idx = batch_idx * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(feature_tables))
        batch = feature_tables[start_idx:end_idx]

        log(f"Batch {batch_idx + 1}/{num_batches}: Joining {len(batch)} tables ({start_idx+1}-{end_idx}/{len(feature_tables)})")

        # Build JOIN query for this batch
        join_query = f"SELECT t.*"

        for i, table_name in enumerate(batch):
            join_query += f",\n  f{i}.* EXCEPT(interval_time)"

        join_query += f"\nFROM `{temp_table}` AS t"

        for i, table_name in enumerate(batch):
            join_query += f"\nLEFT JOIN `{PROJECT}.{STAGING_DATASET}.{table_name}` AS f{i} USING (interval_time)"

        # Execute batch JOIN and replace temp table
        batch_start = time.time()
        create_query = f"""
        CREATE OR REPLACE TABLE `{temp_table}`
        AS
        {join_query}
        """

        client.query(create_query).result()
        batch_time = time.time() - batch_start
        log(f"Batch {batch_idx + 1} complete in {batch_time:.1f}s")

    # Create final training table
    final_table = f"{PROJECT}.{MODELS_DATASET}.training_{PAIR}"
    log(f"Creating final training table: {final_table}")

    client.query(f"""
    CREATE OR REPLACE TABLE `{final_table}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY interval_time
    AS SELECT * FROM `{temp_table}`
    """).result()

    # Clean up temp table
    client.delete_table(temp_table)
    log(f"Merge complete! Training table: {final_table}")

    # Get final statistics
    table = client.get_table(final_table)
    log(f"Final table: {table.num_rows:,} rows, {len(table.schema):,} columns, {table.num_bytes / (1024**3):.2f} GB")

    return final_table

def main():
    start_time = time.time()
    log("=" * 60)
    log("ITERATIVE BIGQUERY MERGE - EA OPTIMIZED")
    log("=" * 60)

    # Step 1: Load parquets from GCS (if needed)
    log("\n[STEP 1] Loading parquets from GCS to BigQuery")
    table_names = get_staging_tables()

    if len(table_names) < 600:
        log(f"Only {len(table_names)} tables found, loading from GCS")
        load_parquets_from_gcs()
        table_names = get_staging_tables()
    else:
        log(f"Found {len(table_names)} tables already in staging, skipping load")

    # Step 2: Iterative merge
    log("\n[STEP 2] Executing iterative merge")
    final_table = iterative_merge(table_names)

    total_time = time.time() - start_time
    log(f"\n{'=' * 60}")
    log(f"MERGE COMPLETE IN {total_time / 60:.1f} MINUTES")
    log(f"Training table: {final_table}")
    log(f"{'=' * 60}")

if __name__ == "__main__":
    main()
