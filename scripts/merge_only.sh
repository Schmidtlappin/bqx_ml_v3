#!/bin/bash
#
# Cloud Run Job 2: Merge GCS Checkpoints to Training File
#
# CE Directive 2025-12-12 20:20: Bifurcated Architecture
# This job ONLY does merge - no extraction
#
# Input: 667 parquet checkpoint files from GCS (created by Job 1)
# Output: Merged training file in GCS
# Exit: 0 (success) or 1 (failure)

set -e  # Exit on any error
set -o pipefail

# Configuration from environment variables
PAIR="${PAIR:-eurusd}"
CHECKPOINT_BUCKET="${GCS_CHECKPOINT_BUCKET:-gs://bqx-ml-staging}"
OUTPUT_BUCKET="${GCS_OUTPUT_BUCKET:-gs://bqx-ml-output}"
MERGE_METHOD="${MERGE_METHOD:-bigquery}"

CHECKPOINT_DIR="${CHECKPOINT_BUCKET}/checkpoints/${PAIR}"
OUTPUT_FILE="${OUTPUT_BUCKET}/training_${PAIR}.parquet"

echo "========================================================================"
echo "CLOUD RUN JOB 2: Checkpoint Merge"
echo "========================================================================"
echo "Pair: ${PAIR}"
echo "Method: ${MERGE_METHOD}"
echo "Input: ${CHECKPOINT_DIR}"
echo "Output: ${OUTPUT_FILE}"
echo "Start: $(date -u)"
echo "========================================================================"
echo ""

# Verify checkpoints exist
echo "=== Verifying Input Checkpoints ==="
checkpoint_count=$(gsutil ls "${CHECKPOINT_DIR}/*.parquet" 2>/dev/null | wc -l)

echo "Checkpoint files found: ${checkpoint_count}"
echo "Expected: 667 files (666 features + 1 targets)"

if [ "${checkpoint_count}" -lt 600 ]; then
    echo ""
    echo "❌ MERGE FAILED: Insufficient checkpoint files"
    echo "   Found: ${checkpoint_count}"
    echo "   Required: >= 600"
    echo ""
    echo "Job 1 (extraction) may not have completed successfully."
    echo "Run Job 1 first: gcloud run jobs execute bqx-ml-extract --args=${PAIR}"
    exit 1
fi

echo "✅ Checkpoint verification passed (${checkpoint_count} files)"
echo ""

# Execute merge based on method
echo "=== Executing Merge (${MERGE_METHOD}) ==="
echo ""

if [ "${MERGE_METHOD}" = "bigquery" ]; then
    echo "Method: BigQuery Cloud Merge"
    echo "  - Load ${checkpoint_count} GCS checkpoints to BigQuery temp tables"
    echo "  - Execute ${checkpoint_count}-table LEFT JOIN in BigQuery (serverless)"
    echo "  - Export merged result to GCS as parquet"
    echo "  - Cleanup temp tables"
    echo "  - Memory: Zero local (all processing in BigQuery cloud)"
    echo ""

    python3 /workspace/scripts/merge_in_bigquery.py "${PAIR}" || {
        echo "❌ MERGE FAILED: BigQuery merge error"
        exit 1
    }

elif [ "${MERGE_METHOD}" = "polars" ]; then
    echo "Method: Polars Local Merge (HIGH MEMORY)"
    echo "  - Download ${checkpoint_count} checkpoints from GCS to /tmp"
    echo "  - Merge with Polars (requires ~56 GB memory for EURUSD)"
    echo "  - Upload merged result to GCS"
    echo "  - Memory: ~6× file size (may OOM on standard instances)"
    echo ""

    # WARNING: This requires high-memory instance (>64 GB)
    python3 /workspace/scripts/merge_with_polars_safe.py \
        "${PAIR}" \
        "${CHECKPOINT_DIR}" \
        "/tmp/training_${PAIR}.parquet" || {
        echo "❌ MERGE FAILED: Polars merge error (likely OOM)"
        exit 1
    }

    # Upload to GCS
    echo "Uploading merged file to GCS..."
    gsutil cp "/tmp/training_${PAIR}.parquet" "${OUTPUT_FILE}" || {
        echo "❌ UPLOAD FAILED"
        exit 1
    }

    # Cleanup local file
    rm -f "/tmp/training_${PAIR}.parquet"

else
    echo "❌ Unknown merge method: ${MERGE_METHOD}"
    echo "Valid methods: bigquery, polars"
    exit 1
fi

echo ""
echo "=== Verifying Output File ==="

# Verify output file exists in GCS
if gsutil ls -lh "${OUTPUT_FILE}" > /tmp/output_stat.txt 2>&1; then
    file_size=$(grep -v TOTAL /tmp/output_stat.txt | awk '{print $1}')

    echo "✅ Output file created:"
    echo "   Location: ${OUTPUT_FILE}"
    echo "   Size: ${file_size}"
else
    echo "❌ MERGE FAILED: Output file not found in GCS"
    cat /tmp/output_stat.txt
    exit 1
fi

echo ""
echo "✅ MERGE COMPLETE"
echo "========================================================================"
echo "Job 2 Status: SUCCESS"
echo "========================================================================"
echo "Pair: ${PAIR}"
echo "Method: ${MERGE_METHOD}"
echo "Input: ${checkpoint_count} checkpoint files"
echo "Output: ${OUTPUT_FILE} (${file_size})"
echo "End: $(date -u)"
echo "========================================================================"
echo ""
echo "Training file ready for model training!"
echo ""

exit 0
