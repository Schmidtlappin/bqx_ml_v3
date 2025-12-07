#!/usr/bin/env python3
"""
BigQuery Cost Estimation Utility

ALWAYS run this before large analytical jobs to estimate costs.
Usage: python3 estimate_query_cost.py "YOUR SQL QUERY"

Pricing: $6.25 per TB scanned (on-demand, us-central1)
"""

import sys
from google.cloud import bigquery

PRICE_PER_TB = 6.25  # USD, on-demand pricing

def estimate_cost(query: str) -> dict:
    """Dry-run a query to estimate bytes scanned and cost."""
    client = bigquery.Client(project='bqx-ml', location='us-central1')

    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    try:
        job = client.query(query, job_config=job_config)

        bytes_processed = job.total_bytes_processed
        tb_processed = bytes_processed / 1e12
        estimated_cost = tb_processed * PRICE_PER_TB

        return {
            'bytes': bytes_processed,
            'gb': bytes_processed / 1e9,
            'tb': tb_processed,
            'cost_usd': estimated_cost,
            'error': None
        }
    except Exception as e:
        return {
            'bytes': 0,
            'gb': 0,
            'tb': 0,
            'cost_usd': 0,
            'error': str(e)
        }

def estimate_batch_job(pairs: list, tables_per_pair: int, rows_per_join: int, queries_per_table: int = 7) -> dict:
    """
    Estimate cost for batch correlation jobs like timing analysis.

    Args:
        pairs: List of currency pairs
        tables_per_pair: Number of feature tables per pair
        rows_per_join: Rows in the target table being joined
        queries_per_table: Number of queries per table (e.g., 7 windows)

    Returns:
        Cost estimation dict
    """
    # Rough estimate: each query scans ~10-15 GB for correlation on 60M rows
    avg_gb_per_query = 12  # Conservative estimate

    total_queries = len(pairs) * tables_per_pair * queries_per_table
    total_gb = total_queries * avg_gb_per_query
    total_tb = total_gb / 1000
    estimated_cost = total_tb * PRICE_PER_TB

    return {
        'pairs': len(pairs),
        'tables_per_pair': tables_per_pair,
        'queries_per_table': queries_per_table,
        'total_queries': total_queries,
        'estimated_tb': round(total_tb, 2),
        'estimated_cost_usd': round(estimated_cost, 2),
        'warning': 'HIGH COST!' if estimated_cost > 50 else None
    }

def print_warning(cost_usd: float):
    """Print cost warning with appropriate severity."""
    if cost_usd > 500:
        print("\n" + "="*60)
        print("🚨 EXTREME COST WARNING 🚨")
        print(f"   Estimated cost: ${cost_usd:,.2f}")
        print("   This requires EXPLICIT USER APPROVAL before running!")
        print("="*60 + "\n")
    elif cost_usd > 100:
        print("\n" + "="*60)
        print("⚠️  HIGH COST WARNING ⚠️")
        print(f"   Estimated cost: ${cost_usd:,.2f}")
        print("   Please confirm before proceeding.")
        print("="*60 + "\n")
    elif cost_usd > 10:
        print(f"\n💰 Estimated cost: ${cost_usd:,.2f}\n")
    else:
        print(f"\n✅ Low cost query: ${cost_usd:,.2f}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Demo: estimate timing correlation job
        print("Timing Correlation Job Cost Estimate:")
        print("-" * 40)

        estimate = estimate_batch_job(
            pairs=['audcad', 'audchf', 'audjpy', 'audnzd', 'audusd', 'cadchf', 'cadjpy',
                   'chfjpy', 'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd',
                   'eurusd', 'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
                   'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd', 'usdcad', 'usdchf', 'usdjpy'],
            tables_per_pair=214,
            rows_per_join=60_000_000,
            queries_per_table=7
        )

        for k, v in estimate.items():
            print(f"  {k}: {v}")

        print_warning(estimate['estimated_cost_usd'])

    else:
        query = sys.argv[1]
        result = estimate_cost(query)

        if result['error']:
            print(f"Error: {result['error']}")
        else:
            print(f"Bytes to scan: {result['bytes']:,}")
            print(f"GB to scan: {result['gb']:.2f}")
            print(f"TB to scan: {result['tb']:.4f}")
            print_warning(result['cost_usd'])
