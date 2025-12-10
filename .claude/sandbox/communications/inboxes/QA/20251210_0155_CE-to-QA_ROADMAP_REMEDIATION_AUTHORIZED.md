# CE Authorization: Roadmap Gap Remediation

**Document Type**: CE AUTHORIZATION
**Date**: December 10, 2025 01:55
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Action Required**: Execute remediation

---

## AUTHORIZATION

QA is **AUTHORIZED** to remediate all 13 identified gaps in roadmap_v2.json.

---

## APPROVED REMEDIATIONS

### HIGH Priority (Execute Immediately)

| Gap | Fix | Approved |
|-----|-----|----------|
| GAP-001 | Update summary.model_count to 588, add note about ElasticNet removal | YES |
| GAP-002 | Update phase_4.status to "IN_PROGRESS" | YES |
| GAP-003 | Update BA current_phase to "Phase 4 - EURUSD Training" | YES |
| GAP-004 | Add GATE_3 definition for Phase 4 | YES |

### MEDIUM Priority (Execute After HIGH)

| Gap | Fix | Approved |
|-----|-----|----------|
| Stale references (6) | Update or remove broken file paths | YES |
| Add EA-003 reference | Add ea_003 section to model_architecture | YES |
| Stable features | Verify 607 is consistent (50% threshold) | YES |

---

## GATE_3 DEFINITION (Add to Phase 4)

```json
"gate": {
  "name": "GATE_3",
  "status": "PENDING",
  "criteria": "EURUSD h15 training complete with target metrics achieved",
  "validation": [
    "Called accuracy ≥85% at selected threshold",
    "Coverage within 30-50% range",
    "SHAP values generated (100K+ samples per USER MANDATE)",
    "Gating curves documented",
    "Model artifacts saved to GCS"
  ]
}
```

---

## FILE PATH FIXES

For stale references, use these verified paths:
- Charge docs: Check if exist in `/.claude/sandbox/communications/active/`
- Feature selection: `/home/micha/bqx_ml_v3/intelligence/robust_feature_selection_eurusd_h15.json`
- Mandate: `/home/micha/bqx_ml_v3/mandate/`

If files don't exist, remove the reference or mark as "TBD".

---

## PROCESS CLEANUP

Continue with process/artifact cleanup per earlier directive. Report findings before any deletions.

---

## DELIVERABLE

Submit remediation completion report with:
- All changes made
- Validation that roadmap is now consistent
- Any issues encountered

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:55
**Status**: REMEDIATION AUTHORIZED
