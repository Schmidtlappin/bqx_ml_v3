# CE Directive: Step 6 Monitoring

**Date**: December 11, 2025 04:25 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**

---

## INTEL-UPDATE: ACKNOWLEDGED

Intelligence file updates confirmed complete. Excellent work.

---

## NEW ASSIGNMENT: STEP 6 MONITORING

Step 6 restart has been authorized. Begin monitoring.

---

## MONITORING TASKS

| Task | Trigger | Priority |
|------|---------|----------|
| **Monitor Step 6 progress** | NOW | P1 |
| ISSUE-006: Test GAP-001 (parquet) | EURUSD complete | P3 |
| ISSUE-003: Validate outputs | All pairs complete | P1 |
| ISSUE-004: Pre-Step 7 gate | After ISSUE-003 | P2 |

---

## VALIDATION CHECKLIST (After Step 6)

When Step 6 completes, validate:
- [ ] 28 parquet files in `data/features/`
- [ ] Each file has ~100K rows
- [ ] Each file has correct columns (merged from 669 tables)
- [ ] No NULL in interval_time
- [ ] No NULL in target columns
- [ ] File sizes reasonable (>100MB each)

---

## MILESTONE MONITORING

| Milestone | Expected ETA |
|-----------|--------------|
| EURUSD complete | +8 min |
| 50% (14 pairs) | +1.5 hrs |
| 100% (28 pairs) | +3-4 hrs |

---

## DELIVERABLES

1. `QA-to-CE_STEP6_MILESTONE_EURUSD.md` - After first pair
2. `QA-to-CE_STEP6_VALIDATION_REPORT.md` - After completion

---

**Chief Engineer (CE)**
