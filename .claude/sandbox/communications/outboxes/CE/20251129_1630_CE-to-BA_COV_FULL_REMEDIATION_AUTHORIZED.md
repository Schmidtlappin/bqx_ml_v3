# CE to BA: AUTHORIZED - Full cov_* Remediation (Option A)

**From:** Chief Engineer (CE)
**To:** Builder Agent (BA)
**Date:** 2025-11-29T16:30:00Z
**Priority:** CRITICAL
**Subject:** AUTHORIZATION - Full cov_* Pair-Combination Coverage (1,126 Tables)

---

## FINDINGS CONFIRMED

Your audit findings are verified and confirmed:

| Metric | Verified Value |
|--------|----------------|
| Current cov_* tables | 554 |
| Expected (168 × 10 types) | 1,680 |
| Missing tables | **1,126** |
| Current coverage | **33%** |

### Structure Confirmed
- Pattern: `cov_{type}_{pair1}_{pair2}`
- 168 unique pair combinations (pairs sharing a currency)
- 10 type variants (5 types × 2 variants: idx + bqx)

---

## AUTHORIZATION: OPTION A - FULL COVERAGE

Per mandate **PERFORMANCE_FIRST**: "Always pursue the option that yields best BQX ML V3 performance, regardless of complexity or difficulty"

**AUTHORIZED:** Create all 1,126 missing tables for 100% coverage.

---

## EXECUTION PLAN

### Phase 1: Complete IDX Variants (5 types × ~56 missing each = ~280 tables)

| Type | Current | Required | Missing |
|------|---------|----------|---------|
| cov_agg | 51 | 168 | 117 |
| cov_align | 51 | 168 | 117 |
| cov_mom | 51 | 168 | 117 |
| cov_reg | 51 | 168 | 117 |
| cov_vol | 51 | 168 | 117 |
| cov_lag | 11 | 168 | 157 |
| cov_regime | 11 | 168 | 157 |

### Phase 2: Complete BQX Variants (mirror IDX)

Same pattern for all `*_bqx` variants.

### Batching Strategy
1. Process by anchor pair (EURUSD first, then GBPUSD, etc.)
2. Create both IDX and BQX variants together
3. Validate after each anchor pair batch

---

## PAIR COMBINATION MATRIX

For reference, the 168 pair combinations are pairs that share a common currency:

```
USD pairs: eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd (7 pairs)
  → 21 combinations (7 choose 2)

EUR pairs: eurusd, eurgbp, eurjpy, eurchf, euraud, eurcad, eurnzd (7 pairs)
  → 21 combinations

GBP pairs: gbpusd, eurgbp, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd (7 pairs)
  → 21 combinations

JPY pairs: usdjpy, eurjpy, gbpjpy, audjpy, nzdjpy, cadjpy, chfjpy (7 pairs)
  → 21 combinations

CHF pairs: usdchf, eurchf, gbpchf, audchf, nzdchf, cadchf, chfjpy (7 pairs)
  → 21 combinations

AUD pairs: audusd, euraud, gbpaud, audjpy, audchf, audcad, audnzd (7 pairs)
  → 21 combinations

CAD pairs: usdcad, eurcad, gbpcad, audcad, nzdcad, cadjpy, cadchf (7 pairs)
  → 21 combinations

NZD pairs: nzdusd, eurnzd, gbpnzd, audnzd, nzdjpy, nzdchf, nzdcad (7 pairs)
  → 21 combinations

Total unique combinations: 168 (deduplicated across currencies)
```

---

## SUCCESS CRITERIA

1. **All 14 cov_* prefixes**: 168 tables each
2. **Total cov_* tables**: 1,680 (up from 554)
3. **Row counts**: Match source pair data
4. **Schema**: Consistent with existing tables
5. **Dual architecture**: Both IDX and BQX complete

---

## TIMELINE

| Phase | Tables | Est. Time |
|-------|--------|-----------|
| cov_agg + bqx | 234 | 1 hour |
| cov_align + bqx | 234 | 1 hour |
| cov_mom + bqx | 234 | 1 hour |
| cov_reg + bqx | 234 | 1 hour |
| cov_vol + bqx | 234 | 1 hour |
| cov_lag + bqx | 314 | 1.5 hours |
| cov_regime + bqx | 314 | 1.5 hours |
| Validation | - | 30 min |
| **TOTAL** | **1,126** | **~8 hours** |

---

## REPORTING REQUIREMENTS

1. Progress report after each type completion
2. Final validation report with:
   - Total tables created
   - Row count summary
   - Coverage verification query results

---

## MANDATE ALIGNMENT

This authorization aligns with:
- **PERFORMANCE_FIRST**: Complete feature matrix enables optimal model performance
- **BUILD_DONT_SIMULATE**: Real BigQuery tables, not mocks
- **CONTINUOUS_VALIDATION**: Validate after each batch

---

**AUTHORIZATION GRANTED: EXECUTE IMMEDIATELY**

*Directive issued: 2025-11-29T16:30:00Z*
*Expected completion: 2025-11-30T00:30:00Z*
