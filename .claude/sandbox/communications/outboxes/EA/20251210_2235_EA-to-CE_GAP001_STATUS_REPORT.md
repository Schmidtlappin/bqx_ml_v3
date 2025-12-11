# EA Report: GAP-001 Status - Partial Fix

**Document Type**: EA GAP ANALYSIS UPDATE
**Date**: December 10, 2025 22:35 UTC
**From**: Engineering Agent (EA)
**To**: Chief Engineer (CE)
**Priority**: **HIGH**
**Subject**: GAP-001 Step 7 Parquet Loading - Partial Fix

---

## EXECUTIVE SUMMARY

GAP-001 (Step 7 re-queries BigQuery) is **PARTIALLY FIXED**.

| Script | Status | Risk |
|--------|--------|------|
| `feature_selection_robust.py` | **PARTIAL** | Requires `--parquet` flag |
| `parallel_stability_selection.py` | **NOT FIXED** | Uses BigQuery only |

---

## DETAILED ANALYSIS

### feature_selection_robust.py

**Fix Applied** (lines 70-80, 700-712):
```python
def load_from_parquet(pair: str) -> pd.DataFrame:
    """Load feature data from Step 6 merged parquet (no BigQuery cost)."""
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    ...
```

**Usage**: Requires `--parquet` flag:
```bash
python feature_selection_robust.py eurusd --parquet  # Uses parquet
python feature_selection_robust.py eurusd            # Uses BigQuery (default!)
```

**Issue**: Default still uses BigQuery. Easy to forget `--parquet` flag.

### parallel_stability_selection.py

**Status**: NO FIX APPLIED

Still imports and uses BigQuery directly:
- Line 16: `from google.cloud import bigquery`
- Line 35: `bigquery.Client(project=PROJECT)`
- Lines 48, 65, 77: Direct BigQuery queries

---

## RISK ASSESSMENT

| Risk | Impact | Likelihood |
|------|--------|------------|
| Step 7 runs without `--parquet` | $30 BQ cost, data inconsistency | **HIGH** if not documented |
| parallel_stability_selection used | $30+ BQ cost | **MEDIUM** |

---

## RECOMMENDATIONS

### Option A: Quick Fix (Recommended)
Make parquet the DEFAULT in `feature_selection_robust.py`:

```python
# Line 700-712: Change default behavior
use_parquet = "--bq" not in sys.argv  # Default to parquet
```

**Effort**: 5 minutes
**Impact**: Eliminates $30 cost per run

### Option B: Full Fix
Add parquet loading to `parallel_stability_selection.py`:

```python
def load_from_parquet(pair: str) -> pd.DataFrame:
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    return pd.read_parquet(parquet_path)
```

**Effort**: 30 minutes
**Impact**: Full GAP-001 resolution

### Option C: Document and Proceed
Document that Step 7 MUST use `--parquet` flag. Accept risk for `parallel_stability_selection.py`.

---

## CE DECISION REQUIRED

Before Step 7 runs, please confirm:

1. [ ] Apply Option A (make parquet default)?
2. [ ] Apply Option B (fix both scripts)?
3. [ ] Accept Option C (document only)?

---

**Enhancement Agent (EA)**
**Date**: December 10, 2025 22:35 UTC
