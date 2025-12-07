# Incident Report: BigQuery Cost Surge

**Date:** 2025-12-06
**Severity:** High (Financial Impact)
**Total Cost:** ~$1,225 USD
**Duration:** ~6 hours (01:00-09:00 UTC)

## Summary

A parallelized timing correlation analysis job resulted in unexpected BigQuery costs of approximately $1,225 USD in a single day, compared to typical daily costs of $1-10.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 01:59 | Sequential timing correlation job started (estimated 24h runtime) |
| 03:09 | User requested parallelization for faster completion |
| 03:09 | Parallel job launched with 7 workers (NO COST ESTIMATE PROVIDED) |
| 03:00-08:00 | Peak processing: 175 TB scanned, $1,095 in charges |
| 09:00 | Job completed: 653,856 correlations |
| 07:15 | Cost surge discovered during routine status check |

## Root Cause

1. **No pre-execution cost estimation** - Job was launched without calculating expected BigQuery charges
2. **Parallelization multiplied costs** - 7 concurrent workers = 7× concurrent table scans
3. **Inefficient query design** - 15,800 separate INSERT statements, each scanning full tables
4. **Large table joins** - Each query joined 60M-row `timing_targets` with feature tables

## Cost Breakdown

| Query Type | Jobs | TB Billed | Cost (USD) |
|------------|------|-----------|------------|
| timing_correlations_comprehensive | 16,385 | 176 TB | $1,143 |
| feature_correlations_by_horizon_extreme | 5,858 | 7.4 TB | $46 |
| feature_correlations_by_horizon | 5,595 | 6.0 TB | $37 |
| **TOTAL** | **43,694** | **196 TB** | **$1,225** |

## What Should Have Happened

Before launching the parallel job, the following estimate should have been calculated and presented:

```
Timing Correlation Job Cost Estimate:
  pairs: 28
  tables_per_pair: 214
  queries_per_table: 7 (windows)
  total_queries: 41,944
  estimated_tb: ~175
  estimated_cost_usd: ~$1,100

🚨 EXTREME COST WARNING 🚨
   Estimated cost: $1,100.00
   This requires EXPLICIT USER APPROVAL before running!
```

## Corrective Actions

### Immediate

1. ✅ Created cost estimation utility: `scripts/estimate_query_cost.py`
2. ✅ Documented incident for future reference
3. ⬜ Review and optimize query patterns for future analyses

### Preventive

1. **Always estimate costs before large jobs**
   ```bash
   python3 scripts/estimate_query_cost.py "YOUR QUERY"
   ```

2. **Cost thresholds requiring approval**
   - \>$10: Notify user of estimated cost
   - \>$100: Request confirmation before proceeding
   - \>$500: Require explicit written approval

3. **Query optimization practices**
   - Partition large tables by pair/date
   - Batch correlations into fewer queries
   - Sample on 1-2 pairs before full runs
   - Use table clustering for frequent join columns

## Lessons Learned

1. Parallelization speeds up runtime but doesn't reduce costs - it may increase them due to concurrent scans
2. BigQuery charges per TB scanned, not per query - many small queries can be more expensive than fewer large ones
3. Always run cost estimates for analytical jobs joining large tables
4. User approval should be obtained for any job estimated to cost >$50

## Prevention Checklist for Future Large Jobs

- [ ] Run `estimate_query_cost.py` to get cost estimate
- [ ] If >$50, inform user and get approval
- [ ] If >$500, require explicit written approval
- [ ] Consider sampling on subset first
- [ ] Check if tables can be partitioned/clustered
- [ ] Batch queries where possible
