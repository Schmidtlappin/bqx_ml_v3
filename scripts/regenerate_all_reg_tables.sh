#!/bin/bash
#
# Regenerate All REG Tables - Phase 0C
# BQX-ML-M005 MANDATE COMPLIANCE
#
# This script regenerates all 84 REG tables with coefficient columns:
#   - 28 reg_bqx_* tables (BQX variant)
#   - 28 reg_idx_* tables (IDX variant)
#   - 28 reg_* tables (other variant)
#
# Expected duration: 2-3 hours
# Expected cost: $5-10 (BigQuery query costs)
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../logs/reg_regeneration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

MAIN_LOG="$LOG_DIR/regeneration.log"

echo "======================================================================" | tee -a "$MAIN_LOG"
echo "REG Table Regeneration - Phase 0C (BQX-ML-M005 Compliance)" | tee -a "$MAIN_LOG"
echo "======================================================================" | tee -a "$MAIN_LOG"
echo "Start time: $(date)" | tee -a "$MAIN_LOG"
echo "Log directory: $LOG_DIR" | tee -a "$MAIN_LOG"
echo "" | tee -a "$MAIN_LOG"

# Track overall stats
TOTAL_TABLES=84
SUCCESS_COUNT=0
FAILED_COUNT=0
declare -a FAILED_TABLES

# Function to run variant and track results
run_variant() {
    local variant=$1
    local variant_name=$2
    local log_file="$LOG_DIR/${variant}_variant.log"

    echo "======================================================================" | tee -a "$MAIN_LOG"
    echo "Processing $variant_name variant (28 tables)..." | tee -a "$MAIN_LOG"
    echo "Log: $log_file" | tee -a "$MAIN_LOG"
    echo "Start: $(date)" | tee -a "$MAIN_LOG"
    echo "" | tee -a "$MAIN_LOG"

    # Run the generator script
    if python3 "$SCRIPT_DIR/generate_reg_tables_with_coefficients.py" "$variant" 2>&1 | tee "$log_file"; then
        # Count successes from log
        local variant_success=$(grep -c "✅ OK:" "$log_file" || echo "0")
        local variant_failed=$(grep -c "❌ FAILED:" "$log_file" || echo "0")

        SUCCESS_COUNT=$((SUCCESS_COUNT + variant_success))
        FAILED_COUNT=$((FAILED_COUNT + variant_failed))

        # Extract failed table names
        if [ "$variant_failed" -gt 0 ]; then
            grep "❌ FAILED:" "$log_file" | awk '{print $3}' | while read table; do
                FAILED_TABLES+=("$table")
            done
        fi

        echo "" | tee -a "$MAIN_LOG"
        echo "$variant_name variant complete:" | tee -a "$MAIN_LOG"
        echo "  Success: $variant_success" | tee -a "$MAIN_LOG"
        echo "  Failed:  $variant_failed" | tee -a "$MAIN_LOG"
        echo "" | tee -a "$MAIN_LOG"
    else
        echo "ERROR: $variant_name variant script failed!" | tee -a "$MAIN_LOG"
        FAILED_COUNT=$((FAILED_COUNT + 28))
        return 1
    fi
}

# Execute all three variants
echo "Starting regeneration of 84 REG tables..." | tee -a "$MAIN_LOG"
echo "" | tee -a "$MAIN_LOG"

# Variant 1: BQX (reg_bqx_*)
run_variant "bqx" "BQX"

# Variant 2: IDX (reg_idx_*)
run_variant "idx" "IDX"

# Variant 3: Other (reg_*)
run_variant "other" "OTHER"

# Final summary
echo "======================================================================" | tee -a "$MAIN_LOG"
echo "REGENERATION COMPLETE" | tee -a "$MAIN_LOG"
echo "======================================================================" | tee -a "$MAIN_LOG"
echo "End time: $(date)" | tee -a "$MAIN_LOG"
echo "" | tee -a "$MAIN_LOG"
echo "Results:" | tee -a "$MAIN_LOG"
echo "  Total tables: $TOTAL_TABLES" | tee -a "$MAIN_LOG"
echo "  Success: $SUCCESS_COUNT" | tee -a "$MAIN_LOG"
echo "  Failed:  $FAILED_COUNT" | tee -a "$MAIN_LOG"
echo "" | tee -a "$MAIN_LOG"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "⚠️  WARNING: $FAILED_COUNT tables failed to regenerate" | tee -a "$MAIN_LOG"
    echo "Check individual variant logs in: $LOG_DIR" | tee -a "$MAIN_LOG"
    exit 1
else
    echo "✅ SUCCESS: All 84 REG tables regenerated successfully!" | tee -a "$MAIN_LOG"
    echo "" | tee -a "$MAIN_LOG"
    echo "Schema verification:" | tee -a "$MAIN_LOG"
    echo "  - All tables should now have 248 columns (was 234)" | tee -a "$MAIN_LOG"
    echo "  - New columns: reg_lin_coef_* and reg_quad_coef_* (14 total)" | tee -a "$MAIN_LOG"
    echo "" | tee -a "$MAIN_LOG"
    echo "Next steps:" | tee -a "$MAIN_LOG"
    echo "  1. Verify schema with: bq show bqx-ml:bqx_ml_v3_features_v2.reg_bqx_eurusd" | tee -a "$MAIN_LOG"
    echo "  2. Proceed to Phase 1: Refactor TRI/COV/VAR scripts" | tee -a "$MAIN_LOG"
    echo "  3. Update intelligence files and catalogues" | tee -a "$MAIN_LOG"
    exit 0
fi
