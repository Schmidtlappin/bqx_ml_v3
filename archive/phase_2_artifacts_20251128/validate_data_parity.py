#!/usr/bin/env python3
"""
Data Parity Validation Script
Validates that IDX, BQX, LAG_BQX, and REGIME_BQX tables have matching row counts
"""

from google.cloud import bigquery
import json
from datetime import datetime

PROJECT_ID = 'bqx-ml'
LOCATION = 'us-central1'
FEATURE_DATASET = 'bqx_ml_v3_features'

# FX Pairs
FX_PAIRS = [
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'USD_CAD', 'AUD_USD', 'NZD_USD',
    'EUR_GBP', 'EUR_JPY', 'EUR_CHF', 'EUR_AUD', 'EUR_CAD', 'EUR_NZD',
    'GBP_JPY', 'GBP_CHF', 'GBP_AUD', 'GBP_CAD', 'GBP_NZD',
    'AUD_JPY', 'AUD_CHF', 'AUD_CAD', 'AUD_NZD',
    'NZD_JPY', 'NZD_CHF', 'NZD_CAD',
    'CAD_JPY', 'CAD_CHF', 'CHF_JPY'
]

BQX_PERIODS = [45, 90]

def get_table_info(client, table_name):
    """Get row count and time range for a table."""
    sql = f"""
    SELECT
        COUNT(*) as row_count,
        MIN(interval_time) as min_time,
        MAX(interval_time) as max_time
    FROM `{PROJECT_ID}.{FEATURE_DATASET}.{table_name}`
    """

    try:
        result = client.query(sql, location=LOCATION).result()
        row = list(result)[0]
        return {
            'row_count': row.row_count,
            'min_time': str(row.min_time) if row.min_time else None,
            'max_time': str(row.max_time) if row.max_time else None,
            'exists': True
        }
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def validate_pair(client, pair):
    """Validate data parity for a single FX pair."""
    pair_lower = pair.replace('_', '').lower()

    result = {
        'pair': pair,
        'idx_table': {},
        'bqx_table': {},
        'lag_tables': {},
        'regime_tables': {},
        'parity_status': 'UNKNOWN'
    }

    # Get IDX table info
    idx_table = f'{pair_lower}_idx'
    result['idx_table'] = get_table_info(client, idx_table)

    # Get BQX table info
    bqx_table = f'{pair_lower}_bqx'
    result['bqx_table'] = get_table_info(client, bqx_table)

    # Get LAG_BQX table info
    for period in BQX_PERIODS:
        lag_table = f'lag_bqx_{pair_lower}_{period}'
        result['lag_tables'][period] = get_table_info(client, lag_table)

    # Get REGIME_BQX table info
    for period in BQX_PERIODS:
        regime_table = f'regime_bqx_{pair_lower}_{period}'
        result['regime_tables'][period] = get_table_info(client, regime_table)

    # Validate parity
    if not result['idx_table'].get('exists') or not result['bqx_table'].get('exists'):
        result['parity_status'] = 'MISSING_SOURCE_TABLES'
        return result

    idx_rows = result['idx_table']['row_count']
    bqx_rows = result['bqx_table']['row_count']

    # Check if IDX and BQX match
    if idx_rows != bqx_rows:
        result['parity_status'] = 'IDX_BQX_MISMATCH'
        result['idx_bqx_delta'] = bqx_rows - idx_rows
        return result

    # Check LAG tables (expected to be less due to lag warmup + NULL filtering)
    # LAG tables filter out rows where BQX lag values are NULL
    # This is CORRECT behavior, not an error
    for period in BQX_PERIODS:
        lag_info = result['lag_tables'][period]
        if not lag_info.get('exists'):
            result['parity_status'] = 'MISSING_LAG_TABLE'
            return result

        lag_rows = lag_info['row_count']
        # LAG tables should be reasonably close to BQX (within 5% is acceptable)
        # The difference is due to warmup period and NULL filtering
        if lag_rows < bqx_rows * 0.95:  # More than 5% difference is suspicious
            result['parity_status'] = 'LAG_ROW_COUNT_SUSPICIOUS'
            result['lag_deficit_pct'] = ((bqx_rows - lag_rows) / bqx_rows) * 100
            return result

    # Check REGIME tables (should match LAG tables)
    for period in BQX_PERIODS:
        regime_info = result['regime_tables'][period]
        lag_info = result['lag_tables'][period]

        if not regime_info.get('exists'):
            result['parity_status'] = 'MISSING_REGIME_TABLE'
            return result

        if regime_info['row_count'] != lag_info['row_count']:
            result['parity_status'] = 'LAG_REGIME_MISMATCH'
            return result

    result['parity_status'] = 'PERFECT_PARITY'
    return result

def main():
    """Validate data parity across all FX pairs."""
    print("=" * 80)
    print("DATA PARITY VALIDATION")
    print("=" * 80)
    print(f"Start time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"FX Pairs: {len(FX_PAIRS)}")
    print(f"BQX Periods: {BQX_PERIODS}")
    print("=" * 80)
    print()

    client = bigquery.Client(project=PROJECT_ID, location=LOCATION)

    results = []
    perfect_parity_count = 0

    for pair in FX_PAIRS:
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Validating {pair}...")
        result = validate_pair(client, pair)
        results.append(result)

        if result['parity_status'] == 'PERFECT_PARITY':
            perfect_parity_count += 1
            idx_rows = result['idx_table']['row_count']
            bqx_rows = result['bqx_table']['row_count']
            print(f"  ✅ PERFECT PARITY: IDX={idx_rows:,}, BQX={bqx_rows:,}")
        else:
            print(f"  ❌ {result['parity_status']}")

    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ Perfect parity: {perfect_parity_count}/{len(FX_PAIRS)}")
    print(f"❌ Issues found: {len(FX_PAIRS) - perfect_parity_count}/{len(FX_PAIRS)}")
    print()

    # Save detailed results
    output_file = '/tmp/data_parity_validation_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'validation_timestamp': datetime.utcnow().isoformat(),
            'total_pairs': len(FX_PAIRS),
            'perfect_parity_count': perfect_parity_count,
            'success_rate_pct': (perfect_parity_count / len(FX_PAIRS)) * 100,
            'results': results
        }, f, indent=2)

    print(f"Detailed results saved to: {output_file}")
    print()
    print(f"End time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 80)

if __name__ == '__main__':
    main()
