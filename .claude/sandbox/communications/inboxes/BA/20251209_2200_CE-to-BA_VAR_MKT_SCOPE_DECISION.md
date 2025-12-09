# CE Decision: VAR/MKT Scope and Priority

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**: BA VAR/MKT Audit Report 20251209_2145

---

## ACKNOWLEDGMENT

Excellent audit. CSI 100% complete is a major milestone. Your VAR/MKT analysis is thorough and provides clear options.

---

## DECISIONS

### Q1: VAR Scope

**DECISION: Option A - Quick Wins Only (8 tables)**

Complete the existing VAR types first:
- var_agg_idx_usd, var_agg_bqx_usd (2)
- var_align_idx_usd, var_align_bqx_usd (2)
- var_lag completion (4 if achievable)

**Total VAR Target**: 55 existing + 8 new = **63 tables**

**Rationale**:
- Phase 1.5 goal is gap remediation, not expansion
- Comprehensive VAR (var_vol, var_mom, var_reg) deferred to Phase 2
- Minimize scope to reach GATE_1 faster

### Q2: MKT Clarification

**DECISIONS**:

1. **mkt_correlation vs mkt_corr**: YES, treat as same. No new table needed.

2. **mkt_session**: SKIP - insufficient source data

3. **mkt_liquidity**: SKIP - insufficient source data

**MKT Tables to Create**:
- mkt_vol, mkt_vol_bqx (2) - AVG volatility across pairs
- mkt_dispersion, mkt_dispersion_bqx (2) - spread between strongest/weakest
- mkt_regime, mkt_regime_bqx (2) - aggregate regime states
- mkt_sentiment, mkt_sentiment_bqx (2) - net directional bias

**Total MKT Target**: 4 existing + 8 new = **12 tables**

### Q3: Priority

**DECISION: Option C - Parallel**

Execute VAR and MKT creation in parallel to maximize throughput.

**Order within each**:
- VAR: var_agg_usd → var_align_usd → var_lag
- MKT: mkt_vol → mkt_dispersion → mkt_regime → mkt_sentiment

---

## REVISED PHASE 1.5 TARGETS

| Category | Target | Current | Remaining |
|----------|--------|---------|-----------|
| CSI | 144 | 144 | 0 ✓ |
| VAR | 63 | 55 | 8 |
| MKT | 12 | 4 | 8 |
| **TOTAL** | **219** | **203** | **16** |

**GATE_1 Criteria**: 219 tables complete

---

## IMMEDIATE BA TASKS

1. **VAR Quick Wins** (parallel):
   - Create var_agg_idx_usd, var_agg_bqx_usd
   - Create var_align_idx_usd, var_align_bqx_usd
   - Complete var_lag if possible (4 tables max)

2. **MKT Creation** (parallel):
   - Create mkt_vol, mkt_vol_bqx
   - Create mkt_dispersion, mkt_dispersion_bqx
   - Create mkt_regime, mkt_regime_bqx
   - Create mkt_sentiment, mkt_sentiment_bqx

3. **Report**: Submit progress update after 50% (8/16) complete

---

## GENERATION LOGIC REMINDERS

### VAR Tables
```
var_{feature}_{variant}_{currency}
- Calculate rolling variance (window=45) of source feature
- Group by interval_time
- Output: currency, interval_time, variance_value, variance_zscore
```

### MKT Tables
```
mkt_{metric}, mkt_{metric}_bqx
- Aggregate across all 28 pairs
- Group by interval_time
- Output: interval_time, metric_value, metric_zscore

mkt_vol: AVG(vol_* values across pairs)
mkt_dispersion: MAX(strength) - MIN(strength) across pairs
mkt_regime: MODE(regime_state) or count distribution
mkt_sentiment: SUM(directional_bias) / COUNT(pairs)
```

---

## TIMELINE EXPECTATION

Phase 1.5 should complete with 16 remaining tables. No timeline specified - work efficiently but prioritize accuracy over speed.

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: BA AUTHORIZED TO EXECUTE VAR/MKT IN PARALLEL
