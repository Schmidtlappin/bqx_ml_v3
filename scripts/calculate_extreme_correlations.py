#!/usr/bin/env python3
"""
Calculate pooled correlations between all EURUSD features and BQX target deltas
at extreme oscillation points.

Scope:
- 5,000 extremes (2,500+, 2,500-)
- 301-interval windows (240 before, 60 after)
- 737 features × 49 target combinations = 36,113 correlations
"""

import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT = "bqx-ml"
LOCATION = "us-central1"
MAX_WORKERS = 8

# Feature inventory: source_table -> list of feature columns
FEATURE_INVENTORY = {
    # AGG features (63 per variant)
    "agg_eurusd": [
        "agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45",
        "agg_cv_45", "agg_position_45", "agg_sum_45", "agg_count_45",
        "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90",
        "agg_cv_90", "agg_position_90", "agg_sum_90", "agg_count_90",
        "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180",
        "agg_cv_180", "agg_position_180", "agg_sum_180", "agg_count_180",
        "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360",
        "agg_cv_360", "agg_position_360", "agg_sum_360", "agg_count_360",
        "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720",
        "agg_cv_720", "agg_position_720", "agg_sum_720", "agg_count_720",
        "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440",
        "agg_cv_1440", "agg_position_1440", "agg_sum_1440", "agg_count_1440",
        "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880",
        "agg_cv_2880", "agg_position_2880", "agg_sum_2880", "agg_count_2880",
    ],
    "agg_bqx_eurusd": [
        "agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45",
        "agg_cv_45", "agg_position_45", "agg_sum_45", "agg_count_45",
        "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90",
        "agg_cv_90", "agg_position_90", "agg_sum_90", "agg_count_90",
        "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180",
        "agg_cv_180", "agg_position_180", "agg_sum_180", "agg_count_180",
        "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360",
        "agg_cv_360", "agg_position_360", "agg_sum_360", "agg_count_360",
        "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720",
        "agg_cv_720", "agg_position_720", "agg_sum_720", "agg_count_720",
        "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440",
        "agg_cv_1440", "agg_position_1440", "agg_sum_1440", "agg_count_1440",
        "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880",
        "agg_cv_2880", "agg_position_2880", "agg_sum_2880", "agg_count_2880",
    ],

    # REG features (70 per variant)
    "reg_eurusd": [
        "reg_mean_45", "reg_std_45", "reg_min_45", "reg_max_45", "reg_first_45",
        "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45", "reg_range_pct_45",
        "reg_mean_90", "reg_std_90", "reg_min_90", "reg_max_90", "reg_first_90",
        "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90", "reg_range_pct_90",
        "reg_mean_180", "reg_std_180", "reg_min_180", "reg_max_180", "reg_first_180",
        "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180", "reg_range_pct_180",
        "reg_mean_360", "reg_std_360", "reg_min_360", "reg_max_360", "reg_first_360",
        "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360", "reg_range_pct_360",
        "reg_mean_720", "reg_std_720", "reg_min_720", "reg_max_720", "reg_first_720",
        "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720", "reg_range_pct_720",
        "reg_mean_1440", "reg_std_1440", "reg_min_1440", "reg_max_1440", "reg_first_1440",
        "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440", "reg_range_pct_1440",
        "reg_mean_2880", "reg_std_2880", "reg_min_2880", "reg_max_2880", "reg_first_2880",
        "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880", "reg_range_pct_2880",
    ],
    "reg_bqx_eurusd": [
        "reg_mean_45", "reg_std_45", "reg_min_45", "reg_max_45", "reg_first_45",
        "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45", "reg_range_pct_45",
        "reg_mean_90", "reg_std_90", "reg_min_90", "reg_max_90", "reg_first_90",
        "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90", "reg_range_pct_90",
        "reg_mean_180", "reg_std_180", "reg_min_180", "reg_max_180", "reg_first_180",
        "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180", "reg_range_pct_180",
        "reg_mean_360", "reg_std_360", "reg_min_360", "reg_max_360", "reg_first_360",
        "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360", "reg_range_pct_360",
        "reg_mean_720", "reg_std_720", "reg_min_720", "reg_max_720", "reg_first_720",
        "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720", "reg_range_pct_720",
        "reg_mean_1440", "reg_std_1440", "reg_min_1440", "reg_max_1440", "reg_first_1440",
        "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440", "reg_range_pct_1440",
        "reg_mean_2880", "reg_std_2880", "reg_min_2880", "reg_max_2880", "reg_first_2880",
        "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880", "reg_range_pct_2880",
    ],

    # MOM features (42 per variant)
    "mom_eurusd": [
        "mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_roc_smooth_45", "mom_zscore_45", "mom_pos_count_45", "mom_strength_45",
        "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_roc_smooth_90", "mom_zscore_90", "mom_pos_count_90", "mom_strength_90",
        "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_roc_smooth_180", "mom_zscore_180", "mom_pos_count_180", "mom_strength_180",
        "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_roc_smooth_360", "mom_zscore_360", "mom_pos_count_360", "mom_strength_360",
        "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_roc_smooth_720", "mom_zscore_720", "mom_pos_count_720", "mom_strength_720",
        "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_roc_smooth_1440", "mom_zscore_1440", "mom_pos_count_1440", "mom_strength_1440",
    ],
    "mom_bqx_eurusd": [
        "mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_roc_smooth_45", "mom_zscore_45", "mom_pos_count_45", "mom_strength_45",
        "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_roc_smooth_90", "mom_zscore_90", "mom_pos_count_90", "mom_strength_90",
        "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_roc_smooth_180", "mom_zscore_180", "mom_pos_count_180", "mom_strength_180",
        "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_roc_smooth_360", "mom_zscore_360", "mom_pos_count_360", "mom_strength_360",
        "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_roc_smooth_720", "mom_zscore_720", "mom_pos_count_720", "mom_strength_720",
        "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_roc_smooth_1440", "mom_zscore_1440", "mom_pos_count_1440", "mom_strength_1440",
    ],

    # ALIGN features (41 per variant)
    "align_eurusd": [
        "dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
        "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
        "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
        "align_trend_45_90", "align_pos_diff_45_90", "align_mean_45_90", "align_zscore_diff_45_90",
        "align_trend_90_180", "align_pos_diff_90_180", "align_mean_90_180", "align_zscore_diff_90_180",
        "align_trend_180_360", "align_pos_diff_180_360", "align_mean_180_360", "align_zscore_diff_180_360",
        "align_trend_360_720", "align_pos_diff_360_720", "align_mean_360_720", "align_zscore_diff_360_720",
        "align_trend_720_1440", "align_pos_diff_720_1440", "align_mean_720_1440", "align_zscore_diff_720_1440",
        "align_trend_score", "align_unanimous", "align_mean_score",
    ],
    "align_bqx_eurusd": [
        "dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
        "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
        "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
        "align_trend_45_90", "align_pos_diff_45_90", "align_mean_45_90", "align_zscore_diff_45_90",
        "align_trend_90_180", "align_pos_diff_90_180", "align_mean_90_180", "align_zscore_diff_90_180",
        "align_trend_180_360", "align_pos_diff_180_360", "align_mean_180_360", "align_zscore_diff_180_360",
        "align_trend_360_720", "align_pos_diff_360_720", "align_mean_360_720", "align_zscore_diff_360_720",
        "align_trend_720_1440", "align_pos_diff_720_1440", "align_mean_720_1440", "align_zscore_diff_720_1440",
        "align_trend_score", "align_unanimous", "align_mean_score",
    ],

    # VOL features (30 per variant)
    "vol_eurusd": [
        "vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_range_pct_45", "vol_of_vol_45", "vol_zscore_45",
        "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_range_pct_90", "vol_of_vol_90", "vol_zscore_90",
        "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_range_pct_180", "vol_of_vol_180", "vol_zscore_180",
        "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_range_pct_360", "vol_of_vol_360", "vol_zscore_360",
        "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_range_pct_720", "vol_of_vol_720", "vol_zscore_720",
    ],
    "vol_bqx_eurusd": [
        "vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_range_pct_45", "vol_of_vol_45", "vol_zscore_45",
        "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_range_pct_90", "vol_of_vol_90", "vol_zscore_90",
        "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_range_pct_180", "vol_of_vol_180", "vol_zscore_180",
        "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_range_pct_360", "vol_of_vol_360", "vol_zscore_360",
        "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_range_pct_720", "vol_of_vol_720", "vol_zscore_720",
    ],

    # DER features (15 per variant)
    "der_eurusd": [
        "der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
        "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880",
        "der_v3_composite",
    ],
    "der_bqx_eurusd": [
        "der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
        "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880",
        "der_v3_composite",
    ],

    # DIV features (6 per variant)
    "div_eurusd": [
        "div_45_2880", "div_90_1440", "div_180_720",
        "div_sign_alignment", "div_cascade_direction", "div_short_leading",
    ],
    "div_bqx_eurusd": [
        "div_45_2880", "div_90_1440", "div_180_720",
        "div_sign_alignment", "div_cascade_direction", "div_short_leading",
    ],

    # MRT features (10 per variant)
    "mrt_eurusd": [
        "mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360",
        "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
        "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability",
    ],
    "mrt_bqx_eurusd": [
        "mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360",
        "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
        "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability",
    ],

    # REV features (10 per variant)
    "rev_eurusd": [
        "rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360",
        "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
        "rev_exhaustion", "rev_divergence", "rev_turning_prob",
    ],
    "rev_bqx_eurusd": [
        "rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360",
        "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
        "rev_exhaustion", "rev_divergence", "rev_turning_prob",
    ],

    # EXT features (16) - BQX only
    "ext_bqx_eurusd": [
        "ext_zscore_45", "ext_zscore_90", "ext_zscore_180", "ext_zscore_360",
        "ext_zscore_720", "ext_zscore_1440", "ext_zscore_2880",
        "ext_percentile_45", "ext_percentile_90", "ext_percentile_180", "ext_percentile_360",
        "ext_percentile_720", "ext_percentile_1440", "ext_percentile_2880",
        "ext_distance_zero", "ext_sigma_band",
    ],

    # CYC features (4) - BQX only
    "cyc_bqx_eurusd": [
        "cyc_intervals_since_zero", "cyc_intervals_since_ext",
        "cyc_avg_cycle_length", "cyc_current_cycle_progress",
    ],

    # TMP features (11 per variant)
    "tmp_eurusd": [
        "tmp_hour_utc", "tmp_day_of_week", "tmp_is_london", "tmp_is_ny", "tmp_is_asian",
        "tmp_is_overlap_london_ny", "tmp_session_phase", "tmp_month", "tmp_quarter",
        "tmp_is_weekend", "tmp_minute",
    ],
    "tmp_bqx_eurusd": [
        "tmp_hour_utc", "tmp_day_of_week", "tmp_is_london", "tmp_is_ny", "tmp_is_asian",
        "tmp_is_overlap_london_ny", "tmp_session_phase", "tmp_month", "tmp_quarter",
        "tmp_is_weekend", "tmp_minute",
    ],

    # LAG features
    "lag_eurusd_45": [
        "close_lag_45", "open_lag_45", "high_lag_45", "low_lag_45", "volume_lag_45",
        "return_lag_45", "sma_45", "volume_sma_45", "volatility_45", "hl_range_45", "momentum_45",
    ],
    "lag_eurusd_90": [
        "close_lag_90", "open_lag_90", "high_lag_90", "low_lag_90", "volume_lag_90",
        "return_lag_90", "sma_90", "volume_sma_90", "volatility_90", "hl_range_90", "momentum_90",
    ],
    "lag_bqx_eurusd_45": [
        "bqx_lag_45", "return_lag_45", "sma_45", "ema_45",
        "volatility_45", "hl_range_45", "momentum_45", "positive_ratio_45",
    ],
    "lag_bqx_eurusd_90": [
        "bqx_lag_90", "return_lag_90", "sma_90", "ema_90",
        "volatility_90", "hl_range_90", "momentum_90", "positive_ratio_90",
    ],

    # REGIME features
    "regime_eurusd_45": [
        "volatility_45", "hl_range_45", "return_lag_45",
        "volatility_regime_code", "range_regime_code", "return_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66",
    ],
    "regime_eurusd_90": [
        "volatility_90", "hl_range_90", "return_lag_90",
        "volatility_regime_code", "range_regime_code", "return_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66",
    ],
    "regime_bqx_eurusd_45": [
        "volatility_45", "hl_range_45", "return_lag_45", "momentum_45",
        "volatility_regime_code", "range_regime_code", "return_regime_code", "momentum_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66", "momentum_p33", "momentum_p66",
    ],
    "regime_bqx_eurusd_90": [
        "volatility_90", "hl_range_90", "return_lag_90", "momentum_90",
        "volatility_regime_code", "range_regime_code", "return_regime_code", "momentum_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66", "momentum_p33", "momentum_p66",
    ],

    # BASE features
    "eurusd_bqx": [
        "bqx_45", "target_45", "bqx_90", "target_90", "bqx_180", "target_180",
        "bqx_360", "target_360", "bqx_720", "target_720", "bqx_1440", "target_1440",
        "bqx_2880", "target_2880",
    ],
    "eurusd_idx": [
        "open_idx", "high_idx", "low_idx", "close_idx", "volume_idx",
    ],
}


def get_correlation_sql(source_table: str, feature_column: str) -> str:
    """Generate SQL for calculating 49 correlations for a single feature."""
    variant = "bqx" if "_bqx_" in source_table or source_table.endswith("_bqx") else "idx"
    feature_id = f"{variant}_{feature_column}"

    return f"""
SELECT
  '{feature_id}' as feature_id,
  '{source_table}' as source_table,
  '{feature_column}' as feature_column,
  COUNT(*) as n_samples,
  -- 49 correlations (7 windows x 7 horizons)
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h15) as corr_w45_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h30) as corr_w45_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h45) as corr_w45_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h60) as corr_w45_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h75) as corr_w45_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h90) as corr_w45_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w45_h105) as corr_w45_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h15) as corr_w90_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h30) as corr_w90_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h45) as corr_w90_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h60) as corr_w90_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h75) as corr_w90_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h90) as corr_w90_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w90_h105) as corr_w90_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h15) as corr_w180_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h30) as corr_w180_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h45) as corr_w180_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h60) as corr_w180_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h75) as corr_w180_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h90) as corr_w180_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w180_h105) as corr_w180_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h15) as corr_w360_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h30) as corr_w360_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h45) as corr_w360_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h60) as corr_w360_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h75) as corr_w360_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h90) as corr_w360_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w360_h105) as corr_w360_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h15) as corr_w720_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h30) as corr_w720_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h45) as corr_w720_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h60) as corr_w720_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h75) as corr_w720_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h90) as corr_w720_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w720_h105) as corr_w720_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h15) as corr_w1440_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h30) as corr_w1440_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h45) as corr_w1440_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h60) as corr_w1440_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h75) as corr_w1440_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h90) as corr_w1440_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w1440_h105) as corr_w1440_h105,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h15) as corr_w2880_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h30) as corr_w2880_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h45) as corr_w2880_h45,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h60) as corr_w2880_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h75) as corr_w2880_h75,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h90) as corr_w2880_h90,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.delta_w2880_h105) as corr_w2880_h105,
  -- Direction correlations (sample)
  CORR(CAST(f.{feature_column} AS FLOAT64), t.dir_w45_h15) as corr_dir_w45_h15,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.dir_w45_h30) as corr_dir_w45_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.dir_w45_h60) as corr_dir_w45_h60,
  -- Reversal correlations
  CORR(CAST(f.{feature_column} AS FLOAT64), t.reversal_w45_h30) as corr_reversal_w45_h30,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.reversal_w45_h60) as corr_reversal_w45_h60,
  CORR(CAST(f.{feature_column} AS FLOAT64), t.reversal_w45_h105) as corr_reversal_w45_h105
FROM `{PROJECT}.bqx_ml_v3_analytics.extreme_targets` t
JOIN `{PROJECT}.bqx_ml_v3_features.{source_table}` f
  ON t.interval_time = f.interval_time
WHERE f.{feature_column} IS NOT NULL
"""


def calculate_correlations_for_table(source_table: str, features: list) -> list:
    """Calculate correlations for all features in a source table."""
    results = []

    # Build UNION ALL query for all features in this table
    union_parts = []
    for feature in features:
        sql = get_correlation_sql(source_table, feature)
        union_parts.append(f"({sql})")

    full_sql = "\nUNION ALL\n".join(union_parts)

    cmd = [
        "bq", "--location", LOCATION, "query",
        "--use_legacy_sql=false",
        "--format=json",
        full_sql
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data
        else:
            print(f"ERROR for {source_table}: {result.stderr[:200]}")
            return []
    except Exception as e:
        print(f"EXCEPTION for {source_table}: {str(e)}")
        return []


def main():
    """Main execution."""
    # Count total features
    total_features = sum(len(features) for features in FEATURE_INVENTORY.values())
    print(f"Total features to process: {total_features}")
    print(f"Total tables: {len(FEATURE_INVENTORY)}")
    print("-" * 60)

    all_results = []
    completed = 0

    # Process tables sequentially (each table has multiple features)
    for source_table, features in FEATURE_INVENTORY.items():
        print(f"Processing {source_table} ({len(features)} features)...")

        results = calculate_correlations_for_table(source_table, features)
        all_results.extend(results)
        completed += len(features)

        print(f"  -> Got {len(results)} results. Total: {completed}/{total_features}")

    # Save results to file
    output_file = "/tmp/extreme_correlations_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("-" * 60)
    print(f"Total results: {len(all_results)}")
    print(f"Saved to: {output_file}")

    # Print top correlations
    if all_results:
        # Find max absolute correlation for each feature
        for r in all_results:
            corr_cols = [k for k in r.keys() if k.startswith('corr_w')]
            max_corr = max(abs(float(r[k] or 0)) for k in corr_cols)
            r['max_abs_corr'] = max_corr

        # Sort by max correlation
        sorted_results = sorted(all_results, key=lambda x: x.get('max_abs_corr', 0), reverse=True)

        print("\nTop 20 Features by Max Absolute Correlation:")
        print("-" * 80)
        for i, r in enumerate(sorted_results[:20]):
            print(f"{i+1:2}. {r['feature_id']}: max_corr={r['max_abs_corr']:.4f}")


if __name__ == "__main__":
    main()
