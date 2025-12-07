# BQX ML V3 - Recommendation Rationale

**Generated:** 2025-12-07
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

## Recommendation 2: Horizon Strategy (h15 vs h105)

### Supporting Data

| Horizon | Full Dataset Features | Extreme Features |
|---------|----------------------|------------------|
| **h15** | 38,736 (42.5%) | 33,905 (36.5%) |
| **h105** | 40,260 (44.2%) | 44,905 (48.4%) |
| h30-h90 | 12,097 (13.3%) | 14,023 (15.1%) |

### Original Rationale

- 87% of features perform best at EITHER h15 OR h105
- Middle horizons (h30, h45, h60, h75, h90) only capture 13-15% of best features

### Critical Update from Timing Analysis

**Finding:** h15↔h105 correlation = 1.0 (features predict identically across all horizons)

This reveals a paradox:
- Features cluster at extremes (h15, h105) but predict them identically
- Features predict **MAGNITUDE** of movement, not **WHEN** it occurs
- A move that peaks at h15 vs h105 looks the same to the features

### Revised Recommendation

Training 7 separate horizon models is **redundant** (they learn the same signal).

Better strategy:
1. Train ONE magnitude prediction model
2. Separate attempt at timing classification (though timing showed weak correlation ~0.05)

---

## Recommendation 3: Aggregation Features (`agg_*`)

### Supporting Data

| Dataset | Top Features | Correlation |
|---------|--------------|-------------|
| Full | reg_ci_lower_1440, reg_mean_360 | 0.9999 |
| **Extreme** | **agg_mean_720, agg_min_720, agg_max_720** | **1.0000** |

### Rationale

- `agg_*` features show **perfect correlation** (1.0) in extreme periods
- These are aggregation statistics: mean, min, max, std over windows
- In extreme periods, these simple statistics perfectly predict BQX values

### Why This Makes Sense

- During extreme volatility, price aggregates (averages, ranges) directly reflect the BQX oscillation
- `agg_mean_720` = average price over 720 minutes, highly correlated with BQX (which measures price oscillation)
- This relationship is almost **tautological**: BQX measures how much price moves, aggregates measure how much price moved

### Critical Caveat

- Perfect correlation may indicate **data leakage** or near-identity relationship
- These features may not be useful for **prediction** (they measure the same thing being predicted)
- Verification needed: are `agg_*` features computed BEFORE the BQX target period?

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

## Summary Matrix

| Recommendation | Rationale | Confidence | Caveat |
|----------------|-----------|------------|--------|
| 1. Extreme-sensitive features | +200% lift proves regime-specific signal | HIGH | Low absolute correlation |
| 2. h15/h105 focus | 87% of features cluster here | MEDIUM | h15↔h105 redundant (corr=1.0) |
| 3. agg_* features | Perfect correlation in extremes | LOW | Possible data leakage/tautology |
| 4. cov_* features | Large set with solid 0.27-0.33 corr | HIGH | Lower lift than volatile features |

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

1. **Consolidate horizon models** - Reduce from 7 to 1-2 (h15 and h105 are equivalent)
2. **Implement regime detection** - Use volatility classifier to detect extreme periods
3. **Dynamic feature weighting** - Increase der/div/mrt/align/mom weights during extremes
4. **Verify agg_* features** - Check for data leakage before relying on perfect correlation
5. **Add range prediction** - Strong signal exists for predicting BQX oscillation magnitude

---

*Document generated from BQX ML V3 Horizon Correlation and Timing Prediction Analysis*
