# CE to BA: Feature Table Gap Remediation Task

**From:** Chief Engineer (CE)
**To:** Builder Agent (BA)
**Date:** 2025-11-29T16:00:00Z
**Priority:** HIGH
**Subject:** Complete Coverage for Covariance (cov_*) Feature Tables

---

## Context

BigQuery audit reveals 1,983 feature tables exist (114.2% of 1,736 mandate target).
However, covariance (cov_*) feature tables have incomplete currency pair coverage.

## Current State

### Complete Prefixes (17) - NO ACTION NEEDED
These prefixes have all 28 currency pairs:
- `agg`, `agg_bqx` (28/28 each)
- `align`, `align_bqx` (28/28 each)
- `corr_ibkr`, `corr_bqx_ibkr` (28/28 each)
- `lag`, `lag_bqx` (28/28 each)
- `mom`, `mom_bqx` (28/28 each)
- `reg`, `reg_bqx` (28/28 each)
- `regime`, `regime_bqx` (28/28 each)
- `vol`, `vol_bqx` (28/28 each)

### Gaps Requiring Remediation

**CRITICAL: cov_* Tables Missing 18-21 Pairs**

| Prefix | Existing | Missing | Missing Pairs |
|--------|----------|---------|---------------|
| cov_agg | 10/28 | 18 | eurgbp, eurcad, eurnzd, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd, audjpy, audchf, audcad, audnzd, nzdjpy, nzdchf, nzdcad, cadjpy, cadchf, chfjpy |
| cov_agg_bqx | 10/28 | 18 | (same as above) |
| cov_align | 10/28 | 18 | (same as above) |
| cov_align_bqx | 10/28 | 18 | (same as above) |
| cov_lag | 7/28 | 21 | usdchf, usdcad, nzdusd, euraud, eurcad, eurnzd, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd, audjpy, audchf, audcad, audnzd, nzdjpy, nzdchf, nzdcad, cadjpy, cadchf, chfjpy |
| cov_lag_bqx | 7/28 | 21 | (same as above) |
| cov_mom | 10/28 | 18 | (same as cov_agg) |
| cov_mom_bqx | 10/28 | 18 | (same as cov_agg) |
| cov_reg | 10/28 | 18 | (same as cov_agg) |
| cov_reg_bqx | 10/28 | 18 | (same as cov_agg) |
| cov_regime | 7/28 | 21 | (same as cov_lag) |
| cov_regime_bqx | 7/28 | 21 | (same as cov_lag) |
| cov_vol | 10/28 | 18 | (same as cov_agg) |
| cov_vol_bqx | 10/28 | 18 | (same as cov_agg) |

**IGNORE: cov_*_audusd Tables**
These appear to be incorrectly named - they contain a pair within the prefix.
These should probably be cleaned up rather than remediated.

**IGNORE: temp_m1**
Temporary table - can be deleted.

## Task Assignment

### TASK 1: Complete cov_* Tables (14 prefixes × ~18-21 pairs = ~267 tables)

For each prefix in the gap list:
1. Use existing complete tables as templates
2. Create missing pair tables following same schema
3. Ensure dual architecture (both IDX and BQX variants)
4. Validate row counts match source data (~2.17M rows per pair)

### TASK 2: Cleanup Incorrectly Named Tables

Delete the following malformed tables:
- All `cov_*_audusd_*` tables (12 tables with wrong naming convention)
- `temp_m1_usdchf` (temporary table)

### Requirements Reminder

**8 Currencies × 7 Crosses = 28 Unique Pairs**
```
USD: eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd (7 crosses)
EUR: eurgbp, eurjpy, eurchf, euraud, eurcad, eurnzd (6 crosses)
GBP: gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd (5 crosses)
AUD: audjpy, audchf, audcad, audnzd (4 crosses)
NZD: nzdjpy, nzdchf, nzdcad (3 crosses)
CAD: cadjpy, cadchf (2 crosses)
CHF: chfjpy (1 cross)
```

Total: 7+6+5+4+3+2+1 = 28 pairs

## Expected Outcome

After remediation:
- All 14 cov_* prefixes should have 28/28 pairs
- Total new tables: ~267
- Final feature table count: ~2,237 tables

## Verification Command

```sql
-- Verify each prefix has 28 tables
SELECT
  REGEXP_EXTRACT(table_id, r'^(cov_[a-z_]+)_[a-z]+$') as prefix,
  COUNT(*) as pair_count
FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'cov_%'
GROUP BY prefix
HAVING COUNT(*) < 28
ORDER BY prefix;
```

---

**Awaiting BA acknowledgment and execution plan.**
