#!/usr/bin/env python3
"""
M008 Phase 4C - LAG Table Rename Mapping Generator

Generates rename mapping for 224 LAG tables (semi-automated approach).

Approach:
- Query all LAG tables from BigQuery
- Generate rename mapping: lag_{pair}_{window} → lag_idx_{pair}_{window}
- Assume IDX variant (most common for LAG tables)
- Save to CSV for BA manual review
- BA reviews CSV for M008 compliance before execution

Author: BA (Build Agent)
Date: 2025-12-14
CE Authorization: 20251214_0030_CE-to-ALL_FINAL_GO_AUTHORIZATION.md
"""

import csv
import logging
import sys
from typing import List, Dict

from google.cloud import bigquery

# Configuration
PROJECT_ID = "bqx-ml"
DATASET_ID = "bqx_ml_v3_features_v2"
OUTPUT_FILE = "LAG_RENAME_MAPPING_20251214.csv"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/lag_mapping_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_lag_tables() -> List[str]:
    """
    Query BigQuery for all LAG tables.

    Returns:
        List of LAG table names
    """
    client = bigquery.Client(project=PROJECT_ID)

    logger.info("Querying for LAG tables...")

    query = f"""
    SELECT table_name
    FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
    WHERE table_name LIKE 'lag_%'
    ORDER BY table_name
    """

    results = client.query(query).result()
    tables = [row.table_name for row in results]

    logger.info(f"Found {len(tables)} LAG tables")
    return tables


def is_m008_compliant(table_name: str) -> bool:
    """
    Check if LAG table is already M008-compliant.

    M008 Pattern: lag_{variant}_{pair}_{window}
    Examples:
    - lag_idx_eurusd_45 (compliant)
    - lag_bqx_eurusd_45 (compliant)
    - lag_eurusd_45 (non-compliant, missing variant)

    Args:
        table_name: LAG table name

    Returns:
        True if already compliant, False otherwise
    """
    return table_name.startswith('lag_idx_') or table_name.startswith('lag_bqx_')


def generate_new_name(old_name: str) -> str:
    """
    Generate M008-compliant LAG table name.

    Pattern: lag_{pair}_{window} → lag_idx_{pair}_{window}

    Assumes IDX variant (most common for LAG tables).
    BA will review and adjust if needed during manual review.

    Args:
        old_name: Original table name

    Returns:
        New M008-compliant table name
    """
    # Simple replacement: insert 'idx_' after 'lag_'
    if old_name.startswith('lag_'):
        new_name = old_name.replace('lag_', 'lag_idx_', 1)
        return new_name
    else:
        logger.warning(f"Unexpected pattern: {old_name}")
        return f"lag_idx_{old_name}"


def extract_window_suffix(table_name: str) -> str:
    """
    Extract window suffix from LAG table name.

    Examples:
    - lag_eurusd_45 → 45
    - lag_idx_gbpusd_90 → 90

    Args:
        table_name: LAG table name

    Returns:
        Window suffix (last part after final underscore)
    """
    parts = table_name.split('_')
    if parts:
        return parts[-1]
    return ""


def generate_lag_mapping(tables: List[str]) -> List[Dict]:
    """
    Generate rename mapping for LAG tables.

    Args:
        tables: List of LAG table names

    Returns:
        List of dicts with rename metadata
    """
    logger.info(f"Generating rename mapping for {len(tables)} LAG tables...")

    mapping = []
    compliant_count = 0
    non_compliant_count = 0

    for table in tables:
        if is_m008_compliant(table):
            logger.info(f"✅ COMPLIANT (skip): {table}")
            compliant_count += 1
            continue

        # Generate new name
        new_name = generate_new_name(table)
        window = extract_window_suffix(table)

        mapping.append({
            'old_name': table,
            'new_name': new_name,
            'window_suffix': window,
            'assumed_variant': 'idx'
        })

        logger.info(f"📋 RENAME: {table} → {new_name} (window={window})")
        non_compliant_count += 1

    logger.info(f"\nSummary:")
    logger.info(f"  Total LAG tables: {len(tables)}")
    logger.info(f"  Already compliant: {compliant_count}")
    logger.info(f"  Need renaming: {non_compliant_count}")

    return mapping


def save_mapping_csv(mapping: List[Dict], filename: str):
    """
    Save LAG rename mapping to CSV file.

    Args:
        mapping: List of rename metadata dicts
        filename: Output CSV filename
    """
    logger.info(f"\nSaving mapping to {filename}...")

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['old_name', 'new_name', 'window_suffix', 'assumed_variant'])
        writer.writeheader()
        writer.writerows(mapping)

    logger.info(f"✅ Mapping saved: {filename}")
    logger.info(f"   {len(mapping)} tables need renaming")


def main():
    """Main execution function."""
    logger.info(f"\n{'='*80}")
    logger.info(f"M008 PHASE 4C - LAG RENAME MAPPING GENERATOR")
    logger.info(f"{'='*80}")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Dataset: {DATASET_ID}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    logger.info(f"{'='*80}\n")

    # Step 1: Get all LAG tables
    tables = get_lag_tables()

    if not tables:
        logger.warning("No LAG tables found!")
        return 1

    # Step 2: Generate rename mapping
    mapping = generate_lag_mapping(tables)

    if not mapping:
        logger.info("✅ All LAG tables are already M008-compliant!")
        return 0

    # Step 3: Save to CSV
    save_mapping_csv(mapping, OUTPUT_FILE)

    # Step 4: Manual review instructions
    logger.info(f"\n{'='*80}")
    logger.info(f"NEXT STEP: MANUAL REVIEW")
    logger.info(f"{'='*80}")
    logger.info(f"1. Review {OUTPUT_FILE}")
    logger.info(f"2. Verify all {len(mapping)} mappings are M008-compliant")
    logger.info(f"3. Adjust 'idx' to 'bqx' if needed (manual check)")
    logger.info(f"4. Flag any unexpected patterns for CE/QA review")
    logger.info(f"5. Approve for execution Dec 15")
    logger.info(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
