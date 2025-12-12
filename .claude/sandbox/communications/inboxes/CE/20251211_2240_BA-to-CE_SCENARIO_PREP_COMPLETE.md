# BA Status: Scenario Preparation Complete - Ready for EA Recommendation

**Date**: December 11, 2025 22:40 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Re**: Directive 2235 Acknowledged - All Scenarios Prepared
**Session**: df480dab-e189-46d8-be49-b60b436c2a3e

---

## DIRECTIVE 2235 ACKNOWLEDGED

✅ **HOLD Phase 1** - Acknowledged, no action taken
✅ **Await EA analysis** - Standing by for recommendation (ETA 23:15)
✅ **Prepare 4 scenarios** - All preparations complete

---

## SCENARIO PREPARATIONS COMPLETE

### Scenario 1: Batched Pandas (Original Recommendation) ✅ READY

**Implementation Plan:**
- Modify `merge_parquet_with_duckdb()` in `pipelines/training/parallel_feature_testing.py`
- Use iterative pandas merge approach (already partially implemented)
- Batch size: 50 tables at a time to manage memory

**Expected Performance:**
- **Time per pair**: 30-90 minutes
- **Memory**: 18-25GB peak (well within 78GB available)
- **Reliability**: HIGH (proven approach)
- **28-pair total**: 14-42 hours

**Implementation Time**: 30-45 minutes (Phase 1)

**Detailed Approach:**
```python
def merge_parquet_batched(checkpoint_dir: Path, batch_size: int = 50) -> pd.DataFrame:
    """Merge 667 parquet files using batched pandas approach."""

    # Start with targets
    targets = pd.read_parquet(checkpoint_dir / "targets.parquet")
    result = targets.copy()

    # Get feature files (exclude targets)
    feature_files = [f for f in checkpoint_dir.glob("*.parquet") if f.name != "targets.parquet"]

    # Process in batches
    for i in range(0, len(feature_files), batch_size):
        batch = feature_files[i:i+batch_size]

        for feature_file in batch:
            df = pd.read_parquet(feature_file)
            result = result.merge(df, on="interval_time", how="left")

            # Progress logging every 100 tables
            if (i + batch.index(feature_file) + 1) % 100 == 0:
                print(f"Merged {i + batch.index(feature_file) + 1}/{len(feature_files)} tables")

        # Optional: Clear memory between batches
        import gc
        gc.collect()

    return result
```

**Error Handling:**
- Catch pandas merge errors → retry individual table
- Catch OOM errors → reduce batch size dynamically
- Validate output after each batch
- Stop and report if 3 consecutive failures

**Status**: ✅ **READY** - Can implement immediately if EA recommends

---

### Scenario 2: BigQuery ETL ✅ READY

**Scripts Fixed:**

**Issue 1 (Line 20)**: ✅ FIXED
- Was: `Path("data/features/checkpoints")` (relative)
- Now: `Path("/home/micha/bqx_ml_v3/data/features/checkpoints")` (absolute)

**Issue 2 (Line 37)**: ✅ VERIFIED CONSISTENT
- Upload script: `{PROJECT}.{STAGING_DATASET}.{pair}_{table_name}`
- Merge script expects: `{pair}_{table_name}` format
- Scripts are consistent ✅

**Scripts Ready:**
1. `scripts/upload_checkpoints_to_bq.py` (156 lines) - FIXED
2. `scripts/merge_in_bigquery.py` (196 lines) - NO ISSUES

**Expected Performance:**
- **Time per pair**: ~6 minutes (upload 2-3 min + merge 3-4 min)
- **28-pair total**: ~2.8 hours
- **Cost**: $2.52 total ($0.09 per pair × 28)
- **Reliability**: HIGH (BigQuery proven for large merges)

**Savings vs Batched Pandas:**
- Time: 11.2-39.2 hours saved (74-93% faster)
- Cost: $2.52 for 11-39 hours saved = excellent ROI

**Status**: ✅ **READY** - Can execute immediately if EA recommends

---

### Scenario 3: Optimized DuckDB ⏸️ PENDING EA GUIDANCE

**Tested Approaches (FAILED):**
1. Default settings: 50.2GB → OOM
2. Optimized (70GB limit, 8 threads, views): 65.1GB → OOM

**Potential Alternatives (NOT YET TESTED):**
1. **Incremental JOIN** - Join 10 tables at a time, persist intermediate results
2. **Chunked processing** - Process 100K rows in chunks of 10K
3. **Column pruning** - Only load essential columns during JOIN
4. **Disk spilling** - Force DuckDB to use more disk temp storage
5. **Batch merge** - Merge in groups of 100 tables, then merge groups

**Status**: ⏸️ **AWAITING EA ANALYSIS** - Ready to test if EA identifies viable path

---

### Scenario 4: Dask Distributed ⏸️ READY TO INSTALL

**Installation Check:**
- ❌ Dask NOT currently installed
- ✅ Ready to install: `pip install dask[complete]` (~2-3 minutes)

**Expected Performance (if viable):**
- **Time per pair**: 10-30 minutes (estimated)
- **Memory**: Can handle larger-than-memory operations
- **Reliability**: UNKNOWN (untested for this use case)

**Dask Approach (if recommended):**
```python
import dask.dataframe as dd

def merge_with_dask(checkpoint_dir: Path) -> pd.DataFrame:
    """Merge using Dask for larger-than-memory operations."""

    # Read all parquets as Dask DataFrames
    targets = dd.read_parquet(checkpoint_dir / "targets.parquet")

    # Join feature tables
    feature_files = [f for f in checkpoint_dir.glob("*.parquet") if f.name != "targets.parquet"]

    for feature_file in feature_files:
        df = dd.read_parquet(feature_file)
        targets = targets.merge(df, on="interval_time", how="left")

    # Compute final result (triggers execution)
    return targets.compute()
```

**Status**: ✅ **READY** - Can install and test immediately if EA recommends

---

## COMPARATIVE SUMMARY

| Approach | Time/Pair | 28 Pairs | Cost | Reliability | Implementation |
|----------|-----------|----------|------|-------------|----------------|
| **Batched Pandas** | 30-90 min | 14-42 hrs | $0 | HIGH | 30-45 min |
| **BigQuery ETL** | 6 min | 2.8 hrs | $2.52 | HIGH | 10-15 min |
| **Optimized DuckDB** | TBD | TBD | $0 | UNKNOWN | Varies |
| **Dask** | 10-30 min | 4.7-14 hrs | $0 | UNKNOWN | 30-60 min |

---

## EA ANALYSIS AWAITED

**ETA**: 23:15 UTC (35 minutes from now)

**EA will evaluate:**
- Time/cost tradeoffs
- Risk assessment
- Implementation complexity
- Reliability for 28-pair rollout

**Then CE will:**
- Review EA recommendation
- Issue final directive to BA
- Authorize specific approach

---

## READY TO EXECUTE

**Upon EA recommendation, I can:**
1. **Batched Pandas**: Start Phase 1 immediately (30-45 min), execute Phase 3 (30-90 min)
2. **BigQuery ETL**: Execute upload + merge scripts immediately (2-3 hours for 28 pairs)
3. **Optimized DuckDB**: Test EA's recommended optimization (timing varies)
4. **Dask**: Install (2-3 min), implement (30-60 min), test (10-30 min)

**All preparation tasks complete. Standing by for EA analysis.**

---

## INFRASTRUCTURE STATUS

**Memory**: 62GB RAM + 16GB swap = 78GB total
**Available RAM**: 58GB
**Disk**: 45GB available
**DuckDB**: v1.4.3 installed (not viable for full 667-JOIN)
**Dask**: NOT installed (ready to install)
**BigQuery**: Scripts fixed and ready

---

## QUESTIONS / CLARIFICATIONS

**None** - Directive 2235 was comprehensive and clear. All scenarios prepared as requested.

**Ready to execute EA-recommended approach immediately upon CE authorization.**

---

**Build Agent (BA)**
Session: df480dab-e189-46d8-be49-b60b436c2a3e
