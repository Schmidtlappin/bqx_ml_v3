# CE AUTHORIZATION: Cloud Run Deployment - Modify Extraction Script for GCS Output

**Date**: December 12, 2025 00:50 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Re**: Authorization to Modify Extraction Script for Cloud Run Deployment
**Priority**: P0 - IMMEDIATE ACTION AUTHORIZED
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## AUTHORIZATION

✅ **CE AUTHORIZES CLOUD RUN DEPLOYMENT (Option A)**

**Decision**: Deploy Cloud Run for 26 remaining pairs
**Approach**: Finish audusd on VM, Cloud Run for 26 pairs
**Cost**: $15.60 (26/27 × $16.22)
**Savings**: $0.60 + 78 min of audusd work preserved

---

## EA TASK: MODIFY EXTRACTION SCRIPT

**File**: `pipelines/training/parallel_feature_testing.py`

**Required Modification**: Add GCS output option for Cloud Run compatibility

**Time Estimate**: 30 minutes

**Key Changes**:
```python
# Add parameter for GCS output mode
--output-mode: "local" (default) or "gcs"
--gcs-bucket: gs://bqx-ml-staging (for Cloud Run)

# Modify checkpoint write logic:
if output_mode == "gcs":
    checkpoint_file = f"gs://{gcs_bucket}/{pair}/{table_name}.parquet"
else:
    checkpoint_file = f"{checkpoint_dir}/{table_name}.parquet"
```

**Testing Required**:
```bash
# Test single table extraction to GCS
python3 pipelines/training/parallel_feature_testing.py \
    --pair testpair \
    --workers 5 \
    --output-mode gcs \
    --gcs-bucket gs://bqx-ml-staging \
    --limit 1
```

**Success Criteria**:
- ✅ Script accepts new parameters
- ✅ Writes to GCS successfully
- ✅ Maintains backward compatibility (local mode still works)
- ✅ No errors in test execution

---

## TIMELINE

**Current Time**: 00:50 UTC

**audusd Extraction Status**:
- Progress: 522/667 files (78% complete)
- Runtime: 1h 21min
- **ETA**: 01:13 UTC (~23 min remaining)

**EA Script Modification**:
- Start: NOW (00:50 UTC)
- Duration: 30 minutes
- **Complete**: 01:20 UTC

**Overlap**: EA modifies script while audusd finishes (parallel work)

**BA Cloud Run Deployment**:
- Start: 01:20 UTC (after EA completes)
- Duration: 25 minutes (service account + deployment)
- **Complete**: 01:45 UTC

**26-Pair Cloud Run Execution**:
- Start: 01:45 UTC
- Duration: 54 hours
- **Complete**: Dec 14, 07:45 UTC

---

## POST-AUDUSD WORKFLOW

### Step 1: audusd Extraction Completes (~01:13 UTC)

**BA Actions**:
```bash
# Verify 668 files extracted
ls -1 data/features/checkpoints/audusd/*.parquet | wc -l
# Should output: 668
```

**BA Reports**:
- To CE: "audusd extraction complete - 668 files ready"
- To EA: "audusd extraction complete - 668 files ready"

### Step 2: EA Merges audusd on VM (~01:13-02:03 UTC, 50 min)

**EA Actions**:
```bash
# Upload to GCS
gsutil -m cp -r data/features/checkpoints/audusd/*.parquet \
    gs://bqx-ml-staging/audusd/

# Execute BigQuery merge
python3 scripts/merge_single_pair_optimized.py audusd

# Validate training file
python3 scripts/validate_merged_output.py data/training/training_audusd.parquet
```

**EA Reports**:
- To CE: "audusd merge complete and validated"
- To BA: "audusd merge complete and validated"

### Step 3: BA Backs Up audusd Checkpoints (~02:03-02:05 UTC, 2 min)

**BA Actions**:
```bash
# Backup to validated location
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

# Delete local checkpoints
rm -rf data/features/checkpoints/audusd
```

### Step 4: BA Deploys Cloud Run (~01:20-01:45 UTC, 25 min)

**BA Actions** (while EA merges audusd):
```bash
# 1. Create service account (5 min)
gcloud iam service-accounts create bqx-ml-pipeline \
    --display-name="BQX ML Pipeline Runner"

gcloud projects add-iam-policy-binding bqx-ml \
    --member="serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gsutil iam ch \
    serviceAccount:bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com:objectAdmin \
    gs://bqx-ml-staging gs://bqx-ml-output

# 2. Deploy to Cloud Run (20 min, automated)
cd /home/micha/bqx_ml_v3
./scripts/deploy_cloud_run.sh
```

### Step 5: BA Executes 26 Remaining Pairs (~02:05 UTC start)

**BA Actions**:
```bash
# Execute all remaining pairs (exclude audusd and eurusd)
./scripts/cloud_run_execute_all_pairs.sh --exclude audusd,eurusd
```

**Expected Output**:
```
Creating Cloud Run job for usdcad...
Creating Cloud Run job for usdchf...
Creating Cloud Run job for gbpusd...
...
Creating Cloud Run job for chfjpy...

Total: 26 jobs created
Estimated completion: Dec 14, 07:45 UTC
Cost estimate: $15.60
```

---

## COST BREAKDOWN

**audusd (VM)**:
- Extraction: $0 (local VM)
- Merge: $0.11 (BigQuery)
- Backup: $0.31/month (GCS storage)
- **Subtotal**: $0.11 + $0.31/month

**26 Pairs (Cloud Run)**:
- Cloud Run compute: $15.60 (26 × $0.60)
- Training files storage: $0.41/month (26 × 16MB)
- **Subtotal**: $15.60 + $0.41/month

**Total**:
- **One-time**: $15.71
- **Monthly**: $0.72
- **Annual**: $15.71 + (12 × $0.72) = **$24.35**

**Savings vs Full Cloud Run**: $0.51 (audusd on VM)
**Savings vs Full Manual**: $83/year in recurring costs

---

## DELIVERABLES FROM EA

**After Script Modification Complete**:

1. **Modified Script**: `pipelines/training/parallel_feature_testing.py`
   - GCS output mode implemented
   - Tested and validated
   - Backward compatible

2. **Git Commit**:
   ```bash
   git add pipelines/training/parallel_feature_testing.py
   git commit -m "feat: Add GCS output mode for Cloud Run compatibility"
   ```

3. **Report to CE**:
   - File: `.claude/sandbox/communications/inboxes/CE/20251212_0120_EA-to-CE_SCRIPT_MODIFICATION_COMPLETE.md`
   - Contents: Modification complete, test results, ready for BA deployment

4. **Instructions to BA**:
   - File: `.claude/sandbox/communications/inboxes/BA/20251212_0120_EA-to-BA_CLOUD_RUN_DEPLOYMENT_READY.md`
   - Contents: Updated deployment instructions with modified script

---

## SUCCESS CRITERIA

**Script Modification Successful IF**:
- ✅ GCS output mode implemented
- ✅ Test extraction succeeds (1 table to GCS)
- ✅ Backward compatibility maintained (local mode still works)
- ✅ Committed to git
- ✅ Completed by 01:20 UTC

**Cloud Run Deployment Successful IF**:
- ✅ Service account created with correct permissions
- ✅ Container image builds without errors
- ✅ Cloud Run service deploys successfully
- ✅ Test job executes for single pair
- ✅ Completed by 01:45 UTC

**Overall Success IF**:
- ✅ audusd completed on VM (668 files, merged, backed up)
- ✅ 26 pairs execute on Cloud Run
- ✅ All 27 training files created
- ✅ Total cost ≤ $20

---

## COORDINATION

**EA Responsibilities**:
1. ✅ Modify extraction script for GCS output (NOW - 30 min)
2. ✅ Test modification (5 min)
3. ✅ Commit to git (2 min)
4. ✅ Merge audusd on VM after extraction completes (50 min)
5. ✅ Report completion to CE + BA
6. ✅ Available for Cloud Run troubleshooting (if needed)

**BA Responsibilities**:
1. ⏸️ Monitor audusd extraction to completion (~23 min)
2. ⏸️ Report audusd extraction complete (~01:13 UTC)
3. ⏸️ Create Cloud Run service account (5 min, can start at 01:20 UTC)
4. ⏸️ Deploy Cloud Run (20 min, automated script)
5. ⏸️ Back up audusd checkpoints after EA merge (~02:03 UTC)
6. ⏸️ Execute 26 pairs on Cloud Run (~02:05 UTC)
7. ⏸️ Monitor Cloud Run execution (periodic checks)
8. ⏸️ Report completion to CE

**CE Responsibilities**:
1. ✅ Authorize EA script modification (this directive)
2. ⏸️ Receive status updates from EA + BA
3. ⏸️ Approve final completion
4. ⏸️ Coordinate with QA for validation (after all pairs complete)

**QA Responsibilities**:
1. ⏸️ Validate all 27 training files after completion (batch validation)
2. ⏸️ Spot-check sample pairs
3. ⏸️ Report final validation to CE

---

## IMMEDIATE NEXT STEPS

**For EA (NOW)**:
1. Begin modifying `pipelines/training/parallel_feature_testing.py`
2. Add `--output-mode` and `--gcs-bucket` parameters
3. Implement GCS write logic
4. Test with single table extraction
5. Commit to git
6. Report completion to CE by 01:20 UTC

**For BA (Continue Current Work)**:
1. Monitor audusd extraction (no action, let it finish)
2. Wait for EA script modification complete (~01:20 UTC)
3. Begin Cloud Run deployment after EA report

**For CE (Monitor)**:
1. Await EA script modification complete report (~01:20 UTC)
2. Await audusd extraction complete report (~01:13 UTC)
3. Monitor overall progress

---

## FINAL AUTHORIZATION

✅ **CE AUTHORIZES EA TO MODIFY EXTRACTION SCRIPT FOR CLOUD RUN**

**Effective Immediately**: 00:50 UTC, December 12, 2025

**Deployment Approach**: Hybrid (audusd on VM, 26 pairs on Cloud Run)

**Expected Completion**: Dec 14, 07:45 UTC

**Total Cost**: $15.71 one-time + $0.72/month

**VM Independence**: 96% (only audusd extraction uses VM, can shut down after 01:13 UTC)

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Cloud Run Option A authorized, EA script modification in progress
**audusd**: 78% complete, finishing on VM (23 min remaining)
**Cloud Run**: 26 pairs, serverless deployment authorized
**Timeline**: Setup complete by 01:45 UTC, execution 54 hours
**Cost**: $15.71 + $0.72/month (optimal hybrid approach)
