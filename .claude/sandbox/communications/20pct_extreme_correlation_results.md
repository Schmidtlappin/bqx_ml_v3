# 20% Extreme Period Correlation Analysis Results
**Date**: 2025-12-02
**Status**: COMPLETE

---

## Methodology

### Previous Approach (2σ Fixed Threshold)
- Used fixed ±2σ threshold across all pairs
- Coverage ranged from 0% to 7.5% (highly inconsistent)
- 4 pairs (GBPJPY, CHFJPY, USDJPY, EURCHF) had ZERO observations
- EURUSD dominated the extreme periods (~2.8% coverage)

### New Approach (20% Pair-Specific Percentiles)
- Each pair has UNIQUE thresholds based on its own bqx_45 distribution
- Bottom 10% + Top 10% = 20% most extreme observations per pair
- ~400K-437K extreme observations per pair (uniform coverage)
- All 28 pairs have meaningful representation

---

## Results Summary

### Tables Created
| Table | Rows | Description |
|-------|------|-------------|
| `pair_extreme_thresholds_20pct` | 28 | Pair-specific z-score thresholds |
| `pair_extreme_periods_20pct` | ~12M | Timestamps of extreme observations per pair |
| `feature_correlations_20pct_extreme` | 12,936 | Correlations for 231 features × 2 variants × 28 pairs |
| `feature_rankings_20pct_extreme` | 462 | Cross-pair aggregated rankings |

### Top Performing Features (BQX Variant)

| Rank | Feature | Avg Corr (28 pairs) | Max Corr | Top Pair |
|------|---------|---------------------|----------|----------|
| 1 | reg_std_2880 | 0.3284 | 0.7366 | EURUSD |
| 2 | reg_rmse_2880 | 0.3284 | 0.7366 | EURUSD |
| 3 | reg_resid_std_2880 | 0.3284 | 0.7366 | EURUSD |
| 4 | reg_std_1440 | 0.3071 | 0.6794 | GBPUSD |
| 5 | reg_rmse_1440 | 0.3071 | 0.6794 | GBPUSD |
| 6 | reg_resid_std_1440 | 0.3071 | 0.6794 | GBPUSD |
| 7 | reg_std_720 | 0.2751 | 0.5893 | GBPUSD |
| 8 | reg_rmse_720 | 0.2751 | 0.5893 | GBPUSD |
| 9 | reg_resid_std_720 | 0.2751 | 0.5893 | GBPUSD |
| 10 | reg_resid_max_2880 | 0.2696 | 0.5855 | GBPUSD |

### Pair Performance (BQX Variant)

| Tier | Pairs | Best Corr | Features >0.5 |
|------|-------|-----------|---------------|
| Strong (>0.5) | EURUSD, GBPUSD, GBPCAD, EURGBP | 0.53-0.74 | 3-23 |
| Moderate (0.3-0.5) | EURCAD, NZDCAD, GBPJPY, AUDCAD, NZDJPY, AUDJPY, AUDUSD | 0.31-0.49 | 0 |
| Lower (<0.3) | Remaining 17 pairs | 0.17-0.28 | 0 |

### Key Findings

1. **EURUSD/GBPUSD Dominance**: Even with pair-specific extreme periods, EURUSD and GBPUSD show significantly stronger correlations (0.73-0.74) than other pairs.

2. **Standard Deviation Features**: The `reg_std_*`, `reg_rmse_*`, and `reg_resid_std_*` features at longer lookback windows (2880, 1440, 720 minutes) consistently rank highest.

3. **Cross-Pair Consistency**:
   - 13/28 pairs (46%) have features with correlations > 0.3
   - 21/28 pairs (75%) have features with correlations > 0.2

4. **IDX vs BQX Variant**:
   - IDX variant shows near-perfect correlations (~1.0) for price-related features (potential data leakage)
   - BQX variant shows more realistic correlations (0.16-0.74)

---

## Tables Deleted (Prior Correlation Results)
- all_pairs_poly_correlation_matrix
- extreme_correlation_results
- extreme_sample_5000
- extreme_targets
- extreme_windows_301
- feature_correlation_ranking
- full_correlation_matrix
- full_correlation_matrix_v2
- new_poly_correlation_matrix
- top100_extreme_features

---

## Interpretation

The polynomial regression features (particularly standard deviation and RMSE at longer lookback windows) show predictive power for future BQX45 changes during extreme periods. However:

1. **Correlation is not uniform**: USD pairs (especially EURUSD, GBPUSD) show stronger relationships than crosses.

2. **Longer windows matter**: Features computed over 2880, 1440, and 720 minute windows outperform shorter windows.

3. **Variability features**: Standard deviation, RMSE, and variance features dominate rankings, suggesting that volatility measures during extremes predict future momentum changes.

---

*Analysis completed: 2025-12-02*
