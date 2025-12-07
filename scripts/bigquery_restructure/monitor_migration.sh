#!/bin/bash
# Monitor migration progress

echo "=============================================="
echo "MIGRATION PROGRESS - $(date)"
echo "=============================================="

# Count tables
OLD_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) FROM \`bqx-ml.bqx_ml_v3_features.__TABLES__\`" 2>/dev/null | tail -1)
NEW_COUNT=$(bq ls --max_results=10000 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | grep -c TABLE)

echo ""
echo "Tables: $NEW_COUNT / $OLD_COUNT migrated ($(echo "scale=1; $NEW_COUNT * 100 / $OLD_COUNT" | bc)%)"
echo ""

# Check running processes
echo "Running migrations:"
ps aux | grep "migrate_.*tables.py" | grep -v grep | awk '{print "  PID " $2 ": " $11 " " $12}'

echo ""
echo "Latest activity:"
echo "  PRIMARY:     $(tail -1 /tmp/migration_primary_log.txt 2>/dev/null | head -c 70)"
echo "  SECONDARY:   $(tail -1 /tmp/migration_secondary_log.txt 2>/dev/null | head -c 70)"
echo "  CROSSMARKET: $(tail -1 /tmp/migration_crossmarket_log.txt 2>/dev/null | head -c 70)"
echo "  COVARIANCE:  $(tail -1 /tmp/migration_covariance_log.txt 2>/dev/null | head -c 70)"

echo ""
echo "Recent table types migrated:"
bq ls --max_results=20 bqx-ml:bqx_ml_v3_features_v2 2>/dev/null | tail -15 | awk '{print "  " $1}'
