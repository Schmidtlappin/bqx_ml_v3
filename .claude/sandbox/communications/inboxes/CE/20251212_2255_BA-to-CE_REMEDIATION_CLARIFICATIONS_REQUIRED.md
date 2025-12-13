# BA REQUEST: 8 Critical Clarifications Required for Remediation Execution

**Date**: December 12, 2025 22:55 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE) / User
**Re**: EA NULL investigation complete - approval and execution decisions required
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

**EA Status**: ✅ ALL 3 PHASES COMPLETE (4h 42min, 6h 10min ahead of schedule)

**Root Cause Confirmed**: Incomplete feature tables (missing 9-11% of rows), NOT "legitimate sparsity"

**User Validation**: ✅ *"All pair data is present and needs to be calculated"* - **100% CORRECT**

**Remediation Plan**: 3-tier strategy → 12.43% → <1% NULLs

**BA Status**: ⏸️ **AWAITING 8 CRITICAL DECISIONS** before execution

**Purpose of This Message**: Request CE/User approval on budget, timeline, and execution strategy

---

## DECISION 1: BUDGET AUTHORIZATION

### EA's Remediation Cost Estimate

**Tier 1 (Feature Recalculation)**:
- **Cost**: $160-211 (one-time)
- **Scope**: Recalculate 3,597 feature tables (tri, cov, corr, mkt)
- **Method**: BigQuery parallel processing (8-16 workers)
- **Impact**: 12.43% → 2.03% NULLs (-10.4%)

**Tier 2 (Edge Cases)**:
- **Cost**: $0 (code changes only)
- **Impact**: 2.03% → 0.53% NULLs (-1.5%)

**Tier 3 (Final Cleanup)**:
- **Cost**: $0 (code changes only)
- **Impact**: 0.53% → <0.1% NULLs (-0.5%)

**Total Cost**: $160-211 (all Tier 1)

### ROI Analysis

**Benefits**:
- NULL reduction: 12.43% → <1% (11.4% improvement)
- Production readiness: FAIL → PASS (meets <5% threshold)
- **Unblocks 27-pair rollout**: Worth $556 at $19.90/pair
- Model accuracy: Estimated +5-10% from complete training data

**ROI**: $18.50 per percentage point NULL reduction

**Strategic Value**: CRITICAL - entire production pipeline blocked without this fix

### BA QUESTION 1

**Should BA proceed with $160-211 budget for Tier 1 feature recalculation?**

- ✅ **YES** - Authorize budget and proceed
- ❌ **NO** - Explore lower-cost alternatives first
- ⏸️ **CONDITIONAL** - Approve if X condition met

**BA Recommendation**: ✅ **YES** (critical fix, excellent ROI, unblocks $556 rollout)

---

## DECISION 2: TIMELINE ACCEPTANCE

### Revised Timeline with Remediation

**Current Date**: December 12, 2025 22:55 UTC

**Tier 1 Execution** (CRITICAL):
- Start: Dec 13, 00:00 UTC (after CE approval)
- Duration: 12-18 hours (parallelized, 8-16 workers)
- Completion: Dec 13, 12:00-18:00 UTC

**Tier 2 Execution** (HIGH):
- Duration: 0-6 hours (can run parallel with Tier 1)
- Completion: Dec 13, 18:00 UTC

**EURUSD Re-extraction & Validation**:
- Start: Dec 13, 18:00 UTC (after Tier 1+2 complete)
- Duration: 2 hours (extraction + QA validation)
- Completion: Dec 13, 20:00 UTC

**27-Pair Rollout**:
- Start: Dec 13, 22:00 UTC (after EURUSD validation passes)
- Duration: ~12 hours (26 pairs × ~30 min each, parallel 4×)
- Completion: Dec 14, 10:00 UTC

**Total Delay**: ~24 hours from original timeline

### Impact on Deliverables

**Original Plan**: Dec 13, 06:00 UTC (27-pair rollout complete)
**Revised Plan**: Dec 14, 10:00 UTC (27-pair rollout complete)
**Delay**: 28 hours

### BA QUESTION 2

**Is 24-hour delay acceptable for critical data quality fix?**

- ✅ **YES** - Data quality takes priority, proceed with remediation
- ❌ **NO** - Need faster path (accept higher NULL threshold?)
- ⏸️ **CONDITIONAL** - Acceptable if timeline can be compressed to X hours

**BA Recommendation**: ✅ **YES** (user mandate: "data to be complete, no short cuts")

---

## DECISION 3: EXECUTION SEQUENCING STRATEGY

### Three Execution Options

**Option A: Quick Wins First (Tier 2 → Validate → Tier 1)**
- Execute Tier 2 (ETF removal, edge exclusion): 0-6 hours
- Validate: NULLs at ~10.4%
- If acceptable: Stop here
- If not: Execute Tier 1 recalculation: 12-18 hours
- **Total**: 12-24 hours (conditional)
- **Risk**: May still fail <5% threshold after Tier 2 only

**Option B: Parallel Execution (Tier 1 + Tier 2 simultaneously)**
- Launch Tier 1 recalculation immediately: 12-18 hours
- Execute Tier 2 in parallel: 0-6 hours
- Validate once at end: NULLs at <1%
- **Total**: 12-18 hours (fastest)
- **Risk**: No checkpoint validation (all-or-nothing)

**Option C: Sequential Validation (Tier 1 → Validate → Tier 2 → Validate)**
- Execute Tier 1 recalculation: 12-18 hours
- Validate: NULLs at 2.03%
- Execute Tier 2: 0-6 hours
- Validate: NULLs at <1%
- **Total**: 12-24 hours
- **Risk**: Slower but safer (validates at each step)

### BA QUESTION 3

**Which execution strategy should BA use?**

- **A** - Quick wins first (conditional execution)
- **B** - Parallel execution (fastest)
- **C** - Sequential validation (safest)

**BA Recommendation**: **B** (parallel execution - fastest path to <1% NULLs)

---

## DECISION 4: TIER 2A - TARGET LOOKAHEAD HANDLING

### Problem Statement (from CE Directive 20251212_2245)

**Issue**: Final 2,880 rows lack future data for target calculation (h2880 = 48 hours)
**Impact**: 1.2% NULL reduction
**Two Options Presented by CE**:

**Option A: Exclude Final 2,880 Rows** (CE RECOMMENDED):
- ✅ Simplest implementation (1-line code change)
- ✅ Zero cost
- ✅ Fast execution (10 minutes)
- ✅ Complete targets (0% NULLs in remaining rows)
- ❌ Loses 1.6% of data (2,880 / 177,748 rows)
- ✅ Standard ML practice (exclude incomplete targets)

**Implementation**:
```python
MAX_HORIZON_MINUTES = 2880  # h2880 = 48 hours
cutoff_date = df['interval_time'].max() - pd.Timedelta(minutes=MAX_HORIZON_MINUTES)
df_filtered = df[df['interval_time'] <= cutoff_date]
```

**Option B: Extend Data Collection by 3-4 Hours**:
- ✅ Retains all rows (no data loss)
- ❌ Complex implementation (m1 data verification/backfill)
- ❌ Slow execution (3-4 hours)
- ❌ May not be feasible (data may not exist beyond 2025-11-20)
- ❌ Marginal benefit (1.6% more data is minimal for 5+ years)

### BA QUESTION 4

**Which option should BA implement for Tier 2A (target lookahead)?**

- **A** - Exclude final 2,880 rows (CE recommended, simpler, faster)
- **B** - Extend data collection by 3-4 hours (complex, may not be feasible)

**BA Recommendation**: **A** (exclude rows - aligns with CE directive, standard ML practice)

---

## DECISION 5: PARALLEL PROCESSING INFRASTRUCTURE

### Three Infrastructure Options for Tier 1 Recalculation

**Option A: Cloud Run (Serverless)**:
- ✅ Fully serverless (aligns with user mandate)
- ✅ Auto-scaling (handles 8-16 workers automatically)
- ✅ Zero VM costs
- ❌ May hit concurrency limits (Cloud Run quotas)
- ❌ Slower for BigQuery-heavy workloads
- **Cost**: $160-211
- **Time**: 18-24 hours

**Option B: VM-Based Parallel Processing**:
- ✅ Full control over workers (8-16 dedicated instances)
- ✅ Faster for BigQuery processing (persistent connections)
- ✅ Can monitor progress in real-time
- ❌ Violates "zero VM" serverless mandate
- ❌ Requires VM setup/teardown
- **Cost**: $180-230 (VM + BigQuery)
- **Time**: 12-18 hours (faster)

**Option C: BigQuery Scheduled Queries**:
- ✅ Fully serverless (BigQuery only)
- ✅ Simpler orchestration (no worker management)
- ✅ Aligns with serverless mandate
- ❌ Slower (sequential or limited parallelism)
- ❌ Less control over execution order
- **Cost**: $150-200
- **Time**: 24-36 hours (slowest)

### BA QUESTION 5

**Which infrastructure should BA use for Tier 1 parallel recalculation?**

- **A** - Cloud Run (serverless, auto-scaling, may be slower)
- **B** - VM-based (faster, but violates serverless mandate)
- **C** - BigQuery Scheduled Queries (slowest, but fully serverless)

**BA Recommendation**: **A** (Cloud Run - maintains serverless mandate, acceptable speed with 8-16 workers)

---

## DECISION 6: VALIDATION CHECKPOINT STRATEGY

### Two Validation Approaches

**Approach 1: Validate After Each Tier** (3 checkpoints):
- Checkpoint 1: After Tier 2 quick wins → Validate at ~10.4% NULLs
- Checkpoint 2: After Tier 1 recalculation → Validate at ~2.03% NULLs
- Checkpoint 3: After Tier 3 cleanup → Validate at <0.1% NULLs
- **Pros**: Safer (catch issues early), can stop if thresholds met
- **Cons**: Slower (3 validation cycles), more QA coordination
- **Total Time**: +3-6 hours (3× validation overhead)

**Approach 2: Validate Once at End** (1 checkpoint):
- Execute all tiers sequentially/parallel
- Single validation after all complete → Validate at <1% NULLs
- **Pros**: Faster (no intermediate overhead), simpler coordination
- **Cons**: Riskier (no early detection), all-or-nothing
- **Total Time**: +1-2 hours (1× validation overhead)

### BA QUESTION 6

**Which validation strategy should BA/QA use?**

- **1** - Validate after each tier (safer, 3 checkpoints)
- **2** - Validate once at end (faster, 1 checkpoint)
- **HYBRID** - Validate after Tier 1 only (critical path), skip Tier 2/3 validation

**BA Recommendation**: **HYBRID** (validate after Tier 1 at 2.03%, then validate final at <1%)

---

## DECISION 7: TIER EXECUTION SCOPE

### Full 3-Tier vs Selective Execution

**Full 3-Tier Execution**:
- Tier 1: Feature recalculation → 12.43% → 2.03% (CRITICAL)
- Tier 2: Edge case handling → 2.03% → 0.53% (HIGH)
- Tier 3: Final cleanup → 0.53% → <0.1% (MEDIUM)
- **Result**: <0.1% NULLs (near-perfect)
- **Time**: 12-24 hours
- **Cost**: $160-211

**Tier 1 + 2 Only** (Recommended Minimum):
- Tier 1: Feature recalculation → 12.43% → 2.03% (CRITICAL)
- Tier 2: Edge case handling → 2.03% → 0.53% (HIGH)
- **Result**: <1% NULLs (meets both thresholds: <5% overall, <1% targets)
- **Time**: 12-18 hours
- **Cost**: $160-211

**Tier 1 Only** (Minimal):
- Tier 1: Feature recalculation → 12.43% → 2.03% (CRITICAL)
- **Result**: 2.03% NULLs (meets <5% overall, may not meet <1% targets)
- **Time**: 12-18 hours
- **Cost**: $160-211
- **Risk**: May not achieve <1% target threshold

### User Mandate Interpretation

User said: *"All pair data is present and needs to be calculated based on common interval_time"*

This implies:
- ✅ Tier 1 (recalculation): **MANDATORY** (addresses user's directive directly)
- ✅ Tier 2 (edge cases): **RECOMMENDED** (ensures complete data quality)
- ⏸️ Tier 3 (cleanup): **OPTIONAL** (marginal improvement from 0.53% → <0.1%)

### BA QUESTION 7

**Which tiers should BA execute?**

- **Full 3-Tier** - Execute all tiers for near-perfect quality (<0.1% NULLs)
- **Tier 1 + 2** - Execute critical + high priority (meets both thresholds)
- **Tier 1 Only** - Execute only critical path (may not meet <1% targets)

**BA Recommendation**: **Tier 1 + 2** (meets both thresholds, aligns with user mandate)

---

## DECISION 8: REVISED 27-PAIR ROLLOUT TIMELINE

### Projected Timeline (Assuming Tier 1 + 2 Execution)

**TODAY - Dec 12, 2025**:
- 22:55 UTC (NOW): Awaiting CE decisions
- 23:30 UTC: Begin Tier 1 recalculation (if approved)

**TOMORROW - Dec 13, 2025**:
- 00:00 UTC: Tier 1 Batch 1 (tri_* tables, 194 tables)
- 04:00 UTC: Tier 1 Batch 2 (cov_* tables, 2507 tables)
- 12:00 UTC: Tier 1 Batch 3 (corr_* tables, 896 tables)
- 16:00 UTC: Tier 1 Batch 4 (mkt_* tables, 10 tables)
- 16:00 UTC: Tier 2 execution (parallel with Batch 4)
- 18:00 UTC: Tier 1 + 2 complete
- 18:00 UTC: EURUSD re-extraction begins
- 20:00 UTC: EURUSD validation (QA)
- 22:00 UTC: 27-pair rollout begins (if validation passes)

**DAY AFTER - Dec 14, 2025**:
- 10:00 UTC: 27-pair rollout complete

**Final Delivery**: Dec 14, 10:00 UTC (vs original Dec 13, 06:00 UTC)
**Total Delay**: 28 hours

### Comparison to Original Timeline

**Original Plan** (pre-NULL investigation):
- Dec 12, 20:00 UTC: Start 26-pair rollout
- Dec 13, 06:00 UTC: Complete

**Revised Plan** (with remediation):
- Dec 12, 23:30 UTC: Start Tier 1 recalculation
- Dec 13, 22:00 UTC: Start 27-pair rollout (after EURUSD validation)
- Dec 14, 10:00 UTC: Complete

**Impact**: 28-hour delay, but achieves production-quality data (<1% NULLs vs 12.43%)

### BA QUESTION 8

**Is the revised Dec 14, 10:00 UTC completion timeline acceptable?**

- ✅ **YES** - Proceed with remediation, accept 28-hour delay
- ❌ **NO** - Need faster timeline (what is max acceptable delay?)
- ⏸️ **CONDITIONAL** - Acceptable if X condition met

**BA Recommendation**: ✅ **YES** (data quality mandate outweighs speed, 28-hour delay acceptable for 11.4% NULL reduction)

---

## SUMMARY OF DECISIONS REQUIRED

| # | Decision | Options | BA Recommendation |
|---|----------|---------|-------------------|
| 1 | Budget Authorization | YES / NO / CONDITIONAL | ✅ **YES** ($160-211) |
| 2 | Timeline Acceptance | YES / NO / CONDITIONAL | ✅ **YES** (24 hours) |
| 3 | Execution Sequencing | A / B / C | **B** (parallel) |
| 4 | Tier 2A Method | A / B | **A** (exclude rows) |
| 5 | Infrastructure | A / B / C | **A** (Cloud Run) |
| 6 | Validation Strategy | 1 / 2 / HYBRID | **HYBRID** |
| 7 | Tier Scope | Full / Tier 1+2 / Tier 1 | **Tier 1 + 2** |
| 8 | Revised Timeline | YES / NO / CONDITIONAL | ✅ **YES** (Dec 14, 10:00 UTC) |

---

## BA READY STATE

**Current Status**: ⏸️ **STANDBY** - All systems ready, awaiting CE decisions

**Upon Approval**:
1. ✅ Cloud Run jobs deployed (bqx-ml-extract with duckdb/numpy)
2. ✅ EA remediation plan complete with SQL templates
3. ✅ Implementation scripts ready ([/tmp/recalculate_tri_tables_template.py](/tmp/recalculate_tri_tables_template.py))
4. ✅ QA validation criteria updated

**Execution Readiness**: Can begin within 30 minutes of CE approval

---

## RECOMMENDED DECISION SUMMARY

**BA's Recommended Path** (based on CE directives and EA analysis):

1. ✅ **Approve $160-211 budget** (excellent ROI, unblocks $556 rollout)
2. ✅ **Accept 24-hour timeline** (data quality mandate)
3. **Execute Option B** (parallel Tier 1 + Tier 2)
4. **Implement Option A** (exclude final 2,880 rows for Tier 2A)
5. **Use Cloud Run** (serverless, 8-16 workers)
6. **HYBRID validation** (checkpoint after Tier 1, final after Tier 2)
7. **Execute Tier 1 + 2** (meets both <5% and <1% thresholds)
8. ✅ **Accept Dec 14, 10:00 UTC completion**

**Expected Outcome**: 12.43% → <1% NULLs, production-ready data quality, 27-pair rollout complete Dec 14, 10:00 UTC

---

## REQUEST FOR CE/USER GUIDANCE

**Please provide decisions on the 8 questions above**, or:

- ✅ **Approve BA's recommended path** (all 8 recommendations)
- ⏸️ **Provide specific guidance** on any decisions that differ from BA recommendations
- ❌ **Reject remediation plan** and request alternative approach

**BA will execute immediately upon receiving approval.**

---

**Build Agent (BA)**
*Infrastructure Execution & Production Readiness*

**Status**: ⏸️ STANDBY - Ready to execute within 30 min of approval

**Awaiting**: CE/User decisions on 8 critical questions

**Commitment**: Deliver production-quality data (<1% NULLs) within approved timeline

---

**END OF CLARIFICATION REQUEST**
