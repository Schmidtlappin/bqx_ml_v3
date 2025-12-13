#!/usr/bin/env python3
"""
Polynomial Regression Feature Generator V5
BQX-ML-M005 MANDATE COMPLIANT: Coefficient + Term Data

CHANGES FROM V4:
- Added reg_lin_coef_{w} and reg_quad_coef_{w} columns (14 new columns)
- Updated to target bqx_ml_v3_features_v2 dataset
- Total columns: 248 (was 234)

USER MANDATE (BQX-ML-M005):
REG tables MUST have BOTH coefficient AND term data:
  - Coefficients: lin_coef, quad_coef, constant (raw β values)
  - Terms: lin_term, quad_term, residual (evaluated contributions)

Key formulas:
- β₂ (quad_coef) = (first - 2*mean + last) / ((N-1)²/2)
- β₁ (lin_coef) = (last - first)/(N-1) - β₂*(N-1)
- β₀ (constant) = first
- quad_term = β₂ × N²
- lin_term = β₁ × N
- const_term = β₀
- residual = y - (quad_term + lin_term + const_term)
"""

import subprocess
import sys
import argparse
from typing import List

PROJECT = "bqx-ml"
DATASET_V2 = "bqx_ml_v3_features_v2"
LOCATION = "us-central1"

PAIRS = [
    'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
    'eurgbp', 'eurjpy', 'eurchf', 'euraud', 'eurcad', 'eurnzd',
    'gbpjpy', 'gbpchf', 'gbpaud', 'gbpcad', 'gbpnzd',
    'audjpy', 'audchf', 'audcad', 'audnzd',
    'nzdjpy', 'nzdchf', 'nzdcad',
    'cadjpy', 'cadchf', 'chfjpy'
]

WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]


def generate_polynomial_sql_v5(pair: str, variant: str = "idx") -> str:
    """
    Generate SQL for polynomial regression features with BOTH coefficients and terms.
    BQX-ML-M005 MANDATE COMPLIANT.

    Uses two-stage CTE to avoid nested window functions:
      Stage 1: Basic window statistics (mean, std, min, max, first, var, sums)
      Stage 2: Calculate polynomial coefficients AND endpoint-scaled terms
    """
    if variant == "bqx":
        source_table = f"base_bqx_{pair}"
        output_table = f"reg_bqx_{pair}"
        source_col = "bqx_45"
    elif variant == "idx":
        source_table = f"base_idx_{pair}"
        output_table = f"reg_idx_{pair}"
        source_col = "close_idx"
    else:
        # For reg_* (other variant)
        source_table = f"{pair}_idx"  # Legacy table name
        output_table = f"reg_{pair}"
        source_col = "close_idx"

    # Stage 1: Basic window calculations
    stage1_cols = []
    for w in WINDOWS:
        stage1_cols.append(f"""
        -- Window {w}: Basic stats
        AVG(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS mean_{w},
        STDDEV(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS std_{w},
        MIN(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS min_{w},
        MAX(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS max_{w},
        FIRST_VALUE(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS first_{w},
        VAR_POP(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS total_var_{w},

        -- For slope calculation
        SUM(CAST(row_num AS FLOAT64) * source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS sum_xy_{w},
        SUM(CAST(row_num AS FLOAT64)) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS sum_x_{w},
        SUM(source_value) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS sum_y_{w},
        SUM(CAST(row_num AS FLOAT64) * CAST(row_num AS FLOAT64)) OVER (ORDER BY interval_time ROWS BETWEEN {w-1} PRECEDING AND CURRENT ROW) AS sum_xx_{w}""")

    stage1_sql = ",\n".join(stage1_cols)

    # Stage 2: Polynomial features with BOTH coefficients and terms
    stage2_cols = []
    for w in WINDOWS:
        N = w  # Window size

        # Calculate coefficient expressions (reusable)
        quad_coef_expr = f"SAFE_DIVIDE(first_{w} - 2.0 * mean_{w} + source_value, POWER({w-1}, 2) / 2.0)"
        lin_coef_expr = f"(SAFE_DIVIDE(source_value - first_{w}, {w-1}) - {quad_coef_expr} * ({w-1}))"

        stage2_cols.append(f"""
        -- Window {w}: Legacy features (10 columns)
        mean_{w} AS reg_mean_{w},
        std_{w} AS reg_std_{w},
        min_{w} AS reg_min_{w},
        max_{w} AS reg_max_{w},
        first_{w} AS reg_first_{w},

        -- Linear slope (backward compatible)
        SAFE_DIVIDE(
            {w} * sum_xy_{w} - sum_x_{w} * sum_y_{w},
            {w} * sum_xx_{w} - POWER(sum_x_{w}, 2)
        ) AS reg_slope_{w},

        -- Direction indicator
        SIGN(source_value - first_{w}) AS reg_direction_{w},

        -- Deviation from mean
        source_value - mean_{w} AS reg_deviation_{w},

        -- Z-score
        SAFE_DIVIDE(source_value - mean_{w}, NULLIF(std_{w}, 0)) AS reg_zscore_{w},

        -- Range percentage
        SAFE_DIVIDE(max_{w} - min_{w}, NULLIF(mean_{w}, 0)) * 100 AS reg_range_pct_{w},

        -- =====================================================
        -- BQX-ML-M005 MANDATE: COEFFICIENT COLUMNS (NEW)
        -- =====================================================

        -- quad_coef = β₂ (raw quadratic coefficient)
        {quad_coef_expr} AS reg_quad_coef_{w},

        -- lin_coef = β₁ (raw linear coefficient)
        {lin_coef_expr} AS reg_lin_coef_{w},

        -- =====================================================
        -- TERM COLUMNS (existing, now with coefficients above)
        -- =====================================================

        -- quad_term = β₂ × N² (quadratic contribution at endpoint)
        {quad_coef_expr} * POWER({N}, 2) AS reg_quad_term_{w},

        -- lin_term = β₁ × N (linear contribution at endpoint)
        {lin_coef_expr} * {N} AS reg_lin_term_{w},

        -- const_term = β₀
        first_{w} AS reg_const_term_{w},

        -- residual = rate - (quad_term + lin_term + const_term)
        source_value - (
            {quad_coef_expr} * POWER({N}, 2) +
            {lin_coef_expr} * {N} +
            first_{w}
        ) AS reg_residual_{w},

        -- Normalized quadratic coefficient
        SAFE_DIVIDE(
            {quad_coef_expr} * POWER({N}, 2) * POWER({w-1}, 2),
            NULLIF(mean_{w}, 0)
        ) AS reg_quad_norm_{w},

        -- Normalized linear coefficient
        SAFE_DIVIDE(
            {lin_coef_expr} * {N} * ({w-1}),
            NULLIF(mean_{w}, 0)
        ) AS reg_lin_norm_{w},

        -- Variance metrics
        total_var_{w} AS reg_total_var_{w},
        POWER(std_{w}, 2) AS reg_resid_var_{w},
        CASE WHEN total_var_{w} > 0 THEN
            1.0 - SAFE_DIVIDE(POWER(std_{w}, 2), total_var_{w})
        ELSE NULL END AS reg_r2_{w},
        std_{w} AS reg_rmse_{w},

        -- Normalized residual
        SAFE_DIVIDE(
            source_value - (
                {quad_coef_expr} * POWER({N}, 2) +
                {lin_coef_expr} * {N} +
                first_{w}
            ),
            NULLIF(mean_{w}, 0)
        ) AS reg_resid_norm_{w},

        -- Residual metrics
        std_{w} AS reg_resid_std_{w},
        min_{w} - mean_{w} AS reg_resid_min_{w},
        max_{w} - mean_{w} AS reg_resid_max_{w},
        source_value - mean_{w} AS reg_resid_last_{w},

        -- Residual skewness approximation
        SIGN(source_value - mean_{w}) * POWER(ABS(source_value - mean_{w}) / NULLIF(std_{w}, 0), 3) AS reg_resid_skew_{w},

        -- Residual kurtosis approximation
        POWER(ABS(source_value - mean_{w}) / NULLIF(std_{w}, 0), 4) - 3.0 AS reg_resid_kurt_{w},

        -- Curvature sign
        CAST(SIGN({quad_coef_expr}) AS INT64) AS reg_curv_sign_{w},

        -- Acceleration (2 * β₂)
        2.0 * {quad_coef_expr} AS reg_acceleration_{w},

        -- Trend strength (lin_term / resid_std)
        SAFE_DIVIDE(
            {lin_coef_expr} * {N},
            NULLIF(std_{w}, 0)
        ) AS reg_trend_str_{w},

        -- 5-step forecast (extrapolate polynomial)
        (
            {quad_coef_expr} * (POWER({N} + 5, 2) - POWER({N}, 2)) +
            {lin_coef_expr} * 5
        ) AS reg_forecast_5_{w},

        -- Confidence interval lower
        source_value - 1.96 * SAFE_DIVIDE(std_{w}, SQRT({w})) AS reg_ci_lower_{w},

        -- Confidence interval upper
        source_value + 1.96 * SAFE_DIVIDE(std_{w}, SQRT({w})) AS reg_ci_upper_{w}""")

    stage2_sql = ",\n".join(stage2_cols)

    sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET_V2}.{output_table}`
PARTITION BY DATE(interval_time)
CLUSTER BY pair
AS
WITH numbered AS (
    SELECT
        interval_time,
        pair,
        {source_col} AS source_value,
        ROW_NUMBER() OVER (ORDER BY interval_time) AS row_num
    FROM `{PROJECT}.{DATASET_V2}.{source_table}`
),
stage1 AS (
    SELECT
        interval_time,
        pair,
        source_value,
        row_num,
        {stage1_sql}
    FROM numbered
)
SELECT
    interval_time,
    pair,
    source_value,
    {stage2_sql}
FROM stage1
"""
    return sql


def execute_bq(sql: str, table_name: str, dry_run: bool = False) -> bool:
    """Execute BigQuery SQL via stdin."""
    if dry_run:
        print(f"DRY-RUN: {table_name}")
        return True

    cmd = [
        "bq", "--location", LOCATION, "query",
        "--use_legacy_sql=false",
        "--max_rows=0"
    ]

    try:
        result = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=900)
        if result.returncode == 0:
            print(f"✅ OK: {table_name}")
            return True
        else:
            print(f"❌ FAILED: {table_name}")
            err_msg = result.stderr or result.stdout
            print(f"  Error: {err_msg[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT: {table_name}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {table_name} - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate REG tables with coefficient + term data (BQX-ML-M005 compliant)"
    )
    parser.add_argument(
        "variant",
        choices=["idx", "bqx", "other"],
        help="Table variant: idx (reg_idx_*), bqx (reg_bqx_*), or other (reg_*)"
    )
    parser.add_argument(
        "--pairs",
        nargs="+",
        default=None,
        help="Specific pairs to process (default: all 28)"
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Test on first 3 pairs only (eurusd, gbpusd, usdjpy)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print table names without executing"
    )

    args = parser.parse_args()

    # Determine pairs to process
    if args.test_only:
        pairs_to_run = ['eurusd', 'gbpusd', 'usdjpy']
    elif args.pairs:
        pairs_to_run = [p.lower() for p in args.pairs]
    else:
        pairs_to_run = PAIRS

    # Validate pairs
    invalid = [p for p in pairs_to_run if p not in PAIRS]
    if invalid:
        print(f"❌ ERROR: Invalid pairs: {invalid}")
        sys.exit(1)

    print("=" * 70)
    print("REG Table Generator V5 - BQX-ML-M005 MANDATE COMPLIANT")
    print("=" * 70)
    print(f"Variant:     {args.variant.upper()}")
    print(f"Dataset:     {DATASET_V2}")
    print(f"Pairs:       {len(pairs_to_run)}")
    print(f"Test mode:   {args.test_only}")
    print(f"Dry run:     {args.dry_run}")
    print()
    print("NEW COLUMNS (14 per table):")
    print("  - reg_lin_coef_45, reg_lin_coef_90, ..., reg_lin_coef_2880 (7)")
    print("  - reg_quad_coef_45, reg_quad_coef_90, ..., reg_quad_coef_2880 (7)")
    print()
    print("Total columns: 248 (was 234)")
    print("=" * 70)

    success, failed = 0, 0

    for pair in pairs_to_run:
        if args.variant == "bqx":
            table_name = f"reg_bqx_{pair}"
        elif args.variant == "idx":
            table_name = f"reg_idx_{pair}"
        else:  # other
            table_name = f"reg_{pair}"

        print(f"Creating {table_name}...", end=" ", flush=True)

        sql = generate_polynomial_sql_v5(pair, args.variant)
        if execute_bq(sql, table_name, args.dry_run):
            success += 1
        else:
            failed += 1

    print("=" * 70)
    print(f"Success: {success}, Failed: {failed}")
    if failed > 0:
        print(f"⚠️ WARNING: {failed} tables failed to generate")
        sys.exit(1)


if __name__ == "__main__":
    main()
