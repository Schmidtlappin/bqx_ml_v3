#!/usr/bin/env python3
"""
Batch correlation calculator for extreme oscillation analysis.
Processes features table by table using SQL files to avoid command line limits.
"""

import subprocess
import tempfile
import json
import os

PROJECT = "bqx-ml"
LOCATION = "us-central1"

# Feature tables and their columns
FEATURE_TABLES = {
    "agg_bqx_eurusd": ["agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45", "agg_cv_45", "agg_position_45",
                       "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90", "agg_cv_90", "agg_position_90",
                       "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180", "agg_cv_180", "agg_position_180",
                       "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360", "agg_cv_360", "agg_position_360",
                       "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720", "agg_cv_720", "agg_position_720",
                       "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440", "agg_cv_1440", "agg_position_1440",
                       "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880", "agg_cv_2880", "agg_position_2880"],
    "agg_eurusd": ["agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45", "agg_cv_45", "agg_position_45",
                   "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90", "agg_cv_90", "agg_position_90",
                   "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180", "agg_cv_180", "agg_position_180",
                   "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360", "agg_cv_360", "agg_position_360",
                   "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720", "agg_cv_720", "agg_position_720",
                   "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440", "agg_cv_1440", "agg_position_1440",
                   "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880", "agg_cv_2880", "agg_position_2880"],
    "reg_bqx_eurusd": ["reg_mean_45", "reg_std_45", "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45",
                       "reg_mean_90", "reg_std_90", "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90",
                       "reg_mean_180", "reg_std_180", "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180",
                       "reg_mean_360", "reg_std_360", "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360",
                       "reg_mean_720", "reg_std_720", "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720",
                       "reg_mean_1440", "reg_std_1440", "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440",
                       "reg_mean_2880", "reg_std_2880", "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880"],
    "reg_eurusd": ["reg_mean_45", "reg_std_45", "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45",
                   "reg_mean_90", "reg_std_90", "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90",
                   "reg_mean_180", "reg_std_180", "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180",
                   "reg_mean_360", "reg_std_360", "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360",
                   "reg_mean_720", "reg_std_720", "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720",
                   "reg_mean_1440", "reg_std_1440", "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440",
                   "reg_mean_2880", "reg_std_2880", "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880"],
    "mom_bqx_eurusd": ["mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_zscore_45", "mom_strength_45",
                       "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_zscore_90", "mom_strength_90",
                       "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_zscore_180", "mom_strength_180",
                       "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_zscore_360", "mom_strength_360",
                       "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_zscore_720", "mom_strength_720",
                       "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_zscore_1440", "mom_strength_1440"],
    "mom_eurusd": ["mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_zscore_45", "mom_strength_45",
                   "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_zscore_90", "mom_strength_90",
                   "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_zscore_180", "mom_strength_180",
                   "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_zscore_360", "mom_strength_360",
                   "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_zscore_720", "mom_strength_720",
                   "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_zscore_1440", "mom_strength_1440"],
    "align_bqx_eurusd": ["dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
                         "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
                         "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
                         "align_trend_score", "align_unanimous", "align_mean_score"],
    "align_eurusd": ["dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
                     "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
                     "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
                     "align_trend_score", "align_unanimous", "align_mean_score"],
    "vol_bqx_eurusd": ["vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_zscore_45",
                       "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_zscore_90",
                       "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_zscore_180",
                       "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_zscore_360",
                       "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_zscore_720"],
    "vol_eurusd": ["vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_zscore_45",
                   "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_zscore_90",
                   "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_zscore_180",
                   "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_zscore_360",
                   "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_zscore_720"],
    "der_bqx_eurusd": ["der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
                       "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880", "der_v3_composite"],
    "der_eurusd": ["der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
                   "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880", "der_v3_composite"],
    "mrt_bqx_eurusd": ["mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360", "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
                       "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability"],
    "mrt_eurusd": ["mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360", "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
                   "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability"],
    "rev_bqx_eurusd": ["rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360", "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
                       "rev_exhaustion", "rev_divergence", "rev_turning_prob"],
    "rev_eurusd": ["rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360", "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
                   "rev_exhaustion", "rev_divergence", "rev_turning_prob"],
    "ext_bqx_eurusd": ["ext_zscore_45", "ext_zscore_90", "ext_zscore_180", "ext_zscore_360", "ext_zscore_720", "ext_zscore_1440", "ext_zscore_2880",
                       "ext_percentile_45", "ext_percentile_90", "ext_percentile_180", "ext_percentile_360", "ext_percentile_720", "ext_percentile_1440", "ext_percentile_2880",
                       "ext_distance_zero", "ext_sigma_band"],
    "cyc_bqx_eurusd": ["cyc_intervals_since_zero", "cyc_intervals_since_ext", "cyc_avg_cycle_length", "cyc_current_cycle_progress"],
    "lag_bqx_eurusd_45": ["bqx_lag_45", "return_lag_45", "sma_45", "ema_45", "volatility_45", "hl_range_45", "momentum_45", "positive_ratio_45"],
    "lag_bqx_eurusd_90": ["bqx_lag_90", "return_lag_90", "sma_90", "ema_90", "volatility_90", "hl_range_90", "momentum_90", "positive_ratio_90"],
    "lag_eurusd_45": ["close_lag_45", "return_lag_45", "sma_45", "volatility_45", "hl_range_45", "momentum_45"],
    "lag_eurusd_90": ["close_lag_90", "return_lag_90", "sma_90", "volatility_90", "hl_range_90", "momentum_90"],
    "eurusd_bqx": ["bqx_45", "bqx_90", "bqx_180", "bqx_360", "bqx_720", "bqx_1440", "bqx_2880"],
    "eurusd_idx": ["close_idx", "volume_idx"],
}


def generate_correlation_sql(table_name: str, features: list) -> str:
    """Generate SQL for correlating all features in a table."""
    variant = "bqx" if "_bqx_" in table_name or table_name.endswith("_bqx") else "idx"

    union_parts = []
    for feature in features:
        feature_id = f"{variant}_{feature}"
        sql = f"""
SELECT
  '{feature_id}' as feature_id,
  '{table_name}' as source_table,
  COUNT(*) as n_samples,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w45_h15) as corr_w45_h15,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w45_h30) as corr_w45_h30,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w45_h60) as corr_w45_h60,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w45_h105) as corr_w45_h105,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w90_h15) as corr_w90_h15,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w90_h30) as corr_w90_h30,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w90_h60) as corr_w90_h60,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w90_h105) as corr_w90_h105,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w180_h30) as corr_w180_h30,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w180_h60) as corr_w180_h60,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w360_h60) as corr_w360_h60,
  CORR(CAST(f.{feature} AS FLOAT64), t.delta_w720_h60) as corr_w720_h60,
  CORR(CAST(f.{feature} AS FLOAT64), t.dir_w45_h30) as corr_dir_w45_h30,
  CORR(CAST(f.{feature} AS FLOAT64), t.reversal_w45_h60) as corr_reversal_w45_h60
FROM `{PROJECT}.bqx_ml_v3_analytics.extreme_targets` t
JOIN `{PROJECT}.bqx_ml_v3_features.{table_name}` f ON t.interval_time = f.interval_time
WHERE f.{feature} IS NOT NULL"""
        union_parts.append(sql)

    return "\nUNION ALL\n".join(union_parts)


def run_query_from_file(sql: str) -> list:
    """Execute SQL from a temp file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql)
        sql_file = f.name

    try:
        cmd = ["bq", "--location", LOCATION, "query", "--use_legacy_sql=false", "--format=json", f"$(cat {sql_file})"]
        # Use shell to expand the file
        result = subprocess.run(
            f"bq --location={LOCATION} query --use_legacy_sql=false --format=json < {sql_file}",
            shell=True, capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            print(f"Query error: {result.stderr[:200]}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []
    finally:
        os.unlink(sql_file)


def main():
    total_features = sum(len(f) for f in FEATURE_TABLES.values())
    print(f"Processing {total_features} features across {len(FEATURE_TABLES)} tables")
    print("-" * 60)

    all_results = []

    for table_name, features in FEATURE_TABLES.items():
        print(f"Processing {table_name} ({len(features)} features)...", end=" ", flush=True)

        sql = generate_correlation_sql(table_name, features)
        results = run_query_from_file(sql)

        if results:
            all_results.extend(results)
            print(f"OK ({len(results)} results)")
        else:
            print("FAILED")

    # Save results
    output_file = "/tmp/all_extreme_correlations.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("-" * 60)
    print(f"Total results: {len(all_results)}")
    print(f"Saved to: {output_file}")

    # Calculate max absolute correlation for ranking
    if all_results:
        for r in all_results:
            corr_cols = [k for k in r.keys() if k.startswith('corr_w') and r[k] is not None]
            if corr_cols:
                r['max_abs_corr'] = max(abs(float(r[k])) for k in corr_cols)
            else:
                r['max_abs_corr'] = 0

        sorted_results = sorted(all_results, key=lambda x: x.get('max_abs_corr', 0), reverse=True)

        print("\nTop 30 Features by Max Absolute Correlation:")
        print("-" * 80)
        for i, r in enumerate(sorted_results[:30]):
            print(f"{i+1:3}. {r['feature_id']:40} max={r['max_abs_corr']:.4f}")


if __name__ == "__main__":
    main()
