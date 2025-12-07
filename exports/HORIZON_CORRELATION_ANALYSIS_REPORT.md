# BQX ML V3 - Horizon Correlation Analysis Report

**Generated:** 2025-12-05
**Updated:** 2025-12-07 (Critical finding on h15/h105 artifact)
**Analysis:** Feature correlations to 7 BQX prediction horizons (h15-h105)

---

## Executive Summary

| Metric | Full Dataset | Extreme 20% | Lift |
|--------|-------------|-------------|------|
| Total Features Analyzed | 91,093 | 92,833 | - |
| Pairs Covered | 28 | 28 | - |
| Avg Max Correlation | 0.1451 | 0.1828 | **+26.0%** |
| Max Correlation | 0.9999 | 1.0000 | - |

**Key Finding:** Extreme 20% periods (highest BQX oscillation magnitude) show **26% stronger feature correlations** than the full dataset, confirming that predictive signals are amplified during high-volatility market conditions.

---

## Correlation by Horizon

All 7 horizons show remarkably consistent correlation strength:

| Horizon | Full Dataset | Extreme 20% | Lift |
|---------|-------------|-------------|------|
| h15 | 0.1448 | 0.1825 | +26.0% |
| h30 | 0.1447 | 0.1825 | +26.1% |
| h45 | 0.1447 | 0.1825 | +26.1% |
| h60 | 0.1447 | 0.1826 | +26.2% |
| h75 | 0.1447 | 0.1826 | +26.2% |
| h90 | 0.1448 | 0.1826 | +26.1% |
| h105 | 0.1448 | 0.1826 | +26.1% |

---

## Best Horizon Distribution

### Full Dataset
| Horizon | Features | Percentage |
|---------|----------|------------|
| h105 | 40,260 | 44.2% |
| h15 | 38,736 | 42.5% |
| h90 | 3,121 | 3.4% |
| h60 | 2,467 | 2.7% |
| h75 | 2,364 | 2.6% |
| h30 | 2,153 | 2.4% |
| h45 | 1,992 | 2.2% |

### Extreme 20%
| Horizon | Features | Percentage |
|---------|----------|------------|
| h105 | 44,905 | 48.4% |
| h15 | 33,905 | 36.5% |
| h90 | 3,318 | 3.6% |
| h75 | 3,025 | 3.3% |
| h30 | 2,583 | 2.8% |
| h45 | 2,559 | 2.8% |
| h60 | 2,538 | 2.7% |

~~**Insight:** Features predominantly perform best at extreme horizons (h15 and h105), with h105 slightly favored in Extreme periods.~~

---

## CRITICAL FINDING: The 87% h15/h105 Clustering is a Statistical Artifact

**Updated 2025-12-07:** Investigation revealed the apparent h15/h105 clustering is NOT a real signal.

### Evidence

| Spread Category (h15 vs h105) | Features | Percentage |
|-------------------------------|----------|------------|
| **Trivial (<0.1%)** | 68,361 | **77.4%** |
| Small (0.1-0.5%) | 18,828 | 21.3% |
| Moderate (0.5-1%) | 1,176 | 1.3% |
| Meaningful (>1%) | 5 | **0.0%** |

**Average h15↔h105 spread: 0.0007 (0.07%)** - statistically meaningless.

### Root Cause

1. **74.6% of features have MONOTONIC correlation patterns** - correlations either always increase or always decrease from h15 to h105
2. For monotonic patterns, the maximum is **mathematically forced** to an endpoint (h15 or h105)
3. The "choice" between h15 and h105 is essentially a **coin flip on noise**

### Example

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

### Implication

Features predict **MAGNITUDE** of BQX movement, not **TIMING** (which horizon). All 7 horizons receive essentially identical predictions. Training separate models for different horizons would be **redundant**.

---

## Feature Type Lift Analysis

Extreme 20% lift varies dramatically by feature type:

| Feature Type | Full Corr | Extreme Corr | Lift | Interpretation |
|--------------|-----------|--------------|------|----------------|
| **der** (derivatives) | 0.0091 | 0.0305 | **+235%** | Massive lift in extreme periods |
| **div** (divergence) | 0.0236 | 0.0786 | **+233%** | Strong volatility signal |
| **mrt** (mean reversion) | 0.0174 | 0.0538 | **+209%** | High extreme sensitivity |
| **align** (alignment) | 0.0097 | 0.0271 | **+179%** | Cross-pair alignment matters in extremes |
| **mom** (momentum) | 0.0250 | 0.0610 | **+144%** | Momentum amplified in extremes |
| **vol** (volatility) | 0.0862 | 0.1560 | **+81%** | Volatility features strong overall |
| **corr** (correlation) | 0.0568 | 0.1021 | **+80%** | Cross-asset correlations valuable |
| **rev** (reversal) | 0.0131 | 0.0214 | **+63%** | Reversal signals in extremes |
| **cov** (covariance) | 0.2653 | 0.3299 | **+24%** | Already high, modest lift |
| **agg** (aggregation) | 0.4801 | 0.5562 | **+16%** | Highest base, lower relative lift |
| **reg** (regression) | 0.2324 | 0.2625 | **+13%** | Strong base correlation |
| **lag** (lagged) | 0.5065 | 0.5471 | **+8%** | Highest correlation, lowest lift |

**Key Insight:** Features with LOW baseline correlations (der, div, mrt) show the HIGHEST lift in extreme periods, suggesting these are particularly valuable for predicting during high-volatility regimes.

---

## Top Features by Correlation

### Full Dataset (Non-BQX Features)
1. **reg_ci_lower_1440** - 0.9999 (27 pairs)
2. **reg_ci_upper_180** - 0.9999 (27 pairs)
3. **reg_mean_360** - 0.9999 (27 pairs)
4. **reg_ci_upper_2880** - 0.9999 (27 pairs)
5. **reg_min_360** - 0.9999 (27 pairs)

### Extreme 20% (Non-BQX Features)
1. **agg_mean_720** - 1.0000 (28 pairs)
2. **agg_mean_1440** - 1.0000 (28 pairs)
3. **agg_min_720** - 1.0000 (28 pairs)
4. **agg_max_720** - 1.0000 (28 pairs)
5. **agg_max_1440** - 1.0000 (28 pairs)

---

## Output Tables Created

| Table | Description | Rows |
|-------|-------------|------|
| `feature_correlations_by_horizon` | Full dataset correlations | 91,093 |
| `feature_correlations_by_horizon_extreme` | Extreme 20% correlations | 92,833 |
| `horizon_correlation_summary` | Summary statistics | 2 |
| `top_features_by_horizon` | Top 20 features per horizon | 280 |
| `feature_type_lift_comparison` | Lift by feature type | 13 |

---

## CSV Exports

Located in `/home/micha/bqx_ml_v3/exports/`:
- `top_features_full_dataset.csv` - Top 500 features (Full)
- `top_features_extreme_20pct.csv` - Top 500 features (Extreme)
- `feature_rankings_full_aggregated.csv` - Aggregated rankings (Full)
- `feature_rankings_extreme_aggregated.csv` - Aggregated rankings (Extreme)
- `feature_type_lift_comparison.csv` - Lift by feature type

---

## Recommendations

### VALID Recommendations

1. **Prioritize Extreme-Sensitive Features:** Features with high lift (der, div, mrt, align, mom) should be weighted more heavily during detected extreme periods. The +144% to +235% lift is a real signal.

2. **Covariance Features:** `cov_*` features represent the largest feature set (26K+) with solid 0.27-0.33 correlation and 24% lift. These provide stable baseline prediction.

### INVALIDATED Recommendation

~~**Horizon Strategy:** Consider separate models for h15 and h105 as these capture the majority of best-performing features.~~

**Status: INVALIDATED (2025-12-07)**

The 87% h15/h105 clustering is a statistical artifact caused by:
- Near-identical correlations across all horizons (spread ~0.07%)
- Monotonic patterns forcing endpoint selection
- Noise determining which endpoint "wins"

**Revised Strategy:** Train ONE model for magnitude prediction. All 7 horizons are redundant.

### CAUTIONARY Recommendation

3. **Aggregation Features:** `agg_*` features show near-perfect correlation (1.0) in extreme periods.

**CAUTION:** Perfect correlation may indicate data leakage or tautological relationship. Verify that `agg_*` features are computed BEFORE the BQX target period before relying on them for prediction.

---

## Summary of Validated Findings

| Finding | Status | Evidence |
|---------|--------|----------|
| Extreme 20% has +26% higher correlations | VALID | Consistent across all horizons |
| der/div/mrt features have +200% lift in extremes | VALID | Feature-type analysis |
| 87% of features best at h15/h105 | **ARTIFACT** | Spread <0.1% for 77% of features |
| cov_* features have solid 0.27-0.33 correlation | VALID | Large feature set, consistent |
| agg_* features have perfect correlation | CAUTION | Possible data leakage |

---

*Report generated by BQX ML V3 Horizon Correlation Analysis Pipeline*
*Updated 2025-12-07 with critical artifact finding*
