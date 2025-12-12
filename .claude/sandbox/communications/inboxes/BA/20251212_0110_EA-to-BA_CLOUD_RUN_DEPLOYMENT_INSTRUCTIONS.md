# EA DIRECTIVE: Cloud Run Deployment Instructions for BA

**Date**: December 12, 2025 01:10 UTC
**From**: Enhancement Assistant (EA)
**To**: Business Analyst (BA)
**Re**: Cloud Run Deployment Instructions - 100% VM Independent Pipeline
**Priority**: P1 - PENDING CE AUTHORIZATION
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## OVERVIEW

**User Decision**: Deploy autonomous pipeline on Cloud Run (serverless)
**Your Role**: Deploy and execute pipeline after EA completes script modifications
**Timeline**: 1 hour setup, 54 hours execution
**Cost**: $16.22 for 27 pairs

---

## YOUR TASKS (After EA Completes Script Modification)

### Task 1: Create Service Account (5 minutes)

```bash
# Create service account
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

### Task 2: Deploy to Cloud Run (20 minutes)

```bash
cd /home/micha/bqx_ml_v3

# Run automated deployment (builds image + deploys)
./scripts/deploy_cloud_run.sh
```

**What this does**:
- Builds container image via Google Cloud Build (~10 min)
- Pushes image to Google Container Registry
- Deploys to Cloud Run in us-central1
- Verifies deployment successful

### Task 3: Execute All 27 Pairs (54 hours)

```bash
# Execute all pairs in parallel
./scripts/cloud_run_execute_all_pairs.sh
```

**What this does**:
- Creates 27 Cloud Run jobs (one per pair)
- Each job runs independently
- Cloud Run auto-scales to handle load
- Jobs complete over ~54 hours

---

## MONITORING

### Check Job Status

```bash
# List all jobs
gcloud run jobs list --region us-central1 --project bqx-ml

# Check specific job
gcloud run jobs executions list pipeline-audusd \
    --region us-central1 \
    --project bqx-ml
```

### View Logs

```bash
# Get execution name from list command above, then:
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

## REPORTING TO CE

**Required Reports**:

1. **After Deployment** (Task 2 complete):
   - Cloud Run service deployed successfully
   - Timestamp
   - Service URL

2. **After Execution Start** (Task 3 complete):
   - 27 jobs created successfully
   - Timestamp
   - Expected completion time

3. **After Completion** (all 27 pairs done):
   - All 27 training files in GCS
   - Total cost (check GCP billing)
   - Total execution time

**Optional Reports** (at your discretion):
- 25% complete (7 pairs)
- 50% complete (14 pairs)
- 75% complete (21 pairs)

---

## COST TRACKING

**Expected Cost**: $16.22

**Verify in GCP Console**:
1. Go to Billing → Reports
2. Filter by: Cloud Run service = bqx-autonomous-pipeline
3. Date range: Dec 12-14, 2025
4. Should show ~$13.23 Cloud Run + $2.99 BigQuery/GCS

**Report to CE** if cost exceeds $20

---

## TROUBLESHOOTING

### Deployment Fails (Task 2)

```bash
# Check Cloud Build logs
gcloud builds list --project bqx-ml --limit 5

# View specific build log
gcloud builds log <build-id> --project bqx-ml
```

**Common Issues**:
- Cloud Build API not enabled → `gcloud services enable cloudbuild.googleapis.com`
- Cloud Run API not enabled → `gcloud services enable run.googleapis.com`
- Insufficient permissions → Check service account roles

**Escalate to EA** if errors persist after checking APIs

### Job Execution Fails (Task 3)

```bash
# Check job logs for errors
gcloud run jobs executions logs <execution-name> \
    --region us-central1 \
    --project bqx-ml
```

**Common Issues**:
- BigQuery permissions missing → Check service account has `bigquery.admin`
- GCS permissions missing → Check service account has `objectAdmin`
- Extraction script bugs → Escalate to EA

**Escalate to EA** if >3 jobs fail with same error

---

## DEPENDENCIES

### Before You Can Deploy

**EA Must Complete** (30 minutes):
- Modify extraction script to write to GCS (not local disk)
- Test script with single pair
- Commit changes to git

**EA Will Notify** when ready for BA deployment

**Current Status**: ⏸️ AWAITING CE AUTHORIZATION
- CE must authorize EA to modify script
- EA will notify BA when modification complete
- Then BA can proceed with tasks above

---

## TIMELINE

**EA Script Modification** (30 min):
- Start: After CE authorization
- Complete: ~01:40 UTC

**BA Service Account Setup** (5 min):
- Start: After EA notifies completion
- Complete: ~01:45 UTC

**BA Cloud Run Deployment** (20 min):
- Start: After service account ready
- Complete: ~02:05 UTC

**BA Job Execution** (54 hours):
- Start: ~02:05 UTC (Dec 12)
- Complete: ~08:05 UTC (Dec 14)

---

## QUESTIONS?

**For deployment issues**: Check troubleshooting section first, then escalate to EA

**For authorization questions**: Contact CE

**For cost questions**: Check GCP Billing console, report to CE if exceeds $20

---

## COMPLETE GUIDE

See: `/home/micha/bqx_ml_v3/scripts/CLOUD_RUN_DEPLOYMENT_GUIDE.md`

For detailed instructions, architecture, cost analysis, and troubleshooting.

---

**Enhancement Assistant (EA)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Pending CE authorization for script modification
**Your Next Action**: Wait for EA notification that script modification is complete
**Then**: Execute Tasks 1-3 above
**Timeline**: ~1 hour setup, 54 hours execution
