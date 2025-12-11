# CE Directive: Complete Gap Remediation for Step 6

**Date**: December 11, 2025 03:15 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **CRITICAL**
**Reference**: Feature Coverage Audit 20251211

---

## STEP 6 HALTED

All Step 6 processes stopped until gaps remediated.

---

## GAP ANALYSIS COMPLETE

### Current Extraction (WORKING)

| Category | Query Pattern | Tables |
|----------|---------------|--------|
| Pair-specific | `%{pair}%` | 4,635 (166 per pair × 28) |
| Triangulation | `tri_*` | 194 |
| Market-wide | `mkt_*` | 12 |
| **SUBTOTAL** | | **4,841** |

### GAPS IDENTIFIED (MISSING)

| Category | Query Pattern | Tables | Impact |
|----------|---------------|--------|--------|
| **Variance** | `var_*` | **63** | Currency-level variance features |
| **Currency Strength** | `csi_*` | **144** | CSI features (IMPLEMENTED - not extracted) |
| **TOTAL MISSING** | | **207** | ~4% of total tables |

---

## REMEDIATION REQUIRED

### Fix `get_feature_tables_for_pair()` in `parallel_feature_testing.py`

Current code (lines 57-101):
```python
def get_feature_tables_for_pair(pair: str) -> dict:
    # Category 1: Pair-specific tables
    pair_query = f"... WHERE table_name LIKE '%{pair}%'"

    # Category 2: Triangulation tables
    tri_query = "... WHERE STARTS_WITH(table_name, 'tri_')"

    # Category 3: Market-wide tables
    mkt_query = "... WHERE STARTS_WITH(table_name, 'mkt_')"
```

**ADD these queries:**

```python
    # Category 4: Variance tables (currency-level, apply to all pairs)
    var_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'var_')
    ORDER BY table_name
    """
    var_tables = [row.table_name for row in client.query(var_query).result()]

    # Category 5: Currency Strength Index tables (currency-level, apply to all pairs)
    csi_query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE STARTS_WITH(table_name, 'csi_')
    ORDER BY table_name
    """
    csi_tables = [row.table_name for row in client.query(csi_query).result()]

    return {
        'pair_specific': pair_tables,
        'triangulation': tri_tables,
        'market_wide': mkt_tables,
        'variance': var_tables,      # NEW
        'currency_strength': csi_tables  # NEW
    }
```

### Update `query_pair_with_checkpoints()`

Add the new categories to `all_tables`:

```python
all_tables = (
    tables['pair_specific'] +
    tables['triangulation'] +
    tables['market_wide'] +
    tables['variance'] +        # NEW
    tables['currency_strength']  # NEW
)
```

---

## EXPECTED RESULT AFTER FIX

| Category | Tables | Status |
|----------|--------|--------|
| Pair-specific | 4,635 | ✅ |
| Triangulation | 194 | ✅ |
| Market-wide | 12 | ✅ |
| Variance | 63 | ✅ NEW |
| Currency Strength | 144 | ✅ NEW |
| **TOTAL** | **5,048** | **100%** |

---

## DELIVERABLES

1. **Modify `parallel_feature_testing.py`**:
   - Add `var_*` query to `get_feature_tables_for_pair()`
   - Add `csi_*` query to `get_feature_tables_for_pair()`
   - Update `all_tables` construction in both query functions

2. **Test dry_run on EURUSD**:
   - Verify new table count: ~462 + 63 + 144 = ~669 tables per pair
   - Confirm no errors

3. **Report to CE**:
   - Confirmation of fix
   - New table counts
   - Ready for Step 6 restart

---

## TIMELINE

| Task | ETA |
|------|-----|
| Implement fix | 15 min |
| Test dry_run | 10 min |
| Report to CE | 5 min |
| **TOTAL** | **30 min** |

---

## AUTHORIZATION

You are authorized to modify:
- `pipelines/training/parallel_feature_testing.py`

**DO NOT** restart Step 6 until CE authorizes.

---

**Chief Engineer (CE)**
