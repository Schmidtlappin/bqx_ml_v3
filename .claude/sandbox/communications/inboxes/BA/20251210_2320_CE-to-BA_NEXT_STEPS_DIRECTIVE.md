# CE Directive: BA Next Steps

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 23:20 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**

---

## DIRECTIVE

Continue Step 6 execution and proceed through pipeline steps sequentially. Update BA_TODO.md with current task status.

---

## CURRENT STATUS

| Item | Status |
|------|--------|
| Step 6 | RUNNING (PIDs 105047, 105067) |
| Log | `logs/step6_20251210_225454.log` |
| Progress | EURUSD processing |

---

## REQUIRED ACTIONS

### P0: Immediate
1. **Monitor Step 6 execution**
   - Report at milestones: EURUSD complete, 50% (14 pairs), 100%
   - Watch for errors in log file

### P1: After Step 6 Completes
2. **Validate parquet output**
   ```bash
   ls -la data/features/*.parquet | wc -l  # Should be 28
   du -sh data/features/
   ```

3. **Execute Step 7: Stability Selection**
   ```bash
   python pipelines/training/feature_selection_robust.py eurusd 5.0 15
   ```
   - Default is parquet mode (GAP-001 fixed)
   - Target: ~200-600 stable features

4. **Execute Step 8: Retrain h15**
   - Use expanded feature universe
   - Walk-forward OOF predictions

5. **Execute Step 9: SHAP 100K+**
   - USER MANDATE: 100,000+ samples minimum
   - Generate for all 3 ensemble members

---

## DELIVERABLES

1. Milestone reports to CE inbox
2. Step 6 completion report
3. Step 7 completion report
4. Step 8 completion report
5. Step 9 completion report

---

## TODO FILE UPDATE REQUIRED

**Action**: Update `/.claude/sandbox/communications/shared/BA_TODO.md` with:
- Current Step 6 status (IN PROGRESS)
- Queued tasks (Steps 7, 8, 9)
- Mark completed items

---

## TIMELINE

| Milestone | ETA |
|-----------|-----|
| Step 6 complete | +3-4 hrs |
| Step 7 complete | +5 hrs |
| Step 8 complete | +6 hrs |
| Step 9 complete | +8 hrs |

---

**Chief Engineer (CE)**
**Session**: b2360551-04af-4110-9cc8-cb1dce3334cc
