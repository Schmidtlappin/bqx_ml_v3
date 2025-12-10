# CE Authorization: Phase 4 EURUSD Training

**Document Type**: PHASE AUTHORIZATION
**Date**: December 10, 2025 01:20
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: PHASE 4 AUTHORIZED

---

## AUTHORIZATION

**PHASE 4 IS AUTHORIZED**

BA is approved to begin EURUSD h15 pilot training.

---

## PHASE 3 ACKNOWLEDGMENT

Phase 3 Readiness Report received and reviewed:

| Prerequisite | Status |
|--------------|--------|
| Training pipeline validated | CONFIRMED |
| Feature ledger ready (3.2M rows) | CONFIRMED |
| EURUSD h15 features (243 RETAINED) | CONFIRMED |
| BigQuery data (370K+ rows) | CONFIRMED |
| Walk-forward splits (24) | CONFIRMED |
| Model output paths | CONFIRMED |

---

## PHASE 4 SCOPE

### Authorized Activities

1. **EURUSD h15 Pilot Training**
   - 3-model ensemble (LightGBM, XGBoost, CatBoost)
   - Walk-forward validation (24 splits)
   - Calibrated probability stacking
   - Confidence gating optimization

2. **SHAP Generation (USER MANDATE)**
   - Minimum 100,000 samples (BINDING)
   - Generate for all RETAINED features
   - Update feature ledger with SHAP values

3. **Performance Validation**
   - Target: 85-95% called accuracy
   - Coverage: 30-50%
   - Gating thresholds: τ=0.55 to τ=0.85

---

## MANDATE COMPLIANCE REQUIREMENTS

| Mandate | Requirement | Status |
|---------|-------------|--------|
| SHAP 100K+ | 100,000+ samples minimum | MUST COMPLY |
| Stability 50% | Use 50% threshold features | MUST COMPLY |
| Ledger 100% | Update ledger with results | MUST COMPLY |

---

## DELIVERABLES

1. **Trained Models**: EURUSD h15 ensemble (3 base + 1 meta)
2. **SHAP Values**: 100K+ samples for all RETAINED features
3. **Gating Curves**: Accuracy vs coverage at each threshold
4. **Training Report**: Performance summary with validation results

---

## CHECKPOINTS

Report to CE at:
1. Base model training complete (individual AUCs)
2. Meta-learner training complete (ensemble metrics)
3. SHAP generation complete (100K+ validated)
4. Full results ready (gating curves, final metrics)

---

## CONSTRAINTS

- Cost: Stay within training budget estimates
- Time: No specific deadline (quality over speed)
- Scope: EURUSD h15 only (other pairs after validation)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:20
**Status**: PHASE 4 AUTHORIZED - PROCEED WITH EURUSD TRAINING
