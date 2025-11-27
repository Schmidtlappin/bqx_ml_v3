#!/usr/bin/env python3
"""
Prepare training dataset with DUAL PROCESSING (IDX + BQX features)
Per Chief Engineer directive 20251127_0010_CE_BA
Implements USER preference for dual feature approach
"""

from google.cloud import bigquery
from typing import Tuple, Dict
from datetime import datetime
import time

def prepare_training_dataset_dual(
    pair: str,
    prediction_window: int,
    project_id: str = "bqx-ml",
    baseline_date: str = "2022-07-01"
) -> Tuple[str, dict]:
    """
    Prepare training dataset with DUAL PROCESSING (IDX + BQX features)

    Args:
        pair: Currency pair (e.g., 'EURUSD')
        prediction_window: Prediction horizon (45, 90, 180, 360, 720, 1440, 2880)
        project_id: GCP project ID
        baseline_date: Starting date for synthetic data

    Returns:
        table_id: BigQuery table containing training data
        stats: Dictionary with dataset statistics
    """

    print(f"\n{'='*60}")
    print(f"DUAL PROCESSING PIPELINE - {pair}-{prediction_window}")
    print(f"Features: 28 (14 IDX + 14 BQX)")
    print(f"{'='*60}")

    client = bigquery.Client(project=project_id)

    # Create destination table name
    output_table = f"{project_id}.bqx_ml_v3_models.{pair.lower()}_{prediction_window}_dual_train"

    # Build the dual processing query
    query = f"""
    WITH feature_engineering AS (
        SELECT
            bqx.interval_time,
            bqx.pair,

            -- IDX features (raw indexed values) - 14 features
            LAG(idx.close_idx, 1) OVER (ORDER BY idx.interval_time) as idx_lag_1,
            LAG(idx.close_idx, 2) OVER (ORDER BY idx.interval_time) as idx_lag_2,
            LAG(idx.close_idx, 3) OVER (ORDER BY idx.interval_time) as idx_lag_3,
            LAG(idx.close_idx, 4) OVER (ORDER BY idx.interval_time) as idx_lag_4,
            LAG(idx.close_idx, 5) OVER (ORDER BY idx.interval_time) as idx_lag_5,
            LAG(idx.close_idx, 6) OVER (ORDER BY idx.interval_time) as idx_lag_6,
            LAG(idx.close_idx, 7) OVER (ORDER BY idx.interval_time) as idx_lag_7,
            LAG(idx.close_idx, 8) OVER (ORDER BY idx.interval_time) as idx_lag_8,
            LAG(idx.close_idx, 9) OVER (ORDER BY idx.interval_time) as idx_lag_9,
            LAG(idx.close_idx, 10) OVER (ORDER BY idx.interval_time) as idx_lag_10,
            LAG(idx.close_idx, 11) OVER (ORDER BY idx.interval_time) as idx_lag_11,
            LAG(idx.close_idx, 12) OVER (ORDER BY idx.interval_time) as idx_lag_12,
            LAG(idx.close_idx, 13) OVER (ORDER BY idx.interval_time) as idx_lag_13,
            LAG(idx.close_idx, 14) OVER (ORDER BY idx.interval_time) as idx_lag_14,

            -- BQX features (momentum percentages) - 14 features
            LAG(bqx.bqx_{prediction_window}, 1) OVER (ORDER BY bqx.interval_time) as bqx_lag_1,
            LAG(bqx.bqx_{prediction_window}, 2) OVER (ORDER BY bqx.interval_time) as bqx_lag_2,
            LAG(bqx.bqx_{prediction_window}, 3) OVER (ORDER BY bqx.interval_time) as bqx_lag_3,
            LAG(bqx.bqx_{prediction_window}, 4) OVER (ORDER BY bqx.interval_time) as bqx_lag_4,
            LAG(bqx.bqx_{prediction_window}, 5) OVER (ORDER BY bqx.interval_time) as bqx_lag_5,
            LAG(bqx.bqx_{prediction_window}, 6) OVER (ORDER BY bqx.interval_time) as bqx_lag_6,
            LAG(bqx.bqx_{prediction_window}, 7) OVER (ORDER BY bqx.interval_time) as bqx_lag_7,
            LAG(bqx.bqx_{prediction_window}, 8) OVER (ORDER BY bqx.interval_time) as bqx_lag_8,
            LAG(bqx.bqx_{prediction_window}, 9) OVER (ORDER BY bqx.interval_time) as bqx_lag_9,
            LAG(bqx.bqx_{prediction_window}, 10) OVER (ORDER BY bqx.interval_time) as bqx_lag_10,
            LAG(bqx.bqx_{prediction_window}, 11) OVER (ORDER BY bqx.interval_time) as bqx_lag_11,
            LAG(bqx.bqx_{prediction_window}, 12) OVER (ORDER BY bqx.interval_time) as bqx_lag_12,
            LAG(bqx.bqx_{prediction_window}, 13) OVER (ORDER BY bqx.interval_time) as bqx_lag_13,
            LAG(bqx.bqx_{prediction_window}, 14) OVER (ORDER BY bqx.interval_time) as bqx_lag_14,

            -- Target remains BQX (momentum percentage)
            bqx.target_{prediction_window} as target,

            -- Row number for splitting
            ROW_NUMBER() OVER (ORDER BY bqx.interval_time) as row_num

        FROM `{project_id}.bqx_ml_v3_features.{pair.lower()}_bqx` bqx
        JOIN `{project_id}.bqx_ml_v3_features.{pair.lower()}_idx` idx
        ON bqx.interval_time = idx.interval_time
        WHERE bqx.bqx_{prediction_window} IS NOT NULL
        AND bqx.target_{prediction_window} IS NOT NULL
        AND idx.close_idx IS NOT NULL
    ),

    labeled_data AS (
        SELECT
            *,
            -- Interval-centric split with temporal isolation
            CASE
                WHEN row_num <= 7000 THEN 'train'
                WHEN row_num > 7100 AND row_num <= 9100 THEN 'validation'  -- 100 interval gap
                WHEN row_num > 9150 THEN 'test'  -- 50 interval gap
                ELSE 'gap'
            END as split
        FROM feature_engineering
    )

    SELECT
        interval_time,
        pair,
        -- All 28 features (14 IDX + 14 BQX)
        idx_lag_1, idx_lag_2, idx_lag_3, idx_lag_4, idx_lag_5,
        idx_lag_6, idx_lag_7, idx_lag_8, idx_lag_9, idx_lag_10,
        idx_lag_11, idx_lag_12, idx_lag_13, idx_lag_14,
        bqx_lag_1, bqx_lag_2, bqx_lag_3, bqx_lag_4, bqx_lag_5,
        bqx_lag_6, bqx_lag_7, bqx_lag_8, bqx_lag_9, bqx_lag_10,
        bqx_lag_11, bqx_lag_12, bqx_lag_13, bqx_lag_14,
        target,
        split
    FROM labeled_data
    WHERE split != 'gap'  -- Exclude temporal isolation gaps
    ORDER BY interval_time
    """

    print("\n📊 Creating dual processing training dataset...")
    print(f"   Destination: {output_table}")

    # Configure query job
    job_config = bigquery.QueryJobConfig(
        destination=output_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    # Execute query
    start_time = time.time()
    query_job = client.query(query, job_config=job_config)

    # Wait for completion
    query_job.result()
    elapsed_time = time.time() - start_time

    # Get statistics
    stats_query = f"""
    SELECT
        COUNT(*) as total_rows,
        COUNT(DISTINCT split) as n_splits,
        COUNT(CASE WHEN split = 'train' THEN 1 END) as train_rows,
        COUNT(CASE WHEN split = 'validation' THEN 1 END) as val_rows,
        COUNT(CASE WHEN split = 'test' THEN 1 END) as test_rows,
        AVG(target) as avg_target,
        STDDEV(target) as stddev_target,
        MIN(target) as min_target,
        MAX(target) as max_target
    FROM `{output_table}`
    """

    stats_result = client.query(stats_query).result()
    stats = list(stats_result)[0]

    # Create comprehensive statistics dictionary
    statistics = {
        "pair": pair,
        "prediction_window": prediction_window,
        "table_id": output_table,
        "creation_time": datetime.now().isoformat(),
        "query_time_seconds": round(elapsed_time, 2),
        "total_rows": stats.total_rows,
        "n_features": 28,  # 14 IDX + 14 BQX
        "feature_types": {
            "idx_features": 14,
            "bqx_features": 14
        },
        "splits": {
            "train": stats.train_rows,
            "validation": stats.val_rows,
            "test": stats.test_rows
        },
        "target_stats": {
            "mean": round(stats.avg_target, 4) if stats.avg_target else 0,
            "stddev": round(stats.stddev_target, 4) if stats.stddev_target else 0,
            "min": round(stats.min_target, 4) if stats.min_target else 0,
            "max": round(stats.max_target, 4) if stats.max_target else 0
        },
        "approach": "dual_processing_idx_bqx"
    }

    print(f"\n✅ Dual processing dataset created successfully!")
    print(f"   Total rows: {statistics['total_rows']:,}")
    print(f"   Features: {statistics['n_features']} (14 IDX + 14 BQX)")
    print(f"   Train: {statistics['splits']['train']:,} rows")
    print(f"   Validation: {statistics['splits']['validation']:,} rows")
    print(f"   Test: {statistics['splits']['test']:,} rows")
    print(f"   Creation time: {statistics['query_time_seconds']} seconds")

    return output_table, statistics


def verify_dual_features(table_id: str, project_id: str = "bqx-ml"):
    """
    Verify that the dual processing table has all 28 features
    """
    client = bigquery.Client(project=project_id)

    # Get table schema
    table_ref = client.get_table(table_id)

    idx_features = [col.name for col in table_ref.schema if col.name.startswith('idx_lag_')]
    bqx_features = [col.name for col in table_ref.schema if col.name.startswith('bqx_lag_')]

    print(f"\n📋 Feature Verification for {table_id}")
    print(f"   IDX features: {len(idx_features)}")
    print(f"   BQX features: {len(bqx_features)}")
    print(f"   Total features: {len(idx_features) + len(bqx_features)}")

    if len(idx_features) == 14 and len(bqx_features) == 14:
        print("   ✅ All 28 features present!")
        return True
    else:
        print("   ❌ Feature count mismatch!")
        return False


if __name__ == "__main__":
    # Test with EURUSD-45 as per CE directive
    pair = "EURUSD"
    window = 45

    print("\n" + "="*60)
    print("IMPLEMENTING DUAL PROCESSING PER USER PREFERENCE")
    print("Directive: 20251127_0010_CE_BA")
    print("="*60)

    try:
        table_id, stats = prepare_training_dataset_dual(pair, window)

        # Verify features
        verify_dual_features(table_id)

        print("\n📊 DUAL PROCESSING IMPLEMENTATION COMPLETE")
        print(f"   Table: {table_id}")
        print(f"   Ready for model training with 28 features")

    except Exception as e:
        print(f"\n❌ Error: {e}")