# CE DIRECTIVE UPDATE: Add Checkpoint Backup Step to Each Pair Workflow

**Date**: December 12, 2025 02:58 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Updated Workflow - Backup Checkpoints Before Deletion (All 27 Pairs)
**Priority**: P0 - WORKFLOW MODIFICATION
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## WORKFLOW UPDATE

**User Directive**: "Add parquet backup step to the end of the pair merge process"

✅ **CE UPDATES 27-PAIR WORKFLOW TO INCLUDE CHECKPOINT BACKUP**

---

## UPDATED PER-PAIR WORKFLOW

**For each of the 27 pairs, execute this sequence**:

### Step 1: BA Extraction (20-30 min)
```bash
python3 pipelines/training/parallel_feature_testing.py \
  --pair {PAIR} \
  --workers 25 \
  --date-start 2020-01-01 \
  --date-end 2020-12-31
```

### Step 2: BA Validation (1 min)
```bash
# Verify 668 files created
ls data/features/checkpoints/{pair}/*.parquet | wc -l
# Should output: 668
```

### Step 3: BA Notification to EA (1 min)
- Send to CE inbox: "Pair {pair} extraction complete - 668 files ready"
- Send to EA inbox: "Pair {pair} extraction complete - 668 files ready"

### Step 4: EA Merge Operations (40-50 min)
- Upload to GCS staging
- Load to BigQuery
- Execute iterative batched JOIN
- Download training file
- Validate training file

### Step 5: EA Notification (EA sends)
- Message: "Pair {pair} merge complete and validated"

### **Step 6: BA Backup Checkpoints** ⭐ **NEW STEP**
```bash
# Backup checkpoints to GCS before deletion
gsutil -m cp -r data/features/checkpoints/{pair}/*.parquet \
  gs://bqx-ml-staging/{pair}_checkpoints_validated/

# Verify backup
backup_count=$(gsutil ls gs://bqx-ml-staging/{pair}_checkpoints_validated/ | wc -l)
if [ $backup_count -eq 668 ]; then
  echo "Backup verified: 668 files"
else
  echo "ERROR: Backup incomplete - expected 668, got $backup_count"
  exit 1
fi
```

**Duration**: ~1-2 min (parallel upload, 12GB)
**Cost**: $0.31/month per pair
**Total Cost**: 27 pairs × $0.31 = **$8.37/month** (affordable storage)

### Step 7: BA Delete Checkpoints (after backup verified)
```bash
rm -rf data/features/checkpoints/{pair}
```

**Disk Freed**: ~12GB per pair

### Step 8: BA Proceed to Next Pair
- Continue with next pair in sequence

---

## RATIONALE

**Why Backup Each Pair**:
1. ✅ **User Mandate**: "Do not delete validated parquet files" - backup required
2. ✅ **Disaster Recovery**: Preserve validated checkpoint files
3. ✅ **Reference**: Available for debugging/comparison
4. ✅ **Affordable**: $8.37/month total for all 27 pairs
5. ✅ **Fast**: 1-2 min backup time (minimal timeline impact)

---

## TIMELINE IMPACT

**Previous Estimate** (without backup):
- Per pair: 52-82 min (avg 67 min)
- 27 pairs: 30.15 hours

**Updated Estimate** (with backup):
- Per pair: 54-84 min (avg 69 min)
- 27 pairs: **31 hours** (+45 min total for all backups)

**Impact**: +2 min per pair, +45 min overall (acceptable)

---

## UPDATED SUCCESS CRITERIA

**Per Pair** (revised):
1. ✅ 668 files extracted
2. ✅ Messages to CE + EA
3. ✅ EA merge complete
4. ✅ **Checkpoints backed up to GCS** ⭐ NEW
5. ✅ Backup verified (668 files)
6. ✅ Checkpoints deleted locally
7. ✅ Next pair starts

---

## GCS BACKUP STRUCTURE

**Backup Locations**:
```
gs://bqx-ml-staging/
├── eurusd_checkpoints_validated/  (668 files, 11.81 GB) ✅ COMPLETE
├── audusd_checkpoints_validated/  (668 files, ~12 GB) ⏸️ PENDING
├── usdcad_checkpoints_validated/  (668 files, ~12 GB) ⏸️ PENDING
├── usdchf_checkpoints_validated/  (668 files, ~12 GB) ⏸️ PENDING
... (24 more pairs)
└── chfjpy_checkpoints_validated/  (668 files, ~12 GB) ⏸️ PENDING
```

**Total Storage**:
- 28 pairs × 12 GB = **336 GB**
- Cost: 336 GB × $0.026/GB/month = **$8.74/month**

**Retention**: Permanent (until explicitly deleted)

---

## ERROR HANDLING

**If Backup Fails**:
1. Retry backup once
2. If second failure: Report to CE with error details
3. **DO NOT delete checkpoints** until backup verified
4. CE will investigate and provide alternate approach

**If Backup Verification Fails**:
- Check actual count vs expected (668)
- Re-upload missing files
- Only proceed to deletion after 668 files confirmed

---

## BA EXECUTION AUTHORIZATION

✅ **CE AUTHORIZES BA TO EXECUTE UPDATED WORKFLOW**

**Applies to**: All 27 remaining pairs (audusd through chfjpy)

**Critical Change**: Add backup step BEFORE deletion (Step 6)

---

## COORDINATION WITH EA

**EA is notified** that BA will backup checkpoints after merge completes.

**EA's notification timing** remains unchanged:
- EA sends: "Pair {pair} merge complete and validated"
- BA then: Backups → Verifies → Deletes → Proceeds

**No changes needed** to EA's workflow.

---

## UPDATED START AUTHORIZATION

✅ **BA START NOW** (02:58 UTC) with updated workflow:

1. Delete EURUSD checkpoints (already backed up)
2. Verify >15GB disk free
3. Start audusd extraction
4. Follow updated workflow (including backup step)
5. Report completion to CE after each pair

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Workflow updated to include checkpoint backups for all pairs
**User Mandate**: ✅ COMPLIANT - All validated files will be backed up before deletion
**Timeline**: 31 hours (avg), +45 min vs original (acceptable)
**Cost**: $8.74/month for 28-pair backup storage (affordable)
**Start Time**: NOW (02:58 UTC)
