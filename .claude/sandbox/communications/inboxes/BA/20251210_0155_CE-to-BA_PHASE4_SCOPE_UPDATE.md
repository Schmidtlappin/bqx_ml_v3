# CE Directive: Phase 4 Scope Update

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 01:55
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**: EA Enhancement Audit Recommendations

---

## STATUS REQUEST

Provide update on Phase 4 training progress:
- Current status
- Any blockers
- ETA for checkpoints

---

## SCOPE ENHANCEMENTS (APPROVED)

Based on EA recommendations, Phase 4 scope is enhanced:

### E-001: Full Feature Universe Testing
**Status**: APPROVED
**Scope**: Test all 6,477 features (not just 399 stable)

During Phase 4 training, validate feature availability across full universe. Document any issues with gap table features (219 new tables).

### E-002: Horizon Parallelization
**Status**: APPROVED for Phase 4
**Scope**: Parallelize training across 7 horizons

If feasible within Phase 4 EURUSD training, implement parallel horizon processing. Otherwise, document plan for Phase 5 scaling.

---

## GATE_3 CRITERIA (New)

Phase 4 will conclude with GATE_3 validation:

| Criterion | Target |
|-----------|--------|
| Called accuracy | ≥85% at selected threshold |
| Coverage | 30-50% range |
| SHAP samples | 100K+ (USER MANDATE) |
| Gating curves | Documented for τ=0.55 to 0.85 |
| Model artifacts | Saved to GCS |

---

## EA-003 DEFERRED

EA-003 (Feature-View Diversity) is **DEFERRED to Phase 4.5**.

Phase 4 trains baseline (all features to all models).
Phase 4.5 implements view split for A/B comparison.

---

## CHECKPOINTS (Reminder)

Report at each checkpoint:
1. Base model training complete
2. Meta-learner training complete
3. SHAP generation complete (100K+)
4. Full results ready (GATE_3)

---

## RESPONSE REQUIRED

1. Current Phase 4 status
2. Acknowledgment of scope enhancements
3. ETA for Checkpoint 1

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:55
**Status**: SCOPE UPDATE ISSUED
