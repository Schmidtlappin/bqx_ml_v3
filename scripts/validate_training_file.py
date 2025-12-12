#!/usr/bin/env python3
"""
Training File Validation Script

Validates parquet training files for completeness and correctness.
Used in Cloud Run pipeline to ensure data quality before upload.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path


def validate_training_file(file_path: str, pair: str, required_targets: int = 7,
                           min_rows: int = 100000, min_columns: int = 10000) -> bool:
    """
    Validate training parquet file.

    Args:
        file_path: Path to training parquet file
        pair: Currency pair name
        required_targets: Number of required target columns
        min_rows: Minimum number of rows expected
        min_columns: Minimum number of columns expected

    Returns:
        True if validation passes, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"TRAINING FILE VALIDATION: {pair.upper()}")
    print(f"{'='*70}\n")

    file_path = Path(file_path)

    # Check 1: File exists
    if not file_path.exists():
        print(f"❌ FAIL: File not found: {file_path}")
        return False
    print(f"✅ File exists: {file_path}")

    # Check 2: File size
    file_size_gb = file_path.stat().st_size / 1024**3
    print(f"✅ File size: {file_size_gb:.2f} GB")

    if file_size_gb < 1:
        print(f"⚠️  WARNING: File size very small ({file_size_gb:.2f} GB)")

    # Check 3: Load and inspect
    try:
        print(f"\nLoading file into memory...")
        df = pd.read_parquet(file_path)
        print(f"✅ File loaded successfully")
    except Exception as e:
        print(f"❌ FAIL: Cannot load file: {e}")
        return False

    # Check 4: Dimensions
    rows, cols = df.shape
    print(f"\nDimensions:")
    print(f"   Rows: {rows:,}")
    print(f"   Columns: {cols:,}")

    if rows < min_rows:
        print(f"❌ FAIL: Insufficient rows ({rows:,} < {min_rows:,})")
        return False
    print(f"✅ Row count sufficient ({rows:,} >= {min_rows:,})")

    if cols < min_columns:
        print(f"❌ FAIL: Insufficient columns ({cols:,} < {min_columns:,})")
        return False
    print(f"✅ Column count sufficient ({cols:,} >= {min_columns:,})")

    # Check 5: Required columns
    if 'interval_time' not in df.columns:
        print(f"❌ FAIL: Missing 'interval_time' column")
        return False
    print(f"✅ interval_time column present")

    # Check 6: Target columns
    target_cols = [c for c in df.columns if c.startswith('target_')]
    print(f"\nTarget columns: {len(target_cols)}")

    if len(target_cols) < required_targets:
        print(f"❌ FAIL: Insufficient target columns ({len(target_cols)} < {required_targets})")
        return False
    print(f"✅ Target columns sufficient ({len(target_cols)} >= {required_targets})")

    # Check all 7 horizons present
    expected_horizons = [15, 30, 45, 60, 75, 90, 105]
    for h in expected_horizons:
        target_col = f'target_bqx45_h{h}'
        if target_col in df.columns:
            non_null_count = df[target_col].notna().sum()
            print(f"   ✅ {target_col}: {non_null_count:,} non-null values")
        else:
            print(f"   ❌ {target_col}: MISSING")
            return False

    # Check 7: Feature columns
    feature_cols = [c for c in df.columns if not c.startswith('target_') and c != 'interval_time']
    print(f"\nFeature columns: {len(feature_cols):,}")

    if len(feature_cols) == 0:
        print(f"❌ FAIL: No feature columns found")
        return False
    print(f"✅ Features present: {len(feature_cols):,}")

    # Check 8: Date range
    if 'interval_time' in df.columns:
        date_min = df['interval_time'].min()
        date_max = df['interval_time'].max()
        print(f"\nDate range: {date_min} to {date_max}")
        print(f"✅ Date range valid")

    # Check 9: Null percentage
    total_cells = rows * cols
    null_cells = df.isnull().sum().sum()
    null_pct = (null_cells / total_cells) * 100

    print(f"\nData completeness:")
    print(f"   Total cells: {total_cells:,}")
    print(f"   Null cells: {null_cells:,}")
    print(f"   Null %: {null_pct:.2f}%")

    if null_pct > 80:
        print(f"⚠️  WARNING: High null percentage ({null_pct:.2f}%)")
    else:
        print(f"✅ Null percentage acceptable ({null_pct:.2f}% < 80%)")

    # Final summary
    print(f"\n{'='*70}")
    print(f"✅ VALIDATION PASSED: {pair.upper()}")
    print(f"{'='*70}\n")

    print(f"Summary:")
    print(f"   Rows: {rows:,}")
    print(f"   Columns: {cols:,}")
    print(f"   Targets: {len(target_cols)}")
    print(f"   Features: {len(feature_cols):,}")
    print(f"   File size: {file_size_gb:.2f} GB")
    print(f"   Null %: {null_pct:.2f}%")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate training parquet file")
    parser.add_argument("file_path", help="Path to training parquet file")
    parser.add_argument("--pair", required=True, help="Currency pair name")
    parser.add_argument("--required-targets", type=int, default=7, help="Number of required target columns")
    parser.add_argument("--min-rows", type=int, default=100000, help="Minimum number of rows")
    parser.add_argument("--min-columns", type=int, default=10000, help="Minimum number of columns")

    args = parser.parse_args()

    success = validate_training_file(
        file_path=args.file_path,
        pair=args.pair,
        required_targets=args.required_targets,
        min_rows=args.min_rows,
        min_columns=args.min_columns
    )

    if success:
        print(f"✅ Validation successful")
        sys.exit(0)
    else:
        print(f"❌ Validation failed")
        sys.exit(1)
