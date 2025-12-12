#!/bin/bash
#
# REAL-TIME PIPELINE MONITOR
#
# Displays live status of the autonomous pipeline
#
# Usage: ./monitor_pipeline.sh [interval_seconds]
# Example: ./monitor_pipeline.sh 30  # Update every 30 seconds
#

INTERVAL="${1:-60}"  # Default 60 seconds
STATUS_FILE="/home/micha/bqx_ml_v3/data/.pipeline_status.json"
PROJECT_ROOT="/home/micha/bqx_ml_v3"

clear

while true; do
    clear
    echo "════════════════════════════════════════════════════════════════════════"
    echo "  27-PAIR AUTONOMOUS PIPELINE MONITOR"
    echo "════════════════════════════════════════════════════════════════════════"
    echo "  Updated: $(date +'%Y-%m-%d %H:%M:%S %Z')"
    echo "════════════════════════════════════════════════════════════════════════"
    echo

    # Current status from status file
    if [ -f "$STATUS_FILE" ]; then
        echo "CURRENT PAIR STATUS:"
        echo "────────────────────────────────────────────────────────────────────────"
        cat "$STATUS_FILE" | python3 -m json.tool 2>/dev/null || cat "$STATUS_FILE"
        echo
    fi

    # System resources
    echo "SYSTEM RESOURCES:"
    echo "────────────────────────────────────────────────────────────────────────"
    echo "Memory:"
    free -h | grep -E "Mem|Swap"
    echo
    echo "Disk Space:"
    df -h "$PROJECT_ROOT" | tail -1
    echo

    # Active processes
    echo "ACTIVE PROCESSES:"
    echo "────────────────────────────────────────────────────────────────────────"
    ps aux | grep -E "parallel_feature_testing|merge_single_pair|autonomous_27pair" | grep -v grep | head -5
    echo

    # Checkpoint directories
    echo "CHECKPOINT DIRECTORIES:"
    echo "────────────────────────────────────────────────────────────────────────"
    if [ -d "$PROJECT_ROOT/data/features/checkpoints" ]; then
        for dir in "$PROJECT_ROOT/data/features/checkpoints"/*; do
            if [ -d "$dir" ]; then
                pair=$(basename "$dir")
                count=$(ls -1 "$dir"/*.parquet 2>/dev/null | wc -l)
                size=$(du -sh "$dir" 2>/dev/null | cut -f1)
                echo "  $pair: $count files, $size"
            fi
        done
    else
        echo "  No checkpoint directories"
    fi
    echo

    # Training files
    echo "COMPLETED TRAINING FILES:"
    echo "────────────────────────────────────────────────────────────────────────"
    if ls "$PROJECT_ROOT/data/training"/training_*.parquet 1>/dev/null 2>&1; then
        ls -lh "$PROJECT_ROOT/data/training"/training_*.parquet | awk '{print "  " $9 " - " $5}'
        echo
        echo "  Total: $(ls -1 "$PROJECT_ROOT/data/training"/training_*.parquet 2>/dev/null | wc -l)/28 pairs"
    else
        echo "  No training files yet"
    fi
    echo

    # Latest log entries
    if [ -f "$STATUS_FILE" ]; then
        PIPELINE_LOG=$(grep -o '"pipeline_log": "[^"]*"' "$STATUS_FILE" | cut -d'"' -f4)
        if [ -n "$PIPELINE_LOG" ] && [ -f "$PIPELINE_LOG" ]; then
            echo "LATEST LOG ENTRIES:"
            echo "────────────────────────────────────────────────────────────────────────"
            tail -10 "$PIPELINE_LOG"
        fi
    fi

    echo
    echo "════════════════════════════════════════════════════════════════════════"
    echo "  Refreshing in $INTERVAL seconds... (Ctrl+C to exit)"
    echo "════════════════════════════════════════════════════════════════════════"

    sleep "$INTERVAL"
done
