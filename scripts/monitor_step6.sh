#!/bin/bash
# Step 6 Progress Monitor - Real-time tracking
# Usage: ./scripts/monitor_step6.sh [interval_seconds]

INTERVAL=${1:-5}
TOTAL_PAIRS=28
TABLES_PER_PAIR=462

while true; do
    clear
    echo "=============================================="
    echo "  STEP 6 PROGRESS MONITOR"
    echo "=============================================="

    # Process status
    PID=$(pgrep -f "parallel_feature_testing.py full" | head -1)
    if [ -z "$PID" ]; then
        echo "STATUS: NOT RUNNING"
    else
        CPU=$(ps -p $PID -o %cpu= 2>/dev/null)
        echo "STATUS: Running (PID: $PID, CPU:$CPU%)"
    fi

    # Completed pairs
    COMPLETED=$(ls /tmp/parallel_batch_full_*.json 2>/dev/null | wc -l)
    echo ""
    echo "PAIRS: $COMPLETED / $TOTAL_PAIRS"

    # Current pair
    CURRENT=$(ls -d /tmp/feature_chunks/*/ 2>/dev/null | xargs -I{} basename {} 2>/dev/null | tail -1)
    CHUNKS=$(ls /tmp/feature_chunks/$CURRENT/*.parquet 2>/dev/null | wc -l)
    echo "CURRENT: ${CURRENT:-waiting} ($CHUNKS / $TABLES_PER_PAIR tables)"

    # Progress bar
    PCT=$((CHUNKS * 100 / TABLES_PER_PAIR))
    BAR=$(printf "%${PCT}s" | tr ' ' '#')
    echo "[$BAR$(printf "%$((100-PCT))s" | tr ' ' '-')]"

    # Resources
    echo ""
    echo "MEMORY: $(free -h | awk '/Mem:/{print $3"/"$2}')"
    echo "DISK: $(df -h /tmp | awk 'NR==2{print $4}') free"
    echo "CHUNKS: $(du -sh /tmp/feature_chunks 2>/dev/null | cut -f1)"

    # Completed list
    echo ""
    echo "COMPLETED:"
    ls /tmp/parallel_batch_full_*.json 2>/dev/null | while read f; do
        P=$(basename $f .json | sed 's/parallel_batch_full_//')
        echo "  $P"
    done

    echo ""
    echo "Updated: $(date '+%H:%M:%S') | Refresh: ${INTERVAL}s | Ctrl+C to exit"
    sleep $INTERVAL
done
