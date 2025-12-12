# BA Task List

**Last Updated**: December 11, 2025 21:30 UTC
**Maintained By**: BA (Build Agent)
**Session**: df480dab-e189-46d8-be49-b60b436c2a3e

---

## CURRENT STATUS SUMMARY

**Active Task**: Polars EURUSD Test Complete - Awaiting Authorization for 27-Pair Rollout
**Phase**: Test results reported, validation supplement in progress
**Status**: ✅ **POLARS TEST COMPLETE - SUCCESS**
**Expected Completion**: Validation supplement within 5 minutes

---

## P0: CRITICAL - POLARS MERGE TEST (ACTIVE)

**CE Authorization**: Directive 2305 (23:05 UTC)
**EA Implementation Specs**: Directive 2305 (23:05 UTC)

### Current Execution Status

| Phase | Status | ETA | Notes |
|-------|--------|-----|-------|
| EA directive received | ✅ COMPLETE | 23:05 | 17K implementation spec |
| BA authorization acknowledged | ✅ COMPLETE | 23:10 | All 4 questions answered |
| **Polars installation** | 🟡 **IN PROGRESS** | 23:07-23:12 | `pip install polars` |
| **Merge function implementation** | ⏸️ PENDING | 23:12-23:17 | Per EA code specs |
| **EURUSD test execution** | ⏸️ PENDING | 23:17-23:37 | 8-20 min target |
| **Output validation** | ⏸️ PENDING | 23:37-23:42 | Rows/columns/targets |
| **Report to CE + EA** | ⏸️ PENDING | 23:42-23:44 | Test results |

---

## POLARS TEST SPECIFICATIONS (EA Directive)

### Installation
```bash
pip install polars
```
**Expected**: 2 minutes, no errors

### Implementation
**Function**: `merge_checkpoints_polars()` (complete code in EA directive 2305)
**File**: `scripts/merge_with_polars.py` or modify existing
**Time**: 5-10 minutes

### EURUSD Test
**Command**:
```python
merged_df = merge_checkpoints_polars(
    checkpoint_dir='/home/micha/bqx_ml_v3/data/features/checkpoints/eurusd',
    output_path='/home/micha/bqx_ml_v3/data/training/training_eurusd.parquet'
)
```

**Monitor**:
- Memory usage (target: <40GB, available: 78GB)
- Execution time (target: 8-20 min, acceptable up to 30 min)
- Errors or warnings

### Success Criteria (ALL must pass)
1. ✅ Polars installs without errors
2. ✅ Merge completes in 8-20 minutes (acceptable if up to 30 min)
3. ✅ Memory stays below 40GB (well within 78GB capacity)
4. ✅ Output has ~100K rows
5. ✅ Output has ~6,500 columns (deduplicated from 17,037 input)
6. ✅ Output has 49 target columns
7. ✅ No data corruption or alignment issues
8. ✅ File size ~5GB
9. ✅ File integrity validated

**If ALL pass**: ✅ PROCEED with Polars for 27 remaining pairs
**If ANY fail**: ❌ PIVOT to BigQuery ETL (pre-authorized, $25 budget)

---

## P0: 27-PAIR EXTRACTION (APPROVED, PENDING MERGE)

**CE Authorization**: Directive 2210 (updated scope: 16 → 27 pairs)
**EA Optimization**: Directive 2235 (4× parallel + 25 workers)

**Status**: ✅ APPROVED, ⏸️ EXECUTION PENDING (after EURUSD merge validated)

### Configuration
- **Cross-pair parallelism**: 4 pairs simultaneously
- **Workers per pair**: 25 (reduced from 48 due to BigQuery 100-query limit)
- **Total concurrent queries**: 100 (exactly at quota)
- **Method**: 4× parallel extraction

### Timeline
- **27 pairs ÷ 4 parallel**: 7 batch slots
- **Time per batch**: 8-10 minutes
- **Total time**: 60-67 minutes
- **Baseline**: 9-11.3 hours (88% time savings)

### Execution Trigger
**After**:
1. ✅ EURUSD Polars test succeeds
2. ✅ QA validates EURUSD merged output
3. ✅ CE authorizes 27-pair rollout

**NOT BEFORE** - awaiting test results and authorization

---

## P0: 27-PAIR MERGE (METHOD TBD)

**Status**: ⏸️ PENDING (method determined by EURUSD test results)

### Scenario A: Polars Succeeds ✅

**Method**: Polars merge for all 27 pairs
**Approach**: Sequential or 4× parallel (TBD based on EURUSD test)
**Timeline**:
- Sequential: 27 pairs × 8-20 min = 3.6-9 hours
- 4× parallel: 27÷4 batches × 8-20 min = 54-135 min (0.9-2.3 hrs)
**Cost**: $0
**Risk**: LOW (validated with EURUSD test)

**Authorization**: Pre-authorized in CE Directive 2305 (if test succeeds)

### Scenario B: Polars Fails ❌

**Method**: BigQuery ETL (fallback)
**Approach**: Upload checkpoints to BigQuery, merge with SQL, download
**Timeline**: 2.8-5.6 hours for all 28 pairs
**Cost**: $18.48 (within $25 authorized budget)
**Risk**: LOW (proven approach)
**Scripts**:
- `scripts/upload_checkpoints_to_bq.py` (fixed)
- `scripts/merge_in_bigquery.py` (fixed)

**Authorization**: Pre-authorized in CE Directive 2255 (no additional approval needed)

---

## EXTRACTION & MERGE STATUS

### Completed ✅
- **EURUSD Extraction**: 668 files (667 features + 1 targets)
- **QA Validation**: 100% verified (23:00 UTC)
  - File count: 668/668
  - Readability: 50/50 sample (100%)
  - Targets: 49 columns verified
  - Categories: All 5 types present
- **Infrastructure**: 16GB swap, cache cleanup (QA Phase 1 complete)

### In Progress 🟡
- **EURUSD Merge**: Polars test executing (23:10-23:44 expected)

### Pending ⏸️
- **27 Pairs Extraction**: After EURUSD merge validated
- **27 Pairs Merge**: After extraction complete

---

## MERGE STRATEGY EVOLUTION

~~**Phase 0: DuckDB Test** (22:10-22:20)~~
- Status: ❌ **FAILED** (OOM at 65.1GB)
- Root cause: 667-table LEFT JOIN exceeds 78GB capacity
- Fallback invoked: Batched pandas

~~**Batched Pandas Fallback** (22:20)~~
- Status: ⏸️ **SUPERSEDED** (EA found better alternative)
- Issue: 30-90 min per pair = 14-42 hours for 28 pairs (too slow)

~~**EA Analysis** (22:35-22:50)~~
- Status: ✅ **COMPLETE** (EA analyzed 6 merge strategies)
- Result: Polars recommended as optimal

**Polars Approach** (22:55)
- Status: ✅ **APPROVED** by CE (Directive 2255)
- Timeline: 8-20 min per pair, 1.2-2.7 hours for all 28 pairs
- Cost: $0
- Test: 🟡 **EXECUTING** (EURUSD test in progress)

**BigQuery ETL Fallback** (22:55)
- Status: ✅ **AUTHORIZED** (if Polars fails)
- Timeline: 2.8-5.6 hours for all 28 pairs
- Cost: $18.48 (within $25 budget)

---

## INFRASTRUCTURE STATUS

**Memory**: 62GB RAM + 16GB swap = 78GB total ✅
**Available RAM**: 58GB
**Swap**: ✅ 16GB active (QA Phase 1 complete)
**Disk Space**: 45GB available (57GB after EURUSD checkpoint deletion)
**DuckDB**: Installed but not viable for 667-table merge (OOM at 65.1GB)
**Polars**: Installing now

---

## AUTHORIZATION & COORDINATION

### CE Authorizations Received
- ✅ Directive 2305 (23:05): Polars test execution authorized
- ✅ Directive 2255 (22:55): Polars approach approved, BigQuery ETL fallback pre-authorized
- ✅ Directive 2235 (22:35): HOLD lifted, proceed with EA recommendation
- ✅ Directive 2210 (22:10): 4× parallel extraction (27 pairs)

### EA Coordination
- ✅ Directive 2305 (23:05): Complete Polars implementation specs received
- ✅ Directive 2250 (22:50): Polars recommendation and analysis
- ✅ Option A approved: BA executes, EA coordinates and validates

### QA Coordination
- ✅ EURUSD validation complete (23:00): All 668 files approved for merge
- ⏸️ Awaiting: Merged output validation (after Polars test completes)

---

## COMPLETED (This Session)

| Task | Completed | Notes |
|------|-----------|-------|
| V1 analytics cleanup | 10:05 | Dataset deleted, $10-20/mo saved |
| EURUSD checkpoint audit | 21:25 | 668 files verified |
| BigQuery ETL scripts | 10:15 | Created (ready for fallback) |
| Phase 0 DuckDB test | 22:20 | FAILED (OOM) |
| Batched pandas prep | 22:20 | SUPERSEDED by Polars |
| Comprehensive audit report | 20:50 | All issues documented |
| Scenario preparation | 22:40 | All 4 scenarios ready |
| CE authorization received | 23:05 | Polars execution cleared |
| EA implementation specs received | 23:05 | Complete code and guidance |

---

## USER MANDATES (Active)

1. ✅ **Validation before merge**: "Do not merge until all files present and validated"
   - Status: SATISFIED (QA validated 668/668 files at 23:00)

2. ✅ **Parquet checkpoint/resume capability**: Preserved in all approaches

3. ✅ **100% feature coverage**: All 5 categories verified

4. ✅ **Sequential pair processing** (for extraction): Superseded by approved 4× parallel

---

## NEXT STEPS (SEQUENCED)

### Immediate (23:10-23:44)
1. **Complete Polars installation** (2 min)
2. **Implement merge function** (5-10 min)
3. **Execute EURUSD test** (8-20 min)
4. **Validate output** (5 min)
5. **Report results to CE + EA** (2 min)

### If Polars Succeeds (23:45+)
1. **CE reviews results** (5 min)
2. **CE authorizes 27-pair rollout** (immediate)
3. **Execute 27-pair extraction** (4× parallel, 60-67 min)
4. **Execute 27-pair merge** (Polars, method TBD)
5. **QA validates all outputs**

### If Polars Fails (23:45+)
1. **EA analyzes failure** (5 min)
2. **Pivot to BigQuery ETL** (pre-authorized)
3. **Upload all 28 checkpoints to BigQuery**
4. **Execute merge SQL for all 28 pairs**
5. **Download merged outputs**

---

## DECISIONS NEEDED FROM CE

**None** - Full authorization received for:
- ✅ Polars test execution
- ✅ 27-pair rollout if test succeeds
- ✅ BigQuery ETL fallback if test fails (no additional approval needed)

**Autonomous execution authority granted.**

---

## TIMELINE TO 100% READY

### Optimistic (Polars Succeeds)
- **23:10-23:44**: EURUSD Polars test (34 min)
- **23:44-23:50**: CE/EA validation (6 min)
- **23:50-00:57**: 27-pair extraction (4× parallel, 67 min)
- **00:57-02:30**: 27-pair merge (Polars, ~93 min estimated)
- **Total**: ~3.3 hours from now
- **Complete by**: ~02:30 UTC December 12

### Conservative (Polars Fails, BigQuery ETL)
- **23:10-23:44**: EURUSD Polars test (34 min)
- **23:44-23:50**: Failure analysis (6 min)
- **23:50-05:30**: BigQuery ETL for all 28 pairs (5.7 hours)
- **Total**: ~6.3 hours from now
- **Complete by**: ~05:30 UTC December 12

---

## SUCCESS CRITERIA

**Polars Test Success** (Current Task):
- ✅ All 9 criteria from CE Directive 2255 met
- ✅ Report delivered to CE + EA with recommendation

**27-Pair Rollout Success**:
- ✅ All 28 pairs extracted (668 files each)
- ✅ All 28 pairs merged (~6,500 columns, 49 targets each)
- ✅ QA validation passed for all outputs
- ✅ Ready for Step 7 (Stability Selection)

---

*Last updated by CE - December 11, 2025 23:15 UTC*
*Session: df480dab-e189-46d8-be49-b60b436c2a3e*
*Status: EXECUTING Polars test per CE Directive 2305 + EA Implementation Specs*
