# CE Directive: Validate Re-Serialized Artifact

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:20
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: MEDIUM
**Trigger**: After BA completes re-serialization

---

## TASK

After BA reports h15_ensemble_v2.joblib complete, validate:

### 1. Structure Validation

```python
import joblib
artifact = joblib.load('models/eurusd/h15_ensemble_v2.joblib')

# Check all required keys exist
required_keys = [
    'base_models', 'calibrators', 'meta_learner',
    'feature_names', 'regime_features',
    'feature_views', 'view_config', 'metadata'
]
assert all(k in artifact for k in required_keys)
```

### 2. Model Validation

| Check | Expected |
|-------|----------|
| base_models keys | ['lightgbm', 'xgboost', 'catboost'] |
| calibrators keys | ['lightgbm', 'xgboost', 'catboost'] |
| meta_learner type | LogisticRegression |
| feature_names length | 59 |
| regime_features length | 6 |

### 3. Metadata Validation

| Field | Expected |
|-------|----------|
| version | '2.0.0' |
| enhancements | ['EA-001', 'EA-002'] |
| accuracy | 0.9166 |
| coverage | 0.3827 |

### 4. EA-003 Compatibility

| Field | Expected |
|-------|----------|
| feature_views | None (placeholder) |
| view_config.mode | 'shared' |

---

## DELIVERABLE

Submit validation report:
- PASS/FAIL for each check
- Flag any deviations
- Approve for h30-h105 if all pass

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:20
