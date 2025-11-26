#!/usr/bin/env python3
"""
Create BQX ML V3 feature tables in BigQuery.
"""

import subprocess
import time
from datetime import datetime

GCP_PROJECT = 'bqx-ml'

# Currency pairs - first batch for initial implementation
CURRENCY_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']

# BQX windows
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

def create_table(dataset, table_name, schema):
    """Create a BigQuery table with given schema."""
    full_table = f"{GCP_PROJECT}:{dataset}.{table_name}"
    cmd = f'bq mk --force --table "{full_table}" {schema}'

    print(f"Creating table: {full_table}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  ✅ Created {table_name}")
        return True
    else:
        print(f"  ❌ Failed: {result.stderr[:100]}")
        return False

def main():
    print("="*80)
    print("🏗️  CREATING BQX ML V3 FEATURE TABLES")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)

    tables_created = 0
    tables_failed = 0

    for pair in CURRENCY_PAIRS:
        print(f"\n📊 Creating tables for {pair}...")

        # Create IDX table (indexed values)
        idx_schema = "interval_time:TIMESTAMP,pair:STRING,open_idx:FLOAT64,high_idx:FLOAT64,low_idx:FLOAT64,close_idx:FLOAT64,volume_idx:FLOAT64"
        if create_table('bqx_ml_v3_features', f"{pair.lower()}_idx", idx_schema):
            tables_created += 1
        else:
            tables_failed += 1

        time.sleep(1)

        # Create BQX table (momentum features)
        bqx_columns = ["interval_time:TIMESTAMP", "pair:STRING"]
        for window in BQX_WINDOWS:
            bqx_columns.append(f"bqx_{window}:FLOAT64")
            bqx_columns.append(f"target_{window}:FLOAT64")

        bqx_schema = ",".join(bqx_columns)
        if create_table('bqx_ml_v3_features', f"{pair.lower()}_bqx", bqx_schema):
            tables_created += 1
        else:
            tables_failed += 1

        time.sleep(1)

    # Create model performance tracking table
    perf_schema = "model_id:STRING,pair:STRING,window:INT64,r2_score:FLOAT64,rmse:FLOAT64,directional_accuracy:FLOAT64,created_at:TIMESTAMP"
    if create_table('bqx_ml_v3_models', 'model_performance', perf_schema):
        tables_created += 1
    else:
        tables_failed += 1

    # Create predictions tracking table
    pred_schema = "prediction_id:STRING,pair:STRING,window:INT64,predicted_value:FLOAT64,actual_value:FLOAT64,prediction_time:TIMESTAMP"
    if create_table('bqx_ml_v3_predictions', 'prediction_log', pred_schema):
        tables_created += 1
    else:
        tables_failed += 1

    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"  Tables created: {tables_created}")
    print(f"  Tables failed: {tables_failed}")
    print(f"  Success rate: {(tables_created/(tables_created+tables_failed)*100):.1f}%")

    print("\n✅ Feature tables creation complete!")
    return 0 if tables_failed == 0 else 1

if __name__ == "__main__":
    exit(main())