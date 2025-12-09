#!/usr/bin/env python3
"""
Efficient batch correlation calculator using BigQuery jobs.
Processes features in table batches and stores results incrementally.
"""

import subprocess
import csv
import json
import sys
import time

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics"
TARGET_TABLE = "extreme_targets"
OUTPUT_TABLE = "full_correlation_matrix"

WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        f = float(val)
        return default if f != f else f
    except:
        return default


def load_feature_columns():
    """Load feature columns from the pre-generated CSV."""
    features_by_table = {}
    with open("/tmp/eurusd_feature_columns.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table = row["table_name"]
            col = row["column_name"]
            if table not in features_by_table:
                features_by_table[table] = []
            features_by_table[table].append(col)
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
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=200"]
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
    print("Loading feature columns...")
    features_by_table = load_feature_columns()
    total_features = sum(len(cols) for cols in features_by_table.values())
    print(f"Found {len(features_by_table)} tables with {total_features} total features")

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
    with open("/tmp/full_correlations.jsonl", "w") as f:
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

    # Load to BigQuery
    print("Loading to BigQuery...")
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--replace",
        f"{PROJECT}:{ANALYTICS_DATASET}.{OUTPUT_TABLE}",
        "/tmp/full_correlations.jsonl",
        schema
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Success! Loaded to {ANALYTICS_DATASET}.{OUTPUT_TABLE}")
        print(f"Total features: {len(all_results)}")
    else:
        print(f"Error: {result.stderr}")


if __name__ == "__main__":
    main()
