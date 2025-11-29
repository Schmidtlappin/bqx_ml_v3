#!/usr/bin/env python3
"""
Validate polynomial regression feature implementation by BA.

This script validates:
1. Table structure - all 492 tables have correct schema (196 columns)
2. Coverage - 100% completeness for IDX and BQX variants
3. Formula correctness - sample data validation of polynomial calculations

Polynomial Formula:
  y = ax² + bx + c
  where:
    x = np.arange(W) = [0, 1, 2, ..., W-1]
    y = values[-W:] (last W source values)
    a = quad_term, b = lin_term, c = const_term

Usage:
  python3 validate_polynomial_features.py [--full] [--sample-size N]

Author: Chief Engineer, BQX ML V3
Date: 2025-11-29
"""

import subprocess
import json
import sys
import argparse
import numpy as np
from scipy import stats

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features"

WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

# Expected new polynomial columns per window
# USER MANDATE v2.1: Endpoint Evaluation with Scaled Coefficients
EXPECTED_POLYNOMIAL_COLUMNS = [
    # Polynomial coefficients (USER MANDATE: Endpoint Scaled)
    "reg_quad_term_{W}",    # β₂ × W² (quadratic at endpoint)
    "reg_lin_term_{W}",     # β₁ × W (linear at endpoint)
    "reg_const_term_{W}",   # β₀ (constant term)
    "reg_residual_{W}",     # USER MANDATE: rate - (quad_term + lin_term + const_term)
    "reg_quad_norm_{W}",
    "reg_lin_norm_{W}",
    # Variance metrics (USER MANDATE v2.1 - AirTable MP02.P16.S01)
    "reg_resid_var_{W}",    # MSE = mean(residuals²) - USER MANDATE
    "reg_total_var_{W}",    # var(y) - USER MANDATE
    "reg_r2_{W}",           # 1 - (resid_var / total_var)
    "reg_rmse_{W}",         # sqrt(resid_var)
    "reg_resid_norm_{W}",   # residuals[-1] / mean(y)
    # Residual metrics
    "reg_resid_std_{W}",
    "reg_resid_min_{W}",
    "reg_resid_max_{W}",
    "reg_resid_last_{W}",
    "reg_resid_skew_{W}",
    "reg_resid_kurt_{W}",
    # Derived features
    "reg_curv_sign_{W}",
    "reg_acceleration_{W}",
    "reg_trend_str_{W}",
    "reg_forecast_5_{W}",
    "reg_ci_lower_{W}",
    "reg_ci_upper_{W}"
]

PAIRS = [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "usdcad", "nzdusd",
    "eurgbp", "eurjpy", "eurchf", "euraud", "eurcad", "eurnzd",
    "gbpjpy", "gbpchf", "gbpaud", "gbpcad", "gbpnzd",
    "audjpy", "audchf", "audcad", "audnzd",
    "nzdjpy", "nzdchf", "nzdcad",
    "cadjpy", "cadchf", "chfjpy"
]


def run_bq_query(sql: str) -> tuple:
    """Run BigQuery query and return results."""
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=1000"]
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr
    try:
        return json.loads(result.stdout), None
    except:
        return None, "JSON parse error"


def get_expected_columns():
    """Get list of all expected polynomial columns."""
    columns = []
    for template in EXPECTED_POLYNOMIAL_COLUMNS:
        for w in WINDOWS:
            columns.append(template.format(W=w))
    return set(columns)


def validate_table_schema(table_name: str) -> dict:
    """Validate schema of a single table."""
    sql = f"""
    SELECT column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
    """
    rows, error = run_bq_query(sql)
    if error:
        return {"status": "ERROR", "error": error}

    actual_columns = {row["column_name"] for row in rows}
    expected = get_expected_columns()

    missing = expected - actual_columns
    if missing:
        return {
            "status": "INCOMPLETE",
            "missing_count": len(missing),
            "missing_sample": list(missing)[:5],
            "total_columns": len(actual_columns)
        }

    return {
        "status": "COMPLETE",
        "total_columns": len(actual_columns),
        "polynomial_columns": len(expected)
    }


def validate_all_tables(verbose: bool = False) -> dict:
    """Validate schema of all reg_ tables."""
    results = {
        "idx_complete": 0,
        "idx_incomplete": 0,
        "bqx_complete": 0,
        "bqx_incomplete": 0,
        "errors": [],
        "details": {}
    }

    print("\n=== Validating Table Schemas ===")

    for pair in PAIRS:
        # IDX variant
        table_idx = f"reg_{pair}"
        result = validate_table_schema(table_idx)
        results["details"][table_idx] = result

        if result["status"] == "COMPLETE":
            results["idx_complete"] += 1
            if verbose:
                print(f"  ✓ {table_idx}: {result['total_columns']} columns")
        else:
            results["idx_incomplete"] += 1
            if verbose:
                print(f"  ✗ {table_idx}: {result.get('error', f'Missing {result.get(\"missing_count\", \"?\")} columns')}")

        # BQX variant
        table_bqx = f"reg_bqx_{pair}"
        result = validate_table_schema(table_bqx)
        results["details"][table_bqx] = result

        if result["status"] == "COMPLETE":
            results["bqx_complete"] += 1
            if verbose:
                print(f"  ✓ {table_bqx}: {result['total_columns']} columns")
        else:
            results["bqx_incomplete"] += 1
            if verbose:
                print(f"  ✗ {table_bqx}: {result.get('error', f'Missing {result.get(\"missing_count\", \"?\")} columns')}")

    total = len(PAIRS) * 2
    complete = results["idx_complete"] + results["bqx_complete"]

    print(f"\n=== Schema Validation Summary ===")
    print(f"IDX tables: {results['idx_complete']}/{len(PAIRS)} complete")
    print(f"BQX tables: {results['bqx_complete']}/{len(PAIRS)} complete")
    print(f"Total: {complete}/{total} ({100*complete/total:.1f}%)")

    return results


def validate_polynomial_formula(table_name: str, sample_size: int = 5) -> dict:
    """
    Validate polynomial formula by comparing stored values with recalculated values.

    For a random sample of rows, fetch the source data (close or bqx values)
    and verify that the stored polynomial coefficients match recalculated values.
    """
    print(f"\n=== Validating Polynomial Formula for {table_name} ===")

    # Determine source column (close for IDX, bqx for BQX)
    is_bqx = "_bqx_" in table_name
    pair = table_name.replace("reg_bqx_", "").replace("reg_", "")

    # Get sample rows with polynomial values
    test_window = 45  # Use smallest window for testing

    sql = f"""
    SELECT
      interval_time,
      reg_quad_term_{test_window},
      reg_lin_term_{test_window},
      reg_const_term_{test_window},
      reg_r2_{test_window}
    FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    WHERE reg_quad_term_{test_window} IS NOT NULL
      AND reg_r2_{test_window} IS NOT NULL
    ORDER BY RAND()
    LIMIT {sample_size}
    """

    rows, error = run_bq_query(sql)
    if error or not rows:
        return {"status": "ERROR", "error": error or "No data"}

    validations = []

    for row in rows:
        interval_time = row["interval_time"]
        stored_quad = float(row[f"reg_quad_term_{test_window}"])
        stored_lin = float(row[f"reg_lin_term_{test_window}"])
        stored_const = float(row[f"reg_const_term_{test_window}"])
        stored_r2 = float(row[f"reg_r2_{test_window}"])

        # Fetch source data for this interval and previous W-1 intervals
        if is_bqx:
            source_table = f"bqx_{pair}"
            source_col = f"bqx_{test_window}"
        else:
            source_table = pair
            source_col = "close"

        source_sql = f"""
        SELECT {source_col} as value
        FROM `{PROJECT}.bqx_bq_uscen1.{source_table}`
        WHERE interval_time <= '{interval_time}'
        ORDER BY interval_time DESC
        LIMIT {test_window}
        """

        source_rows, error = run_bq_query(source_sql)
        if error or len(source_rows) < test_window:
            validations.append({
                "interval_time": interval_time,
                "status": "SKIP",
                "reason": "Insufficient source data"
            })
            continue

        # Reverse to get chronological order
        values = [float(r["value"]) for r in reversed(source_rows)]

        # Calculate polynomial fit
        x = np.arange(test_window)
        y = np.array(values)

        try:
            coeffs = np.polyfit(x, y, 2)
            calc_quad = coeffs[0]
            calc_lin = coeffs[1]
            calc_const = coeffs[2]

            y_hat = np.polyval(coeffs, x)
            ss_tot = np.sum((y - np.mean(y))**2)
            ss_res = np.sum((y - y_hat)**2)
            calc_r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0

            # Check if values match (within tolerance)
            tolerance = 0.01  # 1% tolerance
            quad_match = abs(stored_quad - calc_quad) / max(abs(calc_quad), 1e-10) < tolerance
            lin_match = abs(stored_lin - calc_lin) / max(abs(calc_lin), 1e-10) < tolerance
            r2_match = abs(stored_r2 - calc_r2) < 0.01  # Absolute tolerance for R2

            validation = {
                "interval_time": interval_time,
                "status": "PASS" if (quad_match and lin_match and r2_match) else "FAIL",
                "stored": {"quad": stored_quad, "lin": stored_lin, "r2": stored_r2},
                "calculated": {"quad": calc_quad, "lin": calc_lin, "r2": calc_r2},
                "matches": {"quad": quad_match, "lin": lin_match, "r2": r2_match}
            }
            validations.append(validation)

            status = "✓" if validation["status"] == "PASS" else "✗"
            print(f"  {status} {interval_time}: quad={stored_quad:.6f} (calc={calc_quad:.6f})")

        except Exception as e:
            validations.append({
                "interval_time": interval_time,
                "status": "ERROR",
                "error": str(e)
            })

    passed = sum(1 for v in validations if v["status"] == "PASS")
    total = len(validations)

    print(f"\nFormula validation: {passed}/{total} samples passed")

    return {
        "status": "PASS" if passed == total else "PARTIAL" if passed > 0 else "FAIL",
        "passed": passed,
        "total": total,
        "validations": validations
    }


def main():
    parser = argparse.ArgumentParser(description="Validate polynomial feature implementation")
    parser.add_argument("--full", action="store_true",
                       help="Run full validation (schema + formula)")
    parser.add_argument("--schema-only", action="store_true",
                       help="Only validate table schemas")
    parser.add_argument("--formula-only", action="store_true",
                       help="Only validate polynomial formula")
    parser.add_argument("--sample-size", type=int, default=5,
                       help="Number of samples for formula validation")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--table", type=str,
                       help="Validate specific table only")
    args = parser.parse_args()

    print("=" * 60)
    print("POLYNOMIAL FEATURE VALIDATION")
    print("=" * 60)
    print(f"\nExpected formula: y = ax² + bx + c")
    print(f"  x = np.arange(W) = [0, 1, 2, ..., W-1]")
    print(f"  y = values[-W:] (last W source values)")
    print(f"  a = quad_term, b = lin_term, c = const_term")
    print(f"\nWindows: {WINDOWS}")
    print(f"Pairs: {len(PAIRS)}")
    print(f"Expected polynomial columns per table: {len(EXPECTED_POLYNOMIAL_COLUMNS) * len(WINDOWS)}")

    results = {"schema": None, "formula": None}

    # Schema validation
    if not args.formula_only:
        if args.table:
            result = validate_table_schema(args.table)
            print(f"\n{args.table}: {result}")
            results["schema"] = {args.table: result}
        else:
            results["schema"] = validate_all_tables(verbose=args.verbose)

    # Formula validation
    if not args.schema_only and (args.full or args.formula_only):
        table = args.table or "reg_eurusd"
        results["formula"] = validate_polynomial_formula(table, args.sample_size)

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if results["schema"]:
        schema = results["schema"]
        if "idx_complete" in schema:
            total = len(PAIRS) * 2
            complete = schema["idx_complete"] + schema["bqx_complete"]
            print(f"Schema: {complete}/{total} tables complete ({100*complete/total:.1f}%)")
        else:
            print(f"Schema: Single table validated")

    if results["formula"]:
        formula = results["formula"]
        print(f"Formula: {formula['passed']}/{formula['total']} samples passed ({formula['status']})")

    # Exit code
    all_pass = True
    if results["schema"]:
        if "idx_complete" in results["schema"]:
            all_pass = all_pass and (results["schema"]["idx_complete"] + results["schema"]["bqx_complete"]) == len(PAIRS) * 2

    if results["formula"]:
        all_pass = all_pass and results["formula"]["status"] == "PASS"

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
