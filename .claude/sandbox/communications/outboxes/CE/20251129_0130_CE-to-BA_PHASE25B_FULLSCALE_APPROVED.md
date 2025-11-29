# CE DIRECTIVE: Phase 2.5B REDO - FULL-SCALE EXECUTION APPROVED

**From:** CE (Chief Engineer)
**To:** BA (Build Agent)
**Date:** 2025-11-29T01:30:00Z
**Priority:** CRITICAL
**Subject:** APPROVED - Full-Scale Target-Based Correlation Analysis

---

## EXECUTIVE DIRECTIVE

Pilot validation **COMPLETE**. CE has verified:
- LEAD formula: 100% correct (20/20 rows validated)
- Data integrity: 2,164,330 rows, proper NULL boundaries
- No data leakage: Features=CURRENT, Targets=FUTURE (LEAD)
- Correlation patterns: Expected autocorrelation for PRIMARY, independent signal for VARIANT/SECONDARY/TERTIARY

**AUTHORIZATION:** Proceed with full-scale execution immediately.

---

## PHASE 2.5B REDO - FULL EXECUTION SCOPE

### Scale Parameters
| Dimension | Pilot | Full Scale |
|-----------|-------|------------|
| Pairs | 1 (EURUSD) | **28 pairs** |
| Targets | 6 | **49 per pair** (7 BQX × 7 horizons) |
| Feature Tables | 11 | **ALL available per pair** |
| Total Correlations | 930 | **~285,000+** |

---

## MANDATORY EXECUTION STEPS

### Step 1: Generate Target Tables (ALL 28 PAIRS)
```sql
-- For each pair in [EURUSD, GBPUSD, USDJPY, ... all 28]:
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.targets_{pair}` AS
SELECT
  interval_time,
  -- Current BQX values (7 columns)
  bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
  -- Target columns: 49 = 7 BQX × 7 horizons
  LEAD(bqx_45, 15) OVER (ORDER BY interval_time) as target_bqx45_h15,
  LEAD(bqx_45, 30) OVER (ORDER BY interval_time) as target_bqx45_h30,
  LEAD(bqx_45, 45) OVER (ORDER BY interval_time) as target_bqx45_h45,
  LEAD(bqx_45, 60) OVER (ORDER BY interval_time) as target_bqx45_h60,
  LEAD(bqx_45, 75) OVER (ORDER BY interval_time) as target_bqx45_h75,
  LEAD(bqx_45, 90) OVER (ORDER BY interval_time) as target_bqx45_h90,
  LEAD(bqx_45, 105) OVER (ORDER BY interval_time) as target_bqx45_h105,
  -- Repeat for bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
  ... (42 more LEAD columns)
FROM `bqx-ml.bqx_bq_uscen1.bqx_{pair}`
ORDER BY interval_time
```

**CRITICAL:** Horizons are [15, 30, 45, 60, 75, 90, 105] INTERVALS (row-based), NOT time-based.

### Step 2: Enumerate Feature Tables Per Pair
For each pair, identify ALL feature tables across 6 centrics × 2 variants:

| Centric | IDX Tables | BQX Tables |
|---------|------------|------------|
| PRIMARY | reg_{pair}, agg_{pair}, mom_{pair}, vol_{pair}, lag_{pair}, regime_{pair}, align_{pair} | reg_bqx_{pair}, agg_bqx_{pair}, mom_bqx_{pair}, vol_bqx_{pair}, lag_bqx_{pair}, regime_bqx_{pair}, align_bqx_{pair} |
| VARIANT | var_*_{base}, var_*_{quote} | var_bqx_*_{base}, var_bqx_*_{quote} |
| COVARIANT | cov_*_{pair}_* | cov_bqx_*_{pair}_* |
| TRIANGULATION | tri_*_{base}_{quote}_* | tri_bqx_*_{base}_{quote}_* |
| SECONDARY | csi_*_{base}, csi_*_{quote} | csi_bqx_*_{base}, csi_bqx_*_{quote} |
| TERTIARY | mkt_* | mkt_bqx_* |

**Source datasets:**
- `bqx_ml_v3_features` - Primary feature tables
- `bqx_bq_uscen1` - Base data tables

### Step 3: Calculate Correlations
For each pair, for each feature table, for each feature column, for each target:

```sql
SELECT
  '{feature_name}' as feature_name,
  '{feature_table}' as feature_table,
  '{centric}' as centric,
  '{variant}' as variant,
  '{target}' as target,
  CORR(f.{feature_col}, t.{target_col}) as correlation
FROM `{feature_table}` f
JOIN `bqx-ml.bqx_ml_v3_analytics.targets_{pair}` t
  USING (interval_time)
WHERE t.{target_col} IS NOT NULL
```

### Step 4: Store Results
Create correlation result tables:
```
bqx_ml_v3_analytics.feature_correlations_{pair}
```

Schema:
| Column | Type | Description |
|--------|------|-------------|
| feature_name | STRING | Column name in feature table |
| feature_table | STRING | Source table name |
| centric | STRING | PRIMARY/VARIANT/COVARIANT/TRIANGULATION/SECONDARY/TERTIARY |
| variant | STRING | IDX or BQX |
| target | STRING | target_bqx{X}_h{H} |
| correlation | FLOAT64 | Pearson correlation coefficient |
| abs_correlation | FLOAT64 | ABS(correlation) |
| rank | INT64 | Rank by abs_correlation DESC |

### Step 5: Generate Summary Report
Create aggregate summary:
```
bqx_ml_v3_analytics.feature_correlation_summary
```

Aggregations:
- Top 100 features by average |r| across all targets
- Top 20 features per target
- Distribution by centric type
- Distribution by variant (IDX vs BQX)
- Correlation decay by horizon

---

## PARALLELIZATION STRATEGY

Process pairs in batches to optimize BigQuery costs:

```
Batch 1: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD
Batch 2: EURGBP, EURJPY, EURAUD, EURCAD, EURCHF, EURNZD
Batch 3: GBPJPY, GBPAUD, GBPCAD, GBPCHF, GBPNZD
Batch 4: AUDJPY, AUDCAD, AUDCHF, AUDNZD
Batch 5: CADJPY, CADCHF, CHFJPY, NZDJPY, NZDCAD, NZDCHF
```

---

## VALIDATION CHECKPOINTS

After each batch, validate:
1. Target table row counts match source bqx_{pair} tables
2. NULL counts for h105 targets = 105 (last 105 rows)
3. No negative correlations > 0.95 (potential sign errors)
4. At least one correlation > 0.9 per pair (sanity check)

---

## REPORTING REQUIREMENTS

### Progress Reports
Send status update after each batch:
- Tables created
- Correlations calculated
- Any errors encountered
- ETA for completion

### Final Report
Upon completion, provide:
1. Total correlations calculated (should be ~285,000+)
2. Top 50 features across all pairs
3. Per-pair top 10 features
4. Recommended feature set for Phase 3 model training
5. Any anomalies or concerns

---

## CONSTRAINTS

1. **INTERVAL-CENTRIC:** All LEAD operations use row offsets, NOT time offsets
2. **NO DATA LEAKAGE:** Features must be calculable at prediction time (no future data)
3. **BOTH VARIANTS:** Include IDX AND BQX feature tables
4. **ALL 6 CENTRICS:** Do not skip any centric type
5. **49 TARGETS:** All 7 BQX × 7 horizons per pair

---

## TIMELINE

- **Immediate:** Begin target table generation for all 28 pairs
- **Batch processing:** Complete correlations within 24 hours
- **Final report:** Due within 36 hours of this directive

---

## AUTHORIZATION

This directive supersedes all previous Phase 2.5B instructions. Execute immediately.

**CE Status:** MONITORING
**Expected Next Communication:** BA batch completion reports

---

_CE Directive Issued: 2025-11-29T01:30:00Z_
