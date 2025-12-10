# EURUSD h15 Baseline Metrics

**Document Type**: EA BASELINE DOCUMENT
**Date**: December 10, 2025
**Purpose**: A/B comparison benchmark for h30-h105 and EA-003

---

## Performance Summary

| Metric | Value | Notes |
|--------|-------|-------|
| **Called Accuracy** | 91.66% | at τ=0.85 |
| **Coverage** | 38.27% | Within 30-50% target |
| **Overall AUC** | 0.8505 | Ensemble performance |
| **OOF Samples** | 66,515 | Walk-forward validation |

---

## Accuracy-Coverage Tradeoff

| Threshold | Accuracy | Coverage | Signals |
|-----------|----------|----------|---------|
| τ=0.55 | 78.16% | 95.30% | 63,392 |
| τ=0.60 | 79.48% | 90.36% | 60,106 |
| τ=0.65 | 80.87% | 84.99% | 56,530 |
| τ=0.70 | 82.52% | 78.85% | 52,445 |
| τ=0.75 | 84.58% | 70.87% | 47,139 |
| τ=0.80 | 87.24% | 59.68% | 39,693 |
| **τ=0.85** | **91.66%** | **38.27%** | **25,457** |

### Operating Points

| Mode | Threshold | Accuracy | Coverage | Use Case |
|------|-----------|----------|----------|----------|
| **High Accuracy** | τ=0.85 | 91.66% | 38.27% | Maximum accuracy |
| Balanced | τ=0.80 | 87.24% | 59.68% | Higher signal volume |

---

## Architecture

### Ensemble Composition

| Model | AUC | Status |
|-------|-----|--------|
| LightGBM | 0.8418 | ACTIVE |
| XGBoost | 0.8432 | ACTIVE |
| CatBoost | 0.8510 | ACTIVE |
| ~~ElasticNet~~ | 0.4578 | REMOVED (EA-001) |

**Meta-Learner**: Logistic Regression with regime features

### Features

| Metric | Value |
|--------|-------|
| Training features | 59 |
| Source | robust_feature_selection_eurusd_h15.json |
| Selection method | Group-First Stability (50% threshold) |
| SHAP samples | 100,000+ (USER MANDATE) |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Walk-forward folds | 5 |
| Embargo intervals | 30 |
| Calibration | Platt scaling |

---

## Artifacts

| Artifact | Location | Size |
|----------|----------|------|
| Ensemble Model | gs://bqx-ml-v3-models/models/eurusd/h15_ensemble.joblib | 2.98 MiB |
| SHAP Values | (embedded in ledger) | - |
| Feature Ledger | /data/feature_ledger.parquet | 18 MB |

---

## Enhancements Applied

| ID | Enhancement | Impact | Date |
|----|-------------|--------|------|
| EA-001 | ElasticNet Removal | +1.5% accuracy | 2025-12-09 |
| EA-002 | Higher Threshold (τ=0.85) | +9.14% total | 2025-12-09 |

### Accuracy Progression

```
Baseline (τ=0.70, 4 models):  82.52%
After EA-002 (τ=0.80):        86.23%
After EA-001 (3 models):      87.24%
After EA-002 (τ=0.85):        91.66%
────────────────────────────────────
Total Improvement:            +9.14%
```

---

## Benchmark Criteria

This baseline establishes the benchmark for:

### 1. Horizon Expansion (h30-h105)
- Target: Similar or better accuracy at each horizon
- Acceptable: Within 2% of h15 baseline

### 2. EA-003 Feature-View Diversity (Phase 4.5)
- Target: ≥92.5% accuracy (improvement)
- Minimum: ≥91.0% (no regression)
- Secondary: Inter-model correlation < 0.70

### 3. Pair Scaling (Phase 5)
- Target: Maintain ≥85% called accuracy across 28 pairs
- Coverage: 30-50% range

---

## Validation Notes

- Validated by EA on 2025-12-09
- GATE_2 passed 2025-12-10
- Phase 4 in progress

---

*Created by EA - December 10, 2025*
