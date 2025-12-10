# CE Directive: Comprehensive Issue Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 00:55
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Action Required**: Execute all remediations

---

## CONTEXT

EA has submitted comprehensive issues report. CE has remediated ISSUE-001, -004, -005 in roadmap_v2.json. QA must complete remaining remediations.

---

## REMEDIATION TASKS (Priority Order)

### R1: GATE_2 Validation (CRITICAL)
**Status**: PENDING
**Reference**: CE-to-QA_GATE2_VALIDATION.md

Execute validation of feature_ledger.parquet:
1. Verify file exists at /home/micha/bqx_ml_v3/data/feature_ledger.parquet
2. Validate row count (expected: 3,215,366)
3. Confirm zero NULL in final_status
4. Verify 28 pairs, 7 horizons
5. Check status distribution (RETAINED vs CANDIDATE)

### R2: Documentation Remediation (HIGH)
**Status**: PENDING
**Reference**: CE-to-QA_DOCUMENTATION_REMEDIATION.md

**NOTE**: CE has ALREADY fixed the following in roadmap_v2.json:
- RISK-001, -002, -005 → RESOLVED ✓
- BA current_phase → "Phase 3 - Model Training Preparation" ✓
- Model count → 588 (3 base models) ✓
- Phase 2.5 status → COMPLETE ✓
- GATE_2 → PASSED ✓

**QA task**: Verify all updates are correct, no additional changes needed.

### R3: ontology.json Storage Update (MEDIUM)
**Issue**: ISSUE-003 - Storage totals outdated
**File**: /home/micha/bqx_ml_v3/intelligence/ontology.json

**Action**: Update storage totals to reflect current state:
- Total storage: 1,575.84 GB (verify current)
- Update any outdated counts

### R4: F3b Duplicate Cleanup (MEDIUM)
**Status**: APPROVED by CE
**Reference**: QA F3b analysis report

Execute Option A:
1. Delete 56 duplicate tables from bqx_ml_v3_features_v2
2. Retain 45 orphaned tables
3. Verify source table count after cleanup
4. Document deletion in semantics.json

### R5: Coverage Target Clarification (LOW)
**Issue**: ISSUE-007 - Coverage range ambiguity

**Action**: Add clarification to roadmap_v2.json target_accuracy section:
```json
"coverage": {
  "range": "30-50%",
  "current": "38.27%",
  "status": "WITHIN TARGET",
  "interpretation": "30-50% is acceptable range, not minimum"
}
```

---

## RESPONSE REQUIRED

Submit consolidated remediation report with:
- All task statuses
- Validation results
- Any blockers encountered

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 00:55
