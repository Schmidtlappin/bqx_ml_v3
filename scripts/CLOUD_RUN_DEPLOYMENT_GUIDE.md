# Cloud Run Deployment Guide - 100% VM Independent

## Overview

Deploy the autonomous 27-pair pipeline to Google Cloud Run for complete VM independence.

**Cost**: $16.22 one-time for 27 pairs
**VM Dependency**: Zero (100% serverless)
**Timeline**: 54 hours total execution

---

## Prerequisites

### Required Modifications

**CRITICAL**: Extraction script must write to GCS (not local disk)

The current script writes to local disk. For Cloud Run, modify:

**File**: `pipelines/training/parallel_feature_testing.py`

**Change**:
```python
# Line ~200-220: Change checkpoint output path

# BEFORE (local disk):
checkpoint_file = f"{checkpoint_dir}/{table_name}.parquet"

# AFTER (GCS):
checkpoint_file = f"gs://bqx-ml-staging/{pair}/{table_name}.parquet"
```

**Time**: 30 minutes to modify and test

---

## Deployment Steps

### Step 1: Create Service Account (One-Time)

```bash
# Create service account for Cloud Run
gcloud iam service-accounts create bqx-ml-pipeline \
    --display-name="BQX ML Pipeline Runner" \
    --project=bqx-ml

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding bqx-ml \
    --member="serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

# Grant GCS permissions
gsutil iam ch \
    serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com:objectAdmin \
    gs://bqx-ml-staging

gsutil iam ch \
    serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com:objectAdmin \
    gs://bqx-ml-output
```

**Time**: 5 minutes

### Step 2: Build and Deploy (Automated)

```bash
cd /home/micha/bqx_ml_v3

# Run automated deployment script
./scripts/deploy_cloud_run.sh
```

**What it does**:
1. Builds container image using Cloud Build (~10 min)
2. Pushes to Google Container Registry
3. Deploys to Cloud Run
4. Verifies deployment

**Time**: 15-20 minutes

### Step 3: Execute All 27 Pairs

```bash
# Execute all pairs in parallel (Cloud Run auto-scales)
./scripts/cloud_run_execute_all_pairs.sh
```

**What happens**:
- Creates 27 Cloud Run jobs (one per pair)
- Each job runs independently
- Cloud Run auto-scales to handle load
- Jobs execute in parallel (as resources permit)

**Time**: 54 hours execution (jobs run independently)

---

## Monitoring

### List Running Jobs

```bash
gcloud run jobs list --region us-central1 --project bqx-ml
```

### Check Job Status

```bash
# List executions for specific pair
gcloud run jobs executions list pipeline-audusd \
    --region us-central1 \
    --project bqx-ml

# View logs for specific execution
gcloud run jobs executions logs <execution-name> \
    --region us-central1 \
    --project bqx-ml
```

### Check Output Files

```bash
# List completed training files in GCS
gsutil ls gs://bqx-ml-output/training_*.parquet

# Count completed pairs
gsutil ls gs://bqx-ml-output/training_*.parquet | wc -l
```

---

## Cost Breakdown

**Cloud Run Compute**:
- 27 jobs × $0.49/job = $13.23

**BigQuery + GCS**:
- Merge queries: $2.97
- Temp storage: $0.02
- **Subtotal**: $2.99

**Total One-Time**: **$16.22**

**Recurring** (monthly):
- GCS training files: $0.43/month

---

## Advantages of Cloud Run

✅ **100% VM Independent**
- No VM needed at all
- Can shut down VM completely
- Zero infrastructure management

✅ **Serverless Auto-Scaling**
- Cloud Run provisions resources automatically
- Handles all 27 pairs concurrently
- No capacity planning needed

✅ **Managed Infrastructure**
- Google manages: compute, scaling, monitoring
- No OS updates or maintenance
- Built-in logging and metrics

✅ **Pay-Per-Use**
- Only pay for execution time
- No idle costs
- No pre-provisioning

---

## Disadvantages vs VM

❌ **Cost**
- 5.4× more expensive ($16.22 vs $2.99)
- Trade-off for VM independence

❌ **Execution Time**
- Same 54-hour timeline (no parallel benefit from Cloud Run)
- Jobs are rate-limited by BigQuery API

❌ **Complexity**
- More complex deployment (Cloud Build, service accounts)
- Requires GCS-first extraction (script modification)

---

## When to Use Cloud Run

**Use Cloud Run IF**:
- ✅ You want to shut down VM completely
- ✅ You run pipeline infrequently (monthly, quarterly)
- ✅ You value zero infrastructure management
- ✅ Cost is not primary concern ($13 premium acceptable)

**Use VM Container IF**:
- ✅ You want lowest cost ($2.99 vs $16.22)
- ✅ VM is already running for other work
- ✅ You run pipeline frequently (cost adds up)

---

## Transition Plan from AUDUSD

### Current Status

AUDUSD extraction running on VM:
- Progress: 427/668 files (64%)
- ETA: ~15 minutes to completion

### Recommended Transition

**Option A: Finish AUDUSD on VM, Cloud Run for 26 pairs**

```bash
# 1. Wait for AUDUSD extraction to complete (~15 min)
# 2. Manually merge AUDUSD (or use existing file)
# 3. Deploy Cloud Run
./scripts/deploy_cloud_run.sh

# 4. Execute 26 remaining pairs
# Edit cloud_run_execute_all_pairs.sh to exclude audusd
./scripts/cloud_run_execute_all_pairs.sh
```

**Cost**: $16.22 × (26/27) = **$15.60** for 26 pairs

**Option B: Stop AUDUSD, Cloud Run for all 27**

```bash
# 1. Kill AUDUSD extraction
kill 449948

# 2. Deploy Cloud Run
./scripts/deploy_cloud_run.sh

# 3. Execute all 27 pairs (including audusd)
./scripts/cloud_run_execute_all_pairs.sh
```

**Cost**: **$16.22** for 27 pairs
**Time Lost**: 68 minutes of AUDUSD extraction

---

## Service Account Permissions Checklist

Before deployment, verify service account has:

- ✅ `roles/bigquery.admin` on project
- ✅ `objectAdmin` on `gs://bqx-ml-staging`
- ✅ `objectAdmin` on `gs://bqx-ml-output`
- ✅ `roles/run.invoker` (for job execution)

---

## Troubleshooting

### Build Fails

```bash
# Check Cloud Build API is enabled
gcloud services enable cloudbuild.googleapis.com

# Check build logs
gcloud builds list --project bqx-ml
gcloud builds log <build-id> --project bqx-ml
```

### Deployment Fails

```bash
# Check Cloud Run API is enabled
gcloud services enable run.googleapis.com

# Verify service account exists
gcloud iam service-accounts list --project bqx-ml
```

### Job Execution Fails

```bash
# Check job logs
gcloud run jobs executions logs <execution-name> \
    --region us-central1 \
    --project bqx-ml

# Common issues:
# - Service account lacks BigQuery permissions
# - GCS buckets don't exist
# - Extraction script not modified for GCS output
```

---

## Quick Start Summary

```bash
# 1. Modify extraction script for GCS (30 min)
# 2. Create service account (5 min)
gcloud iam service-accounts create bqx-ml-pipeline ...

# 3. Deploy to Cloud Run (20 min)
./scripts/deploy_cloud_run.sh

# 4. Execute all pairs (54h execution)
./scripts/cloud_run_execute_all_pairs.sh

# 5. Monitor (optional)
gcloud run jobs list --region us-central1
```

**Total Setup**: ~1 hour
**Total Execution**: ~54 hours
**Total Cost**: $16.22

---

## Recommendation

**For 27-pair one-time run with VM independence**:
→ Cloud Run is worth the $13 premium if you need to:
  - Shut down VM completely
  - Avoid all infrastructure management
  - Run pipeline while VM is unavailable

**For cost-conscious deployment**:
→ VM Container + GCS is 82% cheaper ($2.99 vs $16.22)
  - Same outcome (27 training files)
  - Requires VM to run (but can do other work)
  - Still stores all data in GCS
