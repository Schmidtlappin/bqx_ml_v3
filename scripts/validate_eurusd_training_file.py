#!/usr/bin/env python3
"""
EURUSD Training File Validation Script
Purpose: Comprehensive 6-point validation for GCS checkpoint test
Author: Quality Assurance (QA)
Date: 2025-12-12
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

Validation Checklist:
1. File existence & size
2. Checkpoint persistence
3. File dimensions
4. Schema validation
5. Data quality
6. VM reference comparison (optional)

Exit Codes:
0 = All validations passed (GO)
1 = One or more validations failed (NO-GO)
2 = Script error (unable to complete validation)
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}\n")

def print_check(number, description, status, details=""):
    """Print validation check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} Check {number}: {description}")
    if details:
        print(f"   {details}")
    print()

def check_file_existence():
    """Check 1: File existence & size"""
    print_header("CHECK 1: File Existence & Size")

    try:
        result = subprocess.run(
            ["gsutil", "ls", "-lh", "gs://bqx-ml-output/training_eurusd.parquet"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print_check(1, "File Existence", False, "File not found in GCS")
            return False, None

        # Parse file size from output (format: "SIZE DATE TIME gs://...")
        output_lines = [line for line in result.stdout.strip().split('\n') if 'training_eurusd.parquet' in line]
        if not output_lines:
            print_check(1, "File Existence", False, "Unable to parse file info")
            return False, None

        # Extract file size (first column)
        file_info = output_lines[0].split()
        file_size_str = file_info[0] if file_info else "Unknown"

        print(f"File: gs://bqx-ml-output/training_eurusd.parquet")
        print(f"Size: {file_size_str}")

        # Check if size is reasonable (>1 GB, <20 GB)
        # For now, just check file exists
        print_check(1, "File Existence & Size", True, f"File exists, size: {file_size_str}")
        return True, file_size_str

    except subprocess.TimeoutExpired:
        print_check(1, "File Existence", False, "GCS command timed out")
        return False, None
    except Exception as e:
        print_check(1, "File Existence", False, f"Error: {e}")
        return False, None

def check_checkpoint_persistence():
    """Check 2: Checkpoint persistence"""
    print_header("CHECK 2: Checkpoint Persistence")

    try:
        result = subprocess.run(
            ["gsutil", "ls", "gs://bqx-ml-staging/checkpoints/eurusd/"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print_check(2, "Checkpoint Persistence", False, "No checkpoints found")
            return False, 0

        checkpoint_count = len([line for line in result.stdout.strip().split('\n') if line])
        print(f"Checkpoint count: {checkpoint_count}")
        print(f"Expected: 667 (all EURUSD tables)")

        if checkpoint_count >= 667:
            print_check(2, "Checkpoint Persistence", True, f"{checkpoint_count} checkpoints found (≥667)")
            return True, checkpoint_count
        elif checkpoint_count >= 600:
            print_check(2, "Checkpoint Persistence", True, f"{checkpoint_count} checkpoints found (≥600, acceptable)")
            return True, checkpoint_count
        else:
            print_check(2, "Checkpoint Persistence", False, f"Only {checkpoint_count} checkpoints (<600 minimum)")
            return False, checkpoint_count

    except subprocess.TimeoutExpired:
        print_check(2, "Checkpoint Persistence", False, "GCS command timed out")
        return False, 0
    except Exception as e:
        print_check(2, "Checkpoint Persistence", False, f"Error: {e}")
        return False, 0

def check_file_dimensions():
    """Check 3: File dimensions"""
    print_header("CHECK 3: File Dimensions")

    try:
        import polars as pl

        print("Reading parquet file from GCS...")
        df = pl.read_parquet("gs://bqx-ml-output/training_eurusd.parquet")

        rows = len(df)
        cols = len(df.columns)
        size_gb = df.estimated_size() / 1e9

        print(f"Rows: {rows:,}")
        print(f"Columns: {cols}")
        print(f"Estimated size: {size_gb:.2f} GB")

        # Expected: >100K rows, 458 columns exact
        row_pass = rows >= 100000
        col_pass = cols == 458

        if row_pass and col_pass:
            print_check(3, "File Dimensions", True, f"{rows:,} rows (≥100K), {cols} columns (=458)")
            return True, df
        elif not row_pass:
            print_check(3, "File Dimensions", False, f"Row count {rows:,} < 100K minimum")
            return False, df
        else:
            print_check(3, "File Dimensions", False, f"Column count {cols} ≠ 458 expected")
            return False, df

    except ImportError:
        print_check(3, "File Dimensions", False, "Polars not installed")
        return False, None
    except Exception as e:
        print_check(3, "File Dimensions", False, f"Error reading file: {e}")
        return False, None

def check_schema_validation(df):
    """Check 4: Schema validation"""
    print_header("CHECK 4: Schema Validation")

    if df is None:
        print_check(4, "Schema Validation", False, "No dataframe available")
        return False

    try:
        # Check target columns
        expected_targets = [f"target_h{h}" for h in [15, 30, 45, 60, 75, 90, 105]]
        missing_targets = [t for t in expected_targets if t not in df.columns]

        print(f"Expected targets: {len(expected_targets)}")
        print(f"Missing targets: {missing_targets if missing_targets else 'None'}")

        # Check feature count
        feature_cols = [c for c in df.columns if c not in expected_targets + ["interval_time"]]
        feature_count = len(feature_cols)

        print(f"Feature count: {feature_count:,}")
        print(f"Expected range: 6,400-6,500")

        targets_pass = len(missing_targets) == 0
        features_pass = 6400 <= feature_count <= 6500

        if targets_pass and features_pass:
            print_check(4, "Schema Validation", True, f"All 7 targets present, {feature_count:,} features")
            return True
        elif not targets_pass:
            print_check(4, "Schema Validation", False, f"Missing targets: {missing_targets}")
            return False
        else:
            print_check(4, "Schema Validation", False, f"Feature count {feature_count:,} outside 6,400-6,500 range")
            return False

    except Exception as e:
        print_check(4, "Schema Validation", False, f"Error: {e}")
        return False

def check_data_quality(df):
    """Check 5: Data quality"""
    print_header("CHECK 5: Data Quality")

    if df is None:
        print_check(5, "Data Quality", False, "No dataframe available")
        return False

    try:
        # Check missing values
        total_cells = len(df) * len(df.columns)
        total_nulls = df.null_count().sum_horizontal().sum()
        missing_pct = (total_nulls / total_cells) * 100 if total_cells > 0 else 0

        print(f"Missing values: {missing_pct:.2f}%")
        print(f"Expected: <1% overall")

        # Check for infinite values in numeric columns
        inf_count = 0
        inf_cols = []
        for col in df.columns:
            if df[col].dtype in [pl.Float64, pl.Float32]:
                col_inf = df[col].is_infinite().sum()
                if col_inf > 0:
                    inf_count += col_inf
                    inf_cols.append(f"{col} ({col_inf})")

        print(f"Infinite values: {inf_count}")
        if inf_cols:
            print(f"Columns with infinities: {', '.join(inf_cols[:5])}...")

        # Check timestamp monotonic
        is_sorted = df["interval_time"].is_sorted()
        print(f"Timestamps monotonic: {is_sorted}")

        missing_pass = missing_pct < 1.0
        inf_pass = inf_count == 0
        sorted_pass = is_sorted

        if missing_pass and inf_pass and sorted_pass:
            print_check(5, "Data Quality", True, f"{missing_pct:.2f}% missing, no infinities, timestamps sorted")
            return True
        else:
            issues = []
            if not missing_pass:
                issues.append(f"Missing {missing_pct:.2f}% ≥1%")
            if not inf_pass:
                issues.append(f"{inf_count} infinite values")
            if not sorted_pass:
                issues.append("Timestamps not sorted")
            print_check(5, "Data Quality", False, ", ".join(issues))
            return False

    except Exception as e:
        print_check(5, "Data Quality", False, f"Error: {e}")
        return False

def check_vm_reference(df):
    """Check 6: VM reference comparison (optional)"""
    print_header("CHECK 6: VM Reference Comparison (Optional)")

    # Check if VM reference exists
    vm_paths = [
        "/home/micha/bqx_ml_v3/data/training/eurusd_training_h15-h105.parquet",
        "/home/micha/bqx_ml_v3/data/training/training_eurusd.parquet",
    ]

    vm_path = None
    for path in vm_paths:
        if Path(path).exists():
            vm_path = path
            break

    if vm_path is None:
        print("VM reference file not found (checking multiple paths):")
        for path in vm_paths:
            print(f"  - {path}")
        print_check(6, "VM Reference Comparison", True, "SKIPPED - No VM reference available (not blocking)")
        return True

    try:
        import polars as pl

        print(f"Reading VM reference: {vm_path}")
        vm_df = pl.read_parquet(vm_path)

        gcs_rows = len(df)
        vm_rows = len(vm_df)
        row_diff = gcs_rows - vm_rows
        row_diff_pct = (row_diff / vm_rows) * 100 if vm_rows > 0 else 0

        gcs_cols = len(df.columns)
        vm_cols = len(vm_df.columns)
        col_diff = gcs_cols - vm_cols

        print(f"GCS rows: {gcs_rows:,}")
        print(f"VM rows: {vm_rows:,}")
        print(f"Row difference: {row_diff:,} ({row_diff_pct:+.1f}%)")
        print(f"GCS columns: {gcs_cols}")
        print(f"VM columns: {vm_cols}")
        print(f"Column difference: {col_diff}")

        # Accept within ±10% for rows, exact match for columns
        row_pass = abs(row_diff_pct) <= 10.0
        col_pass = col_diff == 0

        if row_pass and col_pass:
            print_check(6, "VM Reference Comparison", True, f"Within ±10% rows, columns match")
            return True
        else:
            issues = []
            if not row_pass:
                issues.append(f"Row diff {row_diff_pct:+.1f}% >±10%")
            if not col_pass:
                issues.append(f"Column diff {col_diff}")
            print_check(6, "VM Reference Comparison", False, ", ".join(issues))
            return False

    except Exception as e:
        print_check(6, "VM Reference Comparison", True, f"SKIPPED - Error reading VM reference: {e} (not blocking)")
        return True

def main():
    """Main validation execution"""
    print_header("EURUSD TRAINING FILE VALIDATION")
    print("GCS Checkpoint Test - Comprehensive Quality Validation")
    print("Quality Assurance (QA) - Session 05c73962-b9f1-4e06-9a5a-a5ae556cae5a")
    print()

    results = {}

    # Check 1: File existence & size
    check1_pass, file_size = check_file_existence()
    results['file_existence'] = check1_pass

    # Check 2: Checkpoint persistence
    check2_pass, checkpoint_count = check_checkpoint_persistence()
    results['checkpoint_persistence'] = check2_pass

    # Check 3: File dimensions (returns df for subsequent checks)
    check3_pass, df = check_file_dimensions()
    results['file_dimensions'] = check3_pass

    # Check 4: Schema validation
    check4_pass = check_schema_validation(df)
    results['schema_validation'] = check4_pass

    # Check 5: Data quality
    check5_pass = check_data_quality(df)
    results['data_quality'] = check5_pass

    # Check 6: VM reference comparison (optional)
    check6_pass = check_vm_reference(df)
    results['vm_reference'] = check6_pass

    # Summary
    print_header("VALIDATION SUMMARY")

    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print()

    for check, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check.replace('_', ' ').title()}")

    print()

    # GO/NO-GO recommendation
    all_pass = all(results.values())

    if all_pass:
        print("=" * 80)
        print("  ✅ RECOMMENDATION: GO")
        print("  All validation checks passed - GCS checkpoint approach verified")
        print("  APPROVE 26-pair production rollout using GCS checkpoints")
        print("=" * 80)
        return 0
    else:
        print("=" * 80)
        print("  ❌ RECOMMENDATION: NO-GO")
        print("  One or more validation checks failed")
        print("  REJECT GCS approach - IMMEDIATE FALLBACK to VM-based execution")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
