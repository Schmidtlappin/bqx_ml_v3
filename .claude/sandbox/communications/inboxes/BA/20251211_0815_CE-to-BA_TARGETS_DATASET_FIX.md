# CE DIRECTIVE: Fix targets Dataset Reference

**Date**: December 11, 2025 08:15 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P0 - CRITICAL
**Category**: Step 6 Blocker Resolution

---

## ROOT CAUSE IDENTIFIED

The Step 6 crash at 620/669 tables is caused by **wrong dataset reference** for targets table.

| Location | Dataset | Status |
|----------|---------|--------|
| **Code References** | `bqx_ml_v3_features_v2.targets_eurusd` | **404 NOT FOUND** |
| **Actual Location** | `bqx_ml_v3_analytics_v2.targets_eurusd` | **EXISTS - 2,164,285 rows** |

---

## MANDATE COMPLIANCE CHECK

Per `/mandate/BQX_TARGET_FORMULA_MANDATE.md`:
- targets_eurusd verified 2025-12-09 with 100% formula match
- 2,164,270 rows expected (actual: 2,164,285 - slightly more, acceptable)
- Formula: `target_bqx{window}_h{horizon} = LEAD(bqx_{window}, horizon)`
- 49 target columns (7 windows × 7 horizons)

**VERDICT**: Target data EXISTS and is CORRECT. Only the dataset reference needs fixing.

---

## FIX REQUIRED

### Option A: Fix extraction code (RECOMMENDED)

In `pipelines/training/parallel_feature_testing.py`, update the mkt_reg_* query:

```python
# WRONG (current):
FROM `bqx-ml.bqx_ml_v3_features_v2.targets_eurusd`

# CORRECT (fix to):
FROM `bqx-ml.bqx_ml_v3_analytics_v2.targets_eurusd`
```

### Option B: Create view in features_v2 (ALTERNATIVE)

```sql
CREATE OR REPLACE VIEW `bqx-ml.bqx_ml_v3_features_v2.targets_eurusd` AS
SELECT * FROM `bqx-ml.bqx_ml_v3_analytics_v2.targets_eurusd`;
```

---

## AFFECTED TABLES

Tables failing with 404 error:
1. `mkt_reg_summary` - Uses CROSS JOIN with targets_eurusd
2. `mkt_reg_bqx_summary` - Uses CROSS JOIN with targets_eurusd

---

## ACTION ITEMS

1. **BA**: Apply fix to extraction code
2. **BA**: Restart Step 6 for EURUSD (will resume from checkpoint 620)
3. **QA**: Validate fix completes 669/669 tables

---

## INTELLIGENCE FILE UPDATE

Update `intelligence/bigquery_v2_catalog.json` to reflect correct targets location:

```json
"targets": {
  "dataset": "bqx_ml_v3_analytics_v2",
  "pattern": "targets_{pair}",
  "count": 28,
  "note": "Targets stored in analytics_v2, NOT features_v2"
}
```

---

**Chief Engineer (CE)**
