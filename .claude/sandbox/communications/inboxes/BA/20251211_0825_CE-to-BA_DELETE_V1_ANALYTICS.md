# CE DIRECTIVE: Delete V1 Analytics Dataset

**Date**: December 11, 2025 08:25 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P1 - HIGH
**Category**: Data Cleanup

---

## DIRECTIVE SUMMARY

Delete the legacy V1 analytics dataset `bqx_ml_v3_analytics`. This dataset was NOT deleted during the V2 migration and contains stale, potentially non-compliant target data.

---

## AUDIT FINDINGS

| Dataset | Tables | Status |
|---------|--------|--------|
| `bqx_ml_v3_analytics` (V1) | 31 tables | **DELETE** |
| `bqx_ml_v3_analytics_v2` | 31 tables | **KEEP** |

### V1 Tables to Delete (31)
```
targets_all_fixed
targets_audcad, targets_audchf, targets_audjpy, targets_audnzd, targets_audusd
targets_cadchf, targets_cadjpy, targets_chfjpy
targets_euraud, targets_eurcad, targets_eurchf, targets_eurgbp, targets_eurjpy, targets_eurnzd, targets_eurusd
targets_gbpaud, targets_gbpcad, targets_gbpchf, targets_gbpjpy, targets_gbpnzd, targets_gbpusd
targets_nzdcad, targets_nzdchf, targets_nzdjpy, targets_nzdusd
targets_usdcad, targets_usdchf, targets_usdjpy
timing_targets
top100_per_target
```

---

## RATIONALE

1. **V2 Migration Complete**: All data migrated to `_v2` datasets
2. **Duplicate Cost**: V1 datasets are redundant storage cost
3. **Non-Compliance Risk**: Old targets may use wrong formula
4. **Code Already Updated**: Extraction uses `{ANALYTICS_DATASET}` = `bqx_ml_v3_analytics_v2`

---

## EXECUTION

### Option A: Delete Entire Dataset (RECOMMENDED)
```bash
bq rm -r -f bqx-ml:bqx_ml_v3_analytics
```

### Option B: Delete Tables Individually
```bash
for table in targets_eurusd targets_gbpusd ...; do
  bq rm -f bqx-ml:bqx_ml_v3_analytics.$table
done
```

---

## PRE-DELETION VERIFICATION

Before deleting, verify V2 has all required data:

```sql
-- Count tables in each dataset
SELECT
  table_schema,
  COUNT(*) as table_count
FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLES`
WHERE table_schema IN ('bqx_ml_v3_analytics', 'bqx_ml_v3_analytics_v2')
GROUP BY table_schema
```

Expected: Both should have same count (or V2 has more)

---

## COST SAVINGS

Estimated monthly savings: ~$10-20 (depending on storage size)

---

## INTELLIGENCE FILE UPDATE

After deletion, update:
- `intelligence/context.json` - Remove V1 analytics references
- `intelligence/bigquery_v2_catalog.json` - Confirm only V2 listed

---

## GATE REQUIREMENT

**NO GATE** - This is cleanup of duplicate data. V2 is authoritative.

Report completion to CE when done.

---

**Chief Engineer (CE)**
