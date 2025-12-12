# CE NOTIFICATION: Workflow Updated - BA Will Backup Checkpoints After Merge

**Date**: December 12, 2025 02:58 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Re**: Workflow Update - Checkpoint Backup Step Added
**Priority**: INFORMATIONAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## WORKFLOW UPDATE

**User Directive**: "Add parquet backup step to the end of the pair merge process"

**Change**: BA will backup checkpoints to GCS **before** deletion (after EA merge complete)

---

## UPDATED PER-PAIR SEQUENCE

**No changes to EA's workflow**, only to BA's post-merge actions:

1. BA extracts (20-30 min)
2. BA notifies EA
3. **EA merges** (40-50 min) ← **NO CHANGE**
4. **EA notifies BA**: "Pair {pair} merge complete and validated" ← **NO CHANGE**
5. **BA backs up checkpoints** (1-2 min) ← **NEW STEP**
6. BA verifies backup (668 files)
7. BA deletes checkpoints
8. BA proceeds to next pair

---

## EA NOTIFICATION REMAINS UNCHANGED

**After EA completes merge**, send:
```
Message: "Pair {pair} merge complete and validated"
To: CE inbox + BA inbox
```

**BA will then**:
- Backup checkpoints to GCS
- Verify backup
- Delete local checkpoints
- Proceed to next pair

---

## TIMELINE IMPACT

**Per Pair**:
- EA merge: 40-50 min (unchanged)
- BA backup: +1-2 min (new)
- **Total**: 54-84 min per pair (was 52-82 min)

**27 Pairs Total**: 31 hours (was 30 hours)
**Impact**: +45 min total (minimal)

---

## BACKUP DETAILS

**Location**: `gs://bqx-ml-staging/{pair}_checkpoints_validated/`
**Size**: ~12 GB per pair
**Duration**: 1-2 min (parallel upload)
**Cost**: $0.31/month per pair, $8.74/month total for 28 pairs

**Purpose**: User mandate to preserve validated parquet files before deletion

---

## EA: NO ACTION REQUIRED

✅ **No changes to EA's workflow**
✅ Continue merge operations as authorized
✅ Continue notifications as planned
✅ BA handles backup step independently

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Workflow updated, EA informed (no action needed from EA)
**Impact**: +45 min to overall timeline (acceptable)
**User Mandate**: ✅ SATISFIED - All validated files will be backed up
