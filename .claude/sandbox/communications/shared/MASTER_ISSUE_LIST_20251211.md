# Master Issue List - December 11, 2025

**Generated**: 00:10 UTC
**Source**: BA, QA, EA Issue Reports

---

## EXECUTIVE SUMMARY

| Severity | BA | QA | EA | Total |
|----------|----|----|----| ------|
| CRITICAL | 0 | 0 | 0 | **0** |
| HIGH | 0 (4 resolved) | 1 | 2 | **3** |
| MEDIUM | 3 | 2 | 3 | **8** |
| LOW | 3 | 2 | 2 | **7** |
| **TOTAL OPEN** | **6** | **5** | **7** | **18** |

---

## HIGH PRIORITY ISSUES (Require Action)

### ISSUE-001: Coverage Below Target (17.33% vs 30-50%)
- **Source**: QA-001
- **Severity**: HIGH
- **Status**: IN PROGRESS (Step 6 running)
- **Owner**: BA (execution) → QA (re-validation)
- **Action**: Awaiting Step 6 completion, then retest with full feature universe

### ISSUE-002: No Checkpoint/Resume in Step 6
- **Source**: EA-001, GAP-BA-002
- **Severity**: HIGH
- **Status**: OPEN
- **Owner**: BA
- **Action**: Implement after Step 6 completes (enhancement for future runs)

### ISSUE-003: No Parquet Output Validation
- **Source**: EA-004, BA-006, QA-003
- **Severity**: HIGH (multiple agents flagged)
- **Status**: OPEN
- **Owner**: QA
- **Action**: Execute validation checklist when Step 6 completes

---

## MEDIUM PRIORITY ISSUES (Schedule for Resolution)

### ISSUE-004: Duplicate Column Skipping (~65% of tables)
- **Source**: EA-002
- **Severity**: MEDIUM
- **Owner**: QA (audit)
- **Action**: Audit skipped tables to verify expected behavior

### ISSUE-005: BQ Concurrent Query Quota Near Limit (96/100)
- **Source**: EA-003, BA-010
- **Severity**: MEDIUM
- **Owner**: CE
- **Decision**: ACCEPT - Current config is optimal

### ISSUE-006: GAP-001 Remediation Needs Testing
- **Source**: EA-006
- **Severity**: MEDIUM
- **Owner**: QA
- **Action**: Test Step 7 with EURUSD after first pair completes

### ISSUE-007: REM-009 Pending (Accuracy Baseline Update)
- **Source**: QA-002
- **Severity**: MEDIUM
- **Owner**: QA
- **Action**: Update after Step 8 completes

### ISSUE-008: Memory Pressure Monitoring
- **Source**: BA-009
- **Severity**: MEDIUM
- **Owner**: EA
- **Action**: Continue monitoring (53GB headroom available)

---

## LOW PRIORITY ISSUES (Defer)

| ID | Issue | Source | Owner | Decision |
|----|-------|--------|-------|----------|
| 009 | Python 3.10 deprecation | BA-005 | CE | DEFER (2026) |
| 010 | BQ cost optimization (Storage API) | BA-007 | BA | DEFER |
| 011 | Hardcoded date range | BA-008 | BA | DEFER |
| 012 | No retry logic | GAP-BA-001 | BA | DEFER |
| 013 | F3b cleanup count discrepancy | QA-004 | QA | DEFER (archived) |
| 014 | Missing GATE_4 script | QA-005 | QA | DEFER (adapt v3) |
| 015 | Memory could support more workers | EA-005 | EA | DEFER |
| 016 | No centralized error logging | EA-007 | EA | DEFER |

---

## RESOLVED THIS SESSION (No Action Needed)

| ID | Issue | Resolution |
|----|-------|------------|
| BA-001 | Single-worker bottleneck | Increased to 12 workers |
| BA-002 | Duplicate column merge failures | Added existing_cols check |
| BA-003 | Missing progress logging | Added per-table logging |
| BA-004 | Per-table INFORMATION_SCHEMA queries | Batch query upfront |

---

## REMEDIATION ASSIGNMENTS

### BA (Build Agent)
- [QUEUED] ISSUE-002: Implement checkpoint/resume (after Step 6)

### QA (QA Agent)
- [ACTIVE] ISSUE-003: Validate Step 6 output (when complete)
- [QUEUED] ISSUE-004: Audit duplicate column skipping
- [QUEUED] ISSUE-006: Test GAP-001 remediation with EURUSD
- [QUEUED] ISSUE-007: Update accuracy baseline (after Step 8)

### EA (Enhancement Agent)
- [ACTIVE] ISSUE-008: Continue memory monitoring

### CE (Chief Engineer)
- [DECIDED] ISSUE-005: Accept 96/100 query limit

---

## NEXT ACTIONS

1. **Immediate**: Continue Step 6 execution (ETA 03:00 UTC)
2. **On Step 6 Complete**: QA validates parquet output (ISSUE-003)
3. **On First Pair Complete**: QA tests GAP-001 fix (ISSUE-006)
4. **After Step 8**: QA updates accuracy baseline (ISSUE-007)
5. **Post-Phase 2.5**: BA implements checkpoint/resume (ISSUE-002)

---

*Master Issue List - CE*
