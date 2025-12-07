# BigQuery Restructure Plan

**Created:** 2025-12-07
**Purpose:** Clean up the 4,078-table mess in bqx_ml_v3_features
**Total Size:** 1.27 TB

---

## Current State Analysis

### Size by Feature Type

| Feature Type | Tables | Size (GB) | Avg MB/Table | Notes |
|--------------|--------|-----------|--------------|-------|
| **cov_*** | 2,352 | 515 GB | 224 | 40% of total! Cross-pair covariance |
| **reg_*** | 56 | 209 GB | 3,815 | Polynomial regression |
| **tri_*** | 194 | 97 GB | 514 | Triangular arbitrage |
| **var_*** | 114 | 93 GB | 836 | Currency variance |
| **agg_*** | 56 | 59 GB | 1,078 | Aggregation features |
| **corr_*** | 448 | 43 GB | 98 | ETF correlations |
| **mom_*** | 56 | 40 GB | 735 | Momentum |
| **align_*** | 56 | 39 GB | 719 | Alignment |
| **regime_*** | 112 | 31 GB | 282 | Regime classification |
| **vol_*** | 56 | 30 GB | 540 | Volatility |
| **lag_*** | 112 | 22 GB | 204 | Lagged features |
| **csi_*** | 112 | 21 GB | 196 | Currency strength |
| **der_*** | 56 | 15 GB | 279 | Derivatives |
| **mkt_*** | 18 | 15 GB | 867 | Market-wide |
| **mrt_*** | 56 | 11 GB | 198 | Mean reversion |
| **rev_*** | 56 | 11 GB | 198 | Reversal |
| **ext_*** | 28 | 8 GB | 295 | Extremity metrics |
| **div_*** | 56 | 6 GB | 118 | Divergence |
| **cyc_*** | 28 | 3 GB | 100 | Cycle position |
| **{pair}_*** | 56 | 10 GB | 192 | Raw base tables |
| **TOTAL** | **4,078** | **1,270 GB** | | |

### Current Naming Chaos

| Pattern | Example | Count | Issue |
|---------|---------|-------|-------|
| `{type}_{pair}` | `reg_eurusd` | ~500 | IDX variant not explicit |
| `{type}_bqx_{pair}` | `reg_bqx_eurusd` | ~500 | BQX explicit |
| `{type}_{source}_{pair}` | `csi_agg_eur` | ~200 | Subtype embedded |
| `{type}_{pair}_{window}` | `lag_eurusd_45` | ~112 | Window in name |
| `{type}_{pair1}_{pair2}` | `cov_reg_eurusd_gbpusd` | ~2,300 | Cross-pair |
| `{type}_{pair}_{etf}` | `corr_ibkr_eurusd_spy` | ~450 | ETF suffix |
| `{pair}_{variant}` | `eurusd_bqx` | ~56 | Raw base tables |

### Issues

1. **No partitioning** - Full table scans on every query ($$$)
2. **No clustering** - Can't filter efficiently
3. **Inconsistent variant marking** - IDX implied, BQX explicit
4. **Window embedded in name** - Should be column, not table split
5. **No catalog** - Have to guess table names

---

## Proposed Standard Naming Convention

### Format
```
{feature_type}_{variant}_{entity}[_{subentity}][_w{window}]
```

### Components

| Component | Values | Required |
|-----------|--------|----------|
| `feature_type` | reg, agg, vol, mom, der, div, mrt, align, rev, lag, cyc, ext, cov, corr, csi, tri, var, mkt, regime | Yes |
| `variant` | idx, bqx | Yes |
| `entity` | pair (eurusd), currency (eur), etf (spy), or "all" | Yes |
| `subentity` | second pair for cov/tri, or source type (agg, reg) | If applicable |
| `window` | w45, w90, w180, w360, w720, w1440, w2880 | Only if window-specific |

### Examples

| Current Name | New Name | Notes |
|--------------|----------|-------|
| `reg_eurusd` | `reg_idx_eurusd` | Add explicit variant |
| `reg_bqx_eurusd` | `reg_bqx_eurusd` | Already correct |
| `csi_agg_eur` | `csi_agg_idx_eur` | Move subtype, add variant |
| `csi_agg_bqx_eur` | `csi_agg_bqx_eur` | Already good |
| `lag_eurusd_45` | `lag_idx_eurusd_w45` | Add variant, window prefix |
| `cov_reg_eurusd_gbpusd` | `cov_reg_idx_eurusd_gbpusd` | Add variant |
| `corr_ibkr_eurusd_spy` | `corr_etf_idx_eurusd_spy` | Rename ibkr → etf |
| `eurusd_bqx` | `base_bqx_eurusd` | Add type prefix |
| `eurusd_idx` | `base_idx_eurusd` | Add type prefix |

---

## Restructure Options

### Option A: Views Only (Non-destructive)
- Create new views with standardized names
- Keep original tables
- Pro: No data movement, instant
- Con: 2x namespace pollution, no partitioning benefit

### Option B: Rename + Views (Medium effort)
- Rename tables to new convention
- Create backward-compat views with old names
- Pro: Clean namespace, backward compat
- Con: Still no partitioning

### Option C: Full Restructure (Recommended)
- Create new tables with partitioning/clustering
- Load data from old tables
- Drop old tables after validation
- Pro: Full optimization, clean slate
- Con: 1.27 TB data copy (~$6 in BQ costs)

---

## Recommended Approach: Option C with Phased Rollout

### Phase 1: Create New Dataset
```sql
CREATE SCHEMA IF NOT EXISTS bqx_ml_v3_features_v2
OPTIONS (
  location = 'us-central1',
  description = 'Restructured feature tables with partitioning'
);
```

### Phase 2: Migrate Tables by Priority

| Priority | Feature Types | Tables | Size | Est. Time |
|----------|--------------|--------|------|-----------|
| P1 | reg, agg, align, vol, mom, der, div, mrt | 448 | 418 GB | 2 hrs |
| P2 | cov (sampling first) | 2,352 | 515 GB | 3 hrs |
| P3 | tri, var, corr, csi, lag, mkt, regime | 1,110 | 323 GB | 2 hrs |
| P4 | rev, ext, cyc, base | 168 | 32 GB | 30 min |

### Phase 3: Table Structure

For pair-level tables:
```sql
CREATE TABLE bqx_ml_v3_features_v2.reg_idx_eurusd
PARTITION BY DATE(interval_time)
CLUSTER BY pair
AS SELECT * FROM bqx_ml_v3_features.reg_eurusd;
```

For cross-pair tables (cov):
```sql
CREATE TABLE bqx_ml_v3_features_v2.cov_reg_idx_eurusd_gbpusd
PARTITION BY DATE(interval_time)
CLUSTER BY pair1, pair2
AS SELECT * FROM bqx_ml_v3_features.cov_reg_eurusd_gbpusd;
```

### Phase 4: Update Catalog
```sql
-- Update feature_catalog with new names and partitioning status
UPDATE bqx_ml_v3_analytics.feature_catalog
SET
  migrated = TRUE,
  new_name = suggested_name,
  partitioned = TRUE,
  clustered = TRUE
WHERE original_name = 'reg_eurusd';
```

### Phase 5: Create Compatibility Views
```sql
-- Old name points to new table
CREATE VIEW bqx_ml_v3_features.reg_eurusd
AS SELECT * FROM bqx_ml_v3_features_v2.reg_idx_eurusd;
```

### Phase 6: Validate and Cleanup
- Compare row counts between old and new
- Run spot correlation checks
- Archive old dataset (don't delete immediately)
- Update all scripts to use new dataset

---

## Cost Estimate

| Operation | GB Processed | Cost |
|-----------|--------------|------|
| Create new tables (CTAS) | 1,270 GB | $0 (no read cost for CTAS) |
| Storage (duplicate during migration) | 1,270 GB × $0.02/GB | ~$25/month |
| Query savings (partitioning) | -50% reads | Ongoing savings |

**Total one-time cost: ~$25 (1 month duplicate storage)**
**Ongoing savings: 50%+ query cost reduction**

---

## Execution Script Location

Migration scripts will be in:
```
/scripts/bigquery_restructure/
├── 01_create_new_dataset.sql
├── 02_migrate_primary_tables.py
├── 03_migrate_covariance_tables.py
├── 04_create_compat_views.py
├── 05_validate_migration.py
└── 06_cleanup_old_tables.py
```

---

## Decision Required

Before proceeding, confirm:

1. **Dataset name:** `bqx_ml_v3_features_v2` or different?
2. **Backward compat views:** Create in old dataset or skip?
3. **Start phase:** Begin with P1 (primary features) or full parallel?

---

*Plan created: 2025-12-07*
*Estimated migration time: 8-10 hours*
*Estimated cost: ~$25 one-time + significant ongoing query savings*
