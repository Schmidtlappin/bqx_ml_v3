# CE Directive: Roadmap v2.2.0 Update - Reingest Required

**Document Type**: ROADMAP UPDATE NOTIFICATION
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: REINGEST REQUIRED

---

## ROADMAP VERSION UPDATE

**Previous**: v2.1.0
**Current**: v2.2.0
**Commit**: `71bcb1c`

---

## KEY CHANGES

### 1. NEW PHASE: Phase 1.5 - Feature Table Gap Remediation

**Location**: Between Phase 1 (Infrastructure) and Phase 2 (Feature Selection)

```
Phase 1.5 Structure:
├── CSI Tables: 192 (CRITICAL)
├── VAR Tables: 59 (HIGH)
├── MKT Tables: 14 (MEDIUM)
├── Total: 265 tables
└── GATE_1: All tables created and validated
```

**BA Current Task**: Phase 1.5 is your ACTIVE phase.

### 2. NEW PHASE: Phase 2.5 - Feature Ledger Generation

**Location**: Between Phase 2 (Feature Selection) and Phase 3 (Stacking)

```
Phase 2.5 Structure:
├── Create generate_feature_ledger.py
├── Generate 1,269,492 ledger rows
├── Validate 100% coverage
├── Run feature selection (50% threshold)
└── GATE_2: Ledger validated
```

**BA Future Task**: After GATE_1 passes.

### 3. NEW SECTION: User Mandates

**All mandates are BINDING**:

| Mandate | Value | Date |
|---------|-------|------|
| SHAP sample size | 100,000+ | 2025-12-09 |
| Stability threshold | 50% | 2025-12-09 |
| Ledger coverage | 100% | 2025-12-09 |

### 4. NEW SECTION: Risk Register

**5 Identified Risks**:

| ID | Description | Status | Owner |
|----|-------------|--------|-------|
| RISK-001 | ElasticNet AUC < 0.5 | OPEN | BA |
| RISK-002 | Gap tables blocking | IN_PROGRESS | BA |
| RISK-003 | SHAP compute time | MITIGATED | BA |
| RISK-004 | Incomplete testing | PLANNED | BA |
| RISK-005 | Accuracy target | PLANNED | CE |

### 5. NEW SECTION: Model Versioning

```
Scheme: v{major}.{minor}.{patch}_{pair}_{horizon}_{timestamp}
Example: v1.0.0_eurusd_h15_20251209
Storage: gs://bqx-ml-v3-models/{pair}/{horizon}/
```

### 6. NEW SECTION: Backtesting Protocol

```
Method: Walk-forward with expanding window
Train window: Minimum 6 months
Test window: 1 month
Embargo: 30 intervals
Refit: Monthly
Minimum windows: 12
```

### 7. FIXED: Stability Threshold Reference

**Old**: `>60% frequency`
**New**: `>50% frequency (USER APPROVED 2025-12-09)`

---

## BA IMMEDIATE ACTIONS

### Action 1: Reingest Updated Roadmap
```
/intelligence/roadmap_v2.json (v2.2.0)
```

### Action 2: Note Your Active Phase
```
Phase 1.5: Feature Table Gap Remediation
├── Status: IN_PROGRESS
├── Your task: CSI → VAR → MKT
└── Gate: GATE_1
```

### Action 3: Acknowledge Risk Ownership
```
RISK-001: ElasticNet AUC (investigate after Phase 4)
RISK-002: Gap tables (your current work)
RISK-003: SHAP time (mitigated via parallelization)
RISK-004: Testing scope (after GATE_1)
```

---

## PHASE SEQUENCE (Updated)

```
✓ Phase 1: Infrastructure (COMPLETE)
→ Phase 1.5: Gap Remediation (IN_PROGRESS) ← YOU ARE HERE
  Phase 2: Feature Selection (COMPLETE - needs full universe)
  Phase 2.5: Feature Ledger (PENDING)
  Phase 3: Stacking Architecture (COMPLETE)
  Phase 4: EURUSD Training (READY)
  Phase 5: Scale to 28 Pairs (PENDING)
  Phase 6: Production (PENDING)
```

---

## GATES

| Gate | Phase | Criteria | Status |
|------|-------|----------|--------|
| GATE_1 | 1.5 | 265 tables created | PENDING |
| GATE_2 | 2.5 | Ledger 100% coverage | PENDING |
| GATE_3 | 4 | EURUSD accuracy targets met | PENDING |
| GATE_4 | 5 | All 784 models trained | PENDING |

---

## NO CHANGE TO CURRENT DIRECTIVE

Your current task remains:
1. **CSI Implementation** (192 tables) - proof of concept then parallel
2. **VAR Completion** (59 tables) - after CSI
3. **MKT Completion** (14 tables) - after VAR

The roadmap update adds structure and documentation but does not change your work order.

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Roadmap Version**: 2.2.0
