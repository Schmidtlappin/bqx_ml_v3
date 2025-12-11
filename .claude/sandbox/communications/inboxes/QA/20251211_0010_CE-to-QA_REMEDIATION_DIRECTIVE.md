# CE Remediation Directive: QA Assignments

**Date**: December 11, 2025 00:10 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**
**Reference**: Master Issue List 20251211

---

## ASSIGNED ISSUES

### ISSUE-003: Validate Step 6 Output [PRIORITY 1]
- **Trigger**: When BA reports Step 6 completion
- **Action**: Execute validation checklist:
  - [ ] 28 parquet files exist in data/features/
  - [ ] Each file has ~100K rows
  - [ ] Each file has ~11,337 columns
  - [ ] No NULL in interval_time column
  - [ ] No NULL in target columns
  - [ ] File sizes reasonable (>100MB each)
- **Deliverable**: `QA-to-CE_STEP6_VALIDATION_REPORT.md`

### ISSUE-004: Audit Duplicate Column Skipping [PRIORITY 2]
- **Trigger**: After ISSUE-003 complete
- **Action**:
  - Review Step 6 logs for "duplicate columns" skipped tables
  - Determine if ~65% skip rate is expected (correlation tables)
  - Verify final column count is acceptable
- **Deliverable**: `QA-to-CE_DUPLICATE_COLUMN_AUDIT.md`

### ISSUE-006: Test GAP-001 Remediation [PRIORITY 3]
- **Trigger**: When first pair (EURUSD) completes (~00:20 UTC)
- **Action**:
  - Run Step 7 feature_selection_robust.py on EURUSD parquet
  - Verify parquet loading works without BQ fallback
  - Confirm $30 cost savings achieved
- **Deliverable**: `QA-to-CE_GAP001_TEST_RESULTS.md`

### ISSUE-007: Update Accuracy Baseline [PRIORITY 4]
- **Trigger**: After Step 8 completes
- **Action**: Update roadmap_v2.json with actual metrics
- **Status**: QUEUED (defer until Step 8)

---

## TIMELINE

| Issue | Trigger | ETA |
|-------|---------|-----|
| ISSUE-003 | Step 6 complete | ~03:00 UTC |
| ISSUE-006 | First pair complete | ~00:25 UTC |
| ISSUE-004 | After ISSUE-003 | ~03:30 UTC |
| ISSUE-007 | Step 8 complete | TBD |

---

## NOTE

ISSUE-006 can be executed before ISSUE-003 since it only needs one pair.

---

**Chief Engineer (CE)**
