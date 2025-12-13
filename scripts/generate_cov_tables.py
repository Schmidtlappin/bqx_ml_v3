#!/usr/bin/env python3
"""
Tier 1 Remediation: Covariance Feature Table Generation
Regenerates cov_* tables with 100% row coverage using FULL OUTER JOIN strategy
"""

from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import sys
import itertools

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

# Variants: agg (aggregation), align (aligned), reg (regression), etc.
VARIANTS = ['agg', 'align']

# Source variants: bqx, idx
SOURCE_VARIANTS = ['bqx', 'idx']

def generate_cov_sql(variant, source_variant, pair1, pair2, validate_only=False):
    """Generate SQL for pair relationship table with 100% row coverage.

    Calculates spread (val1 - val2) and ratio (val1 / val2) metrics,
    NOT covariance/correlation despite table name.

    Args:
        variant: Table variant (agg, align)
        source_variant: Source data variant (bqx, idx)
        pair1: First currency pair
        pair2: Second currency pair
        validate_only: If True, return validation query instead
    """

    # Table naming: BQX uses old naming (cov_agg_pair1_pair2), IDX uses new naming (cov_agg_idx_pair1_pair2)
    if source_variant == 'bqx':
        table_name = f"cov_{variant}_{pair1}_{pair2}"
    else:  # idx
        table_name = f"cov_{variant}_idx_{pair1}_{pair2}"

    # Source tables
    source_table_1 = f"base_{source_variant}_{pair1}"
    source_table_2 = f"base_{source_variant}_{pair2}"

    # Value column depends on source variant
    if source_variant == 'bqx':
        value_col = 'bqx_45'  # Use 45-minute BQX oscillator
    else:
        value_col = 'close_idx'  # Use closing price for idx

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
            FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_1}`
            UNION DISTINCT
            SELECT DISTINCT interval_time
            FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_2}`
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

    # Generation SQL - match actual COV table schema
    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair1
    AS
    WITH
      all_intervals AS (
        -- Get ALL unique interval_times from both pairs
        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_1}`
        WHERE interval_time BETWEEN '2020-01-01' AND '2025-11-21'

        UNION DISTINCT

        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_2}`
        WHERE interval_time BETWEEN '2020-01-01' AND '2025-11-21'
      ),
      pair1_data AS (
        SELECT interval_time, {value_col} as val1
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_1}`
      ),
      pair2_data AS (
        SELECT interval_time, {value_col} as val2
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_2}`
      ),
      combined_data AS (
        SELECT
          ai.interval_time,
          p1.val1,
          p2.val2,
          -- Spread and ratio calculations
          p1.val1 - p2.val2 as spread,
          SAFE_DIVIDE(p1.val1, p2.val2) as ratio,
          -- Sign agreement
          IF(SIGN(p1.val1) = SIGN(p2.val2), 1, 0) as sign_agreement
        FROM all_intervals ai
        LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
        LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
      )
    SELECT
      interval_time,
      '{pair1}' as pair1,
      '{pair2}' as pair2,
      val1,
      val2,
      spread,
      ratio,
      -- Spread moving averages
      AVG(spread) OVER w45 as spread_ma_45,
      AVG(spread) OVER w180 as spread_ma_180,
      -- Spread standard deviation
      STDDEV(spread) OVER w45 as spread_std_45,
      -- Spread Z-score
      SAFE_DIVIDE(
        spread - AVG(spread) OVER w180,
        NULLIF(STDDEV(spread) OVER w180, 0)
      ) as spread_zscore,
      sign_agreement,
      -- Rolling agreement
      AVG(sign_agreement) OVER w45 as rolling_agreement_45,
      -- Mean reversion signal
      IF(ABS(SAFE_DIVIDE(
        spread - AVG(spread) OVER w180,
        NULLIF(STDDEV(spread) OVER w180, 0)
      )) > 2, 1, 0) as mean_reversion_signal
    FROM combined_data
    WINDOW
      w45 AS (ORDER BY interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
      w180 AS (ORDER BY interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
    """

    return sql


def validate_table(client, variant, source_variant, pair1, pair2):
    """Validate regenerated table against original."""
    if source_variant == 'bqx':
        table_name = f"cov_{variant}_{pair1}_{pair2}"
    else:
        table_name = f"cov_{variant}_idx_{pair1}_{pair2}"

    try:
        validation_sql = generate_cov_sql(variant, source_variant, pair1, pair2, validate_only=True)
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


def generate_cov_table(client, variant, source_variant, pair1, pair2, dry_run=False):
    """Generate a single covariance table."""
    if source_variant == 'bqx':
        table_name = f"cov_{variant}_{pair1}_{pair2}"
    else:
        table_name = f"cov_{variant}_idx_{pair1}_{pair2}"

    if dry_run:
        return {'table': table_name, 'status': 'DRY_RUN'}

    try:
        # Generate table
        sql = generate_cov_sql(variant, source_variant, pair1, pair2)
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
    parser = argparse.ArgumentParser(description='Generate covariance feature tables')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not regenerate')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - show what would be generated')
    parser.add_argument('--workers', type=int, default=16, help='Number of parallel workers')
    parser.add_argument('--test-only', action='store_true', help='Test on 3 tables only')
    parser.add_argument('--bqx-only', action='store_true', help='Only regenerate BQX variant (skip IDX)')
    parser.add_argument('--idx-only', action='store_true', help='Only regenerate IDX variant (skip BQX)')
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT, location=LOCATION)

    print("=" * 80)
    print("TIER 1: COVARIANCE TABLE GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Mode: {'VALIDATION ONLY' if args.validate_only else 'DRY RUN' if args.dry_run else 'GENERATION'}")
    print(f"Workers: {args.workers}")

    # Determine which source variants to generate
    source_variants = []
    if args.bqx_only:
        source_variants = ['bqx']
    elif args.idx_only:
        source_variants = ['idx']
    else:
        source_variants = SOURCE_VARIANTS  # Both BQX and IDX

    print(f"Source Variants: {', '.join(source_variants).upper()}")
    print("=" * 80)
    print()

    # Generate all pair combinations (excluding self-pairs)
    tasks = []
    for source_variant in source_variants:
        for variant in VARIANTS:
            for pair1, pair2 in itertools.combinations(PAIRS, 2):
                tasks.append((variant, source_variant, pair1, pair2))

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
            for variant, source_variant, pair1, pair2 in tasks:
                future = executor.submit(validate_table, client, variant, source_variant, pair1, pair2)
                futures[future] = (variant, source_variant, pair1, pair2)

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
        with open('/tmp/cov_validation_results.json', 'w') as f:
            json.dump(validations, f, indent=2, default=str)
        print(f"\nResults saved to: /tmp/cov_validation_results.json")

        return 0 if error_count == 0 else 1

    # Generation mode
    results = []
    successful = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for variant, source_variant, pair1, pair2 in tasks:
            future = executor.submit(generate_cov_table, client, variant, source_variant, pair1, pair2, args.dry_run)
            futures[future] = (variant, source_variant, pair1, pair2)

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result['status'] == 'SUCCESS':
                successful += 1
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] ✅ {result['table']}: {result['rows']:,} rows")
            elif result['status'] == 'DRY_RUN':
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] 🔍 {result['table']}: Would generate")
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
    output_file = '/tmp/cov_generation_results.json'
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
