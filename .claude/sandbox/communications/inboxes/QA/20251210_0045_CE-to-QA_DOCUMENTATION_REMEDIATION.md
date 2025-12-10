# CE Directive: Documentation Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 00:45
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Action Required**: Execute remediation

---

## CONTEXT

EA has completed a comprehensive issues/gaps audit (report in EA outbox). Several documentation inconsistencies have been identified that require QA remediation.

---

## REMEDIATION TASKS

### R1: Risk Register Update (roadmap_v2.json)
**Location**: `risk_register` section
**Action**: Update status for resolved risks

| Risk ID | Current | New Status | Reason |
|---------|---------|------------|--------|
| RISK-001 | OPEN | RESOLVED | ElasticNet removed via EA-001 |
| RISK-002 | MITIGATING | RESOLVED | All 219 gap tables complete |
| RISK-005 | PLANNED | RESOLVED | 91.66% achieved at τ=0.85 |

### R2: BA Current Phase Update (roadmap_v2.json)
**Location**: `agent_hierarchy.agents.BA.current_phase`
**Current Value**: "Phase 1.5 - Gap Remediation"
**New Value**: "Phase 2.5 - Feature Ledger Generation"

### R3: Model Architecture Update (roadmap_v2.json)
**Location**: `model_architecture.ensemble_members`
**Action**: Remove ElasticNet, update count to 3

Current (incorrect):
```json
"ensemble_members": ["XGBoost", "LightGBM", "CatBoost", "ElasticNet"]
```

New (correct):
```json
"ensemble_members": ["XGBoost", "LightGBM", "CatBoost"]
```

Also update any references to "4 ensemble members" → "3 ensemble members"

### R4: Storage Totals (ontology.json) - LOW PRIORITY
**Location**: Storage section
**Action**: Update to reflect current 1,575.84 GB total
**Note**: This is LOW priority - complete after R1-R3

---

## VALIDATION

After remediation:
1. Verify risk_register shows 3 risks as RESOLVED
2. Verify BA current_phase shows Phase 2.5
3. Verify ensemble_members has exactly 3 entries
4. Run grep for "4 ensemble" or "ElasticNet" - should return no active references

---

## RESPONSE REQUIRED

Report completion with:
- List of files modified
- Validation results
- Any additional inconsistencies found

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 00:45
