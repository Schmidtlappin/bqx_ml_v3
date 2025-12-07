# Catalog vs Mandate Gap Analysis

**Created:** 2025-12-07
**Purpose:** Reconcile BigQuery catalog with /mandate feature specifications

---

## Executive Summary

| Status | Count | Notes |
|--------|-------|-------|
| **MATCH** | 18 feature types | All required tables exist |
| **EXCEED** | 2 feature types | More tables than mandate requires |
| **MISSING** | 1 feature type | tmp_ (temporal) tables not created |
| **TOTAL GAP** | 28 tables | tmp_ tables need creation |

---

## Detailed Comparison

### Mandate: FEATURE_TABLE_DIRECTORY.md vs Actual Catalog

| Feature Type | Mandate Required | Actual Count | Status | Notes |
|--------------|-----------------|--------------|--------|-------|
| **PRIMARY FEATURES** |
| reg_ | 56 IDX + 56 BQX | 168 | EXCEEDS | Has additional reg_bqx_ tables |
| agg_ | 56 | 56 | MATCH | |
| align_ | 56 | 56 | MATCH | |
| vol_ | 56 | 56 | MATCH | |
| mom_ | 56 | 56 | MATCH | |
| lag_ | 112 | 112 | MATCH | Different naming: lag_{pair}_{window} |
| regime_ | 56 | 112 | EXCEEDS | Has both IDX and BQX variants |
| **OSCILLATION PREDICTION** |
| der_ | 56 | 56 | MATCH | Derivative features |
| div_ | 56 | 56 | MATCH | Divergence features |
| mrt_ | 28 (BQX only) | 56 | EXCEEDS | Has IDX variant too |
| rev_ | 56 | 56 | MATCH | Reversal features |
| cyc_ | 28 (BQX only) | 28 | MATCH | BQX-only by design |
| ext_ | 28 (BQX only) | 28 | MATCH | BQX-only by design |
| tmp_ | 28 | **0** | **MISSING** | Temporal features NOT created |
| **CROSS-MARKET** |
| cov_ | 2,352 | 2,352 | MATCH | Full covariance matrix |
| corr_ (ETF) | 448 | 448 | MATCH | ETF correlations |
| csi_ | 112 | 112 | MATCH | Currency strength |
| tri_ | 194 | 194 | MATCH | Triangular arbitrage |
| var_ | 114 | 114 | MATCH | Variance features |
| mkt_ | 18 | 18 | MATCH | Market-wide features |

---

## Gap Details

### MISSING: tmp_ (Temporal Patterns) - 28 Tables

Per mandate `/mandate/FEATURE_TABLE_DIRECTORY.md` Section 6.7:

> **TEMPORAL PATTERNS (tmp_) - 28 Tables (TIME-CENTRIC EXCEPTION)**
> Calendar and session effects in BQX behavior.

#### Required Tables
```
tmp_eurusd, tmp_gbpusd, tmp_usdjpy, tmp_usdchf, tmp_audusd, tmp_usdcad, tmp_nzdusd,
tmp_eurgbp, tmp_eurjpy, tmp_eurchf, tmp_euraud, tmp_eurcad, tmp_eurnzd,
tmp_gbpjpy, tmp_gbpchf, tmp_gbpaud, tmp_gbpcad, tmp_gbpnzd,
tmp_audjpy, tmp_audchf, tmp_audcad, tmp_audnzd,
tmp_nzdjpy, tmp_nzdchf, tmp_nzdcad,
tmp_cadjpy, tmp_cadchf, tmp_chfjpy
```

#### Required Features (per mandate)
- Trading session indicator (Asian, European, American)
- Session overlap indicator
- Hours until session change
- Session-specific volatility ratio
- Day of week effects
- Month of year effects
- Hour of day patterns

#### Implementation Note
This is the **ONLY time-centric feature type** per mandate. All others use interval-based calculations.

---

## Additional Findings

### 1. Naming Convention Variations

| Mandate Pattern | Actual Pattern | Count |
|-----------------|----------------|-------|
| `lag_{pair}` | `lag_{pair}_{window}` | 112 |
| `regime_{pair}` | Same + BQX variants | 112 |
| `mrt_bqx_{pair}` | `mrt_{pair}` + `mrt_bqx_{pair}` | 56 |

### 2. Extra Tables Beyond Mandate

| Type | Extra Count | Details |
|------|-------------|---------|
| reg_ | +56 | Additional polynomial variants |
| regime_ | +56 | IDX variants exist (mandate was BQX-only) |
| mrt_ | +28 | IDX variants exist (mandate was BQX-only) |

### 3. Base Data Tables (Not in Mandate)

56 tables in format `{pair}_idx` and `{pair}_bqx` exist as raw source data.
These are foundation tables, not feature tables.

---

## Remediation Plan

### Priority 1: Create tmp_ Tables (28 tables)

**Status:** NOT STARTED
**Estimated Time:** 2-4 hours
**Dependencies:** Source data (bqx_bq_uscen1)

#### SQL Template for tmp_ Tables
```sql
CREATE TABLE bqx_ml_v3_features_v2.tmp_idx_{pair}
PARTITION BY DATE(interval_time)
AS
SELECT
  interval_time,
  '{pair}' as pair,

  -- Session indicators
  CASE
    WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 0 AND 8 THEN 'ASIAN'
    WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 8 AND 16 THEN 'EUROPEAN'
    ELSE 'AMERICAN'
  END as trading_session,

  -- Session overlap
  CASE
    WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 8 AND 12 THEN 1
    WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 13 AND 17 THEN 1
    ELSE 0
  END as session_overlap,

  -- Time features
  EXTRACT(HOUR FROM interval_time) as hour_of_day,
  EXTRACT(DAYOFWEEK FROM interval_time) as day_of_week,
  EXTRACT(MONTH FROM interval_time) as month_of_year,

  -- Hours until next session
  MOD(24 - EXTRACT(HOUR FROM interval_time), 8) as hours_to_session_change

FROM bqx_ml_v3_features.{pair}_idx
```

### Priority 2: Include in Migration

When migration completes, tmp_ tables should be created in `bqx_ml_v3_features_v2` with proper naming:
- `tmp_idx_{pair}` (28 tables)

---

## Summary

| Metric | Value |
|--------|-------|
| **Mandate Required** | 3,472 tables |
| **Actual Existing** | 4,078 tables |
| **Coverage** | 117% (exceeds due to additional variants) |
| **Missing (tmp_)** | 28 tables |
| **Remediation Required** | Create tmp_ tables |

**The only gap is the tmp_ (temporal) feature set.** All other mandate requirements are met or exceeded.

---

*Analysis completed: 2025-12-07*
*Source: /mandate/FEATURE_TABLE_DIRECTORY.md, /mandate/BQX_ML_V3_FEATURE_INVENTORY.md*
