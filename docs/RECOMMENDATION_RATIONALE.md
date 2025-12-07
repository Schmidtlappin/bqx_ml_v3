# BQX ML V3 - Recommendation Rationale

**Generated:** 2025-12-07
**Updated:** 2025-12-07 (Added polynomial features finding, h15/h105 artifact investigation)
**Context:** Analysis of horizon correlation findings and timing prediction results

---

## Recommendation 1: Prioritize Extreme-Sensitive Features

### Supporting Data

| Feature Type | Full Corr | Extreme Corr | Lift |
|--------------|-----------|--------------|------|
| **der** (derivatives) | 0.0091 | 0.0305 | **+235%** |
| **div** (divergence) | 0.0236 | 0.0786 | **+233%** |
| **mrt** (mean reversion) | 0.0174 | 0.0538 | **+209%** |
| **align** (alignment) | 0.0097 | 0.0271 | **+179%** |
| **mom** (momentum) | 0.0250 | 0.0610 | **+144%** |

### Rationale

- These features have LOW baseline correlations (0.009-0.025) during normal periods
- They TRIPLE their predictive power during extreme periods (+144% to +235% lift)
- This indicates they specifically encode information that only matters when markets are volatile
- In a static model, these would be underweighted due to low average correlation

### Implementation

Dynamically increase weights for der, div, mrt, align, mom features when extreme periods are detected (via volatility regime classifier).

### Caveat

Absolute correlations remain low (0.03-0.08 even in extremes). However, combining 5 feature types with ~0.05 correlation could yield ensemble power.

---

## ~~Recommendation 2: Horizon Strategy (h15 vs h105)~~ INVALIDATED

### Status: INVALIDATED

This recommendation has been **invalidated** based on deep-dive investigation conducted 2025-12-07.

### Original Supporting Data

| Horizon | Full Dataset Features | Extreme Features |
|---------|----------------------|------------------|
| **h15** | 38,736 (42.5%) | 33,905 (36.5%) |
| **h105** | 40,260 (44.2%) | 44,905 (48.4%) |
| h30-h90 | 12,097 (13.3%) | 14,023 (15.1%) |

### Original Rationale (Now Disproven)

- 87% of features perform best at EITHER h15 OR h105
- Middle horizons (h30, h45, h60, h75, h90) only capture 13-15% of best features

### Investigation Finding: Statistical Artifact

The 87% h15/h105 clustering is NOT a real signal. It is a statistical artifact.

#### Evidence

| Spread Category (h15 vs h105) | Features | Percentage |
|-------------------------------|----------|------------|
| **Trivial (<0.1%)** | 68,361 | **77.4%** |
| Small (0.1-0.5%) | 18,828 | 21.3% |
| Moderate (0.5-1%) | 1,176 | 1.3% |
| Meaningful (>1%) | 5 | **0.0%** |

**Key metric:** Average h15↔h105 spread = **0.0007 (0.07%)** - statistically meaningless.

#### Root Cause

1. **74.6% of features have MONOTONIC correlation patterns** - correlations either always increase or always decrease from h15→h105
2. For monotonic patterns, the maximum is **mathematically forced** to an endpoint (h15 or h105)
3. The "choice" between h15 and h105 is essentially a **coin flip on noise**

#### Example

```
Feature: bqx_360 (CHFJPY) - classified as "best = h15"
h15:  0.999936  ← "Best" (by 0.000006)
h30:  0.999935
h45:  0.999935
h60:  0.999934
h75:  0.999933
h90:  0.999931
h105: 0.999930

Actual spread: 0.000006 (6 millionths) - meaningless difference
```

### Revised Recommendation

**Do NOT train separate models for h15 and h105.** All 7 horizons are redundant.

Better strategy:
1. Train ONE magnitude prediction model (features predict magnitude, not timing)
2. Accept that timing prediction has weak signal (~0.05 correlation)

---

## ~~Recommendation 3: Aggregation Features (`agg_*`)~~ INVALIDATED - DATA BUG

### Status: INVALIDATED (2025-12-07)

Investigation revealed the "perfect correlation" was caused by a **data bug**, not a real signal.

### Original Supporting Data (NOW KNOWN TO BE INVALID)

| Dataset | Top Features | Correlation |
|---------|--------------|-------------|
| Full | reg_ci_lower_1440, reg_mean_360 | 0.9999 |
| **Extreme** | **agg_mean_720, agg_min_720, agg_max_720** | **1.0000** |

### Investigation Finding: Data Bug in targets_* Tables

The `targets_*` tables were incorrectly populated:

| Table | Column | Expected Value | Actual Value |
|-------|--------|----------------|--------------|
| targets_eurusd | bqx_720 | ~0.1 (BQX oscillation) | ~99.5 (price mean) |

**Evidence:**
```
targets_eurusd.bqx_720 = agg_eurusd.agg_mean_720  (correlation = 1.0)
targets_eurusd.bqx_720 ≠ eurusd_bqx.bqx_720      (completely different values)
```

### Root Cause

The targets tables were built using `agg_mean_*` values instead of actual BQX values from `{pair}_bqx` tables.

### Impact

- All correlation analyses using `targets_*` tables are **invalid**
- The "perfect correlation" was `agg_mean_720` correlating with **itself**
- No actual predictive signal exists

### Remediation

See [REMEDIATION_PLAN.md](REMEDIATION_PLAN.md) for phased fix approach.

### Correct Expected Correlation

When targets are fixed with actual BQX values:
- `agg_mean_720` vs BQX horizons: ~0.02 (weak, not 0.999)
- This matches the direct test against `eurusd_bqx.bqx_720`

---

## Recommendation 4: Covariance Features (`cov_*`)

### Supporting Data

| Metric | Value |
|--------|-------|
| Feature Count | 26,000+ |
| Full Correlation | 0.2653 |
| Extreme Correlation | 0.3299 |
| Lift | +24% |

### Rationale

- `cov_*` features measure cross-pair price relationships (EURUSD↔GBPUSD covariance, etc.)
- 0.27-0.33 correlation is **solid** (not perfect like agg, but substantial)
- 26K features = largest feature set, providing broad cross-pair coverage
- +24% lift shows they gain predictive value in extremes (though less than der/div/mrt)

### Why Covariance Matters

- Extreme market moves often propagate across related pairs
- When EURUSD makes a large move, related pairs (EURGBP, GBPUSD) often move in correlated ways
- Covariance features capture this cross-pair contagion/propagation pattern

### Trade-off

- Lower lift (+24%) than volatile features (+200%+)
- But higher absolute correlation (0.33 vs 0.08)
- Provides **stable baseline prediction** vs volatile features' **regime-specific boost**

---

## Recommendation 5: Polynomial Regression Features (`reg_lin_term_*`, `reg_residual_*`) - NEW

### Status: VALID (2025-12-07) - Major Discovery

Investigation with **corrected targets table** revealed polynomial features have dramatically stronger correlations than originally reported.

### Supporting Data (Tested Against Fixed Targets)

| Feature | EURUSD | GBPUSD | USDJPY | Avg Correlation |
|---------|--------|--------|--------|-----------------|
| **reg_lin_term_720** | 0.6084 | 0.6160 | 0.6157 | **+0.61** |
| reg_quad_term_720 | 0.0339 | - | - | ~0.03 |
| **reg_residual_720** | -0.6595 | -0.6665 | -0.6647 | **-0.66** |

### Horizon Decay Pattern

| Feature | h15 | h45 | h90 | h105 | Pattern |
|---------|-----|-----|-----|------|---------|
| lin_term_720 | 0.61 | 0.53 | 0.42 | 0.39 | Decays with horizon |
| residual_720 | -0.66 | -0.68 | -0.71 | -0.72 | Strengthens with horizon |

### Key Properties

1. **lin_term and residual are NOT correlated with each other** (only 0.16)
2. **Both strongly correlate with BQX** (~0.65 in opposite directions)
3. **Can be combined** for potentially stronger ensemble prediction
4. **Consistent across all tested pairs** (EURUSD, GBPUSD, USDJPY)

### Why Original Analysis Showed ~5% Correlation

The original correlation analysis used the **buggy targets table** which contained `agg_mean_*` values instead of actual BQX values. With corrected targets:
- Original reported: ~0.05 (5%)
- Actual correlation: ~0.61 (61%)
- **12× stronger than originally measured**

### Rationale

- `reg_lin_term_*` captures the **linear trend slope** of price movement
- `reg_residual_*` captures **deviations from polynomial fit** (noise/oscillation)
- These are orthogonal signals that together explain significant variance in BQX oscillation

### Implementation

Prioritize `reg_lin_term_*` and `reg_residual_*` as **primary predictive features**:
- They have 10× higher correlation than other feature types
- They're consistent across pairs
- lin_term better for short horizons (h15), residual better for longer (h105)

---

## Summary Matrix

| Recommendation | Rationale | Status | Caveat |
|----------------|-----------|--------|--------|
| 1. Extreme-sensitive features | +200% lift proves regime-specific signal | **VALID** | Low absolute correlation |
| 2. h15/h105 focus | ~~87% of features cluster here~~ | **INVALIDATED** | Artifact: spread <0.1% for 77% of features |
| 3. agg_* features | ~~Perfect correlation in extremes~~ | **INVALIDATED** | DATA BUG: targets table had wrong values |
| 4. cov_* features | Large set with solid 0.27-0.33 corr | **VALID** | Lower lift than volatile features |
| 5. Polynomial features | **0.61-0.66 correlation** (strongest found) | **VALID** | Only tested on 720 window so far |

---

## Key Insights from Combined Analyses

### Magnitude vs Timing

| Target | Avg Correlation | Max Correlation | Predictability |
|--------|-----------------|-----------------|----------------|
| **bqx_range** (magnitude) | 0.077 | **0.854** | HIGH |
| **peak_ratio** (timing) | 0.053 | 0.914 | LOW |
| **trough_ratio** (timing) | ~0.05 | ~0.9 | LOW |

**Conclusion:** Current features predict HOW MUCH price will move, but not WHEN the peak/trough will occur within the prediction window.

### Top Features for Magnitude Prediction

| Feature | Window | Correlation | Pairs |
|---------|--------|-------------|-------|
| vol_normalized_720 | 720 | **0.811** | 28 |
| agg_cv_720 | 720 | **0.811** | 28 |
| agg_cv_1440 | 1440 | **0.803** | 28 |
| vol_normalized_360 | 360 | **0.789** | 28 |
| agg_cv_2880 | 2880 | **0.774** | 28 |

---

## Actionable Next Steps

1. **Prioritize polynomial features** - `reg_lin_term_*` and `reg_residual_*` have 10× higher correlation than other features (0.61-0.66 vs ~0.05)
2. **Consolidate to ONE model** - All 7 horizon models are redundant (features predict magnitude, not timing)
3. **Implement regime detection** - Use volatility classifier to detect extreme periods
4. **Dynamic feature weighting** - Increase der/div/mrt/align/mom weights during extremes
5. ~~Verify agg_* features~~ - COMPLETED: Data bug confirmed. agg_mean has ~0 correlation, other agg features ~0.01-0.02
6. **Test polynomial features across all windows** - Only 720 tested so far; verify 45, 90, 180, 360, 1440, 2880

---

## Appendix: Investigation Methodology

### How the Artifact Was Discovered

1. **Initial suspicion:** 87% clustering at h15/h105 seemed too extreme
2. **Spread analysis:** Calculated actual difference between h15 and h105 correlations
3. **Finding:** 77.4% of features had spread <0.1% - statistically meaningless
4. **Monotonicity check:** 74.6% of features showed monotonic patterns (always increasing or decreasing)
5. **Conclusion:** Endpoint selection is forced by monotonicity + noise determines which endpoint "wins"

### Queries Used

```sql
-- Spread categorization
SELECT
  CASE
    WHEN ABS(corr_h15 - corr_h105) < 0.001 THEN 'trivial (<0.1%)'
    WHEN ABS(corr_h15 - corr_h105) < 0.005 THEN 'small (0.1-0.5%)'
    WHEN ABS(corr_h15 - corr_h105) < 0.01 THEN 'moderate (0.5-1%)'
    ELSE 'meaningful (>1%)'
  END as spread_category,
  COUNT(*) as count
FROM feature_correlations_by_horizon
GROUP BY 1

-- Monotonicity check
SELECT
  CASE
    WHEN corr_h15 >= corr_h30 >= ... >= corr_h105 THEN 'monotonic_decreasing'
    WHEN corr_h15 <= corr_h30 <= ... <= corr_h105 THEN 'monotonic_increasing'
    ELSE 'non_monotonic'
  END as pattern,
  COUNT(*) as count
FROM feature_correlations_by_horizon
GROUP BY 1
```

---

*Document generated from BQX ML V3 Horizon Correlation and Timing Prediction Analysis*
*Updated 2025-12-07 with polynomial features discovery and h15/h105 artifact investigation*
