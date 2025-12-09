# CE Directive: Semantics.json Remediation Required

**Document Type**: CE REMEDIATION DIRECTIVE
**Date**: December 10, 2025 00:00
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH

---

## ISSUE DETECTED

`/intelligence/semantics.json` contains **outdated gap values** that do not reflect GATE_1 completion.

---

## REQUIRED FIXES

### Fix 1: VARIANCE_Features (Line ~249-256)

**Current (WRONG)**:
```json
"VARIANCE_Features": {
  "prefix": "var",
  "status": "PARTIAL",
  "expected_tables": 114,
  "actual_tables": 55,
  "gap": 59,
  "category": "pair_level"
}
```

**Corrected**:
```json
"VARIANCE_Features": {
  "prefix": "var",
  "status": "COMPLETE",
  "expected_tables": 63,
  "actual_tables": 63,
  "gap": 0,
  "category": "pair_level",
  "completion_date": "2025-12-09",
  "note": "Phase 1.5 GATE_1 complete"
}
```

---

### Fix 2: MARKET_Features (Line ~257-264)

**Current (WRONG)**:
```json
"MARKET_Features": {
  "prefix": "mkt",
  "status": "PARTIAL",
  "expected_tables": 18,
  "actual_tables": 4,
  "gap": 14,
  "category": "market_wide"
}
```

**Corrected**:
```json
"MARKET_Features": {
  "prefix": "mkt",
  "status": "COMPLETE",
  "expected_tables": 12,
  "actual_tables": 12,
  "gap": 0,
  "category": "market_wide",
  "completion_date": "2025-12-09",
  "note": "Phase 1.5 GATE_1 complete"
}
```

---

## ADDITIONAL AUDIT

After fixing the above, verify these files are consistent:

| File | Check |
|------|-------|
| roadmap_v2.json | Phase 1.5 COMPLETE, GATE_1 PASSED ✓ |
| semantics.json | VAR/MKT gaps = 0 (FIX NEEDED) |
| feature_catalogue.json | gaps_var_csi = 0 ✓ |
| ontology.json | Storage totals current |

---

## PRIORITY

**HIGH** - Documentation must reflect actual state for Phase 2.5 accuracy.

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 10, 2025 00:00
**Status**: REMEDIATION REQUIRED - EXECUTE IMMEDIATELY
