# Phase Plan: Full Dataset Correlation Analysis

## Objective
Correlate the COMPLETE dataset (all ~2.15M observations per pair) with all 231 polynomial features across both IDX and BQX variants, enabling comparison with the 20% extreme period correlations.

---

## Comparison Framework

### What We're Comparing

| Dataset | Observations/Pair | Coverage | Already Done? |
|---------|-------------------|----------|---------------|
| Extreme 20% | ~430K | Top 10% + Bottom 10% bqx_45 | ✅ Yes |
| Full Dataset | ~2.15M | 100% of all data | ❌ To Do |

### Expected Patterns

```
Scenario A: Extreme Correlation > Full Correlation
├── Interpretation: Features are MORE predictive during extreme conditions
├── Implication: Use features primarily for extreme period prediction
└── Example: Volatility features may better predict mean reversion during extremes

Scenario B: Extreme Correlation ≈ Full Correlation
├── Interpretation: Features have consistent predictive power
├── Implication: Features are robust across all market conditions
└── Example: Trend features may work equally well in all regimes

Scenario C: Extreme Correlation < Full Correlation
├── Interpretation: Extreme periods add noise or are unpredictable
├── Implication: Features work better for "normal" period prediction
└── Example: Some patterns may break down during volatile conditions
```

---

## Phase 1: Create Full Dataset Correlation Table

**Purpose**: Calculate correlations between all polynomial features and target horizons using the complete dataset for each pair.

**Approach**:
- For each pair, join `reg_bqx_{pair}` (or `reg_{pair}`) with `targets_{pair}`
- Calculate CORR(feature, target_bqx45_h{X}) for all features × horizons
- NO filtering by extreme periods - use all available observations

**Output Table**: `bqx_ml_v3_analytics.feature_correlations_full_dataset`

| Column | Description |
|--------|-------------|
| pair | Currency pair |
| variant | 'bqx' or 'idx' |
| feature_name | Polynomial feature name |
| n_samples | Total observations (~2.15M per pair) |
| corr_h15 | Correlation at 15-min horizon |
| corr_h30 | Correlation at 30-min horizon |
| corr_h45 | Correlation at 45-min horizon |
| corr_h60 | Correlation at 60-min horizon |
| corr_h75 | Correlation at 75-min horizon |
| corr_h90 | Correlation at 90-min horizon |
| corr_h105 | Correlation at 105-min horizon |
| avg_correlation | Average across all horizons |
| max_correlation | Maximum correlation (any horizon) |

**Estimated Rows**: 231 features × 2 variants × 28 pairs = 12,936 rows

---

## Phase 2: Create Full Dataset Feature Rankings

**Purpose**: Aggregate and rank features by correlation strength across all pairs.

**Output Table**: `bqx_ml_v3_analytics.feature_rankings_full_dataset`

| Column | Description |
|--------|-------------|
| feature_name | Polynomial feature name |
| variant | 'bqx' or 'idx' |
| pairs_with_data | Count of pairs with this feature |
| avg_corr_all_pairs | Average correlation across all pairs |
| std_corr_all_pairs | Standard deviation of correlations |
| max_corr_any_pair | Maximum correlation seen in any pair |
| top_pair | Pair with highest correlation |
| consistency_pct_01 | % of pairs where |corr| > 0.1 |
| consistency_pct_02 | % of pairs where |corr| > 0.2 |
| consistency_pct_03 | % of pairs where |corr| > 0.3 |

---

## Phase 3: Create Extreme vs Full Comparison Table

**Purpose**: Direct comparison of correlations between extreme periods and full dataset.

**Output Table**: `bqx_ml_v3_analytics.extreme_vs_full_correlation_comparison`

| Column | Description |
|--------|-------------|
| pair | Currency pair |
| variant | 'bqx' or 'idx' |
| feature_name | Polynomial feature name |
| extreme_n_samples | Samples in extreme dataset (~430K) |
| full_n_samples | Samples in full dataset (~2.15M) |
| extreme_avg_corr | Avg correlation in extreme periods |
| full_avg_corr | Avg correlation in full dataset |
| corr_diff | extreme_avg_corr - full_avg_corr |
| corr_ratio | extreme_avg_corr / full_avg_corr |
| extreme_stronger | Boolean: extreme > full |

### Interpretation Guide

| corr_diff | corr_ratio | Interpretation |
|-----------|------------|----------------|
| > 0.1 | > 1.5 | Feature is MUCH MORE predictive during extremes |
| 0.02 to 0.1 | 1.1 to 1.5 | Feature is somewhat more predictive during extremes |
| -0.02 to 0.02 | 0.9 to 1.1 | Feature has consistent predictive power |
| -0.1 to -0.02 | 0.5 to 0.9 | Feature is somewhat less predictive during extremes |
| < -0.1 | < 0.5 | Feature is MUCH LESS predictive during extremes |

---

## Phase 4: Generate Summary Reports

### 4A: Per-Pair Summary
For each pair, identify:
- Features where extreme > full (extreme-period specialists)
- Features where full > extreme (normal-period specialists)
- Features with consistent performance

### 4B: Cross-Pair Patterns
Identify:
- Universal extreme specialists (features that work better in extremes across many pairs)
- Universal normal specialists (features that work better in normal conditions across many pairs)
- Robust features (consistent performance regardless of market state)

### 4C: Feature Category Analysis
Group features by type and analyze patterns:
- Volatility features (reg_std_*, reg_rmse_*, reg_resid_std_*)
- Level features (reg_mean_*, reg_min_*, reg_max_*)
- Trend features (reg_slope_*, reg_direction_*)
- Polynomial features (reg_quad_term_*, reg_lin_term_*)

---

## Execution Estimates

| Phase | Tables Created | Estimated Rows | Time Estimate |
|-------|----------------|----------------|---------------|
| 1 | 1 | 12,936 | ~45 minutes |
| 2 | 1 | 462 | ~1 minute |
| 3 | 1 | 12,936 | ~2 minutes |
| 4 | Documentation | - | ~5 minutes |

**Total Estimated Time**: ~55 minutes

---

## Key Differences from Extreme Analysis

| Aspect | Extreme 20% | Full Dataset |
|--------|-------------|--------------|
| Observations | ~430K/pair | ~2.15M/pair |
| Coverage | Top/Bottom 10% | 100% |
| Sample size | 5× smaller | 5× larger |
| Market state | Volatile/extreme | All conditions |
| Statistical power | Lower (fewer samples) | Higher (more samples) |

---

## Expected Insights

1. **Volatility features** (reg_std_*, reg_rmse_*): Expected to show HIGHER correlations in extreme periods due to mean reversion dynamics

2. **Level features** (reg_mean_*, reg_min_*, reg_max_*): Expected to show SIMILAR correlations, as price levels are informative in all conditions

3. **Trend features** (reg_slope_*, reg_direction_*): Expected to show MIXED results - trends may be clearer in normal periods but reversals more predictable in extremes

4. **Polynomial terms** (reg_quad_term_*, reg_lin_term_*): Expected to capture non-linear dynamics better during extremes

---

## Ready for Execution?

Confirm to proceed with Phase 1.
