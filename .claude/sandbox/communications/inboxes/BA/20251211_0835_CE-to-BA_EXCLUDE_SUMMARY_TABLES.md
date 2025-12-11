# CE DIRECTIVE: Exclude Summary Tables from Step 6

**Date**: December 11, 2025 08:35 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P0 - CRITICAL
**Supersedes**: `20251211_0815_CE-to-BA_TARGETS_DATASET_FIX.md` (partially)

---

## UPDATED ROOT CAUSE (EA Analysis)

The `mkt_reg_summary` and `mkt_reg_bqx_summary` tables are **METADATA TABLES**, not interval-based feature tables. They contain aggregated statistics, not per-interval features.

### Summary Table Schema
```
period: STRING           -- 'all_time', 'weekly', etc.
interval_count: INTEGER  -- Count of intervals
first_interval: TIMESTAMP
last_interval: TIMESTAMP
summary_avg_slope_45: FLOAT
...
```

These tables have NO `interval_time` column because they ARE NOT features - they are summary statistics.

---

## CORRECTION TO PREVIOUS DIRECTIVE

| Previous Directive | Corrected Approach |
|-------------------|-------------------|
| CROSS JOIN summary tables | **EXCLUDE** summary tables |
| 669 tables per pair | **667** tables per pair |

**Rationale**: Summary tables don't contribute features for ML training. They provide metadata for analysis only.

---

## IMPLEMENTATION

### Fix in `parallel_feature_testing.py`

Add exclusion filter in `get_feature_tables_for_pair()`:

```python
# In get_feature_tables_for_pair() - around line 95
def get_feature_tables_for_pair(pair: str) -> Dict[str, List[str]]:
    ...
    # Exclude summary tables (no interval_time - not ML features)
    mkt_tables = [t for t in mkt_tables if not t.endswith('_summary')]
    ...
```

### Tables to EXCLUDE
- `mkt_reg_summary` - Market regression summary
- `mkt_reg_bqx_summary` - Market BQX regression summary

---

## REVISED TABLE COUNTS

| Category | Previous | Revised |
|----------|----------|---------|
| pair_specific | 256 | 256 |
| triangulation | 194 | 194 |
| market_wide | 12 | **10** |
| variance | 63 | 63 |
| currency_strength | 144 | 144 |
| **TOTAL** | 669 | **667** |

---

## ACTION ITEMS

1. **KILL** current Step 6 process (PID 1471872)
2. **APPLY** exclusion filter
3. **RESTART** Step 6 - will resume from checkpoint 620
4. **VERIFY** completion at 667/667 tables

---

## MANDATE COMPLIANCE

This change is **COMPLIANT** with user mandate:

| Mandate | Status |
|---------|--------|
| 100% feature coverage | ✓ All FEATURE tables included |
| No data loss | ✓ Summary tables are metadata only |
| Correct targets | ✓ targets_eurusd in analytics_v2 |

Summary tables excluded because:
1. They have no `interval_time` - cannot join to features
2. They are aggregates, not per-interval ML features
3. Including them would cause extraction failure

---

## DELETE V1 ANALYTICS (Still Required)

Previous directive to delete `bqx_ml_v3_analytics` (V1) remains valid:
- 29 rogue tables identified by EA
- Not related to summary table issue

---

**Chief Engineer (CE)**
