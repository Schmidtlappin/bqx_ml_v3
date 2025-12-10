# CE Directive: Prepare GATE_3 Re-Validation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 21:35 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**
**Subject**: Prepare for GATE_3 Re-Validation After Pipeline Rebuild

---

## DIRECTIVE: PREPARATION TASKS

While pipeline processes (Steps 6-9), QA shall prepare for GATE_3 re-validation of the new model.

---

## Task 1: Update validate_gate3.py (HIGH)

Ensure validation script handles new model:

| Check | Current | New |
|-------|---------|-----|
| Model name | h15_ensemble_v2.joblib | h15_ensemble_v3.joblib (or similar) |
| Feature count | 59 | ~200-600 (from stability selection) |
| Model path | Fixed | Dynamic from `data/features/` |

**Updates Required:**
- [ ] Accept model path as parameter
- [ ] Dynamic feature count validation
- [ ] Compare against expanded feature universe

---

## Task 2: Prepare Coverage Validation Script (HIGH)

Create/update script to verify coverage target:

| Metric | Target | Current (59-feature) |
|--------|--------|----------------------|
| Coverage | 30-50% | 17.33% |
| Called Accuracy | ≥85% | 91.70% |

**Script Requirements:**
- [ ] Calculate coverage from predictions
- [ ] Verify within 30-50% target range
- [ ] Compare before/after feature expansion

---

## Task 3: Audit Cross-References (MEDIUM)

Verify consistency across files:

| File | Check |
|------|-------|
| `BA_TODO.md` | Matches current pipeline status |
| `EA_TODO.md` | Matches current pipeline status |
| `QA_TODO.md` | Matches current pipeline status |
| Intelligence files | Feature counts consistent (11,337/1,064) |

---

## Task 4: Prepare Test Dataset (MEDIUM)

Identify validation data for GATE_3:

| Requirement | Source |
|-------------|--------|
| Sample size | 100K+ rows (per USER MANDATE) |
| Pairs | Start with EURUSD |
| Horizons | h15 first, then h30-h105 |

---

## Expected Outputs

| Output | Purpose |
|--------|---------|
| Updated `validate_gate3.py` | Handles new model |
| Coverage validation script | Verifies 30-50% target |
| Cross-reference audit report | Confirms consistency |

---

## GATE_3 Criteria Reminder

| Criterion | Target | Notes |
|-----------|--------|-------|
| Called Accuracy | ≥85% | Current: 91.70% |
| Coverage | 30-50% | Current: 17.33% (below target) |
| SHAP Samples | 100K+ | USER MANDATE |
| Model Artifacts | GCS uploaded | After validation |

---

## Timeline

Preparation should complete BEFORE Step 9 (SHAP) completes (~5-6 hours).

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 21:35 UTC
