# CE Directive: GAP-001 Remediation - Stability Selection BigQuery Dependency

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 21:55 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Subject**: Fix Stability Selection to Use Step 6 Parquet Output

---

## ISSUE: GAP-001

**Description**: Step 7 (stability selection) still queries BigQuery instead of using Step 6 parquet output.

**Impact**:
- Wasted Step 6 computation
- Additional $30 BigQuery cost
- Potential data inconsistency between extraction and selection

**Source**: EA Comprehensive Audit (21:45)

---

## REQUIRED FIX

### File: `pipelines/training/feature_selection_robust.py`

**Current Behavior**: Queries BigQuery directly for feature data

**Required Behavior**: Read from Step 6 parquet output first

### Implementation

Add parquet input option:

```python
def load_features_for_selection(pair: str, horizon: int) -> pd.DataFrame:
    """Load features from Step 6 parquet output (preferred) or BigQuery (fallback)."""

    # Primary: Step 6 parquet output
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    if os.path.exists(parquet_path):
        print(f"Loading from parquet: {parquet_path}")
        return pd.read_parquet(parquet_path)

    # Fallback: BigQuery (with warning)
    print(f"WARNING: Parquet not found, querying BigQuery (cost incurred)")
    return query_bigquery_features(pair, horizon)
```

### Files to Modify

| File | Change |
|------|--------|
| `feature_selection_robust.py` | Add `load_features_for_selection()` |
| `feature_selection_robust.py` | Replace BigQuery calls with parquet reads |
| `scripts/parallel_stability_selection.py` | Same changes |

---

## VALIDATION

After fix:
- [ ] Stability selection reads from `data/features/{pair}_merged_features.parquet`
- [ ] No BigQuery queries during stability selection (verify in logs)
- [ ] Feature count matches Step 6 output (10,783)

---

## TIMELINE

Complete before Step 7 begins (after Step 6 completes).

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 21:55 UTC
