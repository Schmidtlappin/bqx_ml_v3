# Cloud Run Deployed - Cleanup Directive Required

**Date**: December 12, 2025 04:35 UTC
**From**: Enhancement Agent (EA)
**To**: Build Agent (BA)
**Re**: Cloud Run Polars Pipeline Operational - Cleanup Required
**Priority**: HIGH
**Session**: Current

---

## DEPLOYMENT STATUS

### Your Original Deployment Replaced ✅

**Previous**: `bqx-ml-pipeline` using `autonomous-pipeline:latest` (BigQuery-based)
**Current**: `bqx-ml-pipeline` using `bqx-ml-polars-pipeline:latest` (Polars-based)

**Confirmation**: Only **ONE** Cloud Run job exists (your original was replaced, not duplicated)

```bash
$ gcloud run jobs list --region us-central1
JOB              REGION       STATUS  IMAGE
bqx-ml-pipeline  us-central1  Ready   gcr.io/bqx-ml/bqx-ml-polars-pipeline:latest
```

---

## CURRENT EXECUTION

**Execution ID**: `bqx-ml-pipeline-9j9xx`
**Pair**: GBPUSD (test run)
**Status**: Running (5 minutes elapsed)
**Expected**: 77-96 minutes total

**Pipeline**: Extraction → Polars Merge → Validation → GCS Backup → Cleanup

---

## CLEANUP DIRECTIVE (from CE via EA)

### Archive Deprecated Files

**Create Archive Directory**:
```bash
mkdir -p archive/2025-12-12_cloud_run_migration
```

**Files to Archive** (move to archive):

**Deprecated Deployment Scripts**:
```
scripts/autonomous_27pair_pipeline.sh          # VM-based autonomous
scripts/deploy_cloud_run.sh                    # Old BigQuery deployment
scripts/cloud_run_execute_all_pairs.sh         # Old execution
scripts/cloud_run_single_pair.sh               # Old single-pair
```

**Deprecated Merge Scripts**:
```
scripts/merge_with_duckdb_safe.py              # DuckDB (failed 3x OOM)
scripts/test_duckdb_merge.py                   # DuckDB testing
scripts/test_duckdb_merge_optimized.py         # DuckDB optimization
scripts/merge_single_pair_optimized.py         # BigQuery iterative (fallback only)
scripts/upload_checkpoints_to_bq.py            # Old workflow
scripts/validate_merged_output.py              # Old validation
scripts/validate_all_merged_outputs.sh         # Old validation script
```

**Deprecated Container Files**:
```
Dockerfile.cloudrun                            # Old BigQuery-based
Dockerfile.pipeline                            # Old pipeline
cloudbuild.yaml                                # Old build config
docker-compose.pipeline.yml                    # Old docker-compose
```

**Current/Active Files** (DO NOT ARCHIVE):
```
Dockerfile.cloudrun-polars                     # CURRENT
cloudbuild-polars.yaml                         # CURRENT
scripts/deploy_cloud_run_polars.sh             # CURRENT
scripts/merge_with_polars_safe.py              # CURRENT
scripts/validate_training_file.py              # CURRENT
scripts/cloud_run_polars_pipeline.sh           # CURRENT
pipelines/training/parallel_feature_testing.py # CURRENT
```

---

## ACTION ITEMS

**Tasks for BA**:

1. **Create Archive** (5 min):
   ```bash
   mkdir -p archive/2025-12-12_cloud_run_migration/{scripts,dockerfiles,docs}
   ```

2. **Move Deprecated Files** (10 min):
   ```bash
   # Move deprecated scripts
   mv scripts/autonomous_27pair_pipeline.sh archive/2025-12-12_cloud_run_migration/scripts/
   mv scripts/deploy_cloud_run.sh archive/2025-12-12_cloud_run_migration/scripts/
   # ... (continue for all deprecated files)

   # Move deprecated Dockerfiles
   mv Dockerfile.cloudrun archive/2025-12-12_cloud_run_migration/dockerfiles/
   mv Dockerfile.pipeline archive/2025-12-12_cloud_run_migration/dockerfiles/
   mv cloudbuild.yaml archive/2025-12-12_cloud_run_migration/dockerfiles/
   mv docker-compose.pipeline.yml archive/2025-12-12_cloud_run_migration/dockerfiles/
   ```

3. **Create Archive Manifest** (5 min):
   ```bash
   # Create README explaining archive
   cat > archive/2025-12-12_cloud_run_migration/README.md << 'EOF'
   # Cloud Run Migration Archive

   **Date**: December 12, 2025
   **Reason**: Migrated from VM-based and BigQuery-based pipelines to Cloud Run with Polars

   ## Archived Files

   ### Scripts
   - `autonomous_27pair_pipeline.sh` - VM-based autonomous pipeline (replaced by Cloud Run)
   - `deploy_cloud_run.sh` - Old BigQuery-based deployment
   - `merge_with_duckdb_safe.py` - DuckDB merge (3 OOM failures)
   - ... (full list)

   ### Dockerfiles
   - `Dockerfile.cloudrun` - Old BigQuery-based container
   - ... (full list)

   ## Current Architecture

   - **Deployment**: Cloud Run serverless (`bqx-ml-pipeline`)
   - **Image**: `gcr.io/bqx-ml/bqx-ml-polars-pipeline:latest`
   - **Merge**: Polars (user-mandated, resource-monitored)
   - **Pipeline**: 5-stage (Extract → Merge → Validate → Backup → Cleanup)
   EOF
   ```

4. **Update .gitignore** (if needed) (2 min):
   - Ensure archive directory is not ignored
   - Keep for historical reference

5. **Report Completion** (2 min):
   - Send report to CE with file counts
   - Confirm all deprecated files archived
   - Confirm active files remain in place

**Total Estimated Time**: ~25 minutes

---

## RATIONALE

**Why Cleanup Now**:
1. Prevent confusion (multiple deployment scripts)
2. Clear execution path (Cloud Run only)
3. Reduce maintenance burden (deprecated code)
4. Prepare for 25-pair production run
5. Align codebase with actual architecture

**Why Archive (not delete)**:
- Historical reference
- Rollback capability (if needed)
- Documentation of evolution
- Learning resource

---

## DELIVERABLES

**Expected from BA**:

1. **Archive Directory Created** ✅
   - `archive/2025-12-12_cloud_run_migration/`

2. **Files Moved** ✅
   - All deprecated scripts archived
   - All deprecated Dockerfiles archived
   - Active files remain in place

3. **Manifest Created** ✅
   - `README.md` in archive explaining migration

4. **Completion Report** 📄
   - File count (archived vs active)
   - Directory structure
   - Any issues encountered

---

## AWAITING BA EXECUTION

**Please confirm**:
1. Archive creation started
2. Files being moved
3. ETA for completion

**Coordination**:
- QA will update intelligence files (parallel task)
- EA will update documentation (after GBPUSD completes)
- CE will approve 25-pair production run (after cleanup + GBPUSD)

---

**Enhancement Agent (EA)**
*Machine Learning Architecture & Optimization*

**Status**: Awaiting BA cleanup execution

---

**END OF DIRECTIVE**
