# CE Directive: Comprehensive Feature-Target Correlation Tables

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 19:30 UTC
**Priority**: HIGH
**Subject**: Create ALL Feature-Target Correlation Tables with Parallel Workers

---

## OBJECTIVE

Create comprehensive correlation tables for **ALL 708 EURUSD features** against **ALL 49 target combinations** (7 BQX windows × 7 horizons).

---

## ARCHITECTURE

### Interval-Centric (CONFIRMED)
- All rolling calculations use `ROWS BETWEEN` (interval-based)
- NOT time-centric (no RANGE BETWEEN with timestamps)
- Each row = 1 interval (regardless of time gaps)

### Target Delta Formula
```sql
delta = target_bqx{W}_h{H} - bqx_{W}
```
Where:
- W = BQX window: 45, 90, 180, 360, 720, 1440, 2880
- H = Horizon: 15, 30, 45, 60, 75, 90, 105

### Output Table Schema
Each correlation table will have:
- `interval_time` (TIMESTAMP) - Primary key
- `pair` (STRING) - Currency pair
- `feature_value` (FLOAT) - The feature value at that interval
- 49 correlation columns: `corr_w{W}_h{H}` (FLOAT)

---

## COMPLETE FEATURE INVENTORY

### Phase 1: AGG Features (126 features)
| Source Table | Features |
|--------------|----------|
| agg_bqx_eurusd | agg_mean_45, agg_std_45, agg_min_45, agg_max_45, agg_range_45, agg_cv_45, agg_position_45, agg_sum_45, agg_count_45, agg_mean_90, agg_std_90, agg_min_90, agg_max_90, agg_range_90, agg_cv_90, agg_position_90, agg_sum_90, agg_count_90, agg_mean_180, agg_std_180, agg_min_180, agg_max_180, agg_range_180, agg_cv_180, agg_position_180, agg_sum_180, agg_count_180, agg_mean_360, agg_std_360, agg_min_360, agg_max_360, agg_range_360, agg_cv_360, agg_position_360, agg_sum_360, agg_count_360, agg_mean_720, agg_std_720, agg_min_720, agg_max_720, agg_range_720, agg_cv_720, agg_position_720, agg_sum_720, agg_count_720, agg_mean_1440, agg_std_1440, agg_min_1440, agg_max_1440, agg_range_1440, agg_cv_1440, agg_position_1440, agg_sum_1440, agg_count_1440, agg_mean_2880, agg_std_2880, agg_min_2880, agg_max_2880, agg_range_2880, agg_cv_2880, agg_position_2880, agg_sum_2880, agg_count_2880 |
| agg_eurusd | (same 63 features as above) |

### Phase 2: REG Features (140 features)
| Source Table | Features |
|--------------|----------|
| reg_bqx_eurusd | reg_mean_45, reg_std_45, reg_min_45, reg_max_45, reg_first_45, reg_slope_45, reg_direction_45, reg_deviation_45, reg_zscore_45, reg_range_pct_45, (×7 windows = 70 features) |
| reg_eurusd | (same 70 features) |

### Phase 3: MOM Features (84 features)
| Source Table | Features |
|--------------|----------|
| mom_bqx_eurusd | mom_roc_45, mom_roc_90, mom_roc_180, mom_roc_360, mom_roc_720, mom_roc_1440, mom_diff_45, mom_diff_90, mom_diff_180, mom_diff_360, mom_diff_720, mom_diff_1440, mom_dir_45, mom_dir_90, mom_dir_180, mom_dir_360, mom_dir_720, mom_dir_1440, mom_roc_smooth_45, mom_zscore_45, mom_pos_count_45, mom_strength_45, (×6 windows = 42 features) |
| mom_eurusd | (same 42 features) |

### Phase 4: ALIGN Features (82 features)
| Source Table | Features |
|--------------|----------|
| align_bqx_eurusd | dir_45, dir_90, dir_180, dir_360, dir_720, dir_1440, pos_45, pos_90, pos_180, pos_360, pos_720, pos_1440, zscore_45, zscore_90, zscore_180, zscore_360, zscore_720, zscore_1440, align_trend_45_90, align_pos_diff_45_90, align_mean_45_90, align_zscore_diff_45_90, align_trend_90_180, align_pos_diff_90_180, align_mean_90_180, align_zscore_diff_90_180, align_trend_180_360, align_pos_diff_180_360, align_mean_180_360, align_zscore_diff_180_360, align_trend_360_720, align_pos_diff_360_720, align_mean_360_720, align_zscore_diff_360_720, align_trend_720_1440, align_pos_diff_720_1440, align_mean_720_1440, align_zscore_diff_720_1440, align_trend_score, align_unanimous, align_mean_score (41 features) |
| align_eurusd | (same 41 features) |

### Phase 5: VOL Features (60 features)
| Source Table | Features |
|--------------|----------|
| vol_bqx_eurusd | vol_realized_45, vol_realized_90, vol_realized_180, vol_realized_360, vol_realized_720, vol_atr_45, vol_atr_90, vol_atr_180, vol_atr_360, vol_atr_720, vol_normalized_45, vol_normalized_90, vol_normalized_180, vol_normalized_360, vol_normalized_720, vol_range_pct_45, vol_range_pct_90, vol_range_pct_180, vol_range_pct_360, vol_range_pct_720, vol_of_vol_45, vol_of_vol_90, vol_of_vol_180, vol_of_vol_360, vol_of_vol_720, vol_zscore_45, vol_zscore_90, vol_zscore_180, vol_zscore_360, vol_zscore_720 (30 features) |
| vol_eurusd | (same 30 features) |

### Phase 6: DER/DIV/MRT/REV/EXT Features (89 features)
| Source Table | Features | Count |
|--------------|----------|-------|
| der_bqx_eurusd | der_v1_45, der_v1_90, der_v1_180, der_v1_360, der_v1_720, der_v1_1440, der_v1_2880, der_v2_45, der_v2_90, der_v2_180, der_v2_360, der_v2_720, der_v2_1440, der_v2_2880, der_v3_composite | 15 |
| der_eurusd | (same) | 15 |
| div_bqx_eurusd | div_45_2880, div_90_1440, div_180_720, div_sign_alignment, div_cascade_direction, div_short_leading | 6 |
| div_eurusd | (same) | 6 |
| mrt_bqx_eurusd | mrt_tension_45, mrt_tension_90, mrt_tension_180, mrt_tension_360, mrt_tension_720, mrt_tension_1440, mrt_tension_2880, mrt_tension_composite, mrt_half_life, mrt_reversion_probability | 10 |
| mrt_eurusd | (same) | 10 |
| rev_bqx_eurusd | rev_decel_45, rev_decel_90, rev_decel_180, rev_decel_360, rev_decel_720, rev_decel_1440, rev_decel_2880, rev_exhaustion, rev_divergence, rev_turning_prob | 10 |
| rev_eurusd | (same) | 10 |
| ext_bqx_eurusd | ext_zscore_45, ext_zscore_90, ext_zscore_180, ext_zscore_360, ext_zscore_720, ext_zscore_1440, ext_zscore_2880, ext_percentile_45, ext_percentile_90, ext_percentile_180, ext_percentile_360, ext_percentile_720, ext_percentile_1440, ext_percentile_2880, ext_distance_zero, ext_sigma_band | 16 |

### Phase 7: LAG/REGIME/TMP/CYC Features (127 features)
| Source Table | Features | Count |
|--------------|----------|-------|
| lag_bqx_eurusd_45 | bqx_close, bqx_lag_45, return_lag_45, sma_45, ema_45, volatility_45, hl_range_45, momentum_45, positive_ratio_45 | 9 |
| lag_bqx_eurusd_90 | (same pattern for 90) | 9 |
| lag_eurusd_45 | close_lag_45, open_lag_45, high_lag_45, low_lag_45, volume_lag_45, return_lag_45, sma_45, volume_sma_45, volatility_45, hl_range_45, momentum_45 | 11 |
| lag_eurusd_90 | (same pattern for 90) | 11 |
| regime_bqx_eurusd_45 | volatility_45, hl_range_45, return_lag_45, momentum_45, volatility_regime_code, range_regime_code, return_regime_code, momentum_regime_code, vol_p33, vol_p66, range_p33, range_p66, momentum_p33, momentum_p66, (numeric only) | 14 |
| regime_bqx_eurusd_90 | (same pattern for 90) | 14 |
| regime_eurusd_45 | volatility_45, hl_range_45, return_lag_45, volatility_regime_code, range_regime_code, return_regime_code, vol_p33, vol_p66, range_p33, range_p66 (numeric only) | 10 |
| regime_eurusd_90 | (same pattern for 90) | 10 |
| tmp_bqx_eurusd | tmp_hour_utc, tmp_day_of_week, tmp_is_london, tmp_is_ny, tmp_is_asian, tmp_is_overlap_london_ny, tmp_month, tmp_quarter, tmp_is_weekend, tmp_minute (numeric only) | 10 |
| tmp_eurusd | (same) | 10 |
| cyc_bqx_eurusd | cyc_intervals_since_zero, cyc_intervals_since_ext, cyc_avg_cycle_length, cyc_current_cycle_progress | 4 |

---

## IMPLEMENTATION

### SQL Template for Rolling Correlation
```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.ftcorr_{feature_name}_eurusd` AS
WITH feature_data AS (
  SELECT
    f.interval_time,
    f.pair,
    f.{feature_column} as feature_value
  FROM `bqx-ml.bqx_ml_v3_features.{source_table}` f
  WHERE f.pair = 'EURUSD'
),
target_data AS (
  SELECT
    t.interval_time,
    -- Delta calculations for all 49 combinations
    t.target_bqx45_h15 - t.bqx_45 as d_w45_h15,
    t.target_bqx45_h30 - t.bqx_45 as d_w45_h30,
    t.target_bqx45_h45 - t.bqx_45 as d_w45_h45,
    t.target_bqx45_h60 - t.bqx_45 as d_w45_h60,
    t.target_bqx45_h75 - t.bqx_45 as d_w45_h75,
    t.target_bqx45_h90 - t.bqx_45 as d_w45_h90,
    t.target_bqx45_h105 - t.bqx_45 as d_w45_h105,
    t.target_bqx90_h15 - t.bqx_90 as d_w90_h15,
    t.target_bqx90_h30 - t.bqx_90 as d_w90_h30,
    t.target_bqx90_h45 - t.bqx_90 as d_w90_h45,
    t.target_bqx90_h60 - t.bqx_90 as d_w90_h60,
    t.target_bqx90_h75 - t.bqx_90 as d_w90_h75,
    t.target_bqx90_h90 - t.bqx_90 as d_w90_h90,
    t.target_bqx90_h105 - t.bqx_90 as d_w90_h105,
    t.target_bqx180_h15 - t.bqx_180 as d_w180_h15,
    t.target_bqx180_h30 - t.bqx_180 as d_w180_h30,
    t.target_bqx180_h45 - t.bqx_180 as d_w180_h45,
    t.target_bqx180_h60 - t.bqx_180 as d_w180_h60,
    t.target_bqx180_h75 - t.bqx_180 as d_w180_h75,
    t.target_bqx180_h90 - t.bqx_180 as d_w180_h90,
    t.target_bqx180_h105 - t.bqx_180 as d_w180_h105,
    t.target_bqx360_h15 - t.bqx_360 as d_w360_h15,
    t.target_bqx360_h30 - t.bqx_360 as d_w360_h30,
    t.target_bqx360_h45 - t.bqx_360 as d_w360_h45,
    t.target_bqx360_h60 - t.bqx_360 as d_w360_h60,
    t.target_bqx360_h75 - t.bqx_360 as d_w360_h75,
    t.target_bqx360_h90 - t.bqx_360 as d_w360_h90,
    t.target_bqx360_h105 - t.bqx_360 as d_w360_h105,
    t.target_bqx720_h15 - t.bqx_720 as d_w720_h15,
    t.target_bqx720_h30 - t.bqx_720 as d_w720_h30,
    t.target_bqx720_h45 - t.bqx_720 as d_w720_h45,
    t.target_bqx720_h60 - t.bqx_720 as d_w720_h60,
    t.target_bqx720_h75 - t.bqx_720 as d_w720_h75,
    t.target_bqx720_h90 - t.bqx_720 as d_w720_h90,
    t.target_bqx720_h105 - t.bqx_720 as d_w720_h105,
    t.target_bqx1440_h15 - t.bqx_1440 as d_w1440_h15,
    t.target_bqx1440_h30 - t.bqx_1440 as d_w1440_h30,
    t.target_bqx1440_h45 - t.bqx_1440 as d_w1440_h45,
    t.target_bqx1440_h60 - t.bqx_1440 as d_w1440_h60,
    t.target_bqx1440_h75 - t.bqx_1440 as d_w1440_h75,
    t.target_bqx1440_h90 - t.bqx_1440 as d_w1440_h90,
    t.target_bqx1440_h105 - t.bqx_1440 as d_w1440_h105,
    t.target_bqx2880_h15 - t.bqx_2880 as d_w2880_h15,
    t.target_bqx2880_h30 - t.bqx_2880 as d_w2880_h30,
    t.target_bqx2880_h45 - t.bqx_2880 as d_w2880_h45,
    t.target_bqx2880_h60 - t.bqx_2880 as d_w2880_h60,
    t.target_bqx2880_h75 - t.bqx_2880 as d_w2880_h75,
    t.target_bqx2880_h90 - t.bqx_2880 as d_w2880_h90,
    t.target_bqx2880_h105 - t.bqx_2880 as d_w2880_h105
  FROM `bqx-ml.bqx_ml_v3_analytics.targets_eurusd` t
)
SELECT
  f.interval_time,
  f.pair,
  f.feature_value,
  -- Rolling correlations (720-interval window, INTERVAL-CENTRIC)
  CORR(f.feature_value, t.d_w45_h15) OVER w as corr_w45_h15,
  CORR(f.feature_value, t.d_w45_h30) OVER w as corr_w45_h30,
  CORR(f.feature_value, t.d_w45_h45) OVER w as corr_w45_h45,
  CORR(f.feature_value, t.d_w45_h60) OVER w as corr_w45_h60,
  CORR(f.feature_value, t.d_w45_h75) OVER w as corr_w45_h75,
  CORR(f.feature_value, t.d_w45_h90) OVER w as corr_w45_h90,
  CORR(f.feature_value, t.d_w45_h105) OVER w as corr_w45_h105,
  CORR(f.feature_value, t.d_w90_h15) OVER w as corr_w90_h15,
  CORR(f.feature_value, t.d_w90_h30) OVER w as corr_w90_h30,
  CORR(f.feature_value, t.d_w90_h45) OVER w as corr_w90_h45,
  CORR(f.feature_value, t.d_w90_h60) OVER w as corr_w90_h60,
  CORR(f.feature_value, t.d_w90_h75) OVER w as corr_w90_h75,
  CORR(f.feature_value, t.d_w90_h90) OVER w as corr_w90_h90,
  CORR(f.feature_value, t.d_w90_h105) OVER w as corr_w90_h105,
  CORR(f.feature_value, t.d_w180_h15) OVER w as corr_w180_h15,
  CORR(f.feature_value, t.d_w180_h30) OVER w as corr_w180_h30,
  CORR(f.feature_value, t.d_w180_h45) OVER w as corr_w180_h45,
  CORR(f.feature_value, t.d_w180_h60) OVER w as corr_w180_h60,
  CORR(f.feature_value, t.d_w180_h75) OVER w as corr_w180_h75,
  CORR(f.feature_value, t.d_w180_h90) OVER w as corr_w180_h90,
  CORR(f.feature_value, t.d_w180_h105) OVER w as corr_w180_h105,
  CORR(f.feature_value, t.d_w360_h15) OVER w as corr_w360_h15,
  CORR(f.feature_value, t.d_w360_h30) OVER w as corr_w360_h30,
  CORR(f.feature_value, t.d_w360_h45) OVER w as corr_w360_h45,
  CORR(f.feature_value, t.d_w360_h60) OVER w as corr_w360_h60,
  CORR(f.feature_value, t.d_w360_h75) OVER w as corr_w360_h75,
  CORR(f.feature_value, t.d_w360_h90) OVER w as corr_w360_h90,
  CORR(f.feature_value, t.d_w360_h105) OVER w as corr_w360_h105,
  CORR(f.feature_value, t.d_w720_h15) OVER w as corr_w720_h15,
  CORR(f.feature_value, t.d_w720_h30) OVER w as corr_w720_h30,
  CORR(f.feature_value, t.d_w720_h45) OVER w as corr_w720_h45,
  CORR(f.feature_value, t.d_w720_h60) OVER w as corr_w720_h60,
  CORR(f.feature_value, t.d_w720_h75) OVER w as corr_w720_h75,
  CORR(f.feature_value, t.d_w720_h90) OVER w as corr_w720_h90,
  CORR(f.feature_value, t.d_w720_h105) OVER w as corr_w720_h105,
  CORR(f.feature_value, t.d_w1440_h15) OVER w as corr_w1440_h15,
  CORR(f.feature_value, t.d_w1440_h30) OVER w as corr_w1440_h30,
  CORR(f.feature_value, t.d_w1440_h45) OVER w as corr_w1440_h45,
  CORR(f.feature_value, t.d_w1440_h60) OVER w as corr_w1440_h60,
  CORR(f.feature_value, t.d_w1440_h75) OVER w as corr_w1440_h75,
  CORR(f.feature_value, t.d_w1440_h90) OVER w as corr_w1440_h90,
  CORR(f.feature_value, t.d_w1440_h105) OVER w as corr_w1440_h105,
  CORR(f.feature_value, t.d_w2880_h15) OVER w as corr_w2880_h15,
  CORR(f.feature_value, t.d_w2880_h30) OVER w as corr_w2880_h30,
  CORR(f.feature_value, t.d_w2880_h45) OVER w as corr_w2880_h45,
  CORR(f.feature_value, t.d_w2880_h60) OVER w as corr_w2880_h60,
  CORR(f.feature_value, t.d_w2880_h75) OVER w as corr_w2880_h75,
  CORR(f.feature_value, t.d_w2880_h90) OVER w as corr_w2880_h90,
  CORR(f.feature_value, t.d_w2880_h105) OVER w as corr_w2880_h105
FROM feature_data f
JOIN target_data t ON f.interval_time = t.interval_time
WINDOW w AS (ORDER BY f.interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW);
```

---

## PARALLEL WORKER IMPLEMENTATION

### Worker Configuration
- **Total Features**: 708
- **Recommended Workers**: 8-12 parallel workers
- **Features per Worker**: ~60-90

### Phase Execution Schedule

| Phase | Worker Batch | Features | Tables |
|-------|--------------|----------|--------|
| 1A | Workers 1-4 | AGG (BQX) | 63 |
| 1B | Workers 5-8 | AGG (IDX) | 63 |
| 2A | Workers 1-4 | REG (BQX) | 70 |
| 2B | Workers 5-8 | REG (IDX) | 70 |
| 3A | Workers 1-4 | MOM (BQX) | 42 |
| 3B | Workers 5-8 | MOM (IDX) | 42 |
| 4A | Workers 1-4 | ALIGN (BQX) | 41 |
| 4B | Workers 5-8 | ALIGN (IDX) | 41 |
| 5A | Workers 1-4 | VOL (BQX) | 30 |
| 5B | Workers 5-8 | VOL (IDX) | 30 |
| 6 | All Workers | DER/DIV/MRT/REV/EXT | 89 |
| 7 | All Workers | LAG/REGIME/TMP/CYC | 127 |

---

## OUTPUT NAMING CONVENTION

```
ftcorr_{feature_type}_{variant}_{feature_name}_eurusd
```

Examples:
- `ftcorr_agg_bqx_mean_45_eurusd`
- `ftcorr_reg_idx_slope_90_eurusd`
- `ftcorr_div_bqx_45_2880_eurusd`

---

## VALIDATION REQUIREMENTS

After each phase:
1. Verify table count matches expected
2. Verify row count (~2.16M per table)
3. Verify 49 correlation columns present
4. Verify no NULL values in recent data (last 30 days)
5. Sample correlation values for sanity check

---

## REPORTING

Send progress reports after each phase completion:
- Tables created
- Validation status
- Any errors encountered
- ETA for next phase

---

*Directive issued: 2025-11-29 19:30 UTC*
*Chief Engineer, BQX ML V3*
