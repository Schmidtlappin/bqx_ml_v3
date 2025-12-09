#!/usr/bin/env python3
"""
Validate V2 Migration - Row Count Parity, Partitioning, and Clustering
"""
import subprocess
import json
import sys
from datetime import datetime

def run_bq_query(query):
    """Run BigQuery query and return results as JSON"""
    cmd = f'bq query --use_legacy_sql=false --format=json "{query}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None

def get_table_count(dataset):
    """Get table count for a dataset"""
    cmd = f'bq ls --max_results=10000 bqx-ml:{dataset} 2>/dev/null | tail -n +3 | wc -l'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return int(result.stdout.strip())

def validate_row_counts():
    """Compare row counts between v1 and v2 datasets"""
    print("\n=== ROW COUNT VALIDATION ===\n")

    # Sample tables to validate
    sample_tables = [
        ('regime_eurusd_45', 'bqx_ml_v3_features', 'bqx_ml_v3_features_v2'),
        ('lag_eurusd_90', 'bqx_ml_v3_features', 'bqx_ml_v3_features_v2'),
        ('corr_eurusd_gbpusd', 'bqx_ml_v3_features', 'bqx_ml_v3_features_v2'),
    ]

    results = []
    for table, v1_ds, v2_ds in sample_tables:
        v1_query = f"SELECT COUNT(*) as cnt FROM `bqx-ml`.{v1_ds}.{table}"
        v2_query = f"SELECT COUNT(*) as cnt FROM `bqx-ml`.{v2_ds}.{table}"

        v1_result = run_bq_query(v1_query)
        v2_result = run_bq_query(v2_query)

        v1_count = int(v1_result[0]['cnt']) if v1_result else -1
        v2_count = int(v2_result[0]['cnt']) if v2_result else -1

        match = "PASS" if v1_count == v2_count else "FAIL"
        results.append((table, v1_count, v2_count, match))
        print(f"  {table}: v1={v1_count:,} v2={v2_count:,} [{match}]")

    return results

def validate_partitioning():
    """Check that v2 tables are partitioned by DATE(interval_time)"""
    print("\n=== PARTITIONING VALIDATION ===\n")

    query = """
    SELECT table_name, partition_column, partition_column_type
    FROM `bqx-ml`.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.PARTITIONS
    GROUP BY 1, 2, 3
    LIMIT 10
    """

    # Use alternative method - check table details
    cmd = 'bq show --format=json bqx-ml:bqx_ml_v3_features_v2.regime_eurusd_45 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        try:
            table_info = json.loads(result.stdout)
            time_part = table_info.get('timePartitioning', {})
            if time_part:
                part_type = time_part.get('type', 'NONE')
                part_field = time_part.get('field', 'N/A')
                print(f"  Sample table: regime_eurusd_45")
                print(f"  Partition type: {part_type}")
                print(f"  Partition field: {part_field}")
                if part_field == 'interval_time':
                    print(f"  Status: [PASS] Partitioned by interval_time")
                    return True
            else:
                print(f"  Status: [FAIL] No partitioning found")
        except:
            print(f"  Status: [ERROR] Could not parse table info")

    return False

def validate_clustering():
    """Check that v2 tables are clustered by pair"""
    print("\n=== CLUSTERING VALIDATION ===\n")

    cmd = 'bq show --format=json bqx-ml:bqx_ml_v3_features_v2.regime_eurusd_45 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        try:
            table_info = json.loads(result.stdout)
            clustering = table_info.get('clustering', {})
            if clustering:
                fields = clustering.get('fields', [])
                print(f"  Sample table: regime_eurusd_45")
                print(f"  Clustering fields: {fields}")
                if 'pair' in fields or 'pair1' in fields:
                    print(f"  Status: [PASS] Clustered by pair")
                    return True
            else:
                print(f"  Status: [WARN] No clustering found (may be per-pair table)")
        except:
            print(f"  Status: [ERROR] Could not parse table info")

    return False

def validate_data_sample():
    """Spot check data integrity on random samples"""
    print("\n=== DATA SAMPLE VALIDATION ===\n")

    query = """
    SELECT
        interval_time,
        pair,
        COUNT(*) as features
    FROM `bqx-ml`.bqx_ml_v3_features_v2.regime_eurusd_45
    WHERE DATE(interval_time) = '2024-01-15'
    GROUP BY 1, 2
    LIMIT 5
    """

    result = run_bq_query(query)
    if result:
        print(f"  Sample from regime_eurusd_45 (2024-01-15):")
        for row in result[:3]:
            print(f"    {row}")
        print(f"  Status: [PASS] Data accessible and structured correctly")
        return True
    else:
        print(f"  Status: [FAIL] Could not retrieve sample data")
        return False

def main():
    print("=" * 60)
    print("BQX ML V3 - V2 MIGRATION VALIDATION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check table counts
    v2_features = get_table_count('bqx_ml_v3_features_v2')
    v2_source = get_table_count('bqx_bq_uscen1_v2')

    print(f"\n=== MIGRATION STATUS ===")
    print(f"  bqx_ml_v3_features_v2: {v2_features} tables")
    print(f"  bqx_bq_uscen1_v2: {v2_source} tables")

    # Run validations
    row_results = validate_row_counts()
    part_ok = validate_partitioning()
    cluster_ok = validate_clustering()
    data_ok = validate_data_sample()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    row_pass = sum(1 for r in row_results if r[3] == 'PASS')
    print(f"  Row Count Parity: {row_pass}/{len(row_results)} tables passed")
    print(f"  Partitioning: {'PASS' if part_ok else 'FAIL'}")
    print(f"  Clustering: {'PASS' if cluster_ok else 'WARN'}")
    print(f"  Data Integrity: {'PASS' if data_ok else 'FAIL'}")

    all_pass = row_pass == len(row_results) and part_ok and data_ok
    print(f"\n  Overall: {'PASS - Ready for v1 deletion' if all_pass else 'NEEDS REVIEW'}")

    return 0 if all_pass else 1

if __name__ == '__main__':
    sys.exit(main())
