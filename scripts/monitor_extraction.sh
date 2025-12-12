#!/bin/bash
# Real-time Extraction Monitor for 27-Pair Feature Extraction
# Usage: ./scripts/monitor_extraction.sh [pair]

PAIR="${1:-audusd}"
CHECKPOINT_DIR="/home/micha/bqx_ml_v3/data/features/checkpoints/$PAIR"
LOG_FILE="/tmp/extraction_monitor_$PAIR.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=== EXTRACTION MONITOR: $PAIR ===" | tee "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "Checkpoint Dir: $CHECKPOINT_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Monitor loop
while true; do
    clear
    echo -e "${BLUE}=== EXTRACTION MONITOR: $PAIR ===${NC}"
    echo "Last Updated: $(date)"
    echo ""

    # Check if checkpoint directory exists
    if [ ! -d "$CHECKPOINT_DIR" ]; then
        echo -e "${RED}⏸  Checkpoint directory not yet created${NC}"
        echo "   Waiting for extraction to start..."
        sleep 5
        continue
    fi

    # Count parquet files
    FILE_COUNT=$(find "$CHECKPOINT_DIR" -name "*.parquet" 2>/dev/null | wc -l)
    EXPECTED=668
    PERCENT=$((FILE_COUNT * 100 / EXPECTED))

    # Calculate progress bar
    PROGRESS_WIDTH=50
    FILLED=$((PERCENT * PROGRESS_WIDTH / 100))
    EMPTY=$((PROGRESS_WIDTH - FILLED))

    # Color based on progress
    if [ $FILE_COUNT -eq $EXPECTED ]; then
        COLOR=$GREEN
        STATUS="✅ COMPLETE"
    elif [ $FILE_COUNT -gt 0 ]; then
        COLOR=$YELLOW
        STATUS="🔄 EXTRACTING"
    else
        COLOR=$RED
        STATUS="⏸  STARTING"
    fi

    echo -e "${COLOR}${STATUS}${NC}"
    echo ""
    echo "Progress: $FILE_COUNT / $EXPECTED files ($PERCENT%)"
    printf "["
    printf "%${FILLED}s" | tr ' ' '='
    printf "%${EMPTY}s" | tr ' ' '-'
    printf "]\n"
    echo ""

    # Show disk usage
    if [ -d "$CHECKPOINT_DIR" ]; then
        DIR_SIZE=$(du -sh "$CHECKPOINT_DIR" 2>/dev/null | cut -f1)
        echo "Checkpoint Size: $DIR_SIZE"
    fi

    DISK_AVAIL=$(df -h /home/micha/bqx_ml_v3 | tail -1 | awk '{print $4}')
    echo "Disk Available: $DISK_AVAIL"
    echo ""

    # Show recent activity (last 5 files created)
    echo "Recent Files:"
    find "$CHECKPOINT_DIR" -name "*.parquet" -type f -printf '%T@ %p\n' 2>/dev/null | \
        sort -rn | head -5 | cut -d' ' -f2 | \
        xargs -I{} basename {} | sed 's/^/  - /'
    echo ""

    # Memory usage
    TOTAL_MEM=$(free -h | grep Mem: | awk '{print $2}')
    USED_MEM=$(free -h | grep Mem: | awk '{print $3}')
    AVAIL_MEM=$(free -h | grep Mem: | awk '{print $7}')
    echo "Memory: $USED_MEM / $TOTAL_MEM used ($AVAIL_MEM available)"
    echo ""

    # Check for extraction process
    if pgrep -f "parallel_feature_testing.py single $PAIR" >/dev/null; then
        PID=$(pgrep -f "parallel_feature_testing.py single $PAIR")
        echo -e "${GREEN}Process Running: PID $PID${NC}"
    else
        if [ $FILE_COUNT -eq $EXPECTED ]; then
            echo -e "${GREEN}Extraction Complete${NC}"
            echo ""
            echo "=== COMPLETION SUMMARY ===" | tee -a "$LOG_FILE"
            echo "Pair: $PAIR" | tee -a "$LOG_FILE"
            echo "Files: $FILE_COUNT / $EXPECTED" | tee -a "$LOG_FILE"
            echo "Size: $(du -sh $CHECKPOINT_DIR | cut -f1)" | tee -a "$LOG_FILE"
            echo "Completed: $(date)" | tee -a "$LOG_FILE"
            break
        else
            echo -e "${RED}⚠️  Process Not Running${NC}"
            echo "   Files extracted so far: $FILE_COUNT / $EXPECTED"
        fi
    fi

    echo ""
    echo "Press Ctrl+C to exit monitor (extraction continues in background)"
    echo "Refreshing in 5 seconds..."

    # Log progress
    echo "$(date +%s),$FILE_COUNT,$PERCENT,$DIR_SIZE" >> "$LOG_FILE"

    sleep 5
done

echo ""
echo "Monitor stopped."
