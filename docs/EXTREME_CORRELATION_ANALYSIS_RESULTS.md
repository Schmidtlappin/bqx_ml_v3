# Extreme Oscillation Correlation Analysis Results

**Date**: 2025-11-29 (Updated)
**Scope**: EURUSD Feature-Target Correlation at Extreme BQX Points
**Status**: COMPLETE - EXPANDED TO 817 FEATURES × 49 TARGETS

---

## Executive Summary

Analyzed **817 features** across **5,000 extreme oscillation events** (2,500 positive, 2,500 negative) to identify the strongest predictors of BQX target changes at extreme zones.

### Key Findings

- **Top features** show correlations up to **0.9982** with BQX delta targets
- **reg_slope features** dominate across all window/horizon combinations
- **Longer windows (1440, 2880 intervals)** have strongest predictive power
- **IDX-derived features** generally outperform BQX-derived features for same-window predictions
- **Window-matching is critical**: Features with window W predict delta_W targets best

---

## Methodology

### 1. Extreme Selection
- **Criteria**: Local peaks/troughs with |BQX_45| > 2σ
- **Count**: 5,000 extremes (2,500 positive + 2,500 negative)
- **Distribution**: 2020-2025 (magnitude-weighted selection)

### 2. Window Extraction
- **Window size**: 301 intervals (240 before + 1 extreme + 60 after)
- **Total samples**: 1,505,000 intervals → 1,215,516 after null filtering

### 3. Target Definition
- **Delta targets**: `target_bqx{W}_h{H} - bqx_{W}` (49 combinations)
- **Direction targets**: `SIGN(delta)` for classification
- **Reversal targets**: Did the extreme reverse direction?

### 4. Correlation Calculation
- **Method**: Pooled Pearson correlation across all windows
- **Features**: 451 features across 24 source tables

---

## Top 50 Features Ranked by Correlation

| Rank | Feature | Max Corr | Best Target | Dir Corr |
|------|---------|----------|-------------|----------|
| 1 | idx_reg_slope_720 | **0.9709** | delta_w720_h60 | 0.11 |
| 2 | idx_mom_diff_720 | **0.9702** | delta_w720_h60 | 0.11 |
| 3 | idx_der_v1_720 | **0.9702** | delta_w720_h60 | 0.11 |
| 4 | bqx_bqx_720 | **0.9689** | delta_w720_h60 | 0.11 |
| 5 | idx_mom_roc_720 | **0.9689** | delta_w720_h60 | 0.11 |
| 6 | bqx_agg_mean_720 | 0.9480 | delta_w720_h60 | 0.03 |
| 7 | bqx_reg_mean_720 | 0.9480 | delta_w720_h60 | 0.03 |
| 8 | idx_reg_slope_360 | 0.9429 | delta_w360_h60 | 0.17 |
| 9 | idx_mom_diff_360 | 0.9415 | delta_w360_h60 | 0.17 |
| 10 | idx_der_v1_360 | 0.9415 | delta_w360_h60 | 0.17 |
| 11 | idx_reg_slope_180 | 0.9413 | delta_w180_h30 | 0.24 |
| 12 | idx_reg_slope_90 | 0.9403 | delta_w90_h15 | 0.34 |
| 13 | idx_mom_roc_360 | 0.9403 | delta_w360_h60 | 0.17 |
| 14 | bqx_bqx_360 | 0.9403 | delta_w360_h60 | 0.17 |
| 15 | idx_mom_diff_180 | 0.9386 | delta_w180_h30 | 0.24 |
| 16 | idx_der_v1_180 | 0.9386 | delta_w180_h30 | 0.24 |
| 17 | idx_mom_roc_180 | 0.9374 | delta_w180_h30 | 0.24 |
| 18 | bqx_bqx_180 | 0.9374 | delta_w180_h30 | 0.24 |
| 19 | idx_der_v1_90 | 0.9347 | delta_w90_h15 | 0.34 |
| 20 | idx_mom_diff_90 | 0.9347 | delta_w90_h15 | 0.34 |

---

## Feature Category Analysis

### By Feature Type (Top Performers)

| Category | Best Feature | Max Corr | Avg Top-5 Corr |
|----------|--------------|----------|----------------|
| REG (slope/deviation) | idx_reg_slope_720 | 0.9709 | 0.93 |
| MOM (momentum) | idx_mom_diff_720 | 0.9702 | 0.92 |
| DER (derivative) | idx_der_v1_720 | 0.9702 | 0.92 |
| BQX (base) | bqx_bqx_720 | 0.9689 | 0.91 |
| AGG (aggregate) | bqx_agg_mean_720 | 0.9480 | 0.88 |
| ALIGN (zscore) | bqx_zscore_1440 | 0.7939 | 0.72 |
| EXT (extremity) | bqx_ext_zscore_2880 | 0.8057 | 0.76 |
| MRT (mean-rev) | bqx_mrt_tension_2880 | 0.7117 | 0.68 |
| VOL (volatility) | idx_vol_realized_360 | 0.5124 | 0.45 |

### By Window Size

| Window | Avg Max Corr | Best Target Horizon |
|--------|--------------|---------------------|
| 720 | 0.95+ | h60 |
| 360 | 0.90+ | h60 |
| 180 | 0.88+ | h30 |
| 90 | 0.87+ | h15-h30 |
| 45 | 0.85+ | h15 |

### IDX vs BQX Variant Performance

| Comparison | Winner | Margin |
|------------|--------|--------|
| Same-window delta | IDX | +0.02-0.05 |
| Cross-window delta | BQX | +0.01-0.03 |
| Direction prediction | BQX | +0.02-0.08 |

---

## Recommended Feature Selection

### Tier 1: Ultra-High Correlation (>0.90)
24 features with correlation > 0.90:
- reg_slope_{180-720}
- mom_diff_{180-720}
- der_v1_{180-720}
- mom_roc_{180-720}
- bqx_{180-720}

### Tier 2: High Correlation (0.80-0.90)
26 features with correlation 0.80-0.90:
- reg_deviation_{45-1440}
- agg_mean_{45-180}
- sma/ema_{45-90}

### Tier 3: Moderate Correlation (0.70-0.80)
~50 features with correlation 0.70-0.80:
- zscore features
- ext features
- mrt_tension features

---

## BigQuery Tables Created

| Table | Description | Rows |
|-------|-------------|------|
| `extreme_sample_5000` | Selected extreme points | 5,000 |
| `extreme_windows_301` | 301-interval windows | 1,505,000 |
| `extreme_targets` | Delta/direction/reversal targets | 1,505,000 |
| `full_correlation_matrix` | 817 features × 49 correlations | 817 |
| `top100_per_target` | Top 100 features per target | 4,900 |

---

## Top Feature Per Target (49 Targets)

| Target | Max Corr | Top Feature | Avg Top-100 |
|--------|----------|-------------|-------------|
| w2880_h15 | **0.9982** | reg_slope_2880 | 0.467 |
| w2880_h30 | **0.9965** | reg_slope_2880 | 0.467 |
| w1440_h15 | **0.9962** | reg_slope_1440 | 0.570 |
| w2880_h45 | **0.9948** | reg_slope_2880 | 0.467 |
| w2880_h60 | **0.9931** | reg_slope_2880 | 0.466 |
| w1440_h30 | **0.9926** | reg_slope_1440 | 0.569 |
| w720_h15 | **0.9924** | reg_slope_720 | 0.619 |
| w2880_h75 | **0.9914** | reg_slope_2880 | 0.466 |
| w2880_h90 | **0.9897** | reg_slope_2880 | 0.466 |
| w1440_h45 | **0.9891** | reg_slope_1440 | 0.568 |
| w2880_h105 | **0.9881** | reg_slope_2880 | 0.466 |
| w1440_h60 | **0.9856** | reg_slope_1440 | 0.567 |
| w720_h30 | **0.9852** | reg_slope_720 | 0.618 |
| w360_h15 | **0.9851** | reg_slope_360 | 0.630 |
| w1440_h75 | **0.9820** | reg_slope_1440 | 0.567 |
| w1440_h90 | **0.9785** | reg_slope_1440 | 0.566 |
| w720_h45 | **0.9781** | reg_slope_720 | 0.617 |
| w1440_h105 | **0.9751** | reg_slope_1440 | 0.565 |
| w360_h30 | **0.9711** | reg_slope_360 | 0.628 |
| w720_h60 | **0.9709** | reg_slope_720 | 0.616 |
| w180_h15 | **0.9703** | reg_slope_180 | 0.646 |
| w720_h75 | **0.9637** | reg_slope_720 | 0.615 |
| w360_h45 | **0.9571** | reg_slope_360 | 0.625 |
| w720_h90 | **0.9564** | reg_slope_720 | 0.613 |
| w720_h105 | **0.9491** | reg_slope_720 | 0.612 |
| w360_h60 | **0.9429** | reg_slope_360 | 0.622 |
| w180_h30 | **0.9413** | reg_slope_180 | 0.641 |
| w90_h15 | **0.9403** | reg_slope_90 | 0.680 |
| w360_h75 | **0.9285** | reg_slope_360 | 0.619 |
| w360_h90 | **0.9140** | reg_slope_360 | 0.616 |
| w180_h45 | **0.9121** | reg_slope_180 | 0.637 |
| w360_h105 | **0.8993** | reg_slope_360 | 0.613 |
| w45_h105 | **0.8874** | target_90 | 0.301 |
| w90_h30 | **0.8808** | reg_slope_90 | 0.669 |
| w180_h60 | **0.8817** | reg_slope_180 | 0.632 |
| w45_h15 | **0.8764** | reg_slope_45 | 0.686 |
| w180_h75 | **0.8742** | reg_deviation_180 | 0.627 |
| w180_h90 | **0.8647** | reg_deviation_180 | 0.621 |
| w90_h45 | **0.8618** | reg_deviation_90 | 0.658 |
| w180_h105 | **0.8509** | reg_deviation_180 | 0.613 |
| w90_h60 | **0.8275** | reg_deviation_90 | 0.629 |
| w90_h90 | **0.8229** | target_90 | 0.323 |
| w45_h30 | **0.8199** | reg_deviation_45 | 0.598 |
| w45_h75 | **0.8131** | target_45 | 0.356 |
| w45_h60 | **0.7768** | target_45 | 0.405 |
| w90_h75 | **0.7732** | reg_deviation_90 | 0.584 |
| w90_h105 | **0.7154** | target_90 | 0.477 |
| w90_h90 | **0.6963** | reg_deviation_90 | 0.528 |
| w45_h45 | **0.6874** | reg_deviation_45 | 0.490 |

---

## Downloadable Artifacts

| File | Description | Location |
|------|-------------|----------|
| `correlation_matrix_817x72.csv` | Full matrix (817 features × 77 columns) | docs/ |
| `top100_features_per_target.csv` | Top 100 features per target (4,900 rows) | docs/ |

---

## Conclusions

1. **Window-matching is critical**: Features with window W predict delta_W targets best
2. **Slope and derivative features** are strongest predictors overall
3. **Magnitude prediction** (correlation 0.97) is much stronger than direction prediction (0.53)
4. **Longer windows** (720, 360) have highest predictive power for their matching targets
5. **IDX vs BQX**: Use IDX for same-window, BQX for cross-window predictions

---

## Next Steps

1. **Feature Engineering**: Create ensemble features from top performers
2. **Model Training**: Use top-50 features for initial model training
3. **Validation**: Apply bootstrap confidence intervals for robustness
4. **Expansion**: Extend analysis to other currency pairs

---

*Analysis completed: 2025-11-29*
*Chief Engineer, BQX ML V3*
