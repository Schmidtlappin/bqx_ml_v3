# CE Work Plan: EA Forward Tasks

**Document Type**: CE WORK PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: HIGH

---

## Current Sprint Status

### Completed Tasks ✓

| Task | Status | Date |
|------|--------|------|
| EA-002 (Threshold testing) | **COMPLETE** | 2025-12-09 |
| EA-001 (ElasticNet analysis) | **COMPLETE** | 2025-12-09 |
| REM-003 (Removal approval) | **COMPLETE** | 2025-12-09 |
| REM-008 (Pipeline update) | **COMPLETE** | 2025-12-09 |

### Pending Tasks

| Task | Status | Decision |
|------|--------|----------|
| Validation Run | PENDING | **PROCEED IMMEDIATELY** |

---

## VALIDATION DECISION

**DECISION: Option 1 - PROCEED IMMEDIATELY**

Run validation on EURUSD h15 to confirm projections.

### Validation Command

```bash
cd /home/micha/bqx_ml_v3
timeout 900 python3 pipelines/training/stack_calibrated.py eurusd 15
```

### Expected Results

| Metric | Projected | Acceptable Range |
|--------|-----------|------------------|
| Overall AUC | 0.8655 | 0.85 - 0.88 |
| Accuracy @ τ=0.70 | 84.02% | 82% - 86% |
| Accuracy @ τ=0.80 | 87.73% | 85% - 90% |

### Report Format

```markdown
## EA Validation Results

### Execution
- Command: python3 pipelines/training/stack_calibrated.py eurusd 15
- Duration: X minutes
- Status: SUCCESS/FAIL

### Results vs Projection

| Metric | Projected | Actual | Delta | Status |
|--------|-----------|--------|-------|--------|
| Overall AUC | 0.8655 | ? | ? | PASS/FAIL |
| Accuracy @ τ=0.70 | 84.02% | ? | ? | PASS/FAIL |
| Accuracy @ τ=0.80 | 87.73% | ? | ? | PASS/FAIL |

### Gating Curve (Extended)

| Threshold | Accuracy | Coverage |
|-----------|----------|----------|
| τ=0.55 | ? | ? |
| τ=0.60 | ? | ? |
| τ=0.65 | ? | ? |
| τ=0.70 | ? | ? |
| τ=0.75 | ? | ? |
| τ=0.80 | ? | ? |
| τ=0.85 | ? | ? |

### Overall Status: PASS/FAIL
```

---

## Execution Plan

```
NOW:        Run validation (10-15 minutes)
                │
                └── Report results to CE

AFTER:      Notify QA for REM-009 (accuracy baseline update)
                │
                └── QA updates roadmap_v2.json

FUTURE:     EA-003 (after GATE_1)
```

---

## After Validation

### If PASS
1. Report success to CE
2. Notify QA to proceed with REM-009
3. Await GATE_1 completion
4. Prepare EA-003 specification

### If FAIL
1. Report failure details to CE
2. Investigate discrepancy
3. Propose remediation
4. Do NOT notify QA until resolved

---

## Future Work (Post-GATE_1)

### EA-003: Feature-View Diversity

| Task | Description |
|------|-------------|
| Specification | Create detailed feature-view assignments |
| Submission | Submit to CE for approval |
| Implementation | BA implements after approval |

**Feature Views** (draft):
```
LightGBM:   Target-history (lags, rolling stats) - ~200 features
XGBoost:    Returns/volatility (multi-horizon, ATR, range) - ~200 features
CatBoost:   Cross-pair/microstructure (spreads, correlations) - ~200 features
```

**Expected Impact**: +1-2% additional accuracy

### Phase 4: Hyperparameter Optimization

| Task | Description |
|------|-------------|
| Analysis | Review default parameters |
| Tuning | Propose optimized settings |
| Validation | Test on subset |

### Phase 5: Performance Monitoring

| Task | Description |
|------|-------------|
| Trend Tracking | Monitor accuracy across pairs |
| Optimization | Identify improvement opportunities |
| Reporting | Monthly enhancement reports |

---

## Accuracy Trajectory

| Stage | Accuracy | Status |
|-------|----------|--------|
| Baseline (τ=0.70, 4 models) | 82.52% | Historical |
| EA-002 (τ=0.80) | 86.23% | Achieved |
| EA-001 (3 models) | 87.73% | **Validating** |
| EA-003 (feature diversity) | 88-90% | Future |
| **Target** | 85-95% | **On Track** |

---

## Ongoing Responsibilities

| Frequency | Task |
|-----------|------|
| Per Enhancement | Full analysis and projection |
| Weekly | Monitor for optimization opportunities |
| Per Phase | Enhancement proposal review |

---

## Success Criteria

### Current Sprint

- [ ] Validation run completes
- [ ] Results within acceptable range
- [ ] QA notified for REM-009

### Post-GATE_1

- [ ] EA-003 specification ready
- [ ] Performance tracking active

---

## Coordination

| Agent | Coordination Point |
|-------|-------------------|
| QA | Notify after validation for REM-009 |
| BA | No direct coordination |
| CE | Report validation results |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: EA PROCEED WITH VALIDATION IMMEDIATELY
