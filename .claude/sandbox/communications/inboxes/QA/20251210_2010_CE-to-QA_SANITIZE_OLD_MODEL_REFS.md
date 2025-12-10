# CE Directive: Sanitize Workspace - Remove 59-Feature Old Model References

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:10 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**
**Subject**: USER MANDATE VIOLATION - Remove Old Model Artifacts

---

## DIRECTIVE: SANITIZE WORKSPACE

The 59-feature model (h15_ensemble_v2.joblib) and associated references are **OBSOLETE** per USER MANDATE requiring full feature universe testing.

---

## Scope: Identify and Flag/Remove

### 1. Model Artifacts (Flag for Removal)

| File | Location | Action |
|------|----------|--------|
| h15_ensemble_v2.joblib | GCS + local | FLAG - will be replaced |
| shap_eurusd_h15.json | intelligence/ | FLAG - only 59 features |

### 2. Hardcoded 59-Feature References

Search for and document all occurrences of:
- `feature_count": 59`
- `59 features`
- Hardcoded feature lists in training pipelines

**Files to audit:**
- `pipelines/training/stack_calibrated.py`
- `pipelines/training/feature_selection_*.py`
- `intelligence/*.json`
- `mandate/*.md`

### 3. Documentation References

Flag any documentation that references:
- "59 features" as current/final
- Old model as production-ready
- SHAP results from 59-feature model as authoritative

---

## Expected Output

QA shall produce:

1. **Audit Report**: List of all files containing 59-feature references
2. **Recommended Actions**: For each file, specify:
   - DELETE (obsolete artifact)
   - UPDATE (change reference)
   - ARCHIVE (move to archive/)
   - KEEP (historical reference OK)

---

## USER MANDATE Context

```
MANDATE: Full 11,337 column universe testing MUST complete before h30-h105 expansion.

Pipeline:
Step 6 (28 pairs) → Stability Selection → Retrain h15 → NEW SHAP
                                              ↑
                                    Replaces 59-feature model
```

Any suggestion to use the 59-feature model for SHAP or production is a **MANDATE VIOLATION**.

---

## Deadline

Report due: Before Step 6 completes (~2 hours)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:10 UTC
