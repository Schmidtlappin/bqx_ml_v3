# BA Report: VAR/MKT Achievability Audit

**Document Type**: AUDIT REPORT
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Reference**: CE Directive 20251209_2130

---

## EXECUTIVE SUMMARY

Audit complete. VAR and MKT tables can be generated from existing sources with some limitations.

---

## VAR TABLE AUDIT

### Current State: 55 tables exist

| Feature Type | BQX | IDX | Other | Total | Notes |
|--------------|-----|-----|-------|-------|-------|
| var_agg | 7 | 7 | 0 | 14 | Missing USD |
| var_align | 7 | 7 | 0 | 14 | Missing USD |
| var_corr | 7 | 7 | 7 | 21 | Complete (8 currencies) |
| var_lag | 5 | 1 | 0 | 6 | Incomplete |
| **Total** | 26 | 22 | 7 | **55** | |

### Gap Analysis

**Missing USD for var_agg and var_align**:
- var_agg_idx_usd (can create from agg_* sources)
- var_agg_bqx_usd (can create from agg_bqx_* sources)
- var_align_idx_usd (can create from align_* sources)
- var_align_bqx_usd (can create from align_bqx_* sources)

**Missing var_lag tables**:
- var_lag_idx_cad, var_lag_idx_chf, var_lag_idx_eur, var_lag_idx_gbp, var_lag_idx_jpy (5 missing)
- var_lag_bqx_jpy, var_lag_bqx_nzd, var_lag_bqx_usd (3 missing)

**Additional VAR types not present** (CE mentioned these):
- var_vol (8 currencies × 2 variants = 16)
- var_mom (8 currencies × 2 variants = 16)
- var_reg (8 currencies × 2 variants = 16)

### VAR Achievability Assessment

| VAR Type | Can Generate | Source Tables | Estimated Tables |
|----------|--------------|---------------|------------------|
| var_agg_usd | YES | agg_* (84 tables) | +4 |
| var_align_usd | YES | align_* (84 tables) | +4 |
| var_lag (complete) | PARTIAL | lag_* (naming varies) | +8 (max) |
| var_vol | YES | vol_* (84 tables) | +16 |
| var_mom | YES | mom_* (84 tables) | +16 |
| var_reg | YES | reg_* (196 tables) | +16 |

**Total Achievable VAR**: ~55 existing + ~64 new = **~119 tables**

### BA Recommendation for VAR

1. **Quick Wins** (can do immediately):
   - var_agg_usd (2 variants) - 4 tables
   - var_align_usd (2 variants) - 4 tables
   - Total: 8 additional tables

2. **Medium Effort** (requires generation script):
   - var_vol for all 8 currencies - 16 tables
   - var_mom for all 8 currencies - 16 tables
   - var_reg for all 8 currencies - 16 tables
   - Total: 48 additional tables

3. **Complex** (naming pattern issues):
   - var_lag completion - 8 tables (naming varies)

---

## MKT TABLE AUDIT

### Current State: 4 tables exist

| Table | Status |
|-------|--------|
| mkt_corr | EXISTS |
| mkt_corr_bqx | EXISTS |
| mkt_reg_summary | EXISTS |
| mkt_reg_bqx_summary | EXISTS |

### Expected MKT Tables (per CE specification)

| MKT Type | IDX | BQX | Total | Source Available |
|----------|-----|-----|-------|------------------|
| mkt_vol | 1 | 1 | 2 | YES (vol_* 84 tables) |
| mkt_regime | 1 | 1 | 2 | YES (regime_* 112 tables) |
| mkt_dispersion | 1 | 1 | 2 | YES (can compute from pairs) |
| mkt_correlation | 1 | 1 | 2 | PARTIAL (mkt_corr exists, rename?) |
| mkt_session | 1 | 1 | 2 | UNCLEAR (need session data) |
| mkt_liquidity | 1 | 1 | 2 | UNCLEAR (need spread/volume) |
| mkt_sentiment | 1 | 1 | 2 | YES (can compute from directional bias) |

### MKT Achievability Assessment

| MKT Type | Can Generate | Complexity | Notes |
|----------|--------------|------------|-------|
| mkt_vol | YES | LOW | AVG(vol_*) across 28 pairs |
| mkt_regime | YES | MEDIUM | Mode/count of regime states |
| mkt_dispersion | YES | LOW | MAX - MIN of strength metrics |
| mkt_correlation | EXISTS? | LOW | mkt_corr already exists |
| mkt_session | UNCLEAR | HIGH | Need session mapping |
| mkt_liquidity | UNCLEAR | HIGH | Need liquidity source data |
| mkt_sentiment | YES | MEDIUM | Net directional bias |

**Total Achievable MKT**: 4 existing + ~8-10 new = **~12-14 tables**

### BA Recommendation for MKT

1. **Quick Wins** (CE recommended first):
   - mkt_vol, mkt_vol_bqx (2 tables) - AVG volatility across pairs
   - mkt_dispersion, mkt_dispersion_bqx (2 tables) - if not duplicate of mkt_corr

2. **Medium Effort**:
   - mkt_regime, mkt_regime_bqx (2 tables) - aggregate regime states
   - mkt_sentiment, mkt_sentiment_bqx (2 tables) - net directional bias

3. **Clarification Needed**:
   - mkt_correlation vs mkt_corr - are these the same?
   - mkt_session - what session data is available?
   - mkt_liquidity - what liquidity source exists?

---

## SUMMARY

| Category | Current | Achievable New | Total | Notes |
|----------|---------|----------------|-------|-------|
| CSI | 144 | 0 | 144 | COMPLETE |
| VAR | 55 | ~64 | ~119 | Depends on scope |
| MKT | 4 | ~8-10 | ~12-14 | Some unclear |

---

## QUESTIONS FOR CE

### Q1: VAR Scope
Should BA generate all VAR types (var_vol, var_mom, var_reg) or only complete existing types (var_agg_usd, var_align_usd)?

**Options**:
- A) Only complete existing (8 tables) - quick
- B) Add var_vol, var_mom, var_reg (48 tables) - comprehensive
- C) Full VAR universe (64+ tables)

### Q2: MKT Clarification
- Is mkt_correlation the same as mkt_corr (already exists)?
- Should we skip mkt_session and mkt_liquidity if source data is unclear?

### Q3: Priority
Which should BA prioritize?
- A) VAR first (higher volume)
- B) MKT first (CE recommended mkt_vol, mkt_corr)
- C) Parallel (both)

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 9, 2025
**Status**: AUDIT COMPLETE - AWAITING CE SCOPE DECISION

