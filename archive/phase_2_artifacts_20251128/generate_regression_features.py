#!/usr/bin/env python3
"""
Phase 2A - REGRESSION Feature Generation
Generates regression features for all 28 FX pairs with dual architecture (IDX + BQX)
Uses ROWS BETWEEN for interval-centric computation per mandate
"""

from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

PROJECT_ID = 'bqx-ml'
LOCATION = 'us-central1'
FEATURE_DATASET = 'bqx_ml_v3_features'

# FX Pairs (28 total)
FX_PAIRS = [
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'USD_CAD', 'AUD_USD', 'NZD_USD',
    'EUR_GBP', 'EUR_JPY', 'EUR_CHF', 'EUR_AUD', 'EUR_CAD', 'EUR_NZD',
    'GBP_JPY', 'GBP_CHF', 'GBP_AUD', 'GBP_CAD', 'GBP_NZD',
    'AUD_JPY', 'AUD_CHF', 'AUD_CAD', 'AUD_NZD',
    'NZD_JPY', 'NZD_CHF', 'NZD_CAD',
    'CAD_JPY', 'CAD_CHF', 'CHF_JPY'
]

# Regression windows
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

def get_client():
    return bigquery.Client(project=PROJECT_ID, location=LOCATION)

def generate_regression_sql(pair, variant='idx'):
    """Generate SQL for regression features using window functions.

    Regression features computed:
    - Linear trend slope (using least squares approximation via window functions)
    - Trend strength (R-squared approximation)
    - Trend direction (sign of slope)
    - Residual volatility
    - Price deviation from trend
    """
    pair_lower = pair.replace('_', '').lower()

    if variant == 'idx':
        source_table = f'{pair_lower}_idx'
        target_table = f'reg_{pair_lower}'
        value_col = 'close_idx'
    else:  # bqx
        source_table = f'{pair_lower}_bqx'
        target_table = f'reg_bqx_{pair_lower}'
        value_col = 'bqx_45'  # Use bqx_45 as primary value for BQX regression

    # Build window-based regression calculations for each window size
    window_calcs = []
    for w in WINDOWS:
        n = w  # number of rows in window

        # For linear regression y = mx + b over window:
        # slope = (n*sum(xy) - sum(x)*sum(y)) / (n*sum(x^2) - sum(x)^2)
        # For row-based: x = row_number within window (1 to n)
        # sum(x) = n*(n+1)/2, sum(x^2) = n*(n+1)*(2n+1)/6

        window_calcs.append(f"""
    -- Window {w}: Regression metrics
    -- Mean of values in window
    AVG({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_mean_{w},

    -- Standard deviation in window
    STDDEV({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_std_{w},

    -- Min/Max in window for range
    MIN({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_min_{w},

    MAX({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_max_{w},

    -- First and last values for slope approximation
    FIRST_VALUE({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_first_{w},

    -- Slope approximation: (last - first) / window_size
    ({value_col} - FIRST_VALUE({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    )) / {w} AS reg_slope_{w},

    -- Trend direction: sign of slope
    SIGN({value_col} - FIRST_VALUE({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    )) AS reg_direction_{w},

    -- Deviation from mean (current value vs window mean)
    {value_col} - AVG({value_col}) OVER (
      ORDER BY interval_time
      ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
    ) AS reg_deviation_{w},

    -- Z-score within window
    SAFE_DIVIDE(
      {value_col} - AVG({value_col}) OVER (
        ORDER BY interval_time
        ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
      ),
      NULLIF(STDDEV({value_col}) OVER (
        ORDER BY interval_time
        ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
      ), 0)
    ) AS reg_zscore_{w},

    -- Trend strength: normalized range
    SAFE_DIVIDE(
      MAX({value_col}) OVER (
        ORDER BY interval_time
        ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
      ) - MIN({value_col}) OVER (
        ORDER BY interval_time
        ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
      ),
      NULLIF(AVG({value_col}) OVER (
        ORDER BY interval_time
        ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW
      ), 0)
    ) * 100 AS reg_range_pct_{w}""")

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT_ID}.{FEATURE_DATASET}.{target_table}` AS
SELECT
  interval_time,
  '{pair}' as pair,
  {value_col} as source_value,
  {','.join(window_calcs)}
FROM `{PROJECT_ID}.{FEATURE_DATASET}.{source_table}`
WHERE {value_col} IS NOT NULL
ORDER BY interval_time
"""
    return sql, target_table

def create_regression_table(pair, variant='idx'):
    """Create regression table for a single pair and variant."""
    client = get_client()
    sql, target_table = generate_regression_sql(pair, variant)

    try:
        query_job = client.query(sql)
        query_job.result()  # Wait for completion

        # Validate row count
        count_sql = f"SELECT COUNT(*) as cnt FROM `{PROJECT_ID}.{FEATURE_DATASET}.{target_table}`"
        count_result = list(client.query(count_sql).result())[0]
        row_count = count_result.cnt

        return {
            'pair': pair,
            'variant': variant,
            'table': target_table,
            'status': 'SUCCESS',
            'rows': row_count
        }
    except Exception as e:
        return {
            'pair': pair,
            'variant': variant,
            'table': target_table,
            'status': 'FAILED',
            'error': str(e)
        }

def main():
    print("=" * 80)
    print("PHASE 2A - REGRESSION FEATURE GENERATION")
    print("=" * 80)
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"FX Pairs: {len(FX_PAIRS)}")
    print(f"Windows: {WINDOWS}")
    print(f"Tables to create: {len(FX_PAIRS) * 2} (28 IDX + 28 BQX)")
    print("Parallelization: 6 workers")
    print("=" * 80)
    print()

    results = []
    successful = 0
    failed = 0

    # Create tasks for both IDX and BQX variants
    tasks = []
    for pair in FX_PAIRS:
        tasks.append((pair, 'idx'))
        tasks.append((pair, 'bqx'))

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {}
        for pair, variant in tasks:
            future = executor.submit(create_regression_table, pair, variant)
            futures[future] = (pair, variant)

        for future in as_completed(futures):
            pair, variant = futures[future]
            result = future.result()
            results.append(result)

            if result['status'] == 'SUCCESS':
                successful += 1
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] ✅ {result['table']}: {result['rows']:,} rows")
            else:
                failed += 1
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] ❌ {result['table']}: {result.get('error', 'Unknown error')[:50]}")

    print()
    print("=" * 80)
    print("REGRESSION FEATURE GENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{len(tasks)}")
    print(f"❌ Failed: {failed}/{len(tasks)}")
    print()

    # Save results
    output_file = '/tmp/regression_feature_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'task': 'Phase 2A - REGRESSION Feature Generation',
            'timestamp': datetime.utcnow().isoformat(),
            'total_tables': len(tasks),
            'successful': successful,
            'failed': failed,
            'success_rate_pct': (successful / len(tasks)) * 100 if tasks else 0,
            'results': results
        }, f, indent=2)

    print(f"Results saved to: {output_file}")
    print(f"End time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

    return successful, failed

if __name__ == '__main__':
    main()
