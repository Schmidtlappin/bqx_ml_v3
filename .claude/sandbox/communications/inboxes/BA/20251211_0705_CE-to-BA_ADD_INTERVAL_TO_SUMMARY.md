# CE Directive: Add interval_time to Summary Tables

**Date**: December 11, 2025 07:00 UTC (Updated 07:05)
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P0 - CRITICAL
**Type**: Bug Fix

---

## USER MANDATE

**Do NOT skip summary tables.** Add `interval_time` by CROSS JOIN to preserve 100% feature coverage.

---

## ISSUE

Step 6 crashes on tables without `interval_time` column:
- `mkt_reg_summary` - 277 columns, NO interval_time
- `mkt_reg_bqx_summary` - NO interval_time

These tables have `first_interval` and `last_interval` but no per-row `interval_time`.

---

## FIX REQUIRED (USER MANDATE)

Modify the query for `*_summary` tables to CROSS JOIN with interval times.

### Query Modification

For tables WITHOUT `interval_time`, use this pattern:

```sql
-- For mkt_reg_summary and mkt_reg_bqx_summary
SELECT
    t.interval_time,
    s.*  -- All summary columns
FROM (
    SELECT DISTINCT interval_time
    FROM `bqx-ml.bqx_ml_v3_features_v2.targets_eurusd`
    WHERE interval_time BETWEEN '2020-01-01' AND '2024-12-31'
) t
CROSS JOIN `bqx-ml.bqx_ml_v3_features_v2.mkt_reg_summary` s
WHERE s.period = 'all_time'
```

### Implementation in parallel_feature_testing.py

```python
def query_table(table_name, pair, start_date, end_date):
    # Check if table has interval_time
    if table_name.endswith('_summary'):
        # Summary tables need CROSS JOIN with intervals
        query = f"""
        SELECT
            t.interval_time,
            s.* EXCEPT(period, first_interval, last_interval, interval_count)
        FROM (
            SELECT DISTINCT interval_time
            FROM `bqx-ml.bqx_ml_v3_features_v2.targets_{pair}`
            WHERE interval_time BETWEEN '{start_date}' AND '{end_date}'
        ) t
        CROSS JOIN `bqx-ml.bqx_ml_v3_features_v2.{table_name}` s
        WHERE s.period = 'all_time'
        """
    else:
        # Normal tables with interval_time
        query = f"""
        SELECT * FROM `bqx-ml.bqx_ml_v3_features_v2.{table_name}`
        WHERE interval_time BETWEEN '{start_date}' AND '{end_date}'
        """
    return query
```

---

## AFFECTED TABLES

| Table | Fix |
|-------|-----|
| `mkt_reg_summary` | CROSS JOIN with intervals |
| `mkt_reg_bqx_summary` | CROSS JOIN with intervals |

---

## RESULT

- Table count remains **669** (100% coverage)
- Summary features replicated for each interval
- All features joinable on `interval_time`

---

## AFTER FIX

1. Apply CROSS JOIN fix to `parallel_feature_testing.py`
2. Test on one summary table
3. Restart Step 6 (checkpoints will resume at 620)
4. Report completion to CE

---

## URGENCY

EURUSD is at 620/669 (93%). Fix will allow completion of remaining ~49 tables.

---

**Chief Engineer (CE)**
