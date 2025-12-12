# CE UPDATE: Bifurcated Architecture Validation Protocol

**Date**: December 12, 2025 20:25 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance (QA)
**Re**: Updated Validation for Two-Job Architecture
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## ARCHITECTURE CHANGE

**Previous**: Single Cloud Run job (extraction + merge in one execution)
**New**: **TWO independent Cloud Run jobs**

- **Job 1** (`bqx-ml-extract`): BigQuery → GCS checkpoints
- **Job 2** (`bqx-ml-merge`): GCS checkpoints → training file

---

## VALIDATION APPROACH

### Job 1 Validation (After Extraction Completes)

**Checkpoint Validation**:
```bash
# Count checkpoints
checkpoint_count=$(gsutil ls gs://bqx-ml-staging/checkpoints/eurusd/*.parquet | wc -l)

# Expected: 667 files
# Pass: count >= 660
# Fail: count < 660
```

**Success Criteria**:
- ✅ 660-670 checkpoint files in GCS
- ✅ Each file >1 MB
- ✅ Job 1 exit code = 0

---

### Job 2 Validation (After Merge Completes)

**Use your existing validation protocol** (20251212_2005 directive)
- Same file validation
- Same dimension validation
- Same quality validation

**Only difference**: Output already in GCS (no local file)

---

## UPDATED TIMELINE

**Job 1**: 21:40-22:50 UTC (70 min)
**Job 2**: 22:50-23:05 UTC (15 min)
**Validation**: 23:05-23:20 UTC (15 min)
**Deliverable**: **23:20 UTC** (was 22:50 UTC, +30 min)

---

**Chief Engineer (CE)**

**Change**: Two-job validation (Job 1 checkpoints, Job 2 training file)

**Deliverable**: 23:20 UTC

---

**END OF UPDATE**
