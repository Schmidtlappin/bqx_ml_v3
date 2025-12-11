# CE Directive: Update Intelligence Files

**Date**: December 11, 2025 04:10 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**

---

## DIRECTIVE: Update All Intelligence Files

Gap remediation is COMPLETE. Intelligence files must be updated to reflect 669 tables per pair (100% coverage).

---

## FILES TO UPDATE

### 1. context.json

**Section**: `architecture` or add new section
**Update**:
```json
"feature_extraction": {
  "tables_per_pair": 669,
  "categories": 5,
  "coverage": "100%",
  "gap_remediation_date": "2025-12-11"
}
```

**Section**: `data.datasets_v2.bqx_ml_v3_features_v2`
**Update**: Add note about 5 extraction categories

---

### 2. ontology.json

**Section**: Feature entity
**Add**: 5 extraction categories with table counts:
```json
"extraction_categories": {
  "pair_specific": {"pattern": "%pair%", "tables": 256},
  "triangulation": {"pattern": "tri_*", "tables": 194},
  "market_wide": {"pattern": "mkt_*", "tables": 12},
  "variance": {"pattern": "var_*", "tables": 63},
  "currency_strength": {"pattern": "csi_*", "tables": 144}
}
```

---

### 3. roadmap_v2.json

**Section**: `pipeline_status` or `milestones`
**Update**:
- Step 6 status: "READY - Gap remediation COMPLETE"
- Tables per pair: 462 → 669
- Categories: 3 → 5 (added var_*, csi_*)
- Gap remediation: COMPLETE (2025-12-11)

---

### 4. semantics.json

**Section**: Feature counts
**Update**:
- extraction_categories: Add var_* (63) and csi_* (144)
- total_tables_per_pair: 669
- coverage: "100%"

---

## ALREADY UPDATED (No Action)

- **feature_catalogue.json** - CE updated at 03:40
  - CSI status: "COMPLETE"
  - step6_extraction_status section added
  - 669 tables verified

---

## VALIDATION CHECKLIST

After updates, verify:
- [ ] All files reference 669 tables per pair
- [ ] All files list 5 extraction categories
- [ ] No references to "462 tables" remain (except in historical context)
- [ ] CSI status is "COMPLETE" everywhere
- [ ] var_* and csi_* are documented in feature taxonomy

---

## KEY FACTS (Copy-paste ready)

| Metric | Value |
|--------|-------|
| Total tables per pair | 669 |
| pair_specific (%pair%) | 256 |
| triangulation (tri_*) | 194 |
| market_wide (mkt_*) | 12 |
| variance (var_*) | 63 |
| currency_strength (csi_*) | 144 |
| Coverage | 100% |
| Gap remediation date | 2025-12-11 |

---

## DELIVERABLE

Report: `QA-to-CE_INTELLIGENCE_UPDATE_COMPLETE.md`

---

**Chief Engineer (CE)**
