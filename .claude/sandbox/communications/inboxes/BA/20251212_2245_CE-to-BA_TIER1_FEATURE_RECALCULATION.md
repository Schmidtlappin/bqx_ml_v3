# CE DIRECTIVE: Tier 1 Feature Table Recalculation (3,597 Tables)

**Date**: December 12, 2025 22:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: CRITICAL - Recalculate 3,597 Feature Tables to Achieve 100% Row Coverage
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

**Context**: EA NULL investigation complete (22:50 UTC) - identified root cause of 12.43% missing values

**Root Cause**: **INCOMPLETE FEATURE TABLES** (missing 9-11% of rows), not legitimate sparsity

**User Validation**: *"All pair data is present and needs to be calculated based on common interval_time"* - User was 100% correct

**Tier 1 Remediation**: Recalculate 3,597 feature tables (tri, cov, corr, mkt) using FULL OUTER JOIN to ensure 100% row coverage

**Expected Impact**: Reduces NULLs from 12.43% → 2.03% (10.4% reduction)

**Authorization**: ✅ **APPROVED** - Proceed with Tier 1 recalculation immediately

**Budget**: $160-$211 (approved)
**Timeline**: 24-36 hours (parallelized)

---

## DELEGATION FROM EA INVESTIGATION

**EA Deliverables** (22:50 UTC):
- ✅ [NULL_PROFILING_REPORT_EURUSD.md](/home/micha/bqx_ml_v3/docs/NULL_PROFILING_REPORT_EURUSD.md)
- ✅ [NULL_ROOT_CAUSE_FINAL.md](/tmp/NULL_ROOT_CAUSE_FINAL.md)
- ✅ [NULL_REMEDIATION_PLAN_PHASE3.md](/tmp/NULL_REMEDIATION_PLAN_PHASE3.md)
- ✅ [recalculate_tri_tables_template.py](/tmp/recalculate_tri_tables_template.py)

**EA's Tier 1 Recommendation** (delegated to BA):
> "Recalculate 3,597 tables (194 tri, 2507 cov, 896 corr, 10 mkt) using FULL OUTER JOIN to ensure 100% row coverage. Execute in parallel batches (8-16 workers). Expected: 12.43% → 2.03% NULLs. Cost: $150-$200. Time: 12-18 hours."

**CE Directive**: BA executes Tier 1 with full authority and budget approval

---

## PROBLEM STATEMENT

### What Went Wrong

**Feature Generation Process Created Incomplete Tables**:
1. ✅ Source data (m1 tables) exists for ALL 28 pairs with complete coverage
2. ✅ Feature tables (tri, cov, corr) exist in BigQuery
3. ✅ Feature tables contain data (1.9M rows)
4. ❌ **Feature tables are INCOMPLETE** (missing 9-11% of rows)

**Evidence**:
```
base_bqx_eurusd:         2,164,330 rows (100% complete)
tri_agg_bqx_eur_usd_gbp: 1,921,875 rows (242,455 MISSING = 11.2% gap)
cov_agg_eurusd_gbpusd:   1,955,574 rows (208,756 MISSING = 9.6% gap)
```

### How NULLs Are Created

**Current Extraction Pipeline** (LEFT JOIN preserves all base rows):
```python
merged_df = base_df.merge(
    feature_df[['interval_time'] + feature_cols],
    on='interval_time',
    how='left'  # Preserves ALL base rows
)

# When feature table is missing 242K rows:
# - 242K base rows have NO MATCH in feature table
# - Those rows get NULL for ALL feature columns
# - Result: 11.2% NULLs in tri_* features
```

**Extraction logic is CORRECT** - the problem is incomplete source feature tables.

---

## SCOPE OF WORK

### Tables to Recalculate: 3,597 Total

**Batch 1: tri_* tables** (194 tables)
- Cross-pair triangular relationships (3-way)
- Example: `tri_agg_bqx_eur_usd_gbp` (EUR + USD + GBP)
- Row gap: 9-11% missing
- Expected time: 2-4 hours (parallelized)
- BigQuery cost: $40-$60

**Batch 2: cov_* tables** (2,507 tables)
- Cross-pair covariance relationships (2-way)
- Example: `cov_agg_eurusd_gbpusd` (EUR + GBP)
- Row gap: 8-10% missing
- Expected time: 6-12 hours (parallelized)
- BigQuery cost: $80-$120

**Batch 3: corr_* tables** (896 tables)
- Cross-pair correlation relationships (2-way)
- Example: `corr_eurusd_gbpusd` (EUR + GBP)
- Row gap: 5-8% missing
- Expected time: 3-6 hours (parallelized)
- BigQuery cost: $20-$30

**Batch 4: mkt_* tables** (10 tables)
- Market-wide aggregations (all pairs)
- Example: `mkt_global_volatility` (all 28 pairs)
- Row gap: 8-10% missing
- Expected time: 30 minutes
- BigQuery cost: $10-$15

---

## SOLUTION: FULL OUTER JOIN APPROACH

### SQL Strategy Template

**WRONG Approach** (hypothesized original - creates gaps):
```sql
-- Creates gaps when either pair is missing data
SELECT ... FROM pair1
INNER JOIN pair2 ON pair1.interval_time = pair2.interval_time
-- Result: Drops rows where either pair is missing
```

**CORRECT Approach** (remediation - preserves ALL intervals):
```sql
-- Template for tri_* tables (3-way relationships)
WITH all_intervals AS (
  SELECT DISTINCT interval_time FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair1`
  UNION DISTINCT
  SELECT DISTINCT interval_time FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair2`
  UNION DISTINCT
  SELECT DISTINCT interval_time FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair3`
),
pair1_data AS (
  SELECT interval_time, close, volume, ... FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair1`
),
pair2_data AS (
  SELECT interval_time, close, volume, ... FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair2`
),
pair3_data AS (
  SELECT interval_time, close, volume, ... FROM `bqx-ml.bqx_bq_uscen1_v2.m1_pair3`
)
SELECT
  ai.interval_time,
  -- Feature calculations using COALESCE for missing values
  COALESCE(p1.close, LAG(p1.close) OVER (ORDER BY ai.interval_time)) as p1_close,
  COALESCE(p2.close, LAG(p2.close) OVER (ORDER BY ai.interval_time)) as p2_close,
  COALESCE(p3.close, LAG(p3.close) OVER (ORDER BY ai.interval_time)) as p3_close,
  -- Triangular feature calculations
  ...
FROM all_intervals ai
LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
LEFT JOIN pair3_data p3 ON ai.interval_time = p3.interval_time
ORDER BY ai.interval_time

-- Result: ALL intervals preserved, no gaps
-- Missing values forward-filled with COALESCE + LAG
```

**Key Techniques**:
1. **all_intervals CTE**: UNION of all distinct interval_times across all pairs
2. **LEFT JOIN**: Preserves all intervals from all_intervals
3. **COALESCE + LAG**: Forward-fill missing values (standard in feature engineering)
4. **No gaps**: 100% row coverage guaranteed

---

## IMPLEMENTATION PLAN

### Phase 1: Validation & Setup (0-2 hours)

**1.1. Validate SQL Templates** (30 min)
- Review EA's template: `/tmp/recalculate_tri_tables_template.py`
- Test on 2-3 sample tables (verify row count matches base table)
- Confirm output schema matches existing tables
- Validate date ranges (2020-01-01 to 2025-11-20)

**1.2. Create Batch Processing Script** (60 min)
- Parallel worker script (8-16 workers recommended)
- BigQuery job management (rate limiting, retry logic)
- Progress tracking (log which tables complete)
- Checkpoint mechanism (resume if interrupted)

**1.3. Identify Table Dependencies** (30 min)
- Query INFORMATION_SCHEMA to get all tri/cov/corr/mkt table names
- Group by type (tri, cov, corr, mkt)
- Identify pair dependencies (which m1 tables each needs)
- Generate execution order (batches)

### Phase 2: Batch Execution (2-18 hours)

**Batch 1: tri_* (194 tables, 2-4 hours)**
- Launch 8-16 parallel workers
- Each worker: DROP table → CREATE table with FULL OUTER JOIN
- Monitor progress every 30 min
- Verify row counts match base table (±1%)
- **Checkpoint**: 194/194 complete, row counts validated

**Batch 2: cov_* (2,507 tables, 6-12 hours)**
- Same parallel approach (8-16 workers)
- Largest batch - monitor memory/BigQuery quota
- Verify row counts match base table (±1%)
- **Checkpoint**: 2,507/2,507 complete, row counts validated

**Batch 3: corr_* (896 tables, 3-6 hours)**
- Same parallel approach (8-16 workers)
- Verify row counts match base table (±1%)
- **Checkpoint**: 896/896 complete, row counts validated

**Batch 4: mkt_* (10 tables, 30 min)**
- Sequential execution (small batch)
- Verify row counts match base table (±1%)
- **Checkpoint**: 10/10 complete, row counts validated

### Phase 3: Validation (18-24 hours)

**3.1. Row Count Verification** (1 hour)
- Query all 3,597 recalculated tables
- Compare row counts to base table (2,164,330 rows expected)
- Generate report: tables with row count mismatches
- **Gate**: All tables within ±1% of base row count

**3.2. Null Percentage Validation** (1 hour)
- Sample 10 tables from each batch
- Calculate NULL percentage per column
- Verify significant reduction from original
- **Gate**: NULL percentage reduced by 8-10% (expected)

**3.3. Re-Extract EURUSD** (2 hours)
- Run extraction pipeline with recalculated tables
- Generate new training file
- Measure NULL percentage
- **Gate**: NULLs reduced from 12.43% → ~2% (Tier 1 complete)

**3.4. Deliver Validation Report** (1 hour)
- Summary of recalculation (tables, row counts, costs)
- Before/after NULL comparison
- Recommendations for Tier 2 (lookahead, edge cases)
- **Deliverable**: `TIER1_RECALCULATION_COMPLETE.md`

---

## SUCCESS CRITERIA

### Gate 1: Feature Table Completeness ✅
- [ ] All 3,597 tables recalculated
- [ ] Row count = base table row count (±1%) for ALL tables
- [ ] No execution errors or failed tables

### Gate 2: NULL Reduction ✅
- [ ] Overall NULLs reduced by 8-10% (12.43% → ~2%)
- [ ] No feature tables with >5% row gaps
- [ ] EURUSD training file NULL percentage validates reduction

### Gate 3: Data Quality ✅
- [ ] No timestamp gaps in recalculated tables
- [ ] Date ranges aligned (2020-01-01 to 2025-11-20)
- [ ] No duplicate interval_times
- [ ] Schema consistency with original tables

### Gate 4: Cost & Timeline ✅
- [ ] Total cost ≤ $211 (approved budget)
- [ ] Completion within 24-36 hours (parallelized)
- [ ] No BigQuery quota violations

---

## RESOURCE REQUIREMENTS

**BigQuery**:
- Quota: Standard (sufficient for 3,597 queries)
- Cost: $150-$200 (APPROVED)
- Slots: Default (no reservation needed)

**Compute**:
- VM workers: 8-16 parallel processes
- Memory: 16-32 GB (moderate)
- CPU: Moderate (mostly I/O wait for BigQuery)

**Storage**:
- BigQuery: ~1.5 TB (recalculated tables, same as current)
- No additional storage cost (replacing existing tables)

---

## COORDINATION REQUIREMENTS

### With EA (Enhancement Assistant):
- **Input**: EA's SQL templates and remediation plan
- **Ongoing**: Cost tracking during execution (EA monitors BigQuery spend)
- **Output**: Final cost report for Tier 1 validation

### With QA (Quality Assurance):
- **After Batch 1**: QA spot-checks 10 tri_* tables for row count accuracy
- **After Batch 2**: QA spot-checks 20 cov_* tables for row count accuracy
- **After All Batches**: QA validates EURUSD re-extraction (NULL percentage)

### With CE (Chief Engineer):
- **Checkpoints**: Report after each batch complete (4 reports total)
- **Issues**: Escalate immediately if any batch fails or costs exceed $211
- **Final**: Deliver validation report within 24 hours of completion

---

## RISK MITIGATION

**Risk 1: BigQuery Quota Exceeded**
- **Mitigation**: Rate limit to 50 queries/min, monitor quota usage
- **Fallback**: Reduce parallelization from 16 → 8 workers

**Risk 2: Row Count Mismatches After Recalculation**
- **Mitigation**: Test SQL on 3 sample tables first, validate row counts
- **Fallback**: Debug SQL template, re-run failed tables

**Risk 3: Cost Overrun (>$211)**
- **Mitigation**: Monitor costs in real-time, pause if approaching limit
- **Fallback**: Seek CE approval for additional budget

**Risk 4: Execution Time >36 Hours**
- **Mitigation**: Use 16 parallel workers for cov_* batch (largest)
- **Fallback**: Extend timeline, notify CE of delay

---

## TIMELINE ESTIMATE

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| **Phase 1: Setup** | 2h | 22:45 Dec 12 | 00:45 Dec 13 |
| **Batch 1: tri_*** | 4h | 00:45 Dec 13 | 04:45 Dec 13 |
| **Batch 2: cov_*** | 12h | 04:45 Dec 13 | 16:45 Dec 13 |
| **Batch 3: corr_*** | 6h | 16:45 Dec 13 | 22:45 Dec 13 |
| **Batch 4: mkt_*** | 0.5h | 22:45 Dec 13 | 23:15 Dec 13 |
| **Phase 3: Validation** | 5h | 23:15 Dec 13 | 04:15 Dec 14 |
| **TOTAL** | **29.5h** | 22:45 Dec 12 | 04:15 Dec 14 |

**Completion Target**: 04:15 UTC December 14, 2025

---

## DELIVERABLES

**Interim Reports** (4 checkpoints):
1. `BATCH1_TRI_COMPLETE.md` - After tri_* batch (04:45 Dec 13)
2. `BATCH2_COV_COMPLETE.md` - After cov_* batch (16:45 Dec 13)
3. `BATCH3_CORR_COMPLETE.md` - After corr_* batch (22:45 Dec 13)
4. `BATCH4_MKT_COMPLETE.md` - After mkt_* batch (23:15 Dec 13)

**Final Deliverable**:
- `TIER1_RECALCULATION_COMPLETE.md` - Comprehensive validation report (04:15 Dec 14)

---

## AUTHORIZATION & APPROVAL

**Budget**: ✅ **APPROVED** - $160-$211 for Tier 1 recalculation

**Timeline**: ✅ **APPROVED** - 24-36 hours acceptable for 27-pair rollout unblock

**Scope**: ✅ **APPROVED** - Recalculate all 3,597 tables (tri, cov, corr, mkt)

**Approach**: ✅ **APPROVED** - FULL OUTER JOIN with forward-fill (EA's recommendation)

**Delegation**: ✅ **CONFIRMED** - BA has full authority to execute Tier 1

---

## NEXT STEPS (IMMEDIATE)

**BA Actions** (Next 2 Hours):
1. ⚙️ Review EA's SQL template: `/tmp/recalculate_tri_tables_template.py`
2. ⚙️ Test template on 3 sample tables (validate row counts)
3. ⚙️ Create parallel batch processing script (8-16 workers)
4. ⚙️ Query INFORMATION_SCHEMA for all tri/cov/corr/mkt table names
5. ⚙️ Launch Batch 1 (tri_*, 194 tables) at 00:45 UTC Dec 13

**EA Actions** (Ongoing):
- Monitor BigQuery costs in real-time
- Provide cost trajectory updates to CE
- Prepare revised ETF recommendation (separate from Tier 1)

**CE Actions** (Monitoring):
- Review BA checkpoint reports after each batch
- Approve additional budget if needed (unlikely)
- Coordinate with QA for validation after all batches complete

---

## USER MANDATE COMPLIANCE

**User Mandate**: *"All pair data is present and needs to be calculated based on common interval_time"*

**Tier 1 Compliance**:
- ✅ Recalculates all feature tables using common interval_time (FULL OUTER JOIN)
- ✅ Ensures 100% row coverage (no gaps)
- ✅ Achieves complete data as user expects (12.43% → 2% NULLs)
- ✅ No shortcuts (comprehensive recalculation of 3,597 tables)

**Strategic Value**: CRITICAL - unblocks 27-pair production rollout worth $556

---

**Chief Engineer (CE)**
*Strategic Coordination & Resource Authorization*

**Directive**: BA executes Tier 1 feature table recalculation with full budget approval ($160-$211)

**Expected Outcome**: 3,597 tables recalculated, 10.4% NULL reduction, completion by 04:15 UTC Dec 14

---

**END OF TIER 1 RECALCULATION DIRECTIVE**
