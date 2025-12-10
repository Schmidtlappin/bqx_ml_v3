# CE Directive: Full 6,477 Feature Universe Testing - USER MANDATE

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:45
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL** - USER MANDATE

---

## USER MANDATE

> "Full 6,477 universe testing is a user mandate."

This supersedes previous h30-h105 expansion authorization. Full feature testing MUST complete first.

---

## CURRENT STATE

| Metric | Value |
|--------|-------|
| Training features | 59 |
| Stable features (50% threshold) | 607 |
| Full universe | **6,477** |
| % Tested | **~15.6%** |

**Problem**: Only 59 of 6,477 features are being tested. Potential accuracy gains of +2-5% are being missed.

---

## TASK: Full Feature Selection

### Phase 1: Query All 6,477 Features

1. Update training query to fetch ALL features from:
   - `bqx_ml_v3_features_v2.*` tables
   - All feature types: reg, mom, vol, der, lag, cov, corr, tri, mkt

2. Generate feature matrix with all 6,477 columns for EURUSD

### Phase 2: Run Stability Selection

```python
# Run on full feature universe
# 5 folds x 3 seeds
# 50% frequency threshold (USER APPROVED)
# Identify stable features
```

Expected output: 200-600 stable features (vs current 59)

### Phase 3: Retrain with Optimal Subset

1. Retrain base models (LGB, XGB, CB) with expanded features
2. Recalibrate probabilities
3. Retrain meta-learner
4. Generate SHAP values (100K+ samples)

---

## FILES TO MODIFY

| File | Change |
|------|--------|
| `pipelines/training/stack_calibrated.py` | Remove hardcoded 59-feature list |
| Training SQL | Dynamic feature query from ledger |

---

## DELIVERABLES

1. **Feature Selection Report**
   - Total features tested: 6,477
   - Stable features identified: X (expected 200-600)
   - Selection method: Stability @ 50% threshold

2. **Retrained Model**
   - h15_ensemble_v3.joblib (with expanded features)
   - Updated SHAP values

3. **Accuracy Comparison**
   | Metric | Before (59 feat) | After (X feat) |
   |--------|------------------|----------------|
   | Accuracy | 91.7% | ? |
   | Coverage | 17.3% | ? |

---

## SUCCESS CRITERIA

- All 6,477 features tested via stability selection
- Optimal subset identified (50% threshold)
- h15 retrained with full feature set
- Accuracy improvement documented

---

## TIMELINE

This is the critical path. Complete before h30-h105 expansion.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:45
**Status**: USER MANDATE - EXECUTE IMMEDIATELY
