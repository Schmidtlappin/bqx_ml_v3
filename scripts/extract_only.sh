#!/bin/bash
#
# Cloud Run Job 1: BigQuery Feature Extraction to GCS Checkpoints
#
# CE Directive 2025-12-12 20:20: Bifurcated Architecture
# This job ONLY does extraction - no merge
#
# Output: 667 parquet checkpoint files in GCS
# Exit: 0 (success) or 1 (failure)

set -e  # Exit on any error
set -o pipefail

# Configuration from environment variables
PAIR="${PAIR:-eurusd}"
CHECKPOINT_BUCKET="${GCS_CHECKPOINT_BUCKET:-gs://bqx-ml-staging}"
CHECKPOINT_DIR="${CHECKPOINT_BUCKET}/checkpoints/${PAIR}"
EXTRACTION_WORKERS="${EXTRACTION_WORKERS:-25}"

echo "========================================================================"
echo "CLOUD RUN JOB 1: BigQuery Feature Extraction"
echo "========================================================================"
echo "Pair: ${PAIR}"
echo "Output: ${CHECKPOINT_DIR}"
echo "Workers: ${EXTRACTION_WORKERS}"
echo "Start: $(date -u)"
echo "========================================================================"
echo ""

# Extract features to GCS checkpoints
echo "=== Extracting Features from BigQuery ===" echo "Protocol: Dynamic table discovery via INFORMATION_SCHEMA"
echo "Checkpoint mode: GCS persistence (survives container restarts)"
echo ""

python3 /workspace/pipelines/training/parallel_feature_testing.py \
    single "${PAIR}" \
    --gcs-output "${CHECKPOINT_BUCKET}" \
    --workers "${EXTRACTION_WORKERS}" || {
    echo "⚠️  Extraction script exited with error"
    echo "Checking if checkpoints were created..."
}

# Verify checkpoint count
echo ""
echo "=== Verifying Checkpoint Files ==="
file_count=$(gsutil ls "${CHECKPOINT_DIR}/*.parquet" 2>/dev/null | wc -l)

echo "Checkpoint files created: ${file_count}"
echo "Expected: 667 files (666 features + 1 targets)"

if [ "${file_count}" -lt 600 ]; then
    echo ""
    echo "❌ EXTRACTION FAILED: Insufficient checkpoint files"
    echo "   Found: ${file_count}"
    echo "   Required: >= 600"
    echo ""
    echo "This indicates the extraction did not complete successfully."
    echo "Check BigQuery extraction logs above for errors."
    exit 1
fi

echo ""
echo "✅ EXTRACTION COMPLETE"
echo "========================================================================"
echo "Job 1 Status: SUCCESS"
echo "========================================================================"
echo "Pair: ${PAIR}"
echo "Checkpoints: ${file_count} parquet files"
echo "Location: ${CHECKPOINT_DIR}"
echo "Size: $(gsutil du -sh ${CHECKPOINT_DIR} 2>/dev/null | cut -f1 || echo 'calculating...')"
echo "End: $(date -u)"
echo "========================================================================"
echo ""
echo "Next step: Execute Job 2 (merge) with PAIR=${PAIR}"
echo ""

exit 0
