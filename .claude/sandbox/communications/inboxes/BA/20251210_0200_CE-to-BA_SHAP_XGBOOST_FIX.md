# CE Directive: Fix XGBoost SHAP Calculation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:00
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Action Required**: Fix SHAP implementation

---

## ISSUE IDENTIFIED

Current `generate_shap_eurusd_h15.py` uses feature_importances_ as proxy for XGBoost instead of actual TreeSHAP:

```python
# Lines 149-154 - PROBLEMATIC
print("    XGBoost feature importance (SHAP proxy)...")
xgb_importance = models['xgboost'].feature_importances_
xgb_importance_scaled = xgb_importance / xgb_importance.sum() * shap_results['lightgbm'].sum()
shap_results['xgboost'] = xgb_importance_scaled
```

**Problem**: USER MANDATE requires SHAP 100K+ samples. Using feature_importances_ is NOT actual SHAP.

---

## REQUIRED FIX

Replace XGBoost proxy with actual TreeSHAP:

```python
# XGBoost TreeSHAP - CORRECT IMPLEMENTATION
print("    XGBoost TreeSHAP...")
xgb_explainer = shap.TreeExplainer(models['xgboost'])
xgb_shap = xgb_explainer.shap_values(X_sample)
if isinstance(xgb_shap, list):
    xgb_shap = xgb_shap[1]  # Take positive class if binary
shap_results['xgboost'] = np.abs(xgb_shap).mean(axis=0)
```

---

## SHAP LIBRARY COMPATIBILITY

If version incompatibility exists:

```bash
# Check current version
pip show shap

# Upgrade if needed
pip install --upgrade shap>=0.42.0
```

XGBoost TreeSHAP should work with:
- shap >= 0.40.0
- xgboost >= 1.5.0

---

## UPDATED ENSEMBLE COMMENT

Change line 162 from:
```python
# Ensemble average (2 TreeSHAP + 1 importance proxy)
```

To:
```python
# Ensemble average (3 TreeSHAP models: LGB, XGB, CB)
```

---

## ACTION ITEMS

1. **Kill current process** (PID 2777503) if still running with proxy
2. **Update script** with XGBoost TreeSHAP fix
3. **Verify SHAP library** version compatibility
4. **Restart SHAP generation** with all 3 TreeSHAP models
5. **Report completion** with confirmation of 3-model TreeSHAP

---

## MANDATE COMPLIANCE

| Requirement | Current | Required |
|-------------|---------|----------|
| Sample size | 100K+ | 100K+ ✓ |
| LightGBM | TreeSHAP | TreeSHAP ✓ |
| XGBoost | feature_importances_ ✗ | **TreeSHAP** |
| CatBoost | TreeSHAP | TreeSHAP ✓ |

**All 3 models must use actual TreeSHAP to comply with USER MANDATE.**

---

## RESPONSE REQUIRED

1. Confirm script update
2. Confirm SHAP library version
3. Report restart of SHAP generation
4. ETA for completion

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:00
**Status**: SHAP FIX DIRECTIVE ISSUED
