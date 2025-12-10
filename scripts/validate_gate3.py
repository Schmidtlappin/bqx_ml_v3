#!/usr/bin/env python3
"""
GATE_3 Validation Script (v2)
Reusable validation for EURUSD horizons and future pairs.

Updated 2025-12-10:
- Accept model path as parameter
- Dynamic feature count validation (200-600 expected)
- Support for v3 model naming

Usage:
    python validate_gate3.py --pair eurusd --horizon 15
    python validate_gate3.py --pair eurusd --horizon 15 --model-version v3
    python validate_gate3.py --pair eurusd --horizon 15 --model-path models/eurusd/h15_custom.joblib
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

# Feature count expectations (after stability selection)
MIN_FEATURES_EXPECTED = 200
MAX_FEATURES_EXPECTED = 600
FEATURE_UNIVERSE_TOTAL = 11337  # Total columns per pair
FEATURE_UNIVERSE_UNIQUE = 1064  # Unique features per pair

def check_gcs_artifact(pair: str, horizon: int, model_version: str = None, model_path: str = None) -> dict:
    """Check GCS model artifact exists and has expected size."""
    if model_path:
        # Custom model path provided
        gcs_path = model_path if model_path.startswith("gs://") else f"gs://bqx-ml-v3-models/{model_path}"
    elif model_version:
        # Versioned model (v2, v3, etc.)
        gcs_path = f"gs://bqx-ml-v3-models/models/{pair}/h{horizon}_ensemble_{model_version}.joblib"
    else:
        # Default (legacy)
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

def check_shap_file(pair: str, horizon: int, model_version: str = None) -> dict:
    """Check SHAP JSON for sample count and model coverage."""
    # Try versioned filename first, then default
    if model_version:
        file_path = Path(f"intelligence/shap_{pair}_h{horizon}_{model_version}.json")
        if not file_path.exists():
            file_path = Path(f"intelligence/shap_{pair}_h{horizon}.json")
    else:
        file_path = Path(f"intelligence/shap_{pair}_h{horizon}.json")

    if not file_path.exists():
        return {"exists": False, "pass": False, "file": str(file_path)}

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

    # Validate feature count is within expected range (after stability selection)
    feature_count_valid = MIN_FEATURES_EXPECTED <= feature_count <= MAX_FEATURES_EXPECTED
    feature_count_note = "within expected range" if feature_count_valid else f"outside {MIN_FEATURES_EXPECTED}-{MAX_FEATURES_EXPECTED} range"

    # For legacy 59-feature model, note it's obsolete
    if feature_count == 59:
        feature_count_note = "OBSOLETE (59-feature model - will be replaced)"
        feature_count_valid = True  # Don't fail on legacy, just note

    return {
        "exists": True,
        "file": str(file_path),
        "sample_size": sample_size,
        "mandate_compliant": mandate_compliant,
        "feature_count": feature_count,
        "feature_count_valid": feature_count_valid,
        "feature_count_note": feature_count_note,
        "models": {
            "lightgbm": has_lgb,
            "xgboost": has_xgb,
            "catboost": has_cb
        },
        "pass": sample_size >= MIN_SHAP_SAMPLES and has_lgb and has_xgb and has_cb
    }

def validate_gate3(pair: str, horizon: int, model_version: str = None, model_path: str = None) -> dict:
    """
    Full GATE_3 validation for a pair-horizon combination.

    Args:
        pair: Currency pair (e.g., 'eurusd')
        horizon: Prediction horizon (e.g., 15, 30, 45)
        model_version: Optional version suffix (e.g., 'v3')
        model_path: Optional custom model path

    Returns dict with overall pass/fail and detailed results.
    """
    results = {
        "pair": pair,
        "horizon": horizon,
        "model_version": model_version or "default",
        "feature_universe": {
            "total_columns": FEATURE_UNIVERSE_TOTAL,
            "unique_features": FEATURE_UNIVERSE_UNIQUE,
            "expected_selected": f"{MIN_FEATURES_EXPECTED}-{MAX_FEATURES_EXPECTED}"
        },
        "checks": {}
    }

    # 1. Check GCS artifact
    results["checks"]["gcs_artifact"] = check_gcs_artifact(pair, horizon, model_version, model_path)

    # 2. Check calibration metrics
    results["checks"]["calibration"] = check_calibration_file(pair, horizon)

    # 3. Check SHAP compliance
    results["checks"]["shap"] = check_shap_file(pair, horizon, model_version)

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
    parser = argparse.ArgumentParser(description="GATE_3 Validation Script (v2)")
    parser.add_argument("--pair", default="eurusd", help="Currency pair")
    parser.add_argument("--horizon", type=int, default=15, help="Horizon (15, 30, 45, etc.)")
    parser.add_argument("--model-version", dest="model_version", help="Model version (e.g., v3)")
    parser.add_argument("--model-path", dest="model_path", help="Custom model path (local or GCS)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = validate_gate3(args.pair, args.horizon, args.model_version, args.model_path)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    # Exit code: 0 for pass, 1 for fail
    return 0 if results["gate3_pass"] else 1

if __name__ == "__main__":
    exit(main())
