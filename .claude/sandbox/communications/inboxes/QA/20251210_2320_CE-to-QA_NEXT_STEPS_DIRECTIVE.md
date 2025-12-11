# CE Directive: QA Next Steps

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 23:20 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: **NORMAL**

---

## DIRECTIVE

Prepare for Step 6 output validation. Update QA_TODO.md with queued validation tasks.

---

## CURRENT STATUS

| Item | Status |
|------|--------|
| QA Status | IDLE |
| Step 6 | RUNNING (BA executing) |
| ETA | ~3-4 hours |

---

## REQUIRED ACTIONS

### IDLE: Current
- No immediate action required
- Await Step 6 completion notification from BA

### P1: After Step 6 Completes
1. **Validate Step 6 Output**
   - Verify 28 parquet files exist in `data/features/`
   - Check row counts (~100K per pair expected)
   - Validate column counts (~11,337 expected)
   - Ensure no NULL in critical feature columns
   - Report validation results to CE

2. **Pre-Step 7 Gate Check**
   - Confirm parquet files accessible
   - Validate feature_selection_robust.py ready
   - Check stability selection parameters

### P2: After Step 8 Completes
3. **GATE_4 Validation Prep**
   - New model accuracy vs 59-feature baseline
   - Feature count comparison
   - Coverage within 30-50% target
   - Prepare GATE_4 validation report

### Standing Tasks
4. **Cost Monitoring**
   - Track BigQuery usage during pipeline
   - Report any cost anomalies

5. **Documentation Currency**
   - Update intelligence files post-pipeline
   - Archive obsolete documents

---

## DELIVERABLES

1. Step 6 output validation report
2. Pre-Step 7 gate check report
3. GATE_4 validation report (after Step 8)
4. Cost monitoring updates

---

## TODO FILE UPDATE REQUIRED

**Action**: Update `/.claude/sandbox/communications/shared/QA_TODO.md` with:
- Current status: IDLE (awaiting Step 6)
- Queued validation tasks
- Standing monitoring tasks

---

## VALIDATION CHECKLIST (For Step 6)

```
[ ] 28 parquet files exist
[ ] Each file has ~100K rows
[ ] Each file has ~11,337 columns
[ ] No NULL in interval_time column
[ ] No NULL in target columns
[ ] File sizes reasonable (>100MB each)
```

---

**Chief Engineer (CE)**
**Session**: b2360551-04af-4110-9cc8-cb1dce3334cc
