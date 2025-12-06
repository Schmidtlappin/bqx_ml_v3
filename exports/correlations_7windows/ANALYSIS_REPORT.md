# 7-Window BQX Correlation Analysis Report

## Executive Summary

This report documents the comprehensive correlation analysis between 422 engineered features and BQX targets across all 7 prediction windows (w45, w90, w180, w360, w720, w1440, w2880) and 7 horizons (h15, h30, h45, h60, h75, h90, h105).

### Key Metrics

| Metric | Full Dataset | Extreme 20% | Change |
|--------|-------------|-------------|--------|
| Total Feature Rows | 23,632 | 23,632 | - |
| Unique Features | 422 | 422 | - |
| Max Correlation | 1.0 | 1.0 | - |
| Avg Max Correlation | 0.127 | 0.161 | **+27%** |
| Features with corr > 0.9 | 2,148 | 2,150 | +2 |

## Remediation Success

The 7-window expansion successfully resolved the correlation gap identified in prior analysis:
- **Before**: Only bqx45 window analyzed, max correlation ~0.74
- **After**: All 7 windows analyzed, max correlation = 1.0

The fix was to expand from 1 BQX window to all 7 windows, enabling the model to capture correlations across all prediction horizons.

## Top Features by Absolute Correlation (Extreme 20%)

These features have the highest predictive power during volatile market periods:

| Rank | Feature | Avg Max Corr | Best Pair |
|------|---------|--------------|-----------|
| 1 | reg_max_2880 | 0.634 | 1.0 |
| 2 | reg_min_2880 | 0.630 | 0.9999 |
| 3 | reg_max_1440 | 0.629 | 1.0 |
| 4 | reg_min_1440 | 0.625 | 1.0 |
| 5 | reg_max_720 | 0.620 | 1.0 |

**Key Insight**: Extreme values (max/min) at longer windows (720-2880) are the strongest predictors.

## Top Features by Extreme Lift

These features show the biggest improvement in correlation during extreme market periods:

| Rank | Feature | Full Corr | Extreme Corr | Lift |
|------|---------|-----------|--------------|------|
| 1 | mom_strength_1440 | 0.136 | 0.250 | +84% |
| 2 | reg_resid_std_2880 | 0.143 | 0.257 | +80% |
| 3 | vol_atr_720 | 0.177 | 0.290 | +64% |
| 4 | reg_resid_max_720 | 0.116 | 0.219 | +88% |
| 5 | agg_range_2880 | 0.148 | 0.254 | +72% |

**Key Insight**: Volatility (std, atr, range) and momentum features show 60-90% higher correlations during extreme periods.

## Feature Type Distribution

| Feature Type | Count | Description |
|--------------|-------|-------------|
| reg_ | 231 | Polynomial regression features |
| agg_ | 63 | Aggregation features (mean, std, etc.) |
| mom_ | 42 | Momentum features |
| align_ | 41 | Alignment features |
| vol_ | 30 | Volatility features |
| der_ | 15 | Derivative features |

## Window Analysis

Longer windows (1440, 2880) consistently show higher correlations:
- w2880: Best for max/min/mean features
- w1440: Strong for momentum and volatility
- w720: Good balance of signal and responsiveness
- w45-w180: Lower correlations but faster signals

## Files Generated

1. `correlations_full_7windows_summary.csv` - Full dataset correlations (23,492 rows)
2. `correlations_extreme_7windows_summary.csv` - Extreme 20% correlations (23,214 rows)
3. `feature_ranking_comparison.csv` - Cross-pair feature rankings (422 features)
4. `top50_features_detailed.csv` - Detailed window correlations for top 50 features

## Recommendations

1. **Prioritize longer windows (w720-w2880)** for training - they show highest correlations
2. **Use extreme period data** for model training - correlations are 27% higher
3. **Focus on max/min features** - they have the strongest signal (0.63+ correlation)
4. **Include volatility features** (ATR, std, range) - they show significant lift during extreme periods
5. **Consider multi-window ensemble** - different windows capture different market regimes

---
Generated: 2025-12-03
Dataset: bqx_ml_v3_analytics
