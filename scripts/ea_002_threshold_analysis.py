#!/usr/bin/env python3
"""
EA-002: Extended Confidence Threshold Analysis

Analyzes existing gating results and extrapolates/estimates
performance at higher thresholds (τ=0.75, τ=0.80).

For accurate validation, this script can also re-run the
gating calculation on cached OOF predictions if available.
"""

import json
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')


def load_existing_results(pair: str = "eurusd", horizon: int = 15) -> dict:
    """Load existing calibrated stack results."""
    path = f"/home/micha/bqx_ml_v3/intelligence/calibrated_stack_{pair}_h{horizon}.json"
    with open(path) as f:
        return json.load(f)


def extract_gating_curve(results: dict) -> tuple:
    """Extract threshold, accuracy, coverage arrays from results."""
    gating = results.get('gating_results', {})

    thresholds = []
    accuracies = []
    coverages = []
    n_signals = []

    for key in sorted(gating.keys()):
        tau = int(key.replace('tau_', '')) / 100
        thresholds.append(tau)
        accuracies.append(gating[key]['accuracy'])
        coverages.append(gating[key]['coverage'])
        n_signals.append(gating[key]['n_signals'])

    return (np.array(thresholds), np.array(accuracies),
            np.array(coverages), np.array(n_signals))


def fit_accuracy_model(thresholds: np.ndarray, accuracies: np.ndarray) -> callable:
    """
    Fit a model to predict accuracy at higher thresholds.
    Uses quadratic fit based on observed pattern.
    """
    # Quadratic fit: acc = a*tau^2 + b*tau + c
    coeffs = np.polyfit(thresholds, accuracies, 2)
    return np.poly1d(coeffs)


def fit_coverage_model(thresholds: np.ndarray, coverages: np.ndarray) -> callable:
    """
    Fit a model to predict coverage at higher thresholds.
    Coverage typically decreases more steeply at higher thresholds.
    """
    # Log-linear fit works well for coverage decay
    log_cov = np.log(coverages)
    coeffs = np.polyfit(thresholds, log_cov, 2)
    poly = np.poly1d(coeffs)
    return lambda x: np.exp(poly(x))


def estimate_extended_thresholds(results: dict) -> dict:
    """
    Estimate accuracy and coverage for extended thresholds.
    """
    thresholds, accuracies, coverages, n_signals = extract_gating_curve(results)
    total_samples = results.get('oof_samples', n_signals[0] / coverages[0])

    # Fit models
    acc_model = fit_accuracy_model(thresholds, accuracies)
    cov_model = fit_coverage_model(thresholds, coverages)

    # Extended thresholds to test
    extended_taus = np.arange(0.55, 0.86, 0.05)

    estimates = {}
    for tau in extended_taus:
        tau_key = f"tau_{int(tau*100)}"

        if tau in thresholds:
            # Use actual data
            idx = list(thresholds).index(tau)
            estimates[tau_key] = {
                'threshold': float(tau),
                'accuracy': float(accuracies[idx]),
                'coverage': float(coverages[idx]),
                'n_signals': int(n_signals[idx]),
                'source': 'ACTUAL'
            }
        else:
            # Estimate
            est_acc = float(min(acc_model(tau), 0.99))  # Cap at 99%
            est_cov = float(max(cov_model(tau), 0.05))  # Floor at 5%
            est_n = int(est_cov * total_samples)

            estimates[tau_key] = {
                'threshold': float(tau),
                'accuracy': est_acc,
                'coverage': est_cov,
                'n_signals': est_n,
                'source': 'ESTIMATED'
            }

    return estimates


def find_optimal_threshold(estimates: dict, min_accuracy: float = 0.85,
                          max_coverage: float = 0.50) -> dict:
    """
    Find optimal threshold meeting accuracy and coverage constraints.

    Target: ≥85% accuracy with reasonable coverage (30-50%)
    """
    candidates = []

    for key, data in estimates.items():
        if data['accuracy'] >= min_accuracy:
            candidates.append({
                'threshold': data['threshold'],
                'accuracy': data['accuracy'],
                'coverage': data['coverage'],
                'n_signals': data['n_signals'],
                'source': data['source'],
                'score': data['accuracy'] * data['coverage']  # Balance metric
            })

    if not candidates:
        # If no candidates meet min_accuracy, find closest
        best = max(estimates.values(), key=lambda x: x['accuracy'])
        return {
            'found': False,
            'closest': best,
            'message': f"No threshold achieves {min_accuracy:.0%} accuracy. Best: {best['accuracy']:.2%}"
        }

    # Sort by accuracy first, then coverage
    candidates.sort(key=lambda x: (-x['accuracy'], -x['coverage']))
    optimal = candidates[0]

    # Also find the one with best balance (highest coverage while meeting accuracy)
    balanced = max(candidates, key=lambda x: x['coverage'])

    return {
        'found': True,
        'optimal_accuracy': optimal,
        'optimal_balance': balanced,
        'all_candidates': candidates
    }


def generate_report(results: dict, estimates: dict, optimal: dict) -> str:
    """Generate EA-002 analysis report."""

    report = []
    report.append("=" * 70)
    report.append("EA-002: EXTENDED CONFIDENCE THRESHOLD ANALYSIS")
    report.append("=" * 70)
    report.append("")
    report.append(f"Pair: {results.get('pair', 'eurusd').upper()}")
    report.append(f"Horizon: h{results.get('horizon', 15)}")
    report.append(f"OOF Samples: {results.get('oof_samples', 'N/A'):,}")
    report.append(f"Baseline Overall Accuracy: {results.get('overall_accuracy', 0):.2%}")
    report.append(f"Baseline Overall AUC: {results.get('overall_auc', 0):.4f}")
    report.append("")

    # Gating curve table
    report.append("-" * 70)
    report.append("CONFIDENCE GATING CURVE (τ=0.55 to τ=0.85)")
    report.append("-" * 70)
    report.append(f"{'Threshold':<12} {'Accuracy':<12} {'Coverage':<12} {'N Signals':<12} {'Source':<10}")
    report.append("-" * 70)

    for key in sorted(estimates.keys()):
        data = estimates[key]
        report.append(
            f"{data['threshold']:<12.2f} "
            f"{data['accuracy']:<12.2%} "
            f"{data['coverage']:<12.2%} "
            f"{data['n_signals']:<12,} "
            f"{data['source']:<10}"
        )

    report.append("-" * 70)
    report.append("")

    # Optimal threshold analysis
    report.append("=" * 70)
    report.append("OPTIMAL THRESHOLD ANALYSIS")
    report.append("=" * 70)
    report.append("")
    report.append(f"Target: ≥85% called accuracy with ≤50% coverage")
    report.append("")

    if optimal['found']:
        opt_acc = optimal['optimal_accuracy']
        opt_bal = optimal['optimal_balance']

        report.append("RECOMMENDED THRESHOLD (Highest Accuracy):")
        report.append(f"  τ = {opt_acc['threshold']:.2f}")
        report.append(f"  Accuracy: {opt_acc['accuracy']:.2%}")
        report.append(f"  Coverage: {opt_acc['coverage']:.2%}")
        report.append(f"  Signals: {opt_acc['n_signals']:,}")
        report.append(f"  Source: {opt_acc['source']}")
        report.append("")

        if opt_bal != opt_acc:
            report.append("ALTERNATIVE (Best Balance - Highest Coverage Meeting Target):")
            report.append(f"  τ = {opt_bal['threshold']:.2f}")
            report.append(f"  Accuracy: {opt_bal['accuracy']:.2%}")
            report.append(f"  Coverage: {opt_bal['coverage']:.2%}")
            report.append(f"  Signals: {opt_bal['n_signals']:,}")
            report.append(f"  Source: {opt_bal['source']}")
            report.append("")

        report.append(f"All thresholds achieving ≥85% accuracy: {len(optimal['all_candidates'])}")

    else:
        report.append("WARNING: No threshold achieves 85% accuracy target")
        report.append(f"Closest: {optimal['closest']['accuracy']:.2%} at τ={optimal['closest']['threshold']:.2f}")

    report.append("")
    report.append("=" * 70)
    report.append("RECOMMENDATIONS")
    report.append("=" * 70)
    report.append("")

    # Generate recommendations based on findings
    if optimal['found']:
        opt = optimal['optimal_accuracy']
        if opt['source'] == 'ESTIMATED':
            report.append("1. VALIDATE: Re-run pipeline with τ=0.75, 0.80 to confirm estimates")
            report.append(f"2. IMPLEMENT: If validated, use τ={opt['threshold']:.2f} as production threshold")
            report.append("3. MONITOR: Track accuracy drift at deployed threshold")
        else:
            report.append(f"1. IMPLEMENT: Use τ={opt['threshold']:.2f} as production threshold")
            report.append("2. DOCUMENT: Update roadmap with new baseline accuracy")
            report.append("3. PROCEED: Move to EA-001 (ElasticNet removal) for additional gains")
    else:
        report.append("1. INVESTIGATE: Current model may not achieve 85% target")
        report.append("2. CONSIDER: EA-001 (ElasticNet removal) may improve baseline")
        report.append("3. ALTERNATIVE: Accept 82.52% with higher coverage (τ=0.70)")

    report.append("")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    print("EA-002: Extended Confidence Threshold Analysis")
    print("-" * 50)

    # Load existing results
    print("Loading calibrated stack results...")
    results = load_existing_results("eurusd", 15)

    # Calculate extended estimates
    print("Calculating extended threshold estimates...")
    estimates = estimate_extended_thresholds(results)

    # Find optimal threshold
    print("Finding optimal threshold...")
    optimal = find_optimal_threshold(estimates, min_accuracy=0.85, max_coverage=0.50)

    # Generate report
    report = generate_report(results, estimates, optimal)
    print(report)

    # Save detailed results
    output = {
        'analysis_type': 'EA-002_threshold_extension',
        'pair': results.get('pair', 'eurusd'),
        'horizon': results.get('horizon', 15),
        'baseline': {
            'overall_accuracy': results.get('overall_accuracy'),
            'overall_auc': results.get('overall_auc'),
            'oof_samples': results.get('oof_samples'),
            'recommended_threshold': results.get('recommended_threshold')
        },
        'extended_estimates': estimates,
        'optimal_threshold': optimal,
        'recommendations': {
            'primary_threshold': optimal.get('optimal_accuracy', {}).get('threshold') if optimal.get('found') else None,
            'expected_accuracy': optimal.get('optimal_accuracy', {}).get('accuracy') if optimal.get('found') else None,
            'expected_coverage': optimal.get('optimal_accuracy', {}).get('coverage') if optimal.get('found') else None,
            'validation_required': any(e['source'] == 'ESTIMATED' for e in estimates.values()
                                       if e['threshold'] >= 0.75)
        }
    }

    output_path = "/home/micha/bqx_ml_v3/intelligence/ea_002_threshold_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
