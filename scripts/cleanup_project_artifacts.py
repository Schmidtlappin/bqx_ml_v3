#!/usr/bin/env python3
"""
Cleanup script for BQX ML V3 project artifacts
Provides options for cleaning up various project components
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Execute a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def cleanup_processes():
    """Kill any lingering background processes"""
    print("\n🔄 Cleaning up background processes...")

    processes = [
        "elevate_tasks",
        "execute_remaining",
        "execute_with_outcomes",
        "generate_meaningful",
        "reset_project"
    ]

    for proc in processes:
        cmd = f"pkill -f {proc} 2>/dev/null"
        run_command(cmd)

    print("  ✅ Background processes cleaned")

def cleanup_bigquery(dry_run=True):
    """Clean up BigQuery artifacts"""
    print("\n🔍 Analyzing BigQuery datasets...")

    datasets = {
        'bqx_ml_v3_staging': 'Temporary staging data (can be cleared)',
        'bqx_ml_v3_predictions': 'Prediction outputs (can be cleared)',
        'bqx_ml_v3_models': 'Training datasets (KEEP for production)',
        'bqx_ml_v3_features': 'Feature tables (KEEP for production)',
        'bqx_ml_v3_analytics': 'Analytics views (KEEP for monitoring)'
    }

    print("\n  BigQuery Datasets:")
    for dataset, description in datasets.items():
        success, stdout, _ = run_command(f"bq ls -d --project_id=bqx-ml {dataset} 2>/dev/null")
        if success:
            print(f"  ✅ {dataset}: {description}")

    # Check for temporary or test tables
    print("\n  Checking for temporary tables...")
    temp_tables = []

    # Check staging dataset for temp tables
    success, stdout, _ = run_command("bq ls --max_results=1000 bqx-ml:bqx_ml_v3_staging 2>/dev/null | grep -E 'temp_|test_|tmp_'")
    if success and stdout:
        temp_tables.extend(stdout.strip().split('\n'))

    if temp_tables:
        print(f"  ⚠️  Found {len(temp_tables)} temporary tables")
        if not dry_run:
            for table in temp_tables:
                table_name = table.split()[0]
                cmd = f"bq rm -f -t bqx-ml:bqx_ml_v3_staging.{table_name}"
                success, _, _ = run_command(cmd)
                if success:
                    print(f"    ✅ Deleted: {table_name}")
    else:
        print("  ✅ No temporary tables found")

    # Check data freshness
    print("\n  Checking data volumes...")
    for pair in ['eurusd', 'gbpusd']:
        for suffix in ['idx', 'bqx']:
            table = f"bqx-ml:bqx_ml_v3_features.{pair}_{suffix}"
            cmd = f"bq query --use_legacy_sql=false 'SELECT COUNT(*) as count FROM `{table}`' 2>/dev/null"
            success, stdout, _ = run_command(cmd)
            if success and 'count' in stdout:
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('+') and not line.startswith('|') and 'count' not in line:
                        count = line.strip()
                        status = "✅" if int(count) > 0 else "❌"
                        print(f"    {status} {pair}_{suffix}: {count} rows")
                        break

def cleanup_local_artifacts():
    """Clean up local temporary files and artifacts"""
    print("\n🧹 Cleaning local artifacts...")

    # Patterns to clean
    cleanup_patterns = [
        "scripts/test_*.py",
        "scripts/temp_*.py",
        "scripts/tmp_*.py",
        "scripts/*_simulation.py",
        "scripts/*_fake_*.py",
        "*.log",
        "*.tmp",
        ".claude/sandbox/*.tmp"
    ]

    removed_count = 0
    for pattern in cleanup_patterns:
        cmd = f"find . -name '{pattern}' -type f 2>/dev/null"
        success, stdout, _ = run_command(cmd)
        if success and stdout:
            files = stdout.strip().split('\n')
            for file in files:
                if file and os.path.exists(file):
                    try:
                        os.remove(file)
                        removed_count += 1
                        print(f"  ✅ Removed: {file}")
                    except Exception as e:
                        print(f"  ❌ Failed to remove {file}: {e}")

    if removed_count == 0:
        print("  ✅ No temporary files to clean")
    else:
        print(f"  ✅ Removed {removed_count} temporary files")

def generate_summary():
    """Generate a summary of what needs attention"""
    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)

    recommendations = []

    # Check if synthetic data needs refreshing (BA's 50K row update)
    cmd = "bq query --use_legacy_sql=false 'SELECT COUNT(*) as count FROM `bqx-ml.bqx_ml_v3_features.eurusd_idx`' 2>/dev/null"
    success, stdout, _ = run_command(cmd)
    if success and 'count' in stdout:
        lines = stdout.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('+') and not line.startswith('|') and 'count' not in line:
                count = int(line.strip())
                if count < 50000:
                    recommendations.append(f"⚠️  EURUSD data has only {count:,} rows (need 50,000)")
                else:
                    recommendations.append(f"✅ EURUSD data has {count:,} rows (sufficient)")
                break

    # Check for model artifacts
    cmd = "ls -la models/*.pkl models/*.joblib 2>/dev/null | wc -l"
    success, stdout, _ = run_command(cmd)
    if success:
        model_count = int(stdout.strip())
        if model_count > 0:
            recommendations.append(f"📦 Found {model_count} saved model files")

    # BigQuery recommendations
    recommendations.append("\n📊 BigQuery Status:")
    recommendations.append("  • bqx_ml_v3_features: KEEP (contains IDX/BQX data)")
    recommendations.append("  • bqx_ml_v3_models: KEEP (training datasets)")
    recommendations.append("  • bqx_ml_v3_staging: SAFE TO CLEAR (temporary)")
    recommendations.append("  • bqx_ml_v3_predictions: SAFE TO CLEAR (outputs)")
    recommendations.append("  • bqx_ml_v3_analytics: KEEP (monitoring views)")

    print("\n".join(recommendations))

def main():
    print("="*60)
    print("BQX ML V3 PROJECT CLEANUP")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Parse arguments
    dry_run = '--execute' not in sys.argv

    if dry_run:
        print("\n🔍 DRY RUN MODE (use --execute to perform cleanup)")
    else:
        print("\n⚠️  EXECUTE MODE - Will perform actual cleanup!")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Run cleanup tasks
    cleanup_processes()
    cleanup_local_artifacts()
    cleanup_bigquery(dry_run)

    # Generate summary
    generate_summary()

    print("\n✅ Cleanup analysis complete!")

    if dry_run:
        print("\nTo execute cleanup, run:")
        print("  python3 scripts/cleanup_project_artifacts.py --execute")

if __name__ == "__main__":
    main()