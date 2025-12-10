# CE Directive: Prepare Steps 7-8 While Step 6 Processes

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 21:35 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **MEDIUM**
**Subject**: Productive Tasks During Step 6 Processing

---

## DIRECTIVE: PREPARATION TASKS

While Step 6 (feature extraction) processes autonomously, BA shall prepare for subsequent pipeline stages.

---

## Task 1: Prepare Step 7 Configuration (HIGH)

**Stability Selection Parameters**

| Parameter | Value | Source |
|-----------|-------|--------|
| Threshold | 50% | USER APPROVED 2025-12-09 |
| Folds | 5 | roadmap_v2.json |
| Seeds | 3 | roadmap_v2.json |
| Input | `data/features/{pair}_merged_features.parquet` | Step 6 output |

**Verify:**
- [ ] `feature_selection_robust.py` can read from parquet
- [ ] Parameters match roadmap specification
- [ ] Output path configured: `intelligence/stable_features_{pair}_h{horizon}.json`

---

## Task 2: Prepare Step 8 Configuration (MEDIUM)

**Training Parameters**

| Parameter | Value |
|-----------|-------|
| Base models | LightGBM, XGBoost, CatBoost |
| Meta-learner | LogisticRegression |
| Calibration | Platt scaling |
| Feature source | Stability selection JSON |

**Verify:**
- [ ] `stack_calibrated.py` loads features from JSON (not hardcoded)
- [ ] `load_from_merged_parquet()` working correctly
- [ ] Output path: `models/{pair}/h{horizon}_ensemble_v3.joblib`

---

## Task 3: Monitor Disk Usage (LOW)

Track disk consumption during Step 6:

```bash
df -h /home/micha/bqx_ml_v3/data/features/
du -sh /tmp/feature_chunks/
```

**Alert Threshold:** If disk exceeds 80%, report to CE.

---

## Task 4: Document Pipeline Changes (LOW)

Update documentation to reflect new pipeline flow:

| File | Update |
|------|--------|
| `docs/BQX_ML_V3_PIPELINE_ARCHITECTURE.md` | New data flow |
| README.md | Update if pipeline section exists |

---

## Reporting

No report required unless:
- Disk threshold exceeded
- Configuration issues found
- Step 6 errors occur

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 21:35 UTC
