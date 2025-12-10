# CE Directive: Target Table Validation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 02:20
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: LOW
**Reference**: BA ISSUE-G3

---

## TASK: Validate Target Tables

BA identified gap G3: Target table availability for all 28 pairs unknown.

**Assignment**: QA to validate target tables exist for all 28 pairs.

**Query**:
```sql
SELECT table_name
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'targets_%'
ORDER BY table_name;
```

**Expected**: 28 tables (one per pair)

**Report**:
- List tables found
- Flag any missing pairs
- Priority: LOW (informational for Phase 4 expansion)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 02:20
