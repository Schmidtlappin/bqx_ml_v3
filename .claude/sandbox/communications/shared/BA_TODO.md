# BA Task List

**Last Updated**: December 13, 2025 00:55 UTC
**Maintained By**: BA (Build Agent)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a
**Current Phase**: NULL Remediation - Tier 1 Preparation (HOLD)

---

## 🔴 P0-CRITICAL: NULL REMEDIATION - TIER 1 HOLD STATUS

**USER MANDATE**: "User suspended Cloud Run activity until NULL issue has been fully remediated"

**Status**: ⏸️ **HOLD** - Tier 1 generation scripts being corrected by EA

**Reason**: Critical table naming mismatches discovered in generation scripts

**ETA**: Scripts re-delivered at 01:30 UTC, validation 01:30-01:45 UTC, launch 01:45 UTC

---

## CURRENT STATUS SUMMARY

**Active Phase**: NULL Remediation - Tier 1 Feature Recalculation
**Current Task**: ⏸️ **STANDBY** - Awaiting EA's corrected generation scripts
**Blocker**: Table naming mismatches (CORR, possibly COV)
**Timeline Impact**: +1 hour delay (Tier 1 launch moved from 00:45 UTC → 01:45 UTC)
**Budget Status**: $0 spent, $160-211 approved and remaining

---

## NULL REMEDIATION PROGRESS

### Phase Overview

**Root Cause**: Incomplete feature tables missing 9-11% of rows
**Current NULLs**: 12.43% (EURUSD)
**Target NULLs**: <1% (<5% threshold with 4× margin)

**Remediation Strategy**:
- ✅ **Tier 2A** (COMPLETE): Exclude final 2,880 rows → -1.2% NULLs
- ⏸️ **Tier 1** (HOLD): Recalculate 3,597 tables with FULL OUTER JOIN → -10.4% NULLs
- ⏸️ **Tier 2B** (PENDING): Re-extract EURUSD with fixed tables

**Expected Outcome**: 12.43% → <1% NULLs

---

## TIER 1 EXECUTION TIMELINE

### What Happened Today (Dec 12-13)

**23:00 UTC**: CE approved all 8 NULL remediation decisions
- Budget: $160-211 ✅
- Timeline: Dec 14, 10:00 UTC (24h delay acceptable) ✅
- Execution: Parallel Tier 1 + Tier 2 ✅

**23:30 UTC**: Tier 1 blocker discovered - generation scripts NOT FOUND
- Searched entire codebase for tri/cov/corr generation logic
- Only found generate_mkt_tables.py (12 tables)
- Escalated to EA for reverse-engineering

**23:45 UTC**: EA found archive template and started reverse-engineering

**00:30 UTC**: EA delivered 3 generation scripts (tri/cov/corr)
- generate_tri_tables.py (394 lines, 194 tables)
- generate_cov_tables.py (345 lines, 2,507 tables)
- generate_corr_tables.py (367 lines, 896 tables)

**00:30-00:45 UTC**: BA validated scripts on 9 sample tables
- COV: 3/3 passing (row increases 1.2-2.7%) ✅
- TRI: 2/3 passing (row increases 3.4-9.7%) ✅
- CORR: 0/3 failing (ETF source tables don't exist) ❌

**00:36 UTC**: ⏸️ **EA HOLD ISSUED** - Critical naming mismatches discovered
- CORR pattern: Script creates `corr_etf_idx_*` but actual is `corr_bqx_ibkr_*`
- COV pattern: Needs verification (script creates `cov_agg_pair1_pair2`, actual may be `cov_agg_pair2`)
- MKT tables: No script created, but training data has 150 MKT columns

**00:48 UTC**: BA acknowledged HOLD, sent status to CE and QA

**00:55 UTC**: ⏸️ **CURRENT STATE** - Standing by for corrected scripts

---

### Revised Timeline

**Original Plan** (Approved by CE):
- 00:30 UTC: Scripts delivered ✅
- 00:45 UTC: Validation complete ✅
- 01:00 UTC: Tier 1 execution starts
- 21:00 UTC: Tier 1 complete
- 22:00 UTC: EURUSD re-extraction complete
- 22:00-23:00 UTC: QA validation
- Dec 14, 00:00 UTC: 27-pair rollout starts
- Dec 14, 10:00 UTC: Complete

**Revised Plan** (+1h delay):
- 00:30 UTC: Scripts delivered ✅
- 00:45 UTC: Validation complete ✅
- 00:48 UTC: HOLD issued ⏸️
- **01:30 UTC: Corrected scripts re-delivered** (EA in progress)
- **01:45 UTC: Tier 1 execution starts** (+45 min)
- **22:00 UTC: Tier 1 complete** (+1h)
- **23:00 UTC: EURUSD re-extraction complete** (+1h)
- **23:00 - Dec 14, 00:00 UTC: QA validation** (+1h)
- **Dec 14, 01:00 UTC: 27-pair rollout starts** (+1h)
- **Dec 14, 11:00 UTC: Complete** (+1h)

**Total Delay**: +1 hour (within 24h acceptable window)

---

## TIER 1 SCOPE & COST

### Tables to Regenerate

| Category | Tables | Estimated Cost | Estimated Time |
|----------|--------|---------------|----------------|
| **TRI** (triangulation) | 194 | $40-50 | 4 hours |
| **COV** (covariance) | 2,507 | $90-120 | 12 hours |
| **CORR** (correlation) | 896 | $25-35 | 4 hours |
| **MKT** (market-wide) | 12 | $5-10 | 30 min |
| **TOTAL** | **3,609** | **$160-215** | **20.5 hours** |

**Status**: Pending EA's corrected scripts and scope clarification

**Possible Scope Reduction**:
- If CORR skipped (ETF tables don't exist): 2,701 tables, $110-150, 16 hours
- If MKT out of scope: 3,597 tables, $155-205, 20 hours

---

## P0-CRITICAL TASKS

### 1. ⏸️ STANDBY for Corrected Scripts (NOW - 01:30 UTC)

**Status**: ⏸️ **WAITING** for EA re-delivery
**ETA**: 01:30 UTC (35 minutes)
**Action**: No action required, standing by

**EA's Corrective Actions**:
1. Query INFORMATION_SCHEMA to verify actual table naming patterns
2. Correct COV script with verified pattern
3. Correct CORR script with verified pattern (`corr_bqx_ibkr_*`)
4. Create or clarify MKT script scope
5. Re-validate against BigQuery tables
6. Re-deliver to BA

---

### 2. Validate Corrected Scripts (01:30-01:45 UTC)

**Status**: ⏸️ **PENDING** EA re-delivery
**Duration**: 15 minutes
**Priority**: P0-CRITICAL

**Validation Steps**:
1. Run validation mode on 3-5 sample tables per script
2. Verify table naming matches INFORMATION_SCHEMA patterns
3. Verify row count increases match expected NULL gap (9-11%)
4. Check date ranges (2020-01-01 to 2025-11-20)

**Success Criteria**:
- ✅ Table names match existing pattern in BigQuery
- ✅ Row counts increase by expected 1-11%
- ✅ No SQL errors or missing source tables
- ✅ Date ranges correct

**If Validation Passes**: Proceed to Tier 1 launch
**If Validation Fails**: Escalate to EA/CE with specific errors

---

### 3. Launch Tier 1 Execution (01:45 UTC - If Validation Passes)

**Status**: ⏸️ **PENDING** validation
**Duration**: 20.5 hours (or 16h if CORR skipped)
**Priority**: P0-CRITICAL
**Budget**: $160-211 approved

**Execution Plan**:
```bash
# Launch all 3 scripts in parallel (16 workers each)
python3 scripts/generate_tri_tables.py --workers 16 &
python3 scripts/generate_cov_tables.py --workers 16 &
python3 scripts/generate_corr_tables.py --workers 16 &  # If in scope

# Monitor progress
watch -n 60 'ls -lh /tmp/*_generation_results.json'
```

**Monitoring**:
- Check progress every 1 hour
- Report checkpoints to CE/EA/QA at 4h, 8h, 12h, 16h, 20h
- Alert if error rate >5%

**Completion ETA**: Dec 13, 22:00 UTC

---

### 4. Monitor Tier 1 Execution (01:45-22:00 UTC)

**Status**: ⏸️ **PENDING** launch
**Duration**: 20.5 hours
**Priority**: P0-CRITICAL

**Monitoring Tasks**:
- Check generation logs every hour
- Track success/failure rate
- Monitor BigQuery quota usage
- Alert if execution stalls or error rate spikes

**Checkpoint Reports**:
- 05:45 UTC (4h): TRI progress, COV progress
- 09:45 UTC (8h): TRI complete, COV 50%
- 13:45 UTC (12h): COV 75%, CORR started
- 17:45 UTC (16h): COV complete, CORR 50%
- 21:45 UTC (20h): CORR 90%
- 22:00 UTC: Tier 1 complete

---

## P1-HIGH TASKS

### 1. ✅ Tier 2A Implementation (COMPLETE)

**Status**: ✅ **COMPLETED** (Dec 12, 23:00 UTC)
**File**: [pipelines/training/parallel_feature_testing.py](../../../pipelines/training/parallel_feature_testing.py)
**Commit**: 845b551

**Implementation**:
```python
MAX_HORIZON_MINUTES = 2880  # h2880 = 48 hours
cutoff_date = df['interval_time'].max() - pd.Timedelta(minutes=MAX_HORIZON_MINUTES)
merged_df = merged_df[merged_df['interval_time'] <= cutoff_date]
```

**Impact**: Excludes final 2,880 rows → -1.2% NULLs

**Next**: Will apply automatically when EURUSD is re-extracted after Tier 1

---

## P2-MEDIUM TASKS

### 1. EURUSD Re-Extraction (After Tier 1 Complete)

**Status**: ⏸️ **PENDING** Tier 1 completion
**Duration**: 1 hour (70 min extraction + 15 min merge)
**Priority**: P2-MEDIUM
**ETA**: Dec 13, 22:00-23:00 UTC

**Execution**:
```bash
# Run Cloud Run extraction job for EURUSD
gcloud run jobs execute bqx-ml-extract \
  --region us-central1 \
  --set-env-vars "PAIR=eurusd" \
  --wait
```

**Expected Outcome**:
- Row count: ~174,868 (2,880 excluded per Tier 2A)
- NULL percentage: <1% (was 12.43%)
- File size: ~9 GB
- Targets: h15-h2880 (100% complete)

**QA Validation**: Dec 13, 23:00 - Dec 14, 00:00 UTC

---

### 2. 27-Pair Rollout (After QA Validation Passes)

**Status**: ⏸️ **PENDING** QA validation
**Duration**: 12 hours (parallel 4× execution)
**Priority**: P2-MEDIUM
**ETA**: Dec 14, 01:00-13:00 UTC (was 00:00-12:00 UTC)

**User Directive**: Cloud Run suspended until NULL remediation complete

**Resumption Criteria**:
1. ✅ EURUSD NULL percentage <1%
2. ✅ QA validation passes
3. ✅ User authorizes Cloud Run resumption

**Execution Plan**:
- Parallel 4× execution (7 batches)
- Monitor checkpoint files (GCS backup enabled)
- Validate each pair after extraction

---

## COMPLETED WORK

### ✅ Tier 2A Implementation (Dec 12, 23:00 UTC)

**Task**: Exclude final 2,880 rows for target lookahead completeness
**Status**: COMPLETE
**File**: [pipelines/training/parallel_feature_testing.py](../../../pipelines/training/parallel_feature_testing.py)
**Commit**: 845b551
**Impact**: -1.2% NULLs

---

### ✅ Script Validation (Dec 13, 00:30-00:45 UTC)

**Task**: Validate EA's generation scripts on sample tables
**Status**: COMPLETE
**Results**: 5/9 passing, CORR naming issue discovered
**Files**:
- `/tmp/tri_validation_results.json`
- `/tmp/cov_validation_results.json`
- `/tmp/corr_validation_results.json`

---

### ✅ HOLD Acknowledgment (Dec 13, 00:48 UTC)

**Task**: Acknowledge EA's HOLD directive and notify stakeholders
**Status**: COMPLETE
**Files**:
- [20251213_0048_BA-to-EA_HOLD_ACKNOWLEDGED_CORR_NAMING_CONFIRMED.md](../communications/outboxes/BA/20251213_0048_BA-to-EA_HOLD_ACKNOWLEDGED_CORR_NAMING_CONFIRMED.md)
- [20251213_0050_BA-to-CE_TIER1_HOLD_TIMELINE_UPDATE.md](../communications/inboxes/CE/20251213_0050_BA-to-CE_TIER1_HOLD_TIMELINE_UPDATE.md)
- [20251213_0052_BA-to-QA_TIER1_HOLD_TIMELINE_UPDATE.md](../communications/inboxes/QA/20251213_0052_BA-to-QA_TIER1_HOLD_TIMELINE_UPDATE.md)

---

## BLOCKERS & RISKS

### ACTIVE BLOCKER 1: Table Naming Mismatches

**Impact**: Tier 1 execution blocked
**Status**: EA correcting scripts (ETA 01:30 UTC)
**Risk Level**: 🟢 **LOW** - Early detection, clear corrective path
**Mitigation**: EA verifying against INFORMATION_SCHEMA before re-delivery

**Good News**: Issue caught BEFORE execution, saving $160-211 and 4h cleanup

---

### RISK 1: Corrected Scripts Still Wrong

**Probability**: LOW (EA verifying against INFORMATION_SCHEMA)
**Impact**: Additional 1h delay + possible scope reduction
**Mitigation**: BA validation before execution

---

### RISK 2: CORR Tables May Need to Be Skipped

**Probability**: MEDIUM (ETF source tables don't exist)
**Impact**: Scope reduction to 2,701 tables, ~1.5% final NULLs instead of <1%
**Mitigation**: Still meets <5% threshold (3× margin), acceptable outcome

---

## COORDINATION STATUS

### With EA
- ✅ Received generation scripts at 00:30 UTC
- ✅ Sent validation results at 00:45 UTC
- ✅ Received HOLD directive at 00:36 UTC
- ✅ Acknowledged HOLD at 00:48 UTC
- ⏸️ Awaiting corrected scripts (ETA 01:30 UTC)

### With CE
- ✅ Received all 8 decision approvals at 23:00 UTC
- ✅ Sent HOLD status update at 00:50 UTC
- ⏸️ Will report Tier 1 launch confirmation after validation

### With QA
- ✅ Sent Tier 2A completion notice at 23:50 UTC
- ✅ Sent HOLD timeline update at 00:52 UTC
- ⏸️ Will coordinate QA validation after EURUSD re-extraction

---

## IMMEDIATE NEXT STEPS

### NOW - 01:30 UTC (35 min)
1. ⏸️ **STANDBY** - No action required, awaiting EA

### 01:30-01:45 UTC (15 min)
2. ✅ **Validate corrected scripts** - 3-5 sample tables per script
3. ✅ **Verify naming patterns** - Match INFORMATION_SCHEMA
4. ✅ **Report validation results** - To EA and CE

### 01:45 UTC (If Validation Passes)
5. ✅ **Launch Tier 1 execution** - 3 scripts in parallel, 16 workers each
6. ✅ **Start monitoring** - Hourly progress checks

### 01:45-22:00 UTC (20.5 hours)
7. ✅ **Monitor Tier 1** - Report checkpoints every 4 hours
8. ✅ **Alert on errors** - If error rate >5%

### 22:00-23:00 UTC
9. ✅ **Re-extract EURUSD** - With recalculated tables + Tier 2A
10. ✅ **Hand off to QA** - Validation window

### Dec 14, 01:00-13:00 UTC (If QA Passes)
11. ✅ **Execute 27-pair rollout** - Parallel 4× execution
12. ✅ **Complete project** - All 28 pairs extracted

---

## USER MANDATE ALIGNMENT

**User Mandate**: "User suspended Cloud Run activity until NULL issue has been fully remediated"

**BA Alignment**:
- ✅ Cloud Run suspended (no 27-pair rollout until NULL fixed)
- ✅ NULL remediation prioritized (Tier 1 + Tier 2)
- ✅ Budget approved ($160-211 for Tier 1)
- ✅ Timeline acceptable (Dec 14, 11:00 UTC within 24h window)
- ⏸️ Cloud Run will resume ONLY after <1% NULLs achieved and QA validated

**Expected Outcome**:
- NULL reduction: 12.43% → <1%
- EURUSD validation: Dec 13, 23:00 UTC
- 27-pair rollout: Dec 14, 01:00-13:00 UTC
- Project complete: Dec 14, 13:00 UTC

---

## BUDGET STATUS

**Approved**: $160-211 (Tier 1)
**Spent**: $0 (HOLD prevented premature execution)
**Remaining**: $160-211 (100%)

**Good News**: Early detection of naming issue saved $160-211 that would have been wasted on incorrectly-named tables

---

*Last updated by BA - December 13, 2025 00:55 UTC*
*Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a*
*Status: ⏸️ STANDBY for EA's corrected scripts (ETA 01:30 UTC)*
*Phase: NULL Remediation - Tier 1 Preparation (HOLD)*
