#!/usr/bin/env python3
"""
BigQuery Feature Extraction to Parquet Checkpoints
Mirrors successful AUDUSD extraction protocol (no DuckDB)

This script ONLY extracts features from BigQuery to parquet checkpoint files.
Merge is handled separately by merge_with_polars_safe.py

Usage:
    python3 extract_to_parquet.py <pair> --workers <N>

Example:
    python3 extract_to_parquet.py audusd --workers 25
"""

import sys
import os
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

# BigQuery configuration
PROJECT_ID = "bqx-ml"
DATASET_V2 = "bqx_ml_v3_features_v2"

# Feature table patterns (667 tables + 1 targets = 668 total)
FEATURE_PATTERNS = {
    'agg': 7,      # Aggregation features (7 horizons)
    'align': 1,    # Aligned base features
    'base_bqx': 1, # BQX base features
    'base_idx': 1, # IDX base features
    'corr_bqx_ibkr': 105,  # BQX-IBKR correlations (15 pairs × 7 horizons)
    'corr_idx_bqx': 105,   # IDX-BQX correlations (15 pairs × 7 horizons)
    'cov_bqx_ibkr': 105,   # BQX-IBKR covariances (15 pairs × 7 horizons)
    'cov_idx_bqx': 105,    # IDX-BQX covariances (15 pairs × 7 horizons)
    'der': 7,      # Derivative features (7 horizons)
    'ewa': 1,      # Exponentially weighted average
    'mom': 7,      # Momentum features (7 horizons)
    'reg': 7,      # Regression features (7 horizons)
    'tri_bqx_ibkr': 105,   # BQX-IBKR triangular arbitrage (15 pairs × 7 horizons)
    'tri_idx_bqx': 105,    # IDX-BQX triangular arbitrage (15 pairs × 7 horizons)
    'vol': 7,      # Volatility features (7 horizons)
    'targets': 1   # Target variables
}


def get_table_list(pair: str) -> list:
    """Generate list of all feature tables for a pair."""
    tables = []

    # Add all feature tables
    for pattern, count in FEATURE_PATTERNS.items():
        if pattern == 'targets':
            tables.append(f"targets_{pair}")
        elif pattern in ['align', 'base_bqx', 'base_idx', 'ewa']:
            # Single table (no horizon suffix)
            tables.append(f"{pattern}_{pair}")
        elif pattern in ['agg', 'der', 'mom', 'reg', 'vol']:
            # Horizon-based tables (h15, h30, h45, h60, h75, h90, h105)
            for horizon in ['h15', 'h30', 'h45', 'h60', 'h75', 'h90', 'h105']:
                tables.append(f"{pattern}_{pair}_{horizon}")
        else:
            # Cross-pair correlation/covariance/triangular tables
            # Pattern: corr_bqx_ibkr_eurusd_gbpusd_h15 (15 pairs × 7 horizons)
            other_pairs = [
                'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd',
                'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'gbpjpy',
                'gbpchf', 'chfjpy', 'audjpy', 'nzdusd', 'usdcad'
            ]
            for other_pair in other_pairs:
                if other_pair != pair:
                    for horizon in ['h15', 'h30', 'h45', 'h60', 'h75', 'h90', 'h105']:
                        tables.append(f"{pattern}_{pair}_{other_pair}_{horizon}")

    return sorted(tables)


def extract_table(args):
    """Extract a single table from BigQuery to parquet."""
    table_name, pair, checkpoint_dir = args

    output_file = checkpoint_dir / f"{table_name}.parquet"

    # Skip if already exists
    if output_file.exists():
        return {'table': table_name, 'status': 'skipped', 'reason': 'exists'}

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Query: SELECT * FROM table ORDER BY interval_time
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_V2}.{table_name}`
        ORDER BY interval_time
        """

        # Execute query
        df = client.query(query).to_dataframe()

        if df.empty:
            return {'table': table_name, 'status': 'empty', 'rows': 0}

        # Write to parquet
        df.to_parquet(output_file, index=False)

        return {
            'table': table_name,
            'status': 'success',
            'rows': len(df),
            'size_mb': output_file.stat().st_size / 1024**2
        }

    except Exception as e:
        return {
            'table': table_name,
            'status': 'error',
            'error': str(e)
        }


def extract_features(pair: str, workers: int = 25, checkpoint_dir: Path = None):
    """
    Extract all feature tables for a pair from BigQuery to parquet checkpoints.

    Args:
        pair: Currency pair (e.g., 'audusd')
        workers: Number of parallel workers
        checkpoint_dir: Directory to save parquet files
    """

    if checkpoint_dir is None:
        checkpoint_dir = Path(f"/home/micha/bqx_ml_v3/data/features/checkpoints/{pair}")

    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"BigQuery Feature Extraction: {pair.upper()}")
    print(f"{'='*70}\n")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_V2}")
    print(f"Output: {checkpoint_dir}")
    print(f"Workers: {workers}")
    print(f"")

    # Get table list
    tables = get_table_list(pair)
    print(f"Tables to extract: {len(tables)}")

    # Check existing files
    existing = list(checkpoint_dir.glob("*.parquet"))
    print(f"Already extracted: {len(existing)}")
    print(f"Remaining: {len(tables) - len(existing)}")
    print(f"")

    # Prepare extraction tasks
    tasks = [(table, pair, checkpoint_dir) for table in tables]

    # Execute extraction in parallel
    start_time = datetime.now()
    results = {
        'success': [],
        'skipped': [],
        'empty': [],
        'error': []
    }

    print(f"Extracting with {workers} workers...")
    print(f"Progress updates every 50 tables\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(extract_table, task): task for task in tasks}

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            status = result['status']
            results[status].append(result)

            completed += 1

            # Progress logging every 50 tables
            if completed % 50 == 0 or completed == len(tables):
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = (len(tables) - completed) / rate if rate > 0 else 0

                print(f"  [{completed:4d}/{len(tables)}] "
                      f"Success: {len(results['success']):3d} | "
                      f"Skipped: {len(results['skipped']):3d} | "
                      f"Empty: {len(results['empty']):3d} | "
                      f"Error: {len(results['error']):3d} | "
                      f"Rate: {rate:5.1f}/s | "
                      f"ETA: {remaining/60:5.1f} min")

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\n{'='*70}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*70}\n")
    print(f"Total tables: {len(tables)}")
    print(f"Success: {len(results['success'])}")
    print(f"Skipped (existing): {len(results['skipped'])}")
    print(f"Empty: {len(results['empty'])}")
    print(f"Errors: {len(results['error'])}")
    print(f"Time: {elapsed/60:.1f} minutes")
    print(f"")

    # Show errors if any
    if results['error']:
        print(f"ERRORS ({len(results['error'])}):")
        for result in results['error'][:10]:  # Show first 10
            print(f"  - {result['table']}: {result['error']}")
        if len(results['error']) > 10:
            print(f"  ... and {len(results['error']) - 10} more")
        print(f"")

    # Verify final count
    final_count = len(list(checkpoint_dir.glob("*.parquet")))
    print(f"Final checkpoint files: {final_count}")

    if final_count >= 600:  # Should have 668 for complete extraction
        print(f"✅ EXTRACTION SUCCESSFUL")
        return True
    else:
        print(f"❌ EXTRACTION INCOMPLETE ({final_count}/668 files)")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract BigQuery features to parquet')
    parser.add_argument('pair', help='Currency pair (e.g., audusd)')
    parser.add_argument('--workers', type=int, default=25, help='Number of parallel workers')
    parser.add_argument('--checkpoint-dir', help='Checkpoint directory')

    args = parser.parse_args()

    checkpoint_dir = Path(args.checkpoint_dir) if args.checkpoint_dir else None

    success = extract_features(
        pair=args.pair.lower(),
        workers=args.workers,
        checkpoint_dir=checkpoint_dir
    )

    sys.exit(0 if success else 1)
