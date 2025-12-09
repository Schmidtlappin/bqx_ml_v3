#!/usr/bin/env python3
"""
Generate Comprehensive Column Catalog for BQX ML V3

Creates a definitive catalog of ALL columns in ALL feature tables.
This prevents column naming errors in training scripts.

Output: /home/micha/bqx_ml_v3/intelligence/column_catalog.json
"""

import json
from datetime import datetime
from google.cloud import bigquery
from collections import defaultdict

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"


def generate_catalog():
    client = bigquery.Client(project=PROJECT)

    print("=" * 70)
    print("GENERATING COMPREHENSIVE COLUMN CATALOG")
    print("=" * 70)

    # Get all tables
    query = f"""
    SELECT table_id, row_count, size_bytes
    FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    ORDER BY table_id
    """

    tables_df = client.query(query).to_dataframe()
    print(f"Found {len(tables_df)} tables in {FEATURES_DATASET}")

    catalog = {
        "catalog_version": "1.0",
        "generated": datetime.now().isoformat(),
        "project": PROJECT,
        "dataset": FEATURES_DATASET,
        "total_tables": 0,
        "total_columns": 0,
        "total_feature_columns": 0,
        "tables": {},
        "columns_by_type": defaultdict(list),
        "column_list": [],  # Flat list of all column names
        "eurusd_columns": {},  # Columns specific to EURUSD tables
    }

    total_cols = 0
    feature_cols = 0

    for _, row in tables_df.iterrows():
        table_name = row['table_id']
        table_id = f"{PROJECT}.{FEATURES_DATASET}.{table_name}"

        try:
            table = client.get_table(table_id)
            columns = []

            for field in table.schema:
                col_info = {
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode
                }
                columns.append(col_info)

                # Track all unique columns
                if field.name not in ['interval_time', 'pair', 'pair1', 'pair2']:
                    feature_cols += 1
                    if field.name not in catalog["column_list"]:
                        catalog["column_list"].append(field.name)

                total_cols += 1

            catalog["tables"][table_name] = {
                "row_count": int(row['row_count']) if row['row_count'] else 0,
                "size_mb": round(row['size_bytes'] / (1024*1024), 2) if row['size_bytes'] else 0,
                "column_count": len(columns),
                "columns": columns
            }

            # Categorize by table type
            for prefix in ['reg_', 'mom_', 'der_', 'vol_', 'agg_', 'align_', 'base_',
                          'rev_', 'div_', 'lag_', 'regime_', 'mrt_', 'cov_', 'corr_',
                          'tri_', 'cyc_', 'ext_', 'tmp_']:
                if table_name.startswith(prefix):
                    catalog["columns_by_type"][prefix.rstrip('_')].extend(
                        [c["name"] for c in columns if c["name"] not in ['interval_time', 'pair', 'pair1', 'pair2']]
                    )
                    break

            # Track EURUSD-specific columns
            if 'eurusd' in table_name:
                catalog["eurusd_columns"][table_name] = [
                    c["name"] for c in columns if c["name"] not in ['interval_time', 'pair', 'pair1', 'pair2']
                ]

        except Exception as e:
            print(f"  Error reading {table_name}: {e}")
            continue

    # Deduplicate columns_by_type
    for key in catalog["columns_by_type"]:
        catalog["columns_by_type"][key] = list(set(catalog["columns_by_type"][key]))

    catalog["total_tables"] = len(catalog["tables"])
    catalog["total_columns"] = total_cols
    catalog["total_feature_columns"] = len(catalog["column_list"])

    # Convert defaultdict to regular dict
    catalog["columns_by_type"] = dict(catalog["columns_by_type"])

    # Summary stats
    print(f"\nCatalog Summary:")
    print(f"  Total tables: {catalog['total_tables']}")
    print(f"  Total columns: {catalog['total_columns']}")
    print(f"  Unique feature columns: {catalog['total_feature_columns']}")
    print(f"\nColumns by type:")
    for cat, cols in sorted(catalog["columns_by_type"].items()):
        print(f"  {cat}: {len(cols)} columns")

    # Count EURUSD columns
    eurusd_total = sum(len(cols) for cols in catalog["eurusd_columns"].values())
    print(f"\nEURUSD-specific:")
    print(f"  Tables: {len(catalog['eurusd_columns'])}")
    print(f"  Total columns: {eurusd_total}")

    # Save catalog
    output_file = "/home/micha/bqx_ml_v3/intelligence/column_catalog.json"
    with open(output_file, "w") as f:
        json.dump(catalog, f, indent=2)

    print(f"\nCatalog saved to: {output_file}")

    # Also save a compact EURUSD-only version for quick reference
    eurusd_catalog = {
        "generated": datetime.now().isoformat(),
        "total_tables": len(catalog["eurusd_columns"]),
        "total_columns": eurusd_total,
        "tables": catalog["eurusd_columns"]
    }

    eurusd_file = "/home/micha/bqx_ml_v3/intelligence/eurusd_column_catalog.json"
    with open(eurusd_file, "w") as f:
        json.dump(eurusd_catalog, f, indent=2)

    print(f"EURUSD catalog saved to: {eurusd_file}")

    return catalog


if __name__ == "__main__":
    generate_catalog()
