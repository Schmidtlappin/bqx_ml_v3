# CE Directive: h15 Baseline & Horizon Prep

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:55
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: MEDIUM

---

## CONTEXT

BA is completing h15 pipeline verification. EA can prepare for horizon expansion.

---

## TASKS

### 1. h15 Baseline Documentation (HIGH)

Create baseline document for A/B comparison:

```markdown
# EURUSD h15 Baseline Metrics

## Performance
- Called Accuracy: 91.66% at τ=0.85
- Coverage: 38.27%
- Accuracy-Coverage tradeoff curve

## Architecture
- Ensemble: LGB + XGB + CB (3 models)
- Features: 59 training features
- SHAP: 100K samples, TreeSHAP

## Artifacts
- Model: gs://bqx-ml-v3-models/models/eurusd/h15_ensemble.joblib
- Size: 2.98 MiB
```

This becomes the benchmark for:
- h30-h105 comparison
- EA-003 feature-view diversity testing (Phase 4.5)

### 2. Horizon Expansion Preparation (MEDIUM)

Review training scripts for parameterization:
- Can `stack_calibrated.py` accept horizon parameter?
- What changes needed for h30, h45, etc.?
- Identify hardcoded h15 references

### 3. Cost Projection (LOW)

Estimate cost for remaining 6 horizons:
- Training time per horizon
- BigQuery query costs
- GCS storage for 7 models

---

## DELIVERABLES

1. h15_baseline.md - Baseline metrics document
2. Horizon expansion readiness assessment
3. Cost projection (optional)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:55
