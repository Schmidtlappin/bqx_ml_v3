#!/bin/bash
# Step 6 Progress Monitor - 16-Worker Real-time Version
# Usage: ./scripts/monitor_step6.sh [interval_seconds]

INTERVAL=${1:-3}
TOTAL_PAIRS=28
FEATURES_DIR="/home/micha/bqx_ml_v3/data/features"
LOG_DIR="/home/micha/bqx_ml_v3/logs"

# Set TERM if not set
export TERM=${TERM:-xterm}

# Start time tracking
START_TIME=$(date +%s)

while true; do
    LOG_FILE=$(ls -t "$LOG_DIR"/step6_*.log 2>/dev/null | head -1)

    clear 2>/dev/null || printf '\033[2J\033[H'

    # Header
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║     STEP 6 FEATURE EXTRACTION - 16-WORKER PARALLEL MONITOR      ║"
    echo "║     $(date '+%Y-%m-%d %H:%M:%S')                                         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # Worker status
    WORKER_PIDS=$(pgrep -f "parallel_feature_testing.py full" 2>/dev/null)
    WORKER_COUNT=$(echo "$WORKER_PIDS" | grep -c . 2>/dev/null || echo 0)

    if [ "$WORKER_COUNT" -eq 0 ]; then
        echo "❌ STATUS: NOT RUNNING"
        echo ""
    else
        # Aggregate stats
        TOTAL_CPU=$(ps aux | grep "parallel_feature_testing.py full" | grep -v grep | awk '{sum+=$3} END {printf "%.0f", sum}')
        TOTAL_RSS=$(ps aux | grep "parallel_feature_testing.py full" | grep -v grep | awk '{sum+=$6} END {printf "%.1f", sum/1024/1024}')

        echo "✅ STATUS: RUNNING"
        printf "   Workers: %d | CPU: %s%% | RAM: %s GB\n" "$WORKER_COUNT" "$TOTAL_CPU" "$TOTAL_RSS"
    fi

    # Overall progress
    COMPLETED=$(ls "$FEATURES_DIR"/*.parquet 2>/dev/null | wc -l)
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "📊 OVERALL: %d / %d pairs complete\n" "$COMPLETED" "$TOTAL_PAIRS"

    # Progress bar
    PCT=$((COMPLETED * 100 / TOTAL_PAIRS))
    FILLED=$((PCT / 5))
    BAR=""
    for i in $(seq 1 $FILLED 2>/dev/null); do BAR="${BAR}█"; done
    for i in $(seq 1 $((20 - FILLED)) 2>/dev/null); do BAR="${BAR}░"; done
    echo "   [$BAR] $PCT%"

    # Real-time per-pair progress from log
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔄 ACTIVE PAIRS (real-time table progress):"
        echo "   ┌─────────┬────────────┬──────────┬────────────┐"
        echo "   │  PAIR   │  PROGRESS  │  TABLES  │   STATUS   │"
        echo "   ├─────────┼────────────┼──────────┼────────────┤"

        # Get all started pairs
        STARTED=$(grep "^Processing " "$LOG_FILE" 2>/dev/null | sed 's/Processing //' | tr -d '=' | tr -d ' ' | sort -u)

        for pair in $STARTED; do
            pair_lower=$(echo "$pair" | tr '[:upper:]' '[:lower:]')
            pair_upper=$(echo "$pair" | tr '[:lower:]' '[:upper:]')

            # Check if completed (parquet file exists)
            if [ -f "$FEATURES_DIR/${pair_lower}_merged_features.parquet" ]; then
                STATUS="✅ DONE"
                PROGRESS="100%"
                TABLES="462/462"
            else
                # Get latest table progress for this pair
                LATEST_TABLE=$(grep -E "\[.*\/.*\].*${pair_lower}" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oE '\[[^]]+\]' | head -1)
                if [ -n "$LATEST_TABLE" ]; then
                    # Extract numbers from [X/Y]
                    CURRENT=$(echo "$LATEST_TABLE" | grep -oE '[0-9]+' | head -1)
                    TOTAL=$(echo "$LATEST_TABLE" | grep -oE '[0-9]+' | tail -1)
                    if [ -n "$CURRENT" ] && [ -n "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
                        PAIR_PCT=$((CURRENT * 100 / TOTAL))
                        PROGRESS="${PAIR_PCT}%"
                        TABLES="${CURRENT}/${TOTAL}"
                    else
                        PROGRESS="..."
                        TABLES="..."
                    fi
                    STATUS="⏳ RUNNING"
                else
                    PROGRESS="0%"
                    TABLES="0/462"
                    STATUS="🚀 STARTING"
                fi
            fi

            printf "   │ %-7s │ %10s │ %8s │ %-10s │\n" "$pair_upper" "$PROGRESS" "$TABLES" "$STATUS"
        done

        echo "   └─────────┴────────────┴──────────┴────────────┘"
    fi

    # Completed files
    if [ "$COMPLETED" -gt 0 ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ COMPLETED FILES:"
        ls -lhS "$FEATURES_DIR"/*.parquet 2>/dev/null | head -6 | awk '{printf "   %s (%s)\n", $NF, $5}'
        if [ "$COMPLETED" -gt 6 ]; then
            echo "   ... and $((COMPLETED - 6)) more"
        fi
        TOTAL_SIZE=$(du -sh "$FEATURES_DIR" 2>/dev/null | cut -f1)
        echo "   Total: $TOTAL_SIZE"
    fi

    # System resources
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💾 SYSTEM:"
    MEM=$(free -h | awk '/Mem:/{printf "%s/%s (%s avail)", $3, $2, $7}')
    DISK=$(df -h /home/micha | awk 'NR==2{printf "%s/%s (%s free)", $3, $2, $4}')
    LOAD=$(cat /proc/loadavg | awk '{printf "%.1f, %.1f, %.1f", $1, $2, $3}')
    echo "   Memory: $MEM"
    echo "   Disk:   $DISK"
    echo "   Load:   $LOAD"

    # Recent activity (last few table completions)
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📝 RECENT ACTIVITY:"
        grep -E "\[.*\/.*\].*cols|Saved:|COMPLETE" "$LOG_FILE" 2>/dev/null | tail -5
    fi

    # ETA
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    REMAINING=$((TOTAL_PAIRS - COMPLETED))
    if [ "$COMPLETED" -gt 0 ]; then
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        ELAPSED_MIN=$((ELAPSED / 60))
        AVG_PER_PAIR=$((ELAPSED / COMPLETED))
        ETA_SEC=$((AVG_PER_PAIR * REMAINING))
        ETA_MIN=$((ETA_SEC / 60))
        printf "⏱️  Elapsed: %d min | ETA: ~%d min for %d remaining pairs\n" "$ELAPSED_MIN" "$ETA_MIN" "$REMAINING"
    else
        echo "⏱️  ETA: ~2.5 hours (16 workers × 28 pairs)"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Refresh: ${INTERVAL}s | Ctrl+C to exit"
    sleep $INTERVAL
done
