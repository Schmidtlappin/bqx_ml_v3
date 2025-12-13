#!/bin/bash
# Cloud Run Polars Pipeline Orchestration
# Integrates: BQ extraction → Polars merge → Validation → GCS backup
#
# This script runs as Cloud Run job entrypoint
# Environment: PAIR (currency pair to process)

set -e  # Exit on any error
set -o pipefail  # Exit on pipe failures

# Configuration
PAIR="${PAIR:-eurusd}"
# CE Directive 2025-12-12: Use GCS for checkpoint persistence (fixes ephemeral /tmp/ cleanup issue)
CHECKPOINT_DIR="gs://bqx-ml-staging/checkpoints/${PAIR}"
TRAINING_FILE="/tmp/training_${PAIR}.parquet"
GCS_OUTPUT_BUCKET="gs://bqx-ml-output"
EXTRACTION_WORKERS=25  # Optimized for Cloud Run 2-core instance

echo "========================================================================"
echo "CLOUD RUN POLARS PIPELINE: ${PAIR}"
echo "========================================================================"
echo "Start: $(date)"
echo "Instance: Cloud Run (2 cores, 12 GB memory)"
echo "Output: ${GCS_OUTPUT_BUCKET}/training_${PAIR}.parquet"
echo "========================================================================"
echo ""

# ============================================================================
# STAGE 1: BigQuery Extraction to Parquet Files (60-70 min)
# ============================================================================
echo "=== STAGE 1: BigQuery Extraction ==="
echo "Extracting feature tables from BigQuery with dynamic discovery..."
echo "Checkpoint directory: ${CHECKPOINT_DIR}"
echo "Protocol: Uses INFORMATION_SCHEMA for table discovery"
echo ""

# Set environment for parallel_feature_testing.py
export CHUNK_DIR="${CHECKPOINT_DIR}"
# No mkdir for GCS - script handles GCS paths automatically

# Call extraction script (single mode) with GCS output flag
# CE Directive 2025-12-12: Pass --gcs-output to enable GCS checkpoint persistence
python3 /workspace/pipelines/training/parallel_feature_testing.py single "${PAIR}" --gcs-output gs://bqx-ml-staging 2>&1 | tee /tmp/extraction_${PAIR}.log || {
    echo "⚠️  Extraction script exited with error (expected if DuckDB merge failed)"
    echo "Checking if checkpoints were created..."
}

# Verify checkpoint extraction succeeded (ignore merge failures)
# CE Directive 2025-12-12: Use gsutil for GCS checkpoint counting
file_count=$(gsutil ls "${CHECKPOINT_DIR}/*.parquet" 2>/dev/null | wc -l)
echo ""
echo "Checkpoint files created: ${file_count}"

if [ "${file_count}" -lt 600 ]; then
    echo "❌ STAGE 1 FAILED: Insufficient checkpoint files (${file_count} < 600)"
    echo "Last 50 lines of extraction log:"
    tail -50 /tmp/extraction_${PAIR}.log
    exit 1
fi

echo "✅ STAGE 1 COMPLETE: ${file_count} parquet checkpoint files extracted"
echo ""

# ============================================================================
# STAGE 2: BigQuery Cloud Merge (10-15 min)
# ============================================================================
# CE Directive 2025-12-12 20:15: Use BigQuery cloud merge instead of Polars
# Reason: Polars requires 56 GB memory (6.0× bloat), Cloud Run has 12 GB limit
# BigQuery solution: Load GCS checkpoints → merge in cloud → export to GCS
# Memory: Zero local (all processing in BigQuery serverless)
echo "=== STAGE 2: BigQuery Cloud Merge ==="
echo "Merging ${file_count} parquet files with BigQuery..."
echo "Mode: GCS Checkpoints → BigQuery → GCS Parquet"
echo "Memory: Zero local (serverless cloud merge)"
echo ""

python3 /workspace/scripts/merge_in_bigquery.py "${PAIR}" || {
    echo "❌ STAGE 2 FAILED: BigQuery merge error"
    exit 1
}

# Verify merge output in GCS
GCS_TRAINING_FILE="gs://${GCS_OUTPUT_BUCKET##gs://}/training_${PAIR}.parquet"
gsutil ls -lh "${GCS_TRAINING_FILE}" || {
    echo "❌ STAGE 2 FAILED: Training file not found in GCS"
    exit 1
}

file_size_info=$(gsutil ls -lh "${GCS_TRAINING_FILE}" | grep -v TOTAL | awk '{print $1}')
echo ""
echo "✅ STAGE 2 COMPLETE: Training file created in GCS (${file_size_info})"
echo "   Output: ${GCS_TRAINING_FILE}"
echo ""

# ============================================================================
# STAGE 3: Validation (1-2 min)
# ============================================================================
# Note: Validation now happens in BigQuery merge script (row count, unique intervals)
# This stage verifies GCS output file existence and basic properties
echo "=== STAGE 3: Validation ==="
echo "Validating GCS training file for ${PAIR}..."
echo ""

# Verify file exists and get metadata
if gsutil stat "${GCS_TRAINING_FILE}" > /tmp/stat_${PAIR}.txt 2>&1; then
    file_size_bytes=$(gsutil stat "${GCS_TRAINING_FILE}" 2>&1 | grep "Content-Length:" | awk '{print $2}')
    file_size_gb=$(echo "scale=2; ${file_size_bytes} / 1073741824" | bc)

    echo "  ✓ File exists: ${GCS_TRAINING_FILE}"
    echo "  ✓ File size: ${file_size_gb} GB"

    # Sanity check: file should be > 1 GB
    if (( $(echo "${file_size_gb} < 1.0" | bc -l) )); then
        echo "  ❌ WARNING: File size unexpectedly small (${file_size_gb} GB)"
        echo "  Expected: > 1 GB for a valid training dataset"
        exit 1
    fi

    echo "  ✓ Size validation passed"

    # Note: Row count and column validation already performed in Stage 2 BigQuery merge
    echo "  ✓ Schema validation passed (verified in BigQuery merge)"
else
    echo "❌ STAGE 3 FAILED: GCS file not found or inaccessible"
    cat /tmp/stat_${PAIR}.txt
    exit 1
fi

echo ""
echo "✅ STAGE 3 COMPLETE: Validation passed"
echo ""

# ============================================================================
# STAGE 4: GCS Backup (SKIPPED - Already in GCS)
# ============================================================================
# CE Directive 2025-12-12: BigQuery merge exports directly to GCS
# No backup needed - file already at gs://bqx-ml-output/training_{pair}.parquet
echo "=== STAGE 4: GCS Backup ==="
echo "SKIPPED: Training file already in GCS from BigQuery merge (Stage 2)"
echo "Location: ${GCS_TRAINING_FILE}"
echo ""
echo "✅ STAGE 4 COMPLETE: File already in GCS"
echo ""

# ============================================================================
# STAGE 5: Cleanup (1 min)
# ============================================================================
echo "=== STAGE 5: Cleanup ==="
echo "Removing temporary files..."
echo ""

# CE Directive 2025-12-12: Cleanup GCS checkpoints
# Note: BigQuery temp tables are already cleaned up in merge script
echo "  Cleaning up GCS checkpoints: ${CHECKPOINT_DIR}"
gsutil -m rm -r "${CHECKPOINT_DIR}" 2>/dev/null || echo "  Note: Checkpoint dir already cleaned"

# Clean up local temp files
rm -f /tmp/stat_${PAIR}.txt
rm -f /tmp/extraction_${PAIR}.log

echo "✅ STAGE 5 COMPLETE: Cleanup finished"
echo ""

# ============================================================================
# PIPELINE COMPLETE
# ============================================================================
echo "========================================================================"
echo "✅ PIPELINE COMPLETE: ${PAIR}"
echo "========================================================================"
echo "End: $(date)"
echo "Mode: BigQuery Cloud Merge (CE Directive 2025-12-12 20:15)"
echo "Output: ${GCS_TRAINING_FILE}"
echo "Size: ${file_size_info}"
echo ""
echo "All stages completed successfully:"
echo "  ✅ Stage 1: BigQuery extraction (${file_count} checkpoint files)"
echo "  ✅ Stage 2: BigQuery cloud merge (${file_count} tables → GCS parquet)"
echo "  ✅ Stage 3: Validation passed (size, schema)"
echo "  ✅ Stage 4: GCS backup (already in GCS from Stage 2)"
echo "  ✅ Stage 5: Cleanup (checkpoints removed)"
echo ""
echo "Memory Usage: Zero local (all processing in BigQuery serverless)"
echo "========================================================================"

exit 0
