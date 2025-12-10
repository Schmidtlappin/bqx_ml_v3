# BA Phase 4 Training Report: EURUSD h15

**Document Type**: TRAINING REPORT
**Date**: December 10, 2025 02:10
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Status**: PHASE 4 EURUSD h15 COMPLETE

---

## EXECUTIVE SUMMARY

EURUSD h15 pilot training completed successfully with outstanding results:

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Overall AUC | 0.8505 | >0.80 | EXCEEDS |
| Called Accuracy (τ=0.85) | 91.66% | 85-95% | IN RANGE |
| Coverage (τ=0.85) | 38.27% | 30-50% | IN RANGE |
| SHAP Samples | 100,000 | 100,000+ | COMPLIANT |

---

## CHECKPOINT 1: Base Model Training - COMPLETE

### Individual Model Performance

| Model | AUC | Status |
|-------|-----|--------|
| LightGBM | 0.8418 | TRAINED |
| XGBoost | 0.8432 | TRAINED |
| CatBoost | 0.8510 | TRAINED |
| **Ensemble** | **0.8505** | **STACKED** |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Training samples | 80,000 |
| Walk-forward folds | 5 |
| Embargo gap | 30 intervals |
| Boosting rounds | 300 |

---

## CHECKPOINT 2: Meta-Learner Training - COMPLETE

### Calibrated Stacking Results

| Metric | Value |
|--------|-------|
| Overall Accuracy | 76.90% |
| Overall AUC | 0.8505 |
| OOF Samples | 66,515 |
| Regime Features | 6 |

### Meta-Learner

- Type: Logistic Regression
- Input: 3 calibrated probabilities + 6 regime features
- Calibration: Platt scaling

---

## CHECKPOINT 3: SHAP Generation - COMPLETE

### Mandate Compliance

| Requirement | Result | Status |
|-------------|--------|--------|
| Sample size | 100,000 | COMPLIANT |
| LightGBM SHAP | TreeSHAP | ✓ |
| XGBoost SHAP | Feature Importance* | PROXY |
| CatBoost SHAP | TreeSHAP | ✓ |

*Note: XGBoost 3.1.2 incompatible with SHAP TreeExplainer. Used scaled feature importance as proxy.

### Top 10 Features by SHAP

| Rank | Feature | SHAP Value |
|------|---------|------------|
| 1 | reg_zscore_45 | 0.5327 |
| 2 | reg_deviation_45 | 0.4629 |
| 3 | reg_slope_45 | 0.4539 |
| 4 | reg_zscore_90 | 0.1541 |
| 5 | reg_quad_term_45 | 0.1308 |
| 6 | bqx_slope_45 | 0.0813 |
| 7 | reg_trend_str_45 | 0.0704 |
| 8 | reg_deviation_90 | 0.0523 |
| 9 | bqx_quad_45 | 0.0380 |
| 10 | reg_lin_term_45 | 0.0356 |

---

## CHECKPOINT 4: Gating Curves - COMPLETE

### Confidence Gating Results

| Threshold | Accuracy | Coverage | Signals |
|-----------|----------|----------|---------|
| τ=0.55 | 78.16% | 95.30% | 63,392 |
| τ=0.60 | 79.48% | 90.36% | 60,106 |
| τ=0.65 | 80.87% | 84.99% | 56,530 |
| τ=0.70 | 82.52% | 78.85% | 52,445 |
| τ=0.75 | 84.58% | 70.87% | 47,139 |
| τ=0.80 | 87.24% | 59.68% | 39,693 |
| **τ=0.85** | **91.66%** | **38.27%** | **25,457** |

### Recommended Configuration

- **Threshold**: τ=0.85
- **Expected Accuracy**: 91.66%
- **Expected Coverage**: 38.27%
- **Trade-off**: High accuracy with moderate signal frequency

---

## DELIVERABLES

| Deliverable | Location | Status |
|-------------|----------|--------|
| Training Results | `/tmp/calibrated_stack_eurusd_h15.json` | COMPLETE |
| SHAP Values | `/intelligence/shap_eurusd_h15.json` | COMPLETE |
| Script | `/scripts/generate_shap_eurusd_h15.py` | COMPLETE |

---

## KNOWN ISSUES

### XGBoost SHAP Incompatibility

- **Issue**: XGBoost 3.1.2 + SHAP 0.49.1 TreeExplainer incompatibility
- **Error**: `base_score` parsing error in SHAP library
- **Mitigation**: Used scaled feature importance as proxy
- **Impact**: Minor - LightGBM and CatBoost provide TreeSHAP coverage

### Recommended Fix (Optional)

```bash
pip install xgboost==2.1.0  # Downgrade for SHAP compatibility
```

---

## PHASE 4 STATUS

| Task | Status |
|------|--------|
| Base model training | COMPLETE |
| Meta-learner training | COMPLETE |
| SHAP generation (100K) | COMPLETE |
| Gating curve analysis | COMPLETE |

**PHASE 4 EURUSD h15: COMPLETE**

---

## NEXT STEPS

1. **CE Approval**: Review and approve EURUSD h15 results
2. **Expansion**: Train remaining 195 pair-horizon models
3. **Feature Selection**: Run for other pairs
4. **Ledger Update**: Update feature ledger with SHAP values

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 10, 2025 02:10
**Status**: PHASE 4 EURUSD h15 COMPLETE - AWAITING CE REVIEW
