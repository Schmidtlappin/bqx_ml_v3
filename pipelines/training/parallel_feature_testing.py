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
MAX_WORKERS = 16  # CE approved 2025-12-11 (all workers focus on ONE pair at a time)
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

    FIVE categories per CE directive 2025-12-11:
    1. Pair-specific (%pair%): ~256 tables
    2. Triangulation (tri_*): ~194 tables
    3. Market-wide (mkt_*): ~12 tables
    4. Variance (var_*): ~63 tables (currency-level)
    5. Currency Strength (csi_*): ~144 tables (currency-level)

    Total: ~669 tables per pair (100% coverage)
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
    # CE Directive 2025-12-11 08:35: EXCLUDE summary tables (metadata, not ML features)
    mkt_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'mkt_')
    ORDER BY table_name
    """
    mkt_tables = [row.table_name for row in client.query(mkt_query).result()]
    # Exclude summary tables per CE directive - they are metadata, not interval features
    mkt_tables = [t for t in mkt_tables if not t.endswith('_summary')]

    # Category 4: Variance tables (currency-level, apply to all pairs)
    # CE Directive 2025-12-11: 63 tables missing
    var_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'var_')
    ORDER BY table_name
    """
    var_tables = [row.table_name for row in client.query(var_query).result()]

    # Category 5: Currency Strength Index tables (currency-level, apply to all pairs)
    # CE Directive 2025-12-11: 144 tables missing
    csi_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'csi_')
    ORDER BY table_name
    """
    csi_tables = [row.table_name for row in client.query(csi_query).result()]

    return {
        'pair_specific': pair_tables,
        'triangulation': tri_tables,
        'market_wide': mkt_tables,
        'variance': var_tables,
        'currency_strength': csi_tables
    }


# Global cache for table columns (populated once, used many times)
_TABLE_COLUMNS_CACHE = {}

def get_all_table_columns_batch(table_names: list) -> dict:
    """
    Batch query to get columns for ALL tables at once.
    Much faster than per-table queries (1 query instead of 462).
    """
    global _TABLE_COLUMNS_CACHE
    if _TABLE_COLUMNS_CACHE:
        return _TABLE_COLUMNS_CACHE

    client = bigquery.Client(project=PROJECT)
    table_list = "', '".join(table_names)

    query = f"""
    SELECT table_name, column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name IN ('{table_list}')
    AND column_name NOT IN ('interval_time', 'pair')
    ORDER BY table_name, ordinal_position
    """

    print(f"    Fetching columns for {len(table_names)} tables (batch query)...", flush=True)
    result = client.query(query).result()

    # Build cache
    for row in result:
        if row.table_name not in _TABLE_COLUMNS_CACHE:
            _TABLE_COLUMNS_CACHE[row.table_name] = []
        _TABLE_COLUMNS_CACHE[row.table_name].append(row.column_name)

    print(f"    Cached columns for {len(_TABLE_COLUMNS_CACHE)} tables", flush=True)
    return _TABLE_COLUMNS_CACHE


def get_table_columns(table_name: str) -> list:
    """Get ALL columns from a table (excluding interval_time, pair). Uses cache if available."""
    global _TABLE_COLUMNS_CACHE
    if _TABLE_COLUMNS_CACHE:
        return _TABLE_COLUMNS_CACHE.get(table_name, [])

    # Fallback to single query if cache not populated
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
                    # Get feature columns (exclude duplicates already in current_df)
                    existing_cols = set(current_df.columns)
                    feature_cols = [c for c in feature_df.columns if c != 'interval_time' and c not in existing_cols]
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


def query_pair_direct(pair: str, date_start: str, date_end: str) -> tuple:
    """
    Query ALL features for a pair using DIRECT IN-MEMORY merge.

    SIMPLER APPROACH for 64GB RAM:
    - Query targets first (100K rows)
    - Query each table and merge immediately
    - No intermediate parquet files
    - Proven to work in Step 5 (24GB peak, 10,783 features)

    Returns: (merged_df, cost_info)
    """
    client = bigquery.Client(project=PROJECT)
    print(f"  Querying {pair.upper()} (DIRECT IN-MEMORY - 64GB RAM)...", flush=True)

    # Step 1: Get targets
    targets_df, targets_bytes = query_targets(pair, date_start, date_end)
    if targets_df is None or len(targets_df) < 1000:
        return None, {'error': 'Insufficient target data'}

    print(f"    Targets: {len(targets_df):,} rows", flush=True)
    total_bytes = targets_bytes

    # Step 2: Get all feature tables
    tables = get_feature_tables_for_pair(pair)
    all_tables = (
        tables['pair_specific'] +
        tables['triangulation'] +
        tables['market_wide'] +
        tables.get('variance', []) +
        tables.get('currency_strength', [])
    )
    print(f"    Tables: {len(all_tables)} total", flush=True)
    print(f"      - pair_specific: {len(tables['pair_specific'])}", flush=True)
    print(f"      - triangulation: {len(tables['triangulation'])}", flush=True)
    print(f"      - market_wide: {len(tables['market_wide'])}", flush=True)
    print(f"      - variance: {len(tables.get('variance', []))}", flush=True)
    print(f"      - currency_strength: {len(tables.get('currency_strength', []))}", flush=True)

    # Step 2.5: Batch fetch ALL column metadata (1 query instead of 462)
    get_all_table_columns_batch(all_tables)

    print(f"    Starting table-by-table extraction...", flush=True)

    # Step 3: Query and merge each table directly
    merged_df = targets_df.copy()
    del targets_df
    gc.collect()

    success_count = 0
    import time as _time
    start_time = _time.time()

    for i, table_name in enumerate(all_tables):
        table_start = _time.time()

        try:
            # Get columns
            cols = get_table_columns(table_name)
            if not cols:
                print(f"      [{i+1:3d}/{len(all_tables)}] {table_name}: SKIP (no cols)", flush=True)
                continue

            # Query table
            col_list = ', '.join(cols)
            query = f"""
            SELECT interval_time, {col_list}
            FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
            ORDER BY interval_time
            LIMIT {SAMPLE_LIMIT}
            """

            job = client.query(query)
            table_df = job.to_dataframe()
            total_bytes += job.total_bytes_processed or 0

            if len(table_df) == 0 or 'interval_time' not in table_df.columns:
                print(f"      [{i+1:3d}/{len(all_tables)}] {table_name}: SKIP (empty)", flush=True)
                continue

            # Add column prefix based on table name to avoid collisions
            # e.g., corr_bqx_ibkr_eurusd_ewa -> corr_bqx_ibkr_ewa
            prefix = table_name.replace(f'_{pair}', '').replace('__', '_').strip('_')
            rename_map = {c: f"{prefix}_{c}" for c in table_df.columns if c != 'interval_time'}
            table_df = table_df.rename(columns=rename_map)

            # Get feature columns (exclude duplicates already in merged_df)
            existing_cols = set(merged_df.columns)
            feature_cols = [c for c in table_df.columns if c != 'interval_time' and c not in existing_cols]
            if not feature_cols:
                # All columns already exist - skip silently
                print(f"      [{i+1:3d}/{len(all_tables)}] {table_name}: SKIP (dup cols)", flush=True)
                del table_df
                continue

            # Merge with main dataframe
            merged_df = merged_df.merge(
                table_df[['interval_time'] + feature_cols],
                on='interval_time',
                how='left'
            )

            elapsed = _time.time() - table_start
            print(f"      [{i+1:3d}/{len(all_tables)}] {table_name}: +{len(feature_cols)} cols, {len(table_df):,} rows ({elapsed:.1f}s)", flush=True)

            success_count += 1
            del table_df

            # Periodic garbage collection and progress summary
            if (i + 1) % 100 == 0:
                gc.collect()
                total_elapsed = _time.time() - start_time
                print(f"      === CHECKPOINT: {i+1}/{len(all_tables)} tables, {len(merged_df.columns)} total cols, {total_elapsed:.0f}s elapsed ===", flush=True)

        except Exception as e:
            print(f"      [{i+1:3d}/{len(all_tables)}] {table_name}: ERROR - {e}", flush=True)
            continue

    total_elapsed = _time.time() - start_time
    print(f"      === COMPLETE: {len(all_tables)}/{len(all_tables)} tables in {total_elapsed:.0f}s ===", flush=True)

    # Final stats
    gb_scanned = total_bytes / (1024**3)
    cost_estimate = gb_scanned * 5 / 1000  # $5 per TB

    target_cols = [c for c in merged_df.columns if c.startswith('target_')]
    feature_cols = [c for c in merged_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    print(f"    Merged: {len(merged_df):,} rows, {len(feature_cols):,} features")
    print(f"    Cost: {gb_scanned:.2f} GB scanned, ~${cost_estimate:.2f}")

    cost_info = {
        'gb_scanned': gb_scanned,
        'cost': cost_estimate,
        'feature_count': len(feature_cols),
        'table_count': success_count,
        'bytes_scanned': total_bytes
    }

    # Save to persistent storage
    features_dir = "/home/micha/bqx_ml_v3/data/features"
    os.makedirs(features_dir, exist_ok=True)
    parquet_path = os.path.join(features_dir, f"{pair}_merged_features.parquet")
    merged_df.to_parquet(parquet_path, index=False)
    print(f"    Saved: {parquet_path} ({os.path.getsize(parquet_path) / 1e9:.2f} GB)")

    return merged_df, cost_info


def _extract_single_table_checkpoint(args) -> dict:
    """Worker function for parallel table extraction with checkpointing."""
    table_name, pair, date_start, date_end, checkpoint_dir, cols = args
    from pathlib import Path
    import sys

    print(f"      [DEBUG] Starting extraction: {table_name}", flush=True)
    sys.stdout.flush()

    parquet_path = Path(checkpoint_dir) / f"{table_name}.parquet"

    # Skip if already exists (checkpoint)
    if parquet_path.exists():
        return {'table': table_name, 'status': 'cached', 'cols': 0, 'bytes': 0}

    try:
        client = bigquery.Client(project=PROJECT)

        if not cols:
            return {'table': table_name, 'status': 'skip_no_cols', 'cols': 0, 'bytes': 0}

        col_list = ', '.join(cols)

        # CE Directive 2025-12-11 08:35: Summary tables EXCLUDED at query level
        # All remaining tables have interval_time column
        query = f"""
        SELECT interval_time, {col_list}
        FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
        ORDER BY interval_time
        LIMIT {SAMPLE_LIMIT}
        """

        job = client.query(query)
        table_df = job.to_dataframe()
        bytes_scanned = job.total_bytes_processed or 0

        if len(table_df) == 0 or 'interval_time' not in table_df.columns:
            return {'table': table_name, 'status': 'skip_empty', 'cols': 0, 'bytes': bytes_scanned}

        # Apply column prefix (bug fix)
        prefix = table_name.replace(f'_{pair}', '').replace('__', '_').strip('_')
        rename_map = {c: f"{prefix}_{c}" for c in table_df.columns if c != 'interval_time'}
        table_df = table_df.rename(columns=rename_map)

        # Save checkpoint immediately
        table_df.to_parquet(parquet_path, index=False)
        col_count = len([c for c in table_df.columns if c != 'interval_time'])

        return {'table': table_name, 'status': 'saved', 'cols': col_count, 'bytes': bytes_scanned}

    except Exception as e:
        return {'table': table_name, 'status': 'error', 'error': str(e), 'cols': 0, 'bytes': 0}


def query_pair_with_checkpoints(pair: str, date_start: str, date_end: str, max_workers: int = MAX_WORKERS) -> tuple:
    """
    Query ALL features for a pair using PARQUET CHECKPOINT approach with PARALLEL extraction.

    USER MANDATE: Resume capability - process MUST accommodate resume with saved data.
    PARALLEL MODE: Uses all 12 workers for table queries on ONE pair at a time.

    Architecture:
    1. Create checkpoint directory: data/features/checkpoints/{pair}/
    2. For each table (PARALLEL with 12 workers):
       - Check if parquet exists: SKIP if yes (already done)
       - If not: Query, prefix columns, save to parquet
    3. After all tables extracted:
       - Merge all parquets for pair
       - Save final: data/features/{pair}_merged_features.parquet
       - Mark pair complete: _COMPLETE marker

    Returns: (merged_df, cost_info)
    """
    from pathlib import Path
    import time as _time

    # Checkpoint directory structure
    checkpoint_base = Path("/home/micha/bqx_ml_v3/data/features/checkpoints")
    checkpoint_dir = checkpoint_base / pair
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    complete_marker = checkpoint_dir / "_COMPLETE"
    final_parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"

    # Check if already complete
    if complete_marker.exists():
        print(f"  {pair.upper()} already COMPLETE, loading cached result...", flush=True)
        if os.path.exists(final_parquet_path):
            merged_df = pd.read_parquet(final_parquet_path)
            return merged_df, {'status': 'cached', 'cost': 0}
        else:
            complete_marker.unlink()
            print(f"    Stale marker removed, re-processing...", flush=True)

    print(f"  Querying {pair.upper()} (CHECKPOINT MODE - {max_workers} parallel workers)...", flush=True)

    # Step 1: Get/check targets
    targets_path = checkpoint_dir / "targets.parquet"
    total_bytes = 0

    if targets_path.exists():
        print(f"    Targets: CACHED", flush=True)
        targets_df = pd.read_parquet(targets_path)
    else:
        targets_df, targets_bytes = query_targets(pair, date_start, date_end)
        if targets_df is None or len(targets_df) < 1000:
            return None, {'error': 'Insufficient target data'}
        targets_df.to_parquet(targets_path, index=False)
        total_bytes += targets_bytes
        print(f"    Targets: {len(targets_df):,} rows SAVED", flush=True)

    # Step 2: Get all feature tables (5 categories per CE directive)
    tables = get_feature_tables_for_pair(pair)
    all_tables = (
        tables['pair_specific'] +
        tables['triangulation'] +
        tables['market_wide'] +
        tables.get('variance', []) +
        tables.get('currency_strength', [])
    )
    print(f"    Tables: {len(all_tables)} total", flush=True)
    print(f"      - pair_specific: {len(tables['pair_specific'])}", flush=True)
    print(f"      - triangulation: {len(tables['triangulation'])}", flush=True)
    print(f"      - market_wide: {len(tables['market_wide'])}", flush=True)
    print(f"      - variance: {len(tables.get('variance', []))}", flush=True)
    print(f"      - currency_strength: {len(tables.get('currency_strength', []))}", flush=True)

    # Batch fetch column metadata
    col_cache = get_all_table_columns_batch(all_tables)

    # Count already cached
    cached_count = sum(1 for t in all_tables if (checkpoint_dir / f"{t}.parquet").exists())
    pending_tables = [t for t in all_tables if not (checkpoint_dir / f"{t}.parquet").exists()]
    print(f"    Status: {cached_count} cached, {len(pending_tables)} pending", flush=True)

    if len(pending_tables) == 0:
        print(f"    All tables already extracted!", flush=True)
        success_count = 0
        error_count = 0
    else:
        print(f"    Starting PARALLEL extraction ({max_workers} workers)...", flush=True)

        # Prepare work items
        work_items = [
            (table_name, pair, date_start, date_end, str(checkpoint_dir), col_cache.get(table_name, []))
            for table_name in pending_tables
        ]

        start_time = _time.time()
        success_count = 0
        error_count = 0
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_extract_single_table_checkpoint, item): item[0] for item in work_items}

            for future in as_completed(futures):
                table_name = futures[future]
                completed += 1
                try:
                    result = future.result(timeout=300)

                    if result['status'] == 'saved':
                        success_count += 1
                        total_bytes += result['bytes']
                        print(f"      [{cached_count + completed:3d}/{len(all_tables)}] {table_name}: +{result['cols']} cols SAVED", flush=True)
                    elif result['status'] == 'error':
                        error_count += 1
                        print(f"      [{cached_count + completed:3d}/{len(all_tables)}] {table_name}: ERROR - {result.get('error', 'unknown')}", flush=True)
                    else:
                        print(f"      [{cached_count + completed:3d}/{len(all_tables)}] {table_name}: SKIP ({result['status']})", flush=True)

                    # Progress update every 50 tables
                    if completed % 50 == 0:
                        elapsed = _time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        remaining = (len(pending_tables) - completed) / rate if rate > 0 else 0
                        print(f"      === Progress: {completed}/{len(pending_tables)} ({rate:.1f}/s, ~{remaining:.0f}s remaining) ===", flush=True)

                except Exception as e:
                    error_count += 1
                    print(f"      [{cached_count + completed:3d}/{len(all_tables)}] {table_name}: EXCEPTION - {e}", flush=True)

        extraction_elapsed = _time.time() - start_time
        print(f"    Extraction complete: {success_count} new, {cached_count} cached, {error_count} errors in {extraction_elapsed:.0f}s", flush=True)

    # Step 3: Merge all checkpoints
    print(f"    Merging checkpoints...", flush=True)
    merge_start = _time.time()

    merged_df = targets_df.copy()
    del targets_df

    checkpoint_files = sorted(checkpoint_dir.glob("*.parquet"))
    merged_cols = set(merged_df.columns)

    for pq_file in checkpoint_files:
        if pq_file.name == "targets.parquet":
            continue

        try:
            table_df = pd.read_parquet(pq_file)

            # Get non-duplicate columns
            feature_cols = [c for c in table_df.columns if c != 'interval_time' and c not in merged_cols]
            if not feature_cols:
                continue

            # Merge
            merged_df = merged_df.merge(
                table_df[['interval_time'] + feature_cols],
                on='interval_time',
                how='left'
            )
            merged_cols.update(feature_cols)
            del table_df

        except Exception as e:
            print(f"      Error merging {pq_file.name}: {e}", flush=True)
            continue

    merge_elapsed = _time.time() - merge_start
    gc.collect()

    # Final stats
    gb_scanned = total_bytes / (1024**3)
    cost_estimate = gb_scanned * 5 / 1000

    target_cols = [c for c in merged_df.columns if c.startswith('target_')]
    feature_cols = [c for c in merged_df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    print(f"    Merged: {len(merged_df):,} rows, {len(feature_cols):,} features in {merge_elapsed:.0f}s")
    print(f"    Cost: {gb_scanned:.2f} GB scanned, ~${cost_estimate:.2f}")

    # Save final merged parquet
    merged_df.to_parquet(final_parquet_path, index=False)
    final_size = os.path.getsize(final_parquet_path) / 1e9
    print(f"    Saved: {final_parquet_path} ({final_size:.2f} GB)")

    # Mark as complete
    complete_marker.touch()
    print(f"    Marked COMPLETE: {complete_marker}")

    cost_info = {
        'gb_scanned': gb_scanned,
        'cost': cost_estimate,
        'feature_count': len(feature_cols),
        'table_count': success_count + cached_count,
        'new_tables': success_count,
        'cached_tables': cached_count,
        'bytes_scanned': total_bytes
    }

    return merged_df, cost_info


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
    print(f"      - variance: {len(table_groups.get('variance', []))}")
    print(f"      - currency_strength: {len(table_groups.get('currency_strength', []))}")

    # Step 3: Query each table in parallel, save to parquet
    total_bytes = targets_bytes
    total_features = 0
    successful_tables = 0

    # Combine all tables into single list for parallel processing
    all_tables = (
        table_groups['pair_specific'] +
        table_groups['triangulation'] +
        table_groups['market_wide'] +
        table_groups.get('variance', []) +
        table_groups.get('currency_strength', [])
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
        # Query all features using CHECKPOINT approach (resume capability - USER MANDATE)
        df, cost_info = query_pair_with_checkpoints(pair, date_start, date_end)

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
    Run batch processing - ONE PAIR AT A TIME with parallel table queries.

    USER MANDATE (2025-12-11): All 12 workers focus on completing ONE pair at a time.
    - Pairs processed SEQUENTIALLY (one by one)
    - Tables within each pair processed in PARALLEL (12 workers)
    """
    if pairs is None:
        pairs = ALL_28_PAIRS

    print("=" * 70)
    print("SEQUENTIAL PAIR PROCESSING - USER MANDATE")
    print(f"(All {max_workers} workers focus on ONE pair at a time)")
    print("=" * 70)
    print(f"Pairs: {len(pairs)}")
    print(f"Table workers per pair: {max_workers}")
    print(f"Date range: {date_start} to {date_end}")
    print("=" * 70)

    start_time = datetime.now()
    all_results = {}
    total_cost = 0

    # USER MANDATE: Process pairs SEQUENTIALLY, one at a time
    for i, pair in enumerate(pairs, 1):
        print(f"\n{'='*70}")
        print(f"PAIR {i}/{len(pairs)}: {pair.upper()}")
        print(f"{'='*70}")

        try:
            result = process_pair_all_horizons(pair, date_start, date_end)
            all_results[pair] = result
            if result.get('cost'):
                total_cost += result['cost'].get('cost', 0)
            print(f"  ✓ {pair.upper()} COMPLETE")
        except Exception as e:
            all_results[pair] = {'pair': pair, 'status': 'error', 'message': str(e)}
            print(f"  ✗ {pair.upper()} ERROR: {e}")

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

    # Get ALL feature tables (5 categories per CE directive 2025-12-11)
    print("\nDiscovering features (5 categories)...")
    table_groups = get_feature_tables_for_pair(pair)

    total_tables = sum(len(tables) for tables in table_groups.values())
    print(f"  Tables found: {total_tables} total")
    print(f"    - pair_specific: {len(table_groups['pair_specific'])}")
    print(f"    - triangulation: {len(table_groups['triangulation'])}")
    print(f"    - market_wide: {len(table_groups['market_wide'])}")
    print(f"    - variance: {len(table_groups.get('variance', []))}")
    print(f"    - currency_strength: {len(table_groups.get('currency_strength', []))}")

    # Combine all tables
    all_tables = (
        table_groups['pair_specific'] +
        table_groups['triangulation'] +
        table_groups['market_wide'] +
        table_groups.get('variance', []) +
        table_groups.get('currency_strength', [])
    )

    feature_count = 0
    total_bytes_estimate = 0
    category_stats = {'pair_specific': 0, 'triangulation': 0, 'market_wide': 0, 'variance': 0, 'currency_strength': 0}

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
