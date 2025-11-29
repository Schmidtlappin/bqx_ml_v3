# CE DIRECTIVE ADDENDUM: PRIMARY BQX corr_ Table Remediation

**From:** CE (Chief Engineer)
**To:** BA (Build Agent)
**Date:** 2025-11-29T01:45:00Z
**Priority:** HIGH
**Subject:** REMEDIATION - Create corr_bqx_ibkr_{pair}_{asset} Tables (224 tables)
**Parent Directive:** 20251129_0130_CE-to-BA_PHASE25B_FULLSCALE_APPROVED.md

---

## EXECUTIVE SUMMARY

During matrix validation, CE identified a gap in PRIMARY BQX correlation tables. The IDX variant exists (224 tables) but BQX variant is missing.

**SCOPE:** Create 224 `corr_bqx_ibkr_{pair}_{asset}` tables
- 28 pairs × 8 external assets = 224 tables
- Parallel execution with Phase 2.5B full-scale correlation analysis

---

## GAP ANALYSIS

### Current State
| Variant | Tables | Status |
|---------|--------|--------|
| IDX | corr_ibkr_{pair}_{asset} | ✅ 224 tables exist |
| BQX | corr_bqx_ibkr_{pair}_{asset} | ❌ 0 tables - MISSING |

### External Assets (8)
| Asset | Description |
|-------|-------------|
| EWA | iShares MSCI Australia ETF |
| EWG | iShares MSCI Germany ETF |
| EWJ | iShares MSCI Japan ETF |
| EWU | iShares MSCI United Kingdom ETF |
| GLD | SPDR Gold Shares |
| SPY | SPDR S&P 500 ETF |
| UUP | Invesco DB US Dollar Index ETF |
| VIX | CBOE Volatility Index |

---

## REMEDIATION SPECIFICATION

### Source Schema (IDX Reference)
```sql
-- From corr_ibkr_{pair}_{asset}
interval_time     TIMESTAMP
fx_pair           STRING
ibkr_instrument   STRING
corr_30min        FLOAT64
corr_60min        FLOAT64
corr_90min        FLOAT64
covar_60min       FLOAT64
fx_volatility_60min    FLOAT64
ibkr_volatility_60min  FLOAT64
```

### Target Schema (BQX)
```sql
-- For corr_bqx_ibkr_{pair}_{asset}
interval_time     TIMESTAMP
fx_pair           STRING
ibkr_instrument   STRING
bqx_corr_30min    FLOAT64   -- Correlation of BQX values with asset
bqx_corr_60min    FLOAT64
bqx_corr_90min    FLOAT64
bqx_covar_60min   FLOAT64   -- Covariance of BQX values with asset
bqx_volatility_60min   FLOAT64  -- Volatility of BQX values
ibkr_volatility_60min  FLOAT64  -- Same as IDX (asset volatility unchanged)
```

### SQL Template
```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features.corr_bqx_ibkr_{pair}_{asset}` AS
WITH
-- Get BQX values for the pair
bqx_data AS (
  SELECT
    interval_time,
    bqx_45 as bqx_value  -- Use primary BQX component
  FROM `bqx-ml.bqx_bq_uscen1.bqx_{pair}`
),
-- Get external asset data
asset_data AS (
  SELECT
    interval_time,
    close as asset_value
  FROM `bqx-ml.bqx_bq_uscen1.m1_{asset}`  -- Or appropriate source
),
-- Join and calculate rolling correlations
joined AS (
  SELECT
    b.interval_time,
    '{PAIR}' as fx_pair,
    '{asset}' as ibkr_instrument,
    b.bqx_value,
    a.asset_value
  FROM bqx_data b
  JOIN asset_data a USING (interval_time)
)
SELECT
  interval_time,
  fx_pair,
  ibkr_instrument,
  -- 30-minute rolling correlation
  CORR(bqx_value, asset_value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
  ) as bqx_corr_30min,
  -- 60-minute rolling correlation
  CORR(bqx_value, asset_value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
  ) as bqx_corr_60min,
  -- 90-minute rolling correlation
  CORR(bqx_value, asset_value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
  ) as bqx_corr_90min,
  -- 60-minute covariance
  COVAR_SAMP(bqx_value, asset_value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
  ) as bqx_covar_60min,
  -- BQX volatility
  STDDEV(bqx_value) OVER (
    ORDER BY interval_time
    ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
  ) as bqx_volatility_60min,
  -- Asset volatility (from original IDX table)
  ibkr.ibkr_volatility_60min
FROM joined j
LEFT JOIN `bqx-ml.bqx_ml_v3_features.corr_ibkr_{pair}_{asset}` ibkr
  USING (interval_time)
ORDER BY interval_time
```

---

## EXECUTION PLAN

### Step 1: Verify External Asset Data Sources
Confirm availability of m1_{asset} tables or equivalent for:
- EWA, EWG, EWJ, EWU, GLD, SPY, UUP, VIX

### Step 2: Create Tables (Batched by Pair)
```
Batch 1: EURUSD × 8 assets = 8 tables
Batch 2: GBPUSD × 8 assets = 8 tables
... (28 batches total)
```

### Step 3: Validation
For each created table:
- Row count matches corresponding IDX table
- No NULL correlations (except initial window)
- Correlation values in [-1, 1] range

### Step 4: Register in Feature Inventory
Update metadata to reflect 224 new tables.

---

## PRIORITIZATION

| Task | Priority | Dependency |
|------|----------|------------|
| Phase 2.5B Full-Scale Correlation | P1 | None |
| corr_bqx_ Remediation | P2 | Can run in parallel |

**Execute corr_bqx_ remediation AFTER Phase 2.5B target generation, but can run PARALLEL with correlation analysis.**

---

## DELIVERABLES

1. 224 `corr_bqx_ibkr_{pair}_{asset}` tables created
2. Validation report confirming data integrity
3. Update to feature inventory metadata

---

## SKIPPED REMEDIATIONS (CE CONFIRMED)

The following gaps are **intentionally NOT remediated**:

| Gap | Reason |
|-----|--------|
| COVARIANT corr_ | Correlation of correlations is redundant |
| SECONDARY corr_ | Correlation of CSI features is redundant |
| TRIANGULATION lag/regime/corr | By architectural design |

---

## TIMELINE

- **Start:** After Phase 2.5B target table generation complete
- **Duration:** ~2-4 hours (parallelizable)
- **Completion:** Before Phase 2.5B correlation analysis ends

---

_CE Directive Addendum Issued: 2025-11-29T01:45:00Z_
