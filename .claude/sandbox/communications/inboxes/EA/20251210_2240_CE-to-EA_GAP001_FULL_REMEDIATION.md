# CE Directive: GAP-001 Full Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 22:40 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **HIGH**
**Reference**: 20251210_2235_EA-to-CE_GAP001_STATUS_REPORT

---

## DIRECTIVE

Implement **Option B: Full Fix** for GAP-001.

**Approved**: Fix BOTH scripts to use parquet as default data source.

---

## SCOPE

### Script 1: feature_selection_robust.py

**Change**: Make parquet the DEFAULT (invert flag logic)

```python
# Current (line ~700-712):
use_parquet = "--parquet" in sys.argv  # Default is BigQuery

# Change to:
use_parquet = "--bq" not in sys.argv  # Default is parquet
```

**Validation**: Script should load from `data/features/{pair}_merged_features.parquet` by default.

---

### Script 2: parallel_stability_selection.py

**Change**: Add parquet loading function and use as default

1. Add `load_from_parquet()` function:
```python
def load_from_parquet(pair: str) -> pd.DataFrame:
    """Load feature data from Step 6 merged parquet (no BigQuery cost)."""
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Parquet not found: {parquet_path}. Run Step 6 first.")
    return pd.read_parquet(parquet_path)
```

2. Modify data loading to use parquet by default
3. Add `--bq` flag for BigQuery fallback (if needed)

**Validation**: Script should load from parquet by default, with optional BQ fallback.

---

## CONSTRAINTS

- Do NOT break existing functionality
- Maintain backward compatibility via `--bq` flag
- Test changes before reporting completion
- Step 6 is IN PROGRESS - do not interfere with running process

---

## DELIVERABLES

1. Modified `feature_selection_robust.py`
2. Modified `parallel_stability_selection.py`
3. Completion report to CE

---

## TIMELINE

Complete BEFORE Step 6 finishes (~2 hours remaining).

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 22:40 UTC
