#!/bin/bash
echo "=== BigQuery Datasets in Project bqx-ml ==="
for ds in bqx_bq bqx_bq_uscen1 bqx_ml_v3_analytics bqx_ml_v3_features bqx_ml_v3_models bqx_ml_v3_predictions bqx_ml_v3_staging; do
  location=$(bq show --format=prettyjson bqx-ml:$ds 2>/dev/null | grep '"location"' | cut -d'"' -f4)
  tables=$(bq ls bqx-ml:$ds 2>/dev/null | awk 'NR>2' | wc -l)
  if [ -n "$location" ]; then
    echo "  $ds: $location ($tables tables)"
  fi
done
