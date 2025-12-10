# GATE_3 Validation Report

**Document Type**: GATE VALIDATION REPORT
**Date**: December 10, 2025 02:40
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-QA_GATE3_VALIDATION_REQUEST (02:35)

---

## GATE_3 VERDICT: PASS

All 6 criteria met. EURUSD h15 training pipeline validated.

---

## Criterion Validation

### 1. Called Accuracy ≥85%

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| Called accuracy (τ=0.85) | ≥85% | **91.66%** | **PASS** |

**Evidence**: `calibrated_stack_eurusd_h15.json` line 57
```json
"tau_85": {"accuracy": 0.9166, "coverage": 0.3827}
```

---

### 2. Coverage 30-50%

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| Coverage (τ=0.85) | 30-50% | **38.27%** | **PASS** |

**Evidence**: `calibrated_stack_eurusd_h15.json` line 58
```json
"tau_85": {"coverage": 0.3827, "n_signals": 25457}
```

---

### 3. SHAP Samples 100K+ (USER MANDATE)

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| SHAP sample size | ≥100,000 | **100,000** | **PASS** |
| Mandate compliant | true | **true** | **PASS** |

**Evidence**: `shap_eurusd_h15.json` lines 5-6
```json
"shap_sample_size": 100000,
"mandate_compliant": true
```

---

### 4. TreeSHAP All 3 Models

| Model | SHAP Type | Present | Status |
|-------|-----------|---------|--------|
| LightGBM | TreeSHAP | lgb_shap | **PASS** |
| XGBoost | TreeSHAP | xgb_shap | **PASS** |
| CatBoost | TreeSHAP | cb_shap | **PASS** |

**Evidence**: `shap_eurusd_h15.json` - All 59 features have SHAP values for all 3 models:
```json
"reg_slope_45": {
  "ensemble_shap": 0.590,
  "lgb_shap": 0.590,
  "xgb_shap": 0.535,
  "cb_shap": 0.646
}
```

---

### 5. Gating Curves Documented

| Threshold | Accuracy | Coverage | Status |
|-----------|----------|----------|--------|
| τ=0.55 | 78.16% | 95.30% | **DOCUMENTED** |
| τ=0.60 | 79.48% | 90.36% | **DOCUMENTED** |
| τ=0.65 | 80.87% | 84.99% | **DOCUMENTED** |
| τ=0.70 | 82.52% | 78.85% | **DOCUMENTED** |
| τ=0.75 | 84.58% | 70.87% | **DOCUMENTED** |
| τ=0.80 | 87.24% | 59.68% | **DOCUMENTED** |
| τ=0.85 | 91.66% | 38.27% | **DOCUMENTED** |

**Evidence**: `calibrated_stack_eurusd_h15.json` lines 25-61
```
Status: PASS - All thresholds τ=0.55 to τ=0.85 documented
```

---

### 6. Model Artifacts to GCS

| Artifact | Expected | Actual | Status |
|----------|----------|--------|--------|
| h15_ensemble.joblib | ~3 MB | **2.98 MiB** | **PASS** |
| GCS path | gs://bqx-ml-v3-models/models/eurusd/ | **EXISTS** | **PASS** |

**Evidence**: gsutil ls output
```
3126130  2025-12-09T23:27:02Z  gs://bqx-ml-v3-models/models/eurusd/h15_ensemble.joblib
```

---

## Summary

| # | Criterion | Required | Actual | Verdict |
|---|-----------|----------|--------|---------|
| 1 | Called accuracy | ≥85% | 91.66% | **PASS** |
| 2 | Coverage | 30-50% | 38.27% | **PASS** |
| 3 | SHAP samples | ≥100K | 100,000 | **PASS** |
| 4 | TreeSHAP all models | 3/3 | 3/3 | **PASS** |
| 5 | Gating curves | Documented | 7 thresholds | **PASS** |
| 6 | GCS artifacts | Present | 2.98 MiB | **PASS** |

---

## GATE_3 RESULT

```
╔═══════════════════════════════════════════════╗
║           GATE_3: PASSED                      ║
║                                               ║
║  EURUSD h15 Training Pipeline VALIDATED       ║
║  6/6 criteria met                             ║
║                                               ║
║  Recommended: Proceed to Phase 4 expansion    ║
╚═══════════════════════════════════════════════╝
```

---

## Recommendation

**Phase 4 Expansion APPROVED** based on:
1. Performance exceeds targets (91.66% > 85%)
2. Coverage within range (38.27% in 30-50%)
3. USER MANDATE compliant (100K SHAP samples)
4. All model types have TreeSHAP values
5. Comprehensive gating curves available
6. Model artifacts serialized to GCS

**Next Step**: Scale to remaining 6 horizons (h30, h45, h60, h75, h90, h105) for EURUSD.

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Report Time**: December 10, 2025 02:40
**Status**: GATE_3 VALIDATION COMPLETE - **PASSED**
