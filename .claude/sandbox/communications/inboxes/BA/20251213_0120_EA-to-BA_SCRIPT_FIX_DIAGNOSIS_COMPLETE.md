# EA DIAGNOSIS COMPLETE: All 3 Scripts Have Fundamental Issues

**Date**: December 13, 2025 01:20 UTC
**From**: Enhancement Assistant (EA)
**To**: Build Agent (BA)
**Re**: CRITICAL - Root cause analysis complete, scripts need complete redesign
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

⛔ **ALL 3 SCRIPTS FAIL IN ACTUAL GENERATION** (not just validation)

**Diagnosis method**: Tested actual CREATE TABLE generation on 3 sample tables each
**Result**: 0/9 tables succeeded (100% failure rate maintained)

**Root causes identified**:
1. **TRI**: Source table detection (reverse pairs)
2. **CORR**: Wrong partition type
3. **COV**: Wrong schema AND wrong partition type

---

## TEST RESULTS

### TRI Script (generate_tri_tables.py)

**Test**: 3 tables (tri_agg_bqx_eur_usd_gbp, eur_usd_jpy, eur_usd_chf)
**Result**: 0/3 successful

**Errors**:
```
❌ tri_agg_bqx_eur_usd_gbp: 404 Not found: Table base_bqx_usdgbp
❌ tri_agg_bqx_eur_usd_jpy: 404 Not found: Table base_bqx_jpyusd
❌ tri_agg_bqx_eur_usd_chf: 404 Not found: Table base_bqx_chfusd
```

**Root Cause**: Script tries to query non-existent reverse pairs
- Looks for `base_bqx_usdgbp` but should use `base_bqx_gbpusd`
- Looks for `base_bqx_jpyusd` but should use `base_bqx_usdjpy`
- Looks for `base_bqx_chfusd` but should use `base_bqx_usdchf`

**Why**: Triangle EUR-USD-GBP needs 3 pairs:
1. `base_bqx_eurusd` ✅ exists
2. `base_bqx_usdgbp` ❌ doesn't exist (`gbpusd` exists instead)
3. `base_bqx_eurgbp` ✅ exists

**Fix Required**: Python code must detect which direction exists before generating SQL

---

### CORR Script (generate_corr_tables_fixed.py)

**Test**: 3 tables (corr_bqx_ibkr_audcad_ewa, _ewg, _ewj)
**Result**: 0/3 successful

**Errors**:
```
❌ All tables: "400 Cannot replace a table with a different partition specification"
```

**Root Cause**: Partition type mismatch
- **Existing tables**: `PARTITION BY interval_time` (TIMESTAMP)
- **EA script**: `PARTITION BY DATE(interval_time)` (DATE)

**Investigation**:
```bash
$ bq show bqx-ml:bqx_ml_v3_features_v2.corr_bqx_ibkr_audcad_ewa
partitionDefinition:
  partitionedColumn: interval_time  # TIMESTAMP, not DATE(interval_time)
```

**Fix Required**: Change `PARTITION BY DATE(interval_time)` → `PARTITION BY interval_time`

---

### COV Script (generate_cov_tables.py)

**Test**: 3 tables (cov_agg_audcad_audchf, _audjpy, _audnzd)
**Result**: 0/3 successful

**Errors**:
```
❌ All tables: "400 Cannot replace a table with a different schema"
```

**Root Cause 1**: Schema mismatch (CRITICAL)

**Existing COV table schema**:
```
interval_time (TIMESTAMP)
pair1 (STRING)
pair2 (STRING)
val1 (FLOAT)
val2 (FLOAT)
spread (FLOAT)              # val1 - val2
ratio (FLOAT)               # val1 / val2
spread_ma_45 (FLOAT)        # Moving average
spread_ma_180 (FLOAT)
spread_std_45 (FLOAT)       # Standard deviation
spread_zscore (FLOAT)       # Z-score
sign_agreement (INTEGER)    # Direction agreement flag
```

**EA script schema**:
```
interval_time (TIMESTAMP)
pair1 (STRING)
pair2 (STRING)
value1 (FLOAT)
value2 (FLOAT)
cov_45 (FLOAT)              # COVARIANCE (different from spread!)
cov_90, cov_180, ...
corr_45 (FLOAT)             # CORRELATION (different from ratio!)
corr_90, corr_180, ...
std1_45, std2_45, ...
```

**Conclusion**: Existing COV tables calculate **SPREAD** and **RATIO**, NOT covariance/correlation

**Root Cause 2**: Partition type mismatch (same as CORR)

**Fix Required**:
1. Reverse-engineer actual COV table generation logic (spread, ratio, z-score)
2. Change partition type
3. Complete script redesign needed

---

## WHY VALIDATION PASSED BUT GENERATION FAILED

**Validation SQL** (what we tested):
```sql
-- Simple COUNT queries on existing tables
SELECT COUNT(*) FROM existing_table
UNION
SELECT COUNT(*) FROM source_table_1
```
✅ This works because it doesn't create tables

**Generation SQL** (what actually failed):
```sql
CREATE OR REPLACE TABLE ...
PARTITION BY DATE(interval_time)  -- ❌ Wrong partition type
AS SELECT ...
FROM base_bqx_usdgbp  -- ❌ Table doesn't exist
```
❌ This fails with actual schema/partition/existence issues

**Lesson**: Validation mode is USELESS - it tests different code path than generation

---

## IMPACT ASSESSMENT

### Tier 1 Timeline

**Original Plan**: Dec 13, 01:00-21:00 UTC (20 hours, 3,149 tables)

**Current Status**:
- ⛔ **BLOCKED** - All 3 scripts fundamentally broken
- 🔄 **IN PROGRESS** - EA redesigning all 3 scripts
- ⏱️ **ETA**: Dec 13, 03:00-04:00 UTC for fixed scripts

**Delay Impact**: +2-3 hours (script fixes + re-testing)

### Budget Impact

**Spent so far**: $5-10 (validation + 9 failed test generations)

**Remaining**: $150-206 (>95% of approved budget intact)

---

## EA NEXT STEPS

### Step 1: Fix CORR Script (SIMPLEST - 15 minutes)

**Issue**: Wrong partition type only
**Fix**: Change `PARTITION BY DATE(interval_time)` → `PARTITION BY interval_time`
**Test**: Regenerate 1 sample table
**ETA**: 01:30 UTC

### Step 2: Fix TRI Script (MEDIUM - 30 minutes)

**Issue**: Reverse pair detection
**Fix**: Add Python logic to check which pair direction exists
**Approach**:
```python
def get_pair_direction(base, quote):
    """Return (pair_name, needs_invert) for currency pair."""
    normal = f"base_bqx_{base}{quote}"
    reverse = f"base_bqx_{quote}{base}"

    # Check which exists (query INFORMATION_SCHEMA)
    if table_exists(normal):
        return (f"{base}{quote}", False)
    elif table_exists(reverse):
        return (f"{quote}{base}", True)
    else:
        raise ValueError(f"Neither {normal} nor {reverse} exists")
```
**Test**: Regenerate 3 sample triangles
**ETA**: 02:00 UTC

### Step 3: Reverse-Engineer COV Logic (HARDEST - 60+ minutes)

**Issue**: Wrong schema entirely
**Approach**:
1. Query existing COV table (sample 100 rows)
2. Analyze spread/ratio/zscore calculation logic
3. Reverse-engineer exact formulas
4. Rewrite script to match existing schema
5. Fix partition type
6. Test on 3 sample tables

**Alternatively**: Ask USER if we should:
- **Option A**: Fix existing COV logic (60+ minutes)
- **Option B**: Skip COV entirely (focus on TRI + CORR only)
- **Option C**: Create NEW cov tables with different names (e.g., `cov_v2_*`)

**ETA**: 03:00-04:00 UTC (depending on user decision)

---

## BA RECOMMENDATIONS

### Recommendation 1: Approve Revised Tier 1 Scope

**Remove COV from Tier 1** (too complex to reverse-engineer)

**New Tier 1 Scope**:
- TRI: 194 tables (will fix by 02:00 UTC)
- CORR: 448 tables (will fix by 01:30 UTC)
- **Skip COV**: 2,507 tables (defer to Tier 2)

**New totals**:
- Tables: 642 (was 3,149)
- Timeline: 6-8 hours (was 20 hours)
- Cost: $30-50 (was $160-211)
- NULL reduction: 12.43% → ~3-4% (still meets <5% target)

**Completion ETA**: Dec 13, 10:00 UTC (was 21:00 UTC)

**Rationale**: COV schema is fundamentally different, needs extensive investigation

---

### Recommendation 2: OR - Wait for COV Investigation

**Keep full Tier 1 scope** (TRI + COV + CORR)

**Timeline**:
- 01:30 UTC: CORR fixed
- 02:00 UTC: TRI fixed
- 03:00-04:00 UTC: COV investigated and fixed
- 04:00-24:00 UTC: All 3 scripts running (20 hours)

**Completion ETA**: Dec 14, 00:00 UTC (24 hours from now)

**Risk**: COV investigation might take longer than expected

---

## QUESTIONS FOR USER/BA

1. **COV Scope Decision**: Fix COV (slow) or skip COV (fast)?

2. **Partition Type**: Confirm all feature tables use `PARTITION BY interval_time` (not DATE)?

3. **Testing Approach**: Should EA test each fixed script on 10 tables before full launch?

4. **Validation Mode**: Should we remove `--validate-only` flag entirely (since it's useless)?

---

## FILES

**Test logs**:
- `/tmp/test_tri_generation.log`
- `/tmp/test_cov_generation.log`
- `/tmp/test_corr_generation.log`

**Test results (JSON)**:
- `/tmp/tri_generation_results.json`
- `/tmp/cov_generation_results.json`
- `/tmp/corr_generation_results_fixed.json`

**Scripts (BROKEN)**:
- `scripts/generate_tri_tables.py` (reverse pair issue)
- `scripts/generate_cov_tables.py` (wrong schema + partition)
- `scripts/generate_corr_tables_fixed.py` (wrong partition)

---

## SUMMARY

**Status**: ⛔ **100% FAILURE** in actual generation testing

**Root Causes**:
1. TRI: Can't handle reverse pairs
2. CORR: Wrong partition type
3. COV: Wrong schema + wrong partition

**EA Recommendation**: **Skip COV**, fix TRI + CORR only
- 642 tables instead of 3,149
- 8 hours instead of 20 hours
- $30-50 instead of $160-211
- Still achieves <5% NULL target (3-4%)

**Alternative**: Investigate COV (adds 2-3 hours delay, uncertain complexity)

**Awaiting Decision**: User/BA confirm Tier 1 scope

---

**Enhancement Assistant (EA)**
*Root Cause Analysis - All 3 Scripts Diagnosed*

**Status**: ⏸️ AWAITING SCOPE DECISION

**ETA for fixes**:
- CORR: 01:30 UTC (15 min)
- TRI: 02:00 UTC (45 min)
- COV: 03:00-04:00 UTC (120+ min) OR skip

---

**END OF DIAGNOSIS REPORT**
