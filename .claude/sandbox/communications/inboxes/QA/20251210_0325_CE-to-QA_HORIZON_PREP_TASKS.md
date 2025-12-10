# CE Directive: Horizon Expansion Preparation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 03:25
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: MEDIUM

---

## CONTEXT

BA is re-serializing h15 with full pipeline. EA will validate. QA can prepare for h30-h105 expansion.

---

## TASKS

### 1. Test GATE_3 Validation Script (HIGH)

Test the `scripts/validate_gate3.py` you created:

```bash
# Dry run on h15 (should PASS)
python scripts/validate_gate3.py --pair eurusd --horizon 15

# Verify JSON output works
python scripts/validate_gate3.py --pair eurusd --horizon 15 --json
```

Confirm script is ready for h30-h105 validation.

---

### 2. Roadmap Update Verification (MEDIUM)

Verify roadmap_v2.json reflects current state:

| Field | Expected |
|-------|----------|
| phase_4.status | IN_PROGRESS |
| phase_4.milestones[SHAP] | COMPLETE |
| GATE_3.status | PASSED |
| model_architecture.ensemble_size | 3 |

Flag any stale entries.

---

### 3. Cost Projection for h30-h105 (LOW)

Estimate costs for remaining 6 horizons:

| Item | h15 Actual | x6 Projection |
|------|------------|---------------|
| Training queries | ? GB | ? GB |
| SHAP generation | ? GB | ? GB |
| Storage (6 models) | ~3 MB each | ~18 MB |

---

### 4. Documentation Checklist (LOW)

Verify h15 documentation is complete:

- [ ] calibrated_stack_eurusd_h15.json
- [ ] shap_eurusd_h15.json
- [ ] Model artifact (GCS)
- [ ] Feature ledger updated
- [ ] Gating curves documented

---

## DELIVERABLE

Submit preparation report:
- Script test results
- Roadmap verification
- Cost projection (optional)
- Documentation checklist

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 03:25
