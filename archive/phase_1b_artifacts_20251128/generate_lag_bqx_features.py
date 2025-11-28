#!/usr/bin/env python3
"""
Phase 1B - Task 1B.1: BQX LAG Feature Generation
Generates LAG features using BQX tables as source (momentum-based features).
"""

import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# All 28 FX pairs
FX_PAIRS = [
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'USD_CAD',
    'AUD_USD', 'NZD_USD', 'EUR_GBP', 'EUR_JPY', 'EUR_CHF',
    'EUR_AUD', 'EUR_CAD', 'EUR_NZD', 'GBP_JPY', 'GBP_CHF',
    'GBP_AUD', 'GBP_CAD', 'GBP_NZD', 'AUD_JPY', 'AUD_CHF',
    'AUD_CAD', 'AUD_NZD', 'NZD_JPY', 'NZD_CHF', 'NZD_CAD',
    'CAD_JPY', 'CAD_CHF', 'CHF_JPY'
]

# Lookback periods (in minutes)
LOOKBACK_PERIODS = [45, 90]

PROJECT_ID = 'bqx-ml'
LOCATION = 'us-central1'
FEATURE_DATASET = 'bqx_ml_v3_features'


def create_lag_bqx_features_sql(pair, period):
    """
    Generate SQL for creating BQX LAG features table.

    Uses {pair}_bqx table as source (BQX momentum scores).
    Pattern identical to IDX LAG, but using BQX data.
    """
    pair_lower = pair.replace('_', '').lower()

    # Determine which BQX column to use based on period
    bqx_col = f'bqx_{period}'  # e.g., bqx_45, bqx_90

    bqx_table = f'{FEATURE_DATASET}.{pair_lower}_bqx'
    output_table = f'{FEATURE_DATASET}.lag_bqx_{pair_lower}_{period}'

    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{output_table}` AS
    WITH base AS (
      SELECT
        interval_time,
        '{pair}' as pair,
        {period} as period_minutes,
        {bqx_col} as bqx_value,
        -- Calculate 1-minute return for volatility calculations
        ({bqx_col} - LAG({bqx_col}, 1) OVER (ORDER BY interval_time)) /
          NULLIF(LAG({bqx_col}, 1) OVER (ORDER BY interval_time), 0) AS bqx_return_1min,
        ROW_NUMBER() OVER (ORDER BY interval_time) AS row_num
      FROM `{PROJECT_ID}.{bqx_table}`
      WHERE {bqx_col} IS NOT NULL
    ),
    lagged AS (
      SELECT
        interval_time,
        pair,
        period_minutes,
        bqx_value as bqx_close,

        -- Lagged BQX values at period intervals
        LAG(bqx_value, {period}) OVER (ORDER BY interval_time) AS bqx_lag_{period},

        -- Returns over lag window
        (bqx_value - LAG(bqx_value, {period}) OVER (ORDER BY interval_time)) /
          NULLIF(LAG(bqx_value, {period}) OVER (ORDER BY interval_time), 0) AS return_lag_{period},

        -- Simple moving average
        AVG(bqx_value) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period} PRECEDING AND CURRENT ROW
        ) AS sma_{period},

        -- Exponential moving average approximation
        AVG(bqx_value) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period//2} PRECEDING AND CURRENT ROW
        ) AS ema_{period},

        -- Volatility (stddev of 1-min returns over window)
        STDDEV(bqx_return_1min) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period} PRECEDING AND CURRENT ROW
        ) AS volatility_{period},

        -- High-Low range
        MAX(bqx_value) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period} PRECEDING AND CURRENT ROW
        ) - MIN(bqx_value) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period} PRECEDING AND CURRENT ROW
        ) AS hl_range_{period},

        -- Momentum (rate of change)
        (bqx_value - LAG(bqx_value, {period}) OVER (ORDER BY interval_time)) /
          NULLIF(ABS(LAG(bqx_value, {period}) OVER (ORDER BY interval_time)), 0) * 100
          AS momentum_{period},

        -- RSI-like indicator (percentage of positive changes)
        AVG(CASE WHEN bqx_return_1min > 0 THEN 1.0 ELSE 0.0 END) OVER (
          ORDER BY interval_time
          ROWS BETWEEN {period} PRECEDING AND CURRENT ROW
        ) * 100 AS positive_ratio_{period},

        row_num

      FROM base
      WHERE bqx_return_1min IS NOT NULL
    )
    SELECT
      interval_time,
      pair,
      period_minutes,
      bqx_close,
      bqx_lag_{period},
      return_lag_{period},
      sma_{period},
      ema_{period},
      volatility_{period},
      hl_range_{period},
      momentum_{period},
      positive_ratio_{period}
    FROM lagged
    WHERE row_num > {period}  -- Ensure full window available
    ORDER BY interval_time
    """

    return sql


def execute_bq_query(sql, description):
    """Execute BigQuery SQL query."""
    try:
        cmd = [
            'bq', 'query',
            f'--project_id={PROJECT_ID}',
            f'--location={LOCATION}',
            '--use_legacy_sql=false',
            '--format=json',
            '--nouse_cache',
            sql
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes per table
        )

        if result.returncode != 0:
            return {
                'success': False,
                'description': description,
                'error': result.stderr
            }

        return {
            'success': True,
            'description': description,
            'output': result.stdout
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'description': description,
            'error': 'Query timeout (30 minutes)'
        }
    except Exception as e:
        return {
            'success': False,
            'description': description,
            'error': str(e)
        }


def validate_lag_bqx_table(pair, period):
    """Validate BQX LAG feature table."""
    pair_lower = pair.replace('_', '').lower()
    table_name = f'lag_bqx_{pair_lower}_{period}'

    validation_sql = f"""
    SELECT
      COUNT(*) as total_rows,
      COUNTIF(bqx_lag_{period} IS NOT NULL) as has_bqx_lag,
      COUNTIF(return_lag_{period} IS NOT NULL) as has_return_lag,
      COUNTIF(sma_{period} IS NOT NULL) as has_sma,
      COUNTIF(volatility_{period} IS NOT NULL) as has_volatility,
      ROUND(MIN(return_lag_{period}), 4) as min_return,
      ROUND(MAX(return_lag_{period}), 4) as max_return,
      ROUND(AVG(volatility_{period}), 6) as avg_volatility
    FROM `{PROJECT_ID}.{FEATURE_DATASET}.{table_name}`
    """

    result = execute_bq_query(validation_sql, f"Validate {table_name}")

    if result['success']:
        try:
            data = json.loads(result['output'])
            if data:
                stats = data[0]
                total = int(stats['total_rows'])
                return {
                    'pair': pair,
                    'period': period,
                    'table': table_name,
                    'status': 'success',
                    'total_rows': total,
                    'bqx_lag_coverage_pct': round(int(stats['has_bqx_lag']) / total * 100, 2) if total > 0 else 0,
                    'return_coverage_pct': round(int(stats['has_return_lag']) / total * 100, 2) if total > 0 else 0,
                    'sma_coverage_pct': round(int(stats['has_sma']) / total * 100, 2) if total > 0 else 0,
                    'volatility_coverage_pct': round(int(stats['has_volatility']) / total * 100, 2) if total > 0 else 0,
                    'return_range': f"{stats['min_return']} to {stats['max_return']}",
                    'avg_volatility': float(stats['avg_volatility']) if stats['avg_volatility'] else 0
                }
        except Exception as e:
            return {
                'pair': pair,
                'period': period,
                'table': table_name,
                'status': 'error',
                'error': f"Validation parse error: {str(e)}"
            }

    return {
        'pair': pair,
        'period': period,
        'table': table_name,
        'status': 'error',
        'error': result.get('error', 'Unknown validation error')
    }


def generate_lag_bqx_features_for_pair(pair, period):
    """Generate BQX LAG features for a single pair and period."""
    pair_lower = pair.replace('_', '').lower()
    table_name = f'lag_bqx_{pair_lower}_{period}'

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating {table_name}...")

    sql = create_lag_bqx_features_sql(pair, period)
    result = execute_bq_query(sql, f"Create {table_name}")

    if not result['success']:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ FAILED: {table_name} - {result['error'][:200]}")
        return {
            'pair': pair,
            'period': period,
            'table': table_name,
            'status': 'failed',
            'error': result['error']
        }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Created {table_name}, validating...")

    # Validate the table
    validation = validate_lag_bqx_table(pair, period)

    if validation['status'] == 'success':
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {table_name}: {validation['total_rows']:,} rows, "
              f"{validation['bqx_lag_coverage_pct']}% coverage")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {table_name}: Validation issue - {validation.get('error', 'unknown')[:100]}")

    return validation


def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print(f"PHASE 1B - TASK 1B.1: BQX LAG FEATURE GENERATION")
    print(f"{'='*80}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"FX Pairs: {len(FX_PAIRS)}")
    print(f"Lookback periods: {LOOKBACK_PERIODS}")
    print(f"Total tables to create: {len(FX_PAIRS) * len(LOOKBACK_PERIODS)}")
    print(f"Parallelization: 6 workers")
    print(f"{'='*80}\n")

    # Generate all pair-period combinations
    tasks = []
    for pair in FX_PAIRS:
        for period in LOOKBACK_PERIODS:
            tasks.append((pair, period))

    results = []

    # Process in parallel (6 concurrent workers)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(generate_lag_bqx_features_for_pair, pair, period): (pair, period)
            for pair, period in tasks
        }

        for future in as_completed(futures):
            pair, period = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Exception for {pair}_{period}: {str(e)}")
                results.append({
                    'pair': pair,
                    'period': period,
                    'status': 'exception',
                    'error': str(e)
                })

    # Generate summary
    print(f"\n{'='*80}")
    print(f"TASK 1B.1 SUMMARY")
    print(f"{'='*80}")

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']

    print(f"✅ Successful: {len(successful)}/{len(tasks)}")
    print(f"❌ Failed: {len(failed)}/{len(tasks)}")

    if failed:
        print(f"\nFailed tables:")
        for r in failed:
            print(f"  - {r.get('table', 'unknown')}: {r.get('error', 'unknown error')[:100]}")

    # Save results
    output_file = '/tmp/task_1b_1_lag_bqx_generation_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'task': 'Task 1B.1 - BQX LAG Feature Generation',
            'timestamp': datetime.now().isoformat(),
            'total_tables': len(tasks),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate_pct': round(len(successful) / len(tasks) * 100, 2),
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*80}\n")

    return len(successful) == len(tasks)


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
