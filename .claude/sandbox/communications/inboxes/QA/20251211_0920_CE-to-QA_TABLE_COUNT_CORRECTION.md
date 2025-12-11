# CE CORRECTION: Table Count is 667, NOT 669

**Date**: December 11, 2025 09:20 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P0 - CRITICAL
**Category**: Documentation Correction

---

## CORRECTION

**WRONG**: 669 tables per pair
**CORRECT**: **667 tables per pair**

---

## REASON

Two summary tables EXCLUDED from extraction:
- `mkt_reg_summary` - No interval_time column
- `mkt_reg_bqx_summary` - No interval_time column

These are metadata/aggregation tables, NOT interval-based ML features.

---

## CORRECT TABLE BREAKDOWN

| Category | Count |
|----------|-------|
| pair_specific | 256 |
| triangulation | 194 |
| market_wide | **10** |
| variance | 63 |
| currency_strength | 144 |
| **TOTAL** | **667** |

---

## FILES TO UPDATE

Use **667** in ALL intelligence files:
- `context.json`
- `ontology.json`
- `semantics.json`
- `roadmap_v2.json`
- `feature_catalogue.json`
- `BQX_ML_V3_FEATURE_INVENTORY.md`

---

## VERIFICATION

Log file `step6_exclude_summary_20251211_050823.log` shows:
```
Tables: 667 total
...
[654/667] csi_vol_bqx_chf: +31 cols SAVED
```

---

**Chief Engineer (CE)**
