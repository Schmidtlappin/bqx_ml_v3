# CE DIRECTIVE: Confirm Serverless Architecture - Zero VM Dependencies

**Date**: December 12, 2025 21:12 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: CRITICAL Confirmation Required - Bifurcated Architecture is 100% Serverless
**Priority**: P0-CRITICAL (PREREQUISITE FOR EXECUTION)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## 🚨 CRITICAL CONFIRMATION REQUIRED

**Before executing EURUSD Job 1**, confirm that the bifurcated architecture is **100% serverless** with **ZERO VM dependencies**.

**User Mandate**: Extraction and merge processes must be **fully contained** in Cloud Run + GCS, completely independent of VM system resources.

---

## CONFIRMATION CHECKLIST

### Job 1 (bqx-ml-extract) - Extraction Process

**Required Confirmations**:

1. ✅ **Execution Environment**:
   - Runs ONLY in Cloud Run container (NOT on VM)
   - No VM processes spawned
   - No VM filesystem access

2. ✅ **Data Sources**:
   - Reads ONLY from BigQuery (cloud-based)
   - No VM file reads
   - No VM database connections

3. ✅ **Data Outputs**:
   - Writes ONLY to GCS (`gs://bqx-ml-staging/checkpoints/`)
   - No VM filesystem writes (no `/home/micha/...` paths)
   - No `/tmp/` local storage (ephemeral or otherwise)

4. ✅ **Dependencies**:
   - All Python libraries in Cloud Run container
   - No VM-installed packages required
   - No VM environment variables (except Cloud Run service account)

5. ✅ **Compute Resources**:
   - Uses ONLY Cloud Run allocated resources (4 vCPUs, 8 GB)
   - No VM CPU usage
   - No VM memory usage
   - No VM disk I/O

---

### Job 2 (bqx-ml-merge) - Merge Process

**Required Confirmations**:

1. ✅ **Execution Environment**:
   - Runs ONLY in Cloud Run container (NOT on VM)
   - No VM processes spawned
   - No VM filesystem access

2. ✅ **Data Sources**:
   - Reads ONLY from GCS (`gs://bqx-ml-staging/checkpoints/`)
   - BigQuery cloud merge (serverless, NOT on VM)
   - No VM file reads

3. ✅ **Data Processing**:
   - BigQuery performs merge (cloud-based, NOT on VM)
   - No Polars/DuckDB local merge on Cloud Run
   - No VM-based processing

4. ✅ **Data Outputs**:
   - Writes ONLY to GCS (`gs://bqx-ml-output/training_{pair}.parquet`)
   - No VM filesystem writes
   - No local file creation

5. ✅ **Compute Resources**:
   - Uses ONLY Cloud Run allocated resources (1 vCPU, 2 GB)
   - BigQuery uses serverless compute (NOT VM)
   - No VM CPU usage
   - No VM memory usage

---

## VERIFICATION COMMANDS

**Before Job 1 Execution**, verify:

```bash
# 1. Check Cloud Run job configuration (NO VM references)
gcloud run jobs describe bqx-ml-extract --region us-central1 --format=json

# Verify:
# - image: gcr.io/bqx-ml/bqx-ml-extract:latest (NOT VM-based)
# - serviceAccount: bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
# - NO volumes mounted from VM
# - NO environment variables pointing to VM paths
```

```bash
# 2. Check Job 1 entrypoint script
cat scripts/extract_only.sh

# Verify:
# - Output path: gs://bqx-ml-staging/checkpoints/{pair}/ (NOT /home/micha/...)
# - No VM filesystem commands (no mkdir -p /home/..., no cp to /home/...)
# - All operations use GCS URIs (gs://...)
```

```bash
# 3. Check Job 2 entrypoint script
cat scripts/merge_only.sh

# Verify:
# - Input path: gs://bqx-ml-staging/checkpoints/{pair}/ (NOT VM filesystem)
# - Output path: gs://bqx-ml-output/training_{pair}.parquet (NOT VM filesystem)
# - Uses scripts/merge_in_bigquery.py (BigQuery cloud merge, NOT Polars local)
# - No VM filesystem commands
```

```bash
# 4. Check merge_in_bigquery.py implementation
grep -E "(gs://|bq load|bq query|CREATE TABLE|SELECT.*FROM)" scripts/merge_in_bigquery.py

# Verify:
# - Loads from GCS URIs (gs://bqx-ml-staging/checkpoints/...)
# - Uses BigQuery SQL (bq query --use_legacy_sql=false ...)
# - Exports to GCS (bq extract ... gs://bqx-ml-output/...)
# - NO local file operations (no open(...), no pd.read_parquet(/tmp/...))
```

---

## ANTI-PATTERNS (MUST NOT BE PRESENT)

**Reject execution if ANY of these are found**:

❌ **VM Filesystem Paths**:
- `/home/micha/bqx_ml_v3/...`
- `/home/micha/data/...`
- Any absolute paths on VM

❌ **VM Process Execution**:
- SSH to VM from Cloud Run
- Subprocess calls to VM scripts
- VM-based Polars/DuckDB merge

❌ **VM Resource Usage**:
- NFS mounts from VM
- VM-based databases (PostgreSQL on VM)
- VM CPU/memory allocation

❌ **Local File Operations** (in Cloud Run):
- Writing to `/tmp/` and keeping files there
- Using local Polars merge (should be BigQuery cloud merge)
- Downloading all checkpoints to Cloud Run `/tmp/` before processing

---

## REQUIRED CONFIRMATION FORMAT

**Subject**: `20251212_[TIME]_BA-to-CE_SERVERLESS_CONFIRMATION.md`

**Content**:

```markdown
# BA CONFIRMATION: 100% Serverless Architecture - Zero VM Dependencies

## JOB 1 (bqx-ml-extract) ✅

**Execution Environment**: ✅ Cloud Run ONLY (no VM)
**Data Sources**: ✅ BigQuery ONLY (no VM files)
**Data Outputs**: ✅ GCS ONLY (`gs://bqx-ml-staging/checkpoints/`)
**Dependencies**: ✅ Container-based ONLY (no VM packages)
**Compute Resources**: ✅ Cloud Run ONLY (4 vCPUs, 8 GB, no VM CPU/memory)

**Verification**:
- Entrypoint: /workspace/scripts/extract_only.sh
- Output path: gs://bqx-ml-staging/checkpoints/{pair}/
- No VM filesystem references: CONFIRMED
- No VM process execution: CONFIRMED

## JOB 2 (bqx-ml-merge) ✅

**Execution Environment**: ✅ Cloud Run ONLY (no VM)
**Data Sources**: ✅ GCS + BigQuery ONLY (no VM files)
**Data Processing**: ✅ BigQuery cloud merge (no VM-based Polars)
**Data Outputs**: ✅ GCS ONLY (`gs://bqx-ml-output/training_{pair}.parquet`)
**Compute Resources**: ✅ Cloud Run (1 vCPU, 2 GB) + BigQuery serverless (no VM)

**Verification**:
- Entrypoint: /workspace/scripts/merge_only.sh
- Merge approach: BigQuery cloud merge (scripts/merge_in_bigquery.py)
- Input path: gs://bqx-ml-staging/checkpoints/{pair}/
- Output path: gs://bqx-ml-output/training_{pair}.parquet
- No VM filesystem references: CONFIRMED
- No local Polars merge: CONFIRMED (using BigQuery)

## OVERALL CONFIRMATION ✅

**100% Serverless**: ✅ CONFIRMED
**Zero VM Dependencies**: ✅ CONFIRMED
**Fully Cloud-Based**: ✅ CONFIRMED

**VM Resource Usage During Execution**:
- CPU: 0% (all processing in Cloud Run + BigQuery)
- Memory: 0% (no VM memory allocation)
- Disk I/O: 0% (no VM filesystem access)

**Ready for Execution**: ✅ YES - Architecture is 100% serverless
```

---

## AUTHORIZATION CONTINGENCY

**IF 100% serverless confirmed**:
- ✅ Proceed with EURUSD Job 1 execution at 21:15 UTC
- ✅ Monitor execution (no VM resource usage expected)
- ✅ Validate serverless assumption during execution

**IF ANY VM dependencies detected**:
- ❌ HALT execution immediately
- ❌ Report to CE with specific VM dependency details
- ❌ Await CE directive on remediation approach

---

## WHY THIS MATTERS

**User Mandate**: Serverless deployment to eliminate:
1. VM maintenance costs ($82/month persistent disk)
2. VM uptime requirements (must be running for 33+ hours)
3. VM failure points (disk failures, SSH disconnections)
4. Manual VM operations (starting/stopping, monitoring)

**Bifurcated Architecture Goal**:
- Job 1: Cloud Run extracts from BigQuery → GCS checkpoints (no VM)
- Job 2: Cloud Run orchestrates BigQuery merge → GCS training file (no VM)
- VM is COMPLETELY IDLE during entire execution

**Validation**:
- During EURUSD execution, VM should show 0% CPU, 0% memory usage
- All costs should be Cloud Run + BigQuery (no VM compute costs)

---

## TIMELINE

**Required Response**: BEFORE Job 1 execution (by 21:14 UTC)

**Execution Sequence**:
1. **21:10-21:12 UTC**: Container builds complete
2. **21:12-21:14 UTC**: BA sends serverless confirmation ← **THIS DIRECTIVE**
3. **21:14-21:15 UTC**: CE reviews confirmation, authorizes Job 1 execution
4. **21:15 UTC**: Job 1 execution starts (if serverless confirmed)

**Deadline**: **21:14 UTC** (2 minutes for confirmation)

---

## COORDINATION

**EA**: Will monitor costs (should be Cloud Run + BigQuery ONLY, no VM costs)
**QA**: Will validate output quality (serverless vs VM should be identical)
**CE**: Will review confirmation before authorizing execution

---

**Chief Engineer (CE)**

**Critical Confirmation**: Bifurcated architecture must be 100% serverless with ZERO VM dependencies

**Deadline**: 21:14 UTC (2 min)

**Authorization**: EURUSD execution contingent on serverless confirmation

---

**END OF DIRECTIVE**
