#!/usr/bin/env python3
"""
Parallel Batch Feature Testing Pipeline - FULL 11,337 COLUMN UNIVERSE

Implements cost-optimized parallel processing:
- BATCHED TABLE QUERIES: Query each table separately, merge locally
- Avoids complex multi-table JOINs (BigQuery limit mitigation)
- Parallel table queries using ThreadPoolExecutor
- Parallel pair processing using ProcessPoolExecutor
- Cost target: ~$30 total (CE approved $29.56)

CE DIRECTIVE: 2025-12-10 06:00 (EXECUTION APPROVED)
CORRECTED COUNTS (2025-12-10):
- Total columns: 11,337 (for BigQuery cost estimation)
- Unique features: 1,064 (for ML training after merge/dedup)
- Tables per pair: 462 (256 pair + 194 tri + 12 mkt)
"""

import sys
import json
import os
import shutil
import numpy as np
import pandas as pd
import duckdb
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
from google.cloud import bigquery
import warnings
import gc
warnings.filterwarnings('ignore')

# Configuration
PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]
MAX_WORKERS = 1  # Sequential pairs (disk limit: 64GB, each pair ~7GB)
MAX_TABLE_WORKERS = 8  # Parallel table queries per pair (CE approved)
SAMPLE_LIMIT = 100000  # 100K samples - CE approved for 64GB RAM (n2-highmem-8)

# Chunk directory for parquet files
CHUNK_DIR = "/tmp/feature_chunks"

ALL_28_PAIRS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
    "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
    "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
    "audjpy", "audchf", "audcad", "audnzd",
    "nzdjpy", "nzdchf", "nzdcad",
    "cadjpy", "cadchf", "chfjpy"
]


def get_feature_tables_for_pair(pair: str) -> dict:
    """
    Get ALL feature tables for COMPLETE feature universe.

    THREE categories per CE directive 05:40:
    1. Pair-specific (%pair%): ~256 tables, 4,173 cols
    2. Triangulation (tri_*): ~194 tables, 6,460 cols
    3. Market-wide (mkt_*): ~12 tables, 704 cols

    Total: ~462 tables, ~11,337 columns
    """
    client = bigquery.Client(project=PROJECT)

    # Category 1: Pair-specific tables
    pair_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE '%{pair}%'
    ORDER BY table_name
    """
    pair_tables = [row.table_name for row in client.query(pair_query).result()]

    # Category 2: Triangulation tables (cross-pair, apply to all)
    tri_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'tri_')
    ORDER BY table_name
    """
    tri_tables = [row.table_name for row in client.query(tri_query).result()]

    # Category 3: Market-wide tables (apply to all pairs)
    mkt_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'mkt_')
    ORDER BY table_name
    """
    mkt_tables = [row.table_name for row in client.query(mkt_query).result()]

    return {
        'pair_specific': pair_tables,
        'triangulation': tri_tables,
        'market_wide': mkt_tables
    }


def get_table_columns(table_name: str) -> list:
    """Get ALL columns from a table (excluding interval_time, pair)."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    AND column_name NOT IN ('interval_time', 'pair')
    ORDER BY ordinal_position
    """

    columns = [row.column_name for row in client.query(query).result()]
    return columns


def query_single_table_to_parquet(table_name: str, pair: str, date_start: str, date_end: str, chunk_dir: str) -> tuple:
    """
    Query a single feature table and save to parquet file.

    MEMORY-EFFICIENT: Saves to disk immediately, doesn't hold in memory.
    Returns: (table_name, parquet_path, bytes_scanned, column_count)
    """
    client = bigquery.Client(project=PROJECT)

    try:
        # Get columns for this table
        cols = get_table_columns(table_name)
        if not cols:
            return table_name, None, 0, 0

        # Build query for this table WITH date filter for efficiency
        col_list = ', '.join(cols)
        query = f"""
        SELECT interval_time, {col_list}
        FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ORDER BY interval_time
        LIMIT {SAMPLE_LIMIT}
        """

        job = client.query(query)
        df = job.to_dataframe()
        bytes_scanned = job.total_bytes_processed or 0

        if len(df) == 0:
            return table_name, None, bytes_scanned, 0

        # Prefix columns with table name to avoid duplicates
        prefix = table_name.replace(f'_{pair}', '').replace('_', '')
        rename_map = {col: f"{prefix}_{col}" for col in cols}
        df = df.rename(columns=rename_map)

        # Save to parquet immediately (memory efficient)
        parquet_path = os.path.join(chunk_dir, f"{table_name}.parquet")
        df.to_parquet(parquet_path, index=False)

        # Free memory immediately
        col_count = len(cols)
        del df

        return table_name, parquet_path, bytes_scanned, col_count

    except Exception as e:
        print(f"    Warning: {table_name}: {e}")
        return table_name, None, 0, 0


def merge_parquet_with_duckdb(targets_path: str, chunk_dir: str, output_path: str) -> pd.DataFrame:
    """
    Use DuckDB to efficiently merge all parquet files in BATCHES.

    BATCHED APPROACH: Merge 50 files at a time to avoid OOM.
    Memory usage: ~4-6GB peak instead of 25GB+
    """
    con = duckdb.connect()

    # Configure DuckDB for memory efficiency
    con.execute("SET preserve_insertion_order=false")
    con.execute("SET threads=2")

    # Get list of feature parquet files
    parquet_files = [f for f in os.listdir(chunk_dir) if f.endswith('.parquet') and f != 'targets.parquet']

    if not parquet_files:
        return pd.read_parquet(targets_path)

    print(f"      Merging {len(parquet_files)} files in batches...")

    # Start with targets
    current_df = pd.read_parquet(targets_path)
    print(f"      Base: {len(current_df):,} rows, {len(current_df.columns)} cols")

    # Merge in batches of 50 files
    BATCH_SIZE = 50
    for batch_start in range(0, len(parquet_files), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(parquet_files))
        batch_files = parquet_files[batch_start:batch_end]

        # Read batch files and merge
        for pf in batch_files:
            pf_path = os.path.join(chunk_dir, pf)
            try:
                feature_df = pd.read_parquet(pf_path)
                if 'interval_time' in feature_df.columns:
                    # Get feature columns (exclude interval_time)
                    feature_cols = [c for c in feature_df.columns if c != 'interval_time']
                    if feature_cols:
                        current_df = current_df.merge(
                            feature_df[['interval_time'] + feature_cols],
                            on='interval_time',
                            how='left'
                        )
                del feature_df
            except Exception as e:
                print(f"      Warning: {pf}: {e}")

        # Progress update
        print(f"      Batch {batch_start//BATCH_SIZE + 1}: {len(current_df.columns):,} columns", flush=True)

        # Force garbage collection between batches
        gc.collect()

    con.close()
    print(f"      Final: {len(current_df):,} rows, {len(current_df.columns):,} columns")
    return current_df


def query_targets(pair: str, date_start: str, date_end: str) -> tuple:
    """Query targets table with all 7 horizons."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        interval_time,
        target_bqx45_h15,
        target_bqx45_h30,
        target_bqx45_h45,
        target_bqx45_h60,
        target_bqx45_h75,
        target_bqx45_h90,
        target_bqx45_h105
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    AND target_bqx45_h15 IS NOT NULL
    ORDER BY interval_time
    LIMIT {SAMPLE_LIMIT}
    """

    job = client.query(query)
    df = job.to_dataframe()
    bytes_scanned = job.total_bytes_processed or 0

    return df, bytes_scanned


def query_pair_batched(pair: str, date_start: str, date_end: str) -> tuple:
    """
    Query ALL features for a pair using PARQUET-CHUNKED approach with DuckDB.

    MEMORY-EFFICIENT: Uses ~4-6GB instead of 12GB+
    1. Query targets first, save to parquet
    2. Query each feature table, save to parquet immediately
    3. Use DuckDB to merge all parquet files efficiently

    This avoids memory issues with large dataframe merges.
    """
    print(f"  Querying {pair.upper()} (COMPLETE universe - PARQUET CHUNKED)...")

    # Create fresh chunk directory for this pair
    pair_chunk_dir = os.path.join(CHUNK_DIR, pair)
    if os.path.exists(pair_chunk_dir):
        shutil.rmtree(pair_chunk_dir)
    os.makedirs(pair_chunk_dir, exist_ok=True)

    # Step 1: Query targets (defines our time index)
    targets_df, targets_bytes = query_targets(pair, date_start, date_end)
    print(f"    Targets: {len(targets_df):,} rows")

    if len(targets_df) == 0:
        return None, {'error': 'No target data'}

    # Save targets to parquet
    targets_path = os.path.join(pair_chunk_dir, "targets.parquet")
    targets_df.to_parquet(targets_path, index=False)
    del targets_df  # Free memory
    gc.collect()

    # Step 2: Get ALL feature tables (3 categories)
    table_groups = get_feature_tables_for_pair(pair)
    total_tables = sum(len(tables) for tables in table_groups.values())
    print(f"    Tables: {total_tables} total")
    print(f"      - pair_specific: {len(table_groups['pair_specific'])}")
    print(f"      - triangulation: {len(table_groups['triangulation'])}")
    print(f"      - market_wide: {len(table_groups['market_wide'])}")

    # Step 3: Query each table in parallel, save to parquet
    total_bytes = targets_bytes
    total_features = 0
    successful_tables = 0

    # Combine all tables into single list for parallel processing
    all_tables = (
        table_groups['pair_specific'] +
        table_groups['triangulation'] +
        table_groups['market_wide']
    )

    print(f"    Querying tables to parquet (memory-efficient)...")

    with ThreadPoolExecutor(max_workers=MAX_TABLE_WORKERS) as executor:
        futures = {
            executor.submit(query_single_table_to_parquet, table, pair, date_start, date_end, pair_chunk_dir): table
            for table in all_tables
        }

        completed = 0
        total = len(all_tables)
        for future in as_completed(futures):
            table = futures[future]
            completed += 1
            try:
                table_name, parquet_path, bytes_scanned, col_count = future.result()
                total_bytes += bytes_scanned

                if parquet_path is not None:
                    total_features += col_count
                    successful_tables += 1

                # Progress update every 25 tables
                if completed % 25 == 0 or completed == total:
                    print(f"      Progress: {completed}/{total} tables ({100*completed//total}%)", flush=True)

            except Exception as e:
                print(f"    Error {table}: {e}", flush=True)

    # Step 4: Use DuckDB to merge all parquet files efficiently
    print(f"    Merging {successful_tables} parquet files with DuckDB...")
    output_path = os.path.join(pair_chunk_dir, "merged.parquet")

    try:
        merged_df = merge_parquet_with_duckdb(targets_path, pair_chunk_dir, output_path)
        print(f"    Merged: {len(merged_df):,} rows, {len(merged_df.columns):,} columns")
    except Exception as e:
        print(f"    DuckDB merge error: {e}")
        # Fallback: just read targets
        merged_df = pd.read_parquet(targets_path)

    # Calculate cost
    gb_scanned = total_bytes / (1024**3)
    cost_estimate = gb_scanned * 6.25 / 1000

    print(f"    Total: {len(merged_df):,} rows, {total_features:,} features, "
          f"{gb_scanned:.2f} GB, ~${cost_estimate:.2f}")

    cost_info = {
        'gb_scanned': gb_scanned,
        'cost': cost_estimate,
        'feature_count': total_features,
        'table_count': total_tables,
        'bytes_scanned': total_bytes
    }

    # Save merged features to persistent storage (CE directive 2025-12-10)
    features_dir = "/home/micha/bqx_ml_v3/data/features"
    merged_parquet_path = os.path.join(features_dir, f"{pair}_merged_features.parquet")
    merged_df.to_parquet(merged_parquet_path, index=False)
    print(f"    Saved: {merged_parquet_path} ({os.path.getsize(merged_parquet_path) / 1e9:.2f} GB)")

    # Cleanup chunk files AFTER merged parquet is saved (disk management)
    if os.path.exists(merged_parquet_path):
        shutil.rmtree(pair_chunk_dir)
        print(f"    Cleaned up chunks for {pair}")

    return merged_df, cost_info


def process_pair_all_horizons(pair: str, date_start: str = '2020-01-01',
                              date_end: str = '2024-12-31') -> dict:
    """
    Process ONE pair: query all features (batched), then process 7 horizons locally.
    """
    print(f"\n{'='*50}")
    print(f"Processing {pair.upper()}")
    print(f"{'='*50}")

    try:
        # Query all features using batched approach
        df, cost_info = query_pair_batched(pair, date_start, date_end)

        if df is None or len(df) < 1000:
            return {'pair': pair, 'status': 'error', 'message': 'Insufficient data'}

        # Identify feature and target columns
        target_cols = [c for c in df.columns if c.startswith('target_')]
        feature_cols = [c for c in df.columns if c not in target_cols
                       and c not in ['interval_time', 'pair']]

        results = {
            'pair': pair,
            'status': 'success',
            'rows': len(df),
            'feature_count': len(feature_cols),
            'cost': cost_info,
            'horizons': {}
        }

        # Process ALL 7 horizons locally
        for horizon in HORIZONS:
            target_col = f'target_bqx45_h{horizon}'
            if target_col not in df.columns:
                continue

            results['horizons'][f'h{horizon}'] = {
                'target_col': target_col,
                'samples': len(df[df[target_col].notna()]),
                'status': 'ready'
            }
            print(f"    h{horizon}: {results['horizons'][f'h{horizon}']['samples']:,} samples")

        # Clean up memory
        del df
        gc.collect()

        return results

    except Exception as e:
        return {'pair': pair, 'status': 'error', 'message': str(e)}


def run_parallel_batch_testing(pairs: list = None, max_workers: int = MAX_WORKERS,
                               date_start: str = '2020-01-01',
                               date_end: str = '2024-12-31') -> dict:
    """
    Run parallel batch processing across multiple pairs.
    """
    if pairs is None:
        pairs = ALL_28_PAIRS

    print("=" * 70)
    print("PARALLEL BATCH FEATURE TESTING - FULL 11,337 COLUMN UNIVERSE")
    print(f"Pairs: {len(pairs)}")
    print(f"Workers: {max_workers}")
    print(f"Date range: {date_start} to {date_end}")
    print("=" * 70)

    start_time = datetime.now()
    all_results = {}
    total_cost = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_pair_all_horizons, pair, date_start, date_end): pair
            for pair in pairs
        }

        for future in as_completed(futures):
            pair = futures[future]
            try:
                result = future.result(timeout=3600)
                all_results[pair] = result
                if result.get('cost'):
                    total_cost += result['cost'].get('cost', 0)
            except Exception as e:
                all_results[pair] = {'pair': pair, 'status': 'error', 'message': str(e)}

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 3600

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Pairs: {len(all_results)}")
    print(f"Cost: ${total_cost:.2f}")
    print(f"Time: {duration:.2f} hours")

    return {
        'timestamp': datetime.now().isoformat(),
        'pairs_processed': len(all_results),
        'total_cost': total_cost,
        'duration_hours': duration,
        'results': all_results
    }


def dry_run_cost_validation(pair: str = 'eurusd') -> dict:
    """
    Dry run to validate cost before full execution.

    COMPLETE FEATURE UNIVERSE (per CE directive 05:40):
    - pair_specific (%pair%): ~256 tables
    - triangulation (tri_*): ~194 tables
    - market_wide (mkt_*): ~12 tables
    Total: ~462 tables, ~11,337 columns
    """
    print("=" * 70)
    print("DRY RUN COST VALIDATION - COMPLETE FEATURE UNIVERSE")
    print(f"Testing pair: {pair.upper()}")
    print("=" * 70)

    client = bigquery.Client(project=PROJECT)

    # Get ALL feature tables (3 categories)
    print("\nDiscovering features (3 categories)...")
    table_groups = get_feature_tables_for_pair(pair)

    total_tables = sum(len(tables) for tables in table_groups.values())
    print(f"  Tables found: {total_tables} total")
    print(f"    - pair_specific: {len(table_groups['pair_specific'])}")
    print(f"    - triangulation: {len(table_groups['triangulation'])}")
    print(f"    - market_wide: {len(table_groups['market_wide'])}")

    # Combine all tables
    all_tables = (
        table_groups['pair_specific'] +
        table_groups['triangulation'] +
        table_groups['market_wide']
    )

    feature_count = 0
    total_bytes_estimate = 0
    category_stats = {'pair_specific': 0, 'triangulation': 0, 'market_wide': 0}

    print("\n  Counting columns per category...")
    for category, tables in table_groups.items():
        cat_cols = 0
        for table in tables:
            cols = get_table_columns(table)
            cat_cols += len(cols)
            feature_count += len(cols)

            # Dry run each table query
            col_list = ', '.join(cols) if cols else '*'
            query = f"""
            SELECT interval_time, {col_list}
            FROM `{PROJECT}.{FEATURES_DATASET}.{table}`
            LIMIT {SAMPLE_LIMIT}
            """

            try:
                job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
                job = client.query(query, job_config=job_config)
                total_bytes_estimate += job.total_bytes_processed or 0
            except:
                pass

        category_stats[category] = cat_cols
        print(f"    {category}: {cat_cols} columns")

    # Add targets query estimate
    targets_query = f"""
    SELECT interval_time, target_bqx45_h15, target_bqx45_h30, target_bqx45_h45,
           target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    LIMIT {SAMPLE_LIMIT}
    """
    try:
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = client.query(targets_query, job_config=job_config)
        total_bytes_estimate += job.total_bytes_processed or 0
    except:
        pass

    print(f"\n  TOTAL: {feature_count} features from {total_tables} tables")

    gb_estimate = total_bytes_estimate / (1024**3)
    cost_per_pair = gb_estimate * 6.25 / 1000
    cost_28_pairs = cost_per_pair * 28

    print(f"\nDRY RUN RESULTS:")
    print(f"  Tables per pair: {total_tables}")
    print(f"  Features per pair: {feature_count}")
    print(f"  Bytes per pair: {total_bytes_estimate:,} ({gb_estimate:.2f} GB)")
    print(f"  Cost per pair: ${cost_per_pair:.2f}")
    print(f"  Cost 28 pairs: ${cost_28_pairs:.2f}")
    print(f"  Budget limit: $50.00")
    print(f"  CE estimate: ~$31.50")
    print(f"  Status: {'WITHIN BUDGET' if cost_28_pairs < 50 else 'OVER BUDGET'}")

    return {
        'pair': pair,
        'tables_per_pair': total_tables,
        'features_per_pair': feature_count,
        'category_breakdown': category_stats,
        'bytes_per_pair': total_bytes_estimate,
        'gb_per_pair': gb_estimate,
        'cost_per_pair': cost_per_pair,
        'cost_28_pairs': cost_28_pairs,
        'within_budget': cost_28_pairs < 50
    }


def count_features(pair: str = 'eurusd') -> dict:
    """Count features per table for a pair (all 3 categories)."""
    print("=" * 70)
    print(f"FEATURE COUNT FOR {pair.upper()} - COMPLETE UNIVERSE")
    print("=" * 70)

    table_groups = get_feature_tables_for_pair(pair)
    total = 0
    breakdown = {}
    category_stats = {}

    for category, tables in table_groups.items():
        print(f"\n  {category.upper()} ({len(tables)} tables):")
        cat_total = 0
        for table in tables:
            cols = get_table_columns(table)
            count = len(cols)
            cat_total += count
            total += count
            breakdown[table] = count
        category_stats[category] = {'tables': len(tables), 'columns': cat_total}
        print(f"    Tables: {len(tables)}, Columns: {cat_total}")

    total_tables = sum(len(t) for t in table_groups.values())
    print(f"\n  TOTAL: {total} features from {total_tables} tables")

    return {
        'pair': pair,
        'total_features': total,
        'table_count': total_tables,
        'category_stats': category_stats,
        'breakdown': breakdown
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry_run"

    if mode == "dry_run":
        result = dry_run_cost_validation()
        output_file = "/tmp/parallel_batch_dry_run.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved: {output_file}")
        print("\n*** REPORT TO CE BEFORE PROCEEDING ***")

    elif mode == "count":
        pair = sys.argv[2] if len(sys.argv) > 2 else "eurusd"
        result = count_features(pair)

    elif mode == "single":
        pair = sys.argv[2] if len(sys.argv) > 2 else "eurusd"
        result = process_pair_all_horizons(pair)
        print(json.dumps(result, indent=2, default=str))
        # Save results to file
        output_file = f"/tmp/parallel_batch_single_{pair}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nSaved: {output_file}")

    elif mode == "full":
        print("\n*** FULL RUN - REQUIRES CE APPROVAL ***\n")
        results = run_parallel_batch_testing()
        output_file = "/tmp/parallel_batch_full_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nSaved: {output_file}")

    else:
        print("Usage:")
        print("  python parallel_feature_testing.py dry_run")
        print("  python parallel_feature_testing.py count eurusd")
        print("  python parallel_feature_testing.py single eurusd")
        print("  python parallel_feature_testing.py full")
