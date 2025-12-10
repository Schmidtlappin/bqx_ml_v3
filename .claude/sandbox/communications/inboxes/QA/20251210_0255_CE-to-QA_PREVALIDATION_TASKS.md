# CE Directive: Pre-Validation Tasks

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:55
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: MEDIUM

---

## CONTEXT

BA is completing h15 pipeline verification. QA can begin pre-validation while waiting.

---

## TASKS

### 1. Artifact Pre-Validation (Do Now)

Verify these files exist and contain expected data:

| File | Check |
|------|-------|
| `gs://bqx-ml-v3-models/models/eurusd/h15_ensemble.joblib` | Exists, ~3MB |
| `intelligence/calibrated_stack_eurusd_h15.json` | Contains accuracy/coverage |
| `intelligence/shap_eurusd_h15.json` | Contains 59 features |
| `data/feature_ledger.parquet` | SHAP values for EURUSD h15 |

### 2. Metrics Pre-Check

From calibrated_stack_eurusd_h15.json, verify:
- `called_accuracy` at τ=0.85 = 91.66%
- `coverage` at τ=0.85 = 38.27%
- Gating curves for τ=0.55 to τ=0.85

### 3. Prepare GATE_3 Validation Script

Create reusable validation for future horizons:
```python
# Pseudocode
def validate_gate3(pair, horizon):
    # Check accuracy >= 85%
    # Check coverage 30-50%
    # Check SHAP 100K+
    # Check GCS artifacts
    return pass/fail
```

### 4. Cost Check (Ongoing)

Quick BigQuery cost check for today's operations.

---

## REPORT

Submit pre-validation findings. Flag any issues before full GATE_3 validation.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:55
