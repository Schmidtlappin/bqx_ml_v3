# 🚨 CRITICAL FINDING: BQX/IDX Data Mismatch

**Date**: 2025-11-28 18:00 UTC
**Status**: CRITICAL - Immediate remediation authorized
**Impact**: Phase 1B features built on synthetic test data (not production data)

---

## 📊 Executive Summary

**User Expectation**: "IDX and BQX datasets should mirror one another"

**Critical Finding**: BQX tables contain only **35 days** of synthetic test data, while IDX tables contain **6 years** of real historical data.

| Metric | IDX Tables (Expected) | BQX Tables (Actual) | Delta |
|--------|----------------------|---------------------|-------|
| **Rows** | ~2.17M per pair | ~50k per pair | ❌ 43x deficit |
| **Time Span** | 6 years (2020-2025) | 35 days (Jan-Feb 2020) | ❌ 63x deficit |
| **Data Type** | Real historical | Synthetic test data | ❌ Wrong source |
| **Latest Date** | 2025-11-20 | 2020-02-04 | ❌ 5 years behind |

---

## 🔍 Root Cause

### What Happened

1. **IDX Tables**: Created from real m1_* source data (~2.17M rows, 6 years)
2. **BQX Tables**: Created from synthetic test data script (`generate_50k_synthetic_data.py`)
3. **Phase 1B Features**: Built on top of synthetic BQX tables (wrong foundation)

### Why BQX Was Synthetic

The `generate_50k_synthetic_data.py` script was used during development to:
- Quickly test the feature generation pipeline
- Validate BQX computation logic
- Create small test dataset for development

**This was appropriate for testing, but NOT suitable for production features.**

### BQX Computation Formula

BQX (backward-looking momentum) is computed FROM idx_ tables:

```sql
BQX = ((current_close - lagged_close) / lagged_close) * 100
```

For example:
- bqx_45 = percentage change over 45-minute lookback
- bqx_90 = percentage change over 90-minute lookback
- ... up to bqx_2880 (2-day lookback)

**No separate data source needed** - BQX is derived from IDX!

---

## ⚡ Impact Assessment

### Current Phase 1B Status

**Tables Created**: 112 (56 lag_bqx_* + 56 regime_bqx_*)
**Structure**: ✅ Correct
**Logic**: ✅ Correct
**Data Source**: ❌ **WRONG (synthetic instead of real)**

### Affected Features

All Phase 1B BQX dual variant features are affected:
- `lag_bqx_{pair}_{period}`: 56 tables (50k rows each, should be 2.17M)
- `regime_bqx_{pair}_{period}`: 56 tables (50k rows each, should be 2.17M)

**Total Impact**: 112 production feature tables built on test data

### Mandate Compliance Impact

**Dual Architecture Requirement**: "IDX and BQX must mirror one another"

**Current State**: ❌ NOT MET
- IDX: 6 years of real data
- BQX: 35 days of synthetic data
- **Data parity: 0%**

**After Remediation**: ✅ WILL BE MET
- IDX: 6 years of real data
- BQX: 6 years of real data (regenerated from IDX)
- **Data parity: 100%**

---

## 📋 Remediation Plan

### Task 1.5: Regenerate BQX Tables from Real IDX Data

**Objective**: Replace synthetic BQX tables with real historical data

**Actions**:
1. Drop existing 28 BQX tables (synthetic, 50k rows each)
2. Regenerate from real idx_ tables (2.17M rows each)
3. Compute BQX scores for ALL historical timeframes
4. Validate row counts match IDX tables

**Duration**: 15-20 minutes (6-8 concurrent workers)

**Output**: 28 BQX tables with ~2.17M rows each (matching IDX)

---

### Task 1.6: Regenerate Phase 1B Features with Real BQX Data

**Objective**: Rebuild Phase 1B features on real historical data

**Actions**:
1. Drop existing 112 Phase 1B tables (built on synthetic BQX)
2. Re-execute Phase 1B generation scripts
3. Validate row counts match source tables (~2.17M each)

**Duration**: 5-8 minutes (same as original Phase 1B)

**Output**: 112 Phase 1B tables with ~2.17M rows each (real data)

---

### Total Remediation Timeline

```
Task 1.5 (BQX regeneration):     15-20 minutes
Task 1.6 (Phase 1B re-execution): 5-8 minutes
Validation:                       2-3 minutes
────────────────────────────────────────────
Total:                           25-35 minutes
```

---

## ✅ Success Criteria

### Data Parity Validation

After remediation, all table types must have identical row counts:

```
eurusd_idx:            2,164,330 rows ✅
eurusd_bqx:            2,164,330 rows ✅ (was 50,000)
lag_eurusd_45:         2,164,330 rows ✅
lag_bqx_eurusd_45:     2,164,330 rows ✅ (was 50,000)
regime_eurusd_45:      2,164,330 rows ✅
regime_bqx_eurusd_45:  2,164,330 rows ✅ (was 50,000)
```

### Quality Checks

- ✅ All BQX tables span 2020-01-01 to 2025-11-20 (matching IDX)
- ✅ All Phase 1B tables span same range
- ✅ No synthetic data remaining in production tables
- ✅ BQX values computed from real price movements
- ✅ Dual architecture truly mirrors IDX

---

## 📊 Before/After Comparison

### Before Remediation (Current State)

| Table Type | Rows | Time Range | Data Type |
|-----------|------|------------|-----------|
| idx_* | 2.17M | 2020-2025 | Real ✅ |
| bqx_* | 50k | Jan-Feb 2020 | Synthetic ❌ |
| lag_* | 2.17M | 2020-2025 | Real ✅ |
| lag_bqx_* | 50k | Jan-Feb 2020 | Synthetic ❌ |
| regime_* | 2.17M | 2020-2025 | Real ✅ |
| regime_bqx_* | 50k | Jan-Feb 2020 | Synthetic ❌ |

**Data Parity**: ❌ 0% (BQX tables don't mirror IDX)

---

### After Remediation (Expected State)

| Table Type | Rows | Time Range | Data Type |
|-----------|------|------------|-----------|
| idx_* | 2.17M | 2020-2025 | Real ✅ |
| bqx_* | 2.17M | 2020-2025 | Real ✅ |
| lag_* | 2.17M | 2020-2025 | Real ✅ |
| lag_bqx_* | 2.17M | 2020-2025 | Real ✅ |
| regime_* | 2.17M | 2020-2025 | Real ✅ |
| regime_bqx_* | 2.17M | 2020-2025 | Real ✅ |

**Data Parity**: ✅ 100% (BQX tables mirror IDX perfectly)

---

## 🎯 Current Status

**BA Status**: Awaiting Task 1.5 execution
- Critical finding acknowledged
- Remediation plan received
- Ready to execute BQX regeneration

**CE Status**: Monitoring
- Task 1.5 authorized (BQX regeneration)
- Task 1.6 authorized (Phase 1B re-execution)
- Validation criteria defined

**Expected Completion**: 2025-11-28 18:30 UTC (~30 minutes)

---

## 📋 Key Takeaways

1. **Issue**: BQX tables contained 35 days of synthetic test data
2. **Root Cause**: Development script used for testing, not replaced with production data
3. **Impact**: Phase 1B features built on wrong foundation
4. **User Expectation**: IDX and BQX should mirror (currently not met)
5. **Solution**: Regenerate BQX from real IDX data, then rebuild Phase 1B features
6. **Timeline**: 25-35 minutes to full remediation
7. **Outcome**: True dual architecture with 100% data parity

---

## ✅ Next Update

**When**: After Task 1.5 completion (~15-20 min)

**Expected Content**:
- BQX table regeneration results
- Row count validation (28 tables, ~2.17M rows each)
- Time range confirmation (2020-2025)
- Ready for Task 1.6 (Phase 1B re-execution)

---

**Document Status**: Active remediation in progress
**Last Updated**: 2025-11-28 18:00 UTC
**Next Update**: Task 1.5 completion report
