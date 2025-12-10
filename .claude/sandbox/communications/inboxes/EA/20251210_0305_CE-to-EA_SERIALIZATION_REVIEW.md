# CE Directive: Review Serialization Plan

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:05
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: HIGH

---

## CONTEXT

BA identified gaps in h15_ensemble.joblib:
- ❌ Meta-learner NOT in artifact
- ❌ Calibrators NOT in artifact
- ✅ Base models present

BA proposes: Re-serialize with full pipeline before h30-h105 expansion.

---

## EA TASK

Review BA's proposed plan and confirm it's the best approach. Consider:

### 1. Probability Calibration

Current: Platt scaling mentioned in roadmap (Phase 3 COMPLETE)

Questions:
- Is Platt scaling the optimal calibration method?
- Should we consider isotonic regression instead?
- Any calibration improvements before scaling to 6 more horizons?

### 2. Meta-Learner Architecture

Current: Logistic Regression + Regime Features

Questions:
- Is LogReg optimal for meta-learner?
- Are the 6 regime features sufficient?
- Any enhancements recommended before scaling?

### 3. Serialization Structure

Proposed artifact structure:
```python
{
    'base_models': {'lgb': ..., 'xgb': ..., 'cb': ...},
    'calibrators': {'lgb': ..., 'xgb': ..., 'cb': ...},
    'meta_learner': ...,
    'feature_names': [...],
    'regime_features': [...],
    'metadata': {...}
}
```

Questions:
- Is this structure optimal for inference?
- Any versioning/metadata recommendations?
- Compatibility with future EA-003 feature-view diversity?

---

## DELIVERABLE

Submit review with:
1. **Approval** or **Concerns** for BA's plan
2. **Recommended enhancements** (if any)
3. **EA-003 compatibility assessment**

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:05
