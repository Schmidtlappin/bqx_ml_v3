#!/usr/bin/env python3
"""
M008 Phase 4C - COV Table Rename Script

Renames 1,596 COV tables to add variant identifier (bqx or idx) for M008 compliance.

Approach:
- Variant Detection: Data sampling with median_abs heuristic
  - BQX: median_abs < 10 (oscillates around 0)
  - IDX: median_abs > 50 (centered around 100)
- Batch Execution: 100 tables per batch (16 batches total)
- Rollback: Auto-generate CSV per batch for manual recovery
- Dry-Run: Validation mode before production execution

Author: BA (Build Agent)
Date: 2025-12-14
CE Authorization: 20251214_0030_CE-to-ALL_FINAL_GO_AUTHORIZATION.md
"""

import argparse
import csv
import json
import logging
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from google.cloud import bigquery

# Configuration
PROJECT_ID = "bqx-ml"
DATASET_ID = "bqx_ml_v3_features_v2"
BATCH_SIZE = 100
SAMPLE_SIZE = 10
MEDIAN_ABS_BQX_THRESHOLD = 10  # Values < 10 = BQX
MEDIAN_ABS_IDX_THRESHOLD = 50  # Values > 50 = IDX

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cov_rename_execution.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class COVRenameExecutor:
    """Executes M008-compliant renaming of COV tables with variant detection."""

    def __init__(self, dry_run: bool = True):
        """
        Initialize the COV rename executor.

        Args:
            dry_run: If True, validate only without executing renames
        """
        self.dry_run = dry_run
        self.client = bigquery.Client(project=PROJECT_ID)
        self.results = {
            'total_tables': 0,
            'bqx_detected': 0,
            'idx_detected': 0,
            'ambiguous': 0,
            'errors': 0,
            'renamed': 0
        }

    def get_non_compliant_cov_tables(self) -> List[str]:
        """
        Query BigQuery for COV tables missing variant identifier.

        Returns:
            List of table names that need variant insertion
        """
        logger.info("Querying for non-compliant COV tables...")

        query = f"""
        SELECT table_name
        FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
        WHERE table_name LIKE 'cov_%'
          AND table_name NOT LIKE 'cov_%_bqx_%'
          AND table_name NOT LIKE 'cov_%_idx_%'
        ORDER BY table_name
        """

        results = self.client.query(query).result()
        tables = [row.table_name for row in results]

        logger.info(f"Found {len(tables)} non-compliant COV tables")
        return tables

    def detect_variant(self, table_name: str) -> Tuple[str, float, Optional[str]]:
        """
        Detect variant (BQX or IDX) using data sampling heuristic.

        Algorithm:
        1. Sample 10 rows from table
        2. Extract numeric feature values (skip timestamp/pair columns)
        3. Calculate median absolute value
        4. Classify:
           - median_abs < 10: BQX (oscillates around 0)
           - median_abs > 50: IDX (centered around 100)
           - 10 <= median_abs <= 50: AMBIGUOUS (manual review)

        Args:
            table_name: Name of COV table to analyze

        Returns:
            Tuple of (variant, median_abs_value, error_message)
        """
        try:
            # Sample data from table
            query = f"""
            SELECT *
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            LIMIT {SAMPLE_SIZE}
            """

            rows = list(self.client.query(query).result())

            if not rows:
                logger.warning(f"{table_name}: No data found")
                return 'bqx', 0.0, "No data in table"

            # Extract numeric values (assume column index 2 is feature value)
            # COV table schema: [interval_time, pair, feature_value, ...]
            values = []
            for row in rows:
                # Get all columns, skip first 2 (timestamp, pair)
                row_values = list(row.values())
                if len(row_values) > 2:
                    # Try to extract numeric value from column index 2
                    try:
                        val = float(row_values[2])
                        values.append(val)
                    except (ValueError, TypeError):
                        # Try other columns if column 2 fails
                        for i in range(3, min(len(row_values), 6)):
                            try:
                                val = float(row_values[i])
                                values.append(val)
                                break
                            except (ValueError, TypeError):
                                continue

            if not values:
                logger.warning(f"{table_name}: No numeric values found")
                return 'bqx', 0.0, "No numeric values"

            # Calculate median absolute value
            median_abs = statistics.median([abs(v) for v in values])

            # Classify variant
            if median_abs < MEDIAN_ABS_BQX_THRESHOLD:
                variant = 'bqx'
            elif median_abs > MEDIAN_ABS_IDX_THRESHOLD:
                variant = 'idx'
            else:
                variant = 'ambiguous'
                logger.warning(f"{table_name}: Ambiguous classification (median_abs={median_abs:.2f})")

            logger.debug(f"{table_name}: variant={variant}, median_abs={median_abs:.2f}, sample_size={len(values)}")
            return variant, median_abs, None

        except Exception as e:
            logger.error(f"{table_name}: Error detecting variant: {str(e)}")
            return 'bqx', 0.0, str(e)

    def generate_new_name(self, old_name: str, variant: str) -> str:
        """
        Generate M008-compliant table name with variant inserted.

        Pattern: cov_{feature_type}_{pair1}_{pair2}
        New:     cov_{feature_type}_{variant}_{pair1}_{pair2}

        Example: cov_agg_eurusd_gbpusd → cov_agg_bqx_eurusd_gbpusd

        Args:
            old_name: Original table name
            variant: Detected variant (bqx or idx)

        Returns:
            New M008-compliant table name
        """
        parts = old_name.split('_')

        if len(parts) < 4:
            logger.warning(f"{old_name}: Unexpected name pattern (parts={len(parts)})")
            # Simple insertion after feature type
            return f"{parts[0]}_{parts[1]}_{variant}_{'_'.join(parts[2:])}"

        # Insert variant after feature type (position 1)
        # cov_agg_eurusd_gbpusd → [cov, agg, eurusd, gbpusd]
        # Result: [cov, agg, bqx, eurusd, gbpusd]
        new_parts = [parts[0], parts[1], variant] + parts[2:]
        new_name = '_'.join(new_parts)

        return new_name

    def generate_rename_mapping(self, tables: List[str]) -> List[Dict]:
        """
        Generate rename mapping for all non-compliant COV tables.

        Args:
            tables: List of table names to process

        Returns:
            List of dicts with rename metadata
        """
        logger.info(f"Generating rename mapping for {len(tables)} tables...")

        mapping = []
        for i, table in enumerate(tables, 1):
            logger.info(f"[{i}/{len(tables)}] Processing {table}")

            variant, median_abs, error = self.detect_variant(table)

            if error:
                self.results['errors'] += 1

            if variant == 'ambiguous':
                self.results['ambiguous'] += 1
            elif variant == 'bqx':
                self.results['bqx_detected'] += 1
            elif variant == 'idx':
                self.results['idx_detected'] += 1

            new_name = self.generate_new_name(table, variant)

            mapping.append({
                'old_name': table,
                'new_name': new_name,
                'variant': variant,
                'median_abs': median_abs,
                'error': error
            })

        self.results['total_tables'] = len(tables)
        return mapping

    def save_mapping_csv(self, mapping: List[Dict], filename: str):
        """
        Save rename mapping to CSV file.

        Args:
            mapping: List of rename metadata dicts
            filename: Output CSV filename
        """
        logger.info(f"Saving mapping to {filename}...")

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['old_name', 'new_name', 'variant', 'median_abs', 'error'])
            writer.writeheader()
            writer.writerows(mapping)

        logger.info(f"Mapping saved: {filename}")

    def execute_batch(self, batch: List[Dict], batch_num: int, total_batches: int) -> int:
        """
        Execute rename operations for a batch of tables.

        Args:
            batch: List of rename metadata dicts
            batch_num: Current batch number (1-indexed)
            total_batches: Total number of batches

        Returns:
            Number of successful renames
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"BATCH {batch_num}/{total_batches}: {len(batch)} tables")
        logger.info(f"{'='*80}")

        # Auto-generate rollback CSV
        rollback_filename = f"rollback_batch_{batch_num:03d}.csv"
        with open(rollback_filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['old_name', 'new_name', 'variant', 'median_abs'])
            writer.writeheader()
            for item in batch:
                writer.writerow({k: item[k] for k in ['old_name', 'new_name', 'variant', 'median_abs']})

        logger.info(f"Rollback CSV generated: {rollback_filename}")

        # Execute renames
        success_count = 0
        for i, item in enumerate(batch, 1):
            old_name = item['old_name']
            new_name = item['new_name']
            variant = item['variant']
            median_abs = item['median_abs']

            if self.dry_run:
                logger.info(f"  [{i}/{len(batch)}] DRY-RUN: {old_name} → {new_name} (variant={variant}, median_abs={median_abs:.2f})")
                success_count += 1
            else:
                try:
                    # Execute ALTER TABLE RENAME
                    query = f"""
                    ALTER TABLE `{PROJECT_ID}.{DATASET_ID}.{old_name}`
                    RENAME TO `{new_name}`
                    """
                    self.client.query(query).result()

                    logger.info(f"  [{i}/{len(batch)}] ✅ {old_name} → {new_name} (variant={variant})")
                    success_count += 1
                    self.results['renamed'] += 1

                except Exception as e:
                    logger.error(f"  [{i}/{len(batch)}] ❌ FAILED: {old_name} → {new_name}")
                    logger.error(f"      Error: {str(e)}")
                    logger.error(f"      Use {rollback_filename} to revert this batch")
                    self.results['errors'] += 1
                    raise  # Stop on first failure

        logger.info(f"\nBatch {batch_num} complete: {success_count}/{len(batch)} successful")
        logger.info(f"Rollback available: {rollback_filename}")

        if not self.dry_run:
            # QA validation checkpoint
            logger.info("\n⏸️  QA VALIDATION CHECKPOINT")
            logger.info("   Please validate this batch before continuing.")
            input("   Press Enter to continue to next batch...")

        return success_count

    def execute_renames_in_batches(self, mapping: List[Dict]):
        """
        Execute renames in batches with rollback support.

        Args:
            mapping: Complete rename mapping
        """
        # Split into batches
        batches = [mapping[i:i+BATCH_SIZE] for i in range(0, len(mapping), BATCH_SIZE)]
        total_batches = len(batches)

        logger.info(f"\n{'='*80}")
        logger.info(f"EXECUTION PLAN")
        logger.info(f"{'='*80}")
        logger.info(f"Total tables: {len(mapping)}")
        logger.info(f"Batch size: {BATCH_SIZE}")
        logger.info(f"Total batches: {total_batches}")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        logger.info(f"{'='*80}\n")

        if not self.dry_run:
            logger.warning("⚠️  PRODUCTION MODE - ACTUAL RENAMES WILL BE EXECUTED")
            response = input("Continue? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Execution cancelled by user")
                return

        # Execute batches
        total_success = 0
        for batch_num, batch in enumerate(batches, 1):
            success = self.execute_batch(batch, batch_num, total_batches)
            total_success += success

        logger.info(f"\n{'='*80}")
        logger.info(f"EXECUTION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total successful: {total_success}/{len(mapping)}")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'PRODUCTION'}")
        logger.info(f"{'='*80}\n")

    def print_summary(self):
        """Print execution summary statistics."""
        logger.info(f"\n{'='*80}")
        logger.info(f"SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total tables processed: {self.results['total_tables']}")
        logger.info(f"BQX detected: {self.results['bqx_detected']} ({self.results['bqx_detected']/self.results['total_tables']*100:.1f}%)")
        logger.info(f"IDX detected: {self.results['idx_detected']} ({self.results['idx_detected']/self.results['total_tables']*100:.1f}%)")
        logger.info(f"Ambiguous: {self.results['ambiguous']} ({self.results['ambiguous']/self.results['total_tables']*100:.1f}%)")
        logger.info(f"Errors: {self.results['errors']}")
        if not self.dry_run:
            logger.info(f"Successfully renamed: {self.results['renamed']}")
        logger.info(f"{'='*80}\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='M008 Phase 4C - COV Table Rename Script')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Dry-run mode (validation only, no actual renames)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Production mode (execute actual renames)'
    )
    parser.add_argument(
        '--output',
        default='COV_RENAME_MAPPING_20251214.csv',
        help='Output CSV filename for rename mapping'
    )

    args = parser.parse_args()

    # Determine mode
    dry_run = not args.execute

    logger.info(f"\n{'='*80}")
    logger.info(f"M008 PHASE 4C - COV TABLE RENAME SCRIPT")
    logger.info(f"{'='*80}")
    logger.info(f"Mode: {'DRY-RUN' if dry_run else 'PRODUCTION'}")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Dataset: {DATASET_ID}")
    logger.info(f"Batch size: {BATCH_SIZE}")
    logger.info(f"Output file: {args.output}")
    logger.info(f"{'='*80}\n")

    # Initialize executor
    executor = COVRenameExecutor(dry_run=dry_run)

    # Step 1: Get non-compliant tables
    tables = executor.get_non_compliant_cov_tables()

    if not tables:
        logger.info("No non-compliant COV tables found. All tables are M008-compliant!")
        return 0

    # Step 2: Generate rename mapping
    mapping = executor.generate_rename_mapping(tables)

    # Step 3: Save mapping to CSV
    executor.save_mapping_csv(mapping, args.output)

    # Step 4: Print detection summary
    executor.print_summary()

    # Step 5: Execute renames (if not dry-run only)
    if dry_run:
        logger.info("✅ DRY-RUN COMPLETE")
        logger.info(f"   Mapping saved to: {args.output}")
        logger.info(f"   To execute renames, run with --execute flag")
    else:
        executor.execute_renames_in_batches(mapping)

    return 0


if __name__ == '__main__':
    sys.exit(main())
