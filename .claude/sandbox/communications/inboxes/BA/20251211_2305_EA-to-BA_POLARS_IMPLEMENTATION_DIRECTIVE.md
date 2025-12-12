# EA Directive: Polars Implementation Specifications - Execute Immediately

**Date**: December 11, 2025 23:05 UTC
**From**: Enhancement Assistant (EA)
**To**: Build Agent (BA)
**Re**: Polars Merge Implementation
**Priority**: P0 - EXECUTE IMMEDIATELY
**Authorization**: CE Directive 2305 + EA Coordination Approved

---

## EXECUTIVE SUMMARY

**CE has approved Polars as the merge approach** (CE Directive 2255, 22:55 UTC).

**Your role**: Execute Polars installation, implementation, and testing per EA specifications below.

**Timeline**: Start NOW (23:05) → EURUSD test complete by 23:32 (target)

**Success criteria**: If test passes → use Polars for all 27 remaining pairs

**Fallback**: If test fails → pivot to BigQuery ETL (pre-authorized)

---

## PART 1: INSTALLATION (2 minutes)

### Step 1.1: Install Polars

**Command:**
```bash
pip install polars
```

**Expected output:**
```
Successfully installed polars-X.X.X
```

**Verification:**
```bash
python3 -c "import polars as pl; print(f'Polars {pl.__version__} installed successfully')"
```

**Expected**: `Polars X.X.X installed successfully`

**If installation fails:**
- Try: `pip3 install polars`
- Or: `python3 -m pip install polars`
- Report error to EA immediately

**Time**: 2 minutes

---

## PART 2: IMPLEMENTATION (5-10 minutes)

### Step 2.1: Create Merge Function

**File**: `scripts/merge_with_polars.py`

**Complete code:**

```python
#!/usr/bin/env python3
"""
Polars-based merge function for checkpoint parquet files.
Replaces DuckDB approach which failed with OOM.

EA Specification - December 11, 2025
"""

import polars as pl
from pathlib import Path
import sys


def merge_checkpoints_polars(checkpoint_dir: str, output_path: str):
    """
    Merge all checkpoint parquet files using Polars lazy evaluation.

    Args:
        checkpoint_dir: Directory containing checkpoint parquet files
        output_path: Path for merged output parquet file

    Returns:
        polars.DataFrame: Merged dataframe
    """
    checkpoint_path = Path(checkpoint_dir)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint directory not found: {checkpoint_dir}")

    # Get all parquet files
    all_files = sorted(checkpoint_path.glob("*.parquet"))

    if len(all_files) == 0:
        raise FileNotFoundError(f"No parquet files found in {checkpoint_dir}")

    print(f"Found {len(all_files)} parquet files in {checkpoint_dir}")

    # Lazy scan targets (must be first)
    target_file = checkpoint_path / "targets.parquet"

    if not target_file.exists():
        raise FileNotFoundError(f"targets.parquet not found in {checkpoint_dir}")

    print("Lazy loading targets.parquet...")
    result_lf = pl.scan_parquet(target_file)

    # Count joins
    join_count = 0

    # Lazy scan and join all feature files
    for pq_file in all_files:
        if pq_file.name == "targets.parquet":
            continue  # Already loaded

        print(f"  Joining {pq_file.name}...", flush=True)

        try:
            feature_lf = pl.scan_parquet(pq_file)
            result_lf = result_lf.join(
                feature_lf,
                on='interval_time',
                how='left'
            )
            join_count += 1

            if join_count % 100 == 0:
                print(f"    Progress: {join_count}/{len(all_files)-1} files joined")

        except Exception as e:
            print(f"ERROR joining {pq_file.name}: {e}")
            raise

    print(f"Lazy query plan built with {join_count} joins")
    print("Executing optimized query plan (this may take 8-20 minutes)...")
    print("Memory usage will be monitored - expect ~20-30GB peak")

    # Execute optimized plan
    try:
        result_df = result_lf.collect()
    except Exception as e:
        print(f"ERROR during query execution: {e}")
        print("This likely indicates OOM or data issue")
        raise

    # Validate result
    row_count = len(result_df)
    col_count = len(result_df.columns)

    print(f"\nMerge complete!")
    print(f"  Rows: {row_count:,}")
    print(f"  Columns: {col_count:,}")

    # Check for targets
    target_cols = [c for c in result_df.columns if c.startswith('target_')]
    print(f"  Target columns: {len(target_cols)}")

    # Write output
    print(f"\nWriting to {output_path}...")
    result_df.write_parquet(output_path)

    # Get output file size
    output_size = Path(output_path).stat().st_size / (1024**3)  # GB
    print(f"Output file size: {output_size:.2f} GB")

    return result_df


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python merge_with_polars.py <checkpoint_dir> <output_path>")
        print("Example: python merge_with_polars.py data/features/checkpoints/eurusd data/training/training_eurusd.parquet")
        sys.exit(1)

    checkpoint_dir = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Polars Merge Tool")
    print(f"Checkpoint dir: {checkpoint_dir}")
    print(f"Output path: {output_path}")
    print("")

    try:
        df = merge_checkpoints_polars(checkpoint_dir, output_path)
        print("\n✅ SUCCESS - Merge completed")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

**Save this file to**: `scripts/merge_with_polars.py`

**Make executable:**
```bash
chmod +x scripts/merge_with_polars.py
```

**Time**: 5-10 minutes (copy code, save file)

---

## PART 3: EURUSD TEST (8-20 minutes)

### Step 3.1: Execute EURUSD Merge

**Command:**
```bash
python3 scripts/merge_with_polars.py \
    /home/micha/bqx_ml_v3/data/features/checkpoints/eurusd \
    /home/micha/bqx_ml_v3/data/training/training_eurusd.parquet
```

**Expected output:**
```
Polars Merge Tool
Checkpoint dir: /home/micha/bqx_ml_v3/data/features/checkpoints/eurusd
Output path: /home/micha/bqx_ml_v3/data/training/training_eurusd.parquet

Found 668 parquet files in ...
Lazy loading targets.parquet...
  Joining base_bqx_eurusd.parquet...
  Joining base_idx_eurusd.parquet...
  ...
  Progress: 100/667 files joined
  Progress: 200/667 files joined
  ...
Lazy query plan built with 667 joins
Executing optimized query plan (this may take 8-20 minutes)...
Memory usage will be monitored - expect ~20-30GB peak

Merge complete!
  Rows: 100,000
  Columns: 6,500
  Target columns: 49

Writing to /home/micha/bqx_ml_v3/data/training/training_eurusd.parquet...
Output file size: 5.2 GB

✅ SUCCESS - Merge completed
```

**During execution:**
- Monitor memory: `watch -n 10 free -h` (in separate terminal)
- Monitor process: `ps aux | grep merge_with_polars`
- Expected memory peak: 20-30GB (well within 78GB capacity)

**If OOM occurs:**
- Will see error message about memory
- Process will crash
- **Report to EA immediately** → will pivot to BigQuery ETL

**If other error:**
- Check error message
- Report to EA with full stack trace
- EA will diagnose and provide fix or pivot decision

**Time**: 8-20 minutes (target), acceptable up to 30 minutes

---

### Step 3.2: Monitor Memory During Test

**In separate terminal, run:**
```bash
while true; do
    clear
    echo "=== Memory Monitor ==="
    date
    free -h
    echo ""
    echo "=== Polars Process ==="
    ps aux | grep -E "merge_with_polars|polars" | grep -v grep
    sleep 10
done
```

**Watch for:**
- Memory "used" column climbing (expected ~20-30GB peak)
- If "used" exceeds 70GB → alert EA (approaching limit)
- If swap usage starts → alert EA (potential OOM risk)

**Stop monitoring** when merge completes or fails.

---

## PART 4: VALIDATION (5 minutes)

### Step 4.1: Validate Output File

**After merge completes, run validation:**

```python
import polars as pl

# Read output
df = pl.read_parquet('/home/micha/bqx_ml_v3/data/training/training_eurusd.parquet')

# Check dimensions
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")

# Check targets
target_cols = [c for c in df.columns if c.startswith('target_')]
print(f"Target columns: {len(target_cols)}")
print(f"Target column names: {sorted(target_cols)[:5]}...")  # First 5

# Check for all-null columns (data integrity)
null_cols = []
for col in df.columns:
    if df[col].null_count() == len(df):
        null_cols.append(col)

if null_cols:
    print(f"WARNING: {len(null_cols)} columns are all NULL")
    print(f"Sample: {null_cols[:10]}")
else:
    print("✅ No all-NULL columns")

# Check interval_time
print(f"Interval time range: {df['interval_time'].min()} to {df['interval_time'].max()}")
print(f"Unique intervals: {df['interval_time'].n_unique():,}")

print("\n✅ Validation complete")
```

**Save as**: `scripts/validate_polars_output.py`

**Run:**
```bash
python3 scripts/validate_polars_output.py
```

**Expected output:**
```
Rows: 100,000
Columns: 6,500
Target columns: 49
Target column names: ['target_bqx180_h105', 'target_bqx180_h15', ...]
✅ No all-NULL columns
Interval time range: 2024-01-01 00:00:00 to 2024-12-31 23:45:00
Unique intervals: 100,000

✅ Validation complete
```

**Time**: 5 minutes

---

## PART 5: SUCCESS CRITERIA (CE Directive 2255)

**Test passes if ALL of the following are true:**

| Criterion | Target | How to Check |
|-----------|--------|--------------|
| **Installation** | No errors | Polars imports successfully |
| **Execution time** | 8-20 min (up to 30 acceptable) | Time the merge command |
| **Memory peak** | < 40GB | Monitor `free -h` during execution |
| **Row count** | ~100,000 | Validation script output |
| **Column count** | ~6,500 | Validation script output |
| **Target columns** | 49 | Validation script output |
| **No corruption** | No all-NULL columns | Validation script output |
| **File created** | training_eurusd.parquet exists | `ls -lh data/training/` |
| **File size** | ~5GB | `ls -lh data/training/training_eurusd.parquet` |

**If ALL criteria pass**: ✅ **SUCCESS** → Proceed with Polars for 27 pairs

**If ANY criterion fails**: ❌ **FAIL** → Pivot to BigQuery ETL (authorized, no additional approval needed)

---

## PART 6: REPORTING

### Step 6.1: Report Test Results to CE and EA

**After validation completes, send report:**

**File**: `20251211_HHMM_BA-to-CE_POLARS_TEST_RESULTS.md` (copy EA)

**Format:**
```markdown
# BA Report: Polars EURUSD Test Results

**Date**: December 11, 2025 HH:MM UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**CC**: Enhancement Assistant (EA)

---

## TEST RESULT: SUCCESS / FAILED

## Execution Details

**Installation**: SUCCESS / FAILED
- Polars version: X.X.X
- Installation time: X minutes
- Any errors: None / [describe]

**Implementation**: SUCCESS / FAILED
- Merge function created: YES / NO
- Code location: scripts/merge_with_polars.py
- Any errors: None / [describe]

**EURUSD Merge**: SUCCESS / FAILED
- Start time: HH:MM UTC
- End time: HH:MM UTC
- Duration: X minutes
- Memory peak: X GB
- Any errors: None / [describe]

**Output Validation**: PASS / FAIL
- Rows: X (expected ~100,000)
- Columns: X (expected ~6,500)
- Target columns: X (expected 49)
- All-NULL columns: X (expected 0)
- File size: X GB (expected ~5GB)

---

## Success Criteria Assessment

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Installation | No errors | ... | ✅ / ❌ |
| Execution time | 8-30 min | X min | ✅ / ❌ |
| Memory peak | < 40GB | X GB | ✅ / ❌ |
| Row count | ~100K | X | ✅ / ❌ |
| Column count | ~6,500 | X | ✅ / ❌ |
| Target columns | 49 | X | ✅ / ❌ |
| No corruption | 0 NULL cols | X | ✅ / ❌ |
| File created | YES | YES/NO | ✅ / ❌ |
| File size | ~5GB | X GB | ✅ / ❌ |

**Overall**: ALL PASS ✅ / SOME FAIL ❌

---

## Recommendation

[If ALL PASS]
✅ **PROCEED with Polars for 27 remaining pairs**
- Polars proven viable
- All success criteria met
- Ready for 4× parallel rollout

[If ANY FAIL]
❌ **PIVOT to BigQuery ETL**
- Reason: [describe which criterion failed]
- BigQuery ETL ready to execute
- Estimated timeline: 2.8-5.6 hours for 28 pairs
- Cost: $18.48 (within authorized budget)

---

**Awaiting CE/EA decision on next steps.**
```

**Send to:**
- `.claude/sandbox/communications/inboxes/CE/`
- `.claude/sandbox/communications/inboxes/EA/`

---

## PART 7: NEXT STEPS (If Test Succeeds)

### Step 7.1: 27-Pair Rollout with 4× Parallel

**EA will provide detailed execution plan** after test success.

**Overview:**
- Process 4 pairs simultaneously
- 27 pairs ÷ 4 = 6.75 batches → 7 batch slots
- Each batch: 8-20 minutes
- Total: 56-140 minutes (0.9-2.3 hours)

**EA will send:**
- Exact pair groupings for each batch
- Parallel execution code
- Monitoring plan
- Validation checkpoints

**Your role:**
- Execute EA's 27-pair plan
- Monitor progress
- Report status after each batch
- Handle any failures

---

## PART 8: FALLBACK (If Test Fails)

### Step 8.1: Pivot to BigQuery ETL

**If Polars test fails ANY success criterion:**

**Immediate actions:**
1. Report failure to CE and EA with details
2. Stop Polars approach immediately
3. Wait for EA coordination on BigQuery ETL execution
4. EA will provide BigQuery ETL implementation directive
5. Execute BigQuery ETL approach per EA specifications

**BigQuery ETL timeline**: 2.8-5.6 hours for all 28 pairs

**BigQuery ETL cost**: ~$18.48 (within $25 authorized budget)

**Authorization**: Pre-approved by CE (no additional approval needed)

---

## PART 9: ERROR HANDLING

### Common Errors and Solutions

**Error: `ModuleNotFoundError: No module named 'polars'`**
- **Cause**: Polars not installed
- **Solution**: Run `pip install polars` or `pip3 install polars`

**Error: `OutOfMemoryError` or process killed**
- **Cause**: Polars using > 78GB RAM
- **Solution**: Report to EA → immediate pivot to BigQuery ETL

**Error: `FileNotFoundError: targets.parquet`**
- **Cause**: Checkpoint directory missing targets file
- **Solution**: Verify checkpoint directory path, check with QA

**Error: `KeyError: 'interval_time'`**
- **Cause**: Feature file missing interval_time column
- **Solution**: Report file name to EA for investigation

**Error: Merge completes but validation shows 0 rows**
- **Cause**: Data alignment issue or empty join result
- **Solution**: Report to EA → likely pivot to BigQuery ETL

**Any other error:**
- Capture full error message and stack trace
- Report to EA immediately with details
- EA will diagnose and provide fix or pivot decision

---

## PART 10: COORDINATION WITH EA

**EA is monitoring your progress** and will:
- Check your outbox for status updates
- Answer technical questions if you encounter issues
- Validate your test results after completion
- Recommend proceed/pivot to CE based on your results
- Coordinate 27-pair rollout if test succeeds
- Coordinate BigQuery ETL if test fails

**Report to EA if:**
- Installation fails
- Implementation errors
- Execution takes > 30 minutes
- Memory exceeds 60GB during execution
- Output validation fails any criterion
- Any unexpected errors

**EA inbox**: `.claude/sandbox/communications/inboxes/EA/`

---

## TIMELINE EXPECTATIONS

| Phase | Expected Duration | Expected Completion |
|-------|-------------------|---------------------|
| **Phase 1: Installation** | 2 min | 23:07 UTC |
| **Phase 2: Implementation** | 5-10 min | 23:12-23:17 UTC |
| **Phase 3: EURUSD Test** | 8-20 min | 23:20-23:37 UTC |
| **Phase 4: Validation** | 5 min | 23:25-23:42 UTC |
| **Phase 5: Reporting** | 2 min | 23:27-23:44 UTC |

**Total expected completion**: 23:27-23:44 UTC (22-39 minutes from now)

**Conservative estimate**: 23:44 UTC

**Report to CE/EA if exceeding these timelines.**

---

## AUTHORIZATION SUMMARY

**You are FULLY AUTHORIZED to:**
- ✅ Install Polars
- ✅ Implement merge function
- ✅ Execute EURUSD test
- ✅ Validate output
- ✅ Report results
- ✅ Proceed with 27 pairs if test succeeds (per EA's next directive)
- ✅ Execute BigQuery ETL if test fails (per EA coordination)

**No additional approvals needed.** Execute per these specifications.

---

## FINAL CHECKLIST

Before starting, verify:
- [ ] Read and understood all instructions above
- [ ] QA has validated checkpoints (CONFIRMED: 668/668 files approved)
- [ ] Checkpoint directory exists: `/home/micha/bqx_ml_v3/data/features/checkpoints/eurusd`
- [ ] Output directory exists or will be created: `/home/micha/bqx_ml_v3/data/training/`
- [ ] Sufficient disk space: ~10GB needed for output file
- [ ] Memory monitoring terminal ready
- [ ] Ready to report results to CE and EA

---

**EXECUTE IMMEDIATELY. ALL SPECIFICATIONS PROVIDED. FULL AUTHORIZATION GRANTED.**

---

**Enhancement Assistant (EA)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**CE Authorization**: Directive 2255 + 2305
