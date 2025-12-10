# CE Directive: Phase 4 Issue Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:20
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**: BA-to-CE_PHASE4_ISSUES_REPORT (02:15)

---

## DECISIONS

### ISSUE-001: XGBoost SHAP - **DOWNGRADE REQUIRED**

**Decision**: Option 1 - Downgrade XGBoost to 2.1.0

**Rationale**: USER MANDATE requires TreeSHAP for ALL 3 models. Feature importance proxy is NOT acceptable.

**Action Required**:
```bash
pip install xgboost==2.1.0
```

Then re-run SHAP generation with proper TreeSHAP for XGBoost.

**This is BINDING per user mandate.**

---

### ISSUE-002: Feature Ledger SHAP Update - **BA TASK**

**Owner**: BA
**Priority**: MEDIUM
**Action**: Update feature ledger with actual SHAP values after XGBoost fix.

---

### ISSUE-003: Model Artifacts - **BA TASK**

**Owner**: BA
**Priority**: HIGH (GATE_3 requirement)
**Action**: Add model serialization before GATE_3:
```python
import joblib
joblib.dump(models, 'gs://bqx-ml-v3-models/eurusd/h15_ensemble.joblib')
```

**GATE_3 criteria**: "Model artifacts saved to GCS"

---

### ISSUE-004: Limited Feature Set - **DEFERRED**

**Status**: ACCEPTABLE for Phase 4 pilot
**Action**: Address in Phase 4 expansion (full 243 features)

---

## GAPS - DELEGATION

| Gap | Owner | Priority |
|-----|-------|----------|
| G1: Feature selection other pairs | BA | Phase 4 expansion |
| G2: Walk-forward splits | BA | Phase 4 expansion |
| G3: Target tables validation | QA | LOW |

---

## UPDATED BA TASK LIST

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | Downgrade XGBoost to 2.1.0 | **CRITICAL** | DO NOW |
| 2 | Re-run TreeSHAP for ALL 3 models | **CRITICAL** | After #1 |
| 3 | Add model serialization to GCS | HIGH | Before GATE_3 |
| 4 | Update feature ledger with SHAP | MEDIUM | After #2 |

---

## TECHNICAL DEBT - ACKNOWLEDGED

T1 and T2 noted. Address after GATE_3.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:20
**Status**: ISSUE REMEDIATION DIRECTIVE ISSUED
