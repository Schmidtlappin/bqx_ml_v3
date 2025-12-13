# EA UPDATE: Feature Generation Scripts - Reverse-Engineered from Archive

**Date**: December 12, 2025 23:45 UTC
**From**: Enhancement Assistant (EA)
**To**: Build Agent (BA)
**Re**: Feature generation scripts found in archive - can proceed with modified approach
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## STATUS UPDATE

**Finding**: ✅ Found `generate_regression_features.py` in archive showing feature generation pattern using BigQuery window functions

**Solution**: Can create tri/cov/corr generation scripts using same pattern

**Timeline**: Scripts ready in 30-60 minutes (reverse-engineering from existing table schemas + regression template)

**Risk**: MEDIUM - Scripts will recreate tables with same structure but may have slightly different values than originals

---

## WHAT I FOUND

### Archive Script: generate_regression_features.py

**Location**: `/home/micha/bqx_ml_v3/archive/phase_2_artifacts_20251128/generate_regression_features.py`

**What it shows**:
- How to use BigQuery window functions (AVG, STDDEV, MIN, MAX over ROWS BETWEEN)
- How to ensure 100% row coverage (FROM source table directly)
- How to create features at multiple windows (45, 90, 180, 360, 720, 1440, 2880)
- How to parallelize with ThreadPoolExecutor

**Template SQL**:
```python
sql = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{target_table}` AS
SELECT
  interval_time,
  '{pair}' as pair,
  -- Window-based features
  AVG(value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW
  ) AS feature_mean_{window},
  ...
FROM `{PROJECT}.{DATASET}.{source_table}`
WHERE value IS NOT NULL
ORDER BY interval_time
"""
```

---

## REVERSE-ENGINEERING APPROACH

### For TRI Tables (Triangular Arbitrage)

**From test_triangulation_features.py logic** + **BigQuery schema inspection**:

```python
# tri_agg_bqx_eur_usd_gbp calculation
sql = f"""
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`
PARTITION BY DATE(interval_time)
AS
WITH
  eurusd_data AS (
    SELECT interval_time, bqx_45 as eur_usd FROM `bqx-ml.bqx_ml_v3_features_v2.base_bqx_eurusd`
  ),
  gbpusd_data AS (
    SELECT interval_time, bqx_45 as gbp_usd FROM `bqx-ml.bqx_ml_v3_features_v2.base_bqx_gbpusd`
  ),
  eurgbp_data AS (
    SELECT interval_time, bqx_45 as eur_gbp FROM `bqx-ml.bqx_ml_v3_features_v2.base_bqx_eurgbp`
  ),
  all_intervals AS (
    SELECT DISTINCT interval_time FROM eurusd_data
    UNION DISTINCT
    SELECT DISTINCT interval_time FROM gbpusd_data
    UNION DISTINCT
    SELECT DISTINCT interval_time FROM eurgbp_data
  )
SELECT
  ai.interval_time,
  'EUR' as base_curr,
  'USD' as quote_curr,
  'GBP' as cross_curr,
  e1.eur_usd as pair1_val,
  e2.gbp_usd as pair2_val,
  e3.eur_gbp as pair3_val,
  e1.eur_usd * (1/e2.gbp_usd) as synthetic_val,  -- EUR/USD * USD/GBP
  e3.eur_gbp - (e1.eur_usd * (1/e2.gbp_usd)) as tri_error,
  AVG(tri_error) OVER w45 as error_ma_45,
  AVG(tri_error) OVER w180 as error_ma_180,
  STDDEV(tri_error) OVER w180 as error_std_180,
  ...
FROM all_intervals ai
LEFT JOIN eurusd_data e1 ON ai.interval_time = e1.interval_time
LEFT JOIN gbpusd_data e2 ON ai.interval_time = e2.interval_time
LEFT JOIN eurgbp_data e3 ON ai.interval_time = e3.interval_time
WINDOW
  w45 AS (ORDER BY ai.interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
  w180 AS (ORDER BY ai.interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
"""
```

### For COV Tables (Covariance)

**From schema inspection** + **standard covariance formula**:

```python
# cov_agg_eurusd_gbpusd calculation
sql = f"""
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.cov_agg_eurusd_gbpusd`
PARTITION BY DATE(interval_time)
AS
WITH
  eurusd_data AS (
    SELECT interval_time, bqx_45 as value1 FROM `bqx-ml.bqx_ml_v3_features_v2.base_bqx_eurusd`
  ),
  gbpusd_data AS (
    SELECT interval_time, bqx_45 as value2 FROM `bqx-ml.bqx_ml_v3_features_v2.base_bqx_gbpusd`
  ),
  all_intervals AS (
    SELECT DISTINCT interval_time FROM eurusd_data
    UNION DISTINCT
    SELECT DISTINCT interval_time FROM gbpusd_data
  )
SELECT
  ai.interval_time,
  'eurusd' as pair1,
  'gbpusd' as pair2,
  e1.value1,
  e2.value2,
  -- Covariance at multiple windows
  COVAR_POP(e1.value1, e2.value2) OVER w45 as cov_45,
  COVAR_POP(e1.value1, e2.value2) OVER w180 as cov_180,
  ...
FROM all_intervals ai
LEFT JOIN eurusd_data e1 ON ai.interval_time = e1.interval_time
LEFT JOIN gbpusd_data e2 ON ai.interval_time = e2.interval_time
WINDOW
  w45 AS (ORDER BY ai.interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
  w180 AS (ORDER BY ai.interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
"""
```

### For CORR Tables (Correlation)

**Similar to COV but using CORR() function**:

```python
# Similar pattern using CORR(value1, value2) OVER window
```

---

## IMPLEMENTATION PLAN (UPDATED)

### Option: Reverse-Engineer with Template

**Timeline**:
1. **NOW - 00:15 UTC** (30 min): EA creates generation scripts using regression template
2. **00:15 - 00:30 UTC** (15 min): BA reviews and validates SQL logic
3. **00:30 UTC**: Launch Tier 1 Batch 1 (if approved)

**Scripts to create**:
1. `generate_tri_tables.py` - 194 triangulation tables
2. `generate_cov_tables.py` - 2,507 covariance tables
3. `generate_corr_tables.py` - 896 correlation tables
4. Use existing `generate_mkt_tables.py` - 12 market tables

**Risk Assessment**:
- ✅ Row coverage: Will be 100% (using all_intervals CTE + LEFT JOIN)
- ⚠️ Feature values: May differ from originals if calculation logic assumptions are wrong
- ✅ Schema: Matches existing tables (validated from INFORMATION_SCHEMA)

---

## RECOMMENDATION

**Proceed with reverse-engineering** because:

1. ✅ Found solid template (generate_regression_features.py)
2. ✅ Understand feature logic from test scripts
3. ✅ Can validate schemas from existing tables
4. ✅ User mandate: "data to be complete" - fixing row coverage is primary goal
5. ⚠️ Acceptable risk: Slightly different values OK if row coverage fixed

**BA Action**:
- ⏸️ STANDBY for EA to deliver 3 generation scripts (30 min)
- ✅ Review SQL logic when ready
- ✅ Launch Tier 1 at ~00:30 UTC (1 hour delay from original plan)

---

## NEXT STEPS

**EA (IMMEDIATE)**:
1. Create `generate_tri_tables.py` using regression template + tri logic
2. Create `generate_cov_tables.py` using COV AR_POP() window function
3. Create `generate_corr_tables.py` using CORR() window function
4. Deliver to BA for review

**BA (AFTER SCRIPTS READY)**:
1. Review SQL logic (5-10 min)
2. Test on 1-2 tables (5 min)
3. If validation passes: Launch full Tier 1
4. If validation fails: Escalate to CE for guidance

---

**Enhancement Assistant (EA)**
*Feature Generation Scripts*

**Status**: ⚙️ CREATING SCRIPTS - reverse-engineering from archive template

**ETA**: 30 minutes (00:15 UTC)

**Confidence**: MEDIUM-HIGH (template found, can recreate structure/logic)

---

**END OF UPDATE**
