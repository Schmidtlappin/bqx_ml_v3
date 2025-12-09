#!/usr/bin/env python3
"""
Dynamic full 49-correlation calculator - discovers columns automatically.
"""

import subprocess
import json
import sys
import time

PROJECT = "bqx-ml"
DATASET = "bqx_ml_v3_features_v2"

# All BQX windows and horizons
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Tables to process
FEATURE_TABLES = [
    "eurusd_bqx", "eurusd_idx",
    "agg_eurusd", "agg_bqx_eurusd",
    "reg_eurusd", "reg_bqx_eurusd",
    "mom_eurusd", "mom_bqx_eurusd",
    "vol_eurusd", "vol_bqx_eurusd",
    "der_eurusd", "der_bqx_eurusd",
    "align_eurusd", "align_bqx_eurusd",
    "ext_bqx_eurusd",
    "mrt_eurusd", "mrt_bqx_eurusd",
    "rev_eurusd", "rev_bqx_eurusd",
    "div_eurusd", "div_bqx_eurusd",
    "tmp_eurusd", "tmp_bqx_eurusd",
    "cyc_bqx_eurusd",
]


def get_table_columns(table_name: str) -> list:
    """Get numeric columns from a table, excluding interval_time and pair."""
    cmd = ["bq", "show", "--schema", "--format=json", f"{PROJECT}:{DATASET}.{table_name}"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  Failed to get schema for {table_name}", file=sys.stderr)
        return []

    try:
        schema = json.loads(result.stdout)
        # Get numeric columns, excluding system columns
        cols = [
            c["name"] for c in schema
            if c["name"] not in ["interval_time", "pair", "source_value"]
            and c["type"] in ["FLOAT", "FLOAT64", "INTEGER", "INT64", "NUMERIC"]
        ]
        return cols
    except json.JSONDecodeError:
        print(f"  Failed to parse schema for {table_name}", file=sys.stderr)
        return []


def safe_float(val, default=0.0):
    """Convert to float safely."""
    if val is None:
        return default
    try:
        f = float(val)
        if f != f:  # NaN
            return default
        return f
    except:
        return default


def generate_correlation_sql(table_name: str, features: list, batch_size: int = 5) -> list:
    """Generate SQL for correlations in batches."""
    variant = "bqx" if "_bqx_" in table_name or table_name.endswith("_bqx") else "idx"

    sqls = []
    for i in range(0, len(features), batch_size):
        batch = features[i:i+batch_size]
        union_parts = []

        for feature in batch:
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
JOIN `{PROJECT}.{DATASET}.{table_name}` f ON t.interval_time = f.interval_time
WHERE f.{feature} IS NOT NULL
"""
            union_parts.append(sql)

        sqls.append("\nUNION ALL\n".join(union_parts))

    return sqls


def run_bq_query(sql: str) -> list:
    """Run BigQuery query and return results as list of dicts."""
    with open("/tmp/corr_query.sql", "w") as f:
        f.write(sql)

    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=100"]
    result = subprocess.run(cmd, stdin=open("/tmp/corr_query.sql"), capture_output=True, text=True)

    if result.returncode != 0:
        # Print the error for debugging
        if result.stderr:
            print(f"    Query error: {result.stderr[:200]}", file=sys.stderr)
        return []

    try:
        return json.loads(result.stdout)
    except:
        return []


def process_table(table_name: str) -> list:
    """Process a single feature table."""
    print(f"Processing {table_name}...")

    # Get columns
    columns = get_table_columns(table_name)
    if not columns:
        print(f"  No columns found")
        return []

    print(f"  Found {len(columns)} features")

    # Generate SQL in batches
    sqls = generate_correlation_sql(table_name, columns, batch_size=3)

    all_results = []
    for i, sql in enumerate(sqls):
        results = run_bq_query(sql)
        if results:
            all_results.extend(results)
        print(f"  Batch {i+1}/{len(sqls)}: {len(results)} results")
        time.sleep(0.5)  # Rate limit

    print(f"  Total: {len(all_results)} results")
    return all_results


def main():
    """Main function."""
    all_results = []

    for table_name in FEATURE_TABLES:
        results = process_table(table_name)
        all_results.extend(results)

    print(f"\n=== TOTAL: {len(all_results)} feature correlations ===")

    if not all_results:
        print("No results!")
        return

    # Build schema
    schema_parts = ["feature_id:STRING", "source_table:STRING", "n_samples:INTEGER"]
    for w in WINDOWS:
        for h in HORIZONS:
            schema_parts.append(f"corr_w{w}_h{h}:FLOAT")
    schema = ",".join(schema_parts)

    # Write JSONL
    with open("/tmp/full_correlations.jsonl", "w") as f:
        for row in all_results:
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
        print("Success! Loaded to bqx_ml_v3_analytics.full_correlation_matrix")
    else:
        print(f"Error: {result.stderr}")


if __name__ == "__main__":
    main()
