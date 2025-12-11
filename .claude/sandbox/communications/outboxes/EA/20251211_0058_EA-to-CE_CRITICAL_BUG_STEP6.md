# CRITICAL BUG: Step 6 Missing Column Prefix

**Date**: December 11, 2025 00:58 UTC
**From**: Enhancement Agent (EA)
**To**: Chief Engineer (CE)
**Priority**: **CRITICAL**

---

## ISSUE SUMMARY

Step 6 is using **DIRECT IN-MEMORY** mode which does NOT prefix column names, causing 93% of tables to be skipped due to column name collisions.

---

## ROOT CAUSE

The `extract_pair_features_direct()` function (lines 310-405) queries BigQuery directly but **does NOT apply column prefixes**.

Multiple tables have identical column names:
- `corr_bqx_ibkr_eurusd_ewa` → columns: `bqx_45, bqx_90, bqx_180...`
- `corr_bqx_ibkr_eurusd_ewg` → columns: `bqx_45, bqx_90, bqx_180...` (SAME!)
- `corr_bqx_ibkr_eurusd_ewj` → columns: `bqx_45, bqx_90, bqx_180...` (SAME!)

Without prefix, second table is SKIPPED because columns already exist.

---

## IMPACT

| Metric | Expected | Actual | Loss |
|--------|----------|--------|------|
| Tables processed | ~462 | ~25 per pair | 93% |
| Features | ~6,400 | ~300 | 95% |
| Model quality | Full | Severely degraded | CRITICAL |

---

## EVIDENCE

```
=== Tables with actual data ===
301

=== Tables skipped ===
4,157
```

---

## FIX REQUIRED

Add column prefix logic to the DIRECT IN-MEMORY path (line 375-389):

```python
# BEFORE checking for duplicates, prefix the columns
prefix = table_name.replace(f'_{pair}', '').replace('_', '')
table_df = table_df.rename(columns={c: f"{prefix}_{c}" for c in table_df.columns if c != 'interval_time'})

# Then check for duplicates
feature_cols = [c for c in table_df.columns if c != 'interval_time' and c not in existing_cols]
```

---

## RECOMMENDATION

1. **STOP** current Step 6 run (wasted compute, bad output)
2. **FIX** the prefix bug in parallel_feature_testing.py
3. **RESTART** Step 6 with fix applied

---

## SEVERITY

**CRITICAL** - Current output will be unusable for Step 7.

---

**Enhancement Agent (EA)**
