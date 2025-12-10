#!/usr/bin/env python3
"""
GATE_3 Validation Script
Reusable validation for EURUSD horizons and future pairs.

Usage:
    python validate_gate3.py --pair eurusd --horizon 15
    python validate_gate3.py --pair eurusd --horizon 30
"""

import json
import argparse
import subprocess
from pathlib import Path

# Thresholds (from USER MANDATES)
MIN_ACCURACY = 0.85  # 85%
MIN_COVERAGE = 0.30  # 30%
MAX_COVERAGE = 0.50  # 50%
MIN_SHAP_SAMPLES = 100000  # USER MANDATE

def check_gcs_artifact(pair: str, horizon: int) -> dict:
    """Check GCS model artifact exists and has expected size."""
    gcs_path = f"gs://bqx-ml-v3-models/models/{pair}/h{horizon}_ensemble.joblib"
    try:
        result = subprocess.run(
            ["gsutil", "ls", "-l", gcs_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            # Parse size from output
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'joblib' in line:
                    parts = line.split()
                    size_bytes = int(parts[0]) if parts[0].isdigit() else 0
                    return {
                        "exists": True,
                        "size_mb": round(size_bytes / 1024 / 1024, 2),
                        "path": gcs_path,
                        "pass": size_bytes > 1000000  # > 1MB
                    }
        return {"exists": False, "pass": False, "path": gcs_path}
    except Exception as e:
        return {"exists": False, "pass": False, "error": str(e)}

def check_calibration_file(pair: str, horizon: int) -> dict:
    """Check calibration JSON for accuracy and coverage."""
    file_path = Path(f"intelligence/calibrated_stack_{pair}_h{horizon}.json")
    if not file_path.exists():
        return {"exists": False, "pass": False}

    with open(file_path) as f:
        data = json.load(f)

    # Get tau_85 metrics (default threshold)
    gating = data.get("gating_results", {})
    tau_85 = gating.get("tau_85", {})

    accuracy = tau_85.get("accuracy", 0)
    coverage = tau_85.get("coverage", 0)

    return {
        "exists": True,
        "accuracy": accuracy,
        "coverage": coverage,
        "accuracy_pass": accuracy >= MIN_ACCURACY,
        "coverage_pass": MIN_COVERAGE <= coverage <= MAX_COVERAGE,
        "pass": accuracy >= MIN_ACCURACY and MIN_COVERAGE <= coverage <= MAX_COVERAGE
    }

def check_shap_file(pair: str, horizon: int) -> dict:
    """Check SHAP JSON for sample count and model coverage."""
    file_path = Path(f"intelligence/shap_{pair}_h{horizon}.json")
    if not file_path.exists():
        return {"exists": False, "pass": False}

    with open(file_path) as f:
        data = json.load(f)

    sample_size = data.get("shap_sample_size", 0)
    mandate_compliant = data.get("mandate_compliant", False)
    feature_count = data.get("feature_count", 0)

    # Check all 3 models have SHAP
    all_features = data.get("all_features", [])
    has_lgb = has_xgb = has_cb = False
    if all_features:
        first = all_features[0]
        has_lgb = "lgb_shap" in first
        has_xgb = "xgb_shap" in first
        has_cb = "cb_shap" in first

    return {
        "exists": True,
        "sample_size": sample_size,
        "mandate_compliant": mandate_compliant,
        "feature_count": feature_count,
        "models": {
            "lightgbm": has_lgb,
            "xgboost": has_xgb,
            "catboost": has_cb
        },
        "pass": sample_size >= MIN_SHAP_SAMPLES and has_lgb and has_xgb and has_cb
    }

def validate_gate3(pair: str, horizon: int) -> dict:
    """
    Full GATE_3 validation for a pair-horizon combination.

    Returns dict with overall pass/fail and detailed results.
    """
    results = {
        "pair": pair,
        "horizon": horizon,
        "checks": {}
    }

    # 1. Check GCS artifact
    results["checks"]["gcs_artifact"] = check_gcs_artifact(pair, horizon)

    # 2. Check calibration metrics
    results["checks"]["calibration"] = check_calibration_file(pair, horizon)

    # 3. Check SHAP compliance
    results["checks"]["shap"] = check_shap_file(pair, horizon)

    # Overall verdict
    all_pass = all(
        results["checks"][k].get("pass", False)
        for k in results["checks"]
    )
    results["gate3_pass"] = all_pass
    results["verdict"] = "PASS" if all_pass else "FAIL"

    return results

def print_report(results: dict):
    """Print formatted validation report."""
    print("=" * 60)
    print(f"GATE_3 VALIDATION: {results['pair'].upper()} h{results['horizon']}")
    print("=" * 60)

    for check_name, check_data in results["checks"].items():
        status = "PASS" if check_data.get("pass") else "FAIL"
        print(f"\n{check_name.upper()}: {status}")
        for k, v in check_data.items():
            if k != "pass":
                print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print(f"GATE_3 VERDICT: {results['verdict']}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="GATE_3 Validation Script")
    parser.add_argument("--pair", default="eurusd", help="Currency pair")
    parser.add_argument("--horizon", type=int, default=15, help="Horizon (15, 30, 45, etc.)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = validate_gate3(args.pair, args.horizon)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    # Exit code: 0 for pass, 1 for fail
    return 0 if results["gate3_pass"] else 1

if __name__ == "__main__":
    exit(main())
