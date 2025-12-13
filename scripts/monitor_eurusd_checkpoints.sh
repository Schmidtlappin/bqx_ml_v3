#!/bin/bash
# EURUSD Checkpoint Persistence Monitor
# Purpose: Monitor GCS checkpoint count during EURUSD execution (Phase 2)
# Author: Quality Assurance (QA)
# Date: 2025-12-12
# Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a
#
# Usage: ./monitor_eurusd_checkpoints.sh [interval_seconds]
# Default interval: 60 seconds (1 minute)

set -euo pipefail

CHECKPOINT_PATH="gs://bqx-ml-staging/checkpoints/eurusd/"
INTERVAL="${1:-60}"
EXPECTED_COUNT=667

echo "========================================="
echo "EURUSD Checkpoint Persistence Monitor"
echo "========================================="
echo ""
echo "Checkpoint path: $CHECKPOINT_PATH"
echo "Expected count: $EXPECTED_COUNT"
echo "Check interval: ${INTERVAL}s"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

previous_count=0
start_time=$(date +%s)

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    elapsed_min=$((elapsed / 60))

    # Get checkpoint count
    count=$(gsutil ls "$CHECKPOINT_PATH" 2>/dev/null | wc -l || echo "0")

    # Calculate progress
    progress_pct=0
    if [ "$EXPECTED_COUNT" -gt 0 ]; then
        progress_pct=$((count * 100 / EXPECTED_COUNT))
    fi

    # Check for checkpoint disappearance
    if [ "$count" -lt "$previous_count" ]; then
        echo ""
        echo "🚨 ALERT: CHECKPOINT DISAPPEARANCE DETECTED!"
        echo "Previous count: $previous_count"
        echo "Current count: $count"
        echo "Difference: $((previous_count - count))"
        echo ""
    fi

    # Status symbols
    if [ "$count" -eq "$EXPECTED_COUNT" ]; then
        status="✅ COMPLETE"
    elif [ "$count" -gt 0 ]; then
        status="🔄 IN PROGRESS"
    else
        status="⏸️  PENDING"
    fi

    # Print status
    timestamp=$(date '+%Y-%m-%d %H:%M:%S UTC')
    printf "[%s] %s | Checkpoints: %d/%d (%d%%) | Elapsed: %dm\n" \
        "$timestamp" "$status" "$count" "$EXPECTED_COUNT" "$progress_pct" "$elapsed_min"

    # Check if complete
    if [ "$count" -ge "$EXPECTED_COUNT" ]; then
        echo ""
        echo "✅ All $EXPECTED_COUNT checkpoints detected!"
        echo "Elapsed time: ${elapsed_min} minutes"
        break
    fi

    previous_count=$count
    sleep "$INTERVAL"
done

echo ""
echo "Monitoring complete."
