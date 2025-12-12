#!/usr/bin/env python3
"""
Polars-based merge function for checkpoint parquet files.
Replaces DuckDB approach which failed with OOM.

EA Specification - December 11, 2025
"""

import polars as pl
from pathlib import Path
import sys


def merge_checkpoints_polars(checkpoint_dir: str, output_path: str):
    """
    Merge all checkpoint parquet files using Polars lazy evaluation.

    Args:
        checkpoint_dir: Directory containing checkpoint parquet files
        output_path: Path for merged output parquet file

    Returns:
        polars.DataFrame: Merged dataframe
    """
    checkpoint_path = Path(checkpoint_dir)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint directory not found: {checkpoint_dir}")

    # Get all parquet files
    all_files = sorted(checkpoint_path.glob("*.parquet"))

    if len(all_files) == 0:
        raise FileNotFoundError(f"No parquet files found in {checkpoint_dir}")

    print(f"Found {len(all_files)} parquet files in {checkpoint_dir}")

    # Lazy scan targets (must be first)
    target_file = checkpoint_path / "targets.parquet"

    if not target_file.exists():
        raise FileNotFoundError(f"targets.parquet not found in {checkpoint_dir}")

    print("Lazy loading targets.parquet...")
    result_lf = pl.scan_parquet(target_file)

    # Count joins
    join_count = 0

    # Lazy scan and join all feature files
    for pq_file in all_files:
        if pq_file.name == "targets.parquet":
            continue  # Already loaded

        print(f"  Joining {pq_file.name}...", flush=True)

        try:
            feature_lf = pl.scan_parquet(pq_file)
            result_lf = result_lf.join(
                feature_lf,
                on='interval_time',
                how='left'
            )
            join_count += 1

            if join_count % 100 == 0:
                print(f"    Progress: {join_count}/{len(all_files)-1} files joined")

        except Exception as e:
            print(f"ERROR joining {pq_file.name}: {e}")
            raise

    print(f"Lazy query plan built with {join_count} joins")
    print("Executing optimized query plan (this may take 8-20 minutes)...")
    print("Memory usage will be monitored - expect ~20-30GB peak")

    # Execute optimized plan
    try:
        result_df = result_lf.collect()
    except Exception as e:
        print(f"ERROR during query execution: {e}")
        print("This likely indicates OOM or data issue")
        raise

    # Validate result
    row_count = len(result_df)
    col_count = len(result_df.columns)

    print(f"\nMerge complete!")
    print(f"  Rows: {row_count:,}")
    print(f"  Columns: {col_count:,}")

    # Check for targets
    target_cols = [c for c in result_df.columns if c.startswith('target_')]
    print(f"  Target columns: {len(target_cols)}")

    # Write output
    print(f"\nWriting to {output_path}...")
    result_df.write_parquet(output_path)

    # Get output file size
    output_size = Path(output_path).stat().st_size / (1024**3)  # GB
    print(f"Output file size: {output_size:.2f} GB")

    return result_df


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python merge_with_polars.py <checkpoint_dir> <output_path>")
        print("Example: python merge_with_polars.py data/features/checkpoints/eurusd data/training/training_eurusd.parquet")
        sys.exit(1)

    checkpoint_dir = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Polars Merge Tool")
    print(f"Checkpoint dir: {checkpoint_dir}")
    print(f"Output path: {output_path}")
    print("")

    try:
        df = merge_checkpoints_polars(checkpoint_dir, output_path)
        print("\n✅ SUCCESS - Merge completed")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
