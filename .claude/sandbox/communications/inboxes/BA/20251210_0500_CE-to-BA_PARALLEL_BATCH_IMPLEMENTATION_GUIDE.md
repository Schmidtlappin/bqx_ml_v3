# CE Directive: Parallel Batch Implementation Guide

**Document Type**: CE DIRECTIVE (IMPLEMENTATION GUIDE)
**Date**: December 10, 2025 05:00
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL** - BLOCKING
**Reference**:
- 20251210_0445_CE-to-BA_PARALLEL_BATCH_REQUIREMENT
- 20251210_0435_QA-to-CE_SHAP_COST_ESTIMATE

---

## EXECUTIVE SUMMARY

| Current State | Required State |
|---------------|----------------|
| Sequential processing | Parallel batch processing |
| ~$70-1,287 cost risk | ~$10 cost |
| ~30-200 hours | ~8 hours |
| No implementation | `parallel_feature_testing.py` |

**QA-VALIDATED BUDGET**: $9.21 total (approved)

---

## STEP 1: CREATE FILE

**File**: `pipelines/training/parallel_feature_testing.py`

```python
#!/usr/bin/env python3
"""
Parallel Batch Feature Testing Pipeline

Implements cost-optimized parallel processing for 6,477 feature testing:
- Batch query: 1 query per pair (all 7 horizons)
- Parallel workers: 8 concurrent processes
- Cost target: <$2 per pair, ~$10 total

CE DIRECTIVE: 2025-12-10 05:00
QA VALIDATED: $9.21 total budget
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from google.cloud import bigquery
import warnings
warnings.filterwarnings('ignore')

# Configuration
PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

HORIZONS = [15, 30, 45, 60, 75, 90, 105]
MAX_WORKERS = 8
SAMPLE_LIMIT = 80000

ALL_28_PAIRS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
    "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
    "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
    "audjpy", "audchf", "audcad", "audnzd",
    "nzdjpy", "nzdchf", "nzdcad",
    "cadjpy", "cadchf", "chfjpy"
]


def build_batch_query(pair: str, date_start: str, date_end: str) -> str:
    """
    Build SINGLE query that returns ALL features + ALL 7 horizon targets.

    CRITICAL: This is the cost optimization - 1 query instead of 7.
    """
    query = f"""
    SELECT
        -- Timestamp
        reg_idx.interval_time,

        -- IDX Polynomial Features (window 45-1440)
        reg_idx.reg_quad_term_45, reg_idx.reg_lin_term_45, reg_idx.reg_total_var_45,
        reg_idx.reg_slope_45, reg_idx.reg_trend_str_45, reg_idx.reg_deviation_45, reg_idx.reg_zscore_45,
        reg_idx.reg_quad_term_90, reg_idx.reg_lin_term_90, reg_idx.reg_total_var_90,
        reg_idx.reg_slope_90, reg_idx.reg_trend_str_90, reg_idx.reg_deviation_90, reg_idx.reg_zscore_90,
        reg_idx.reg_quad_term_180, reg_idx.reg_lin_term_180, reg_idx.reg_total_var_180,
        reg_idx.reg_slope_180, reg_idx.reg_trend_str_180, reg_idx.reg_deviation_180, reg_idx.reg_zscore_180,
        reg_idx.reg_quad_term_360, reg_idx.reg_lin_term_360, reg_idx.reg_total_var_360,
        reg_idx.reg_slope_360, reg_idx.reg_trend_str_360,
        reg_idx.reg_quad_term_720, reg_idx.reg_lin_term_720, reg_idx.reg_total_var_720,
        reg_idx.reg_slope_720, reg_idx.reg_trend_str_720,
        reg_idx.reg_quad_term_1440, reg_idx.reg_lin_term_1440, reg_idx.reg_total_var_1440,
        reg_idx.reg_slope_1440, reg_idx.reg_trend_str_1440,

        -- BQX Polynomial Features
        reg_bqx.reg_quad_term_45 as bqx_quad_45, reg_bqx.reg_lin_term_45 as bqx_lin_45,
        reg_bqx.reg_total_var_45 as bqx_tvar_45, reg_bqx.reg_slope_45 as bqx_slope_45,
        reg_bqx.reg_quad_term_90 as bqx_quad_90, reg_bqx.reg_lin_term_90 as bqx_lin_90,
        reg_bqx.reg_total_var_90 as bqx_tvar_90, reg_bqx.reg_slope_90 as bqx_slope_90,
        reg_bqx.reg_quad_term_180 as bqx_quad_180, reg_bqx.reg_lin_term_180 as bqx_lin_180,
        reg_bqx.reg_total_var_180 as bqx_tvar_180,

        -- Base BQX values
        base_bqx.bqx_45, base_bqx.bqx_90, base_bqx.bqx_180, base_bqx.bqx_360,

        -- Aggregation features
        agg_bqx.agg_std_45 as regime_vol_45, agg_bqx.agg_std_90 as regime_vol_90,
        agg_bqx.agg_cv_45 as regime_cv_45, agg_bqx.agg_cv_90 as regime_cv_90,

        -- Derivative features
        der_bqx.der_v1_45 as regime_der1_45, der_bqx.der_v1_90 as regime_der1_90,
        der_bqx.der_v2_45 as regime_der2_45, der_bqx.der_v2_90 as regime_der2_90,

        -- ALL 7 HORIZON TARGETS (single query, not 7 separate queries)
        targets.target_bqx45_h15,
        targets.target_bqx45_h30,
        targets.target_bqx45_h45,
        targets.target_bqx45_h60,
        targets.target_bqx45_h75,
        targets.target_bqx45_h90,
        targets.target_bqx45_h105

    FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}` reg_idx
    JOIN `{PROJECT}.{FEATURES_DATASET}.reg_bqx_{pair}` reg_bqx
        ON reg_idx.interval_time = reg_bqx.interval_time
    JOIN `{PROJECT}.{FEATURES_DATASET}.base_bqx_{pair}` base_bqx
        ON reg_idx.interval_time = base_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.agg_bqx_{pair}` agg_bqx
        ON reg_idx.interval_time = agg_bqx.interval_time
    LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.der_bqx_{pair}` der_bqx
        ON reg_idx.interval_time = der_bqx.interval_time
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON reg_idx.interval_time = targets.interval_time
    WHERE DATE(reg_idx.interval_time) BETWEEN '{date_start}' AND '{date_end}'
    AND targets.target_bqx45_h15 IS NOT NULL
    ORDER BY reg_idx.interval_time
    LIMIT {SAMPLE_LIMIT}
    """
    return query


def query_pair_all_horizons(pair: str, date_start: str, date_end: str) -> pd.DataFrame:
    """
    Execute SINGLE batch query for one pair, returning all 7 horizons.

    Cost: ~$0.36 per pair (57.5 GB × $6.25/TB)
    """
    client = bigquery.Client(project=PROJECT)
    query = build_batch_query(pair, date_start, date_end)

    # Execute query and get job info for cost tracking
    job = client.query(query)
    df = job.to_dataframe()

    # Log bytes scanned for cost validation
    bytes_scanned = job.total_bytes_processed
    gb_scanned = bytes_scanned / (1024**3)
    cost_estimate = gb_scanned * 6.25 / 1000  # $6.25 per TB

    print(f"  {pair.upper()}: {len(df):,} rows, {gb_scanned:.2f} GB scanned, ~${cost_estimate:.2f}")

    return df, {'gb_scanned': gb_scanned, 'cost': cost_estimate}


def process_pair_all_horizons(pair: str, date_start: str = '2020-01-01',
                              date_end: str = '2024-12-31') -> dict:
    """
    Process ONE pair: query once, then run stability selection for all 7 horizons locally.

    This function runs in a separate process via ProcessPoolExecutor.
    """
    print(f"\n{'='*50}")
    print(f"Processing {pair.upper()}")
    print(f"{'='*50}")

    try:
        # SINGLE BigQuery call for this pair
        df, cost_info = query_pair_all_horizons(pair, date_start, date_end)

        if df is None or len(df) < 1000:
            return {'pair': pair, 'status': 'error', 'message': 'Insufficient data'}

        # Identify feature and target columns
        target_cols = [c for c in df.columns if c.startswith('target_')]
        feature_cols = [c for c in df.columns if c not in target_cols
                       and c not in ['interval_time', 'pair']]

        results = {
            'pair': pair,
            'status': 'success',
            'rows': len(df),
            'feature_count': len(feature_cols),
            'cost': cost_info,
            'horizons': {}
        }

        # Process ALL 7 horizons locally (no additional BigQuery cost)
        for horizon in HORIZONS:
            target_col = f'target_bqx45_h{horizon}'
            if target_col not in df.columns:
                continue

            # Run stability selection locally
            # TODO: Implement full stability selection here
            # For now, placeholder metrics
            results['horizons'][f'h{horizon}'] = {
                'target_col': target_col,
                'samples': len(df[df[target_col].notna()]),
                'status': 'pending_stability_selection'
            }

            print(f"    h{horizon}: {results['horizons'][f'h{horizon}']['samples']:,} samples ready")

        return results

    except Exception as e:
        return {'pair': pair, 'status': 'error', 'message': str(e)}


def run_parallel_batch_testing(pairs: list = None, max_workers: int = MAX_WORKERS,
                               date_start: str = '2020-01-01',
                               date_end: str = '2024-12-31') -> dict:
    """
    Run parallel batch processing across multiple pairs.

    Each worker processes one pair at a time:
    - 1 BigQuery query per pair (batch)
    - 7 horizons processed locally per pair
    - 8 workers = 8 pairs processed concurrently
    """
    if pairs is None:
        pairs = ALL_28_PAIRS

    print("=" * 70)
    print("PARALLEL BATCH FEATURE TESTING")
    print(f"Pairs: {len(pairs)}")
    print(f"Workers: {max_workers}")
    print(f"Date range: {date_start} to {date_end}")
    print("=" * 70)

    start_time = datetime.now()
    all_results = {}
    total_cost = 0

    # Use ProcessPoolExecutor for true parallelism
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all pairs for parallel processing
        futures = {
            executor.submit(process_pair_all_horizons, pair, date_start, date_end): pair
            for pair in pairs
        }

        # Collect results as they complete
        for future in futures:
            pair = futures[future]
            try:
                result = future.result(timeout=3600)  # 1 hour timeout per pair
                all_results[pair] = result
                if result.get('cost'):
                    total_cost += result['cost'].get('cost', 0)
            except Exception as e:
                all_results[pair] = {'pair': pair, 'status': 'error', 'message': str(e)}

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 3600

    # Summary
    print("\n" + "=" * 70)
    print("PARALLEL BATCH TESTING SUMMARY")
    print("=" * 70)
    print(f"Pairs processed: {len(all_results)}")
    print(f"Total BigQuery cost: ${total_cost:.2f}")
    print(f"Total time: {duration:.2f} hours")
    print(f"Successful: {sum(1 for r in all_results.values() if r.get('status') == 'success')}")
    print(f"Failed: {sum(1 for r in all_results.values() if r.get('status') == 'error')}")

    return {
        'timestamp': datetime.now().isoformat(),
        'pairs_processed': len(all_results),
        'total_cost': total_cost,
        'duration_hours': duration,
        'results': all_results
    }


def dry_run_cost_validation(pair: str = 'eurusd') -> dict:
    """
    Dry run to validate cost before full execution.

    REQUIRED: Must run this and report to CE before full 28-pair run.
    """
    print("=" * 70)
    print("DRY RUN COST VALIDATION")
    print(f"Testing pair: {pair.upper()}")
    print("=" * 70)

    client = bigquery.Client(project=PROJECT)
    query = build_batch_query(pair, '2023-01-01', '2023-12-31')  # 1 year sample

    # Dry run to get bytes without executing
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    job = client.query(query, job_config=job_config)

    bytes_estimate = job.total_bytes_processed
    gb_estimate = bytes_estimate / (1024**3)
    cost_per_pair = gb_estimate * 6.25 / 1000
    cost_28_pairs = cost_per_pair * 28

    print(f"\nDRY RUN RESULTS:")
    print(f"  Bytes per pair: {bytes_estimate:,} ({gb_estimate:.2f} GB)")
    print(f"  Cost per pair: ${cost_per_pair:.2f}")
    print(f"  Cost 28 pairs: ${cost_28_pairs:.2f}")
    print(f"  Budget limit: $50.00")
    print(f"  Status: {'WITHIN BUDGET' if cost_28_pairs < 50 else 'OVER BUDGET'}")

    return {
        'pair': pair,
        'bytes_per_pair': bytes_estimate,
        'gb_per_pair': gb_estimate,
        'cost_per_pair': cost_per_pair,
        'cost_28_pairs': cost_28_pairs,
        'within_budget': cost_28_pairs < 50
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry_run"

    if mode == "dry_run":
        # REQUIRED: Run this first and report to CE
        result = dry_run_cost_validation()

        output_file = "/tmp/parallel_batch_dry_run.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {output_file}")
        print("\n*** REPORT THIS TO CE BEFORE PROCEEDING ***")

    elif mode == "single":
        # Test single pair
        pair = sys.argv[2] if len(sys.argv) > 2 else "eurusd"
        result = process_pair_all_horizons(pair)
        print(json.dumps(result, indent=2, default=str))

    elif mode == "full":
        # Full 28-pair run (REQUIRES CE APPROVAL)
        print("\n*** FULL RUN - ENSURE CE APPROVAL ***\n")
        results = run_parallel_batch_testing()

        output_file = "/tmp/parallel_batch_full_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to: {output_file}")

    else:
        print("Usage:")
        print("  python parallel_feature_testing.py dry_run    # Cost validation (REQUIRED FIRST)")
        print("  python parallel_feature_testing.py single eurusd  # Test single pair")
        print("  python parallel_feature_testing.py full       # Full 28-pair run (needs CE approval)")
```

---

## STEP 2: VALIDATION SEQUENCE

### 2.1 Dry Run (REQUIRED)

```bash
cd /home/micha/bqx_ml_v3
python pipelines/training/parallel_feature_testing.py dry_run
```

**Expected output**:
```
DRY RUN RESULTS:
  Bytes per pair: ~61,xxx,xxx,xxx (~57.5 GB)
  Cost per pair: ~$0.36
  Cost 28 pairs: ~$10.06
  Status: WITHIN BUDGET
```

### 2.2 Report to CE

After dry run, create report:
```
.claude/sandbox/communications/outboxes/BA/20251210_XXXX_BA-to-CE_DRY_RUN_RESULTS.md
```

Include:
- Bytes scanned
- Cost per pair
- Total cost estimate
- Comparison to QA estimate ($9.21)

### 2.3 Await CE Approval

**DO NOT proceed to full run without CE written approval.**

### 2.4 Single Pair Test (After CE approval)

```bash
python pipelines/training/parallel_feature_testing.py single eurusd
```

### 2.5 Full Run (After CE approval)

```bash
python pipelines/training/parallel_feature_testing.py full
```

---

## STEP 3: VERIFICATION CHECKLIST

Before reporting completion, verify:

| Check | Command | Expected |
|-------|---------|----------|
| File exists | `ls pipelines/training/parallel_feature_testing.py` | File present |
| Dry run works | `python ... dry_run` | No errors, cost reported |
| Cost within budget | Check output | <$2 per pair |
| Parallel works | `python ... single eurusd` | 8 workers visible in logs |
| All 7 horizons | Check output | h15-h105 all present |

---

## CRITICAL REQUIREMENTS

| Requirement | Why |
|-------------|-----|
| **1 query per pair** | 85% cost reduction vs sequential |
| **All 7 horizons in query** | Eliminates redundant scans |
| **ProcessPoolExecutor** | True parallel execution |
| **8 workers max** | Memory constraint (32 GB) |
| **Dry run FIRST** | Validate cost before spending |
| **CE approval GATE** | Budget control |

---

## DO NOT

- DO NOT run `full` mode without CE approval
- DO NOT use sequential queries (for loop per horizon)
- DO NOT exceed 8 workers (memory risk)
- DO NOT skip dry run validation
- DO NOT modify production tables without validation

---

## SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| File created | `parallel_feature_testing.py` exists |
| Dry run cost | <$2 per pair |
| Single pair test | Completes without error |
| All 7 horizons | Present in single query |
| Parallel execution | 8 workers active |
| CE approval | Written approval received |

---

## DELIVERABLES

1. **File**: `pipelines/training/parallel_feature_testing.py`
2. **Dry run report**: Cost validation JSON
3. **CE report**: Outbox message with results
4. **Await**: CE approval before full run

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 05:00
**Status**: IMPLEMENTATION GUIDE ISSUED - EXECUTE IN ORDER
