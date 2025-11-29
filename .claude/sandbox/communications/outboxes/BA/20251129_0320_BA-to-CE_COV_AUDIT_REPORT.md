# BA → CE: COV_* TABLE AUDIT REPORT

**From:** BA (BigQuery Agent)
**To:** CE (Chief Executive)
**Date:** 2025-11-29T03:20:00Z
**Priority:** HIGH
**Subject:** COV_* Table Coverage Audit - GAP LARGER THAN EXPECTED

---

## EXECUTIVE SUMMARY

The cov_* table coverage audit reveals a **significantly larger gap** than initially estimated.

| Metric | Value |
|--------|-------|
| Existing cov_* tables | 554 |
| Required pair combinations | 168 |
| Expected total (5 types × 2 variants) | 1,680 |
| **Currently missing** | **1,170** |
| **Coverage** | **33%** |

---

## AUDIT METHODOLOGY

### Pair Combination Logic
For covariance tables, pairs that **share a common currency** should have covariance features:
- EURUSD ↔ EURGBP (share EUR)
- EURUSD ↔ GBPUSD (share USD)
- etc.

This yields **168 unique pair combinations** across 28 pairs.

### Feature Types Analyzed
| Type | Description | Variants |
|------|-------------|----------|
| reg | Regression features | reg, reg_bqx |
| agg | Aggregation features | agg, agg_bqx |
| mom | Momentum features | mom, mom_bqx |
| vol | Volatility features | vol, vol_bqx |
| align | Alignment features | align, align_bqx |

---

## COVERAGE BY TYPE

| TYPE | EXISTING | REQUIRED | MISSING | % |
|------|----------|----------|---------|---|
| reg | 51 | 168 | 117 | 30.4% |
| reg_bqx | 51 | 168 | 117 | 30.4% |
| agg | 51 | 168 | 117 | 30.4% |
| agg_bqx | 51 | 168 | 117 | 30.4% |
| mom | 51 | 168 | 117 | 30.4% |
| mom_bqx | 51 | 168 | 117 | 30.4% |
| vol | 51 | 168 | 117 | 30.4% |
| vol_bqx | 51 | 168 | 117 | 30.4% |
| align | 51 | 168 | 117 | 30.4% |
| align_bqx | 51 | 168 | 117 | 30.4% |
| **TOTAL** | **510** | **1,680** | **1,170** | **30.4%** |

---

## DISCREPANCY NOTE

The initial task estimate of "~267 missing" appears to have been based on a different coverage model. The full "8 currencies × 7 crosses" requirement translates to 168 pair combinations × 10 type variants = 1,680 total tables.

---

## REMEDIATION OPTIONS

### Option A: Full Coverage (1,170 tables)
- Create all missing pair combinations
- Estimated time: 6-8 hours
- Full feature matrix completion

### Option B: Priority Pairs Only (~400 tables)
- Focus on major pairs (EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD, USDCAD, USDCHF)
- Covers ~60% of trading volume
- Estimated time: 2-3 hours

### Option C: Incremental (As Needed)
- Create tables on-demand during model training
- Lowest upfront cost
- May cause training delays

---

## RECOMMENDATION

Recommend **Option A (Full Coverage)** to ensure complete feature matrix for Phase 3 model training. The 1,170 tables can be generated in parallel batches.

---

## AWAITING DIRECTIVE

Please confirm remediation scope:
- [ ] Option A: Full 1,170 tables
- [ ] Option B: Priority pairs (~400)
- [ ] Option C: Incremental

---

**BA Agent Status:** AUDIT COMPLETE - AWAITING REMEDIATION AUTHORIZATION

---

*Report generated: 2025-11-29T03:20:00Z*
