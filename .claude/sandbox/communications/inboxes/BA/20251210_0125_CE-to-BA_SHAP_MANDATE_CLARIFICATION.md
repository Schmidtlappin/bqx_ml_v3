# CE Clarification: SHAP 100K+ Mandate

**Document Type**: CE CLARIFICATION
**Date**: December 10, 2025 01:25
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**: Phase 4 Authorization

---

## CLARIFICATION

**SHAP 100K+ is a Phase 4 DELIVERABLE, not a prerequisite.**

---

## Current State

The feature ledger `shap_importance` column currently contains stability selection scores (placeholder values), NOT actual SHAP values.

| Column | Current Content | Required Content |
|--------|-----------------|------------------|
| shap_importance | Stability scores ÷ 1000 | TreeSHAP values (100K+ samples) |

---

## USER MANDATE (BINDING)

```json
"shap_sample_size": {
  "value": 100000,
  "unit": "samples minimum",
  "binding": true,
  "rationale": "Statistical robustness for SHAP importance calculation"
}
```

---

## PHASE 4 REQUIREMENT

During EURUSD h15 training, BA MUST:

1. **Generate TreeSHAP values** for all 243 RETAINED features
2. **Use minimum 100,000 samples** for SHAP calculation
3. **Update feature ledger** with actual SHAP importance values
4. **Report SHAP completion** as a checkpoint deliverable

---

## IMPLEMENTATION GUIDANCE

```python
# SHAP calculation requirements
import shap

# Minimum sample size (USER MANDATE)
SHAP_SAMPLE_SIZE = 100_000  # BINDING

# Generate SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample[:SHAP_SAMPLE_SIZE])

# Calculate mean absolute SHAP importance per feature
shap_importance = np.abs(shap_values).mean(axis=0)
```

---

## DELIVERABLE CHECKLIST

Phase 4 SHAP deliverables:

- [ ] TreeSHAP explainer created for each base model
- [ ] 100,000+ samples used for SHAP calculation
- [ ] SHAP importance calculated for all 243 RETAINED features
- [ ] Feature ledger updated with actual SHAP values
- [ ] SHAP completion reported to CE

---

## CHECKPOINT

Report SHAP completion as Checkpoint 3 (per Phase 4 authorization):
- Confirm sample count ≥ 100,000
- Confirm all RETAINED features have SHAP values
- Provide top 20 features by SHAP importance

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:25
**Status**: SHAP MANDATE CLARIFIED - PHASE 4 DELIVERABLE
