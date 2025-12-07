# BQX ML V3 - Data Bug Remediation Plan

**Created:** 2025-12-07
**Issue:** `targets_*` tables contain incorrect data (agg_mean values instead of BQX values)
**Impact:** All horizon correlation analyses are invalid

---

## Executive Summary

A data bug was discovered where `targets_*.bqx_*` columns contain price means (`agg_mean_*`) instead of actual BQX oscillation values. This invalidates all correlation analyses performed against these tables.

**Cost Constraint:** Previous correlation job cost $1,225. This plan prioritizes cost efficiency.

---

## Phase 1: Validation & Scoping (Cost: ~$0.50)

### 1.1 Verify Bug Scope
Confirm which tables/columns are affected.

```sql
-- Estimated cost: ~$0.10 (small query)
-- Check if all 28 pairs have the bug
SELECT pair, CORR(agg_mean_720, bqx_720) as correlation
FROM targets_{pair}
JOIN agg_{pair} USING (interval_time)
-- Expected: 1.0 for all pairs (confirming bug)
```

### 1.2 Identify Valid vs Invalid Analyses
Determine which existing analyses are still valid.

| Analysis | Uses targets_* | Status |
|----------|---------------|--------|
| `feature_correlations_by_horizon` | YES | INVALID |
| `feature_correlations_by_horizon_extreme` | YES | INVALID |
| `timing_correlations_comprehensive` | NO (uses timing_targets) | VALID |
| Feature type lift comparison | DEPENDS | CHECK |

### 1.3 Estimate Remediation Cost

**Option A: Full rebuild (NOT RECOMMENDED)**
- 28 pairs × 214 tables × 7 horizons = 41,944 correlations
- Estimated: 150-200 TB scanned = $940-$1,250

**Option B: Targeted rebuild (RECOMMENDED)**
- Fix targets tables: ~$5-10 (simple INSERT queries)
- Re-correlate only non-agg features: ~$200-300
- Sample validation first: ~$20

---

## Phase 2: Fix Targets Tables (Cost: ~$10)

### 2.1 Rebuild targets_* with Correct Values

For each pair, recreate the targets table using actual BQX values:

```sql
-- Cost per pair: ~$0.30 (single table scan)
-- Total for 28 pairs: ~$8.40

CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.targets_{pair}_fixed` AS
SELECT
  interval_time,
  bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
  LEAD(bqx_45, 15) OVER w as target_bqx45_h15,
  LEAD(bqx_45, 30) OVER w as target_bqx45_h30,
  -- ... all horizon targets
FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
WINDOW w AS (ORDER BY interval_time)
```

### 2.2 Validate Fix

```sql
-- Verify bqx_720 now has oscillation values (~0.1), not price means (~99)
SELECT AVG(bqx_720), STDDEV(bqx_720) FROM targets_eurusd_fixed
-- Expected: AVG ≈ 0, STDDEV ≈ 0.2 (normalized oscillation)
```

---

## Phase 3: Sample Correlation Test (Cost: ~$20)

### 3.1 Test on Single Pair First

Before running full analysis, validate approach on EURUSD only:

```sql
-- Test correlation with fixed targets
-- Estimated cost: ~$20 for one pair, all features

SELECT
  feature_name,
  CORR(feature_value, target_bqx720_h15) as corr_h15,
  CORR(feature_value, target_bqx720_h105) as corr_h105
FROM features
JOIN targets_eurusd_fixed USING (interval_time)
GROUP BY feature_name
```

### 3.2 Expected Outcomes

With correct BQX values, expect:
- `agg_mean_*` correlation: ~0.02 (NOT 0.999)
- `vol_*`, `cov_*` correlations: Similar to previous (~0.15-0.30)
- Overall pattern should match non-agg feature correlations

---

## Phase 4: Targeted Re-correlation (Cost: ~$200-300)

### 4.1 Prioritize Feature Types

Based on Phase 3 results, selectively re-correlate:

| Feature Type | Count | Priority | Rationale |
|--------------|-------|----------|-----------|
| agg_* | ~3,500 | HIGH | Bug directly affected these |
| reg_* | ~4,000 | MEDIUM | Validation check |
| vol_*, cov_* | ~30,000 | LOW | Likely unaffected |

### 4.2 Cost Optimization Strategies

1. **Use DRY_RUN first** - Estimate bytes before running
2. **Batch by pair** - Process 1-2 pairs at a time
3. **Stop early** - If results match expectations, skip remaining pairs
4. **Exclude redundant features** - Skip features with near-zero correlation

---

## Phase 5: Documentation Update (Cost: $0)

### 5.1 Update Reports
- Mark `agg_*` "perfect correlation" as DATA BUG
- Revise Recommendation 3 status
- Document correct correlation values

### 5.2 Archive Invalid Results
- Move invalid analyses to `archive/` folder
- Create audit trail of what was fixed

---

## Cost Summary

| Phase | Description | Estimated Cost |
|-------|-------------|----------------|
| 1 | Validation & Scoping | $0.50 |
| 2 | Fix Targets Tables | $10 |
| 3 | Sample Correlation Test | $20 |
| 4 | Targeted Re-correlation | $200-300 |
| 5 | Documentation | $0 |
| **TOTAL** | | **$230-330** |

Compare to:
- Full re-run (no optimization): $1,000+
- Previous job cost: $1,225

---

## Approval Gates

**Before Phase 2:** User approval required ($10 estimate)
**Before Phase 3:** User approval required ($20 estimate)
**Before Phase 4:** User approval required ($200-300 estimate)

---

## Alternative: Minimal Fix

If budget is extremely constrained, consider:

1. **Document-only fix** ($0)
   - Mark all agg_* correlations as invalid
   - Do not re-run analysis
   - Use non-agg features only going forward

2. **Single-pair validation** (~$30)
   - Fix EURUSD only
   - Validate pattern change
   - Apply learnings to future analyses

---

## Recommendation

**Proceed with Phases 1-3 first** (total ~$30):
1. Validate bug scope
2. Fix targets tables
3. Sample test on one pair

Then decide if Phase 4 is necessary based on results.

---

*Plan created with cost estimation utility: scripts/estimate_query_cost.py*
