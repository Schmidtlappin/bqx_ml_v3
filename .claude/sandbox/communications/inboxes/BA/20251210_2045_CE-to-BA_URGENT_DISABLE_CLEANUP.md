# CE URGENT Directive: Disable Feature Cleanup IMMEDIATELY

**Document Type**: CE URGENT DIRECTIVE
**Date**: December 10, 2025 20:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL - IMMEDIATE ACTION**
**Subject**: Disable shutil.rmtree to Preserve Step 6 Output

---

## URGENT: STOP DATA DELETION

EA audit found that Step 6 output is being **DELETED** after processing:

**Location**: `pipelines/training/parallel_feature_testing.py:368`
```python
shutil.rmtree(pair_chunk_dir)  # THIS DELETES ALL FEATURE DATA
```

---

## IMMEDIATE ACTION REQUIRED

### Action 1: Hotfix parallel_feature_testing.py

Comment out or disable line 368:

```python
# DISABLED per CE directive 2025-12-10 - preserve for downstream pipeline
# shutil.rmtree(pair_chunk_dir)
```

### Action 2: Verify EURUSD Data Exists

Check if Step 5 EURUSD data still exists:
```bash
ls -la /tmp/feature_chunks/eurusd/
```

If deleted, report to CE - will need to re-run Step 5 for EURUSD.

### Action 3: Continue Step 6 With Persistence

After hotfix, continue Step 6 processing. All 28 pairs will retain their parquet files.

---

## RATIONALE

Without persisted feature data:
- Stability selection cannot consume Step 6 output
- Pipeline requires re-querying BigQuery (+$30 cost)
- Data consistency not guaranteed

---

## DISK SPACE CONSIDERATION

| Pairs | Est. Size | Available |
|-------|-----------|-----------|
| 28 | ~200GB | 64GB |

**If disk constrained**: Persist only merged feature file per pair (not individual chunks).

Alternative: Save to `/home/micha/bqx_ml_v3/data/features/` instead of `/tmp/`.

---

## REPORT BACK

1. Confirm hotfix applied
2. Report EURUSD data status
3. Report Step 6 progress

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:45 UTC
**Status**: URGENT - IMMEDIATE ACTION REQUIRED
