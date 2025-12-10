# CE Directive: File Updates

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:30
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: MEDIUM

---

## TASK: Update BA Files to Current State

### 1. Update BA_TODO.md

Reflect completed tasks:
- ✅ XGBoost downgrade to 2.1.0
- ✅ TreeSHAP re-run (all 3 models)
- ⏳ Model serialization to GCS (IN PROGRESS)
- ⏸️ Feature ledger SHAP update (PENDING)

### 2. Update roadmap_v2.json

Update Phase 4 milestones:
```json
{
  "shap_value_generation": {
    "status": "COMPLETE",
    "method": "TreeSHAP for all 3 models",
    "samples": 100000,
    "compliance": "USER MANDATE MET"
  }
}
```

### 3. Update Training Script

Ensure `generate_shap_eurusd_h15.py` reflects:
- XGBoost 2.1.0 requirement in comments
- TreeExplainer for all 3 models

### 4. Create/Update Model Config

Document trained model configuration:
- XGBoost version: 2.1.0
- SHAP method: TreeSHAP
- Sample size: 100,000

---

## REPORT

Submit file update completion report when done.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:30
