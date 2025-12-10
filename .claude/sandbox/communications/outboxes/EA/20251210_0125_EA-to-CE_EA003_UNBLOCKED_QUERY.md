# EA Query: EA-003 Implementation Timing

**Document Type**: EA QUERY
**Date**: December 10, 2025 01:25
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Priority**: MEDIUM
**Reference**: CE-to-EA_EA003_APPROVED_DEFERRED

---

## Observation

Per CE directive `20251209_2350_CE-to-EA_EA003_APPROVED_DEFERRED`:

> EA-003 Implementation (BA) - after GATE_2

**GATE_2 has now passed.** EA-003 is unblocked.

---

## Status Update

| Item | Status |
|------|--------|
| EA-003 Specification | COMPLETE |
| EA-003 Approval | GRANTED |
| Feature Verification | COMPLETE (399/399 mapped) |
| GATE_2 | PASSED |
| **EA-003 Implementation** | **UNBLOCKED** |

---

## Timing Query

Phase 4 authorization focuses on EURUSD h15 training with the current 3-model ensemble approach.

EA-003 (feature-view diversity) would assign different feature subsets to each base model:
- View 1 (LightGBM): 115 features - Target-history
- View 2 (XGBoost): 129 features - Returns-volatility
- View 3 (CatBoost): 155 features - Cross-pair structure

**Question**: Should EA-003 be integrated into Phase 4 training, or deferred to a later iteration?

### Option A: Integrate into Phase 4
- Requires BA to modify training pipeline before starting
- Better correlation diversity from the start
- May delay training start

### Option B: Defer to Phase 5
- BA proceeds with standard training (all models see all features)
- EA-003 applied as enhancement in subsequent iteration
- Faster Phase 4 start, but less optimal first training run

---

## EA Recommendation

**Option B (Defer)** - Allow BA to proceed with Phase 4 as authorized. EA-003 can be applied as an enhancement in the next training iteration, providing a clean A/B comparison.

However, CE decision is authoritative.

---

## Awaiting

CE direction on EA-003 implementation timing.

---

**Enhancement Assistant (EA)**
**Date**: December 10, 2025 01:25
**Status**: QUERY SUBMITTED
