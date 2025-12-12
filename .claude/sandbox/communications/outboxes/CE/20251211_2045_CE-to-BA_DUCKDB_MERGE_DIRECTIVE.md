# CE Directive: DuckDB Merge Strategy Implementation

**Date**: December 11, 2025 20:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Category**: Implementation Directive
**Decision**: APPROVED

---

## EXECUTIVE DECISION

**APPROVED: Option A - DuckDB Local Merge Strategy**

Based on EA's comprehensive analysis (message 1030), I am approving the DuckDB merge approach over the previously planned BigQuery ETL strategy.

**Rationale:**
- **Cost savings**: $180.60 over 12 months ($0 vs $2.52 + $14.84/month)
- **Time savings**: 67-76% faster (1-3 hours vs 5.6-9.3 hours)
- **Low risk**: 20GB/62GB memory usage, proven fallback available
- **Minimal effort**: 30 min code + 18 min test = 48 minutes
- **Zero dependencies**: All local, no BigQuery/network required

**This directive supersedes CE directive 1015 (BigQuery ETL strategy).**

---

## YOUR MISSION

Implement DuckDB merge for all 28 currency pairs, starting with EURUSD as proof-of-concept.

### Success Criteria
1. ✅ EURUSD merged successfully (100K rows, ~6,500 columns, 49 targets)
2. ✅ 2 additional test pairs merged successfully
3. ✅ All 28 pairs merged (1-3 hours total execution time)
4. ✅ Memory usage stays below 32GB peak
5. ✅ Zero BigQuery costs incurred

---

## IMPLEMENTATION INSTRUCTIONS

### Phase 0: Debug/Test with EURUSD Checkpoints (15 minutes) **DO THIS FIRST**

**CRITICAL**: Before modifying production code, test the DuckDB approach manually with EURUSD parquet files.

**Purpose:**
- Verify DuckDB can handle 667 parquet files
- Confirm memory usage stays reasonable
- Test JOIN syntax works correctly
- Validate output has correct shape
- Debug any issues BEFORE code modification

**Test Script:**

```python
#!/usr/bin/env python3
"""
Test DuckDB merge with EURUSD checkpoints
Run this BEFORE modifying parallel_feature_testing.py
"""
import duckdb
import os
import time
import pandas as pd

def test_duckdb_merge_eurusd():
    """Test DuckDB merge approach with EURUSD data."""

    print("=== DuckDB Merge Test: EURUSD ===\n")

    # Paths
    checkpoint_dir = "checkpoints/eurusd"
    targets_path = os.path.join(checkpoint_dir, "targets.parquet")

    # Verify checkpoint exists
    if not os.path.exists(checkpoint_dir):
        print(f"✗ Checkpoint directory not found: {checkpoint_dir}")
        return False

    if not os.path.exists(targets_path):
        print(f"✗ Targets file not found: {targets_path}")
        return False

    # Get all parquet files
    all_files = [f for f in os.listdir(checkpoint_dir) if f.endswith('.parquet')]
    feature_files = [f for f in all_files if f != 'targets.parquet']

    print(f"Checkpoint directory: {checkpoint_dir}")
    print(f"Total parquet files: {len(all_files)}")
    print(f"Feature files: {len(feature_files)}")
    print(f"Targets file: targets.parquet")
    print()

    # Initialize DuckDB
    print("Initializing DuckDB...")
    con = duckdb.connect()
    con.execute("SET memory_limit='32GB'")
    con.execute("SET threads=8")
    con.execute("SET preserve_insertion_order=false")
    print("✓ DuckDB initialized (32GB limit, 8 threads)")
    print()

    # Build SQL query
    print(f"Building SQL query with {len(feature_files)} LEFT JOINs...")
    sql = f"SELECT * FROM parquet_scan('{targets_path}') AS t"

    for i, file in enumerate(feature_files[:10]):  # Show first 10
        file_path = os.path.join(checkpoint_dir, file)
        print(f"  JOIN {i+1}: {file}")

    if len(feature_files) > 10:
        print(f"  ... and {len(feature_files) - 10} more files")

    for i, file in enumerate(feature_files):
        file_path = os.path.join(checkpoint_dir, file)
        sql += f"\n    LEFT JOIN parquet_scan('{file_path}') AS f{i} USING (interval_time)"

    print()

    # Execute merge
    print("Executing DuckDB merge...")
    print("(This may take 2-6 minutes, monitor memory with: watch -n 1 free -h)")
    print()

    start_time = time.time()

    try:
        result = con.execute(sql).df()
        elapsed = time.time() - start_time

        # Validate result
        print("✓ MERGE SUCCESSFUL\n")
        print(f"Execution time: {elapsed:.1f} seconds ({elapsed/60:.2f} minutes)")
        print(f"Result shape: {result.shape[0]:,} rows × {result.shape[1]:,} columns")
        print()

        # Check targets
        target_cols = [c for c in result.columns if c.startswith('bqx') and '_h' in c]
        print(f"Target columns found: {len(target_cols)}")
        print(f"First 10 targets: {target_cols[:10]}")
        print()

        # Validate expectations
        assert result.shape[0] == 100000, f"Expected 100K rows, got {result.shape[0]:,}"
        assert len(target_cols) == 49, f"Expected 49 targets, got {len(target_cols)}"
        assert result.shape[1] > 6000, f"Expected 6000+ columns, got {result.shape[1]:,}"

        print("✓ VALIDATION PASSED")
        print(f"  - Row count: {result.shape[0]:,} (expected 100,000)")
        print(f"  - Target columns: {len(target_cols)} (expected 49)")
        print(f"  - Total columns: {result.shape[1]:,} (expected 6000+)")
        print()

        # Memory estimate
        memory_mb = result.memory_usage(deep=True).sum() / (1024**2)
        print(f"DataFrame memory usage: {memory_mb:,.1f} MB ({memory_mb/1024:.2f} GB)")
        print()

        con.close()

        print("=== TEST COMPLETE: SUCCESS ===")
        print()
        print("Next step: Proceed with Phase 1 (code modification)")
        return True

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ MERGE FAILED after {elapsed:.1f} seconds\n")
        print(f"Error: {e}")
        print()
        print("Debugging tips:")
        print("1. Check memory: free -h")
        print("2. Check DuckDB version: python3 -c 'import duckdb; print(duckdb.__version__)'")
        print("3. Try with fewer files (modify feature_files[:100] to test subset)")
        print("4. Check logs: dmesg | tail -50 (for OOM killer)")
        print()

        con.close()

        print("=== TEST COMPLETE: FAILED ===")
        print()
        print("DO NOT proceed with Phase 1. Report to CE with error details.")
        return False


if __name__ == "__main__":
    success = test_duckdb_merge_eurusd()
    exit(0 if success else 1)
```

**Save as**: `scripts/test_duckdb_merge.py`

**Execute:**
```bash
chmod +x scripts/test_duckdb_merge.py
python3 scripts/test_duckdb_merge.py
```

**Expected Output:**
```
=== DuckDB Merge Test: EURUSD ===

Checkpoint directory: checkpoints/eurusd
Total parquet files: 668
Feature files: 667
Targets file: targets.parquet

Initializing DuckDB...
✓ DuckDB initialized (32GB limit, 8 threads)

Building SQL query with 667 LEFT JOINs...
  JOIN 1: align_eurusd.parquet
  JOIN 2: atr_eurusd.parquet
  ...

Executing DuckDB merge...
(This may take 2-6 minutes)

✓ MERGE SUCCESSFUL

Execution time: 183.4 seconds (3.06 minutes)
Result shape: 100,000 rows × 6,527 columns

Target columns found: 49
First 10 targets: ['bqx45_h15', 'bqx45_h30', 'bqx45_h45', ...]

✓ VALIDATION PASSED
  - Row count: 100,000 (expected 100,000)
  - Target columns: 49 (expected 49)
  - Total columns: 6,527 (expected 6000+)

DataFrame memory usage: 5,234.5 MB (5.11 GB)

=== TEST COMPLETE: SUCCESS ===

Next step: Proceed with Phase 1 (code modification)
```

**If test succeeds:** Proceed to Phase 1
**If test fails:** Report to CE with full error output, DO NOT proceed

---

### Phase 1: Code Modification (30 minutes)

**File**: `pipelines/training/parallel_feature_testing.py`
**Function**: `merge_parquet_with_duckdb()` (lines 240-298)

**Replace the existing batched pandas approach with:**

```python
def merge_parquet_with_duckdb(targets_path: str, chunk_dir: str, output_path: str):
    """Use DuckDB to efficiently merge all parquet files.

    Args:
        targets_path: Path to targets.parquet file
        chunk_dir: Directory containing feature parquet files
        output_path: Path for merged output file

    Returns:
        pd.DataFrame: Merged dataframe with all features and targets
    """
    import duckdb
    import os
    import pandas as pd

    print(f"   Merging with DuckDB...")

    # Initialize DuckDB connection
    con = duckdb.connect()
    con.execute("SET memory_limit='32GB'")
    con.execute("SET threads=8")
    con.execute("SET preserve_insertion_order=false")

    # Get feature parquet files (exclude targets)
    all_files = [f for f in os.listdir(chunk_dir) if f.endswith('.parquet')]
    feature_files = [f for f in all_files if f != 'targets.parquet']

    if not feature_files:
        print(f"   No feature files found, returning targets only")
        con.close()
        return pd.read_parquet(targets_path)

    print(f"   Found {len(feature_files)} feature files to merge")

    # Build single SQL query with all LEFT JOINs
    sql = f"SELECT * FROM parquet_scan('{targets_path}') AS t"

    for i, file in enumerate(feature_files):
        file_path = os.path.join(chunk_dir, file)
        sql += f"\n    LEFT JOIN parquet_scan('{file_path}') AS f{i} USING (interval_time)"

    # Execute merge
    print(f"   Executing DuckDB merge (this may take 2-6 minutes)...")
    start_time = time.time()

    try:
        merged_df = con.execute(sql).df()
        elapsed = time.time() - start_time

        print(f"   ✓ Merge complete: {len(merged_df):,} rows, {len(merged_df.columns):,} columns")
        print(f"   ✓ Elapsed time: {elapsed:.1f} seconds ({elapsed/60:.2f} minutes)")

        con.close()
        return merged_df

    except Exception as e:
        print(f"   ✗ DuckDB merge failed: {e}")
        print(f"   → Falling back to batched pandas merge...")
        con.close()

        # Fallback to existing batched pandas approach
        return merge_parquet_batched_pandas(targets_path, chunk_dir, output_path)


def merge_parquet_batched_pandas(targets_path: str, chunk_dir: str, output_path: str):
    """Fallback: Batched pandas merge (existing implementation).

    This is the existing batched approach, kept as fallback if DuckDB fails.
    """
    import pandas as pd
    import os
    import gc

    print(f"   Using batched pandas merge (fallback mode)...")

    # Load targets
    merged_df = pd.read_parquet(targets_path)
    print(f"   Loaded targets: {len(merged_df):,} rows, {len(merged_df.columns):,} columns")

    # Get feature files
    all_files = [f for f in os.listdir(chunk_dir) if f.endswith('.parquet')]
    feature_files = [f for f in all_files if f != 'targets.parquet']

    if not feature_files:
        return merged_df

    # Process in batches of 50 files
    batch_size = 50
    num_batches = (len(feature_files) + batch_size - 1) // batch_size

    print(f"   Processing {len(feature_files)} files in {num_batches} batches...")

    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(feature_files))
        batch_files = feature_files[start_idx:end_idx]

        print(f"   Batch {batch_idx + 1}/{num_batches}: {len(batch_files)} files")

        for file in batch_files:
            file_path = os.path.join(chunk_dir, file)
            feature_df = pd.read_parquet(file_path)
            merged_df = merged_df.merge(feature_df, on='interval_time', how='left')
            del feature_df

        gc.collect()

    print(f"   ✓ Batched merge complete: {len(merged_df):,} rows, {len(merged_df.columns):,} columns")
    return merged_df
```

**Changes Summary:**
- Primary: DuckDB SQL-based merge (single query, all JOINs)
- Fallback: Batched pandas merge (existing approach, extracted to separate function)
- Error handling: Automatic fallback if DuckDB fails
- Memory safety: SET memory_limit='32GB'
- Performance: SET threads=8 for parallel execution

---

### Phase 2: Testing (18 minutes)

**Test Plan:**

1. **EURUSD Test** (6 minutes)
   ```bash
   python3 pipelines/training/parallel_feature_testing.py \
     --pair eurusd \
     --mode merge_only
   ```

   **Expected Output:**
   - Merge time: 2-6 minutes
   - Rows: 100,000
   - Columns: ~6,500
   - Memory peak: <20 GB
   - File: `checkpoints/eurusd/eurusd_merged_features.parquet`

   **Validation:**
   ```python
   import pandas as pd
   df = pd.read_parquet('checkpoints/eurusd/eurusd_merged_features.parquet')
   print(f"Shape: {df.shape}")
   print(f"Targets present: {[c for c in df.columns if c.startswith('bqx') and '_h' in c][:10]}")
   assert df.shape[0] == 100000, "Row count mismatch"
   assert len([c for c in df.columns if c.startswith('bqx') and '_h' in c]) == 49, "Target count mismatch"
   ```

2. **Test Pair 2: GBPUSD** (6 minutes)
   ```bash
   python3 pipelines/training/parallel_feature_testing.py \
     --pair gbpusd \
     --mode full  # Extract + merge
   ```

3. **Test Pair 3: USDJPY** (6 minutes)
   ```bash
   python3 pipelines/training/parallel_feature_testing.py \
     --pair usdjpy \
     --mode full
   ```

**If all 3 tests pass:** Proceed to Phase 3
**If any test fails:** Report to CE, use fallback pandas approach

---

### Phase 3: Full Rollout (1-3 hours)

**Execute for all 28 pairs:**

```bash
# Option A: Sequential (safest)
for pair in eurusd gbpusd usdjpy audusd nzdusd usdcad usdchf eurjpy eurgbp euraud eurchf eurnzd eurcad gbpjpy gbpaud gbpchf gbpnzd gbpcad audjpy audnzd audcad audchf nzdjpy nzdusd nzdcad nzdchf cadjpy chfjpy; do
    echo "=== Processing $pair ==="
    python3 pipelines/training/parallel_feature_testing.py \
      --pair $pair \
      --mode merge_only
done
```

**Option B: Parallel (faster, if memory allows):**
- Run 4 pairs in parallel (4 x 20GB = 80GB potential, but DuckDB should stay under 32GB per process)
- Monitor memory usage: `watch -n 5 free -h`

**Monitoring:**
- Watch memory: `watch -n 5 free -h`
- Watch progress: `tail -f logs/merge_all_pairs.log`
- Checkpoint after each pair: Verify merged file created

---

## ROLLBACK PLAN

**If DuckDB fails at any point:**

1. **Immediate**: Code already has automatic fallback to batched pandas
2. **Manual**: Revert to CE directive 1015 (BigQuery ETL)
3. **Report**: Send failure details to CE with logs

**Rollback triggers:**
- DuckDB OOM crash (memory >58GB)
- DuckDB JOIN limit hit (667 JOINs too many)
- Merge time >30 minutes per pair
- Any 2 test failures in Phase 2

---

## SUCCESS REPORTING

After completion, send CE a report with:

1. **Execution summary**: Time per pair, total time
2. **Memory usage**: Peak memory observed
3. **Output validation**: Row/column counts for all 28 pairs
4. **Cost**: $0 confirmed (no BigQuery charges)
5. **Issues encountered**: Any fallbacks used, errors, warnings

**Report format:**
```
Subject: 20251211_HHMM_BA-to-CE_DUCKDB_MERGE_COMPLETE.md

Summary:
- Pairs merged: 28/28
- Total time: X hours Y minutes
- Peak memory: XX GB
- Cost: $0
- Fallbacks used: N pairs (if any)
- Status: SUCCESS
```

---

## DEPENDENCIES & VERIFICATION

**Before starting, verify:**

```bash
# 1. DuckDB installed
python3 -c "import duckdb; print(f'DuckDB version: {duckdb.__version__}')"

# 2. Checkpoints exist
ls -lh checkpoints/eurusd/ | wc -l  # Should be 668 files

# 3. Available memory
free -h  # Should show 50+ GB available

# 4. Disk space
df -h checkpoints/  # Need ~50GB free for merged files
```

**If DuckDB not installed:**
```bash
pip3 install duckdb --upgrade
```

---

## TIMELINE

| Phase | Duration | Checkpoint |
|-------|----------|------------|
| Code modification | 30 min | Code committed, tests added |
| Testing (3 pairs) | 18 min | 3 merged files validated |
| Full rollout | 1-3 hours | 28 merged files created |
| **TOTAL** | **2-4 hours** | All pairs ready for training |

**Start immediately.** Report after Phase 2 testing complete.

---

## AUTHORIZATION

**Authority**: Chief Engineer (CE)
**Scope**: Modify merge strategy, implement DuckDB approach
**Budget**: $0 (no costs authorized)
**Timeline**: Complete within 4 hours
**Approval**: GRANTED

---

## NOTES

- This strategy saves $180.60 over 12 months vs BigQuery ETL
- EA's analysis was thorough and compelling
- Fallback to pandas batching ensures zero risk
- QA and EA will be notified of this decision
- Intelligence files will be updated to reflect new strategy

**Proceed with confidence. EA has done excellent analysis work.**

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
