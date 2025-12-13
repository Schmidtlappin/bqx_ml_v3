#!/usr/bin/env python3
"""
Tier 1 Remediation: Triangulation Feature Table Generation
Regenerates tri_* tables with 100% row coverage using FULL OUTER JOIN strategy
"""

from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import sys

PROJECT = 'bqx-ml'
FEATURES_DATASET = 'bqx_ml_v3_features_v2'
LOCATION = 'us-central1'

# Currency triangles - all valid 3-currency combinations
# Format: (base, quote, cross) where base/quote * quote/cross ≈ base/cross
TRIANGLES = [
    # EUR-based triangles
    ('eur', 'usd', 'gbp'),  # EURUSD * USDGBP ≈ EURGBP
    ('eur', 'usd', 'jpy'),  # EURUSD * USDJPY ≈ EURJPY
    ('eur', 'usd', 'chf'),
    ('eur', 'usd', 'aud'),
    ('eur', 'usd', 'cad'),
    ('eur', 'usd', 'nzd'),
    # GBP-based triangles
    ('gbp', 'usd', 'jpy'),
    ('gbp', 'usd', 'chf'),
    ('gbp', 'usd', 'aud'),
    ('gbp', 'usd', 'cad'),
    ('gbp', 'usd', 'nzd'),
    # AUD-based triangles
    ('aud', 'usd', 'jpy'),
    ('aud', 'usd', 'chf'),
    ('aud', 'usd', 'cad'),
    ('aud', 'usd', 'nzd'),
    # NZD-based triangles
    ('nzd', 'usd', 'jpy'),
    ('nzd', 'usd', 'chf'),
    ('nzd', 'usd', 'cad'),
]

# Variants: agg (aggregation) and align (aligned)
VARIANTS = ['agg', 'align']

# Source variants: bqx (momentum oscillator) and idx (price index)
SOURCE_VARIANTS = ['bqx', 'idx']


def get_pair_name(curr1, curr2):
    """Convert currency pair to standard format."""
    return f"{curr1}{curr2}"


def get_standard_pair_direction(curr1, curr2):
    """Determine which direction exists for a currency pair.
    Returns (pair_name, needs_invert) tuple.

    FX market conventions:
    - Major pairs with USD: EURUSD, GBPUSD, AUDUSD, NZDUSD
    - USD as base: USDJPY, USDCHF, USDCAD
    - Cross pairs: Check both directions (most follow alphabetical)
    """
    # Define standard pairs (these exist in BigQuery)
    standard_usd_pairs = {'eur', 'gbp', 'aud', 'nzd'}  # These go XXX/USD

    if curr2 == 'usd' and curr1 in standard_usd_pairs:
        # EURUSD, GBPUSD, AUDUSD, NZDUSD
        return (f"{curr1}{curr2}", False)
    elif curr1 == 'usd' and curr2 in standard_usd_pairs:
        # USD/EUR → Use EURUSD inverted
        return (f"{curr2}{curr1}", True)
    elif curr1 == 'usd':
        # USDJPY, USDCHF, USDCAD
        return (f"{curr1}{curr2}", False)
    elif curr2 == 'usd':
        # JPY/USD → Use USDJPY inverted
        return (f"{curr2}{curr1}", True)
    else:
        # Cross pairs - try alphabetical order first
        if curr1 < curr2:
            return (f"{curr1}{curr2}", False)
        else:
            return (f"{curr2}{curr1}", True)


def generate_tri_sql(variant, source_variant, base_curr, quote_curr, cross_curr, validate_only=False):
    """Generate SQL for triangulation table with 100% row coverage."""

    # Table names
    table_name = f"tri_{variant}_{source_variant}_{base_curr}_{quote_curr}_{cross_curr}"

    # Source tables (base_bqx_* or base_idx_*)
    pair1 = get_pair_name(base_curr, quote_curr)   # e.g., eurusd
    pair3 = get_pair_name(base_curr, cross_curr)   # e.g., eurgbp

    # Determine correct direction for pair2 (might need inversion)
    pair2_actual, pair2_needs_invert = get_standard_pair_direction(quote_curr, cross_curr)

    source_table_1 = f"base_{source_variant}_{pair1}"
    source_table_2 = f"base_{source_variant}_{pair2_actual}"
    source_table_3 = f"base_{source_variant}_{pair3}"

    # Value column depends on source variant
    if source_variant == 'bqx':
        value_col = 'bqx_45'  # Use 45-minute BQX oscillator
    else:
        value_col = 'close_idx'   # Use closing price for idx

    # Validation query - compare old vs new
    # NOTE: Only use pair1 and pair3 to avoid 404 on reverse pairs
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
            FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_3}`
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

    # Generation SQL
    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    PARTITION BY DATE(interval_time)
    
    AS
    WITH
      all_intervals AS (
        -- Get ALL unique interval_times from pair1 and pair3
        -- (pair2 direction varies, so we'll handle it separately)
        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_1}`
        WHERE interval_time BETWEEN '2020-01-01' AND '2025-11-21'

        UNION DISTINCT

        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_3}`
        WHERE interval_time BETWEEN '2020-01-01' AND '2025-11-21'
      ),
      pair1_data AS (
        SELECT interval_time, {value_col} as pair1_val
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_1}`
      ),
      pair2_data AS (
        -- Use the correct pair direction (may need inversion)
        SELECT interval_time, {"SAFE_DIVIDE(1.0, " if pair2_needs_invert else ""}{value_col}{")" if pair2_needs_invert else ""} as pair2_val
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_2}`
      ),
      pair3_data AS (
        SELECT interval_time, {value_col} as pair3_val
        FROM `{PROJECT}.{FEATURES_DATASET}.{source_table_3}`
      ),
      triangle_data AS (
        SELECT
          ai.interval_time,
          p1.pair1_val,
          p2.pair2_val,
          p3.pair3_val,
          -- Synthetic value: what pair3 SHOULD be if no arbitrage
          p1.pair1_val * p2.pair2_val as synthetic_val,
          -- Triangle error: actual - synthetic
          p3.pair3_val - (p1.pair1_val * p2.pair2_val) as tri_error
        FROM all_intervals ai
        LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
        LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
        LEFT JOIN pair3_data p3 ON ai.interval_time = p3.interval_time
      )
    SELECT
      interval_time,
      '{base_curr}' as base_curr,
      '{quote_curr}' as quote_curr,
      '{cross_curr}' as cross_curr,
      pair1_val,
      pair2_val,
      pair3_val,
      synthetic_val,
      tri_error,
      -- Rolling statistics for arbitrage detection
      AVG(tri_error) OVER w45 as error_ma_45,
      AVG(tri_error) OVER w180 as error_ma_180,
      STDDEV(tri_error) OVER w180 as error_std_180,
      -- Z-score for arbitrage signal
      SAFE_DIVIDE(
        tri_error - AVG(tri_error) OVER w180,
        NULLIF(STDDEV(tri_error) OVER w180, 0)
      ) as error_zscore,
      -- Binary arbitrage flag (|z-score| > 2)
      IF(ABS(SAFE_DIVIDE(
        tri_error - AVG(tri_error) OVER w180,
        NULLIF(STDDEV(tri_error) OVER w180, 0)
      )) > 2, 1, 0) as arb_opportunity,
      -- Volatility regime
      CASE
        WHEN STDDEV(tri_error) OVER w45 > STDDEV(tri_error) OVER w180 * 1.5 THEN 'high_vol'
        WHEN STDDEV(tri_error) OVER w45 < STDDEV(tri_error) OVER w180 * 0.5 THEN 'low_vol'
        ELSE 'normal'
      END as error_regime
    FROM triangle_data
    WINDOW
      w45 AS (ORDER BY interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
      w180 AS (ORDER BY interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
    """

    return sql


def validate_table(client, variant, source_variant, base_curr, quote_curr, cross_curr):
    """Validate regenerated table against original."""
    table_name = f"tri_{variant}_{source_variant}_{base_curr}_{quote_curr}_{cross_curr}"

    try:
        validation_sql = generate_tri_sql(variant, source_variant, base_curr, quote_curr, cross_curr, validate_only=True)
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


def generate_tri_table(client, variant, source_variant, base_curr, quote_curr, cross_curr, dry_run=False):
    """Generate a single triangulation table."""
    table_name = f"tri_{variant}_{source_variant}_{base_curr}_{quote_curr}_{cross_curr}"

    if dry_run:
        return {'table': table_name, 'status': 'DRY_RUN'}

    try:
        # Generate table
        sql = generate_tri_sql(variant, source_variant, base_curr, quote_curr, cross_curr)
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
    parser = argparse.ArgumentParser(description='Generate triangulation feature tables')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not regenerate')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - show what would be generated')
    parser.add_argument('--workers', type=int, default=16, help='Number of parallel workers')
    parser.add_argument('--test-only', action='store_true', help='Test on 3 tables only')
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT, location=LOCATION)

    print("=" * 80)
    print("TIER 1: TRIANGULATION TABLE GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Mode: {'VALIDATION ONLY' if args.validate_only else 'DRY RUN' if args.dry_run else 'GENERATION'}")
    print(f"Workers: {args.workers}")
    print("=" * 80)
    print()

    # Generate task list
    tasks = []
    for variant in VARIANTS:
        for source_variant in SOURCE_VARIANTS:
            for base, quote, cross in TRIANGLES:
                tasks.append((variant, source_variant, base, quote, cross))

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
            for variant, source_variant, base, quote, cross in tasks:
                future = executor.submit(validate_table, client, variant, source_variant, base, quote, cross)
                futures[future] = (variant, source_variant, base, quote, cross)

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
        with open('/tmp/tri_validation_results.json', 'w') as f:
            json.dump(validations, f, indent=2, default=str)
        print(f"\nResults saved to: /tmp/tri_validation_results.json")

        return 0 if error_count == 0 else 1

    # Generation mode
    results = []
    successful = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for variant, source_variant, base, quote, cross in tasks:
            future = executor.submit(generate_tri_table, client, variant, source_variant, base, quote, cross, args.dry_run)
            futures[future] = (variant, source_variant, base, quote, cross)

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
    output_file = '/tmp/tri_generation_results.json'
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
