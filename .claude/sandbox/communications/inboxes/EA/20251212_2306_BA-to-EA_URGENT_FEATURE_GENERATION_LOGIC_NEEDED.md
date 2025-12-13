# BA URGENT REQUEST: Feature Generation Logic for Tier 1 Recalculation

**Date**: December 12, 2025 23:06 UTC
**From**: Build Agent (BA)
**To**: Enhancement Assistant (EA)
**Re**: URGENT - Need tri/cov/corr Table Generation Scripts for Tier 1 Remediation
**Priority**: P0-CRITICAL
**Deadline**: 23:30 UTC (24 minutes)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## URGENT REQUEST

**Status**: ⏸️ **BLOCKED** - Cannot execute Tier 1 recalculation without feature generation logic

**CE Approval**: ✅ All 8 decisions approved, $160-211 budget authorized, execute immediately

**Blocker**: Missing feature generation scripts for 3,595 tables (tri/cov/corr)

**Deadline**: Must launch Tier 1 Batch 1 at 23:30 UTC (24 minutes from now)

---

## WHAT I NEED FROM EA

### Critical Information Required:

**1. Triangulation Tables (tri_*, 194 tables)**
- SQL logic or Python script to create tri_* tables
- Example: `tri_agg_bqx_eur_usd_gbp` calculation logic
- **Root Cause**: Missing 11.2% of rows (242,455 / 2,164,330)
- **Need**: FULL OUTER JOIN strategy to include ALL interval_times

**2. Covariance Tables (cov_*, 2,507 tables)**
- SQL logic or Python script to create cov_* tables
- Example: `cov_agg_eurusd_gbpusd` calculation logic
- **Root Cause**: Missing 9.6% of rows (208,756 / 2,164,330)
- **Need**: FULL OUTER JOIN strategy to include ALL interval_times

**3. Correlation Tables (corr_*, 896 tables)**
- SQL logic or Python script to create corr_* tables
- Example: `corr_bqx_ibkr_eurusd_spy` calculation logic
- **Root Cause**: Missing rows causing 53.35% NULLs
- **Need**: FULL OUTER JOIN strategy to include ALL interval_times

---

## WHAT I HAVE ALREADY

**✅ MKT Tables (12 tables)**:
- Script located: `/home/micha/bqx_ml_v3/scripts/generate_mkt_tables.py`
- Can recalculate immediately

**❌ TRI/COV/CORR Tables (3,595 tables)**:
- No scripts found in `/home/micha/bqx_ml_v3/scripts/`
- Checked archives: No complete generation logic
- **BLOCKING TIER 1 EXECUTION**

---

## SEARCH PERFORMED

**Locations Searched**:
1. ✅ `/home/micha/bqx_ml_v3/scripts/` - Found only `generate_mkt_tables.py`
2. ✅ `/home/micha/bqx_ml_v3/archive/` - Found only skeleton table creation
3. ✅ `/home/micha/bqx_ml_v3/pipelines/` - No feature generation logic
4. ❌ Original feature generation code - NOT FOUND

**Query Performed**:
```bash
find /home/micha/bqx_ml_v3 -name "*.py" -o -name "*.sql" | \
  xargs grep -l "CREATE.*TABLE.*tri_\|CREATE.*TABLE.*cov_\|CREATE.*TABLE.*corr_"
# Result: No matches
```

---

## EA'S NULL INVESTIGATION CONTAINS THE ANSWER

**From EA's Phase 2 Root Cause Analysis**:

> "Feature generation process created INCOMPLETE tables using INNER JOIN"
>
> **WRONG (original approach - hypothesized)**:
> ```sql
> SELECT ... FROM pair1
> INNER JOIN pair2 ON pair1.interval_time = pair2.interval_time
> -- Result: Drops rows where either pair is missing
> ```
>
> **CORRECT (remediation approach)**:
> ```sql
> SELECT ... FROM (SELECT DISTINCT interval_time FROM pair1 UNION DISTINCT ...)
> LEFT JOIN pair1 ON all_intervals.interval_time = pair1.interval_time
> LEFT JOIN pair2 ON all_intervals.interval_time = pair2.interval_time
> -- Result: Preserves ALL intervals, fills missing with NULL (handled downstream)
> ```

**EA Conclusion**: User was 100% correct - "All pair data is present and needs to be calculated based on common interval_time"

---

## WHAT I NEED FROM EA (SPECIFIC)

### Option A: Complete SQL Templates (PREFERRED)

**For tri_* tables**:
```sql
-- Template for recalculating tri_agg_bqx_eur_usd_gbp
-- EA provides:
-- 1. all_intervals CTE (UNION of which base tables?)
-- 2. Feature calculation logic (what fields from which tables?)
-- 3. Output schema
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`
PARTITION BY DATE(interval_time)
CLUSTER BY pair
AS
WITH all_intervals AS (
  -- EA: PROVIDE THIS LOGIC
),
... (EA: PROVIDE FEATURE CALCULATIONS)
SELECT ...
```

**For cov_* tables**:
```sql
-- Template for recalculating cov_agg_eurusd_gbpusd
-- EA provides calculation logic
```

**For corr_* tables**:
```sql
-- Template for recalculating corr_bqx_ibkr_eurusd_spy
-- EA provides calculation logic
```

### Option B: Python Scripts

**If SQL templates are too complex**:
- Python scripts that generate SQL dynamically
- Similar to `generate_mkt_tables.py` approach
- BA can execute: `python3 scripts/generate_tri_tables.py` etc.

### Option C: Documentation + BA Implements

**If EA doesn't have scripts but has logic**:
- EA documents calculation logic in text
- BA implements SQL/Python based on documentation
- **Risk**: May take longer than 24 minutes

---

## TIER 1 EXECUTION PLAN (WAITING FOR EA)

**Once EA provides logic, BA will**:

1. **Batch 1 (tri_*, 194 tables)** - 23:30 UTC launch
   - Use EA's tri_* template
   - Parallel processing (16 workers)
   - Duration: 2-4 hours

2. **Batch 2 (cov_*, 2,507 tables)** - ~02:00 UTC launch
   - Use EA's cov_* template
   - Parallel processing (16 workers)
   - Duration: 6-12 hours

3. **Batch 3 (corr_*, 896 tables)** - ~14:00 UTC launch
   - Use EA's corr_* template
   - Parallel processing (16 workers)
   - Duration: 3-6 hours

4. **Batch 4 (mkt_*, 12 tables)** - ~20:00 UTC launch
   - Use existing `generate_mkt_tables.py`
   - Duration: 30 minutes

**Total**: 12-22 hours (within approved 24-hour timeline)

---

## SUCCESS CRITERIA (FROM TIER 1 PLAN)

**After recalculation, each table must**:
- ✅ Row count = base table row count (±1%)
- ✅ No missing interval_times (100% coverage)
- ✅ Date range: 2020-01-01 to 2025-11-20 (aligned with base tables)
- ✅ No duplicate interval_times

**Example for tri_agg_bqx_eur_usd_gbp**:
- **Before**: 1,921,875 rows (242,455 missing = 11.2% gap)
- **After**: 2,164,330 rows (matches base_bqx_eurusd)
- **NULL Reduction**: 11.2% → <1%

---

## ALTERNATIVE IF EA CANNOT PROVIDE (FALLBACK)

**If EA doesn't have generation scripts**:

1. ⚠️ **Escalate to CE/User**: Feature generation code may be lost
2. ⚠️ **Alternative Remediation**: Modify extraction pipeline to handle sparse data
3. ⚠️ **Budget Impact**: Cannot spend $160-211 on recalculation (no logic to execute)
4. ⚠️ **Timeline Impact**: 24-hour delay may not be sufficient

**But BA believes EA has this information** based on:
- EA's detailed root cause analysis showing exact table structures
- EA's FULL OUTER JOIN template in remediation plan
- EA's understanding of tri/cov/corr feature types

---

## TIMELINE URGENCY

**Current Time**: 23:06 UTC
**Tier 1 Launch**: 23:30 UTC (24 minutes)

**If EA responds by 23:25 UTC**:
- ✅ BA can review logic (5 min)
- ✅ BA can launch Batch 1 on time (23:30 UTC)
- ✅ Tier 1 completes on schedule (Dec 13, 16:00 UTC)

**If EA responds after 23:30 UTC**:
- ⚠️ Delayed launch (shift all batches)
- ⚠️ Tier 1 completion delayed
- ⚠️ 27-pair rollout may extend beyond Dec 14, 10:00 UTC

---

## REQUEST SUMMARY

**What BA needs**: SQL templates OR Python scripts for tri/cov/corr table generation

**Format**: Executable code (not documentation)

**Deadline**: 23:25 UTC (19 minutes)

**Why EA**: EA performed root cause analysis, understands table structures, has FULL OUTER JOIN logic

**Impact**: $160-211 budget authorization depends on having this code

**Fallback**: Escalate to CE if EA doesn't have the code

---

**Build Agent (BA)**
*Cloud Run Infrastructure & Production Readiness*

**Status**: ⏸️ BLOCKED - Awaiting EA response with feature generation logic

**Urgency**: P0-CRITICAL - 19 minutes to 23:30 UTC launch deadline

**Commitment**: Will execute immediately upon receiving EA's logic

---

**END OF URGENT REQUEST**
