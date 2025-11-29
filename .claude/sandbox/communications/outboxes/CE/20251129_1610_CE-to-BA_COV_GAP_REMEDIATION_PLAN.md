# CE to BA: Covariance Gap Remediation Plan

**From:** Chief Engineer (CE)
**To:** Builder Agent (BA)
**Date:** 2025-11-29T16:10:00Z
**Priority:** HIGH
**Subject:** EXECUTE - Complete cov_* Covariance Tables (267 Tables)

---

## DIRECTIVE

Complete all covariance (cov_*) feature tables to ensure full 8×7 currency cross coverage.

**Requirement:** Each of the 8 currencies (USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD) must have 7 crosses.

---

## GAP ANALYSIS SUMMARY

| Prefix | Current | Target | Gap |
|--------|---------|--------|-----|
| cov_agg | 10 | 28 | 18 |
| cov_agg_bqx | 10 | 28 | 18 |
| cov_align | 10 | 28 | 18 |
| cov_align_bqx | 10 | 28 | 18 |
| cov_lag | 7 | 28 | 21 |
| cov_lag_bqx | 7 | 28 | 21 |
| cov_mom | 10 | 28 | 18 |
| cov_mom_bqx | 10 | 28 | 18 |
| cov_reg | 10 | 28 | 18 |
| cov_reg_bqx | 10 | 28 | 18 |
| cov_regime | 7 | 28 | 21 |
| cov_regime_bqx | 7 | 28 | 21 |
| cov_vol | 10 | 28 | 18 |
| cov_vol_bqx | 10 | 28 | 18 |
| **TOTAL** | **122** | **392** | **270** |

---

## MISSING PAIRS BY CATEGORY

### Category A: Missing 18 pairs (cov_agg, cov_align, cov_mom, cov_reg, cov_vol + BQX variants)
```
eurgbp, eurcad, eurnzd, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd,
audjpy, audchf, audcad, audnzd, nzdjpy, nzdchf, nzdcad, cadjpy, cadchf, chfjpy
```

### Category B: Missing 21 pairs (cov_lag, cov_regime + BQX variants)
```
usdchf, usdcad, nzdusd, euraud, eurcad, eurnzd, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd,
audjpy, audchf, audcad, audnzd, nzdjpy, nzdchf, nzdcad, cadjpy, cadchf, chfjpy
```

---

## IMPLEMENTATION PLAN

### Phase 1: Analyze Existing cov_* Tables (10 min)

```sql
-- Get schema from existing table
SELECT column_name, data_type
FROM `bqx-ml.bqx_ml_v3_features.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'cov_agg_eurusd'
ORDER BY ordinal_position;
```

### Phase 2: Create Category A Tables (10 prefixes × 18 pairs = 180 tables)

For each prefix in [cov_agg, cov_agg_bqx, cov_align, cov_align_bqx, cov_mom, cov_mom_bqx, cov_reg, cov_reg_bqx, cov_vol, cov_vol_bqx]:

```sql
-- Template: Create cov_{type}_{pair} from source data
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features.{prefix}_{pair}` AS
SELECT * FROM (
  -- Use same SQL pattern as existing {prefix}_eurusd
  -- Adapted for {pair}
);
```

### Phase 3: Create Category B Tables (4 prefixes × 21 pairs = 84 tables)

For each prefix in [cov_lag, cov_lag_bqx, cov_regime, cov_regime_bqx]:

```sql
-- Template: Create cov_{type}_{pair} from source data
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features.{prefix}_{pair}` AS
SELECT * FROM (
  -- Use same SQL pattern as existing {prefix}_eurusd
  -- Adapted for {pair}
);
```

### Phase 4: Cleanup Malformed Tables

Delete incorrectly named tables (contain pair within prefix):
```sql
-- These tables have wrong naming convention
DROP TABLE IF EXISTS `bqx-ml.bqx_ml_v3_features.cov_agg_audusd_usdjpy`;
DROP TABLE IF EXISTS `bqx-ml.bqx_ml_v3_features.cov_agg_bqx_audusd_usdjpy`;
-- (12 tables total)
```

Also delete temporary table:
```sql
DROP TABLE IF EXISTS `bqx-ml.bqx_ml_v3_features.temp_m1_usdchf`;
```

---

## EXECUTION BATCHES

| Batch | Prefixes | Pairs | Tables | Est. Time |
|-------|----------|-------|--------|-----------|
| 1 | cov_agg, cov_agg_bqx | 18 each | 36 | 15 min |
| 2 | cov_align, cov_align_bqx | 18 each | 36 | 15 min |
| 3 | cov_mom, cov_mom_bqx | 18 each | 36 | 15 min |
| 4 | cov_reg, cov_reg_bqx | 18 each | 36 | 15 min |
| 5 | cov_vol, cov_vol_bqx | 18 each | 36 | 15 min |
| 6 | cov_lag, cov_lag_bqx | 21 each | 42 | 20 min |
| 7 | cov_regime, cov_regime_bqx | 21 each | 42 | 20 min |
| 8 | Cleanup malformed tables | - | 13 | 5 min |
| **TOTAL** | 14 prefixes | - | **277** | **~2 hours** |

---

## VALIDATION REQUIREMENTS

After each batch:
```sql
-- Verify all 28 pairs exist for prefix
SELECT
  REGEXP_EXTRACT(table_id, r'^(cov_[a-z_]+)_[a-z]+$') as prefix,
  COUNT(*) as pair_count
FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'cov_agg_%'
  AND table_id NOT LIKE 'cov_agg_audusd_%'  -- Exclude malformed
GROUP BY prefix;
-- Expected: 28 for each prefix
```

Final validation:
```sql
-- All cov_* prefixes should have 28 pairs
SELECT
  REGEXP_EXTRACT(table_id, r'^(cov_[a-z_]+)_[a-z]+$') as prefix,
  COUNT(*) as pair_count
FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'cov_%'
  AND table_id NOT LIKE '%audusd_%'  -- Exclude malformed
GROUP BY prefix
ORDER BY prefix;
-- Expected: 14 rows, each with pair_count = 28
```

---

## SUCCESS CRITERIA

1. All 14 cov_* prefixes have exactly 28 tables each
2. Total cov_* tables: 392 (was 122)
3. All malformed tables deleted
4. Row counts match source data (~2.17M per pair)
5. Schema matches existing tables

---

## REPORTING

Send progress report after each batch completion:
- Tables created
- Validation results
- Any errors encountered

Final report should include:
- Total tables created
- Final validation query results
- Updated feature table count

---

**AUTHORIZATION:** EXECUTE IMMEDIATELY

*Directive issued: 2025-11-29T16:10:00Z*
