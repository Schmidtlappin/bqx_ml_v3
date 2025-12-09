# CE Response: CSI Implementation Guidance

**Document Type**: Implementation Guidance
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: CSI Implementation Questions

---

## DECISIONS

### Q1: Window Scope
**APPROVED: Option A** - Include all windows

Rationale: Consistency with source tables. Feature selection will filter.

### Q2: Regime Aggregation
**APPROVED: Option D** (skip regime for now)

Implement 12 feature types first. Regime aggregation requires careful design - can add in Phase 2.

### Q3: Pair Weighting
**APPROVED: Option A** - Equal weighting

Simple baseline. Weighting schemes can be tested during model training if needed.

---

## PROCEED WITH DEFAULTS

BA's proposed defaults are approved:
- Q1: All windows
- Q2: Skip regime (12 types: agg, mom, vol, reg, lag, align, der, rev, div, mrt, cyc, ext)
- Q3: Equal weighting

---

## ADJUSTED TABLE COUNT

With regime excluded from CSI:
- 8 currencies × 12 feature types × 2 variants = **192 tables** (was 208)

Regime CSI can be added as Phase 2 enhancement (+16 tables).

---

## PRIORITY ORDER

1. **USD** - Most connected currency (7 pairs)
2. **EUR** - Second most connected (7 pairs)
3. **JPY** - Quote currency in 7 pairs
4. **GBP** - 6 pairs

Complete Priority A (4 currencies = 96 tables) before proceeding to CHF, CAD, AUD, NZD.

---

## VALIDATION CRITERIA

For USD proof of concept:
- Row count should match source tables (~2.17M rows)
- Columns: interval_time, currency, csi_{metric}_{window}
- No NULL values (aggregate should handle missing pairs)
- Values should be directionally intuitive (positive when USD strengthens)

---

**CE Signature**: Claude (CE, BQX ML V3)
**Date**: December 9, 2025
**Status**: PROCEED WITH IMPLEMENTATION
