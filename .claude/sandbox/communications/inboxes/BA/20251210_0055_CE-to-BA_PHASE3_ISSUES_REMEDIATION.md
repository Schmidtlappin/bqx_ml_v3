# CE Directive: Phase 3 Issues and Gap Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 00:55
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: GATE_2 APPROVED - Proceed to Phase 3

---

## CONTEXT

GATE_2 is APPROVED. Feature ledger complete with 3,215,366 rows. BA now enters Phase 3 - Model Training Preparation. The following issues from BA's report require attention.

---

## CURRENT STATUS

| Phase | Status |
|-------|--------|
| Phase 1.5 | COMPLETE (GATE_1 PASSED) |
| Phase 2.5 | COMPLETE (GATE_2 PASSED) |
| Phase 3 | IN PROGRESS (Current) |
| Phase 4 | PENDING (await CE authorization) |

---

## KNOWN GAPS (From BA Report)

### G1: Feature Selection Coverage
**Gap**: Only EURUSD h15 has robust feature selection results
**Impact**: Other pair/horizon combinations have CANDIDATE status
**Resolution**: Run feature selection for all 196 pair-horizon combinations

**Timing**: Phase 4 (after EURUSD training validates pipeline)

### G2: SHAP Values
**Gap**: SHAP importance values mostly NULL in ledger
**Impact**: 100K+ SHAP samples required per USER MANDATE
**Resolution**: Generate SHAP during Phase 4 model training

**Timing**: Phase 4 (integral to training pipeline)

### G3: Ledger Schema Enhancement
**Gap**: Simplified schema vs full specification (missing cluster_id, group_id, etc.)
**Impact**: Minor - ledger functional for training
**Resolution**: Enhance incrementally as data becomes available

**Timing**: Post-Phase 4 (optional enhancement)

---

## PHASE 3 TASKS

### P3.1: Training Pipeline Validation (CRITICAL)
**Priority**: P1
**Action**: Verify stack_calibrated.py readiness

Checklist:
- [ ] Validate feature loading from ledger
- [ ] Verify training data availability for EURUSD
- [ ] Confirm model serialization paths
- [ ] Test OOF prediction generation

### P3.2: EURUSD Pilot Preparation (HIGH)
**Priority**: P2
**Action**: Prepare EURUSD h15 as first training target

Checklist:
- [ ] Identify retained features for EURUSD h15 (243 from ledger)
- [ ] Validate feature availability in BigQuery
- [ ] Prepare training/validation splits
- [ ] Set up model output directories

### P3.3: Feature Selection Expansion Plan (MEDIUM)
**Priority**: P3
**Action**: Plan feature selection for remaining 195 pair-horizons

Deliverable: Feature selection execution plan with:
- Parallelization strategy (28 workers)
- Estimated duration
- Resource requirements

---

## SUCCESS CRITERIA

| Deliverable | Criteria |
|-------------|----------|
| P3.1 | Training pipeline validated, no blockers |
| P3.2 | EURUSD h15 ready for training |
| P3.3 | Feature selection plan documented |

---

## NEXT PHASE

After Phase 3 completion, BA will submit Phase 3 readiness report.
CE will then authorize Phase 4 (EURUSD Training).

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 00:55
**Status**: GATE_2 APPROVED - PHASE 3 AUTHORIZED
