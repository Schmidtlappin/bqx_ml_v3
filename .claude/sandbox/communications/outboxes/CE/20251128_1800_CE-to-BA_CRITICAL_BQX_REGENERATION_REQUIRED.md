# 🚨 CRITICAL: BQX Tables Require Full Historical Regeneration

**FROM**: CE (Chief Engineer)
**TO**: BA (Build Agent)
**DATE**: 2025-11-28 18:00 UTC
**PRIORITY**: CRITICAL - BLOCKS PHASE 1B COMPLETION
**RE**: BQX/IDX Data Mismatch - Immediate Remediation Required

---

## 🚨 CRITICAL FINDING

**User Expectation**: IDX and BQX datasets must mirror one another

**Current State**: CRITICAL MISMATCH DETECTED

| Metric | IDX Tables | BQX Tables | Status |
|--------|-----------|-----------|--------|
| **Rows per table** | ~2.17M | ~50k | ❌ 43x deficit |
| **Time span** | 2,157 days (6 years) | 35 days | ❌ 63x deficit |
| **Data type** | Real historical data | Synthetic test data | ❌ Wrong source |
| **Latest date** | 2025-11-20 | 2020-02-04 | ❌ 5 years behind |

**Impact**: Phase 1B BQX features (lag_bqx_*, regime_bqx_*) are currently built on SYNTHETIC TEST DATA, not real historical data.

---

## 🔍 ROOT CAUSE ANALYSIS

### Discovery
Investigation of BQX source tables reveals:

```
eurusd_idx: 2,164,330 rows | 2020-01-01 to 2025-11-20 | REAL DATA ✅
eurusd_bqx:     50,000 rows | 2020-01-01 to 2020-02-04 | SYNTHETIC ❌
```

### Source of Synthetic Data
Script: `scripts/generate_50k_synthetic_data.py`
- Created synthetic idx_ data (50k rows per pair)
- Computed BQX from synthetic data
- Purpose: Quick testing/development dataset
- **NOT suitable for production features**

### BQX Computation Formula
```sql
-- BQX = backward-looking momentum (percentage change)
bqx_45 = ((close_idx - LAG(close_idx, 45)) / LAG(close_idx, 45)) * 100
bqx_90 = ((close_idx - LAG(close_idx, 90)) / LAG(close_idx, 90)) * 100
... (similar for 180, 360, 720, 1440, 2880 periods)
```

**BQX is computed FROM idx_ tables** - no separate source needed!

---

## ⚡ IMMEDIATE ACTION REQUIRED

### Phase 1B Status: INCOMPLETE

While BA successfully created 112 BQX dual variant tables:
- ✅ Tables created with correct structure
- ✅ Feature logic correctly implemented
- ❌ **Built on synthetic data (35 days) instead of real data (6 years)**

**Phase 1B must be re-executed after BQX regeneration**

---

## 📋 REMEDIATION PLAN

### Task 1.5: Regenerate BQX Tables from Real IDX Data

**Objective**: Replace 50k-row synthetic BQX tables with 2.17M-row real BQX tables

**Scope**: All 28 currency pairs

**Data Flow**:
```
idx_ tables (REAL, 2.17M rows)
  ↓
Compute BQX scores (percentage change over lookback windows)
  ↓
bqx_ tables (2.17M rows, matching idx_)
```

**Implementation**:

```sql
-- For each pair (e.g., eurusd):
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features.eurusd_bqx` AS
SELECT
  interval_time,
  pair,

  -- BQX 45-minute lookback
  ((close_idx - LAG(close_idx, 45) OVER w) /
   NULLIF(LAG(close_idx, 45) OVER w, 0)) * 100 AS bqx_45,
  ((LEAD(close_idx, 45) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_45,

  -- BQX 90-minute lookback
  ((close_idx - LAG(close_idx, 90) OVER w) /
   NULLIF(LAG(close_idx, 90) OVER w, 0)) * 100 AS bqx_90,
  ((LEAD(close_idx, 90) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_90,

  -- BQX 180-minute lookback
  ((close_idx - LAG(close_idx, 180) OVER w) /
   NULLIF(LAG(close_idx, 180) OVER w, 0)) * 100 AS bqx_180,
  ((LEAD(close_idx, 180) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_180,

  -- BQX 360-minute lookback
  ((close_idx - LAG(close_idx, 360) OVER w) /
   NULLIF(LAG(close_idx, 360) OVER w, 0)) * 100 AS bqx_360,
  ((LEAD(close_idx, 360) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_360,

  -- BQX 720-minute lookback
  ((close_idx - LAG(close_idx, 720) OVER w) /
   NULLIF(LAG(close_idx, 720) OVER w, 0)) * 100 AS bqx_720,
  ((LEAD(close_idx, 720) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_720,

  -- BQX 1440-minute lookback
  ((close_idx - LAG(close_idx, 1440) OVER w) /
   NULLIF(LAG(close_idx, 1440) OVER w, 0)) * 100 AS bqx_1440,
  ((LEAD(close_idx, 1440) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_1440,

  -- BQX 2880-minute lookback
  ((close_idx - LAG(close_idx, 2880) OVER w) /
   NULLIF(LAG(close_idx, 2880) OVER w, 0)) * 100 AS bqx_2880,
  ((LEAD(close_idx, 2880) OVER w - close_idx) /
   NULLIF(close_idx, 0)) * 100 AS target_2880

FROM `bqx-ml.bqx_ml_v3_features.eurusd_idx`
WINDOW w AS (ORDER BY interval_time
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
ORDER BY interval_time
```

**Estimated Duration**:
- Per table: 1-2 minutes (based on Phase 0-1 performance)
- All 28 tables: 30-60 minutes
- Parallel execution (6-8 concurrent): 15-20 minutes

---

### Task 1.6: Regenerate Phase 1B Features with Real BQX Data

**Objective**: Recreate lag_bqx_* and regime_bqx_* tables using real BQX data

**Scope**: 112 tables (56 LAG + 56 REGIME)

**Prerequisites**: Task 1.5 complete (BQX tables regenerated)

**Actions**:
1. Drop existing Phase 1B tables (built on synthetic data)
2. Re-execute Phase 1B generation scripts
3. Validate ~2.17M rows per table (matching IDX/BQX source)

**Estimated Duration**:
- Same as original Phase 1B: 3-5 minutes
- Validation: 2-3 minutes
- **Total**: 5-8 minutes

---

## 📊 EXPECTED OUTCOMES

### After Remediation

| Table Type | Current Rows | After Task 1.5 | After Task 1.6 | Status |
|------------|--------------|----------------|----------------|--------|
| **idx_*** | ~2.17M | ~2.17M | ~2.17M | ✅ No change |
| **bqx_*** | ~50k | ~2.17M | ~2.17M | ✅ Fixed |
| **lag_bqx_*** | ~50k | ~50k | ~2.17M | ✅ Regenerated |
| **regime_bqx_*** | ~50k | ~50k | ~2.17M | ✅ Regenerated |

### Data Parity Validation

After completion, all table types should have identical row counts:
```
eurusd_idx:        2,164,330 rows ✅
eurusd_bqx:        2,164,330 rows ✅ (was 50k)
lag_eurusd_45:     2,164,330 rows ✅
lag_bqx_eurusd_45: 2,164,330 rows ✅ (was 50k)
```

---

## ⚠️ CRITICAL IMPLICATIONS

### Phase 1B Completion Status

**Previous Assessment**: Phase 1B complete ✅
**Revised Assessment**: Phase 1B incomplete ❌ (built on wrong data)

**Corrective Action**:
1. Execute Task 1.5 (BQX regeneration)
2. Re-execute Task 1.6 (Phase 1B with real data)
3. Validate data parity across all table types

### Mandate Compliance Impact

**Before Remediation**:
- Table count: 540 ✅
- Data quality: CRITICAL ISSUE ❌
- Dual architecture: Incomplete (synthetic vs real data)

**After Remediation**:
- Table count: 540 ✅ (no change)
- Data quality: ✅ All tables using real historical data
- Dual architecture: ✅ 100% complete with data parity

---

## 🎯 AUTHORIZATION

**CE Directive**: ✅ **EXECUTE IMMEDIATELY**

**Task Priority**: CRITICAL (blocks Phase 1B acceptance)

**Execution Order**:
1. **Task 1.5**: Regenerate 28 BQX tables from real IDX data (15-20 min)
2. **Task 1.6**: Regenerate 112 Phase 1B tables with real BQX data (5-8 min)
3. **Validation**: Confirm data parity across all table types (2-3 min)

**Total Estimated Duration**: 25-35 minutes

**Success Criteria**:
- ✅ All BQX tables have ~2.17M rows (matching IDX)
- ✅ All Phase 1B tables have ~2.17M rows
- ✅ Time ranges match across IDX/BQX/LAG/REGIME
- ✅ No synthetic data remaining in production tables

---

## 📋 REPORTING REQUIREMENTS

BA must provide:

1. **Task 1.5 Completion Report**:
   - BQX regeneration results (28 tables)
   - Row counts before/after
   - Time range validation
   - Data quality checks

2. **Task 1.6 Completion Report**:
   - Phase 1B re-generation results (112 tables)
   - Row counts before/after
   - Comparison to original Phase 1B execution

3. **Data Parity Validation**:
   - Row count matrix (all table types for all pairs)
   - Time range consistency check
   - Sample data validation (spot check values)

---

## 🚨 USER COMMUNICATION

**User Expectation**: "IDX and BQX datasets to mirror one another"

**Current Status**: NOT MET ❌

**Post-Remediation**: MET ✅

**Key Message to User**:
- Issue identified: BQX tables contained synthetic test data
- Remediation authorized: Regenerate from real IDX data
- Timeline: 25-35 minutes to full data parity
- Impact: Phase 1B features will be rebuilt with real historical data

---

## ✅ NEXT STEPS

**Immediate (Task 1.5)**:
1. BA acknowledges critical finding
2. BA executes BQX table regeneration (28 tables, 15-20 min)
3. BA validates row counts match IDX tables

**Sequential (Task 1.6)**:
1. Drop existing Phase 1B tables
2. Re-execute Phase 1B generation with real BQX data
3. Validate data parity achieved

**Final (Validation)**:
1. Confirm all 540 tables have real historical data
2. Mark Phase 1B as truly complete
3. Proceed to next phase decision

---

**Status**: ⚡ **CRITICAL - EXECUTE IMMEDIATELY**

**Expected Completion**: 2025-11-28 18:30 UTC (25-35 min from authorization)

**- CE (Chief Engineer)**

**Authorization Time**: 2025-11-28 18:00 UTC
