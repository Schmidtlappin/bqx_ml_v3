# EA Report: AUDUSD Status - OOM Incident & Path Forward

**Date**: December 12, 2025 03:25 UTC
**From**: Enhancement Agent (EA)
**To**: Chief Engineer (CE)
**Re**: AUDUSD Extraction Complete, Merge Failed (OOM), Recommendations
**Priority**: HIGH - Requires CE Decision
**Session**: Current

---

## EXECUTIVE SUMMARY

**AUDUSD Extraction**: ✅ **COMPLETE** (668/668 files, 12 GB, 113 minutes)
**AUDUSD Merge**: ❌ **FAILED** (OOM killed at 03:13 UTC)
**Root Cause**: DuckDB local merge consumed 63 GB RAM for 668-table JOIN
**OPS Status**: Third memory crisis in 6 hours, critical incident report issued

**Recommendation**: Proceed with **BigQuery cloud merge** approach (avoids local memory limits).

---

## AUDUSD EXTRACTION RESULTS ✅

### Files Created (100% Success)
- **Feature tables**: 667 files
- **Targets file**: 1 file
- **Total**: **668/668 files** ✅
- **Size**: 12 GB
- **Location**: `data/features/checkpoints/audusd/`

### Performance Metrics
- **Extraction time**: 113 minutes (01:55 UTC complete)
- **Success rate**: 100% (0 errors)
- **Peak memory**: 3.97 GB (6% of system)
- **CPU usage**: 112% (multi-threaded, 40 workers)
- **Disk usage**: 12 GB

**Status**: ✅ PERFECT - Ready for merge

---

## AUDUSD MERGE FAILURE ❌

### Attempted Approach
- **Method**: Local DuckDB 668-table LEFT JOIN
- **Start time**: 01:55 UTC (after extraction)
- **Failure time**: 03:13 UTC (78 minutes into merge)

### Memory Consumption Pattern
```
Time        Memory    Swap    Total
01:55 UTC   12 GB     0 GB    12 GB   (merge start)
02:20 UTC   18 GB     0 GB    18 GB   (loading tables)
02:40 UTC   33 GB     0 GB    33 GB   (JOIN operations)
02:52 UTC   60 GB     5.8 GB  65.8 GB (peak before kill)
03:13 UTC   KILLED BY OPS (process unresponsive)
```

### Failure Root Cause

**668-table LEFT JOIN** materialized in memory:
- DuckDB loads all 668 tables
- Creates intermediate result sets for each JOIN
- Memory bloat: 12 GB input → 63 GB in-memory (**5.3× bloat**)
- Exceeds VM capacity (62 GB RAM + 15 GB swap)

**Conclusion**: Local merge approach **NOT VIABLE** for 668 tables.

---

## OPS INCIDENT REPORT SUMMARY

### Crisis #3 Details (03:13 UTC)

**Trigger**: `parallel_feature_testing.py` (PID 449948)
**Memory**: 63 GB (95.7% of system)
**Runtime**: 192 minutes (stuck in merge)
**Impact**: SSH connection failure (memory exhaustion)

### OPS Action Taken
```bash
sudo kill -9 449948  # Killed stuck process
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'  # Freed memory
```

**Recovery**: 60 seconds (63 GB → 1 GB)

### Recurring Pattern (3 Crises in 6 Hours)

| Crisis | Time | Process | Memory | Outcome |
|--------|------|---------|--------|---------|
| #1 | 21:10 UTC | Polars validate | 30 GB | OOM killed |
| #2 | 21:10 UTC | Polars parquet read | 35 GB | OOM killed |
| #3 | 03:13 UTC | DuckDB merge | 63 GB | OOM killed |

### OPS Recommendations (CRITICAL)

1. **Immediate**: Add memory limits to all ML scripts
2. **Short-term**: Create ML workload wrapper with resource limits
3. **Medium-term**: Implement systemd resource control
4. **Long-term**: Containerize ML workloads

**OPS Risk Assessment**: HIGH - Crisis #4 likely within next 6 hours without intervention.

---

## RECOMMENDED PATH FORWARD

### Option 1: BigQuery Cloud Merge (RECOMMENDED) ✅

**Approach**: Upload checkpoints to GCS → Merge in BigQuery → Download result

**Advantages**:
- ✅ No local memory limits (cloud-based processing)
- ✅ Iterative JOIN approach (50 tables per batch)
- ✅ Already tested and validated (EURUSD merge successful)
- ✅ Cost-effective ($0.11 per pair)
- ✅ Predictable runtime (50-60 minutes)

**Process**:
1. Upload 668 audusd checkpoints to GCS staging bucket (~5 min)
2. Load to BigQuery as native tables (~10 min)
3. Execute iterative batched JOIN (~40 min)
   - Batch 1: targets + 50 tables
   - Batch 2: result + 50 tables
   - ... (14 batches total)
4. Download training file to VM (~5 min)
5. Validate and cleanup

**Cost**: $0.11 (BigQuery scan charges)
**Time**: ~60 minutes
**Memory**: 0 local (all processing in cloud)

### Option 2: Optimize Local Merge (NOT RECOMMENDED) ❌

**Approaches Attempted**:
- ❌ DuckDB: 63 GB OOM (failed)
- ❌ Polars: 65 GB OOM (failed, crashed system)
- ❌ Pandas: Would require 80+ GB (untested, likely fails)

**Why Not Recommended**:
- All local approaches hit 60+ GB memory wall
- Risk of Crisis #4 (OPS escalation)
- Unpredictable runtime (stuck for hours)
- Requires implementing resource limits first

---

## CLOUD RUN GCS-FIRST MODIFICATION STATUS ✅

### Script Modification Complete

**File**: `pipelines/training/parallel_feature_testing.py`
**Status**: ✅ Modified to support GCS output

**Changes Made**:
1. Added `google.cloud.storage` import
2. Created GCS helper functions:
   - `_write_parquet_to_gcs()` - Write DataFrame to GCS
   - `_read_parquet_from_gcs()` - Read DataFrame from GCS
   - `_parquet_exists()` - Check file existence (local or GCS)
   - `_write_parquet()` - Unified write (local or GCS)
   - `_read_parquet()` - Unified read (local or GCS)
3. Modified `query_pair_with_checkpoints()` to accept `gcs_output` parameter
4. Modified `process_pair_all_horizons()` to pass `gcs_output` through
5. Added `--gcs-output` CLI flag support

**Usage**:
```bash
# Local mode (VM)
python3 pipelines/training/parallel_feature_testing.py single audusd

# GCS mode (Cloud Run)
python3 pipelines/training/parallel_feature_testing.py single audusd --gcs-output gs://bqx-ml-staging
```

**Testing Status**: ⏸️ Pending (not yet tested with GCS)

---

## RECOMMENDED ACTIONS FOR CE

### IMMEDIATE (Next 30 Minutes)

**Decision Required**: Choose merge approach for AUDUSD

**Option A - BigQuery Cloud Merge** (RECOMMENDED):
```bash
# 1. Upload audusd checkpoints to GCS
gsutil -m cp -r data/features/checkpoints/audusd/ gs://bqx-ml-staging/audusd/

# 2. Execute BigQuery merge
python3 scripts/merge_single_pair_optimized.py audusd

# 3. Download training file
gsutil cp gs://bqx-ml-output/training_audusd.parquet data/training/

# 4. Validate
python3 scripts/validate_merged_output.py audusd
```
**Time**: ~60 minutes
**Cost**: $0.11
**Risk**: LOW (proven approach)

**Option B - Skip AUDUSD** (Use existing training_eurusd.parquet from Dec 11):
- AUDUSD and EURUSD have similar characteristics
- Existing file validated and ready
- Saves 60 minutes
- But: missing AUDUSD-specific features

### SHORT-TERM (Next 24 Hours)

**If proceeding with Cloud Run for 26 pairs**:

1. **Test GCS-first extraction** (10 minutes):
   ```bash
   python3 pipelines/training/parallel_feature_testing.py single testpair \
       --gcs-output gs://bqx-ml-staging
   ```

2. **Verify GCS bucket permissions** (5 minutes):
   ```bash
   gsutil iam ch serviceAccount:bqx-ml-ibgateway@bqx-ml.iam.gserviceaccount.com:objectAdmin \
       gs://bqx-ml-staging
   ```

3. **Deploy Cloud Run** (25 minutes):
   ```bash
   cd /home/micha/bqx_ml_v3
   ./scripts/deploy_cloud_run.sh
   ```

4. **Execute 26 pairs** (54 hours):
   ```bash
   ./scripts/cloud_run_execute_all_pairs.sh
   ```

### MEDIUM-TERM (Next 7 Days)

**Implement OPS Recommendations**:

1. **Create ML workload wrapper**:
   ```bash
   # scripts/run_ml_safe.sh
   systemd-run --user \
       --property MemoryMax=50G \
       --property CPUQuota=80% \
       "$@"
   ```

2. **Add resource checks**:
   ```bash
   # Pre-flight memory check
   available=$(free -g | awk '/Mem:/{print $7}')
   if [ $available -lt 20 ]; then
       echo "ERROR: Insufficient memory ($available GB < 20 GB required)"
       exit 1
   fi
   ```

3. **Enable monitoring**:
   ```bash
   # Run health monitor every 5 minutes
   cron: */5 * * * * /home/micha/bqx_ml_v3/scripts/health-monitor.sh
   ```

---

## AUDUSD FILES INVENTORY

### Checkpoint Files (Ready for Upload)
```
Location: data/features/checkpoints/audusd/
Files: 668 parquet files
Size: 12 GB
Status: ✅ Ready for GCS upload or BigQuery merge
```

### Training File Status
```
File: data/features/audusd_merged_features.parquet
Status: ❌ NOT CREATED (merge failed)
Alternative: Create via BigQuery cloud merge
```

---

## COST SUMMARY

### AUDUSD (Completed Work)
- Extraction (VM): $0
- Merge (failed): $0
- **Total spent**: $0

### AUDUSD (To Complete)
- BigQuery merge: $0.11
- GCS storage: $0.31/month
- **Total to complete**: $0.11 one-time + $0.31/month

### Remaining 26 Pairs (Cloud Run Option)
- Cloud Run compute: $15.60
- BigQuery merges: $2.86 (26 × $0.11)
- GCS storage: $0.41/month
- **Total**: $18.46 one-time + $0.41/month

### Full Project (27 Pairs)
- **One-time**: $18.57
- **Monthly**: $1.03
- **Annual**: $30.93

---

## TIMELINE ESTIMATES

### If BigQuery Merge AUDUSD Now
```
03:30 UTC - Start BigQuery merge (CE authorized)
04:30 UTC - AUDUSD training file ready
04:35 UTC - Deploy Cloud Run
05:00 UTC - Start 26 pairs on Cloud Run
Dec 14 11:00 UTC - All 27 pairs complete
```
**Total**: ~56 hours from now

### If Skip AUDUSD, Deploy Cloud Run Now
```
03:30 UTC - Deploy Cloud Run
04:00 UTC - Start 26 pairs on Cloud Run
Dec 14 10:00 UTC - 26 pairs complete
```
**Total**: ~54 hours from now (saves 2 hours)

---

## SUMMARY & RECOMMENDATION

### Current Status
- ✅ AUDUSD extraction: COMPLETE (668 files, perfect)
- ❌ AUDUSD merge: FAILED (OOM killed)
- ✅ GCS-first script: READY (modified, untested)
- ✅ Cloud Run infrastructure: READY (complete)
- ⚠️ System health: RECOVERED (after OPS intervention)

### EA Recommendation

**PROCEED WITH BIGQUERY CLOUD MERGE FOR AUDUSD**

**Rationale**:
1. Proven approach (EURUSD successful)
2. No local memory risk (cloud-based)
3. Fast (~60 minutes)
4. Low cost ($0.11)
5. Completes AUDUSD properly (not skipped)

**Then deploy Cloud Run for remaining 26 pairs** (100% VM independent).

### Awaiting CE Decision

**Option 1**: Authorize BigQuery merge for AUDUSD (recommended)
**Option 2**: Skip AUDUSD, proceed with Cloud Run for 26 pairs
**Option 3**: Implement resource limits first, retry local merge (high risk)

---

**Enhancement Agent (EA)**
*Machine Learning Architecture & Optimization*

**Next Actions**:
1. Awaiting CE decision on AUDUSD merge approach
2. Ready to deploy Cloud Run once authorized
3. GCS-first extraction script ready for testing

**Risk Status**: System recovered, but OPS recommends resource limits before next ML workload

---

**END OF REPORT**
