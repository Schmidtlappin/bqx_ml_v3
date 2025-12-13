#!/bin/bash
#
# Extract all remaining pairs using Cloud Run Job 1 (bqx-ml-extract)
# Excludes EURUSD and AUDUSD (already have checkpoints in GCS)
#
# Usage: ./scripts/extract_all_remaining_pairs.sh

set -e

# Remaining pairs (26 total)
PAIRS=(
    gbpusd usdjpy usdchf usdcad nzdusd
    eurgbp eurjpy eurchf euraud eurcad eurnzd
    gbpjpy gbpchf gbpaud gbpcad gbpnzd
    audjpy audchf audcad audnzd
    nzdjpy nzdchf nzdcad
    cadjpy cadchf chfjpy
)

TOTAL_PAIRS=${#PAIRS[@]}
REGION="us-central1"
LOG_DIR="/home/micha/bqx_ml_v3/logs/extraction"

mkdir -p "${LOG_DIR}"

echo "========================================================================"
echo "CLOUD RUN JOB 1: Extracting All Remaining Pairs"
echo "========================================================================"
echo "Total pairs to process: ${TOTAL_PAIRS}"
echo "Estimated time: $((TOTAL_PAIRS * 70 / 60)) hours (70 min per pair)"
echo "Start time: $(date -u)"
echo "Log directory: ${LOG_DIR}"
echo "========================================================================"
echo ""

SUCCESS_COUNT=0
FAILURE_COUNT=0
FAILED_PAIRS=()

for i in "${!PAIRS[@]}"; do
    PAIR="${PAIRS[$i]}"
    PAIR_NUM=$((i + 1))

    echo ""
    echo "========================================================================"
    echo "[$PAIR_NUM/$TOTAL_PAIRS] Processing: ${PAIR^^}"
    echo "========================================================================"
    echo "Start time: $(date -u)"

    # Execute Cloud Run Job 1
    LOG_FILE="${LOG_DIR}/extract_${PAIR}_$(date +%Y%m%d_%H%M%S).log"

    if gcloud run jobs execute bqx-ml-extract \
        --region "${REGION}" \
        --args="${PAIR}" \
        --wait 2>&1 | tee "${LOG_FILE}"; then

        echo "✅ SUCCESS: ${PAIR^^}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Verify checkpoints in GCS
        CHECKPOINT_COUNT=$(gsutil ls "gs://bqx-ml-staging/checkpoints/${PAIR}/*.parquet" 2>/dev/null | wc -l)
        echo "Checkpoints created: ${CHECKPOINT_COUNT}"

        if [ "${CHECKPOINT_COUNT}" -lt 600 ]; then
            echo "⚠️  WARNING: Only ${CHECKPOINT_COUNT} checkpoints (expected 667)"
            FAILED_PAIRS+=("${PAIR} (incomplete: ${CHECKPOINT_COUNT} files)")
        fi

    else
        echo "❌ FAILED: ${PAIR^^}"
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        FAILED_PAIRS+=("${PAIR}")
    fi

    echo "End time: $(date -u)"
    echo "Progress: ${PAIR_NUM}/${TOTAL_PAIRS} pairs completed (${SUCCESS_COUNT} success, ${FAILURE_COUNT} failed)"
    echo ""
done

echo ""
echo "========================================================================"
echo "EXTRACTION COMPLETE"
echo "========================================================================"
echo "End time: $(date -u)"
echo "Total pairs processed: ${TOTAL_PAIRS}"
echo "Successful: ${SUCCESS_COUNT}"
echo "Failed: ${FAILURE_COUNT}"
echo ""

if [ ${FAILURE_COUNT} -gt 0 ]; then
    echo "Failed pairs:"
    for FAILED_PAIR in "${FAILED_PAIRS[@]}"; do
        echo "  - ${FAILED_PAIR}"
    done
    echo ""
    exit 1
else
    echo "✅ All ${TOTAL_PAIRS} pairs extracted successfully!"
    exit 0
fi
