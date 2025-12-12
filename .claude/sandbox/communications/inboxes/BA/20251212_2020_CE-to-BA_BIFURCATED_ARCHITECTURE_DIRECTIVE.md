# 🚀 CE ARCHITECTURAL DIRECTIVE: Bifurcated Cloud Run Deployment

**Date**: December 12, 2025 20:20 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: SUPERSEDES Previous Directives - Bifurcated Cloud Run Architecture
**Priority**: P0-CRITICAL (REPLACES 20:05 AND 20:15 DIRECTIVES)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## 🚀 NEW ARCHITECTURAL PARADIGM

**Previous Approach** (SUPERSEDED):
- Single Cloud Run job doing both extraction AND merge
- Monolithic pipeline (5 stages in one execution)
- Stage 1 failure = re-run everything
- Stage 2 failure = re-run everything

**New Approach** (THIS DIRECTIVE):
- **TWO independent Cloud Run jobs**:
  - **Job 1**: BigQuery extraction → GCS checkpoints (ONLY)
  - **Job 2**: GCS checkpoints → merged training file (ONLY)
- Decoupled, specialized, failure-isolated
- Checkpoints persist in GCS between jobs

---

## RATIONALE: WHY BIFURCATE?

### 1. Separation of Concerns

**Job 1 (Extraction)**: I/O-intensive workload
- Parallel BigQuery queries (4-25 workers)
- Network I/O to GCS
- Moderate memory requirements (8-12 GB sufficient)
- **Optimized for**: Throughput, parallelism

**Job 2 (Merge)**: Compute/orchestration workload
- Sequential processing (single thread)
- BigQuery orchestration (if using BigQuery merge)
- **Optimized for**: Memory efficiency, cost

**Benefit**: Each job can be optimized for its specific workload characteristics

---

### 2. Failure Isolation & Recovery

**Current Single-Job Risk**:
- Extraction succeeds (60 min) → Merge fails → **RE-RUN BOTH** (75+ min wasted)
- Total waste: 135 min for a merge-only failure

**Bifurcated Architecture**:
- Job 1 succeeds → checkpoints in GCS → Job 1 terminates
- Job 2 fails → **RE-RUN JOB 2 ONLY** (10-20 min)
- Checkpoints already persisted, no re-extraction needed
- **Time saved**: 60-70 min per failure

**ROI**: First failure recovery pays for entire architecture change

---

### 3. Resource Optimization

**Job 1 Configuration**:
```yaml
resources:
  cpu: 4
  memory: 8GB  # Reduced from 12GB (no merge memory needed)
  timeout: 7200s  # 2 hours (extraction only)
```

**Job 2 Configuration** (BigQuery Merge):
```yaml
resources:
  cpu: 1  # Minimal (just orchestration)
  memory: 2GB  # Minimal (BigQuery does processing)
  timeout: 1800s  # 30 min (merge orchestration only)
```

**Cost Savings**:
- Job 1: 4 vCPUs × 8 GB × 70 min = $0.34/pair
- Job 2: 1 vCPU × 2 GB × 15 min = **$0.01/pair**
- **Total Cloud Run**: **$0.35/pair** (vs $0.46 single-job)
- **Savings**: $0.11/pair × 28 pairs = **$3.08 saved**

---

### 4. Decoupling & Flexibility

**Timeline Flexibility**:
- Job 1 (EURUSD) completes 21:30 UTC → checkpoints in GCS
- Job 2 (EURUSD) can run:
  - **Immediately**: 21:30 UTC (same day)
  - **Later**: 22:00 UTC (test different merge approaches)
  - **Tomorrow**: (checkpoints persist indefinitely)

**Testing Flexibility**:
- Extract once (Job 1)
- Test multiple merge strategies (Job 2 variants):
  - BigQuery merge (recommended)
  - Polars merge (if we provision high-memory instance)
  - DuckDB merge (alternative)
- No need to re-extract for each test

**Multi-Pair Scalability**:
- Job 1 completes for 5 pairs → 5 checkpoint sets in GCS
- Trigger 5× Job 2 instances in **parallel** (all reading from GCS)
- Massive parallelization opportunity

---

### 5. Cost Efficiency

**Single-Job Approach**:
```
Job duration: 75 min (extraction 60 min + merge 15 min)
Idle time: Merge waits for extraction (sequential)
Cost: 75 min × full resources
```

**Bifurcated Approach**:
```
Job 1: 70 min × extraction resources = $0.34
Job 2: 15 min × minimal resources = $0.01
Total: 85 min but lower average resource cost
Cost: $0.35 (vs $0.46 single-job)
Savings: $0.11/pair
```

**Plus BigQuery**:
- BigQuery merge: $0.50/pair
- **Total**: $0.85/pair (vs $0.93 in previous directive)
- **Savings**: $0.08/pair × 28 = $2.24

---

## ARCHITECTURE DESIGN

### Cloud Run Job 1: Extraction

**Name**: `bqx-ml-extract`
**Purpose**: BigQuery → GCS parquet checkpoints
**Trigger**: Manual or scheduled

**Configuration**:
```yaml
name: bqx-ml-extract
image: gcr.io/bqx-ml/bqx-ml-extract:latest
region: us-central1
resources:
  cpu: 4
  memory: 8Gi
  timeout: 7200s
env:
  - name: PAIR
    value: eurusd
  - name: GCS_CHECKPOINT_BUCKET
    value: gs://bqx-ml-staging/checkpoints
  - name: EXTRACTION_WORKERS
    value: "25"
service_account: bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

**Entrypoint**: `/workspace/scripts/extract_only.sh`

**Output**:
- 667 parquet files → `gs://bqx-ml-staging/checkpoints/{pair}/checkpoint_*.parquet`
- Exit code 0 (success) or 1 (failure)

**Success Criteria**:
- 667 checkpoint files created in GCS
- Each checkpoint file >1 MB
- Exit code 0

---

### Cloud Run Job 2: Merge

**Name**: `bqx-ml-merge`
**Purpose**: GCS checkpoints → merged training file
**Trigger**: After Job 1 success (or manual)

**Configuration**:
```yaml
name: bqx-ml-merge
image: gcr.io/bqx-ml/bqx-ml-merge:latest
region: us-central1
resources:
  cpu: 1  # Minimal (orchestration only)
  memory: 2Gi
  timeout: 1800s
env:
  - name: PAIR
    value: eurusd
  - name: GCS_CHECKPOINT_BUCKET
    value: gs://bqx-ml-staging/checkpoints
  - name: GCS_OUTPUT_BUCKET
    value: gs://bqx-ml-output
  - name: MERGE_METHOD
    value: bigquery  # or 'polars' for alternative
service_account: bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

**Entrypoint**: `/workspace/scripts/merge_only.sh`

**Output**:
- Merged training file → `gs://bqx-ml-output/training_{pair}.parquet`
- Exit code 0 (success) or 1 (failure)

**Success Criteria**:
- Training file created in GCS
- File size ~9-10 GB
- Dimensions: >100K rows, 6,477 features, 7 targets
- Exit code 0

---

## IMPLEMENTATION PLAN

### Phase 1: Create Extract-Only Script (30 min)

**New File**: `scripts/extract_only.sh`

```bash
#!/bin/bash
set -e

PAIR="${PAIR:-eurusd}"
CHECKPOINT_BUCKET="${GCS_CHECKPOINT_BUCKET:-gs://bqx-ml-staging/checkpoints}"
CHECKPOINT_DIR="${CHECKPOINT_BUCKET}/${PAIR}"

echo "=== EXTRACTION JOB: ${PAIR} ==="
echo "Output: ${CHECKPOINT_DIR}"

# Extract features to GCS checkpoints
python3 /workspace/pipelines/training/parallel_feature_testing.py \
    single "${PAIR}" \
    --gcs-output "${CHECKPOINT_BUCKET}" \
    --extract-only  # NEW FLAG: Skip merge, exit after extraction

# Verify checkpoint count
file_count=$(gsutil ls "${CHECKPOINT_DIR}/*.parquet" 2>/dev/null | wc -l)

if [ "${file_count}" -lt 600 ]; then
    echo "❌ EXTRACTION FAILED: Only ${file_count} checkpoints created"
    exit 1
fi

echo "✅ EXTRACTION COMPLETE: ${file_count} checkpoints in GCS"
exit 0
```

---

### Phase 2: Create Merge-Only Script (30 min)

**New File**: `scripts/merge_only.sh`

```bash
#!/bin/bash
set -e

PAIR="${PAIR:-eurusd}"
CHECKPOINT_BUCKET="${GCS_CHECKPOINT_BUCKET:-gs://bqx-ml-staging/checkpoints}"
OUTPUT_BUCKET="${GCS_OUTPUT_BUCKET:-gs://bqx-ml-output}"
MERGE_METHOD="${MERGE_METHOD:-bigquery}"

echo "=== MERGE JOB: ${PAIR} ==="
echo "Method: ${MERGE_METHOD}"
echo "Input: ${CHECKPOINT_BUCKET}/${PAIR}"
echo "Output: ${OUTPUT_BUCKET}/training_${PAIR}.parquet"

# Verify checkpoints exist
checkpoint_count=$(gsutil ls "${CHECKPOINT_BUCKET}/${PAIR}/*.parquet" 2>/dev/null | wc -l)
if [ "${checkpoint_count}" -lt 600 ]; then
    echo "❌ MERGE FAILED: Only ${checkpoint_count} checkpoints found (expected 667)"
    exit 1
fi

# Execute merge based on method
if [ "${MERGE_METHOD}" = "bigquery" ]; then
    echo "Using BigQuery cloud merge..."
    python3 /workspace/scripts/merge_in_bigquery.py \
        --pair "${PAIR}" \
        --checkpoint-bucket "${CHECKPOINT_BUCKET}" \
        --output-bucket "${OUTPUT_BUCKET}"
elif [ "${MERGE_METHOD}" = "polars" ]; then
    echo "Using Polars local merge..."
    python3 /workspace/scripts/merge_with_polars_safe.py \
        "${PAIR}" \
        "${CHECKPOINT_BUCKET}/${PAIR}" \
        "/tmp/training_${PAIR}.parquet"
    gsutil cp "/tmp/training_${PAIR}.parquet" "${OUTPUT_BUCKET}/"
else
    echo "❌ Unknown merge method: ${MERGE_METHOD}"
    exit 1
fi

# Verify output
gsutil ls -lh "${OUTPUT_BUCKET}/training_${PAIR}.parquet" || {
    echo "❌ MERGE FAILED: Output file not found"
    exit 1
}

echo "✅ MERGE COMPLETE"
exit 0
```

---

### Phase 3: Create Two Dockerfiles (20 min)

**Dockerfile.extract**:
```dockerfile
FROM python:3.10-slim
WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy extraction scripts only
COPY pipelines/ /workspace/pipelines/
COPY scripts/extract_only.sh /workspace/scripts/

ENTRYPOINT ["/workspace/scripts/extract_only.sh"]
```

**Dockerfile.merge**:
```dockerfile
FROM python:3.10-slim
WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy merge scripts only
COPY scripts/merge_only.sh /workspace/scripts/
COPY scripts/merge_in_bigquery.py /workspace/scripts/
COPY scripts/merge_with_polars_safe.py /workspace/scripts/

ENTRYPOINT ["/workspace/scripts/merge_only.sh"]
```

---

### Phase 4: Build & Deploy Two Jobs (20 min)

**Build Job 1**:
```bash
gcloud builds submit --config cloudbuild-extract.yaml
```

**cloudbuild-extract.yaml**:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/bqx-ml/bqx-ml-extract:latest', '-f', 'Dockerfile.extract', '.']
images:
  - 'gcr.io/bqx-ml/bqx-ml-extract:latest'
```

**Build Job 2**:
```bash
gcloud builds submit --config cloudbuild-merge.yaml
```

**cloudbuild-merge.yaml**:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/bqx-ml/bqx-ml-merge:latest', '-f', 'Dockerfile.merge', '.']
images:
  - 'gcr.io/bqx-ml/bqx-ml-merge:latest'
```

**Deploy Job 1**:
```bash
gcloud run jobs create bqx-ml-extract \
  --image gcr.io/bqx-ml/bqx-ml-extract:latest \
  --region us-central1 \
  --cpu 4 \
  --memory 8Gi \
  --timeout 7200s \
  --service-account bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

**Deploy Job 2**:
```bash
gcloud run jobs create bqx-ml-merge \
  --image gcr.io/bqx-ml/bqx-ml-merge:latest \
  --region us-central1 \
  --cpu 1 \
  --memory 2Gi \
  --timeout 1800s \
  --service-account bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com
```

---

### Phase 5: Execute EURUSD Test (85 min)

**Job 1 Execution**:
```bash
gcloud run jobs execute bqx-ml-extract \
  --region us-central1 \
  --args="eurusd"
```
**Duration**: 60-70 min
**Output**: 667 checkpoints in `gs://bqx-ml-staging/checkpoints/eurusd/`

**Job 2 Execution** (after Job 1 success):
```bash
gcloud run jobs execute bqx-ml-merge \
  --region us-central1 \
  --args="eurusd"
```
**Duration**: 10-15 min (BigQuery merge)
**Output**: `gs://bqx-ml-output/training_eurusd.parquet`

**Total**: 70-85 min (similar to single-job approach)

---

## UPDATED TIMELINE

### Previous Timeline (SUPERSEDED)
- 20:15-21:00: Implementation (45 min)
- 21:00-21:10: Pipeline update (10 min)
- 21:10-21:20: Container rebuild (10 min)
- 21:20-22:35: EURUSD execution (75 min)
- **Total**: 2h 20min to GO/NO-GO

### Bifurcated Timeline (NEW)
- 20:20-21:20: Implementation (60 min - 2 scripts, 2 Dockerfiles)
- 21:20-21:40: Build & deploy (20 min - 2 containers, 2 jobs)
- 21:40-22:50: Job 1 execution (70 min)
- 22:50-23:05: Job 2 execution (15 min)
- 23:05-23:20: Validation (15 min)
- **GO/NO-GO**: **23:20 UTC**

**Net Delay**: +50 min from original 22:30 UTC target
**Acceptable**: Architectural improvement worth 50-min delay

---

## COST MODEL (UPDATED)

### Bifurcated Architecture Cost

**Job 1 (Extract)**:
- 4 vCPUs × 8 GB × 70 min = **$0.34/pair**

**Job 2 (Merge orchestration)**:
- 1 vCPU × 2 GB × 15 min = **$0.01/pair**

**BigQuery Processing**:
- 667-table JOIN: ~100 GB scanned = **$0.50/pair**

**Total**: **$0.85/pair**

**28-Pair Total**: $23.80

**vs Previous Estimates**:
- Single-job Polars: $15.96 (but OOMs)
- Single-job BigQuery: $26.04
- **Bifurcated**: **$23.80** (saves $2.24)

---

## AUTHORIZATION

**Build Agent (BA)**: **AUTHORIZED TO PROCEED** with bifurcated architecture

**This Directive SUPERSEDES**:
- ❌ 20251212_2005_CE-to-BA_GCS_CHECKPOINT_FIX_APPROVED.md
- ❌ 20251212_2015_CE-to-BA_CRITICAL_BIGQUERY_MERGE_REQUIRED.md

**GCS Checkpoint Fix**: ✅ STILL VALID (incorporate into Job 1)
**BigQuery Merge**: ✅ STILL VALID (incorporate into Job 2)

**Required Actions**:
1. Create `scripts/extract_only.sh` (30 min)
2. Create `scripts/merge_only.sh` (30 min)
3. Create `Dockerfile.extract` and `Dockerfile.merge` (20 min)
4. Build & deploy both Cloud Run jobs (20 min)
5. Execute Job 1 (EURUSD extraction, 70 min)
6. Execute Job 2 (EURUSD merge, 15 min)
7. Report completion by 23:05 UTC

**Deliverable**: Both jobs successful, training file in GCS by 23:05 UTC

---

## BENEFITS SUMMARY

1. ✅ **Failure isolation**: Re-run only failed job (saves 60-70 min per failure)
2. ✅ **Resource optimization**: Each job sized for its workload (saves $0.08/pair)
3. ✅ **Decoupling**: Jobs can run asynchronously (flexibility)
4. ✅ **Testing flexibility**: Extract once, test multiple merge strategies
5. ✅ **Scalability**: Parallel Job 2 execution for multiple pairs
6. ✅ **Cost efficiency**: $23.80 vs $26.04 (saves $2.24 for 28 pairs)
7. ✅ **Maintainability**: Simpler, focused jobs (easier debugging)

---

**Chief Engineer (CE)**
*Strategic Coordination & Decision Authority*

**Architectural Decision**: Bifurcated Cloud Run deployment (TWO jobs vs ONE)

**Rationale**: Failure isolation, resource optimization, cost savings ($2.24)

**Timeline**: GO/NO-GO at 23:20 UTC (+50 min acceptable for architectural improvement)

**Authorization**: BA proceed immediately with bifurcated implementation

---

**END OF ARCHITECTURAL DIRECTIVE**
