#!/bin/bash
# Real-time migration monitor - refreshes every 10 seconds
# Usage: ./monitor_all.sh
# Press Ctrl+C to exit

while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║              BQX ML V3 MIGRATION MONITOR - $(date '+%Y-%m-%d %H:%M:%S')              ║"
    echo "╠══════════════════════════════════════════════════════════════════════════╣"

    # Get current counts
    FEATURES=$(bq ls --max_results=10000 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | grep -c TABLE)
    SOURCE=$(bq ls --max_results=5000 bqx-ml:bqx_bq_uscen1_v2 2>/dev/null | grep -c TABLE)
    COV=$(bq ls --max_results=5000 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | grep "cov_" | wc -l)
    REGIME=$(bq ls --max_results=5000 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | grep "regime_" | wc -l)

    # Calculate percentages
    FEAT_PCT=$(echo "scale=1; $FEATURES * 100 / 4218" | bc)
    SRC_PCT=$(echo "scale=1; $SOURCE * 100 / 2200" | bc)
    COV_PCT=$(echo "scale=1; $COV * 100 / 2352" | bc)
    REG_PCT=$(echo "scale=1; $REGIME * 100 / 112" | bc)

    echo "║                                                                          ║"
    echo "║  DATASET PROGRESS                                                        ║"
    echo "║  ────────────────────────────────────────────────────────────────────    ║"
    printf "║  Features v2:    %5d / 4,218  [%5.1f%%]                                 ║\n" $FEATURES $FEAT_PCT
    printf "║  Source v2:      %5d / 2,200  [%5.1f%%]                                 ║\n" $SOURCE $SRC_PCT
    printf "║  Covariance:     %5d / 2,352  [%5.1f%%]                                 ║\n" $COV $COV_PCT
    printf "║  Regime:         %5d /   112  [%5.1f%%]                                 ║\n" $REGIME $REG_PCT
    echo "║                                                                          ║"
    echo "╠══════════════════════════════════════════════════════════════════════════╣"
    echo "║  ACTIVE PROCESSES                                                        ║"
    echo "║  ────────────────────────────────────────────────────────────────────    ║"

    # Count processes
    PROCS=$(ps aux | grep -E "migrate_" | grep -v grep | wc -l)
    printf "║  Running: %d migration processes                                        ║\n" $PROCS
    echo "║                                                                          ║"
    echo "╠══════════════════════════════════════════════════════════════════════════╣"
    echo "║  COVARIANCE BATCHES (4 parallel)                                         ║"
    echo "║  ────────────────────────────────────────────────────────────────────    ║"

    for i in 1 2 3 4; do
        if [ -f "/tmp/migration_cov_batch$i.log" ]; then
            LAST=$(tail -1 /tmp/migration_cov_batch$i.log 2>/dev/null | head -c 70)
            printf "║  B%d: %-68s ║\n" $i "$LAST"
        fi
    done

    echo "║                                                                          ║"
    echo "╠══════════════════════════════════════════════════════════════════════════╣"
    echo "║  OTHER MIGRATIONS                                                        ║"
    echo "║  ────────────────────────────────────────────────────────────────────    ║"

    # Primary
    if [ -f "/tmp/migration_primary.log" ]; then
        LAST=$(tail -1 /tmp/migration_primary.log 2>/dev/null | head -c 68)
        printf "║  Primary:     %-60s ║\n" "$LAST"
    fi

    # Crossmarket
    if [ -f "/tmp/migration_crossmarket.log" ]; then
        LAST=$(tail -1 /tmp/migration_crossmarket.log 2>/dev/null | head -c 68)
        printf "║  Crossmarket: %-60s ║\n" "$LAST"
    fi

    # Source m1_
    if [ -f "/tmp/migration_source_m1.log" ]; then
        LAST=$(tail -1 /tmp/migration_source_m1.log 2>/dev/null | head -c 68)
        printf "║  Source m1_:  %-60s ║\n" "$LAST"
    fi

    # Source bqx_
    if [ -f "/tmp/migration_source_bqx.log" ]; then
        LAST=$(tail -1 /tmp/migration_source_bqx.log 2>/dev/null | head -c 68)
        printf "║  Source bqx_: %-60s ║\n" "$LAST"
    fi

    # Source reg_
    if [ -f "/tmp/migration_source_reg.log" ]; then
        LAST=$(tail -1 /tmp/migration_source_reg.log 2>/dev/null | head -c 68)
        printf "║  Source reg_: %-60s ║\n" "$LAST"
    fi

    # Regime
    if [ -f "/tmp/migration_regime.log" ]; then
        LAST=$(tail -1 /tmp/migration_regime.log 2>/dev/null | head -c 68)
        printf "║  Regime:      %-60s ║\n" "$LAST"
    fi

    echo "║                                                                          ║"
    echo "╠══════════════════════════════════════════════════════════════════════════╣"
    echo "║  COMPLETED                                                               ║"
    echo "║  ────────────────────────────────────────────────────────────────────    ║"
    echo "║  ✓ Analytics v2: 54/54 (100%)                                            ║"
    echo "║  ✓ tmp_ tables:  28/28 (100%)                                            ║"
    echo "║  ✓ Source idx_:  36/36 (100%)                                            ║"
    echo "║                                                                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Press Ctrl+C to exit. Refreshing every 10 seconds..."

    sleep 10
done
