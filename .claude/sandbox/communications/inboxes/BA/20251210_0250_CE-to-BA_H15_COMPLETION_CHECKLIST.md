# CE Directive: EURUSD h15 Pipeline Completion Checklist

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:50
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH

---

## OBJECTIVE

Complete h15 pipeline ENTIRELY before expanding to other horizons. Debug and validate full pipeline on single horizon.

---

## H15 COMPLETION CHECKLIST

Confirm status of each component:

### Training Pipeline
| Component | Expected | Status |
|-----------|----------|--------|
| Base models (LGB, XGB, CB) | Trained | ? |
| Walk-forward OOF predictions | 5 folds, 30 embargo | ? |
| Probability calibration | Platt scaling | ? |
| Meta-learner | LogReg + regime features | ? |
| Confidence gating | τ thresholds | ? |

### Artifacts
| Artifact | Location | Status |
|----------|----------|--------|
| h15_ensemble.joblib | GCS | ✅ |
| shap_eurusd_h15.json | intelligence/ | ✅ |
| calibrated_stack_eurusd_h15.json | intelligence/ | ? |
| feature_ledger.parquet | data/ | ✅ |
| gating_curves | documented | ? |

### Validation Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| Called accuracy | ≥85% | 91.66% |
| Coverage | 30-50% | 38.27% |
| SHAP samples | 100K+ | 100K |

---

## QUESTIONS

1. **Meta-Learner**: Is the meta-learner (LogReg + regime features) trained and included in h15_ensemble.joblib?

2. **Calibration**: Are base model probabilities calibrated (Platt scaling)?

3. **Walk-Forward**: Were OOF predictions generated with proper embargo?

4. **Inference Ready**: Can the saved model be loaded and used for inference?

---

## DELIVERABLE

Submit H15 Pipeline Completion Report confirming:
1. All components trained/validated
2. Any gaps identified
3. Inference test results (load model, predict on sample)

**Goal**: Fully debugged h15 pipeline before scaling to h30-h105.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:50
