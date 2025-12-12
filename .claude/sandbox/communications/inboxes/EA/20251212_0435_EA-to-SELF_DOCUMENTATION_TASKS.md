# EA Documentation Tasks - Cloud Run Deployment

**Date**: December 12, 2025 04:35 UTC
**From**: Enhancement Agent (EA)
**To**: Enhancement Agent (EA)
**Re**: Documentation Updates Required for Cloud Run Deployment
**Priority**: MEDIUM
**Session**: Current

---

## SELF-ASSIGNED TASKS

### Documentation Updates After GBPUSD Completion

**Status**: GBPUSD test running (5 min elapsed, 72-91 min remaining)

**When to Start**: After GBPUSD execution completes successfully

---

## DOCUMENTATION TO CREATE

### 1. `docs/CLOUD_RUN_DEPLOYMENT_GUIDE.md` 🔴 HIGH PRIORITY

**Purpose**: Complete guide for deploying and executing Cloud Run pipeline

**Sections**:

1. **Overview**
   - Architecture diagram
   - Pipeline stages
   - Resource requirements

2. **Prerequisites**
   - GCP project setup
   - Service account permissions
   - Required APIs enabled

3. **Deployment Instructions**
   - Build container image
   - Deploy Cloud Run job
   - Verify deployment

4. **Execution Instructions**
   - Single pair execution
   - Batch execution (sequential)
   - Parallel execution (if applicable)
   - Monitoring execution status

5. **Cost Tracking**
   - Per-pair costs
   - Monthly storage costs
   - Total project costs
   - Cost optimization tips

6. **Troubleshooting**
   - Common errors
   - Debugging techniques
   - Log inspection
   - Rollback procedures

**Estimated Time**: 90 minutes

---

### 2. `docs/POLARS_MERGE_PROTOCOL.md` 🔴 HIGH PRIORITY

**Purpose**: Document Polars merge approach and lessons learned

**Sections**:

1. **Background**
   - Why Polars was chosen (user mandate)
   - Previous approaches (DuckDB failures)
   - Technical requirements

2. **Resource Management**
   - Soft monitoring approach (no hard limits)
   - Why hard limits fail with Polars
   - Memory usage patterns (AUDUSD: 48-50 GB peak)
   - Cloud Run containerization (12 GB limit works)

3. **Pre-Flight Checks**
   - Available memory check (40 GB min for VM)
   - Checkpoint file validation (668 files)
   - Disk space check (15 GB min)

4. **Merge Process**
   - Load targets first
   - Iterative feature joins
   - Progress logging (every 50 files)
   - Aggressive garbage collection

5. **Test Results**
   - EURUSD: 9.3 GB, 177K rows × 17K cols (local)
   - AUDUSD: 9.0 GB, 172K rows × 17K cols (local)
   - GBPUSD: [to be added after completion] (Cloud Run)

6. **Cloud Run Integration**
   - Container memory limits
   - Polars efficiency in containerized environment
   - Why it works despite 12 GB limit

**Estimated Time**: 60 minutes

---

### 3. `docs/TRAINING_FILE_VALIDATION_PROTOCOL.md` 🟡 MEDIUM PRIORITY

**Purpose**: Document validation requirements and procedures

**Sections**:

1. **Validation Requirements**
   - Minimum 100,000 rows
   - Minimum 10,000 columns
   - All 7 target horizons present (h15, h30, h45, h60, h75, h90, h105)
   - Feature count > 0
   - Null percentage < 80%
   - Date range valid

2. **Validation Script Usage**
   ```bash
   python3 scripts/validate_training_file.py \
     /path/to/training_eurusd.parquet \
     --pair eurusd \
     --required-targets 7 \
     --min-rows 100000 \
     --min-columns 10000
   ```

3. **Expected Outputs**
   - Success: Exit code 0, validation report
   - Failure: Exit code 1, error details

4. **Common Validation Failures**
   - Missing target columns
   - Insufficient rows
   - High null percentage
   - Date range issues

5. **Remediation Steps**
   - Re-extract from BigQuery
   - Re-merge with Polars
   - Check source data quality

**Estimated Time**: 45 minutes

---

## DOCUMENTATION TO UPDATE

### 1. `docs/CLOUD_RUN_POLARS_ARCHITECTURE.md` (exists) 🔴 HIGH PRIORITY

**Current Status**: Draft created during deployment planning

**Updates Needed**:

1. **Add Actual Results**:
   - AUDUSD local test: 13 min, 9.0 GB, validated
   - GBPUSD Cloud Run: [add after completion]
   - Actual Cloud Run build time: 3m 26s
   - Container image size: [check GCR]

2. **Update Cost Analysis**:
   - Confirm $0.71/pair for Cloud Run
   - Add actual build costs (if any)
   - Update total 28-pair estimate: $19.90

3. **Add Troubleshooting Section**:
   - apt-key deprecation fix
   - Memory limit errors (12Gi requires 4 CPUs)
   - Execution argument errors (--timeout → --task-timeout)

**Estimated Time**: 30 minutes

---

### 2. `docs/VM_HEALTH_MAINTENANCE_GUIDE.md` (exists) 🟡 MEDIUM PRIORITY

**Updates Needed**:

Add section:
```markdown
## Cloud Run Migration Impact

**Reduced VM Dependency**:
- Feature extraction now runs on Cloud Run (serverless)
- Polars merge runs in containerized environment
- VM only needed for:
  - Local testing
  - Alternative execution methods
  - Development work

**VM Health Monitoring**:
- Still important for local work
- Less critical for production pipeline
- Swap space incidents reduced (3 OOM events were pre-Cloud Run)
```

**Estimated Time**: 15 minutes

---

### 3. `docs/CONTAINERIZED_DEPLOYMENT_GUIDE.md` (exists) 🟡 MEDIUM PRIORITY

**Updates Needed**:

1. **Update to Polars-Based Container**:
   - Replace BigQuery merge references
   - Add Polars merge stage
   - Update Dockerfile references (`Dockerfile.cloudrun-polars`)

2. **Update Build Instructions**:
   - Modern GPG key management (apt-key → gpg --dearmor)
   - Updated cloudbuild.yaml reference

3. **Update Resource Specs**:
   - 4 CPUs (not 2)
   - 12 GB memory
   - 2-hour timeout

**Estimated Time**: 30 minutes

---

### 4. `docs/AUTONOMOUS_PIPELINE_GUIDE.md` (exists) 🟢 LOW PRIORITY

**Options**:

**Option A: Archive**
- Move to `archive/2025-12-12_cloud_run_migration/docs/`
- VM-based autonomous pipeline replaced by Cloud Run

**Option B: Update for Cloud Run**
- Rewrite for Cloud Run batch execution
- Sequential vs parallel execution strategies
- Cost considerations

**Recommendation**: Archive (let BA handle during cleanup)

**Estimated Time**: N/A (BA task)

---

## TIMELINE

### Phase 1: Wait for GBPUSD Completion
- **Duration**: ~72-91 minutes (in progress)
- **Action**: Monitor execution, capture results

### Phase 2: Create New Documentation
- **Task 1**: CLOUD_RUN_DEPLOYMENT_GUIDE.md (90 min)
- **Task 2**: POLARS_MERGE_PROTOCOL.md (60 min)
- **Task 3**: TRAINING_FILE_VALIDATION_PROTOCOL.md (45 min)
- **Total**: ~3 hours

### Phase 3: Update Existing Documentation
- **Task 1**: CLOUD_RUN_POLARS_ARCHITECTURE.md (30 min)
- **Task 2**: VM_HEALTH_MAINTENANCE_GUIDE.md (15 min)
- **Task 3**: CONTAINERIZED_DEPLOYMENT_GUIDE.md (30 min)
- **Total**: ~1.25 hours

**Total Documentation Time**: ~4.25 hours

---

## DELIVERABLES

**New Documentation**:
1. ✅ `docs/CLOUD_RUN_DEPLOYMENT_GUIDE.md`
2. ✅ `docs/POLARS_MERGE_PROTOCOL.md`
3. ✅ `docs/TRAINING_FILE_VALIDATION_PROTOCOL.md`

**Updated Documentation**:
1. ✅ `docs/CLOUD_RUN_POLARS_ARCHITECTURE.md`
2. ✅ `docs/VM_HEALTH_MAINTENANCE_GUIDE.md`
3. ✅ `docs/CONTAINERIZED_DEPLOYMENT_GUIDE.md`

**Completion Report**: Send to CE with doc count and summary

---

## COORDINATION

**Dependencies**:
- **GBPUSD Completion**: Must complete before finalizing docs (need actual results)
- **BA Cleanup**: Archive of deprecated docs (parallel task)
- **QA Updates**: Intelligence files (parallel task)

**After Documentation**:
- CE reviews all updates
- Authorizes 25-pair production run
- Final project completion

---

**Enhancement Agent (EA)**
*Machine Learning Architecture & Optimization*

**Status**: Awaiting GBPUSD completion to begin documentation

---

**END OF SELF-ASSIGNMENT**
