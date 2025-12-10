#!/usr/bin/env python3
"""
Coverage Validation Script for GATE_3
Validates that coverage is within 30-50% target range.

Created: 2025-12-10
Purpose: Verify coverage metric meets GATE_3 requirements

Usage:
    python validate_coverage.py --pair eurusd --horizon 15
    python validate_coverage.py --calibration-file intelligence/calibrated_stack_eurusd_h15.json
"""

import json
import argparse
from pathlib import Path

# GATE_3 Coverage Targets (from USER MANDATE)
MIN_COVERAGE = 0.30  # 30%
MAX_COVERAGE = 0.50  # 50%
MIN_ACCURACY = 0.85  # 85%

# Thresholds to evaluate
THRESHOLDS = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]


def load_calibration_data(file_path: Path) -> dict:
    """Load calibration JSON file."""
    if not file_path.exists():
        return None
    with open(file_path) as f:
        return json.load(f)


def find_optimal_threshold(gating_results: dict) -> dict:
    """
    Find optimal threshold balancing accuracy and coverage.

    Returns threshold that:
    1. Achieves ≥85% accuracy
    2. Maintains 30-50% coverage
    """
    optimal = None
    best_coverage = 0

    for tau_key, metrics in gating_results.items():
        accuracy = metrics.get("accuracy", 0)
        coverage = metrics.get("coverage", 0)

        # Check if meets minimum accuracy
        if accuracy >= MIN_ACCURACY:
            # Check if coverage is within target range
            if MIN_COVERAGE <= coverage <= MAX_COVERAGE:
                if coverage > best_coverage:
                    best_coverage = coverage
                    optimal = {
                        "threshold": tau_key,
                        "accuracy": accuracy,
                        "coverage": coverage,
                        "meets_accuracy": True,
                        "meets_coverage": True
                    }

    return optimal


def analyze_coverage(calibration_data: dict) -> dict:
    """
    Comprehensive coverage analysis for GATE_3 validation.
    """
    results = {
        "overall_metrics": {},
        "threshold_analysis": [],
        "optimal_threshold": None,
        "recommendation": None,
        "gate3_coverage_pass": False
    }

    # Extract overall metrics
    results["overall_metrics"] = {
        "overall_accuracy": calibration_data.get("overall_accuracy"),
        "overall_auc": calibration_data.get("overall_auc"),
        "oof_samples": calibration_data.get("oof_samples")
    }

    # Analyze each threshold
    gating = calibration_data.get("gating_results", {})
    for tau_key in sorted(gating.keys()):
        metrics = gating[tau_key]
        accuracy = metrics.get("accuracy", 0)
        coverage = metrics.get("coverage", 0)

        entry = {
            "threshold": tau_key,
            "accuracy": round(accuracy * 100, 2),
            "coverage": round(coverage * 100, 2),
            "accuracy_pass": accuracy >= MIN_ACCURACY,
            "coverage_pass": MIN_COVERAGE <= coverage <= MAX_COVERAGE,
            "gate3_pass": accuracy >= MIN_ACCURACY and MIN_COVERAGE <= coverage <= MAX_COVERAGE
        }
        results["threshold_analysis"].append(entry)

    # Find optimal threshold
    optimal = find_optimal_threshold(gating)
    if optimal:
        results["optimal_threshold"] = optimal
        results["gate3_coverage_pass"] = True
        results["recommendation"] = f"Use {optimal['threshold']}: {optimal['accuracy']*100:.1f}% accuracy, {optimal['coverage']*100:.1f}% coverage"
    else:
        # Find best available even if not in target range
        best = None
        for tau_key, metrics in gating.items():
            accuracy = metrics.get("accuracy", 0)
            coverage = metrics.get("coverage", 0)
            if accuracy >= MIN_ACCURACY:
                if best is None or coverage > best["coverage"]:
                    best = {"threshold": tau_key, "accuracy": accuracy, "coverage": coverage}

        if best:
            results["best_available"] = best
            if best["coverage"] < MIN_COVERAGE:
                results["recommendation"] = f"Coverage {best['coverage']*100:.1f}% below {MIN_COVERAGE*100}% target. May improve after full feature universe testing."
            elif best["coverage"] > MAX_COVERAGE:
                results["recommendation"] = f"Coverage {best['coverage']*100:.1f}% above {MAX_COVERAGE*100}% target. Consider higher threshold."
        else:
            results["recommendation"] = "No threshold achieves ≥85% accuracy. Model may need retraining."

    return results


def print_report(results: dict, pair: str, horizon: int):
    """Print formatted coverage report."""
    print("=" * 70)
    print(f"COVERAGE VALIDATION: {pair.upper()} h{horizon}")
    print("=" * 70)

    print(f"\nTarget Range: {MIN_COVERAGE*100:.0f}%-{MIN_ACCURACY*100:.0f}% coverage with ≥{MIN_ACCURACY*100:.0f}% accuracy")

    print("\nOverall Metrics:")
    for k, v in results["overall_metrics"].items():
        if v is not None:
            print(f"  {k}: {v}")

    print("\nThreshold Analysis:")
    print(f"  {'Threshold':<12} {'Accuracy':<12} {'Coverage':<12} {'GATE_3':<8}")
    print("  " + "-" * 44)
    for entry in results["threshold_analysis"]:
        status = "PASS" if entry["gate3_pass"] else "FAIL"
        print(f"  {entry['threshold']:<12} {entry['accuracy']:.1f}%{'':<6} {entry['coverage']:.1f}%{'':<6} {status:<8}")

    print("\n" + "-" * 70)
    if results["gate3_coverage_pass"]:
        opt = results["optimal_threshold"]
        print(f"OPTIMAL: {opt['threshold']} - {opt['accuracy']*100:.1f}% accuracy, {opt['coverage']*100:.1f}% coverage")
    else:
        print(f"RECOMMENDATION: {results.get('recommendation', 'N/A')}")

    print("\n" + "=" * 70)
    verdict = "PASS" if results["gate3_coverage_pass"] else "FAIL"
    print(f"COVERAGE VALIDATION: {verdict}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Coverage Validation for GATE_3")
    parser.add_argument("--pair", default="eurusd", help="Currency pair")
    parser.add_argument("--horizon", type=int, default=15, help="Horizon")
    parser.add_argument("--calibration-file", dest="calibration_file", help="Custom calibration file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Determine file path
    if args.calibration_file:
        file_path = Path(args.calibration_file)
    else:
        file_path = Path(f"intelligence/calibrated_stack_{args.pair}_h{args.horizon}.json")

    # Load and analyze
    data = load_calibration_data(file_path)
    if data is None:
        print(f"ERROR: File not found: {file_path}")
        return 1

    results = analyze_coverage(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results, args.pair, args.horizon)

    return 0 if results["gate3_coverage_pass"] else 1


if __name__ == "__main__":
    exit(main())
