# CE Directive: Full Pipeline Audit & Optimization Review

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:25 UTC
**From**: Chief Engineer (CE)
**To**: Engineering Agent (EA)
**Priority**: **HIGH**
**Subject**: Audit Pipeline Architecture, Identify Gaps, Recommend Optimizations

---

## DIRECTIVE: COMPREHENSIVE PIPELINE AUDIT

EA shall audit the full feature universe pipeline to confirm:
1. Pipeline is properly formed with no gaps
2. All stages are correctly sequenced
3. Recommend performance-improving enhancements for short/long-term outcomes

---

## Current Pipeline (Per BA_TODO)

```
Step 6: Feature Extraction (28 pairs)     ← IN PROGRESS
         ↓
    10,783 features per pair extracted
    Output: /tmp/feature_chunks/{pair}/*.parquet
         ↓
Stability Selection                       ← PENDING
    - L1/Lasso regularization
    - 5 folds × 3 seeds = 15 iterations
    - 50% threshold
    - Script: pipelines/training/feature_selection_robust.py
         ↓
    ~200-600 stable features identified
         ↓
Retrain h15                               ← PENDING
    - LGB, XGB, CatBoost base models
    - Platt calibration
    - Meta-learner (LogisticRegression)
    - Script: pipelines/training/stack_calibrated.py
         ↓
SHAP Calculation                          ← PENDING
    - TreeSHAP on retrained model
    - 100K+ samples (USER MANDATE)
    - Output: intelligence/shap_{pair}_{horizon}.json
         ↓
h30-h105 Expansion                        ← BLOCKED until above complete
```

---

## Audit Requirements

### 1. Pipeline Integrity Check

| Question | Answer Required |
|----------|-----------------|
| Are all pipeline stages properly connected? | Y/N + details |
| Are inputs/outputs correctly specified? | Y/N + details |
| Are there any missing stages? | Y/N + details |
| Are there data format mismatches? | Y/N + details |

### 2. Gap Analysis

Identify any gaps between:
- Step 6 output (parquet chunks) → Stability selection input
- Stability selection output → Training input
- Training output → SHAP input
- SHAP output → Feature ledger

### 3. Performance Optimization Recommendations

**Short-term (This Sprint):**
| Area | Current | Recommended | Impact |
|------|---------|-------------|--------|
| ? | ? | ? | ? |

**Long-term (Future Sprints):**
| Area | Current | Recommended | Impact |
|------|---------|-------------|--------|
| ? | ? | ? | ? |

---

## Files to Audit

| File | Purpose |
|------|---------|
| `pipelines/training/parallel_feature_testing.py` | Feature extraction |
| `pipelines/training/feature_selection_robust.py` | Stability selection |
| `pipelines/training/stack_calibrated.py` | Model training |
| `scripts/parallel_stability_selection.py` | (if exists) |
| `intelligence/roadmap_v2.json` | Pipeline specification |

---

## Expected Output

EA shall produce:

1. **Pipeline Diagram**: Validated/corrected flow diagram
2. **Gap Report**: Any missing connections or stages
3. **Optimization Report**: Short-term and long-term recommendations
4. **Risk Assessment**: Any potential failure points

---

## Context

- Step 6 running sequentially (~2-3 hours remaining)
- User mandate: Full feature universe testing before h30-h105 expansion
- 59-feature model is OBSOLETE, will be replaced
- QA audit confirms no hardcoded feature lists in training pipelines

---

## Deadline

Report due: When Step 6 completes (or earlier if possible)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:25 UTC
