#!/bin/bash
# Real-time V2 Migration Monitor
# Usage: ./monitor_v2_migration.sh

TARGET=5155  # Total expected tables in v2
REFRESH=30   # Seconds between updates

echo "=============================================="
echo "  BQX ML V3 - V2 Migration Real-Time Monitor  "
echo "=============================================="
echo "Target: $TARGET tables"
echo "Refresh: Every ${REFRESH}s"
echo "Press Ctrl+C to exit"
echo ""

while true; do
    # Get current count
    CURRENT=$(bq ls --max_results=10000 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | tail -n +3 | wc -l)
    PCT=$((CURRENT * 100 / TARGET))

    # Get size
    SIZE=$(bq query --use_legacy_sql=false --format=csv --quiet \
        "SELECT ROUND(SUM(size_bytes)/1024/1024/1024, 2) FROM region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE WHERE table_schema='bqx_ml_v3_features_v2'" 2>/dev/null | tail -1)

    # Progress bar
    FILLED=$((PCT / 2))
    EMPTY=$((50 - FILLED))
    BAR=$(printf "%${FILLED}s" | tr ' ' '█')$(printf "%${EMPTY}s" | tr ' ' '░')

    # Check if migration process is running
    if pgrep -f "complete_migration.py" > /dev/null; then
        STATUS="RUNNING"
    else
        STATUS="IDLE"
    fi

    # Display
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║        BQX ML V3 - V2 Migration Monitor                      ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    printf "║  Tables: %5d / %5d (%3d%%)                                ║\n" "$CURRENT" "$TARGET" "$PCT"
    echo "║  [$BAR] ║"
    printf "║  Size: %s GB                                              ║\n" "${SIZE:-N/A}"
    printf "║  Status: %-8s                                           ║\n" "$STATUS"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║  Last update: $(date '+%H:%M:%S')                                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Recent migration activity:"
    tail -5 /tmp/migration_output.log 2>/dev/null || echo "  (waiting for activity...)"
    echo ""
    echo "Press Ctrl+C to exit"

    sleep $REFRESH
done
