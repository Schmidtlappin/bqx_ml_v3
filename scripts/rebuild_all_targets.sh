#!/bin/bash
# Rebuild all 27 targets tables (excluding eurusd) with correct BQX values
# Must DROP first due to clustering spec change

PROJECT="bqx-ml"
FEATURES_DATASET="bqx_ml_v3_features_v2"
ANALYTICS_DATASET="bqx_ml_v3_analytics_v2"

# All pairs except eurusd (already correct)
PAIRS=(
    gbpusd usdjpy usdchf audusd usdcad nzdusd
    eurgbp eurjpy eurchf euraud eurcad eurnzd
    gbpjpy gbpchf gbpaud gbpcad gbpnzd
    audjpy audchf audcad audnzd
    nzdjpy nzdchf nzdcad
    cadjpy cadchf
    chfjpy
)

BQX_WINDOWS=(45 90 180 360 720 1440 2880)
HORIZONS=(15 30 45 60 75 90 105)

echo "=============================================="
echo "Rebuilding targets tables for ${#PAIRS[@]} pairs"
echo "=============================================="

for pair in "${PAIRS[@]}"; do
    echo ""
    echo "[$pair] Processing..."

    # Build target columns
    TARGET_COLS=""
    for window in "${BQX_WINDOWS[@]}"; do
        for horizon in "${HORIZONS[@]}"; do
            if [ -n "$TARGET_COLS" ]; then
                TARGET_COLS="$TARGET_COLS,"$'\n'"        "
            fi
            TARGET_COLS="${TARGET_COLS}LEAD(bqx_${window}, ${horizon}) OVER (ORDER BY interval_time) as target_bqx${window}_h${horizon}"
        done
    done

    # Generate SQL
    SQL="
CREATE TABLE \`${PROJECT}.${ANALYTICS_DATASET}.targets_${pair}\`
PARTITION BY DATE(interval_time)
CLUSTER BY pair
AS
WITH source AS (
    SELECT
        interval_time,
        pair,
        bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
    FROM \`${PROJECT}.${FEATURES_DATASET}.base_bqx_${pair}\`
    WHERE bqx_45 IS NOT NULL
)
SELECT
    interval_time,
    pair,
    bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
    ${TARGET_COLS}
FROM source
"

    # Drop existing table
    echo "  Dropping old table..."
    bq rm -f "${PROJECT}:${ANALYTICS_DATASET}.targets_${pair}" 2>/dev/null

    # Create new table
    echo "  Creating new table..."
    echo "$SQL" > /tmp/targets_${pair}.sql
    bq query --use_legacy_sql=false --max_rows=0 < /tmp/targets_${pair}.sql

    if [ $? -eq 0 ]; then
        echo "  ✓ SUCCESS"
    else
        echo "  ✗ FAILED"
    fi

    # Small delay to avoid rate limiting
    sleep 2
done

echo ""
echo "=============================================="
echo "COMPLETE - Verifying results..."
echo "=============================================="

# Verify a few pairs
for test_pair in gbpusd usdjpy audusd; do
    echo ""
    echo "Verifying targets_${test_pair}..."
    bq query --use_legacy_sql=false --format=pretty "
    SELECT
        '${test_pair}' as pair,
        AVG(target_bqx45_h15) as avg_target,
        COUNT(*) as rows
    FROM \`${PROJECT}.${ANALYTICS_DATASET}.targets_${test_pair}\`
    WHERE target_bqx45_h15 IS NOT NULL
    "
done
