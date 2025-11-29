#!/usr/bin/env python3
"""
Expanded batch correlation calculator including polynomial regression features.
Processes features in table batches and stores results incrementally.

This script is prepared for the expanded feature set that includes:
- All existing features (817)
- New polynomial regression features (252):
  - reg_quad_term_{W}, reg_lin_term_{W}, reg_const_term_{W}
  - reg_quad_norm_{W}, reg_lin_norm_{W}
  - reg_r2_{W}, reg_rmse_{W}
  - reg_resid_std_{W}, reg_resid_last_{W}, reg_resid_skew_{W}, reg_resid_kurt_{W}
  - reg_acceleration_{W}, reg_trend_str_{W}, reg_forecast_5_{W}, reg_curv_sign_{W}

Usage:
  python3 batch_full_correlation_expanded.py [--include-polynomial] [--polynomial-only]

Author: Chief Engineer, BQX ML V3
Date: 2025-11-29
"""

import subprocess
import csv
import json
import sys
import time
import argparse

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features"
ANALYTICS_DATASET = "bqx_ml_v3_analytics"
TARGET_TABLE = "extreme_targets"
OUTPUT_TABLE = "full_correlation_matrix"
OUTPUT_TABLE_EXPANDED = "full_correlation_matrix_expanded"

WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# New polynomial regression columns to be added by BA
# Includes USER MANDATE v2.1 variance metrics from AirTable MP02.P16.S01
POLYNOMIAL_COLUMNS = [
    # Polynomial coefficients
    "reg_quad_term_{W}",
    "reg_lin_term_{W}",
    "reg_const_term_{W}",
    "reg_quad_norm_{W}",
    "reg_lin_norm_{W}",
    # Variance metrics (USER MANDATE v2.1 - AirTable MP02.P16.S01)
    "reg_resid_var_{W}",    # MSE = mean(residuals²)
    "reg_total_var_{W}",    # var(y)
    "reg_r2_{W}",           # 1 - (resid_var / total_var)
    "reg_rmse_{W}",         # sqrt(resid_var)
    "reg_resid_norm_{W}",   # residuals[-1] / mean(y)
    # Residual metrics
    "reg_resid_std_{W}",
    "reg_resid_min_{W}",
    "reg_resid_max_{W}",
    "reg_resid_last_{W}",
    "reg_resid_skew_{W}",
    "reg_resid_kurt_{W}",
    # Derived features
    "reg_curv_sign_{W}",
    "reg_acceleration_{W}",
    "reg_trend_str_{W}",
    "reg_forecast_5_{W}",
    "reg_ci_lower_{W}",
    "reg_ci_upper_{W}"
]

# Expand polynomial columns across all windows
def get_all_polynomial_columns():
    """Get list of all polynomial column names across all windows."""
    columns = []
    for template in POLYNOMIAL_COLUMNS:
        for w in WINDOWS:
            columns.append(template.format(W=w))
    return columns


def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        f = float(val)
        return default if f != f else f
    except:
        return default


def check_polynomial_features_exist():
    """Check if polynomial features have been implemented in reg_eurusd."""
    check_sql = """
    SELECT column_name
    FROM `bqx-ml.bqx_ml_v3_features.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'reg_eurusd'
      AND column_name LIKE 'reg_quad_term_%'
    LIMIT 1
    """
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", check_sql]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return False

    try:
        rows = json.loads(result.stdout)
        return len(rows) > 0
    except:
        return False


def load_feature_columns(include_polynomial=False, polynomial_only=False):
    """Load feature columns from the pre-generated CSV, optionally adding polynomial features."""
    features_by_table = {}

    if not polynomial_only:
        # Load existing features
        with open("/tmp/eurusd_feature_columns.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                table = row["table_name"]
                col = row["column_name"]
                if table not in features_by_table:
                    features_by_table[table] = []
                features_by_table[table].append(col)

    # Add polynomial features if requested
    if include_polynomial or polynomial_only:
        poly_columns = get_all_polynomial_columns()

        # Add to reg_ tables (IDX variant)
        pairs = [
            "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
            "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
            "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
            "audjpy", "audchf", "audcad", "audnzd",
            "nzdjpy", "nzdchf", "nzdcad",
            "cadjpy", "cadchf", "chfjpy"
        ]

        for pair in pairs:
            # IDX variant (reg_{pair})
            table_idx = f"reg_{pair}"
            if table_idx not in features_by_table:
                features_by_table[table_idx] = []
            for col in poly_columns:
                if col not in features_by_table[table_idx]:
                    features_by_table[table_idx].append(col)

            # BQX variant (reg_bqx_{pair})
            table_bqx = f"reg_bqx_{pair}"
            if table_bqx not in features_by_table:
                features_by_table[table_bqx] = []
            for col in poly_columns:
                if col not in features_by_table[table_bqx]:
                    features_by_table[table_bqx].append(col)

    return features_by_table


def generate_table_correlation_sql(table_name: str, columns: list):
    """Generate SQL for all columns in a table."""
    variant = "bqx" if "_bqx_" in table_name or table_name.endswith("_bqx") else "idx"

    union_parts = []
    for col in columns:
        feature_id = f"{table_name}.{col}"

        corr_cols = []
        for w in WINDOWS:
            for h in HORIZONS:
                corr_cols.append(f"CORR(CAST(f.{col} AS FLOAT64), t.delta_w{w}_h{h}) as corr_w{w}_h{h}")

        corr_sql = ",\n    ".join(corr_cols)

        sql = f"""
  SELECT
    '{feature_id}' as feature_id,
    '{table_name}' as source_table,
    '{col}' as column_name,
    '{variant}' as variant,
    COUNT(*) as n_samples,
    {corr_sql}
  FROM `{PROJECT}.{ANALYTICS_DATASET}.{TARGET_TABLE}` t
  JOIN `{PROJECT}.{FEATURES_DATASET}.{table_name}` f ON t.interval_time = f.interval_time
  WHERE f.{col} IS NOT NULL"""
        union_parts.append(sql)

    return "\nUNION ALL\n".join(union_parts)


def run_table_batch(table_name: str, columns: list, batch_num: int):
    """Run correlation for a single table and append results."""
    print(f"  Processing {table_name} ({len(columns)} features)...")

    sql = generate_table_correlation_sql(table_name, columns)

    # Write SQL to file
    sql_file = f"/tmp/corr_batch_{batch_num}.sql"
    with open(sql_file, "w") as f:
        f.write(sql)

    # Run query and get JSON results
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=500"]
    result = subprocess.run(cmd, stdin=open(sql_file), capture_output=True, text=True)

    if result.returncode != 0:
        print(f"    Error: {result.stderr[:200]}")
        return []

    try:
        rows = json.loads(result.stdout)
        print(f"    Got {len(rows)} results")
        return rows
    except json.JSONDecodeError:
        print(f"    JSON parse error")
        return []


def main():
    parser = argparse.ArgumentParser(description="Batch correlation calculator with polynomial support")
    parser.add_argument("--include-polynomial", action="store_true",
                       help="Include polynomial regression features in analysis")
    parser.add_argument("--polynomial-only", action="store_true",
                       help="Only analyze polynomial regression features")
    parser.add_argument("--check-polynomial", action="store_true",
                       help="Check if polynomial features exist and exit")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be processed without running")
    args = parser.parse_args()

    # Check if polynomial features exist
    if args.check_polynomial:
        exists = check_polynomial_features_exist()
        print(f"Polynomial features exist: {exists}")
        sys.exit(0 if exists else 1)

    # Determine if polynomial features are available
    poly_available = check_polynomial_features_exist()

    if (args.include_polynomial or args.polynomial_only) and not poly_available:
        print("WARNING: Polynomial features not yet implemented!")
        print("Run with --check-polynomial to verify status")
        print("BA implementation required first.")
        if not args.dry_run:
            sys.exit(1)

    print("Loading feature columns...")
    features_by_table = load_feature_columns(
        include_polynomial=args.include_polynomial or poly_available,
        polynomial_only=args.polynomial_only
    )
    total_features = sum(len(cols) for cols in features_by_table.values())
    print(f"Found {len(features_by_table)} tables with {total_features} total features")

    if args.include_polynomial or args.polynomial_only:
        poly_count = len(get_all_polynomial_columns()) * 2 * 28  # 2 variants * 28 pairs
        print(f"Including {poly_count} polynomial features across reg_ and reg_bqx_ tables")

    if args.dry_run:
        print("\nDry run - tables to process:")
        for table, cols in sorted(features_by_table.items()):
            print(f"  {table}: {len(cols)} columns")
        return

    all_results = []
    batch_num = 0

    for table_name, columns in features_by_table.items():
        results = run_table_batch(table_name, columns, batch_num)
        all_results.extend(results)
        batch_num += 1
        time.sleep(0.3)  # Rate limit

    print(f"\n=== Total: {len(all_results)} feature correlations ===")

    if not all_results:
        print("No results!")
        return

    # Build schema
    schema_parts = [
        "feature_id:STRING",
        "source_table:STRING",
        "column_name:STRING",
        "variant:STRING",
        "n_samples:INTEGER"
    ]
    for w in WINDOWS:
        for h in HORIZONS:
            schema_parts.append(f"corr_w{w}_h{h}:FLOAT")
    schema = ",".join(schema_parts)

    # Write JSONL
    print("\nWriting results...")
    output_file = "/tmp/full_correlations_expanded.jsonl"
    with open(output_file, "w") as f:
        for row in all_results:
            clean_row = {
                "feature_id": row.get("feature_id", ""),
                "source_table": row.get("source_table", ""),
                "column_name": row.get("column_name", ""),
                "variant": row.get("variant", ""),
                "n_samples": int(row.get("n_samples", 0))
            }
            for w in WINDOWS:
                for h in HORIZONS:
                    key = f"corr_w{w}_h{h}"
                    clean_row[key] = safe_float(row.get(key))
            f.write(json.dumps(clean_row) + "\n")

    # Determine output table
    output_table = OUTPUT_TABLE_EXPANDED if (args.include_polynomial or args.polynomial_only) else OUTPUT_TABLE

    # Load to BigQuery
    print(f"Loading to BigQuery ({output_table})...")
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--replace",
        f"{PROJECT}:{ANALYTICS_DATASET}.{output_table}",
        output_file,
        schema
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Success! Loaded to {ANALYTICS_DATASET}.{output_table}")
        print(f"Total features: {len(all_results)}")

        # Print summary by category
        poly_count = sum(1 for r in all_results if "quad_term" in r.get("column_name", "") or
                                                   "lin_term" in r.get("column_name", "") or
                                                   "r2_" in r.get("column_name", ""))
        existing_count = len(all_results) - poly_count
        print(f"  Existing features: {existing_count}")
        print(f"  Polynomial features: {poly_count}")
    else:
        print(f"Error: {result.stderr}")


if __name__ == "__main__":
    main()
