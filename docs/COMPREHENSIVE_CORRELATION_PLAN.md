# Comprehensive Feature Correlation Re-examination Plan

**Created:** 2025-12-07
**Purpose:** Systematic re-examination of ALL features against corrected BQX targets
**Constraint:** Cost-conscious ($1,225 incident learned)

---

## Executive Summary

### Problem
Spot testing approach risks missing critical features. Previous correlation analysis used **buggy targets table** (contained `agg_mean_*` instead of BQX values).

### Solution
Phased, comprehensive re-correlation of ALL feature types against `targets_all_fixed`:
- **Full dataset** (59.8M rows)
- **Extreme 20%** (top BQX magnitude periods)

---

## Feature Inventory (What Actually Exists)

| Feature Type | IDX Tables | BQX Tables | Total | Priority |
|--------------|------------|------------|-------|----------|
| **cov_*** | 1,176 | 1,176 | 2,352 | P2 |
| **corr_ibkr_*** | 224 | 224 | 448 | P3 |
| **tri_*** | 97 | 97 | 194 | P3 |
| **reg_*** | 84 | 84 | 168 | P1 |
| **var_*** | 57 | 57 | 114 | P3 |
| **csi_*** | 56 | 56 | 112 | P3 |
| **lag_*** | 56 | 56 | 112 | P2 |
| **agg_*** | 28 | 28 | 56 | P1 |
| **align_*** | 28 | 28 | 56 | P1 |
| **vol_*** | 28 | 28 | 56 | P1 |
| **mom_*** | 28 | 28 | 56 | P1 |
| **der_*** | 28 | 28 | 56 | P1 |
| **div_*** | 28 | 28 | 56 | P1 |
| **mrt_*** | 28 | 28 | 56 | P1 |
| **rev_*** | 28 | 28 | 56 | P2 |
| **cyc_*** | 0 | 28 | 28 | P2 |
| **ext_*** | 0 | 28 | 28 | P2 |
| **mkt_*** | 9 | 9 | 18 | P2 |
| **pair_bqx** | 0 | 28 | 28 | P1 |
| **TOTAL** | ~2,065 | ~2,143 | **4,208** | |

---

## Phase Plan

### Phase 0: Create Extreme Period Dataset (Cost: ~$0.50)

Create `targets_all_fixed_extreme` filtering to top 20% BQX magnitude.

```sql
CREATE TABLE targets_all_fixed_extreme AS
SELECT t.*
FROM targets_all_fixed t
JOIN (
  SELECT pair, PERCENTILE_CONT(ABS(bqx_720), 0.80) OVER(PARTITION BY pair) as p80
  FROM targets_all_fixed
) p ON t.pair = p.pair
WHERE ABS(t.bqx_720) >= p.p80
```

**Output:** ~12M rows (20% of 60M)

---

### Phase 1: PRIMARY Features - Core Pair Features (Cost: ~$5-10)

**Tables:** 504 (reg, agg, align, vol, mom, der, div, mrt, pair_bqx)
**Scope:** 28 pairs × 9 feature types × 2 variants (IDX + BQX)

**Strategy:**
1. For each feature type, correlate ALL columns with 7 horizons
2. Test against BOTH full and extreme datasets
3. Calculate lift (extreme vs full)

**Expected Duration:** ~30 minutes

**Output Table:** `feature_correlations_phase1_fixed`

| Column | Type |
|--------|------|
| feature_type | STRING |
| feature_name | STRING |
| pair | STRING |
| variant | STRING (IDX/BQX) |
| corr_h15_full | FLOAT |
| corr_h15_extreme | FLOAT |
| ... | ... |
| corr_h105_full | FLOAT |
| corr_h105_extreme | FLOAT |
| max_abs_corr_full | FLOAT |
| max_abs_corr_extreme | FLOAT |
| lift | FLOAT |

---

### Phase 2: LAG, REV, CYC, EXT, MKT Features (Cost: ~$3-5)

**Tables:** 298 (lag, rev, cyc, ext, mkt)
**Scope:** Mixed - some pairs, some BQX-only, some market-wide

**Strategy:**
1. lag_ tables - 112 tables, high potential (autoregressive)
2. rev_ tables - 56 tables (reversal signals)
3. cyc_ tables - 28 BQX-only (cycle position)
4. ext_ tables - 28 BQX-only (extremity metrics)
5. mkt_ tables - 18 (market-wide conditions)

**Output Table:** `feature_correlations_phase2_fixed`

---

### Phase 3: COVARIANCE Features (Cost: ~$15-25)

**Tables:** 2,352 (largest group!)
**Scope:** Cross-pair covariance relationships

**Challenge:** This is the largest group by far.

**Strategy - SAMPLING APPROACH:**
1. First pass: Sample 10% of cov tables (~235 tables) - Cost: ~$2
2. Identify patterns: Which cov types have signal?
3. Full pass: Only on promising cov types - Cost: ~$10-20

**Cov Types to Test:**
- cov_agg_* (aggregation covariance)
- cov_reg_* (regression covariance)
- cov_mom_* (momentum covariance)
- cov_vol_* (volatility covariance)
- cov_align_* (alignment covariance)
- cov_lag_* (lag covariance)
- cov_regime_* (regime covariance)

**Output Table:** `feature_correlations_phase3_fixed`

---

### Phase 4: CORRELATION (ETF), TRI, VAR, CSI Features (Cost: ~$5-8)

**Tables:** 868 (corr_ibkr, tri, var, csi)

**Subgroups:**
1. **corr_ibkr_** (448) - FX vs ETF correlations
   - SPY, VIX, GLD, UUP, EWA, EWG, EWJ, EWU
   - High potential for cross-market signals

2. **tri_** (194) - Triangular arbitrage
   - Triangulation error as predictive signal

3. **var_** (114) - Currency family variance
   - Family-level aggregation signals

4. **csi_** (112) - Currency Strength Index
   - Relative strength differentials

**Output Table:** `feature_correlations_phase4_fixed`

---

## Cost Summary

| Phase | Tables | Est. GB | Est. Cost | Priority |
|-------|--------|---------|-----------|----------|
| 0 | 1 | 0.1 | $0.50 | Required |
| 1 | 504 | 1.5 | $10 | HIGH |
| 2 | 298 | 1.0 | $5 | HIGH |
| 3 | 2,352 | 8.0 | $25 | MEDIUM |
| 4 | 868 | 3.0 | $10 | MEDIUM |
| **TOTAL** | **4,023** | **13.6** | **~$50** | |

**Compare to:** Original buggy analysis cost $1,225!

---

## Optimization Strategies

### 1. Batch Correlations
Instead of 1 query per feature, batch 50-100 features per query:
```sql
SELECT
  CORR(f.feature_1, t.target_h15) as corr_1_h15,
  CORR(f.feature_2, t.target_h15) as corr_2_h15,
  ...
FROM features f
JOIN targets t USING(interval_time)
```

### 2. Column Unpivoting
Use UNPIVOT to process all columns at once:
```sql
SELECT feature_name, CORR(feature_value, target) as correlation
FROM features_unpivoted
JOIN targets USING(interval_time)
GROUP BY feature_name
```

### 3. Cache Reuse
BigQuery caches table scans - run related queries in sequence.

### 4. Sampling for Screening
For Phase 3 (2,352 cov tables), sample first to identify signal.

---

## Expected Outcomes

### From Spot Testing Today (Full Dataset Only):

| Feature Type | Top Correlation | Status |
|--------------|-----------------|--------|
| mom_ (IDX) | 0.9774 | STRONG |
| der_ (IDX) | 0.9759 | STRONG |
| reg_ (IDX) | 0.9133 | STRONG |
| div_ (IDX) | 0.8795 | STRONG |
| align_ (IDX) | 0.7680 | STRONG |
| agg_ (IDX) | 0.7308 | MODERATE |
| mrt_ (IDX) | 0.7295 | STRONG |
| reg_bqx_ | 0.2218 | Weak |
| vol_ (IDX) | 0.0181 | Very Weak |
| cyc_bqx_ | 0.0069 | Very Weak |
| ext_bqx_ | 0.037 | Very Weak |

### Expected Additional Findings:

1. **lag_** features: Likely strong (autoregressive BQX patterns)
2. **corr_ibkr_** features: Unknown (cross-market signals)
3. **cov_** features: Original showed 0.27-0.33 - need validation
4. **csi_** features: Currency strength differentials
5. **tri_** features: Triangulation errors as signals

### Lift Analysis (Full vs Extreme):

Original analysis showed:
- der: +235% lift in extremes
- div: +233% lift
- mrt: +209% lift

**NEED TO VALIDATE** these lifts with corrected targets.

---

## Deliverables

### Per Phase:
1. BigQuery results table with all correlations
2. CSV export of top 100 features
3. Summary report with lift analysis

### Final:
1. **MASTER_FEATURE_RANKINGS.csv** - All features ranked by correlation
2. **LIFT_ANALYSIS_REPORT.md** - Full vs Extreme comparison
3. **UPDATED_RECOMMENDATION_RATIONALE.md** - Validated recommendations

---

## Approval Gates

| Phase | Est. Cost | Approval Required |
|-------|-----------|-------------------|
| 0 | $0.50 | Auto-approved |
| 1 | $10 | User approval |
| 2 | $5 | Auto if Phase 1 OK |
| 3 | $25 | User approval |
| 4 | $10 | Auto if Phase 3 OK |

---

## Execution Order

1. **Phase 0** - Create extreme dataset (required for all phases)
2. **Phase 1** - Primary features (highest priority, most likely to have signal)
3. **Phase 2** - Secondary features (lag, rev, cyc, ext, mkt)
4. **Phase 4** - Cross-market features (corr_ibkr, tri, var, csi)
5. **Phase 3** - Covariance features (largest, do last with sampling)

---

## Risk Mitigation

### Cost Overrun Prevention:
- Use `--dry_run` for cost estimation before each phase
- Stop if any single query exceeds $5
- User approval for any phase >$10

### Signal Detection:
- Correlation >0.3 = STRONG (investigate)
- Correlation 0.1-0.3 = MODERATE (include in model)
- Correlation <0.1 = WEAK (deprioritize)
- Correlation <0.01 = NOISE (exclude)

### Data Quality:
- Verify sample counts match expected (~2.1M per pair)
- Check for NULL values in correlations
- Validate extreme dataset is truly 20%

---

*Plan created: 2025-12-07*
*Estimated total cost: ~$50 (vs $1,225 for original buggy analysis)*
*Estimated duration: 2-4 hours*
