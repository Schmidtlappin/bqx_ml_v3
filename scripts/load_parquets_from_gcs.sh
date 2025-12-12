#!/bin/bash
# Load all EURUSD parquet files from GCS to BigQuery staging tables
# Optimized parallel loading approach

PAIR="eurusd"
GCS_BUCKET="gs://bqx-ml-staging"
BQ_DATASET="bqx-ml:bqx_ml_v3_staging"

echo "Starting batch load at $(date '+%H:%M:%S')"

# Get list of all parquet files
gsutil ls "${GCS_BUCKET}/${PAIR}/*.parquet" | while read -r gcs_path; do
    # Extract filename without extension
    filename=$(basename "$gcs_path" .parquet)
    table_name="${PAIR}_${filename}"

    # Load parquet to BigQuery table (runs in parallel due to while loop)
    bq load --source_format=PARQUET --replace \
        "${BQ_DATASET}.${table_name}" \
        "$gcs_path" &

    # Limit to 50 parallel jobs at a time to avoid quota issues
    if [[ $(jobs -r -p | wc -l) -ge 50 ]]; then
        wait -n
    fi
done

# Wait for all remaining jobs
wait

echo "Batch load complete at $(date '+%H:%M:%S')"
