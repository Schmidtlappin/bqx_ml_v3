# CE Forward Work Plan - All Agents

**Document Type**: CE MASTER WORK PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**Status**: **ARCHIVED** - Phase 1.5 Complete, All Gates Passed
**Version**: 1.1.0
**Archived**: December 10, 2025

---

## Executive Summary

This document outlines the forward work plan for all agents (BA, QA, EA) through GATE_1 completion and beyond.

**Final Status**: Phase 1.5 COMPLETE (219/219 tables)
**Actual Accuracy**: 91.70% at τ=0.85
**Gates Passed**: GATE_1, GATE_2, GATE_3 (all PASSED)
**Current Phase**: Phase 2.5 (Full Feature Universe Testing)

---

## Timeline Overview

```
NOW ─────────────────────────────────────────────────────────────────────►

Phase 1.5                    GATE_1              Phase 2.5
├── BA: VAR/MKT (16 tables)    │                 ├── Feature Ledger
├── EA: Pipeline update        │                 ├── Full universe testing
├── QA: Documentation          │                 └── 28-pair expansion
│                              │
└── 16 tables remaining        └── VALIDATION

```

---

## PHASE 1: Current Sprint (Complete Phase 1.5)

### BA Work Plan

| Priority | Task | Description | Deliverable | Dependencies |
|----------|------|-------------|-------------|--------------|
| P1.1 | VAR Tables | Create 8 VAR tables | 8 tables in BQ | None |
| P1.2 | MKT Tables | Create 8 MKT tables | 8 tables in BQ | None |
| P1.3 | 50% Report | Progress at 8/16 | Status message | After 8 tables |
| P1.4 | Completion Report | Final status | Completion message | After 16 tables |

**Execution Order**:
```
VAR tables (parallel) ──┬── 50% report ──┬── Completion report
MKT tables (parallel) ──┘                │
                                         └── Notify QA for GATE_1
```

**Specific Tables**:
```
VAR (8):
├── var_agg_idx_usd, var_agg_bqx_usd
├── var_align_idx_usd, var_align_bqx_usd
└── var_lag_idx_cad, var_lag_idx_chf, var_lag_bqx_jpy, var_lag_bqx_nzd

MKT (8):
├── mkt_vol, mkt_vol_bqx
├── mkt_dispersion, mkt_dispersion_bqx
├── mkt_regime, mkt_regime_bqx
└── mkt_sentiment, mkt_sentiment_bqx
```

---

### QA Work Plan

| Priority | Task | Description | Deliverable | Dependencies |
|----------|------|-------------|-------------|--------------|
| ~~P2.1~~ | ~~REM-004~~ | ~~Roadmap CSI count~~ | ~~Updated roadmap~~ | **COMPLETE** |
| ~~P2.2~~ | ~~REM-005~~ | ~~Gap reconciliation~~ | ~~Consistent counts~~ | **COMPLETE** |
| P2.3 | REM-007 | GATE_1 pre-flight | Validation report | BA completion |
| P2.4 | REM-009 | Accuracy baseline | Updated roadmap | EA completion |
| P3.1 | REM-006 | F3b cleanup | Cleanup report | After GATE_1 |
| P3.2 | T11 | Weekly audit protocol | Protocol document | After GATE_1 |

**Execution Order**:
```
REM-004, REM-005 ── COMPLETE
                        │
Wait for BA ────────────┼── REM-007 (GATE_1 validation)
                        │
Wait for EA ────────────┼── REM-009 (accuracy baseline)
                        │
After GATE_1 ───────────┴── REM-006 (F3b cleanup)
                            T11 (weekly audit)
```

**GATE_1 Checklist** (REM-007):
```
□ Table counts: CSI=144, VAR=63, MKT=12, Total=219
□ Schema compliance: partitioned, clustered
□ Row count validation: 10% sampling
□ Documentation alignment: all files consistent
□ Cost verification: within budget
```

---

### EA Work Plan

| Priority | Task | Description | Deliverable | Dependencies |
|----------|------|-------------|-------------|--------------|
| P1.1 | REM-003 | Approve ElasticNet removal | Confirmation | **APPROVED** |
| P1.2 | REM-008 | Pipeline update | Updated stack_calibrated.py | None |
| P1.3 | Validation | Run EURUSD h15 | Validation report | REM-008 |
| P2.1 | Notify QA | Pipeline complete | Message to QA | Validation |
| P3.1 | EA-003 Spec | Feature-view diversity | Specification doc | After GATE_1 |

**Execution Order**:
```
REM-003 (approved) ─── REM-008 (implement) ─── Validation ─── Notify QA
                                                                │
                                                                └── QA updates accuracy baseline
```

**Pipeline Changes**:
```python
# stack_calibrated.py modifications:
1. Remove ElasticNet from base_models
2. Update meta_X to 3 columns
3. Add extended thresholds [0.75, 0.80, 0.85]
```

**Validation Criteria**:
```
Expected:
├── Overall AUC: 0.8655 (acceptable: 0.85-0.88)
├── Accuracy @ τ=0.70: 84.02% (acceptable: 82-86%)
└── Accuracy @ τ=0.80: 87.73% (acceptable: 85-90%)
```

---

## PHASE 2: GATE_1 Validation

### Gate Criteria

| Criterion | Target | Owner | Validation |
|-----------|--------|-------|------------|
| Table Count | 219 | QA | BQ query |
| Schema Compliance | 100% | QA | Spot check |
| Row Count | >0 all tables | QA | Sampling |
| Documentation | Aligned | QA | File review |
| Accuracy | ≥85% | EA | Pipeline run |
| Cost | <$277/mo | QA | Dashboard |

### GATE_1 Process

```
BA Complete ──► QA Pre-flight ──► CE Review ──► GATE_1 PASS/FAIL
                    │
                    ├── If PASS: Proceed to Phase 2.5
                    └── If FAIL: Remediation loop
```

---

## PHASE 3: Post-GATE_1 (Phase 2.5 and Beyond)

### BA Future Work

| Phase | Task | Description |
|-------|------|-------------|
| 2.5 | Feature Ledger | Generate 1,269,492 ledger rows |
| 4 | Training Pipeline | Train 784 models (28 pairs × 7 horizons × 4 ensemble) |
| 5 | Evaluation | Validate all models against targets |

### QA Future Work

| Phase | Task | Description |
|-------|------|-------------|
| 2.5 | GATE_2 | Ledger 100% coverage validation |
| 4 | Model Validation | Accuracy verification per model |
| 5 | Production Readiness | Final audit |

### EA Future Work

| Phase | Task | Description |
|-------|------|-------------|
| 2.5 | EA-003 | Feature-view diversity implementation |
| 4 | Hyperparameter | Tuning recommendations |
| 5 | Performance | Optimization proposals |

---

## Dependency Graph

```
                    ┌─────────────────────────────────────┐
                    │           PHASE 1.5                  │
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
   ┌─────────┐               ┌─────────────┐              ┌─────────┐
   │   BA    │               │     QA      │              │   EA    │
   │ VAR/MKT │               │ REM-004/005 │              │ REM-003 │
   │16 tables│               │  COMPLETE   │              │APPROVED │
   └────┬────┘               └──────┬──────┘              └────┬────┘
        │                           │                          │
        │                           │                          ▼
        │                           │                    ┌─────────┐
        │                           │                    │   EA    │
        │                           │                    │ REM-008 │
        │                           │                    │Pipeline │
        │                           │                    └────┬────┘
        │                           │                          │
        │                           │                          ▼
        │                           │                    ┌─────────┐
        │                           │                    │   EA    │
        │                           │                    │Validate │
        │                           │                    └────┬────┘
        │                           │                          │
        ▼                           │                          │
   ┌─────────┐                      │                          │
   │   BA    │                      │                          │
   │Complete │──────────────────────┼──────────────────────────┤
   └────┬────┘                      │                          │
        │                           ▼                          ▼
        │                    ┌─────────────┐            ┌─────────────┐
        └───────────────────►│     QA      │◄───────────│     QA      │
                             │  REM-007    │            │  REM-009    │
                             │   GATE_1    │            │  Baseline   │
                             └──────┬──────┘            └─────────────┘
                                    │
                                    ▼
                             ┌─────────────┐
                             │   GATE_1    │
                             │    PASS     │
                             └──────┬──────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │           PHASE 2.5                  │
                    └─────────────────────────────────────┘
```

---

## Communication Protocol

### Progress Reports

| Agent | Frequency | Trigger |
|-------|-----------|---------|
| BA | Every 50% | 8/16 tables, 16/16 tables |
| QA | On completion | Each REM task |
| EA | On completion | Pipeline update, validation |

### Escalation

| Issue | Action | Owner |
|-------|--------|-------|
| Table creation fails | Retry 3x, then escalate | BA → CE |
| Validation fails | Document issue, escalate | QA → CE |
| Accuracy below projection | Investigate, report | EA → CE |

---

## Success Metrics

### Phase 1.5 Completion - **ACHIEVED**

| Metric | Target | Final |
|--------|--------|-------|
| Tables | 219 | 219 (100%) ✓ |
| CSI | 144 | 144 (100%) ✓ |
| VAR | 63 | 63 (100%) ✓ |
| MKT | 12 | 12 (100%) ✓ |

### Model Performance (h15_ensemble_v2)

| Metric | Target | Actual |
|--------|--------|--------|
| Called Accuracy | 85-95% | 91.70% ✓ |
| Coverage | 30-50% | 17.33% (needs expansion) |
| Ensemble | 3 models | 3 models ✓ |

**Note**: Coverage below target with 59-feature model. Full feature universe (11,337 columns, 1,064 unique) testing in progress.

### Cost

| Metric | Budget | Final |
|--------|--------|-------|
| Monthly | $277 | $33.57 (12.2%) ✓ |

---

## Document References

| Document | Location | Purpose |
|----------|----------|---------|
| Master Remediation Plan | shared/CE_MASTER_REMEDIATION_PLAN.md | Issue tracking |
| Progress Tracker | shared/QA_BA_PROGRESS_TRACKER.md | BA progress |
| Cost Dashboard | shared/QA_COST_ALERT_DASHBOARD.md | Cost monitoring |
| GATE_1 Checklist | shared/QA_GATE1_PREFLIGHT_CHECKLIST.md | Validation |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Archive Date**: December 10, 2025
**Status**: Phase 1.5 COMPLETE - All gates passed, proceed to Phase 2.5

---

*Document archived by QA - December 10, 2025*
