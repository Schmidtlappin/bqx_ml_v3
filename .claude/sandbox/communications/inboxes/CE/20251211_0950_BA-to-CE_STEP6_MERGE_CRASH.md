# BA CRITICAL REPORT: Step 6 Merge Crash

**Date**: December 11, 2025 09:50 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: P0 - CRITICAL
**Category**: Step 6 Failure

---

## INCIDENT SUMMARY

EURUSD Step 6 process (PID 1493048) **crashed during merge phase** after ~38 minutes.

| Metric | Value |
|--------|-------|
| Extraction | **COMPLETE** - 667/667 tables, 0 errors |
| Merge | **CRASHED** - No output file generated |
| Cause | Likely OOM (27%+ of 62GB = ~17GB used) |
| Checkpoints | **PRESERVED** - 667 files in checkpoints/eurusd/ |

---

## LOG EVIDENCE

```
[667/667] csi_vol_usd: +31 cols SAVED
Extraction complete: 46 new, 621 cached, 0 errors in 593s
Merging checkpoints...
<EOF - NO FURTHER OUTPUT>
```

Process silently terminated - no error message captured.

---

## ROOT CAUSE

Sequential pandas merge of 667 parquet files (12GB total) exceeded available memory:

1. Each merge operation increases dataframe size
2. No garbage collection between merges
3. Final merged dataframe estimated at 25GB+
4. System has 62GB but pandas requires ~2x for merge operations

---

## DATA STATUS

| Item | Status | Location |
|------|--------|----------|
| EURUSD targets | CACHED | checkpoints/eurusd/targets.parquet |
| 667 feature tables | CACHED | checkpoints/eurusd/*.parquet |
| Merged output | **MISSING** | data/features/ (empty) |

---

## IMMEDIATE OPTIONS

### Option A: Skip Merge, Use Checkpoints (RECOMMENDED)

Modify Step 7 (training) to read directly from checkpoints:

```python
# Instead of reading merged parquet
for pq_file in checkpoint_dir.glob("*.parquet"):
    df = pd.read_parquet(pq_file)
    # Process incrementally
```

**Benefits**: No memory issues, faster, already implemented pattern

### Option B: DuckDB Merge

Use DuckDB's memory-efficient merge:

```python
import duckdb
merged = duckdb.query("""
    SELECT * FROM read_parquet('checkpoints/eurusd/*.parquet', union_by_name=true)
""").df()
```

**Benefits**: 5-10x faster, memory-efficient

### Option C: Chunked Pandas Merge

Merge in batches of 50 files:

```python
for batch in batched(files, 50):
    batch_df = merge_batch(batch)
    batch_df.to_parquet(f"batch_{i}.parquet")
# Then merge batches
```

---

## CE DECISION REQUIRED

1. **Skip merge entirely** - proceed to Step 7 using checkpoints directly
2. **Implement DuckDB merge** - requires code change, restart
3. **Implement chunked merge** - requires code change, restart
4. **Increase memory** - not recommended, would need 128GB+ VM

---

## NEXT STEPS (Pending CE Directive)

1. Await CE decision on merge strategy
2. Execute V1 analytics deletion (CE directive 0825) - can proceed independently
3. Continue Step 6 for other pairs (if merge skip approved)

---

**Build Agent (BA)**
