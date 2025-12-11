# BA Report: Step 6 Merge Performance Issue

**Date**: December 11, 2025 09:45 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: P2 - PERFORMANCE
**Category**: Step 6 Optimization Needed

---

## ISSUE SUMMARY

EURUSD merge phase taking **35+ minutes** due to sequential pandas merge of 667 parquet files.

---

## CURRENT STATUS

| Metric | Value |
|--------|-------|
| PID | 1493048 |
| Elapsed | 35+ minutes |
| Memory | 18 GB (27.5% of 62GB) |
| CPU | 96% |
| Phase | Merging checkpoints |

---

## ROOT CAUSE ANALYSIS

The current merge implementation uses **sequential pandas joins**:

```python
# Current approach (slow)
for pq_file in checkpoint_files:  # 667 files
    table_df = pd.read_parquet(pq_file)
    merged_df = merged_df.merge(table_df, on='interval_time', how='left')
```

This approach:
1. Reads each file one at a time
2. Performs 667 sequential merge operations
3. Memory grows with each merge
4. No parallelization

---

## DATA SCALE

| Metric | Value |
|--------|-------|
| Checkpoint files | 667 |
| Checkpoint size | 12 GB |
| Target rows | ~500,000 |
| Feature columns | ~6,477 |
| Final merged size | ~25+ GB (estimated) |

---

## RECOMMENDATIONS

### Option 1: DuckDB Merge (RECOMMENDED)
Replace pandas merge with DuckDB's parallel SQL join:

```python
import duckdb

# DuckDB can merge all files in parallel
query = """
SELECT * FROM read_parquet('checkpoints/*.parquet', union_by_name=true)
"""
merged_df = duckdb.query(query).df()
```

**Benefits**: 5-10x faster, memory-efficient, parallel I/O

### Option 2: Chunked Merge
Merge files in batches of 50, then merge batches:

```python
BATCH_SIZE = 50
batches = [files[i:i+BATCH_SIZE] for i in range(0, len(files), BATCH_SIZE)]
# Merge within batches, then merge batches
```

### Option 3: Accept Current Duration
35+ min per pair × 28 pairs = ~16+ hours for merge phase alone

---

## IMMEDIATE ACTION

**No action required** - current merge will complete, just slowly.

Optimization should be prioritized for future runs.

---

## ESTIMATED TIMELINE (Current Approach)

| Pair | Extraction | Merge | Total |
|------|------------|-------|-------|
| EURUSD | 10 min | 40 min | 50 min |
| Per pair | 10 min | 40 min | 50 min |
| **28 pairs** | 280 min | 1120 min | **~23 hours** |

---

**Build Agent (BA)**
