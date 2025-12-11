# BA Report: Step 6 Refactored - Direct In-Memory Approach

**Document Type**: BA STATUS REPORT
**Date**: December 10, 2025 22:08 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE), All Agents
**Priority**: **HIGH**
**Subject**: Step 6 Architecture Change

---

## ISSUE: Parquet-Chunked Approach Unstable

The original parquet-chunked approach crashed multiple times during the 460-file merge phase. Process repeatedly failed at ~70-80% completion.

---

## SOLUTION: Direct In-Memory Approach

With 64GB RAM now available, refactored to simpler direct merge:

### Before (Parquet-Chunked)
```
Query table → Save parquet → ... (462 files) → Merge 460 files → Save
```
- Complex, many I/O operations
- Unstable merge phase
- Crashed multiple times

### After (Direct In-Memory)
```
Query targets → For each table: Query → Merge directly → Save final parquet
```
- Simple, proven approach
- Step 5 validated: 24GB peak, 10,783 features
- No intermediate files

---

## Code Changes

**File**: `pipelines/training/parallel_feature_testing.py`

1. **Added**: `query_pair_direct()` function (lines 260-374)
   - Direct in-memory query and merge
   - No parquet intermediates
   - Saves final merged parquet to `data/features/`

2. **Modified**: `process_pair_all_horizons()` (line 509)
   - Changed from `query_pair_batched()` to `query_pair_direct()`

---

## Current Status

Step 6 now running with new approach:
```
DIRECT IN-MEMORY - 64GB RAM
```

---

## Memory Analysis

| Phase | Previous | New |
|-------|----------|-----|
| Query | ~7GB | ~7GB |
| Merge | ~20GB (unstable) | ~24GB (proven) |
| Available | 62GB | 62GB |
| Headroom | 42GB | 38GB |

---

**Build Agent (BA)**
**Date**: December 10, 2025 22:08 UTC
