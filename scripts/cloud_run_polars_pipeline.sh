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
CHECKPOINT_DIR="/tmp/checkpoints/${PAIR}"
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
mkdir -p "${CHECKPOINT_DIR}"

# Call extraction script (single mode) - will extract checkpoints
# Note: Script may attempt DuckDB merge which could fail - we ignore that and use Polars
python3 /workspace/scripts/parallel_feature_testing.py single "${PAIR}" 2>&1 | tee /tmp/extraction_${PAIR}.log || {
    echo "⚠️  Extraction script exited with error (expected if DuckDB merge failed)"
    echo "Checking if checkpoints were created..."
}

# Verify checkpoint extraction succeeded (ignore merge failures)
file_count=$(find "${CHECKPOINT_DIR}" -name "*.parquet" 2>/dev/null | wc -l)
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
# STAGE 2: Safe Polars Merge (13-20 min)
# ============================================================================
echo "=== STAGE 2: Safe Polars Merge ==="
echo "Merging ${file_count} parquet files with Polars..."
echo "Memory monitoring: Enabled (soft limits)"
echo "Output: ${TRAINING_FILE}"
echo ""

python3 /workspace/scripts/merge_with_polars_safe.py "${PAIR}" "${CHECKPOINT_DIR}" "${TRAINING_FILE}" || {
    echo "❌ STAGE 2 FAILED: Polars merge error"
    exit 1
}

# Verify merge output
if [ ! -f "${TRAINING_FILE}" ]; then
    echo "❌ STAGE 2 FAILED: Training file not created"
    exit 1
fi

file_size_gb=$(du -h "${TRAINING_FILE}" | cut -f1)
echo ""
echo "✅ STAGE 2 COMPLETE: Training file created (${file_size_gb})"
echo ""

# ============================================================================
# STAGE 3: Validation (1-2 min)
# ============================================================================
echo "=== STAGE 3: Validation ==="
echo "Validating training file for ${PAIR}..."
echo ""

python3 /workspace/scripts/validate_training_file.py \
    "${TRAINING_FILE}" \
    --pair "${PAIR}" \
    --required-targets 7 \
    --min-rows 100000 \
    --min-columns 10000 || {
    echo "❌ STAGE 3 FAILED: Validation error"
    exit 1
}

echo ""
echo "✅ STAGE 3 COMPLETE: Validation passed"
echo ""

# ============================================================================
# STAGE 4: Backup to GCS (2-3 min)
# ============================================================================
echo "=== STAGE 4: Backup to GCS ==="
echo "Uploading training file to ${GCS_OUTPUT_BUCKET}..."
echo ""

gsutil cp "${TRAINING_FILE}" "${GCS_OUTPUT_BUCKET}/training_${PAIR}.parquet" || {
    echo "❌ STAGE 4 FAILED: GCS upload error"
    exit 1
}

# Verify upload
gsutil ls -lh "${GCS_OUTPUT_BUCKET}/training_${PAIR}.parquet" || {
    echo "❌ STAGE 4 FAILED: File not found in GCS"
    exit 1
}

echo ""
echo "✅ STAGE 4 COMPLETE: File uploaded to GCS"
echo ""

# ============================================================================
# STAGE 5: Cleanup (1 min)
# ============================================================================
echo "=== STAGE 5: Cleanup ==="
echo "Removing temporary files..."
echo ""

rm -rf "${CHECKPOINT_DIR}"
rm -f "${TRAINING_FILE}"

echo "✅ STAGE 5 COMPLETE: Cleanup finished"
echo ""

# ============================================================================
# PIPELINE COMPLETE
# ============================================================================
echo "========================================================================"
echo "✅ PIPELINE COMPLETE: ${PAIR}"
echo "========================================================================"
echo "End: $(date)"
echo "Output: ${GCS_OUTPUT_BUCKET}/training_${PAIR}.parquet"
echo "Size: ${file_size_gb}"
echo ""
echo "All stages completed successfully:"
echo "  ✅ Stage 1: BigQuery extraction (${file_count} files)"
echo "  ✅ Stage 2: Polars merge (${file_size_gb})"
echo "  ✅ Stage 3: Validation passed"
echo "  ✅ Stage 4: Backup to GCS"
echo "  ✅ Stage 5: Cleanup"
echo "========================================================================"

exit 0
