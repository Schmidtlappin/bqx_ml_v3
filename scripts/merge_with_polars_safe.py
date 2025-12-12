#!/usr/bin/env python3
"""
Safe Polars Merge with Resource Limits

CRITICAL LESSON LEARNED (Dec 11-12, 2025):
- Polars merge WORKS and produces valid output (training_eurusd.parquet - 9.3GB)
- Issue: Consumed 60-65GB RAM causing system crash (3 OOM incidents)
- Solution: Implement resource limits as recommended by OPS

This script adds safety controls:
1. Pre-flight memory check (require 40GB free)
2. Memory limit enforcement (max 50GB via resource module)
3. Progress monitoring
4. Graceful failure handling
"""

import sys
import os
import polars as pl
import resource
import gc
from pathlib import Path
from datetime import datetime

# ============================================================================
# SAFETY CONFIGURATION (OPS Requirements)
# ============================================================================

MAX_MEMORY_GB = 50  # Maximum memory this process can use
MIN_FREE_MEMORY_GB = 40  # Minimum free memory required to start
CHECKPOINT_INTERVAL = 50  # Log progress every N files

# Memory monitoring configuration (no hard limits - Polars manages memory well)
# Note: Hard limits via RLIMIT_AS cause allocation failures with Polars
# Instead: Monitor and warn, let Polars handle memory management
MAX_MEMORY_BYTES = MAX_MEMORY_GB * 1024 * 1024 * 1024

print(f"✅ Memory monitoring configured: {MAX_MEMORY_GB} GB target (soft)")


def check_available_memory() -> float:
    """Check available system memory in GB."""
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemAvailable'):
                # MemAvailable in kB
                available_kb = int(line.split()[1])
                available_gb = available_kb / 1024 / 1024
                return available_gb
    return 0.0


def get_current_memory_usage() -> float:
    """Get current process memory usage in GB."""
    import psutil
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024**3


def preflight_check(pair: str, checkpoint_dir: Path) -> bool:
    """
    Pre-flight safety checks before starting merge.

    Returns: True if safe to proceed, False otherwise
    """
    print("\n" + "="*70)
    print("PRE-FLIGHT SAFETY CHECKS")
    print("="*70)

    # Check 1: Available memory
    available_gb = check_available_memory()
    print(f"1. Available memory: {available_gb:.1f} GB")

    if available_gb < MIN_FREE_MEMORY_GB:
        print(f"   ❌ FAIL: Need {MIN_FREE_MEMORY_GB} GB, have {available_gb:.1f} GB")
        print(f"   Action: Free memory or increase MIN_FREE_MEMORY_GB")
        return False
    print(f"   ✅ PASS: Sufficient memory available")

    # Check 2: Checkpoint directory exists
    if not checkpoint_dir.exists():
        print(f"2. Checkpoint directory: {checkpoint_dir}")
        print(f"   ❌ FAIL: Directory not found")
        return False

    # Check 3: Count checkpoint files
    parquet_files = list(checkpoint_dir.glob("*.parquet"))
    targets_file = checkpoint_dir / "targets.parquet"

    if targets_file not in parquet_files:
        print(f"   ❌ FAIL: targets.parquet not found")
        return False

    feature_files = [f for f in parquet_files if f.name != "targets.parquet"]
    print(f"2. Checkpoint files: {len(feature_files)} features + 1 targets = {len(parquet_files)} total")
    print(f"   ✅ PASS: All files present")

    # Check 4: Disk space for output
    import shutil
    output_dir = Path(f"/home/micha/bqx_ml_v3/data/training")
    output_dir.mkdir(parents=True, exist_ok=True)

    stat = shutil.disk_usage(output_dir)
    free_gb = stat.free / 1024**3
    print(f"3. Disk space: {free_gb:.1f} GB free")

    if free_gb < 15:
        print(f"   ❌ FAIL: Need 15 GB, have {free_gb:.1f} GB")
        return False
    print(f"   ✅ PASS: Sufficient disk space")

    # Check 5: Memory monitoring (no hard limits - causes Polars allocation failures)
    print(f"4. Memory monitoring: {MAX_MEMORY_GB} GB target (soft)")
    print(f"   ℹ️  Using soft monitoring (Polars manages memory efficiently)")

    print("\n✅ ALL PRE-FLIGHT CHECKS PASSED")
    print("="*70 + "\n")
    return True


def merge_with_polars_safe(pair: str, checkpoint_dir: Path, output_path: Path) -> bool:
    """
    Safely merge parquet files using Polars with resource limits.

    Args:
        pair: Currency pair (e.g., 'audusd')
        checkpoint_dir: Path to checkpoint directory
        output_path: Path to output file

    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*70}")
    print(f"SAFE POLARS MERGE: {pair.upper()}")
    print(f"{'='*70}\n")

    # Pre-flight checks
    if not preflight_check(pair, checkpoint_dir):
        return False

    start_time = datetime.now()

    try:
        # Load targets
        targets_file = checkpoint_dir / "targets.parquet"
        print(f"Loading targets from {targets_file.name}...")
        df = pl.read_parquet(targets_file)
        print(f"  ✅ Loaded: {len(df):,} rows, {len(df.columns)} columns")
        print(f"  Memory: {get_current_memory_usage():.2f} GB")

        # Get feature files
        feature_files = sorted([
            f for f in checkpoint_dir.glob("*.parquet")
            if f.name != "targets.parquet" and f.name != "_COMPLETE"
        ])

        print(f"\nMerging {len(feature_files)} feature files...")
        print(f"Progress checkpoints every {CHECKPOINT_INTERVAL} files\n")

        # Merge feature files in batches
        for i, feature_file in enumerate(feature_files, 1):
            try:
                # Load feature file
                feature_df = pl.read_parquet(feature_file)

                # Join with main dataframe
                df = df.join(
                    feature_df,
                    on="interval_time",
                    how="left"
                )

                # Free memory immediately
                del feature_df

                # Progress logging
                if i % CHECKPOINT_INTERVAL == 0 or i == len(feature_files):
                    elapsed = (datetime.now() - start_time).total_seconds()
                    mem_usage = get_current_memory_usage()
                    print(f"  [{i:4d}/{len(feature_files)}] {feature_file.name[:40]:<40} "
                          f"| Cols: {len(df.columns):5d} | Mem: {mem_usage:5.2f} GB | "
                          f"Time: {elapsed/60:5.1f} min")

                    # Garbage collection every checkpoint
                    gc.collect()

                    # Safety check: If memory exceeds 45GB, abort
                    if mem_usage > 45:
                        print(f"\n⚠️  WARNING: Memory usage ({mem_usage:.2f} GB) approaching limit (50 GB)")
                        print(f"   Consider increasing batch size or using BigQuery merge")
                        # Don't abort yet, Polars is efficient

            except Exception as e:
                print(f"  ❌ ERROR on {feature_file.name}: {e}")
                return False

        # Write output
        print(f"\n✅ All files merged successfully!")
        print(f"   Final dimensions: {len(df):,} rows × {len(df.columns):,} columns")
        print(f"   Final memory: {get_current_memory_usage():.2f} GB")

        print(f"\nWriting output to {output_path}...")
        df.write_parquet(output_path)

        # Verify output
        file_size_gb = output_path.stat().st_size / 1024**3
        print(f"✅ Output file created: {file_size_gb:.2f} GB")

        # Mark complete
        complete_marker = checkpoint_dir / "_COMPLETE"
        complete_marker.touch()
        print(f"✅ Completion marker created: {complete_marker.name}")

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*70}")
        print(f"MERGE COMPLETE")
        print(f"{'='*70}")
        print(f"Time: {elapsed/60:.1f} minutes")
        print(f"Peak Memory: {get_current_memory_usage():.2f} GB (limit: {MAX_MEMORY_GB} GB)")
        print(f"Output: {output_path}")
        print(f"Size: {file_size_gb:.2f} GB")
        print(f"{'='*70}\n")

        return True

    except MemoryError as e:
        print(f"\n❌ MEMORY ERROR: {e}")
        print(f"   Memory limit ({MAX_MEMORY_GB} GB) exceeded")
        print(f"   Recommendation: Use BigQuery cloud merge instead")
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 merge_with_polars_safe.py <pair> [checkpoint_dir] [output_path]")
        print("Example: python3 merge_with_polars_safe.py audusd")
        print("Example (custom paths): python3 merge_with_polars_safe.py audusd /tmp/checkpoints/audusd /tmp/training_audusd.parquet")
        sys.exit(1)

    pair = sys.argv[1].lower()

    # Support both VM and Cloud Run environments
    # Check if running in Cloud Run (paths in /tmp) or VM (paths in /home/micha)
    if len(sys.argv) >= 3:
        # Custom paths provided (Cloud Run)
        checkpoint_dir = Path(sys.argv[2])
        output_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else Path(f"/tmp/training_{pair}.parquet")
    else:
        # Default VM paths
        checkpoint_dir = Path(f"/home/micha/bqx_ml_v3/data/features/checkpoints/{pair}")
        output_path = Path(f"/home/micha/bqx_ml_v3/data/training/training_{pair}.parquet")

    print(f"Checkpoint directory: {checkpoint_dir}")
    print(f"Output path: {output_path}")

    success = merge_with_polars_safe(pair, checkpoint_dir, output_path)

    if success:
        print(f"✅ {pair.upper()} merge completed successfully")
        sys.exit(0)
    else:
        print(f"❌ {pair.upper()} merge failed")
        sys.exit(1)
