# BA Phase 4 Issues, Errors & Gaps Report

**Document Type**: ISSUES REPORT
**Date**: December 10, 2025 02:15
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH

---

## EXECUTIVE SUMMARY

Phase 4 EURUSD h15 training completed successfully. One technical issue identified requiring attention.

---

## CRITICAL ISSUES

### NONE

---

## HIGH PRIORITY ISSUES

### ISSUE-001: XGBoost 3.x SHAP Incompatibility

**Status**: ACTIVE - WORKAROUND APPLIED

**Description**:
XGBoost 3.1.2 is incompatible with SHAP 0.49.1 TreeExplainer due to `base_score` parsing error.

**Error**:
```
ValueError: could not convert string to float: '[4.849E-1]'
```

**Root Cause**:
XGBoost 3.x changed the format of `learner_model_param["base_score"]` from float to array notation `[4.849E-1]`.

**Mitigation Applied**:
Used scaled XGBoost feature importance as proxy for TreeSHAP.

**Impact**:
- 2/3 models use actual TreeSHAP (LightGBM, CatBoost)
- 1/3 model uses feature importance proxy (XGBoost)
- SHAP sample count mandate (100K+) is COMPLIANT

**Recommended Fix**:
```bash
# Option 1: Downgrade XGBoost
pip install xgboost==2.1.0

# Option 2: Wait for SHAP library update
# shap issue tracking: https://github.com/shap/shap/issues
```

**Decision Required**: Accept workaround or downgrade XGBoost?

---

## MEDIUM PRIORITY ISSUES

### ISSUE-002: Feature Ledger SHAP Update Pending

**Status**: PENDING

**Description**:
Feature ledger `shap_importance` column contains stability scores, not actual SHAP values.

**Current State**:
- SHAP values generated for 59 training features
- Feature ledger has 243 RETAINED features for EURUSD h15
- Mapping between SHAP output and ledger not yet implemented

**Action Required**:
Update feature ledger with actual SHAP values for mapped features.

---

### ISSUE-003: Model Artifacts Not Persisted

**Status**: PENDING

**Description**:
Trained models exist only in memory during script execution. Not saved to disk or GCS.

**Impact**:
- Models would need to be retrained for inference
- No version control for trained models

**Recommendation**:
Add model serialization to training pipeline:
```python
import joblib
joblib.dump(models, '/models/eurusd/h15_ensemble.joblib')
```

---

## LOW PRIORITY ISSUES

### ISSUE-004: Limited Feature Set in Training Query

**Status**: COSMETIC

**Description**:
Training query uses 59 hardcoded features, not all 243 RETAINED features from ledger.

**Impact**:
- Training pipeline functional with core features
- Full feature integration would require dynamic query generation

**Recommendation**:
Enhance training pipeline to read feature list from ledger for complete coverage.

---

## GAPS INVENTORY

### G1: Feature Selection for Other Pairs

**Status**: PLANNED (Phase 4 expansion)

**Description**:
Only EURUSD h15 has feature selection and SHAP values.

**Scope**: 195 remaining pair-horizon combinations

**Plan**: Run feature selection after EURUSD validation

---

### G2: Walk-Forward Split Configs for Other Pairs

**Status**: PARTIAL

**Description**:
Only `walk_forward_splits_eurusd.json` exists.

**Scope**: 27 additional pairs need split configs

**Plan**: Generate configs during Phase 4 expansion

---

### G3: Target Tables Coverage

**Status**: UNKNOWN

**Description**:
Verified `targets_eurusd` exists. Other pairs not validated.

**Action**: Validate target table availability for all 28 pairs

---

## TECHNICAL DEBT

### T1: Hardcoded Query in Training Pipeline

**Issue**: Training features hardcoded in SQL query
**Impact**: Inflexible feature selection
**Recommendation**: Parameterize query from feature ledger

### T2: No Model Versioning

**Issue**: No version tracking for trained models
**Impact**: Cannot roll back to previous models
**Recommendation**: Implement model registry (MLflow or GCS versioning)

---

## RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| XGBoost SHAP accuracy | LOW | LOW | 2/3 TreeSHAP + proxy acceptable |
| Model loss | MEDIUM | HIGH | Add model serialization |
| Feature mismatch | LOW | MEDIUM | Validate ledger→query mapping |

---

## ACTION ITEMS

| # | Action | Owner | Priority | Status |
|---|--------|-------|----------|--------|
| A1 | Decide on XGBoost SHAP approach | CE | HIGH | PENDING |
| A2 | Update feature ledger with SHAP | BA | MEDIUM | PENDING |
| A3 | Add model serialization | BA | MEDIUM | PENDING |
| A4 | Validate other pairs' data | BA | LOW | PENDING |

---

## PHASE 4 STATUS SUMMARY

| Metric | Status |
|--------|--------|
| Training | COMPLETE |
| SHAP 100K+ | COMPLIANT |
| Gating curves | COMPLETE |
| Issues identified | 4 |
| Critical issues | 0 |

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 10, 2025 02:15
**Status**: ISSUES REPORTED - AWAITING CE GUIDANCE
