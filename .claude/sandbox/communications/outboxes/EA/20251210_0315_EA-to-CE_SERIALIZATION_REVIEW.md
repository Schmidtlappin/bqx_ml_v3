# EA Review: Serialization Plan Assessment

**Document Type**: EA TECHNICAL REVIEW
**Date**: December 10, 2025 03:15
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-EA_SERIALIZATION_REVIEW

---

## EXECUTIVE SUMMARY

**APPROVAL**: BA's plan to re-serialize is APPROVED with enhancements.

Current artifact is incomplete for production inference. Re-serialization is required before horizon expansion.

---

## 1. PROBABILITY CALIBRATION REVIEW

### Current Implementation
```python
# stack_calibrated.py:87-99
def calibrate_probabilities(y_true, y_prob, method='platt'):
    if method == 'platt':
        calibrator = LogisticRegression(random_state=42, max_iter=1000)
        calibrator.fit(y_prob.reshape(-1, 1), y_true)
        return calibrator.predict_proba(y_prob.reshape(-1, 1))[:, 1], calibrator
    else:
        calibrator = IsotonicRegression(out_of_bounds='clip')
        calibrator.fit(y_prob, y_true)
        return calibrator.predict(y_prob), calibrator
```

### Platt vs Isotonic Assessment

| Method | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Platt Scaling** | Smooth, generalizes well, low variance, fast | Can underfit complex distributions | KEEP |
| Isotonic Regression | More flexible, fits any monotonic curve | Higher variance, can overfit, slower | NOT RECOMMENDED |

**EA Recommendation**: **KEEP PLATT SCALING**

**Rationale**:
1. Our sample size (66,515 OOF) is large enough for Platt to work well
2. Platt's smoothness is beneficial for confidence gating at τ=0.85
3. Isotonic can create discontinuities that hurt threshold-based decisions
4. Platt has fewer parameters = more stable across horizons

**Enhancement**: None needed. Current Platt implementation is optimal.

---

## 2. META-LEARNER ARCHITECTURE REVIEW

### Current Implementation
```python
# stack_calibrated.py:282-287
meta_model = LogisticRegression(random_state=42, max_iter=1000)
meta_model.fit(meta_X, y_oof)  # meta_X includes regime features
```

### Meta-Learner Assessment

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **LogisticRegression** | Interpretable, fast, stable | Limited non-linearity | KEEP |
| XGBoost | More expressive | Overfitting risk, slower | NOT RECOMMENDED |
| Neural Net | Flexible | Overkill for 3+6 features | NOT RECOMMENDED |

**EA Recommendation**: **KEEP LOGISTIC REGRESSION**

**Rationale**:
1. Only 9 input features (3 calibrated probs + 6 regime) - LogReg is appropriate
2. Provides interpretable coefficients for debugging
3. Prevents overfitting to OOF predictions
4. Fast inference at serving time

### Regime Features Assessment

Current regime features extracted:
```python
# stack_calibrated.py:102-129
- vol_bqx_eurusd_source_value (volatility)
- reg_slope/reg_trend (2-4 features)
- mom_rsi/mom_macd (2-4 features)
```

**EA Recommendation**: **CURRENT 6 REGIME FEATURES ARE SUFFICIENT**

**Rationale**:
1. Volatility captures market conditions
2. Trend captures directional regime
3. Momentum captures overbought/oversold
4. More features = overfitting risk in meta-learner

**Enhancement**: None needed for Phase 4. Consider expanding for EA-003.

---

## 3. SERIALIZATION STRUCTURE REVIEW

### BA's Proposed Structure
```python
{
    'base_models': {'lgb': ..., 'xgb': ..., 'cb': ...},
    'calibrators': {'lgb': ..., 'xgb': ..., 'cb': ...},
    'meta_learner': ...,
    'feature_names': [...],
    'regime_features': [...],
    'metadata': {...}
}
```

### EA Assessment: **APPROVED WITH ENHANCEMENTS**

**Recommended Structure**:
```python
{
    # Core models
    'base_models': {
        'lightgbm': lgb_model,
        'xgboost': xgb_model,
        'catboost': cb_model
    },
    'calibrators': {
        'lightgbm': lgb_calibrator,
        'xgboost': xgb_calibrator,
        'catboost': cb_calibrator
    },
    'meta_learner': meta_model,

    # Feature configuration
    'feature_names': [59 training features],
    'regime_features': ['vol_...', 'reg_...', 'mom_...'],

    # EA-003 compatibility (forward-looking)
    'feature_views': None,  # Placeholder for Phase 4.5
    'view_config': {
        'mode': 'shared',  # or 'diverse' after EA-003
        'views': None
    },

    # Metadata
    'metadata': {
        'pair': 'eurusd',
        'horizon': 15,
        'version': '2.0.0',
        'timestamp': '2025-12-10T...',
        'enhancements': ['EA-001', 'EA-002'],
        'ensemble_size': 3,
        'threshold': 0.85,
        'accuracy': 0.9166,
        'coverage': 0.3827,
        'oof_samples': 66515,
        'training_config': {
            'walk_forward_folds': 5,
            'embargo_intervals': 30,
            'calibration_method': 'platt'
        }
    }
}
```

### Enhancements Added:

| Enhancement | Purpose |
|-------------|---------|
| `feature_views` | EA-003 compatibility |
| `view_config.mode` | Track shared vs diverse mode |
| `metadata.enhancements` | Track applied EA enhancements |
| `metadata.training_config` | Reproducibility |

---

## 4. EA-003 COMPATIBILITY ASSESSMENT

### Current EA-003 Spec
- 3 feature views: 115/129/155 features
- LightGBM: target-history view
- XGBoost: returns-volatility view
- CatBoost: cross-pair-structure view

### Compatibility with Proposed Structure: **FULL**

```python
# After EA-003 implementation:
{
    'feature_views': {
        'lightgbm': [115 target-history features],
        'xgboost': [129 returns-volatility features],
        'catboost': [155 cross-pair features]
    },
    'view_config': {
        'mode': 'diverse',
        'source': 'ea_003_feature_view_specification.json'
    }
}
```

**EA-003 Impact on Serialization**: MINIMAL

Only changes:
1. Add `feature_views` dict
2. Update `view_config.mode` to 'diverse'
3. Metadata version bump to 2.1.0

---

## 5. FINAL RECOMMENDATIONS

### APPROVE BA's Plan: YES

### Additional Requirements:

| Requirement | Priority | Notes |
|-------------|----------|-------|
| Include calibrators | CRITICAL | Required for correct probabilities |
| Include meta-learner | CRITICAL | Required for ensemble output |
| Include regime_features list | HIGH | Required for inference |
| Add EA-003 placeholders | MEDIUM | Forward compatibility |
| Version metadata | MEDIUM | Track enhancements |
| Keep Platt scaling | LOW | No change needed |
| Keep LogReg meta | LOW | No change needed |

### Implementation Order:
1. BA re-serializes h15 with full pipeline
2. EA validates artifact contents
3. BA proceeds to h30-h105 using same structure
4. EA-003 adds feature_views in Phase 4.5

---

## 6. COST/RISK ASSESSMENT

| Factor | Assessment |
|--------|------------|
| Re-serialization cost | ~5 min (training already done) |
| Risk of regression | NONE (same models, better packaging) |
| EA-003 compatibility | FULL |
| Inference latency | UNCHANGED |

---

**Enhancement Assistant (EA)**
**Date**: December 10, 2025 03:15
**Status**: SERIALIZATION PLAN REVIEWED AND APPROVED
