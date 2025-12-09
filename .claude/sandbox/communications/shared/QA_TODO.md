# QA Task List

**Last Updated**: December 10, 2025 00:25
**Maintained By**: CE

---

## CURRENT SPRINT

### P1: CRITICAL (Execute When Triggered)

| Task | Status | Trigger |
|------|--------|---------|
| **GATE_2 Validation** | AWAITING | BA completes feature ledger |
| - Row count = 1,269,492 | READY | Validation query prepared |
| - No NULL final_status | READY | Validation query prepared |
| - SHAP coverage 100% | READY | Validation query prepared |

---

### P2: HIGH (Execute Now)

| Task | Status | Notes |
|------|--------|-------|
| **F3b Cleanup Execution** | APPROVED | Delete 56 duplicates |
| - Run cleanup script | PENDING | CE approved Option A |
| - Verify deletion | PENDING | Check source_v2 table count |
| - Update documentation | PENDING | Note in semantics.json |

---

### P3: NORMAL (Completed)

| Task | Status | Notes |
|------|--------|-------|
| ~~Semantics.json remediation~~ | **COMPLETE** | VAR/MKT gaps fixed |
| ~~P3.1 F3b analysis~~ | **COMPLETE** | 101 tables identified |
| ~~P3.2 Weekly audit protocol~~ | **COMPLETE** | Protocol document created |
| ~~P3.3 Gate template~~ | **COMPLETE** | Template document created |

---

### P4: ONGOING

| Task | Frequency | Next Due |
|------|-----------|----------|
| Daily cost monitoring | Daily | Tomorrow |
| Weekly audit | Weekly | Monday |
| Documentation drift | Weekly | Monday |

---

### P5: LOW PRIORITY

| Task | Status | Notes |
|------|--------|-------|
| Ontology.json storage update | PENDING | Minor - storage totals |
| F3b orphans review | DEFERRED | Phase 4 |

---

## SUCCESS CRITERIA

| Deliverable | Criteria |
|-------------|----------|
| GATE_2 | All validation checks pass |
| F3b cleanup | 56 tables deleted, 45 retained |
| Weekly audit | Protocol executed Mondays |

---

*Updated by CE - December 10, 2025*
