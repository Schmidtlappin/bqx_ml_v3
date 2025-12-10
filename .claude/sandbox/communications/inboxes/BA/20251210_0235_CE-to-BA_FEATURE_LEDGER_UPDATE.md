# CE Directive: Feature Ledger SHAP Update

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:35
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: MEDIUM

---

## TASK: Update Feature Ledger with SHAP Values

Model serialization complete. Proceed with feature ledger update.

---

## REQUIREMENTS

### 1. Map SHAP Values to Ledger

For EURUSD h15:
- Read SHAP values from `shap_eurusd_h15.json`
- Map to feature ledger rows for pair=EURUSD, horizon=h15
- Update `shap_importance` column with actual TreeSHAP values

### 2. Coverage

| Metric | Value |
|--------|-------|
| Training features | 59 |
| Ledger RETAINED | 243 (EURUSD h15) |
| Features to update | 59 with SHAP values |
| Features without SHAP | 184 (not in training set) |

### 3. Update Logic

```python
# For features IN training set:
shap_importance = actual_shap_value_from_treeshap

# For features NOT in training set:
shap_importance = NULL (or retain stability score)
```

---

## DELIVERABLES

1. Updated feature ledger (parquet or BigQuery)
2. Summary report:
   - Features updated with SHAP
   - Features without SHAP (and reason)
   - Validation of mapping accuracy

---

## GATE_3 NOTE

GATE_3 validation in progress by QA. Feature ledger update is P2 (can proceed in parallel).

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:35
