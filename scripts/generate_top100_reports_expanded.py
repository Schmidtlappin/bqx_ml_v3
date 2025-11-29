#!/usr/bin/env python3
"""
Generate top 100 correlation reports including polynomial features.

This script creates:
1. top100_per_target table - Top 100 features per each of 49 targets
2. CSV exports for docs/ directory
3. Summary statistics for polynomial vs existing features

Usage:
  python3 generate_top100_reports_expanded.py [--source-table TABLE]

Author: Chief Engineer, BQX ML V3
Date: 2025-11-29
"""

import subprocess
import json
import sys
import argparse
import csv
from datetime import datetime

PROJECT = "bqx-ml"
ANALYTICS_DATASET = "bqx_ml_v3_analytics"
DEFAULT_SOURCE_TABLE = "full_correlation_matrix_expanded"
OUTPUT_TABLE = "top100_per_target_expanded"

WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]


def generate_top100_sql(source_table: str) -> str:
    """Generate SQL to create top 100 features per target."""

    # Build UNION ALL for each target
    union_parts = []
    for w in WINDOWS:
        for h in HORIZONS:
            target = f"w{w}_h{h}"
            union_parts.append(f"""
  SELECT
    feature_id,
    source_table,
    column_name,
    variant,
    n_samples,
    '{target}' as target,
    corr_{target} as correlation
  FROM `{PROJECT}.{ANALYTICS_DATASET}.{source_table}`""")

    sql = f"""
-- Unpivot all 49 target correlations and rank top 100 per target
WITH unpivoted AS (
  {"  UNION ALL".join(union_parts)}
),
ranked AS (
  SELECT
    target,
    feature_id,
    source_table,
    column_name,
    variant,
    n_samples,
    correlation,
    ROW_NUMBER() OVER (PARTITION BY target ORDER BY ABS(correlation) DESC) as rank
  FROM unpivoted
  WHERE correlation IS NOT NULL AND ABS(correlation) > 0.001
)
SELECT
  target,
  rank,
  feature_id,
  column_name,
  variant,
  ROUND(correlation, 4) as correlation,
  n_samples,
  -- Flag polynomial features
  CASE
    WHEN column_name LIKE 'reg_quad%' OR column_name LIKE 'reg_lin_term%'
      OR column_name LIKE 'reg_r2%' OR column_name LIKE 'reg_resid%'
      OR column_name LIKE 'reg_acceleration%' OR column_name LIKE 'reg_trend_str%'
      OR column_name LIKE 'reg_forecast%' OR column_name LIKE 'reg_curv%'
    THEN 'polynomial'
    ELSE 'existing'
  END as feature_type
FROM ranked
WHERE rank <= 100
ORDER BY target, rank
"""
    return sql


def run_bq_query(sql: str, output_format: str = "json") -> tuple:
    """Run a BigQuery query and return results."""
    cmd = ["bq", "query", "--use_legacy_sql=false", f"--format={output_format}", "--max_rows=10000"]
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def create_top100_table(source_table: str):
    """Create the top100 table in BigQuery."""
    print(f"Creating top100 table from {source_table}...")

    sql = generate_top100_sql(source_table)

    # Write SQL to file for debugging
    with open("/tmp/top100_query.sql", "w") as f:
        f.write(sql)

    # Create table
    create_sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{ANALYTICS_DATASET}.{OUTPUT_TABLE}` AS
    {sql}
    """

    returncode, stdout, stderr = run_bq_query(create_sql)

    if returncode != 0:
        print(f"Error creating table: {stderr}")
        return False

    print(f"Created {OUTPUT_TABLE}")
    return True


def export_to_csv(output_dir: str = "/home/micha/bqx_ml_v3/docs"):
    """Export results to CSV files."""
    print("\nExporting to CSV...")

    # Export top100
    export_sql = f"""
    SELECT * FROM `{PROJECT}.{ANALYTICS_DATASET}.{OUTPUT_TABLE}`
    ORDER BY target, rank
    """

    returncode, stdout, stderr = run_bq_query(export_sql, "csv")

    if returncode != 0:
        print(f"Error exporting: {stderr}")
        return False

    output_file = f"{output_dir}/top100_features_per_target_expanded.csv"
    with open(output_file, "w") as f:
        f.write(stdout)

    print(f"Exported to {output_file}")
    return True


def generate_summary_report():
    """Generate summary statistics comparing polynomial vs existing features."""
    print("\nGenerating summary report...")

    summary_sql = f"""
    WITH stats AS (
      SELECT
        target,
        feature_type,
        COUNT(*) as count_in_top100,
        AVG(ABS(correlation)) as avg_correlation,
        MAX(ABS(correlation)) as max_correlation,
        MIN(rank) as best_rank
      FROM `{PROJECT}.{ANALYTICS_DATASET}.{OUTPUT_TABLE}`
      GROUP BY target, feature_type
    )
    SELECT
      feature_type,
      COUNT(DISTINCT target) as targets_represented,
      SUM(count_in_top100) as total_appearances,
      ROUND(AVG(avg_correlation), 4) as mean_avg_correlation,
      ROUND(MAX(max_correlation), 4) as highest_correlation,
      MIN(best_rank) as best_rank_achieved
    FROM stats
    GROUP BY feature_type
    ORDER BY mean_avg_correlation DESC
    """

    returncode, stdout, stderr = run_bq_query(summary_sql, "pretty")

    if returncode == 0:
        print("\n=== Feature Type Comparison ===")
        print(stdout)

    # Top performers by type
    top_sql = f"""
    SELECT
      feature_type,
      column_name,
      target,
      rank,
      correlation
    FROM `{PROJECT}.{ANALYTICS_DATASET}.{OUTPUT_TABLE}`
    WHERE rank = 1
    ORDER BY feature_type, ABS(correlation) DESC
    LIMIT 20
    """

    returncode, stdout, stderr = run_bq_query(top_sql, "pretty")

    if returncode == 0:
        print("\n=== Top 1 Features by Type ===")
        print(stdout)

    # Polynomial performance across windows
    poly_sql = f"""
    SELECT
      REGEXP_EXTRACT(column_name, r'_(\d+)$') as window,
      column_name,
      COUNT(*) as top100_appearances,
      ROUND(AVG(ABS(correlation)), 4) as avg_corr,
      ROUND(MAX(ABS(correlation)), 4) as max_corr
    FROM `{PROJECT}.{ANALYTICS_DATASET}.{OUTPUT_TABLE}`
    WHERE feature_type = 'polynomial'
    GROUP BY window, column_name
    ORDER BY max_corr DESC
    LIMIT 30
    """

    returncode, stdout, stderr = run_bq_query(poly_sql, "pretty")

    if returncode == 0:
        print("\n=== Polynomial Features Performance ===")
        print(stdout)


def main():
    parser = argparse.ArgumentParser(description="Generate top 100 correlation reports")
    parser.add_argument("--source-table", default=DEFAULT_SOURCE_TABLE,
                       help=f"Source correlation matrix table (default: {DEFAULT_SOURCE_TABLE})")
    parser.add_argument("--output-dir", default="/home/micha/bqx_ml_v3/docs",
                       help="Directory for CSV exports")
    parser.add_argument("--summary-only", action="store_true",
                       help="Only generate summary report (assumes table exists)")
    args = parser.parse_args()

    print(f"=== Top 100 Report Generator ===")
    print(f"Source: {args.source_table}")
    print(f"Output: {OUTPUT_TABLE}")
    print(f"Time: {datetime.now().isoformat()}")
    print()

    if not args.summary_only:
        # Create top100 table
        if not create_top100_table(args.source_table):
            sys.exit(1)

        # Export to CSV
        if not export_to_csv(args.output_dir):
            print("Warning: CSV export failed")

    # Generate summary
    generate_summary_report()

    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
