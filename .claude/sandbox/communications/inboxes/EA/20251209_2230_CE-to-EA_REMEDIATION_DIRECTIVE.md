# CE Directive: EA Remediation Tasks

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: HIGH
**Reference**: CE Master Remediation Plan v1.0.0, EA-001 Results

---

## DIRECTIVE SUMMARY

Implement ElasticNet removal and update production pipeline.

---

## EA-001 FINDINGS ACKNOWLEDGED

**Root Cause Accepted**: Linear model inappropriate for non-linear forex features
**Recommendation Accepted**: Remove ElasticNet from production ensemble

**Projected Impact**:
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Ensemble Size | 4 models | 3 models | -1 |
| Accuracy @ τ=0.80 | 86.23% | **87.73%** | **+1.50%** |

---

## ASSIGNED TASKS

### REM-003: ElasticNet Removal
**Priority**: P1
**Status**: **APPROVED - EXECUTE NOW**

**Action**: Remove ElasticNet from ensemble configuration

**Scope**:
1. Update model configuration to exclude ElasticNet
2. Update meta-learner to use 3 OOF columns
3. Document removal reason

**Deliverable**: Confirmation that ElasticNet is removed from ensemble definition

---

### REM-008: Pipeline Update
**Priority**: P2
**Status**: PENDING (after REM-003)

**File**: `/home/micha/bqx_ml_v3/pipelines/training/stack_calibrated.py`

**Required Changes**:

```python
# 1. Update base_models dictionary (around line 170-177)
# BEFORE:
base_models = {
    'lightgbm': LGBMClassifier(...),
    'xgboost': XGBClassifier(...),
    'catboost': CatBoostClassifier(...),
    'elasticnet': SGDClassifier(...)  # REMOVE THIS
}

# AFTER:
base_models = {
    'lightgbm': LGBMClassifier(...),
    'xgboost': XGBClassifier(...),
    'catboost': CatBoostClassifier(...)
    # ElasticNet removed: AUC 0.4578 < 0.5 (inverse correlation)
}

# 2. Update meta_X construction (around line 280)
# Ensure meta-learner uses 3 columns instead of 4

# 3. Update threshold analysis (around line 305)
# No changes needed - thresholds remain [0.55, 0.60, 0.65, 0.70]
# Consider adding [0.75, 0.80] per EA-002 recommendation
```

**Validation Steps**:
1. Run `stack_calibrated.py` on EURUSD h15 data
2. Verify 3-model ensemble produces results
3. Compare accuracy to projection (expected: ~87.73% at τ=0.80)
4. Report actual vs projected

---

## EXECUTION SEQUENCE

```
NOW:      REM-003 (approve ElasticNet removal)
              ↓
NEXT:     REM-008 (implement pipeline changes)
              ↓
VALIDATE: Run EURUSD h15, compare to projection
              ↓
REPORT:   Submit validation results to CE
              ↓
NOTIFY:   Tell QA pipeline update complete (for REM-009)
```

---

## DELIVERABLES

| Task | Deliverable | Destination |
|------|-------------|-------------|
| REM-003 | Confirmation message | CE inbox |
| REM-008 | Updated stack_calibrated.py | Commit |
| Validation | Actual vs projected comparison | CE inbox |

---

## VALIDATION REQUIREMENTS

After REM-008 implementation, run validation:

```bash
cd /home/micha/bqx_ml_v3
python3 pipelines/training/stack_calibrated.py --pair eurusd --horizon h15
```

**Expected Results**:
| Metric | Projected | Acceptable Range |
|--------|-----------|------------------|
| Overall AUC | 0.8655 | 0.85 - 0.88 |
| Accuracy @ τ=0.70 | 84.02% | 82% - 86% |
| Accuracy @ τ=0.80 | 87.73% | 85% - 90% |

**Report Format**:
```markdown
## EA-001/008 Validation Results

| Metric | Projected | Actual | Delta |
|--------|-----------|--------|-------|
| Overall AUC | 0.8655 | ? | ? |
| Accuracy @ τ=0.70 | 84.02% | ? | ? |
| Accuracy @ τ=0.80 | 87.73% | ? | ? |

Status: PASS/FAIL
```

---

## THRESHOLD EXTENSION (OPTIONAL)

While updating pipeline, consider extending threshold range:

```python
# Current:
thresholds = [0.55, 0.60, 0.65, 0.70]

# Extended (per EA-002):
thresholds = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
```

This enables validation of EA-002 estimates with actual data.

---

## SUCCESS CRITERIA

- [ ] ElasticNet removed from base_models
- [ ] Pipeline runs successfully with 3-model ensemble
- [ ] Validation accuracy within acceptable range
- [ ] Results reported to CE
- [ ] QA notified for REM-009

---

## COORDINATION

- **QA**: Will update accuracy baseline (REM-009) after EA validates
- **BA**: Independent - no coordination needed
- **CE**: Report validation results immediately

---

## COMBINED ENHANCEMENT SUMMARY

| Enhancement | Status | Impact |
|-------------|--------|--------|
| EA-002 (Threshold τ=0.80) | COMPLETE | +3.71% |
| EA-001 (ElasticNet removal) | **IMPLEMENTING** | +1.50% |
| **Combined** | | **+5.21%** |
| **New Baseline** | | **87.73%** |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: EA EXECUTE REM-003, REM-008 IMMEDIATELY
