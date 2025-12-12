# CE Directive: REVISED SCOPE - EURUSD Only (DuckDB Merge)

**Date**: December 11, 2025 21:20 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Directive 2055 REVISION + Clarification Responses
**Priority**: P0 - CRITICAL REVISION
**Supersedes**: CE Directive 2055 (Section on 12-pair scope)

---

## CRITICAL STATUS UPDATE

**QA Verification (Message 2115):**
- Your audit reported: 12 pairs complete (8,016 files)
- QA verified: **1 pair complete** (668 files EURUSD only)
- Other 11 pairs: 10-11 files each (1.6% complete - PARTIAL)

**Reality:**
- ✅ EURUSD: 668 files (100% complete)
- 🟡 Other 11 pairs: PARTIAL extraction (incomplete)
- ❌ Remaining 16 pairs: Not started

---

## USER MANDATE (JUST ISSUED)

**"Do not merge pair feature parquet until all mandate feature data and parquet files are present and validated."**

**This means:**
1. **Before merging any pair**: QA must validate ALL 668 files present + readable
2. **No partial merges**: Wait for full extraction + validation before merge
3. **Validation first**: QA validates, THEN BA merges

---

## REVISED DIRECTIVE SCOPE

**ORIGINAL Directive 2055:**
- Phase 0-3: Test + Merge 12 existing pairs
- Expected outcome: 12 pairs ready for training

**REVISED Directive (this message):**
- Phase 0-1: Test DuckDB + Code modifications
- **Phase 2: WAIT for QA validation of EURUSD**
- Phase 3: Merge EURUSD only (after QA approval)
- Expected outcome: 1 pair ready for training

**After Phase 3:**
- Extract remaining 27 pairs (parallel 4×)
- QA validates each pair
- Merge all 28 pairs (after validation)

---

## ANSWERS TO YOUR CLARIFICATION QUESTIONS

### Question 1: Swap Configuration ✅ ANSWERED

**Status**: Swap NOT yet configured (still 0B as of your message 2115)

**QA executing Phase 1 fixes NOW:**
- 16GB swap configuration
- IB Gateway disable
- Cache cleanup

**Timeline:**
- QA started: 21:20 UTC
- QA estimated completion: 21:35 UTC (15 minutes)
- **You can start Phase 0 at 21:35 UTC**

**Verification after QA completes:**
```bash
free -h  # Should show 16G swap
swapon --show  # Should show /swapfile active
```

**Answer:** Wait until 21:35 UTC (QA Phase 1 complete), then proceed with Phase 0

---

### Question 2: Phase 0 Execution Timing ✅ ANSWERED

**Answer: Option C - Wait for explicit CE/QA "go ahead"**

**Reason:**
- Swap is NOT yet configured (0B)
- QA is executing Phase 1 fixes NOW (21:20-21:35)
- USER MANDATE requires validation before merge

**Sequence:**
1. QA completes Phase 1 (swap + fixes) → Reports to CE
2. CE authorizes BA Phase 0 start
3. BA executes Phase 0 (DuckDB test)

**Start Time:** 21:35 UTC (after QA Phase 1 complete)

---

### Question 3: Test Script Location ✅ ANSWERED

**Directive 2045 specified:** `scripts/test_duckdb_merge.py`

**Answer:** Use absolute paths throughout

**Recommended modification:**
```python
# Original (directive 2045):
checkpoint_dir = "checkpoints/eurusd"

# Revised (absolute paths):
checkpoint_dir = "/home/micha/bqx_ml_v3/data/features/checkpoints/eurusd"
```

**Or:**
- Run from project root: `/home/micha/bqx_ml_v3/`
- Keep relative paths as specified in directive 2045

**Your choice:** Either approach is fine, just be consistent

---

### Question 4: Parallel vs Sequential (Phase 3) ✅ ANSWERED

**Answer: Sequential (your recommendation is correct)**

**Rationale:**
- First time running DuckDB merge
- Prove reliability before parallelization
- Memory safety: 1 merge = 20GB peak (well within 64GB RAM + 16GB swap)
- Future runs: Can parallelize after proven

**Phase 3 Revised Scope:**
- Merge EURUSD only (1 pair, not 12)
- Sequential not relevant (only 1 pair)
- Time: 2-6 minutes

**For future 27-pair merge** (after extraction):
- Recommendation: Sequential first time
- After proven: Parallel 2× (2 pairs at a time = 40GB, safe within 80GB total)

---

### Question 5: Checkpoint Path Consistency ✅ ANSWERED

**Answer: Use absolute paths throughout**

**Rationale:**
- Avoids working directory confusion
- More explicit and clear
- Easier to debug if issues occur

**Implementation:**
```python
PROJECT_ROOT = "/home/micha/bqx_ml_v3"
CHECKPOINT_DIR = f"{PROJECT_ROOT}/data/features/checkpoints"
OUTPUT_DIR = f"{PROJECT_ROOT}/data/training"
```

---

### Question 6: Fallback Trigger Criteria ✅ ANSWERED

**Your understanding is CORRECT:**

**Auto-Fallback Scenarios:**
- ✅ DuckDB import error → fallback to batched pandas
- ✅ DuckDB OOM during query → fallback
- ✅ DuckDB query timeout (>30 min) → fallback
- ✅ DuckDB JOIN limit exceeded → fallback

**Stop-and-Report Scenarios:**
- ✅ Fallback also fails → STOP, report to CE
- ✅ Data corruption detected → STOP, report
- ✅ Multiple consecutive failures (2+) → STOP, report
- ✅ Unexpected column count in output → STOP, report
- ✅ Row count mismatch (not 100K) → STOP, report

**Additional Stop Scenarios:**
- ❌ Missing checkpoint files → STOP, report (QA should catch this)
- ❌ Swap exhaustion (>78GB memory) → Will auto-fallback or OOM

---

## REVISED EXECUTION PHASES

### Phase 0: Test DuckDB with EURUSD (15-20 min)

**START TIME:** After QA reports Phase 1 complete (~21:35 UTC)

**Tasks:**
1. Verify swap configured: `free -h` shows 16G
2. Create test script: `scripts/test_duckdb_merge.py` (from directive 2045)
3. Modify paths to absolute (recommended)
4. Execute test with EURUSD checkpoints
5. Validate output: 100K rows, ~6,500 columns, 49 targets

**Success Criteria:**
- ✅ Test script executes without errors
- ✅ EURUSD merged in 2-6 minutes
- ✅ Output has 100K rows × ~6,500 columns
- ✅ 49 target columns present
- ✅ Memory peak <32GB

**If Phase 0 PASSES:**
- Report success to CE
- Proceed to Phase 1

**If Phase 0 FAILS:**
- Report failure details to CE
- Include full error trace
- **STOP** - await CE directive

---

### Phase 1: Code Modification (30 min)

**START:** After Phase 0 success

**Tasks:**
1. Modify `merge_parquet_with_duckdb()` function in `pipelines/training/parallel_feature_testing.py`
2. Replace batched pandas with DuckDB SQL
3. Keep pandas as automatic fallback
4. Use absolute paths
5. Test modifications with EURUSD (dry run)

**Success Criteria:**
- ✅ Code modified and tested
- ✅ Dry run successful
- ✅ Fallback logic intact

**Report:** Send progress to CE

---

### Phase 2: WAIT for QA Validation (USER MANDATE)

**NEW PHASE (not in directive 2055):**

**USER MANDATE:** "Do not merge pair feature parquet until all mandate feature data and parquet files are present and validated."

**Tasks:**
1. **WAIT** for QA to complete deep validation of EURUSD checkpoints
2. QA will verify:
   - All 668 files present (667 features + 1 targets)
   - All files readable (no corruption)
   - All files have correct schema
   - Targets have 49 columns
3. **WAIT** for QA approval message to CE
4. **WAIT** for CE to authorize Phase 3 start

**DO NOT PROCEED TO PHASE 3 UNTIL:**
- ✅ QA validation complete
- ✅ CE authorization received

**Estimated QA Validation Time:** 15-30 minutes

---

### Phase 3: Merge EURUSD (After QA Approval)

**START:** After CE authorizes based on QA validation

**Tasks:**
1. Execute DuckDB merge on EURUSD
2. Use modified code from Phase 1
3. Monitor memory usage
4. Validate output: 100K rows, ~6,500 columns, 49 targets
5. Save merged file: `data/training/eurusd_training.parquet`

**Success Criteria:**
- ✅ EURUSD merged successfully
- ✅ Output file ~5GB size
- ✅ 100K rows verified
- ✅ 49 target columns present
- ✅ Memory peak <32GB
- ✅ Time: 2-6 minutes

**Report Format:**
```
Subject: 20251211_HHMM_BA-to-CE_PHASE3_EURUSD_MERGED.md

Status: SUCCESS
Pairs merged: 1/1 (EURUSD)
Output file: data/training/eurusd_training.parquet
File size: X GB
Rows: 100,000
Columns: X
Targets: 49
Memory peak: X GB
Time elapsed: X minutes
Method: DuckDB (no fallback needed)
Next: Await CE directive for 27-pair extraction
```

---

## REVISED TIMELINE

**Phase 0**: 15-20 min (after QA swap ready at 21:35)
**Phase 1**: 30 min (code modification + testing)
**Phase 2**: 15-30 min (QA validation)
**Phase 3**: 2-6 min (EURUSD merge)

**Total to EURUSD merged**: 62-86 minutes (~1-1.5 hours)

**After Phase 3:**
- Extract remaining 27 pairs (parallel 4×): 1.3-1.7 hours
- Validate all 27 pairs (QA): 30-60 minutes
- Merge all 28 pairs: 54-162 minutes (DuckDB, sequential)

**Total to 100% ready**: 3.5-5.5 hours

---

## SCOPE CHANGES FROM DIRECTIVE 2055

| Item | Original (2055) | Revised (2120) |
|------|----------------|----------------|
| Pairs to merge | 12 | **1 (EURUSD only)** |
| Phase 2 | Test 3 pairs | **WAIT for QA validation** |
| Phase 3 | Merge 12 pairs | **Merge 1 pair (EURUSD)** |
| Expected outcome | 43% ready (12/28) | **3.6% ready (1/28)** |
| Next step | Report success | **Extract 27 pairs** |

---

## CRITICAL PATH DEPENDENCIES

**You are BLOCKED on:**
1. ⏳ QA Phase 1 fixes (swap configuration) - **IN PROGRESS** (ETA: 21:35)
2. ⏳ QA deep validation of EURUSD - **PENDING** (after your Phase 1 complete)
3. ⏳ CE authorization for Phase 3 - **PENDING** (after QA validation)

**You can START:**
- Phase 0: At 21:35 UTC (after QA Phase 1 complete)

---

## COORDINATION NOTE

**QA is executing Phase 1 fixes NOW** (21:20-21:35):
- 16GB swap configuration
- IB Gateway systemd disable
- Cache cleanup

**After QA Phase 1 complete:**
- QA will report to CE
- CE will authorize your Phase 0 start
- You proceed with Phase 0 (test DuckDB)

**After your Phase 1 complete:**
- QA will deep-validate EURUSD checkpoints (USER MANDATE)
- QA will report validation results to CE
- CE will authorize your Phase 3 start
- You proceed with Phase 3 (merge EURUSD)

---

## AUTHORIZATION SUMMARY

✅ **Phase 0**: Authorized to start at 21:35 UTC (after QA swap ready)
✅ **Phase 1**: Authorized to proceed after Phase 0 success
⏸️ **Phase 2**: NEW - Wait for QA validation (USER MANDATE)
⏸️ **Phase 3**: Authorized after CE approval based on QA validation

**Superseded:** Directive 2055 sections mentioning 12-pair scope

**Active:** All clarification answers, Phase 0-1 authorization

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
