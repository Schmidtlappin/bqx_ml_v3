#!/bin/bash
echo "======================================================================"
echo "PHASE 1 VALIDATION - Final Dataset Completeness Check"
echo "======================================================================"
echo ""

PROJECT="bqx-ml"
DATASET="bqx_ml_v3_features"

# Count tables by type
echo "📊 Table Inventory:"
echo ""
LAG_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "^lag_" | grep -v "_raw" | wc -l)
REGIME_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "^regime_" | grep -v "_raw" | wc -l)
CORR_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "^corr_ibkr_" | wc -l)
IDX_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "_idx$" | wc -l)
BQX_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "_bqx$" | wc -l)
TOTAL_COUNT=$(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | wc -l)

echo "  LAG tables:         $LAG_COUNT / 56 expected"
echo "  REGIME tables:      $REGIME_COUNT / 56 expected"
echo "  Correlation tables: $CORR_COUNT / 224 expected"
echo "  IDX tables:         $IDX_COUNT (baseline)"
echo "  BQX tables:         $BQX_COUNT (baseline)"
echo "  Total tables:       $TOTAL_COUNT"
echo ""

# Validate Phase 1 tables
PHASE1_TOTAL=$((LAG_COUNT + REGIME_COUNT + CORR_COUNT))
echo "  Phase 1 tables:     $PHASE1_TOTAL / 336 expected"
echo ""

# Check for any failures
if [ $LAG_COUNT -eq 56 ] && [ $REGIME_COUNT -eq 56 ] && [ $CORR_COUNT -eq 224 ]; then
    echo "✅ Phase 1 Complete: All 336 tables present"
else
    echo "⚠️  Phase 1 Incomplete:"
    [ $LAG_COUNT -lt 56 ] && echo "    Missing $((56 - LAG_COUNT)) LAG tables"
    [ $REGIME_COUNT -lt 56 ] && echo "    Missing $((56 - REGIME_COUNT)) REGIME tables"
    [ $CORR_COUNT -lt 224 ] && echo "    Missing $((224 - CORR_COUNT)) Correlation tables"
fi
echo ""

# Sample data quality check
echo "📈 Data Quality Sample (5 random tables):"
echo ""
for table in $(bq ls --project_id=$PROJECT --max_results=1000 $DATASET | awk '{print $1}' | grep -E "^(lag_|regime_|corr_ibkr_)" | shuf | head -5); do
    ROW_COUNT=$(bq query --project_id=$PROJECT --location=us-central1 --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`$PROJECT.$DATASET.$table\`" | tail -1)
    echo "  $table: $ROW_COUNT rows"
done
echo ""

echo "======================================================================"
