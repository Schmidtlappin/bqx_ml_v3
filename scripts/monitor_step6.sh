#!/bin/bash
# Step 6 Progress Monitor - Real-time Worker & Process Tracking
# Usage: ./scripts/monitor_step6.sh [interval_seconds]

INTERVAL=${1:-3}
TOTAL_PAIRS=28
TOTAL_TABLES=669
FEATURES_DIR="/home/micha/bqx_ml_v3/data/features"
LOG_DIR="/home/micha/bqx_ml_v3/logs"
CHECKPOINT_DIR="/home/micha/bqx_ml_v3/data/features/checkpoints"

# Set TERM if not set
export TERM=${TERM:-xterm}

# Start time tracking
START_TIME=$(date +%s)

while true; do
    LOG_FILE=$(ls -t "$LOG_DIR"/step6_*.log 2>/dev/null | head -1)

    clear 2>/dev/null || printf '\033[2J\033[H'

    # Header
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║       STEP 6 FEATURE EXTRACTION - REAL-TIME PROCESS MONITOR             ║"
    echo "║       $(date '+%Y-%m-%d %H:%M:%S')                                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo ""

    # ═══════════════════════════════════════════════════════════════════════════════
    # PROCESS TRACKING
    # ═══════════════════════════════════════════════════════════════════════════════
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 PROCESS TRACKING:"
    echo ""

    # Main process
    MAIN_PID=$(pgrep -f "parallel_feature_testing.py full" 2>/dev/null | head -1)

    if [ -n "$MAIN_PID" ]; then
        MAIN_STATS=$(ps -p "$MAIN_PID" -o pid,state,rss,%mem,%cpu,etime --no-headers 2>/dev/null)
        MAIN_RSS=$(echo "$MAIN_STATS" | awk '{printf "%.1f", $3/1024/1024}')
        MAIN_MEM=$(echo "$MAIN_STATS" | awk '{print $4}')
        MAIN_CPU=$(echo "$MAIN_STATS" | awk '{print $5}')
        MAIN_TIME=$(echo "$MAIN_STATS" | awk '{print $6}')
        MAIN_STATE=$(echo "$MAIN_STATS" | awk '{print $2}')

        echo "   ┌─────────────────────────────────────────────────────────────────────┐"
        printf "   │ %-70s│\n" "MAIN PROCESS (parallel_feature_testing.py)"
        echo "   ├─────────────────────────────────────────────────────────────────────┤"
        printf "   │ PID: %-8s  State: %-4s  CPU: %6s%%  RAM: %5s GB (%s%%)     │\n" "$MAIN_PID" "$MAIN_STATE" "$MAIN_CPU" "$MAIN_RSS" "$MAIN_MEM"
        printf "   │ Runtime: %-60s│\n" "$MAIN_TIME"
        echo "   └─────────────────────────────────────────────────────────────────────┘"
    else
        echo "   ❌ MAIN PROCESS: NOT RUNNING"
    fi

    # Worker processes (Python children)
    echo ""
    WORKER_PIDS=$(pgrep -P "$MAIN_PID" 2>/dev/null)
    WORKER_COUNT=$(echo "$WORKER_PIDS" | grep -c . 2>/dev/null || echo 0)

    if [ "$WORKER_COUNT" -gt 0 ] && [ -n "$WORKER_PIDS" ]; then
        echo "   ┌────────┬───────┬─────────┬─────────┬───────────────────────────────┐"
        echo "   │ WORKER │  PID  │   CPU   │   RAM   │            STATE              │"
        echo "   ├────────┼───────┼─────────┼─────────┼───────────────────────────────┤"

        W_NUM=1
        TOTAL_W_CPU=0
        TOTAL_W_RSS=0

        for wpid in $WORKER_PIDS; do
            if [ -n "$wpid" ]; then
                W_STATS=$(ps -p "$wpid" -o pid,state,rss,%cpu --no-headers 2>/dev/null)
                if [ -n "$W_STATS" ]; then
                    W_PID=$(echo "$W_STATS" | awk '{print $1}')
                    W_STATE=$(echo "$W_STATS" | awk '{print $2}')
                    W_RSS_KB=$(echo "$W_STATS" | awk '{print $3}')
                    W_CPU=$(echo "$W_STATS" | awk '{print $4}')
                    W_RSS_MB=$((W_RSS_KB / 1024))

                    # State description
                    case $W_STATE in
                        R) STATE_DESC="Running" ;;
                        S) STATE_DESC="Sleeping (I/O wait)" ;;
                        D) STATE_DESC="Disk wait" ;;
                        Z) STATE_DESC="Zombie" ;;
                        *) STATE_DESC="$W_STATE" ;;
                    esac

                    printf "   │   %2d   │ %5s │ %6s%% │ %4d MB │ %-29s │\n" "$W_NUM" "$W_PID" "$W_CPU" "$W_RSS_MB" "$STATE_DESC"

                    TOTAL_W_CPU=$(echo "$TOTAL_W_CPU + $W_CPU" | bc 2>/dev/null || echo $TOTAL_W_CPU)
                    TOTAL_W_RSS=$((TOTAL_W_RSS + W_RSS_MB))
                    W_NUM=$((W_NUM + 1))
                fi
            fi
        done

        echo "   ├────────┴───────┼─────────┼─────────┼───────────────────────────────┤"
        printf "   │ TOTAL (%2d)     │ %6.0f%% │ %4d MB │                               │\n" "$((W_NUM-1))" "$TOTAL_W_CPU" "$TOTAL_W_RSS"
        echo "   └────────────────┴─────────┴─────────┴───────────────────────────────┘"
    else
        echo "   Workers: None detected (may be between batches)"
    fi

    # All Python processes
    echo ""
    echo "   ALL PYTHON PROCESSES:"
    echo "   ┌───────┬────────┬─────────┬──────────────────────────────────────────┐"
    echo "   │  PID  │  CPU   │   RAM   │ COMMAND                                  │"
    echo "   ├───────┼────────┼─────────┼──────────────────────────────────────────┤"

    ps aux --sort=-%cpu | grep python | grep -v grep | head -8 | while read -r line; do
        P_PID=$(echo "$line" | awk '{print $2}')
        P_CPU=$(echo "$line" | awk '{print $3}')
        P_RSS_KB=$(echo "$line" | awk '{print $6}')
        P_RSS_MB=$((P_RSS_KB / 1024))
        P_CMD=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}' | cut -c1-40)
        printf "   │ %5s │ %5s%% │ %4d MB │ %-40s │\n" "$P_PID" "$P_CPU" "$P_RSS_MB" "$P_CMD"
    done

    echo "   └───────┴────────┴─────────┴──────────────────────────────────────────┘"

    # ═══════════════════════════════════════════════════════════════════════════════
    # PROGRESS TRACKING
    # ═══════════════════════════════════════════════════════════════════════════════
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 PROGRESS:"

    # Overall progress
    COMPLETED=$(ls "$FEATURES_DIR"/*_merged_features.parquet 2>/dev/null | wc -l)
    PCT=$((COMPLETED * 100 / TOTAL_PAIRS))

    # Progress bar
    FILLED=$((PCT / 5))
    BAR=""
    for i in $(seq 1 $FILLED 2>/dev/null); do BAR="${BAR}█"; done
    for i in $(seq 1 $((20 - FILLED)) 2>/dev/null); do BAR="${BAR}░"; done

    printf "\n   Pairs Complete: %d / %d\n" "$COMPLETED" "$TOTAL_PAIRS"
    echo "   [$BAR] $PCT%"

    # Current pair progress from log
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        CURRENT_PAIR=$(grep "^PAIR" "$LOG_FILE" 2>/dev/null | tail -1 | awk '{print $3}')
        PAIR_NUM=$(grep "^PAIR" "$LOG_FILE" 2>/dev/null | tail -1 | awk '{print $2}' | tr -d ':')

        if [ -n "$CURRENT_PAIR" ]; then
            # Get table progress
            LATEST=$(grep -E "\[.*\/.*\]" "$LOG_FILE" 2>/dev/null | tail -1)
            if [ -n "$LATEST" ]; then
                TABLE_PROGRESS=$(echo "$LATEST" | grep -oE '\[[0-9]+/[0-9]+\]' | head -1)
                TABLE_NAME=$(echo "$LATEST" | grep -oE '\] [a-z_]+:' | sed 's/\] //' | sed 's/://')
                printf "\n   Current: %s (Pair %s) - Table %s\n" "$CURRENT_PAIR" "$PAIR_NUM" "$TABLE_PROGRESS"
                printf "   Table: %s\n" "$TABLE_NAME"
            fi
        fi

        # Checkpoint count for current pair
        if [ -n "$CURRENT_PAIR" ]; then
            PAIR_LOWER=$(echo "$CURRENT_PAIR" | tr '[:upper:]' '[:lower:]')
            CHECKPOINT_COUNT=$(ls "$CHECKPOINT_DIR/$PAIR_LOWER"/*.parquet 2>/dev/null | wc -l)
            printf "   Checkpoints: %d / %d tables cached\n" "$CHECKPOINT_COUNT" "$TOTAL_TABLES"
        fi
    fi

    # ═══════════════════════════════════════════════════════════════════════════════
    # COMPLETED FILES
    # ═══════════════════════════════════════════════════════════════════════════════
    if [ "$COMPLETED" -gt 0 ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ COMPLETED PAIRS:"
        ls -lhS "$FEATURES_DIR"/*_merged_features.parquet 2>/dev/null | head -5 | while read -r line; do
            FNAME=$(basename "$(echo "$line" | awk '{print $NF}')" | sed 's/_merged_features.parquet//' | tr '[:lower:]' '[:upper:]')
            FSIZE=$(echo "$line" | awk '{print $5}')
            printf "   %-8s  %s\n" "$FNAME" "$FSIZE"
        done
        if [ "$COMPLETED" -gt 5 ]; then
            echo "   ... and $((COMPLETED - 5)) more"
        fi
        TOTAL_SIZE=$(du -sh "$FEATURES_DIR" 2>/dev/null | cut -f1)
        echo "   Total size: $TOTAL_SIZE"
    fi

    # ═══════════════════════════════════════════════════════════════════════════════
    # SYSTEM RESOURCES
    # ═══════════════════════════════════════════════════════════════════════════════
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "💾 SYSTEM RESOURCES:"

    # Memory
    MEM_TOTAL=$(free -g | awk '/Mem:/{print $2}')
    MEM_USED=$(free -g | awk '/Mem:/{print $3}')
    MEM_AVAIL=$(free -g | awk '/Mem:/{print $7}')
    MEM_PCT=$((MEM_USED * 100 / MEM_TOTAL))
    printf "   Memory: %dG / %dG used (%dG available) [%d%%]\n" "$MEM_USED" "$MEM_TOTAL" "$MEM_AVAIL" "$MEM_PCT"

    # Disk
    DISK_USED=$(df -h /home/micha | awk 'NR==2{print $3}')
    DISK_TOTAL=$(df -h /home/micha | awk 'NR==2{print $2}')
    DISK_FREE=$(df -h /home/micha | awk 'NR==2{print $4}')
    DISK_PCT=$(df /home/micha | awk 'NR==2{print $5}')
    printf "   Disk:   %s / %s used (%s free) [%s]\n" "$DISK_USED" "$DISK_TOTAL" "$DISK_FREE" "$DISK_PCT"

    # Load
    LOAD=$(cat /proc/loadavg | awk '{printf "%.1f, %.1f, %.1f", $1, $2, $3}')
    CPUS=$(nproc)
    printf "   Load:   %s (on %d CPUs)\n" "$LOAD" "$CPUS"

    # ═══════════════════════════════════════════════════════════════════════════════
    # RECENT ACTIVITY
    # ═══════════════════════════════════════════════════════════════════════════════
    if [ -n "$LOG_FILE" ] && [ -f "$LOG_FILE" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📝 RECENT LOG (last 5 lines):"
        tail -5 "$LOG_FILE" 2>/dev/null | while read -r line; do
            echo "   $line"
        done
    fi

    # ═══════════════════════════════════════════════════════════════════════════════
    # ETA CALCULATION
    # ═══════════════════════════════════════════════════════════════════════════════
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    REMAINING=$((TOTAL_PAIRS - COMPLETED))
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    ELAPSED_MIN=$((ELAPSED / 60))
    ELAPSED_SEC=$((ELAPSED % 60))

    if [ "$COMPLETED" -gt 0 ]; then
        AVG_PER_PAIR=$((ELAPSED / COMPLETED))
        ETA_SEC=$((AVG_PER_PAIR * REMAINING))
        ETA_MIN=$((ETA_SEC / 60))
        printf "⏱️  Monitor running: %dm %ds | Pairs done: %d | Remaining: %d\n" "$ELAPSED_MIN" "$ELAPSED_SEC" "$COMPLETED" "$REMAINING"
        printf "   Avg time/pair: %dm | ETA: ~%dm\n" "$((AVG_PER_PAIR / 60))" "$ETA_MIN"
    else
        printf "⏱️  Monitor running: %dm %ds | Waiting for first pair...\n" "$ELAPSED_MIN" "$ELAPSED_SEC"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Refresh: ${INTERVAL}s | Ctrl+C to exit | Log: $(basename "$LOG_FILE" 2>/dev/null)"

    sleep $INTERVAL
done
