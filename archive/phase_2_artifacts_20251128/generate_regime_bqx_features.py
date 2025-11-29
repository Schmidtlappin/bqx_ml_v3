#!/usr/bin/env python3
"""
Phase 1B - Task 1B.2: BQX REGIME Feature Generation
Generates volatility regime features using BQX LAG tables as source.
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


def create_regime_bqx_features_sql(pair, period):
    """
    Generate SQL for creating BQX REGIME features table.

    Uses lag_bqx_{pair}_{period} table as source.
    Pattern identical to IDX REGIME, but using BQX LAG features.
    """
    pair_lower = pair.replace('_', '').lower()
    lag_bqx_table = f'{FEATURE_DATASET}.lag_bqx_{pair_lower}_{period}'
    output_table = f'{FEATURE_DATASET}.regime_bqx_{pair_lower}_{period}'

    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{output_table}` AS
    WITH lag_data AS (
      SELECT
        lag.interval_time,
        '{pair}' as pair,
        {period} as period_minutes,
        lag.volatility_{period},
        lag.hl_range_{period},
        lag.return_lag_{period},
        lag.bqx_close,
        lag.momentum_{period}
      FROM `{PROJECT_ID}.{lag_bqx_table}` lag
    ),
    percentiles AS (
      SELECT
        APPROX_QUANTILES(volatility_{period}, 100) AS vol_percentiles,
        APPROX_QUANTILES(hl_range_{period}, 100) AS range_percentiles,
        APPROX_QUANTILES(ABS(return_lag_{period}), 100) AS abs_return_percentiles,
        APPROX_QUANTILES(ABS(momentum_{period}), 100) AS abs_momentum_percentiles
      FROM lag_data
      WHERE volatility_{period} IS NOT NULL
    ),
    regimes AS (
      SELECT
        ld.interval_time,
        ld.pair,
        ld.period_minutes,
        ld.volatility_{period},
        ld.hl_range_{period},
        ld.return_lag_{period},
        ld.bqx_close,
        ld.momentum_{period},

        -- Volatility regime (low/medium/high based on percentiles)
        CASE
          WHEN ld.volatility_{period} <= p.vol_percentiles[OFFSET(33)] THEN 'low'
          WHEN ld.volatility_{period} <= p.vol_percentiles[OFFSET(66)] THEN 'medium'
          ELSE 'high'
        END AS volatility_regime,

        -- Range regime
        CASE
          WHEN ld.hl_range_{period} <= p.range_percentiles[OFFSET(33)] THEN 'low'
          WHEN ld.hl_range_{period} <= p.range_percentiles[OFFSET(66)] THEN 'medium'
          ELSE 'high'
        END AS range_regime,

        -- Return regime (absolute returns)
        CASE
          WHEN ABS(ld.return_lag_{period}) <= p.abs_return_percentiles[OFFSET(33)] THEN 'low'
          WHEN ABS(ld.return_lag_{period}) <= p.abs_return_percentiles[OFFSET(66)] THEN 'medium'
          ELSE 'high'
        END AS return_regime,

        -- Momentum regime (unique to BQX)
        CASE
          WHEN ABS(ld.momentum_{period}) <= p.abs_momentum_percentiles[OFFSET(33)] THEN 'low'
          WHEN ABS(ld.momentum_{period}) <= p.abs_momentum_percentiles[OFFSET(66)] THEN 'medium'
          ELSE 'high'
        END AS momentum_regime,

        -- Numeric encoding for regimes (for model training)
        CASE
          WHEN ld.volatility_{period} <= p.vol_percentiles[OFFSET(33)] THEN 1
          WHEN ld.volatility_{period} <= p.vol_percentiles[OFFSET(66)] THEN 2
          ELSE 3
        END AS volatility_regime_code,

        CASE
          WHEN ld.hl_range_{period} <= p.range_percentiles[OFFSET(33)] THEN 1
          WHEN ld.hl_range_{period} <= p.range_percentiles[OFFSET(66)] THEN 2
          ELSE 3
        END AS range_regime_code,

        CASE
          WHEN ABS(ld.return_lag_{period}) <= p.abs_return_percentiles[OFFSET(33)] THEN 1
          WHEN ABS(ld.return_lag_{period}) <= p.abs_return_percentiles[OFFSET(66)] THEN 2
          ELSE 3
        END AS return_regime_code,

        CASE
          WHEN ABS(ld.momentum_{period}) <= p.abs_momentum_percentiles[OFFSET(33)] THEN 1
          WHEN ABS(ld.momentum_{period}) <= p.abs_momentum_percentiles[OFFSET(66)] THEN 2
          ELSE 3
        END AS momentum_regime_code,

        -- Percentile values (for reference)
        p.vol_percentiles[OFFSET(33)] as vol_p33,
        p.vol_percentiles[OFFSET(66)] as vol_p66,
        p.range_percentiles[OFFSET(33)] as range_p33,
        p.range_percentiles[OFFSET(66)] as range_p66,
        p.abs_momentum_percentiles[OFFSET(33)] as momentum_p33,
        p.abs_momentum_percentiles[OFFSET(66)] as momentum_p66

      FROM lag_data ld
      CROSS JOIN percentiles p
    )
    SELECT
      interval_time,
      pair,
      period_minutes,
      volatility_{period},
      hl_range_{period},
      return_lag_{period},
      momentum_{period},
      volatility_regime,
      range_regime,
      return_regime,
      momentum_regime,
      volatility_regime_code,
      range_regime_code,
      return_regime_code,
      momentum_regime_code,
      vol_p33,
      vol_p66,
      range_p33,
      range_p66,
      momentum_p33,
      momentum_p66
    FROM regimes
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


def validate_regime_bqx_table(pair, period):
    """Validate BQX REGIME feature table."""
    pair_lower = pair.replace('_', '').lower()
    table_name = f'regime_bqx_{pair_lower}_{period}'

    validation_sql = f"""
    SELECT
      COUNT(*) as total_rows,
      COUNTIF(volatility_regime IS NOT NULL) as has_vol_regime,
      COUNTIF(range_regime IS NOT NULL) as has_range_regime,
      COUNTIF(return_regime IS NOT NULL) as has_return_regime,
      COUNTIF(momentum_regime IS NOT NULL) as has_momentum_regime,
      COUNTIF(volatility_regime = 'low') as vol_low_count,
      COUNTIF(volatility_regime = 'medium') as vol_medium_count,
      COUNTIF(volatility_regime = 'high') as vol_high_count,
      COUNTIF(momentum_regime = 'low') as momentum_low_count,
      COUNTIF(momentum_regime = 'medium') as momentum_medium_count,
      COUNTIF(momentum_regime = 'high') as momentum_high_count
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
                    'vol_regime_coverage_pct': round(int(stats['has_vol_regime']) / total * 100, 2),
                    'range_regime_coverage_pct': round(int(stats['has_range_regime']) / total * 100, 2),
                    'return_regime_coverage_pct': round(int(stats['has_return_regime']) / total * 100, 2),
                    'momentum_regime_coverage_pct': round(int(stats['has_momentum_regime']) / total * 100, 2),
                    'vol_regime_distribution': {
                        'low': int(stats['vol_low_count']),
                        'medium': int(stats['vol_medium_count']),
                        'high': int(stats['vol_high_count'])
                    },
                    'momentum_regime_distribution': {
                        'low': int(stats['momentum_low_count']),
                        'medium': int(stats['momentum_medium_count']),
                        'high': int(stats['momentum_high_count'])
                    }
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


def generate_regime_bqx_features_for_pair(pair, period):
    """Generate BQX REGIME features for a single pair and period."""
    pair_lower = pair.replace('_', '').lower()
    table_name = f'regime_bqx_{pair_lower}_{period}'

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating {table_name}...")

    sql = create_regime_bqx_features_sql(pair, period)
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
    validation = validate_regime_bqx_table(pair, period)

    if validation['status'] == 'success':
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {table_name}: {validation['total_rows']:,} rows, "
              f"{validation['vol_regime_coverage_pct']}% vol coverage")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {table_name}: Validation issue - {validation.get('error', 'unknown')[:100]}")

    return validation


def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print(f"PHASE 1B - TASK 1B.2: BQX REGIME FEATURE GENERATION")
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
            executor.submit(generate_regime_bqx_features_for_pair, pair, period): (pair, period)
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
    print(f"TASK 1B.2 SUMMARY")
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
    output_file = '/tmp/task_1b_2_regime_bqx_generation_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'task': 'Task 1B.2 - BQX REGIME Feature Generation',
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
