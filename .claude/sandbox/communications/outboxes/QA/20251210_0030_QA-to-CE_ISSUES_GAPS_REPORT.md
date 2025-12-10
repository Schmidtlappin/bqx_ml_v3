# QA Report: Known Issues, Errors, and Gaps

**Document Type**: QA ISSUES REPORT
**Date**: December 10, 2025 00:30
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Purpose**: QA-specific findings (complements EA report)

---

## Executive Summary

QA has identified issues from validation, documentation audits, and cleanup operations. No critical blockers remain.

---

## CRITICAL ISSUES

### NONE CURRENTLY BLOCKING

- GATE_1: PASSED
- Documentation: ALIGNED (post-remediation)
- Cost: GREEN (12.5% of budget)

---

## HIGH PRIORITY ISSUES

### QA-ISSUE-001: F3b Orphan Tables Pending Review
**Location**: `bqx_bq_uscen1_v2`
**Count**: 45 tables
**Status**: DEFERRED TO PHASE 4

| Group | Count | Potential Use |
|-------|-------|---------------|
| reg_bqx | 1 | Combined regression |
| reg_corr_* | 8 | ETF correlation features |
| regime_* | 36 | Regime classification |

**Risk**: May contain valuable features for regime-aware meta-learner
**Decision Needed**: Migrate to features_v2 or delete after Phase 4 evaluation

---

### QA-ISSUE-002: F3b Cleanup Completion Report Not Filed
**Status**: INTERRUPTED
**Action**: Cleanup executed (56 tables deleted), but formal report cancelled

**Summary**:
- Duplicates deleted: 56
- Orphans retained: 45
- Verification: PASSED (45 remaining as expected)
- Documentation: semantics.json updated with f3b_cleanup section

---

## MEDIUM PRIORITY ISSUES

### QA-ISSUE-003: Ontology.json Storage Outdated
**Status**: CONFIRMED (also flagged by EA)
**Impact**: Minor documentation inconsistency
**Recommendation**: Update during next weekly audit

---

### QA-ISSUE-004: Weekly Audit Not Yet Executed
**Status**: PROTOCOL READY, NOT EXECUTED
**File**: `/intelligence/qa_protocols/weekly_audit.md`
**Schedule**: Mondays
**Action**: First audit pending (protocol just created)

---

## LOW PRIORITY ISSUES

### QA-ISSUE-005: Background Monitor Shell Orphaned
**Status**: Shell 13257b still showing in system reminders
**Impact**: None (already killed)
**Action**: Cosmetic only - will clear on session end

---

## ERRORS ENCOUNTERED (QA Session)

| Error | Resolution |
|-------|------------|
| BQ "current" reserved word | Changed alias to "actual_count" |
| File edit without read | Read file first |
| BQ query grouping error | Simplified query |

**Status**: All resolved during session

---

## GAPS INVENTORY (QA Perspective)

### Documentation Gaps (RESOLVED)
| Gap | File | Status |
|-----|------|--------|
| VAR/MKT gaps wrong | semantics.json | FIXED |
| VAR/MKT gaps wrong | feature_catalogue.json | FIXED |
| feature_type_summary counts | semantics.json | FIXED |

### Validation Gaps (PENDING)
| Gap | Trigger | Status |
|-----|---------|--------|
| GATE_2 validation | Phase 2.5 complete | CRITERIA READY |
| GATE_3 validation | Phase 3 complete | TEMPLATE READY |
| GATE_4 validation | Phase 4 complete | TEMPLATE READY |

### Process Gaps
| Gap | Status |
|-----|--------|
| Cross-agent validation protocol | PENDING (P5.3) |
| Historical audit archive | PENDING (P5.1) |

---

## QA DELIVERABLES STATUS

| Deliverable | Status |
|-------------|--------|
| GATE_1 Validation | COMPLETE |
| GATE_2 Criteria | COMPLETE |
| Weekly Audit Protocol | COMPLETE |
| Gate Template | COMPLETE |
| F3b Cleanup Script | EXECUTED |
| Semantics Remediation | COMPLETE |

---

## RECOMMENDED ACTIONS

### Immediate
1. **Acknowledge F3b cleanup completion** - 56 duplicates deleted
2. **Confirm orphan review timeline** - Phase 4 or earlier

### Near-Term
3. **Update ontology.json storage** - Reflect cleanup
4. **Execute first weekly audit** - Monday

### Post-GATE_2
5. **Review orphan tables** - Migrate or delete decision

---

## Summary

| Category | Count |
|----------|-------|
| High Issues | 2 |
| Medium Issues | 2 |
| Low Issues | 1 |
| Errors (resolved) | 3 |
| Gaps (pending) | 5 |

**Overall QA Status**: GREEN - No blockers, documentation aligned

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Date**: December 10, 2025 00:30
**Status**: ISSUES REPORT COMPLETE
