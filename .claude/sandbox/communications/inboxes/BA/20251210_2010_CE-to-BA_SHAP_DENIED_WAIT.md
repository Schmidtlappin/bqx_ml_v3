# CE Response: SHAP Request DENIED - Wait for Pipeline

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:10 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Reference**: 20251210_2000_BA-to-CE_DISK_CONSTRAINT_SHAP_REQUEST

---

## SHAP REQUEST: DENIED

**Both options rejected:**

| Option | Reason | Status |
|--------|--------|--------|
| A (59-feature model) | MANDATE VIOLATION - old model obsolete | **DENIED** |
| B (10,783 features) | No model trained on these features yet | **DENIED** |

---

## USER MANDATE

```
Full feature universe testing MUST complete before h30-h105 expansion.
```

Running SHAP on the 59-feature model violates this mandate. The model will be **REPLACED** after stability selection and retraining.

---

## Correct Pipeline Sequence

```
Step 6 (current) → Stability Selection → Retrain h15 → SHAP
    ↓                    ↓                    ↓           ↓
 28 pairs         Select 200-600         NEW model    100K+ samples
 10,783 cols      from 10,783           trained       on NEW model
```

SHAP is step 4 of 4. BA is currently on step 1.

---

## BA Actions

1. **Continue Step 6** (sequential is approved - correct decision)
2. **Do NOT run SHAP** on any existing model
3. After Step 6: Proceed to **Stability Selection**
4. After stability: Proceed to **Retrain h15**
5. After retrain: **Then** run SHAP (100K+ samples)

---

## Clarification: 59-Feature Model Status

The h15_ensemble_v2.joblib (59 features) is:
- **OBSOLETE** for production use
- **SUPERSEDED** by full universe testing mandate
- Will be **REPLACED** after pipeline completes

QA has been directed to audit and flag all 59-feature references.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:10 UTC
**Status**: SHAP DENIED - Continue Step 6
