#!/usr/bin/env python3
"""
Full 49-correlation calculator for all features.
Calculates correlation for ALL 7 windows × 7 horizons combinations.
"""

import subprocess
import json
import sys
from typing import Dict, List

PROJECT = "bqx-ml"

# All BQX windows and horizons
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Feature tables and their columns (from previous analysis)
FEATURE_TABLES = {
    "eurusd_bqx": ["bqx_45", "bqx_90", "bqx_180", "bqx_360", "bqx_720", "bqx_1440", "bqx_2880"],
    "eurusd_idx": ["idx_45", "idx_90", "idx_180", "idx_360", "idx_720"],
    "agg_eurusd": ["sma_45", "sma_90", "sma_180", "sma_360", "sma_720", "ema_45", "ema_90", "ema_180", "ema_360", "ema_720", "wma_45", "wma_90", "wma_180", "wma_360", "wma_720"],
    "agg_bqx_eurusd": ["mean_45", "mean_90", "mean_180", "mean_360", "mean_720", "mean_1440", "mean_2880", "median_45", "median_90", "median_180", "median_360", "median_720", "median_1440", "median_2880"],
    "reg_eurusd": ["slope_45", "slope_90", "slope_180", "slope_360", "slope_720", "deviation_45", "deviation_90", "deviation_180", "deviation_360", "deviation_720", "r2_45", "r2_90", "r2_180", "r2_360", "r2_720"],
    "reg_bqx_eurusd": ["slope_45", "slope_90", "slope_180", "slope_360", "slope_720", "slope_1440", "slope_2880", "deviation_45", "deviation_90", "deviation_180", "deviation_360", "deviation_720", "deviation_1440", "deviation_2880"],
    "mom_eurusd": ["roc_45", "roc_90", "roc_180", "roc_360", "roc_720", "diff_45", "diff_90", "diff_180", "diff_360", "diff_720"],
    "mom_bqx_eurusd": ["roc_45", "roc_90", "roc_180", "roc_360", "roc_720", "roc_1440", "roc_2880", "diff_45", "diff_90", "diff_180", "diff_360", "diff_720", "diff_1440", "diff_2880"],
    "vol_eurusd": ["realized_45", "realized_90", "realized_180", "realized_360", "realized_720", "atr_45", "atr_90", "atr_180", "atr_360", "atr_720"],
    "vol_bqx_eurusd": ["realized_45", "realized_90", "realized_180", "realized_360", "realized_720", "realized_1440", "realized_2880", "std_45", "std_90", "std_180", "std_360", "std_720", "std_1440", "std_2880"],
    "der_eurusd": ["v1_45", "v1_90", "v1_180", "v1_360", "v1_720", "v2_45", "v2_90", "v2_180", "v2_360", "v2_720"],
    "der_bqx_eurusd": ["v1_45", "v1_90", "v1_180", "v1_360", "v1_720", "v2_45", "v2_90", "v2_180", "v2_360", "v2_720"],
    "align_eurusd": ["zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "pctile_45", "pctile_90", "pctile_180", "pctile_360", "pctile_720"],
    "align_bqx_eurusd": ["zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440", "zscore_2880", "pctile_45", "pctile_90", "pctile_180", "pctile_360", "pctile_720", "pctile_1440", "pctile_2880"],
    "ext_bqx_eurusd": ["zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440", "zscore_2880", "pctile_45", "pctile_90", "pctile_180", "pctile_360", "pctile_720", "pctile_1440", "pctile_2880"],
    "mrt_eurusd": ["tension_45", "tension_90", "tension_180", "tension_360", "tension_720"],
    "mrt_bqx_eurusd": ["tension_45", "tension_90", "tension_180", "tension_360", "tension_720", "tension_1440", "tension_2880"],
    "rev_eurusd": ["strength_45", "strength_90", "strength_180", "strength_360", "strength_720"],
    "rev_bqx_eurusd": ["strength_45", "strength_90", "strength_180", "strength_360", "strength_720", "strength_1440", "strength_2880"],
    "div_eurusd": ["div_45", "div_90", "div_180", "div_360", "div_720"],
    "div_bqx_eurusd": ["div_45", "div_90", "div_180", "div_360", "div_720", "div_1440", "div_2880"],
}


def safe_float(val, default=0.0):
    """Convert to float safely, handling NaN and None."""
    if val is None:
        return default
    try:
        f = float(val)
        if f != f:  # NaN check
            return default
        return f
    except (ValueError, TypeError):
        return default


def generate_full_correlation_sql(table_name: str, features: list) -> str:
    """Generate SQL for all 49 correlations for each feature."""
    variant = "bqx" if "_bqx_" in table_name or table_name.endswith("_bqx") else "idx"

    union_parts = []
    for feature in features:
        feature_id = f"{variant}_{feature}"

        # Build all 49 correlation columns
        corr_columns = []
        for w in WINDOWS:
            for h in HORIZONS:
                corr_columns.append(f"CORR(CAST(f.{feature} AS FLOAT64), t.delta_w{w}_h{h}) as corr_w{w}_h{h}")

        corr_sql = ",\n      ".join(corr_columns)

        sql = f"""
SELECT
  '{feature_id}' as feature_id,
  '{table_name}' as source_table,
  COUNT(*) as n_samples,
  {corr_sql}
FROM `{PROJECT}.bqx_ml_v3_analytics.extreme_targets` t
JOIN `{PROJECT}.bqx_ml_v3_features.{table_name}` f ON t.interval_time = f.interval_time
WHERE f.{feature} IS NOT NULL
"""
        union_parts.append(sql)

    return "\nUNION ALL\n".join(union_parts)


def run_bq_query(sql: str, output_format: str = "json") -> str:
    """Run BigQuery query and return results."""
    # Write SQL to temp file
    with open("/tmp/full_corr_query.sql", "w") as f:
        f.write(sql)

    cmd = ["bq", "query", "--use_legacy_sql=false", f"--format={output_format}", "--max_rows=1000"]

    result = subprocess.run(
        cmd,
        stdin=open("/tmp/full_corr_query.sql"),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return ""

    return result.stdout


def process_table(table_name: str, features: list) -> list:
    """Process a single feature table and return results."""
    print(f"Processing {table_name} ({len(features)} features)...")

    sql = generate_full_correlation_sql(table_name, features)

    result = run_bq_query(sql, "json")

    if not result:
        print(f"  No results for {table_name}")
        return []

    try:
        rows = json.loads(result)
        print(f"  Got {len(rows)} results")
        return rows
    except json.JSONDecodeError:
        print(f"  Failed to parse JSON for {table_name}")
        return []


def main():
    """Main function to calculate full correlations and save to BigQuery."""
    all_results = []

    for table_name, features in FEATURE_TABLES.items():
        results = process_table(table_name, features)
        all_results.extend(results)

    print(f"\nTotal results: {len(all_results)}")

    if not all_results:
        print("No results to save!")
        return

    # Create the schema for all 49 correlations
    schema_parts = [
        "feature_id:STRING",
        "source_table:STRING",
        "n_samples:INTEGER"
    ]
    for w in WINDOWS:
        for h in HORIZONS:
            schema_parts.append(f"corr_w{w}_h{h}:FLOAT")

    schema = ",".join(schema_parts)

    # Write results to JSONL file
    with open("/tmp/full_correlations.jsonl", "w") as f:
        for row in all_results:
            # Clean up the row
            clean_row = {
                "feature_id": row.get("feature_id", ""),
                "source_table": row.get("source_table", ""),
                "n_samples": int(row.get("n_samples", 0))
            }
            for w in WINDOWS:
                for h in HORIZONS:
                    key = f"corr_w{w}_h{h}"
                    clean_row[key] = safe_float(row.get(key))
            f.write(json.dumps(clean_row) + "\n")

    # Load to BigQuery
    print("\nLoading to BigQuery...")
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--replace",
        f"{PROJECT}:bqx_ml_v3_analytics.full_correlation_matrix",
        "/tmp/full_correlations.jsonl",
        schema
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Successfully loaded to bqx_ml_v3_analytics.full_correlation_matrix")
    else:
        print(f"Error loading: {result.stderr}")


if __name__ == "__main__":
    main()
