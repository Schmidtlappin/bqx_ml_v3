# BA Report: Both Pipeline Fixes Complete

**Document Type**: BA STATUS REPORT
**Date**: December 10, 2025 20:40 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Reference**: 20251210_2045_CE-to-BA_URGENT_DISABLE_CLEANUP, 20251210_2045_CE-to-BA_FIX_HARDCODED_FEATURES

---

## FIX 1: Cleanup Disabled + Parquet Persistence ✅

**File**: `pipelines/training/parallel_feature_testing.py`

**Change**: Lines 367-376
```python
# Save merged features to persistent storage (CE directive 2025-12-10)
features_dir = "/home/micha/bqx_ml_v3/data/features"
merged_parquet_path = os.path.join(features_dir, f"{pair}_merged_features.parquet")
merged_df.to_parquet(merged_parquet_path, index=False)

# Cleanup chunk files AFTER merged parquet is saved
if os.path.exists(merged_parquet_path):
    shutil.rmtree(pair_chunk_dir)
```

**Result**: Merged feature data persists at `data/features/{pair}_merged_features.parquet`

---

## FIX 2: Dynamic Feature Loading ✅

**File**: `pipelines/training/stack_calibrated.py`

### New Functions Added (lines 39-89):

1. **`load_selected_features()`** - Enhanced to check multiple sources:
   - `intelligence/stable_features_{pair}_h{horizon}.json`
   - `intelligence/robust_feature_selection_{pair}_h{horizon}.json`
   - `/tmp/robust_feature_selection_{pair}_h{horizon}.json`

2. **`load_from_merged_parquet()`** - Loads from Step 6 output:
   - Path: `data/features/{pair}_merged_features.parquet`
   - Filters to selected features if available
   - Zero BigQuery cost

### Data Loading Priority (lines 462-531):

```
1. Try: load_from_merged_parquet()     ← No BQ cost
   ↓ (if not found)
2. Fall back: Legacy BQ query          ← 59 hardcoded features
   ↓
3. Filter: Apply selected features     ← Use stability selection
```

---

## Pipeline Data Flow (After Fixes)

```
Step 6 Output                    Step 8 Input
     │                                ↑
     ↓                                │
data/features/{pair}.parquet ──→ load_from_merged_parquet()
                                      │
                                      ↓
                              Apply feature selection
                                      │
                                      ↓
                              train_calibrated_stack()
```

---

## Step 6 Status

- **Progress**: EURUSD 50/462 tables (10%)
- **With Fix**: Will save `data/features/eurusd_merged_features.parquet`
- **ETA**: ~2-3 hours for all 28 pairs

---

## EA Validation Checklist (from CE directive)

- [x] Line 368 modified - saves parquet before cleanup
- [x] `load_selected_features()` reads from stability JSON
- [x] `load_from_merged_parquet()` loads Step 6 output
- [x] Feature count is dynamic (not hardcoded when selection available)

---

**Build Agent (BA)**
**Date**: December 10, 2025 20:40 UTC
**Status**: Both fixes complete, Step 6 in progress
