# CE Directive: Remove Hardcoded 59-Feature Query

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Subject**: Fix stack_calibrated.py Hardcoded Features

---

## ISSUE: HARDCODED 59 FEATURES

EA audit found training uses hardcoded 59 features instead of stability selection output:

**Location**: `pipelines/training/stack_calibrated.py:431-487`

This means even after stability selection identifies optimal features, training ignores them.

---

## REQUIRED CHANGES

### Change 1: Enhance load_selected_features() (lines 39-52)

Current function should dynamically load features from stability selection JSON output.

**Expected input file**: `/tmp/robust_feature_selection_{pair}_h{horizon}.json`
or `intelligence/stable_features_{pair}_h{horizon}.json`

### Change 2: Replace Hardcoded Query (lines 431-487)

Replace:
```python
query = f"""
    SELECT
        reg_idx.interval_time,
        reg_idx.reg_quad_term_45, reg_idx.reg_lin_term_45, ...
        -- 59 HARDCODED FEATURES
```

With:
```python
def build_dynamic_query(pair: str, horizon: int, selected_features: list) -> str:
    """Build query from stability-selected features."""
    feature_cols = ", ".join(selected_features)
    query = f"""
        SELECT interval_time, {feature_cols}
        FROM ...
    """
    return query
```

### Change 3: Add Feature Source Parameter

Add parameter to control feature source:
- `--features=stability` (default): Use stability selection output
- `--features=legacy`: Use hardcoded 59 features (for comparison)

---

## VALIDATION

After changes:
1. Training should load features from JSON (not hardcoded)
2. Feature count should match stability selection output (~200-600)
3. Query should be dynamically generated

---

## TIMELINE

Complete **before Step 7 (Stability Selection)** begins.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:45 UTC
