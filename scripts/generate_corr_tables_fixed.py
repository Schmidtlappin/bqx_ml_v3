#!/usr/bin/env python3
"""
Tier 1 Remediation: ETF Correlation Table Regeneration
Regenerates corr_* tables with 100% row coverage using FULL OUTER JOIN strategy
NOTE: Preserves existing correlation values, adds rows for missing intervals
"""

from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import sys

PROJECT = 'bqx-ml'
FEATURES_DATASET = 'bqx_ml_v3_features_v2'
LOCATION = 'us-central1'

# All 28 currency pairs
PAIRS = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd',
    'usdcad', 'usdchf', 'usdjpy'
]

# ETF/Index assets
ASSETS = ['ewa', 'ewg', 'ewj', 'ewu', 'gld', 'spy', 'uup', 'vix']

def generate_corr_sql(variant, pair, asset, validate_only=False):
    """Generate SQL for ETF correlation table with 100% row coverage."""

    # Table names - use actual BigQuery naming
    if variant == 'idx':
        table_name = f"corr_etf_idx_{pair}_{asset}"
    else:  # bqx
        table_name = f"corr_bqx_ibkr_{pair}_{asset}"

    # Source: Use pair's base table for intervals
    pair_table = f"base_{variant}_{pair}"

    # Validation query
    if validate_only:
        return f"""
        WITH old_table AS (
          SELECT COUNT(*) as old_rows,
                 MIN(interval_time) as old_min,
                 MAX(interval_time) as old_max
          FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
        ),
        new_table_preview AS (
          SELECT COUNT(*) as new_rows,
                 MIN(interval_time) as new_min,
                 MAX(interval_time) as new_max
          FROM (
            SELECT DISTINCT interval_time
            FROM `{PROJECT}.{FEATURES_DATASET}.{pair_table}`
          )
        )
        SELECT
          o.old_rows,
          n.new_rows,
          n.new_rows - o.old_rows as row_diff,
          ((n.new_rows - o.old_rows) / o.old_rows) * 100 as row_diff_pct,
          o.old_min,
          n.new_min,
          o.old_max,
          n.new_max
        FROM old_table o, new_table_preview n
        """

    # Generation SQL - preserve existing values, add missing rows
    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    PARTITION BY DATE(interval_time)
    
    AS
    WITH
      all_intervals AS (
        -- Get ALL unique interval_times from pair's base table
        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.{pair_table}`
        WHERE interval_time BETWEEN '2020-01-01' AND '2025-11-21'
      ),
      existing_correlations AS (
        SELECT *
        FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
      )
    SELECT
      ai.interval_time,
      ec.bqx_45,
      ec.bqx_90,
      ec.bqx_180,
      ec.bqx_360,
      ec.bqx_720,
      ec.bqx_1440,
      ec.bqx_2880
    FROM all_intervals ai
    LEFT JOIN existing_correlations ec
      ON ai.interval_time = ec.interval_time
    """

    return sql


def validate_table(client, variant, pair, asset):
    """Validate regenerated table against original."""
    if variant == 'idx':
        table_name = f"corr_etf_idx_{pair}_{asset}"
    else:
        table_name = f"corr_bqx_ibkr_{pair}_{asset}"

    try:
        validation_sql = generate_corr_sql(variant, pair, asset, validate_only=True)
        result = list(client.query(validation_sql).result())[0]

        return {
            'table': table_name,
            'old_rows': result.old_rows,
            'new_rows': result.new_rows,
            'row_diff': result.row_diff,
            'row_diff_pct': result.row_diff_pct,
            'old_date_range': f"{result.old_min} to {result.old_max}",
            'new_date_range': f"{result.new_min} to {result.new_max}",
            'validation': 'PASS' if abs(result.row_diff_pct) <= 1.0 else 'WARN'
        }
    except Exception as e:
        return {
            'table': table_name,
            'error': str(e),
            'validation': 'ERROR'
        }


def generate_corr_table(client, variant, pair, asset, dry_run=False):
    """Generate a single ETF correlation table."""
    if variant == 'idx':
        table_name = f"corr_etf_idx_{pair}_{asset}"
    else:
        table_name = f"corr_bqx_ibkr_{pair}_{asset}"

    if dry_run:
        return {'table': table_name, 'status': 'DRY_RUN'}

    try:
        # Generate table
        sql = generate_corr_sql(variant, pair, asset)
        job = client.query(sql)
        job.result()  # Wait for completion

        # Get row count
        count_sql = f"SELECT COUNT(*) as cnt FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`"
        row_count = list(client.query(count_sql).result())[0].cnt

        return {
            'table': table_name,
            'status': 'SUCCESS',
            'rows': row_count
        }
    except Exception as e:
        return {
            'table': table_name,
            'status': 'FAILED',
            'error': str(e)[:200]
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Regenerate ETF correlation tables with 100% row coverage')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not regenerate')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - show what would be generated')
    parser.add_argument('--workers', type=int, default=16, help='Number of parallel workers')
    parser.add_argument('--test-only', action='store_true', help='Test on 3 tables only')
    parser.add_argument('--bqx-only', action='store_true', help='Only regenerate BQX variant (skip IDX)')
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT, location=LOCATION)

    print("=" * 80)
    print("TIER 1: ETF CORRELATION TABLE REGENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Mode: {'VALIDATION ONLY' if args.validate_only else 'DRY RUN' if args.dry_run else 'GENERATION'}")
    print(f"Workers: {args.workers}")
    print(f"Variants: {'BQX only' if args.bqx_only else 'IDX + BQX'}")
    print("=" * 80)
    print()

    # Generate all pair-asset combinations
    tasks = []
    variants = ['bqx'] if args.bqx_only else ['idx', 'bqx']

    for variant in variants:
        for pair in PAIRS:
            for asset in ASSETS:
                tasks.append((variant, pair, asset))

    if args.test_only:
        tasks = tasks[:3]
        print(f"TEST MODE: Processing only {len(tasks)} tables")
        print()

    print(f"Total tables to process: {len(tasks)}")
    print()

    # Validation mode
    if args.validate_only:
        print("VALIDATION MODE: Comparing old vs new row counts")
        print("-" * 80)

        validations = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            for variant, pair, asset in tasks:
                future = executor.submit(validate_table, client, variant, pair, asset)
                futures[future] = (variant, pair, asset)

            for future in as_completed(futures):
                result = future.result()
                validations.append(result)

                status = result.get('validation', 'ERROR')
                if status == 'PASS':
                    print(f"✅ {result['table']}: {result['new_rows']:,} rows (+{result['row_diff']:,}, {result['row_diff_pct']:.1f}%)")
                elif status == 'WARN':
                    print(f"⚠️  {result['table']}: {result['new_rows']:,} rows (+{result['row_diff']:,}, {result['row_diff_pct']:.1f}%)")
                else:
                    print(f"❌ {result['table']}: {result.get('error', 'Unknown error')[:50]}")

        # Summary
        pass_count = sum(1 for v in validations if v.get('validation') == 'PASS')
        warn_count = sum(1 for v in validations if v.get('validation') == 'WARN')
        error_count = sum(1 for v in validations if v.get('validation') == 'ERROR')

        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"✅ Pass: {pass_count}/{len(validations)}")
        print(f"⚠️  Warn: {warn_count}/{len(validations)}")
        print(f"❌ Error: {error_count}/{len(validations)}")

        # Save results
        with open('/tmp/corr_validation_results_fixed.json', 'w') as f:
            json.dump(validations, f, indent=2, default=str)
        print(f"\nResults saved to: /tmp/corr_validation_results_fixed.json")

        return 0 if error_count == 0 else 1

    # Generation mode
    results = []
    successful = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for variant, pair, asset in tasks:
            future = executor.submit(generate_corr_table, client, variant, pair, asset, args.dry_run)
            futures[future] = (variant, pair, asset)

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result['status'] == 'SUCCESS':
                successful += 1
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] ✅ {result['table']}: {result['rows']:,} rows")
            elif result['status'] == 'DRY_RUN':
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🔍 {result['table']}: Would regenerate")
            else:
                failed += 1
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] ❌ {result['table']}: {result.get('error', 'Unknown')[:50]}")

    print()
    print("=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{len(tasks)}")
    print(f"❌ Failed: {failed}/{len(tasks)}")
    print(f"Success rate: {(successful/len(tasks)*100) if tasks else 0:.1f}%")
    print()

    # Save results
    output_file = '/tmp/corr_generation_results_fixed.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'dry_run' if args.dry_run else 'generation',
            'total_tables': len(tasks),
            'successful': successful,
            'failed': failed,
            'results': results
        }, f, indent=2, default=str)

    print(f"Results saved to: {output_file}")
    print(f"End time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
