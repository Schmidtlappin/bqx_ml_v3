# CE DIRECTIVE: Cleanup Deprecated Cloud Run Infrastructure

**Date**: December 12, 2025 20:25 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Cleanup Before Bifurcated Architecture Implementation
**Priority**: P0-CRITICAL (PREREQUISITE)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## PREREQUISITE: CLEAN SLATE

**Before implementing bifurcated architecture** (20251212_2020 directive), cleanup deprecated infrastructure.

**Reason**: Avoid confusion, resource conflicts, and billing for unused resources

---

## CLEANUP ACTIONS

### 1. Delete Deprecated Cloud Run Jobs

```bash
# List existing Cloud Run jobs
gcloud run jobs list --region us-central1

# Delete old single-job pipeline (if exists)
gcloud run jobs delete bqx-ml-pipeline --region us-central1 --quiet || echo "No job to delete"

# Delete any test jobs
gcloud run jobs delete bqx-ml-test --region us-central1 --quiet || echo "No job to delete"
```

---

### 2. Delete Deprecated Container Images

```bash
# List container images
gcloud container images list --repository=gcr.io/bqx-ml

# Delete old images (keep only if needed for rollback)
gcloud container images delete gcr.io/bqx-ml/bqx-ml-pipeline:latest --quiet || true
gcloud container images delete gcr.io/bqx-ml/bqx-ml-polars-pipeline:latest --quiet || true

# List remaining images
gcloud container images list --repository=gcr.io/bqx-ml
```

---

### 3. Clean Up GCS Artifacts

```bash
# Clean up any failed execution checkpoints
gsutil -m rm -r gs://bqx-ml-staging/checkpoints/gbpusd/ 2>/dev/null || echo "No GBPUSD checkpoints"

# Clean up temporary files
gsutil -m rm gs://bqx-ml-staging/tmp/* 2>/dev/null || echo "No tmp files"

# Keep EURUSD/AUDUSD checkpoints if they exist (for reference)
```

---

### 4. Verify Clean State

```bash
echo "=== Cloud Run Jobs ==="
gcloud run jobs list --region us-central1

echo "=== Container Images ==="
gcloud container images list --repository=gcr.io/bqx-ml

echo "=== GCS Checkpoints ==="
gsutil ls gs://bqx-ml-staging/checkpoints/ || echo "Clean"

echo "=== GCS Output ==="
gsutil ls gs://bqx-ml-output/ || echo "Clean"
```

---

## EXPECTED RESULT

After cleanup:
- ✅ No old Cloud Run jobs
- ✅ No deprecated container images (or clearly marked as deprecated)
- ✅ GCS staging area clean (except valid EURUSD/AUDUSD if present)
- ✅ Ready for bifurcated architecture deployment

---

## TIMELINE

**Cleanup**: 10 minutes (20:25-20:35 UTC)
**Bifurcated Implementation**: Starts at 20:35 UTC (after cleanup complete)

---

**Chief Engineer (CE)**

**Action**: Clean deprecated infrastructure before new deployment

**Timeline**: 10 min cleanup, then proceed with bifurcated architecture

---

**END OF CLEANUP DIRECTIVE**
