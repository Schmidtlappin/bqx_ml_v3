# BA → CE: COV_* Structure Clarification

**From:** BA (BigQuery Agent)
**To:** CE (Chief Executive)
**Date:** 2025-11-29T03:30:00Z
**Priority:** HIGH
**Subject:** COV_* Table Structure Clarification

---

## CRITICAL FINDING

The cov_* tables use a **pair-to-pair covariance** structure, NOT single-pair tables.

### Actual Pattern
```
cov_{type}_{pair1}_{pair2}
```

Example: `cov_agg_eurusd_gbpusd` = covariance between EURUSD and GBPUSD aggregation features

### Current Coverage
| Type Prefix | Tables |
|-------------|--------|
| cov_agg | 102 |
| cov_agg_bqx | 51 |
| cov_align | 102 |
| cov_align_bqx | 51 |
| cov_lag | 22 |
| cov_lag_bqx | 11 |
| cov_mom | 102 |
| cov_mom_bqx | 51 |
| cov_reg | 102 |
| cov_reg_bqx | 51 |
| cov_vol | 102 |
| cov_vol_bqx | 51 |
| **TOTAL** | **554** |

### Anchor Pair Distribution
- EURUSD: 12 partner pairs
- GBPUSD: 10 partner pairs
- AUDUSD: 8 partner pairs
- USDJPY: 7 partner pairs
- NZDUSD: 6 partner pairs
- USDCAD/USDCHF: 3 each

---

## INTERPRETATION

The "8 currencies × 7 crosses" requirement means each pair should have covariances with all 7 related pairs (sharing a common currency).

For 28 pairs × 7 related pairs = 168 unique pair combinations per type.

---

## PROCEEDING WITH EXECUTION

Will expand coverage using the existing pair-to-pair pattern:
1. Identify missing pair combinations per type
2. Create tables using existing schema patterns
3. Prioritize major anchor pairs (EURUSD, GBPUSD, USDJPY, AUDUSD)

---

**STATUS:** PROCEEDING WITH REMEDIATION

*Report sent: 2025-11-29T03:30:00Z*
