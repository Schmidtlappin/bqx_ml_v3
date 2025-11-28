#!/usr/bin/env python3
"""
Task 1.5: Regenerate BQX Tables from Real IDX Data

Replaces 50k-row synthetic BQX tables with 2.17M-row real BQX tables
computed from actual IDX data.

BQX Formula: ((close_idx - LAG(close_idx, period)) / LAG(close_idx, period)) * 100
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

PROJECT_ID = 'bqx-ml'
LOCATION = 'us-central1'
FEATURE_DATASET = 'bqx_ml_v3_features'


def create_bqx_table_sql(pair):
    """
    Generate SQL for creating BQX table from IDX source.

    BQX = backward-looking momentum (percentage change over multiple periods)
    """
    pair_lower = pair.replace('_', '').lower()
    idx_table = f'{FEATURE_DATASET}.{pair_lower}_idx'
    bqx_table = f'{FEATURE_DATASET}.{pair_lower}_bqx'

    sql = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{bqx_table}` AS
    SELECT
      interval_time,
      '{pair}' as pair,

      -- BQX 45-minute lookback (backward momentum)
      ((close_idx - LAG(close_idx, 45) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 45) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_45,

      -- Target 45 (forward momentum for prediction)
      ((LEAD(close_idx, 45) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_45,

      -- BQX 90-minute lookback
      ((close_idx - LAG(close_idx, 90) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 90) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_90,
      ((LEAD(close_idx, 90) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_90,

      -- BQX 180-minute lookback
      ((close_idx - LAG(close_idx, 180) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 180) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_180,
      ((LEAD(close_idx, 180) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_180,

      -- BQX 360-minute lookback (6 hours)
      ((close_idx - LAG(close_idx, 360) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 360) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_360,
      ((LEAD(close_idx, 360) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_360,

      -- BQX 720-minute lookback (12 hours)
      ((close_idx - LAG(close_idx, 720) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 720) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_720,
      ((LEAD(close_idx, 720) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_720,

      -- BQX 1440-minute lookback (24 hours / 1 day)
      ((close_idx - LAG(close_idx, 1440) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 1440) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_1440,
      ((LEAD(close_idx, 1440) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_1440,

      -- BQX 2880-minute lookback (48 hours / 2 days)
      ((close_idx - LAG(close_idx, 2880) OVER (ORDER BY interval_time)) /
       NULLIF(LAG(close_idx, 2880) OVER (ORDER BY interval_time), 0)) * 100 AS bqx_2880,
      ((LEAD(close_idx, 2880) OVER (ORDER BY interval_time) - close_idx) /
       NULLIF(close_idx, 0)) * 100 AS target_2880

    FROM `{PROJECT_ID}.{idx_table}`
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


def validate_bqx_table(pair):
    """Validate BQX table against IDX source."""
    pair_lower = pair.replace('_', '').lower()
    idx_table = f'{pair_lower}_idx'
    bqx_table = f'{pair_lower}_bqx'

    validation_sql = f"""
    SELECT
      idx_table.row_count as idx_rows,
      bqx_table.row_count as bqx_rows,
      idx_table.row_count = bqx_table.row_count as rows_match,
      idx_table.earliest as idx_earliest,
      bqx_table.earliest as bqx_earliest,
      idx_table.latest as idx_latest,
      bqx_table.latest as bqx_latest
    FROM (
      SELECT
        COUNT(*) as row_count,
        MIN(interval_time) as earliest,
        MAX(interval_time) as latest
      FROM `{PROJECT_ID}.{FEATURE_DATASET}.{idx_table}`
    ) idx_table
    CROSS JOIN (
      SELECT
        COUNT(*) as row_count,
        MIN(interval_time) as earliest,
        MAX(interval_time) as latest,
        COUNTIF(bqx_45 IS NOT NULL) as bqx_45_coverage,
        COUNTIF(bqx_90 IS NOT NULL) as bqx_90_coverage
      FROM `{PROJECT_ID}.{FEATURE_DATASET}.{bqx_table}`
    ) bqx_table
    """

    result = execute_bq_query(validation_sql, f"Validate {bqx_table}")

    if result['success']:
        try:
            data = json.loads(result['output'])
            if data:
                stats = data[0]
                return {
                    'pair': pair,
                    'table': bqx_table,
                    'status': 'success',
                    'idx_rows': int(stats['idx_rows']),
                    'bqx_rows': int(stats['bqx_rows']),
                    'rows_match': stats['rows_match'],
                    'idx_time_range': f"{stats['idx_earliest']} to {stats['idx_latest']}",
                    'bqx_time_range': f"{stats['bqx_earliest']} to {stats['bqx_latest']}"
                }
        except Exception as e:
            return {
                'pair': pair,
                'table': bqx_table,
                'status': 'error',
                'error': f"Validation parse error: {str(e)}"
            }

    return {
        'pair': pair,
        'table': bqx_table,
        'status': 'error',
        'error': result.get('error', 'Unknown validation error')
    }


def regenerate_bqx_table(pair):
    """Regenerate BQX table for a single pair from IDX source."""
    pair_lower = pair.replace('_', '').lower()
    bqx_table = f'{pair_lower}_bqx'

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Regenerating {bqx_table} from IDX data...")

    sql = create_bqx_table_sql(pair)
    result = execute_bq_query(sql, f"Regenerate {bqx_table}")

    if not result['success']:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ FAILED: {bqx_table} - {result['error'][:200]}")
        return {
            'pair': pair,
            'table': bqx_table,
            'status': 'failed',
            'error': result['error']
        }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Created {bqx_table}, validating...")

    # Validate the table
    validation = validate_bqx_table(pair)

    if validation['status'] == 'success':
        match_status = "✅ MATCH" if validation['rows_match'] else "❌ MISMATCH"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {bqx_table}: {validation['bqx_rows']:,} rows {match_status}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {bqx_table}: Validation issue")

    return validation


def main():
    """Main execution function."""
    print(f"\n{'='*80}")
    print(f"TASK 1.5: BQX TABLE REGENERATION FROM REAL IDX DATA")
    print(f"{'='*80}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"FX Pairs: {len(FX_PAIRS)}")
    print(f"BQX periods: [45, 90, 180, 360, 720, 1440, 2880] minutes")
    print(f"Source: {FEATURE_DATASET}.*_idx tables (REAL historical data)")
    print(f"Target: {FEATURE_DATASET}.*_bqx tables (regenerated)")
    print(f"Parallelization: 6 workers")
    print(f"{'='*80}\n")

    results = []

    # Process in parallel (6 concurrent workers)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(regenerate_bqx_table, pair): pair
            for pair in FX_PAIRS
        }

        for future in as_completed(futures):
            pair = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Exception for {pair}: {str(e)}")
                results.append({
                    'pair': pair,
                    'status': 'exception',
                    'error': str(e)
                })

    # Generate summary
    print(f"\n{'='*80}")
    print(f"TASK 1.5 SUMMARY")
    print(f"{'='*80}")

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    row_mismatches = [r for r in successful if not r.get('rows_match', False)]

    print(f"✅ Successful: {len(successful)}/{len(FX_PAIRS)}")
    print(f"❌ Failed: {len(failed)}/{len(FX_PAIRS)}")
    print(f"⚠️  Row count mismatches: {len(row_mismatches)}")

    if failed:
        print(f"\nFailed tables:")
        for r in failed:
            print(f"  - {r.get('table', 'unknown')}: {r.get('error', 'unknown error')[:100]}")

    if row_mismatches:
        print(f"\nRow count mismatches (IDX vs BQX):")
        for r in row_mismatches:
            print(f"  - {r['table']}: IDX={r['idx_rows']:,}, BQX={r['bqx_rows']:,}")

    # Save results
    output_file = '/tmp/task_1_5_bqx_regeneration_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'task': 'Task 1.5 - BQX Table Regeneration from Real IDX Data',
            'timestamp': datetime.now().isoformat(),
            'total_tables': len(FX_PAIRS),
            'successful': len(successful),
            'failed': len(failed),
            'row_mismatches': len(row_mismatches),
            'success_rate_pct': round(len(successful) / len(FX_PAIRS) * 100, 2),
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*80}\n")

    return len(successful) == len(FX_PAIRS) and len(row_mismatches) == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
