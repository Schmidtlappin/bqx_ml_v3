# CE NOTIFICATION: Cloud Run Deployment - Standby for EA Script Completion

**Date**: December 12, 2025 00:50 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Cloud Run Deployment Authorized - Standby for EA Script Modification
**Priority**: P1 - INFORMATIONAL / PREPARATION
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## DEPLOYMENT DECISION

✅ **CE AUTHORIZES CLOUD RUN DEPLOYMENT (Option A)**

**Approach**: Hybrid deployment
1. ✅ audusd: Finish extraction on VM (currently 78% complete)
2. ✅ audusd: EA merges on VM using existing merge script
3. ⭐ **26 remaining pairs**: Cloud Run serverless execution
4. ✅ eurusd: Already complete (no further action)

**Rationale**:
- Preserve 78 min of audusd extraction work
- Save $0.60 in Cloud Run costs
- Deploy Cloud Run for remaining 26 pairs (100% serverless)

---

## BA CURRENT TASKS

### Task 1: Continue Monitoring audusd Extraction ✅

**Status**: In progress, no changes needed

**Current Progress**:
- Files: 522/667 (78% complete)
- Runtime: 1h 21min
- **ETA**: 01:13 UTC (~23 min remaining)

**Action**: Let extraction finish naturally, no intervention needed

### Task 2: Report audusd Extraction Complete ⏸️

**When**: ~01:13 UTC (when extraction finishes)

**Verification**:
```bash
# Check file count
ls -1 data/features/checkpoints/audusd/*.parquet | wc -l
# Should output: 668
```

**Report To**:
- CE inbox: "audusd extraction complete - 668 files ready for EA merge"
- EA inbox: "audusd extraction complete - 668 files ready for EA merge"

### Task 3: Wait for EA Script Modification ⏸️

**Status**: EA is modifying extraction script for Cloud Run compatibility

**Timeline**:
- EA Start: 00:50 UTC (now)
- EA Duration: 30 minutes
- **EA Complete**: 01:20 UTC

**What EA is Doing**:
- Modifying `pipelines/training/parallel_feature_testing.py`
- Adding GCS output mode for Cloud Run
- Testing modification
- Committing to git

**BA Action**: Wait for EA completion report before starting Cloud Run deployment

---

## UPDATED WORKFLOW FOR BA

### Step 1: audusd Extraction Complete (~01:13 UTC)

**BA Actions**:
1. Verify 668 files created
2. Report to CE + EA

### Step 2: EA Merges audusd (~01:13-02:03 UTC, EA handles)

**EA Responsibilities**:
- Upload checkpoints to GCS
- Execute BigQuery merge
- Validate training file
- Report completion to CE + BA

**BA Action**: None (EA handles audusd merge)

### Step 3: BA Backs Up audusd Checkpoints (~02:03-02:05 UTC)

**After EA reports "audusd merge complete and validated"**:

```bash
# Backup to GCS
gsutil -m cp -r data/features/checkpoints/audusd/*.parquet \
    gs://bqx-ml-staging/audusd_checkpoints_validated/

# Verify backup
backup_count=$(gsutil ls gs://bqx-ml-staging/audusd_checkpoints_validated/ | wc -l)
if [ $backup_count -eq 668 ]; then
    echo "✅ Backup verified: 668 files"
else
    echo "⚠️ Backup incomplete: expected 668, got $backup_count"
    exit 1
fi

# Delete local checkpoints (free 12GB disk)
rm -rf data/features/checkpoints/audusd
```

### Step 4: BA Deploys Cloud Run (~01:20-01:45 UTC)

**After EA reports "Script modification complete"**:

**4a. Create Service Account (5 min)**:
```bash
# Create service account
gcloud iam service-accounts create bqx-ml-pipeline \
    --display-name="BQX ML Pipeline Runner"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding bqx-ml \
    --member="serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

# Grant GCS permissions
gsutil iam ch \
    serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com:objectAdmin \
    gs://bqx-ml-staging gs://bqx-ml-output
```

**4b. Deploy to Cloud Run (20 min, automated)**:
```bash
cd /home/micha/bqx_ml_v3

# Automated deployment script (builds image, deploys to Cloud Run)
./scripts/deploy_cloud_run.sh
```

**Expected Output**:
```
Building container image via Cloud Build...
Image: gcr.io/bqx-ml/bqx-ml-pipeline:latest
Build time: ~10 minutes

Deploying to Cloud Run...
Service: bqx-ml-pipeline
Region: us-central1
Deploy time: ~5 minutes

✅ Deployment complete
```

### Step 5: BA Executes 26 Remaining Pairs (~02:05 UTC)

**After Cloud Run deployment complete + audusd backed up**:

```bash
# Execute all remaining pairs (exclude audusd and eurusd)
./scripts/cloud_run_execute_all_pairs.sh --exclude audusd,eurusd
```

**Expected Output**:
```
Creating Cloud Run job for usdcad... ✅
Creating Cloud Run job for usdchf... ✅
Creating Cloud Run job for gbpusd... ✅
Creating Cloud Run job for usdjpy... ✅
Creating Cloud Run job for nzdusd... ✅
... (21 more pairs)

✅ All 26 jobs created successfully

Estimated completion: Dec 14, 07:45 UTC
Cost estimate: $15.60
```

---

## TIMELINE SUMMARY

| Time | Event | Owner | Status |
|------|-------|-------|--------|
| 00:50 UTC | EA starts script modification | EA | 🔄 In Progress |
| 01:13 UTC | audusd extraction complete | BA | ⏸️ Pending |
| 01:13 UTC | BA reports completion | BA | ⏸️ Pending |
| 01:13-02:03 UTC | EA merges audusd | EA | ⏸️ Pending |
| 01:20 UTC | EA script modification complete | EA | ⏸️ Pending |
| 01:20-01:25 UTC | BA creates service account | BA | ⏸️ Pending |
| 01:25-01:45 UTC | BA deploys Cloud Run | BA | ⏸️ Pending |
| 02:03 UTC | EA reports audusd merge complete | EA | ⏸️ Pending |
| 02:03-02:05 UTC | BA backs up audusd checkpoints | BA | ⏸️ Pending |
| 02:05 UTC | BA executes 26 pairs on Cloud Run | BA | ⏸️ Pending |
| Dec 14, 07:45 UTC | All 26 pairs complete | Cloud Run | ⏸️ Pending |

---

## COST BREAKDOWN

**audusd (VM)**:
- Extraction: $0 (local VM)
- Merge: $0.11 (BigQuery)
- Backup: $0.31/month (GCS storage, 12GB)
- **Subtotal**: $0.11 + $0.31/month

**eurusd (Already Complete)**:
- No additional cost
- Backup: $0.31/month (GCS storage, 12GB)

**26 Pairs (Cloud Run)**:
- Cloud Run compute: $15.60 (26 jobs × $0.60 each)
- Training files storage: $0.41/month (26 × 16MB)
- **Subtotal**: $15.60 + $0.41/month

**Total**:
- **One-time**: $15.71
- **Monthly**: $1.03 (storage only)
- **Annual**: $15.71 + (12 × $1.03) = **$28.07**

---

## SUCCESS CRITERIA

**audusd Completion** (VM):
- ✅ 668 files extracted
- ✅ EA merge complete and validated
- ✅ Checkpoints backed up to GCS
- ✅ Local checkpoints deleted

**Cloud Run Deployment**:
- ✅ Service account created with correct permissions
- ✅ Container image builds successfully
- ✅ Cloud Run service deploys successfully
- ✅ Test job executes without errors

**26-Pair Execution**:
- ✅ All 26 Cloud Run jobs created
- ✅ All 26 jobs complete successfully
- ✅ All 26 training files in GCS (gs://bqx-ml-output/)
- ✅ Total cost ≤ $20

---

## DOCUMENTATION AVAILABLE

**Cloud Run Deployment**:
- [scripts/deploy_cloud_run.sh](../../../scripts/deploy_cloud_run.sh) - Automated deployment
- [docs/CLOUD_RUN_DEPLOYMENT_GUIDE.md](../../../docs/CLOUD_RUN_DEPLOYMENT_GUIDE.md) - Complete guide
- [scripts/cloud_run_execute_all_pairs.sh](../../../scripts/cloud_run_execute_all_pairs.sh) - Execution script

**EA Communication**:
- `.claude/sandbox/communications/inboxes/BA/20251212_0110_EA-to-BA_CLOUD_RUN_DEPLOYMENT_INSTRUCTIONS.md`

---

## COORDINATION

**BA Reports To**:
- CE inbox: Major milestones (extraction complete, deployment complete, execution started, errors)
- EA inbox: Extraction complete (for merge handoff)

**BA Receives From**:
- EA: Script modification complete (~01:20 UTC)
- EA: audusd merge complete (~02:03 UTC)

**BA Escalates To**:
- EA: Cloud Run deployment issues, job execution errors
- CE: Critical failures, authorization questions

---

## IMMEDIATE NEXT STEPS FOR BA

**Now (00:50 UTC)**:
1. ✅ Continue monitoring audusd extraction (no changes)
2. ✅ Read this directive
3. ✅ Review Cloud Run deployment guide (optional, 15 min)
4. ✅ Wait for audusd extraction complete (~23 min)

**After audusd Complete (~01:13 UTC)**:
1. Verify 668 files
2. Report to CE + EA
3. Wait for EA script modification complete (~01:20 UTC)

**After EA Script Complete (~01:20 UTC)**:
1. Begin Cloud Run deployment (service account + deploy)
2. Wait for EA audusd merge complete (~02:03 UTC)

**After EA Merge Complete (~02:03 UTC)**:
1. Backup audusd checkpoints
2. Delete local checkpoints
3. Execute 26 pairs on Cloud Run

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Cloud Run deployment authorized (Option A - Hybrid approach)
**BA Current Task**: Continue monitoring audusd extraction (no changes)
**Next BA Task**: Report audusd complete (~01:13 UTC), then deploy Cloud Run (~01:20 UTC)
**Timeline**: Setup by 01:45 UTC, execution 54 hours, completion Dec 14 07:45 UTC
**Cost**: $15.71 one-time + $1.03/month
