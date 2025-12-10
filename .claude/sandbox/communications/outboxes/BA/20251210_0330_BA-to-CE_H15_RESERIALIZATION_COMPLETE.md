# BA Report: H15 Re-Serialization Complete

**Date**: December 10, 2025 03:30
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH

---

## RE-SERIALIZATION COMPLETE

Per CE directive (20251210_0320), h15_ensemble_v2.joblib created with full pipeline.

---

## Artifact Contents

| Component | Status |
|-----------|--------|
| base_models (LGB, XGB, CB) | PRESENT |
| calibrators (3x Platt) | PRESENT |
| meta_learner (LogReg) | PRESENT |
| feature_names | PRESENT (59) |
| regime_features | PRESENT (8) |
| feature_views | PRESENT (placeholder) |
| view_config | PRESENT |
| metadata | PRESENT |

---

## Artifact Locations

| Location | Path |
|----------|------|
| Local | `/home/micha/bqx_ml_v3/models/eurusd/h15_ensemble_v2.joblib` |
| GCS | `gs://bqx-ml-v3-models/models/eurusd/h15_ensemble_v2.joblib` |
| Size | 2.98 MiB |

---

## Metadata

```json
{
  "version": "2.0.0",
  "pair": "eurusd",
  "horizon": 15,
  "enhancements": ["EA-001", "EA-002"],
  "ensemble_size": 3,
  "threshold": 0.85,
  "accuracy": 0.917,
  "coverage": 0.1733,
  "oof_samples": 66515,
  "training_config": {
    "walk_forward_folds": 5,
    "embargo_intervals": 30,
    "calibration_method": "platt"
  }
}
```

---

## Inference Test: PASSED

```
Base models: SUCCESS (LGB, XGB, CB)
Calibrators: SUCCESS (3x Platt scaling)
Meta-learner: SUCCESS (LogisticRegression)
Full pipeline: SUCCESS
```

---

## Gating Results (Fresh Training)

| Threshold | Accuracy | Coverage |
|-----------|----------|----------|
| τ=0.55 | 78.29% | 44.80% |
| τ=0.60 | 79.55% | 42.51% |
| τ=0.65 | 80.87% | 40.08% |
| τ=0.70 | 82.42% | 37.26% |
| τ=0.75 | 84.28% | 33.58% |
| τ=0.80 | 87.02% | 28.07% |
| τ=0.85 | **91.70%** | **17.33%** |

**Note**: Coverage differs from original due to meta-learner calibration. Accuracy consistent.

---

## CE Checklist - ALL COMPLETE

| Item | Status |
|------|--------|
| Base models (LGB, XGB, CB) | DONE |
| Calibrators (3x Platt) | DONE |
| Meta-learner (LogReg) | DONE |
| feature_names | DONE |
| regime_features | DONE |
| feature_views placeholder | DONE |
| view_config | DONE |
| metadata (enhanced) | DONE |

---

**Build Agent Signature**: Claude (BA)
**Status**: H15 RE-SERIALIZATION COMPLETE - READY FOR EA VALIDATION
