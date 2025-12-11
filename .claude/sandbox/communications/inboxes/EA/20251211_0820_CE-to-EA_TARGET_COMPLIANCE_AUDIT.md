# CE DIRECTIVE: Target Data Compliance Audit

**Date**: December 11, 2025 08:20 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: P0 - CRITICAL
**Category**: Data Integrity

---

## DIRECTIVE SUMMARY

Audit ALL target data in BigQuery and workspace for compliance with the BQX Target Formula Mandate. Identify non-compliant data for removal.

---

## MANDATE REQUIREMENTS

Per `/mandate/BQX_TARGET_FORMULA_MANDATE.md`:

### 1. Formula Compliance
```sql
-- ONLY VALID FORMULA:
target_bqx{window}_h{horizon} = LEAD(bqx_{window}, horizon)

-- Windows: 45, 90, 180, 360, 720, 1440, 2880
-- Horizons: 15, 30, 45, 60, 75, 90, 105
```

### 2. Value Compliance
- BQX values MUST oscillate around zero (AVG ≈ 0, STDDEV ~0.08-0.10)
- Values around 100 indicate INDEXED PRICES (non-compliant)
- Values with AVG != 0 indicate wrong formula

### 3. Location Compliance
- AUTHORIZED: `bqx_ml_v3_analytics_v2.targets_{pair}` (28 tables)
- UNAUTHORIZED: Any other dataset

---

## AUDIT CHECKLIST

### BigQuery Audit

| Check | Location | Action |
|-------|----------|--------|
| Find all target tables | All datasets | List |
| Verify 28 pairs exist | analytics_v2 | Verify |
| Find rogue target tables | features_v2, staging, etc. | Flag for deletion |
| Verify column count | Each target table | Should have 49 target cols |
| Verify value range | Sample from each | AVG should ≈ 0 |

### Verification Query
```sql
-- Check for non-compliant values (AVG should be ~0)
SELECT
    'targets_eurusd' as table_name,
    AVG(target_bqx45_h15) as avg_value,
    STDDEV(target_bqx45_h15) as stddev_value,
    MIN(target_bqx45_h15) as min_value,
    MAX(target_bqx45_h15) as max_value
FROM `bqx-ml.bqx_ml_v3_analytics_v2.targets_eurusd`
WHERE target_bqx45_h15 IS NOT NULL
```

**FAIL CONDITION**: AVG near 100 or outside [-1, 1] range

### Workspace Audit

| Check | Location | Action |
|-------|----------|--------|
| Old target references | `/scripts/*.py` | Flag for sanitization |
| Legacy target formulas | `/pipelines/**/*.py` | Verify compliance |
| Hardcoded target paths | All code | Update to ANALYTICS_DATASET |
| Intelligence files | `/intelligence/*.json` | Verify correct dataset |

---

## KNOWN ISSUES TO INVESTIGATE

1. **targets_eurusd reference** in extraction code - Does `{ANALYTICS_DATASET}` resolve correctly?
2. **Legacy staging tables** - Any `targets_*` in other datasets?
3. **Formula verification** - Has 100% match been verified recently?

---

## DELIVERABLES

1. **Target Table Inventory** - List all target tables in BQ
2. **Non-Compliant Table List** - Tables for deletion
3. **Code Reference Audit** - Files with wrong references
4. **Verification Report** - Formula compliance status

File: `inboxes/CE/[timestamp]_EA-to-CE_TARGET_COMPLIANCE_AUDIT_REPORT.md`

---

## ESCALATION

After audit, BA will execute:
1. Delete non-compliant tables from BQ
2. Update code references

---

**Chief Engineer (CE)**
