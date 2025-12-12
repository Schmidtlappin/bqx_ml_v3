# CE URGENT CLARIFICATION: Bifurcated Architecture SUPERSEDES Single-Job Approach

**Date**: December 12, 2025 21:00 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: URGENT - Bifurcated Architecture SUPERSEDES Single Cloud Run Job
**Priority**: P0-CRITICAL (STOP CURRENT IMPLEMENTATION)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## 🚨 URGENT: STOP CURRENT IMPLEMENTATION

**BA**: Your 20:57 acknowledgment shows you're implementing a **SINGLE Cloud Run job** with BigQuery merge.

**CRITICAL**: This approach is **SUPERSEDED** by the bifurcated architecture directive sent at 20:20 UTC.

**Required Action**: STOP current implementation, pivot to bifurcated (two-job) architecture.

---

## DIRECTIVE TIMELINE (CRITICAL)

### Directive 1: BigQuery Merge Required (20:15 UTC)
**File**: `20251212_2015_CE-to-BA_CRITICAL_BIGQUERY_MERGE_REQUIRED.md`
**Content**: Use BigQuery cloud merge (not Polars) due to 56 GB memory requirement
**Status**: ✅ Acknowledged by BA at 20:57 UTC

### Directive 2: Bifurcated Architecture (20:20 UTC) ← **SUPERSEDES ALL PREVIOUS**
**File**: `20251212_2020_CE-to-BA_BIFURCATED_ARCHITECTURE_DIRECTIVE.md`
**Content**: Split into TWO separate Cloud Run jobs (extract + merge)
**Status**: ⚠️ **NOT ACKNOWLEDGED** - BA implementing wrong approach

### Directive 3: Cleanup (20:25 UTC)
**File**: `20251212_2025_CE-to-BA_CLEANUP_DEPRECATED_INFRASTRUCTURE.md`
**Content**: Delete old Cloud Run jobs/images before bifurcated deployment
**Status**: ⚠️ **NOT ACKNOWLEDGED**

---

## WHAT CHANGED

### Your Current Approach (WRONG)
**Architecture**: SINGLE Cloud Run job (`bqx-ml-pipeline`)
- Stage 1: BigQuery extraction → GCS checkpoints (60-70 min)
- Stage 2: BigQuery cloud merge → training file (10-15 min)
- **Total**: 75 min in ONE job

### Required Approach (BIFURCATED)
**Architecture**: TWO independent Cloud Run jobs
- **Job 1** (`bqx-ml-extract`): BigQuery extraction → GCS checkpoints (70 min)
- **Job 2** (`bqx-ml-merge`): GCS checkpoints → BigQuery merge → training file (15 min)
- **Total**: 85 min across TWO separate jobs

---

## WHY BIFURCATED ARCHITECTURE

### Rationale (from 20:20 directive)

1. **Failure Isolation**: If merge fails, re-run only Job 2 (saves 70 min)
2. **Resource Optimization**:
   - Job 1: 4 vCPUs, 8 GB RAM (I/O-intensive)
   - Job 2: 1 vCPU, 2 GB RAM (orchestration)
3. **Cost Savings**: $0.85/pair vs $0.93/pair (saves $2.24 for 28 pairs)
4. **Decoupling**: Jobs run independently, checkpoints persist in GCS
5. **Testing Flexibility**: Extract once, test multiple merge strategies

---

## CORRECTED IMPLEMENTATION PLAN

### Phase 0: Cleanup (21:00-21:10 UTC, 10 min)

**Per directive 20251212_2025**:
```bash
# Delete old single-job infrastructure
gcloud run jobs list --region us-central1
gcloud run jobs delete bqx-ml-pipeline --region us-central1 --quiet || true
gcloud container images delete gcr.io/bqx-ml/bqx-ml-pipeline:latest --quiet || true
```

---

### Phase 1: Create Extraction Scripts (21:10-21:40 UTC, 30 min)

**File 1**: `scripts/extract_only.sh` (NEW)
```bash
#!/bin/bash
# Job 1: BigQuery extraction to GCS checkpoints
# CE Directive 2025-12-12 20:20: Bifurcated architecture

PAIR="${1:-eurusd}"
CHECKPOINT_DIR="gs://bqx-ml-staging/checkpoints/${PAIR}"

echo "=== JOB 1: EXTRACT ONLY ==="
echo "Pair: ${PAIR}"
echo "Output: ${CHECKPOINT_DIR}"

# Execute extraction
python3 /workspace/pipelines/training/parallel_feature_testing.py single "${PAIR}" \
  --gcs-output gs://bqx-ml-staging

# Verify checkpoint count
file_count=$(gsutil ls "${CHECKPOINT_DIR}/*.parquet" 2>/dev/null | wc -l)
echo "Checkpoints created: ${file_count}"

if [ "${file_count}" -lt 660 ]; then
  echo "❌ FAILED: Expected 660-670 checkpoints, got ${file_count}"
  exit 1
fi

echo "✅ JOB 1 COMPLETE: ${file_count} checkpoints in GCS"
```

**File 2**: `scripts/merge_only.sh` (NEW)
```bash
#!/bin/bash
# Job 2: BigQuery merge from GCS checkpoints
# CE Directive 2025-12-12 20:20: Bifurcated architecture

PAIR="${1:-eurusd}"

echo "=== JOB 2: MERGE ONLY ==="
echo "Pair: ${PAIR}"
echo "Input: gs://bqx-ml-staging/checkpoints/${PAIR}/"
echo "Output: gs://bqx-ml-output/training_${PAIR}.parquet"

# Execute BigQuery cloud merge
python3 /workspace/scripts/merge_in_bigquery.py "${PAIR}" || {
  echo "❌ JOB 2 FAILED: BigQuery merge error"
  exit 1
}

echo "✅ JOB 2 COMPLETE: Training file in GCS"
```

---

### Phase 2: Create Dockerfiles (21:40-22:00 UTC, 20 min)

**File 1**: `Dockerfile.extract` (NEW)
```dockerfile
FROM python:3.10-slim
WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy extraction code
COPY pipelines/ /workspace/pipelines/
COPY scripts/extract_only.sh /workspace/scripts/

# Set entrypoint
ENTRYPOINT ["/workspace/scripts/extract_only.sh"]
```

**File 2**: `Dockerfile.merge` (NEW)
```dockerfile
FROM python:3.10-slim
WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy merge code
COPY scripts/merge_in_bigquery.py /workspace/scripts/
COPY scripts/merge_only.sh /workspace/scripts/

# Set entrypoint
ENTRYPOINT ["/workspace/scripts/merge_only.sh"]
```

---

### Phase 3: Build Containers (22:00-22:20 UTC, 20 min)

```bash
# Build Job 1 (extract) container
gcloud builds submit --config cloudbuild-extract.yaml --region us-central1

# Build Job 2 (merge) container
gcloud builds submit --config cloudbuild-merge.yaml --region us-central1
```

**Expected**: 10 min per build (parallel if possible)

---

### Phase 4: Deploy Cloud Run Jobs (22:20-22:40 UTC, 20 min)

**Job 1: Extract**
```bash
gcloud run jobs create bqx-ml-extract \
  --image gcr.io/bqx-ml/bqx-ml-extract:latest \
  --region us-central1 \
  --cpu 4 \
  --memory 8Gi \
  --max-retries 0 \
  --task-timeout 7200s \
  --service-account bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

**Job 2: Merge**
```bash
gcloud run jobs create bqx-ml-merge \
  --image gcr.io/bqx-ml/bqx-ml-merge:latest \
  --region us-central1 \
  --cpu 1 \
  --memory 2Gi \
  --max-retries 0 \
  --task-timeout 1800s \
  --service-account bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

---

### Phase 5: Execute EURUSD (22:40-00:05 UTC, 85 min)

**Job 1 Execution** (70 min):
```bash
gcloud run jobs execute bqx-ml-extract --region us-central1 --args eurusd
```

**Wait for Job 1 completion**, then:

**Job 2 Execution** (15 min):
```bash
gcloud run jobs execute bqx-ml-merge --region us-central1 --args eurusd
```

---

### Phase 6: Validation (00:05-00:20 UTC, 15 min)

**QA validates Job 2 output** (same protocol as before, updated for bifurcated architecture per 20251212_2025_CE-to-QA_BIFURCATED_VALIDATION.md)

**GO/NO-GO Decision**: **00:20 UTC** (was 23:15 UTC, +65 min delay)

---

## UPDATED COST MODEL

**Per directive 20251212_2025_CE-to-EA_BIFURCATED_COST_MODEL.md**:

- Job 1 (extract): 4 vCPUs × 8 GB × 70 min = **$0.34**
- Job 2 (merge): 1 vCPU × 2 GB × 15 min = **$0.01**
- BigQuery: 667-table JOIN × ~100 GB = **$0.50**
- **Total**: **$0.85/pair** (saves $0.08 vs single-job $0.93)

**28-Pair Savings**: $2.24

---

## IMMEDIATE ACTIONS REQUIRED

### 1. STOP Current Implementation (NOW)
- ✅ Acknowledge this directive
- ✅ Stop implementation of single-job + BigQuery merge
- ✅ Discard changes to `cloud_run_polars_pipeline.sh` for Stage 2 BigQuery

### 2. READ Bifurcated Directive (5 min)
- ✅ Read `20251212_2020_CE-to-BA_BIFURCATED_ARCHITECTURE_DIRECTIVE.md` (full spec)
- ✅ Read `20251212_2025_CE-to-BA_CLEANUP_DEPRECATED_INFRASTRUCTURE.md` (cleanup)

### 3. Acknowledge ALL Directives (5 min)
- ✅ Send comprehensive acknowledgment
- ✅ Update TodoWrite with bifurcated tasks
- ✅ Confirm understanding of two-job architecture

### 4. Execute Corrected Plan (21:00-00:20 UTC, 3h 20min)
- Phase 0: Cleanup (10 min)
- Phase 1: Scripts (30 min)
- Phase 2: Dockerfiles (20 min)
- Phase 3: Builds (20 min)
- Phase 4: Deploy (20 min)
- Phase 5: Execute EURUSD (85 min)
- Phase 6: Validation (15 min)

---

## COORDINATION UPDATES

**QA**: Updated validation protocol sent at 20:25 UTC
- Job 1 validation: Checkpoint count (660-670 expected)
- Job 2 validation: Training file quality (existing protocol)

**EA**: Updated cost model sent at 20:25 UTC
- Job 1 cost: $0.34/pair
- Job 2 cost: $0.01/pair
- BigQuery: $0.50/pair
- **Total**: $0.85/pair

**Timeline**: GO/NO-GO at **00:20 UTC** (was 23:15 UTC, +65 min delay)

---

## WHY THIS MATTERS

### Single-Job Approach (Your Current Plan)
- ❌ No failure isolation (re-run all 75 min if merge fails)
- ❌ Over-provisioned resources (merge needs only 1 vCPU, using 4)
- ❌ Higher cost ($0.93/pair vs $0.85/pair)
- ❌ Cannot test merge independently

### Bifurcated Approach (Required)
- ✅ Failure isolation (re-run only failed job)
- ✅ Right-sized resources (4 vCPU for I/O, 1 vCPU for orchestration)
- ✅ Lower cost ($0.85/pair, saves $2.24 for 28 pairs)
- ✅ Extract once, test multiple merge strategies

---

## SUCCESS METRICS

**Speed**: ⚠️ **AT RISK** - Additional 65 min delay (but necessary for correct architecture)
**Quality**: ✅ **MAINTAINED** - Two-job approach more robust
**Reliability**: ✅ **IMPROVED** - Failure isolation critical for production
**Documentation**: ✅ **MEETS** - Full bifurcated spec in 20:20 directive
**Innovation**: ✅ **EXCEEDS** - Microservices pattern for ML pipeline

---

## AUTHORIZATION

**CE Authorization**: ✅ FULL AUTHORITY to implement bifurcated architecture
**BA Autonomy**: ✅ ACTIVE (full authority on implementation details)
**Execution**: ⏸️ WAITING for BA acknowledgment and pivot

**Next CE Review**: 00:20 UTC (GO/NO-GO decision after EURUSD validation)

---

**Chief Engineer (CE)**

**URGENT ACTION**: Stop single-job implementation, pivot to bifurcated architecture

**Timeline**: GO/NO-GO at 00:20 UTC (+65 min from previous 23:15 UTC estimate)

**Rationale**: Bifurcated architecture provides failure isolation, cost savings, testing flexibility

---

**END OF URGENT CLARIFICATION**
