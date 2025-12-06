# Extreme vs Full Dataset Correlation Comparison
**Date**: 2025-12-02
**Status**: COMPLETE

---

## Executive Summary

**Key Finding**: Volatility/variance features are **significantly MORE predictive during extreme periods** than during normal conditions. This supports the mean reversion hypothesis.

| Comparison | BQX Features | IDX Features |
|------------|--------------|--------------|
| Extreme MUCH stronger | 870 (13%) | 622 (10%) |
| Extreme stronger | 926 (14%) | 1,527 (24%) |
| Similar | 4,562 (71%) | 4,088 (63%) |
| Full stronger | 110 (2%) | 231 (4%) |

---

## Tables Created

| Table | Rows | Description |
|-------|------|-------------|
| `feature_correlations_full_dataset` | 12,936 | Correlations using ALL ~2.15M observations per pair |
| `feature_rankings_full_dataset` | 462 | Cross-pair aggregated rankings |
| `extreme_vs_full_correlation_comparison` | 12,936 | Direct comparison of extreme (20%) vs full correlations |

---

## Top Features: Extreme Much Stronger Than Full

These features show the largest gains in predictive power during extreme periods:

| Pair | Feature | Extreme Corr | Full Corr | Difference |
|------|---------|--------------|-----------|------------|
| GBPUSD | reg_total_var_2880 | 0.554 | 0.164 | **+0.390** |
| GBPUSD | reg_resid_var_2880 | 0.554 | 0.164 | **+0.390** |
| GBPUSD | reg_resid_var_1440 | 0.478 | 0.120 | **+0.358** |
| GBPJPY | reg_std_2880 | 0.470 | 0.117 | **+0.354** |
| EURCAD | reg_std_2880 | 0.492 | 0.152 | **+0.340** |
| EURUSD | reg_std_2880 | 0.737 | 0.398 | **+0.338** |
| GBPUSD | reg_std_2880 | 0.727 | 0.393 | **+0.334** |

### Pattern Observed
The features with the largest extreme-vs-full difference are:
1. **Variance features** (`reg_total_var_*`, `reg_resid_var_*`)
2. **Standard deviation features** (`reg_std_*`, `reg_resid_std_*`)
3. **RMSE features** (`reg_rmse_*`)
4. **Longer lookback windows** (2880, 1440 minutes)

---

## Interpretation

### Why Extreme Periods Show Stronger Correlations

1. **Mean Reversion Dynamics**: When bqx_45 is at an extreme (top/bottom 10%), it tends to revert. Features measuring volatility/deviation capture this reversion potential.

2. **Signal-to-Noise Ratio**: During extreme periods, the "signal" (momentum change) is larger, making correlations easier to detect.

3. **Regime Specificity**: The polynomial regression features were implicitly designed to capture dynamics that are more pronounced during volatile conditions.

### Practical Implications

| Scenario | Strategy |
|----------|----------|
| **Extreme Period Detected** | Weight volatility features (std, var, rmse) more heavily |
| **Normal Period** | Features have lower but still positive predictive power |
| **Model Design** | Consider regime-switching models that use different feature weights |

---

## Comparison by Feature Category

### Volatility Features (reg_std, reg_rmse, reg_resid_std)
- **Extreme Periods**: avg corr ~0.33
- **Full Dataset**: avg corr ~0.12
- **Improvement**: +0.21 (175% stronger in extremes)

### Variance Features (reg_total_var, reg_resid_var)
- **Extreme Periods**: avg corr ~0.26
- **Full Dataset**: avg corr ~0.09
- **Improvement**: +0.17 (189% stronger in extremes)

### Level Features (reg_mean, reg_min, reg_max)
- **Extreme Periods**: avg corr ~0.15
- **Full Dataset**: avg corr ~0.08
- **Improvement**: +0.07 (88% stronger in extremes)

### Trend Features (reg_slope, reg_direction)
- **Extreme Periods**: avg corr ~0.05
- **Full Dataset**: avg corr ~0.03
- **Improvement**: +0.02 (67% stronger in extremes)

---

## Pair-Level Summary

| Pair | Best Extreme Corr | Best Full Corr | Difference |
|------|-------------------|----------------|------------|
| EURUSD | 0.737 | 0.398 | +0.338 |
| GBPUSD | 0.727 | 0.393 | +0.334 |
| GBPCAD | 0.562 | 0.240 | +0.322 |
| EURGBP | 0.533 | 0.224 | +0.309 |
| EURCAD | 0.492 | 0.152 | +0.340 |
| GBPJPY | 0.470 | 0.117 | +0.354 |

---

## Conclusion

**Extreme periods amplify predictive power** for volatility-based polynomial features:
- Features that capture deviation, variance, and residual spread are 2-3x more correlated with future BQX changes during extreme periods
- This validates the 20% extreme threshold approach for identifying high-predictability regimes
- Longer lookback windows (1440, 2880 minutes) show the strongest extreme-vs-full differential

---

*Analysis completed: 2025-12-02*
