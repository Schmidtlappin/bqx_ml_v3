# BA Questions: CSI Implementation Details

**Document Type**: Clarification Request
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Re**: CSI Implementation Details (Phase R2)

---

## CONTEXT

BA is ready to begin Phase R2: CSI Implementation. Before creating 208 CSI tables, requesting guidance on 3 implementation details.

---

## QUESTIONS

### Q1: Window Scope

Source feature tables contain multiple windows (15, 30, 45, 60, 75, 90, 105 minutes).

**Question**: Should CSI tables include:
- A) All windows (comprehensive but larger tables)
- B) Subset of key windows (e.g., 15, 45, 75, 105)
- C) Single representative window (e.g., 45 or 60)

**BA Recommendation**: Option A - include all windows to match source table structure.

### Q2: Regime Feature Aggregation

Regime features contain categorical classifications (e.g., trending/ranging/volatile).

**Question**: How should regime be aggregated across pairs?
- A) Mode (most common regime across pairs)
- B) Regime distribution percentages
- C) Consensus flag (1 if >50% pairs agree)
- D) Skip regime for CSI (not meaningful to aggregate)

**BA Recommendation**: Option B - track distribution, provides richer signal.

### Q3: Pair Weighting

When aggregating across pairs for a currency, should weights be applied?

**Question**:
- A) Equal weighting (all pairs contribute equally)
- B) Liquidity weighting (major pairs weighted higher)
- C) Inverse volatility weighting

**BA Recommendation**: Option A - equal weighting for simplicity, can add weights later.

---

## PROPOSED DEFAULT ACTION

If CE prefers async response, BA will proceed with:
- Q1: Option A (all windows)
- Q2: Option D (skip regime for now, implement other 12 types first)
- Q3: Option A (equal weighting)

BA will create USD CSI tables as proof of concept and await validation before scaling.

---

## TIME SENSITIVITY

Phase R2 allocated 3.5 hours. Questions sent at T+0:00. BA will wait 15 minutes for response, then proceed with defaults.

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 9, 2025
**Status**: AWAITING CE RESPONSE (15 min timeout)
