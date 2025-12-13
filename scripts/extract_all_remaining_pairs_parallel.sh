#!/bin/bash
#
# Extract all remaining pairs using Cloud Run Job 1 (bqx-ml-extract) in PARALLEL
# Parallel 4× execution: 4 concurrent Cloud Run executions
#
# Usage: ./scripts/extract_all_remaining_pairs_parallel.sh

set -e

# Remaining pairs (26 total)
ALL_PAIRS=(
    gbpusd usdjpy usdchf usdcad nzdusd
    eurgbp eurjpy eurchf euraud eurcad eurnzd
    gbpjpy gbpchf gbpaud gbpcad gbpnzd
    audjpy audchf audcad audnzd
    nzdjpy nzdchf nzdcad
    cadjpy cadchf chfjpy
)

TOTAL_PAIRS=${#ALL_PAIRS[@]}
CONCURRENCY=4
REGION="us-central1"
LOG_DIR="/home/micha/bqx_ml_v3/logs/extraction"

mkdir -p "${LOG_DIR}"

echo "========================================================================"
echo "CLOUD RUN JOB 1: Parallel 4× Extraction (All Remaining Pairs)"
echo "========================================================================"
echo "Total pairs to process: ${TOTAL_PAIRS}"
echo "Concurrency: ${CONCURRENCY}× (4 simultaneous executions)"
echo "Estimated time: $((TOTAL_PAIRS * 70 / CONCURRENCY / 60)) hours (vs 30 hours sequential)"
echo "Time savings: ~21 hours"
echo "Start time: $(date -u)"
echo "Log directory: ${LOG_DIR}"
echo "========================================================================"
echo ""

# Track success/failure
SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_PAIRS=()
ACTIVE_PIDS=()

# Function to extract a single pair in background
extract_pair() {
    local PAIR=$1
    local PAIR_NUM=$2
    local LOG_FILE="${LOG_DIR}/extract_${PAIR}_$(date +%Y%m%d_%H%M%S).log"

    echo "[${PAIR_NUM}/${TOTAL_PAIRS}] Starting: ${PAIR^^} (PID: $$)" | tee -a "${LOG_FILE}"

    if gcloud run jobs execute bqx-ml-extract \
        --region "${REGION}" \
        --set-env-vars "PAIR=${PAIR}" \
        --wait >> "${LOG_FILE}" 2>&1; then

        echo "[${PAIR_NUM}/${TOTAL_PAIRS}] ✅ SUCCESS: ${PAIR^^}" | tee -a "${LOG_FILE}"

        # Verify checkpoints
        CHECKPOINT_COUNT=$(gsutil ls "gs://bqx-ml-staging/checkpoints/${PAIR}/*.parquet" 2>/dev/null | wc -l)
        echo "[${PAIR_NUM}/${TOTAL_PAIRS}] Checkpoints: ${CHECKPOINT_COUNT}" | tee -a "${LOG_FILE}"

        if [ "${CHECKPOINT_COUNT}" -lt 600 ]; then
            echo "[${PAIR_NUM}/${TOTAL_PAIRS}] ⚠️  WARNING: Only ${CHECKPOINT_COUNT} checkpoints (expected 667)" | tee -a "${LOG_FILE}"
            echo "${PAIR} (incomplete: ${CHECKPOINT_COUNT} files)" >> /tmp/extraction_warnings.txt
        fi

        echo "SUCCESS:${PAIR}" >> /tmp/extraction_results.txt
    else
        echo "[${PAIR_NUM}/${TOTAL_PAIRS}] ❌ FAILED: ${PAIR^^}" | tee -a "${LOG_FILE}"
        echo "FAILED:${PAIR}" >> /tmp/extraction_results.txt
    fi
}

# Initialize results files
> /tmp/extraction_results.txt
> /tmp/extraction_warnings.txt

# Process pairs in batches of CONCURRENCY
for (( i=0; i<${TOTAL_PAIRS}; i+=${CONCURRENCY} )); do
    BATCH_NUM=$(( i / CONCURRENCY + 1 ))
    BATCH_START=$i
    BATCH_END=$(( i + CONCURRENCY ))
    if [ ${BATCH_END} -gt ${TOTAL_PAIRS} ]; then
        BATCH_END=${TOTAL_PAIRS}
    fi

    BATCH_SIZE=$(( BATCH_END - BATCH_START ))

    echo ""
    echo "========================================================================"
    echo "BATCH ${BATCH_NUM}: Processing ${BATCH_SIZE} pairs in parallel"
    echo "========================================================================"
    echo "Start time: $(date -u)"
    echo ""

    # Launch parallel executions for this batch
    ACTIVE_PIDS=()
    for (( j=${BATCH_START}; j<${BATCH_END}; j++ )); do
        PAIR="${ALL_PAIRS[$j]}"
        PAIR_NUM=$(( j + 1 ))

        echo "Launching: ${PAIR^^} (${PAIR_NUM}/${TOTAL_PAIRS})"
        extract_pair "${PAIR}" "${PAIR_NUM}" &
        ACTIVE_PIDS+=($!)
    done

    echo ""
    echo "Waiting for ${BATCH_SIZE} parallel executions to complete..."
    echo "PIDs: ${ACTIVE_PIDS[@]}"
    echo ""

    # Wait for all executions in this batch to complete
    for PID in "${ACTIVE_PIDS[@]}"; do
        wait $PID
    done

    echo ""
    echo "Batch ${BATCH_NUM} complete at $(date -u)"

    # Count results so far
    SUCCESS_COUNT=$(grep -c "^SUCCESS:" /tmp/extraction_results.txt 2>/dev/null || echo "0")
    FAILURE_COUNT=$(grep -c "^FAILED:" /tmp/extraction_results.txt 2>/dev/null || echo "0")
    COMPLETED=$(( SUCCESS_COUNT + FAILURE_COUNT ))

    echo "Progress: ${COMPLETED}/${TOTAL_PAIRS} pairs completed (${SUCCESS_COUNT} success, ${FAILURE_COUNT} failed)"
    echo ""
done

echo ""
echo "========================================================================"
echo "PARALLEL EXTRACTION COMPLETE"
echo "========================================================================"
echo "End time: $(date -u)"
echo "Total pairs processed: ${TOTAL_PAIRS}"
echo "Successful: ${SUCCESS_COUNT}"
echo "Failed: ${FAILURE_COUNT}"
echo ""

if [ ${FAILURE_COUNT} -gt 0 ]; then
    echo "Failed pairs:"
    grep "^FAILED:" /tmp/extraction_results.txt | cut -d: -f2 | while read PAIR; do
        echo "  - ${PAIR}"
    done
    echo ""
fi

WARNING_COUNT=$(wc -l < /tmp/extraction_warnings.txt 2>/dev/null || echo "0")
if [ ${WARNING_COUNT} -gt 0 ]; then
    echo "Warnings (incomplete checkpoints):"
    cat /tmp/extraction_warnings.txt
    echo ""
fi

if [ ${FAILURE_COUNT} -gt 0 ]; then
    echo "❌ ${FAILURE_COUNT} pairs failed - review logs for details"
    exit 1
else
    echo "✅ All ${TOTAL_PAIRS} pairs extracted successfully!"
    exit 0
fi
