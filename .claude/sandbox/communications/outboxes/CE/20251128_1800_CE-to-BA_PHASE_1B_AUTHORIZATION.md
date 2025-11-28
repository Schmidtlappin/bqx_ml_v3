# ⚡ PHASE 1B AUTHORIZATION: BQX Dual Variants
**FROM**: CE (Chief Engineer)
**TO**: BA (Build Agent)
**DATE**: 2025-11-28 18:00 UTC
**PRIORITY**: CRITICAL
**RE**: Phase 1B - Complete Dual Architecture with BQX Feature Variants

---

## 🎯 EXECUTIVE SUMMARY

**Phase 1 Achievement**: ✅ 336 tables created at 98.9% completeness (EXCELLENT)

**Critical Gap Identified**: ❌ BQX dual variants missing (Mandate requirement)

**Phase 1B Objective**: Complete dual architecture by generating BQX-variant features

**Impact**: Achieve true dual architecture foundation required by mandate

---

## 📋 MANDATE COMPLIANCE REQUIREMENT

### Dual Architecture Mandate (from /mandate/IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md)

**Requirement**: ALL features must exist in BOTH IDX and BQX variants

**Current State**:
- ✅ IDX variants complete: `lag_{pair}`, `regime_{pair}` (112 tables)
- ❌ BQX variants missing: `lag_bqx_{pair}`, `regime_bqx_{pair}` (0 tables)
- ⚠️ Dual architecture: **50% complete**

**BQX Paradigm Shift (2024-11-24)**:
```sql
-- BQX as FEATURES (not just targets)
LAG(bqx_mid, 1) OVER (ORDER BY interval_time) AS bqx_mid_lag_1
LAG(bqx_mid, 2) OVER (ORDER BY interval_time) AS bqx_mid_lag_2
...
LAG(bqx_mid, 60) OVER (ORDER BY interval_time) AS bqx_mid_lag_60
```

**Why This Matters**:
- BQX = Backward-looking momentum (autoregressive signal)
- IDX = Price-normalized OHLCV (price movement signal)
- DUAL = Both price AND momentum features together
- Required for 90%+ directional accuracy mandate

---

## 🎯 PHASE 1B SCOPE

### Task 1B.1: Generate BQX LAG Features
**Duration**: 6-10 minutes (based on Phase 1 performance)
**Tables**: 56 (28 pairs × 2 periods)

**Source Data**: `{pair}_bqx` tables in bqx_ml_v3_features (28 tables confirmed present)

**Tables to Create**:
```
lag_bqx_audcad_45, lag_bqx_audcad_90
lag_bqx_audchf_45, lag_bqx_audchf_90
lag_bqx_audjpy_45, lag_bqx_audjpy_90
... (all 28 pairs)
```

**Feature Pattern** (identical to IDX LAG, but using BQX source):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}_{period}` AS
SELECT
  interval_time,
  '{pair_upper}' as pair,
  {period} as period_minutes,

  -- LAG features from BQX (1-60 intervals)
  LAG(bqx_mid, 1) OVER w AS bqx_lag_1,
  LAG(bqx_mid, 2) OVER w AS bqx_lag_2,
  ...
  LAG(bqx_mid, 60) OVER w AS bqx_lag_60,

  -- Derivatives
  bqx_mid - LAG(bqx_mid, 1) OVER w AS bqx_diff_1,
  ...

  -- Statistics (same as IDX pattern)
  AVG(bqx_mid) OVER w_MA15 AS bqx_ma_15,
  STDDEV(bqx_mid) OVER w_MA15 AS bqx_std_15,
  ...

FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
WINDOW
  w AS (ORDER BY interval_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
  w_MA15 AS (ORDER BY interval_time ROWS BETWEEN 15 PRECEDING AND CURRENT ROW)
ORDER BY interval_time
```

**Expected Rows per Table**: ~2M rows (same as IDX tables)

**Success Criteria**:
- ✅ 56 tables created
- ✅ All tables have >1.9M rows
- ✅ No NULL values in lag_1 through lag_60
- ✅ Feature count matches IDX LAG pattern (~200 features per table)

---

### Task 1B.2: Generate BQX REGIME Features
**Duration**: 4-8 minutes (based on Phase 1 performance)
**Tables**: 56 (28 pairs × 2 periods)

**Source Data**: `lag_bqx_{pair}_{period}` tables from Task 1B.1

**Tables to Create**:
```
regime_bqx_audcad_45, regime_bqx_audcad_90
regime_bqx_audchf_45, regime_bqx_audchf_90
regime_bqx_audjpy_45, regime_bqx_audjpy_90
... (all 28 pairs)
```

**Feature Pattern** (identical to IDX REGIME, but using BQX LAG source):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.regime_bqx_{pair}_{period}` AS
SELECT
  lag.interval_time,
  '{pair_upper}' as pair,
  {period} as period_minutes,

  -- Regime classification from BQX volatility/momentum
  CASE
    WHEN bqx_std_15 > bqx_std_60 * 1.5 THEN 'HIGH_VOL'
    WHEN bqx_std_15 < bqx_std_60 * 0.5 THEN 'LOW_VOL'
    ELSE 'NORMAL'
  END as volatility_regime,

  CASE
    WHEN bqx_ma_15 > bqx_ma_60 * 1.02 THEN 'STRONG_UP'
    WHEN bqx_ma_15 < bqx_ma_60 * 0.98 THEN 'STRONG_DOWN'
    ELSE 'RANGING'
  END as momentum_regime,

  -- Volatility metrics
  bqx_std_15, bqx_std_30, bqx_std_60,
  bqx_std_15 / NULLIF(bqx_std_60, 0) AS volatility_ratio,

  -- Momentum metrics
  bqx_ma_15, bqx_ma_30, bqx_ma_60,
  (bqx_ma_15 - bqx_ma_60) / NULLIF(bqx_ma_60, 0) AS momentum_strength,

  ...

FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}_{period}` lag
ORDER BY interval_time
```

**Success Criteria**:
- ✅ 56 tables created
- ✅ All tables have >1.9M rows
- ✅ Regime classifications valid (HIGH_VOL, LOW_VOL, NORMAL, etc.)
- ✅ Feature count matches IDX REGIME pattern (~150 features per table)

---

## 📊 PHASE 1B DELIVERABLES

### Tables to Create
- **Task 1B.1**: 56 BQX LAG tables
- **Task 1B.2**: 56 BQX REGIME tables
- **Total**: 112 new tables

### Final Inventory (After Phase 1B)
```
Current:  395 tables
Phase 1B: +112 tables
─────────────────────
Final:    507 tables
```

### Feature Count Impact
```
Current per pair:  ~700 features (IDX only)
Phase 1B adds:     ~350 BQX features
─────────────────────────────────────
Final per pair:    ~1,050 features
```

### Completeness Impact
```
Mandate total:     1,736 tables
After Phase 1B:    507 tables
─────────────────────────────────
Completeness:      29% (up from 19%)
Dual Architecture: 100% (up from 50%) ✅
```

---

## ⚡ EXECUTION PLAN

### Parallelization Strategy
**NOT REQUIRED** - Sequential execution acceptable given Phase 1 performance

**Reasoning**:
- Phase 1 Tasks 1.1 + 1.2 completed in 10 minutes (vs 16-24 hour estimate)
- Phase 1B estimated at 10-18 minutes total
- Parallelization overhead not justified for <20 minute tasks

### Recommended Approach
```bash
# Task 1B.1: Generate 56 BQX LAG tables (sequential)
python generate_lag_features.py \
  --source bqx \
  --pairs all \
  --periods 45,90 \
  --dataset bqx_ml_v3_features \
  --project bqx-ml \
  --location us-central1 \
  --workers 6

# Task 1B.2: Generate 56 BQX REGIME tables (sequential, after 1B.1)
python generate_regime_features.py \
  --source lag_bqx \
  --pairs all \
  --periods 45,90 \
  --dataset bqx_ml_v3_features \
  --project bqx-ml \
  --location us-central1 \
  --workers 6
```

**Estimated Duration**: 10-18 minutes total

---

## ✅ SUCCESS CRITERIA

### Task 1B.1 Success
- ✅ 56 BQX LAG tables created
- ✅ Table naming: `lag_bqx_{pair}_{period}`
- ✅ Source: `{pair}_bqx` tables
- ✅ Row count: ~2M per table
- ✅ Feature pattern matches IDX LAG (but using BQX source)
- ✅ No NULL values in primary lag features

### Task 1B.2 Success
- ✅ 56 BQX REGIME tables created
- ✅ Table naming: `regime_bqx_{pair}_{period}`
- ✅ Source: `lag_bqx_{pair}_{period}` tables
- ✅ Row count: ~2M per table
- ✅ Feature pattern matches IDX REGIME (but using BQX lag source)
- ✅ Valid regime classifications

### Phase 1B Success
- ✅ All 112 tables created (0 failures)
- ✅ Final table count: 507 tables
- ✅ Dual architecture: 100% complete
- ✅ Execution time: <20 minutes
- ✅ No errors, no retries needed

---

## 🔍 VALIDATION REQUIREMENTS

After completion, BA must validate:

### 1. Table Count Validation
```sql
SELECT
  COUNT(*) as total_tables,
  COUNTIF(table_name LIKE 'lag_bqx_%') as lag_bqx_tables,
  COUNTIF(table_name LIKE 'regime_bqx_%') as regime_bqx_tables
FROM bqx_ml_v3_features.INFORMATION_SCHEMA.TABLES
```

**Expected**: 507 total, 56 lag_bqx, 56 regime_bqx

### 2. Row Count Validation (Sample)
```sql
SELECT
  'lag_bqx_eurusd_45' as table_name,
  COUNT(*) as row_count,
  MIN(interval_time) as earliest,
  MAX(interval_time) as latest
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_eurusd_45`
```

**Expected**: ~2M rows, spans full time range

### 3. Feature Completeness (Sample)
```sql
SELECT
  COUNTIF(bqx_lag_1 IS NOT NULL) as has_lag_1,
  COUNTIF(bqx_lag_60 IS NOT NULL) as has_lag_60,
  COUNTIF(bqx_ma_15 IS NOT NULL) as has_ma_15,
  COUNT(*) as total_rows
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_eurusd_45`
```

**Expected**: All counts should equal total_rows (no NULLs)

### 4. Dual Architecture Validation
```sql
-- Confirm both IDX and BQX variants exist for each pair/period
WITH pairs AS (
  SELECT DISTINCT
    REGEXP_EXTRACT(table_name, r'lag_(.+?)_\d+') as pair
  FROM bqx_ml_v3_features.INFORMATION_SCHEMA.TABLES
  WHERE table_name LIKE 'lag_%'
)
SELECT
  pair,
  COUNTIF(table_name LIKE 'lag_' || pair || '%' AND table_name NOT LIKE '%_bqx_%') as idx_lag_count,
  COUNTIF(table_name LIKE 'lag_bqx_' || pair || '%') as bqx_lag_count
FROM pairs
CROSS JOIN bqx_ml_v3_features.INFORMATION_SCHEMA.TABLES
WHERE table_name LIKE 'lag_%'
GROUP BY pair
```

**Expected**: Each pair should have 2 idx_lag_count (45, 90) and 2 bqx_lag_count (45, 90)

---

## 📋 REPORTING REQUIREMENTS

BA must provide completion report with:

### 1. Execution Summary
- Start time, end time, total duration
- Tasks completed (1B.1, 1B.2)
- Success rate (expect 100%)

### 2. Table Inventory
- Final table count: 507 expected
- Breakdown: lag_bqx (56), regime_bqx (56), existing (395)

### 3. Validation Results
- All 4 validation queries (from above)
- Confirmation: Dual architecture 100% complete

### 4. Performance Metrics
- Execution time vs estimate (10-18 min estimate)
- Tables per minute
- Performance comparison to Phase 1

### 5. Next Steps Recommendation
- Phase 1B completeness: Should be 100%
- Mandate completeness: Expected ~29%
- Recommendation: Continue to Phase 2 (missing feature types) or pause

---

## 🚨 CRITICAL NOTES

### BQX Source Tables Confirmed Present
```
Total BQX source tables: 28 (verified)
Pattern: {pair}_bqx
Location: bqx_ml_v3_features dataset
```

**All BQX source tables available** - no data acquisition needed.

### Dual Architecture Pattern
- **IDX variants**: Use `{pair}_idx` as source (price-normalized OHLCV)
- **BQX variants**: Use `{pair}_bqx` as source (backward momentum)
- **Feature logic**: IDENTICAL for both (only source data differs)
- **Result**: Models can learn from BOTH price and momentum signals

### Script Reusability
- ✅ Reuse existing `generate_lag_features.py` with `--source bqx` flag
- ✅ Reuse existing `generate_regime_features.py` with `--source lag_bqx` flag
- ❌ NO new scripts needed (if scripts parameterized correctly)
- ⚠️ If scripts hardcoded to IDX → BA may need to modify or create variants

---

## 🎯 AUTHORIZATION

**CE Authorization**: ✅ **APPROVED TO EXECUTE**

**Scope**: Phase 1B - Generate 112 BQX dual variant tables

**Timeline**: Execute immediately, complete within 20 minutes

**Success Criteria**: 100% table creation, dual architecture complete

**Reporting**: Provide completion report immediately after execution

---

## 📞 NEXT STEPS AFTER PHASE 1B

Upon completion, BA should:

1. ✅ Mark Phase 1B complete
2. 📊 Provide completion report to CE
3. ⏸️ Await CE decision on Phase 2 (missing feature types) or project pause
4. 📋 Update mandate compliance (expect 29% vs 19% pre-Phase 1B)

**Expected CE Actions**:
- Review Phase 1B completion report
- Assess mandate gap (expect 71% remaining: 1,229 tables)
- Decide: Continue to Phase 2 (Regression, Aggregation, Alignment, Momentum, Volatility) or pause
- Consult user on timeline/scope tradeoffs

---

## 🎯 SUMMARY

**What**: Generate 112 BQX dual variant tables (lag_bqx_*, regime_bqx_*)

**Why**: Complete dual architecture foundation (mandate requirement)

**How**: Reuse Phase 1 scripts with BQX source data

**When**: Execute immediately

**Duration**: 10-18 minutes estimated

**Impact**: Dual architecture 100% complete, mandate compliance +10% (19% → 29%)

**Status**: ✅ **AUTHORIZED - EXECUTE IMMEDIATELY**

---

**- CE (Chief Engineer)**
**Phase 1B Authorization issued: 2025-11-28 18:00 UTC**
