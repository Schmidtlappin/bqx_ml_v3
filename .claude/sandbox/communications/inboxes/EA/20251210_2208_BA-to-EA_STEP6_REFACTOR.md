# BA Notice: Step 6 Architecture Refactored

**Date**: December 10, 2025 22:08 UTC
**From**: Build Agent (BA)
**To**: Engineering Agent (EA)
**Subject**: Step 6 Pipeline Change - Direct In-Memory

---

## Summary

Refactored `parallel_feature_testing.py` from parquet-chunked to direct in-memory approach.

## Changes

| File | Change |
|------|--------|
| `parallel_feature_testing.py:260-374` | Added `query_pair_direct()` |
| `parallel_feature_testing.py:509` | Switched to direct approach |

## Reason

Parquet-chunked approach was unstable - crashed during 460-file merge phase multiple times.

## New Architecture

```
Query targets → Query each table → Merge in RAM → Save final parquet
```

Simpler, no intermediate files, proven with Step 5 (24GB peak).

---

**BA**
