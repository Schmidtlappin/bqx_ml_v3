# CE Directive: GATE_3 Validation Request

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:35
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH

---

## TASK: Validate GATE_3

BA has reported GATE_3 ready. QA to validate all criteria are met.

---

## GATE_3 CRITERIA TO VALIDATE

| # | Criterion | BA Reported | QA Action |
|---|-----------|-------------|-----------|
| 1 | Called accuracy ≥85% | 91.66% | Verify |
| 2 | Coverage 30-50% | 38.27% | Verify |
| 3 | SHAP samples 100K+ | 100,000 | Verify |
| 4 | TreeSHAP ALL 3 models | LGB+XGB+CB | Verify |
| 5 | Gating curves documented | τ=0.55-0.85 | Verify |
| 6 | Model artifacts to GCS | Uploaded | Verify exists |

---

## VALIDATION CHECKS

### 1. Performance Metrics
Verify in `calibrated_stack_eurusd_h15.json`:
- `called_accuracy_at_85` = 91.66%
- `coverage_at_85` = 38.27%

### 2. SHAP Compliance
Verify in `shap_eurusd_h15.json`:
- Sample count = 100,000
- All 3 models have TreeSHAP values (not proxy)

### 3. Model Artifacts
Verify GCS upload:
```bash
gsutil ls gs://bqx-ml-v3-models/models/eurusd/
```

Expected:
- h15_ensemble.joblib (~3 MB)

### 4. Gating Curves
Verify documented for thresholds τ=0.55 to τ=0.85

---

## REPORT FORMAT

Submit GATE_3 Validation Report:
- PASS/FAIL for each criterion
- Evidence for each check
- Overall GATE_3 verdict
- Recommendation for Phase 4 expansion

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:35
**Status**: GATE_3 VALIDATION REQUESTED
