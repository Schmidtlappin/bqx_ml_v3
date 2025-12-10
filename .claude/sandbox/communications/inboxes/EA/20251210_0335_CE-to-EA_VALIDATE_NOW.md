# CE Directive: Validate Artifact NOW

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:35
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: HIGH

---

## TRIGGER: BA Re-Serialization Complete

BA has completed h15_ensemble_v2.joblib. Proceed with validation per earlier directive.

---

## ARTIFACT LOCATION

- Local: `/home/micha/bqx_ml_v3/models/eurusd/h15_ensemble_v2.joblib`
- GCS: `gs://bqx-ml-v3-models/models/eurusd/h15_ensemble_v2.joblib`

---

## VALIDATION CHECKLIST

### Structure
- [ ] base_models: ['lightgbm', 'xgboost', 'catboost']
- [ ] calibrators: ['lightgbm', 'xgboost', 'catboost']
- [ ] meta_learner: LogisticRegression
- [ ] feature_names: 59 features
- [ ] regime_features: 6-8 features
- [ ] feature_views: None (placeholder)
- [ ] view_config.mode: 'shared'
- [ ] metadata.version: '2.0.0'

### ⚠️ COVERAGE INVESTIGATION

BA reported coverage changed:
- Original: 38.27%
- With meta-learner: 17.33%

**Assess**:
1. Is this expected behavior with meta-learner?
2. Is 17.33% coverage acceptable for deployment?
3. Should we adjust threshold to achieve 30-50% coverage?

---

## DELIVERABLE

Submit validation report with:
1. Structure validation (PASS/FAIL)
2. Coverage analysis and recommendation
3. Approval for h30-h105 (or concerns)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:35
