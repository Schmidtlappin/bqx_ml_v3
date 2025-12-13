#!/usr/bin/bash
#
# M008 Phase 4C - LAG Rename Mapping Generator (using bq CLI)
#
# Generates rename mapping for LAG tables using bq CLI commands
#
# Author: BA (Build Agent)
# Date: 2025-12-14

set -e

PROJECT="bqx-ml"
DATASET="bqx_ml_v3_features_v2"
OUTPUT="LAG_RENAME_MAPPING_20251214.csv"

echo "================================================================================"
echo "M008 PHASE 4C - LAG RENAME MAPPING GENERATOR (bq CLI)"
echo "================================================================================"
echo "Project: $PROJECT"
echo "Dataset: $DATASET"
echo "Output: $OUTPUT"
echo "================================================================================"
echo ""

# Step 1: List all LAG tables
echo "[1/3] Querying for LAG tables..."
bq ls --max_results=10000 --format=csv "$PROJECT:$DATASET" | \
    grep "^lag_" | \
    cut -d',' -f1 > /tmp/all_lag_tables.txt

TOTAL_TABLES=$(wc -l < /tmp/all_lag_tables.txt)
echo "Found $TOTAL_TABLES LAG tables"

# Step 2: Filter non-compliant tables (missing variant)
echo ""
echo "[2/3] Filtering non-compliant LAG tables..."
grep -v "lag_idx_" /tmp/all_lag_tables.txt | \
    grep -v "lag_bqx_" > /tmp/noncompliant_lag_tables.txt || true

NON_COMPLIANT=$(wc -l < /tmp/noncompliant_lag_tables.txt)
echo "Non-compliant tables: $NON_COMPLIANT"
echo "Already compliant: $((TOTAL_TABLES - NON_COMPLIANT))"

if [ "$NON_COMPLIANT" -eq 0 ]; then
    echo ""
    echo "✅ All LAG tables are M008-compliant!"
    exit 0
fi

# Step 3: Generate rename mapping
echo ""
echo "[3/3] Generating rename mapping..."
echo "old_name,new_name,window_suffix,assumed_variant" > "$OUTPUT"

while IFS= read -r old_name; do
    # Generate new name: lag_{pair}_{window} → lag_idx_{pair}_{window}
    new_name=$(echo "$old_name" | sed 's/^lag_/lag_idx_/')

    # Extract window suffix (last part)
    window=$(echo "$old_name" | rev | cut -d'_' -f1 | rev)

    echo "$old_name,$new_name,$window,idx" >> "$OUTPUT"
    echo "  $old_name → $new_name (window=$window)"
done < /tmp/noncompliant_lag_tables.txt

echo ""
echo "================================================================================"
echo "COMPLETE"
echo "================================================================================"
echo "Mapping saved: $OUTPUT"
echo "Tables to rename: $NON_COMPLIANT"
echo ""
echo "Next step: Manual review"
echo "  1. Review $OUTPUT"
echo "  2. Verify all mappings are M008-compliant"
echo "  3. Adjust 'idx' to 'bqx' if needed"
echo "  4. Approve for execution Dec 15"
echo "================================================================================"
