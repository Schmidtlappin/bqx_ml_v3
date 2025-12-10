# CE Directive: Re-Serialize h15 with Full Pipeline

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:20
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH

---

## CONTEXT

EA reviewed and APPROVED serialization plan with enhancements. Proceed with re-serialization.

---

## REQUIRED ARTIFACT STRUCTURE

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

    # EA-003 compatibility (placeholders)
    'feature_views': None,
    'view_config': {
        'mode': 'shared',
        'views': None
    },

    # Metadata
    'metadata': {
        'pair': 'eurusd',
        'horizon': 15,
        'version': '2.0.0',
        'timestamp': '<ISO timestamp>',
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

---

## CHECKLIST

| Item | Action |
|------|--------|
| Base models (LGB, XGB, CB) | Include (already have) |
| Calibrators (3x Platt) | **ADD** |
| Meta-learner (LogReg) | **ADD** |
| feature_names | Include |
| regime_features | **ADD** |
| feature_views placeholder | **ADD** |
| view_config | **ADD** |
| metadata (enhanced) | **ADD** |

---

## DELIVERABLES

1. Re-serialize to `models/eurusd/h15_ensemble_v2.joblib`
2. Upload to GCS: `gs://bqx-ml-v3-models/models/eurusd/h15_ensemble_v2.joblib`
3. Run inference test (load, predict, verify calibrated output)
4. Submit completion report

---

## VALIDATION

After completion, EA will validate artifact contents match specification.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:20
**Status**: RE-SERIALIZATION AUTHORIZED
