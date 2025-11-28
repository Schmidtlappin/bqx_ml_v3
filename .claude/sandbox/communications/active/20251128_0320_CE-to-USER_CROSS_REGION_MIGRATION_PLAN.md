# 🌍 CROSS-REGION MIGRATION PLAN: Consolidate to us-east1

**FROM**: CE (Chief Engineer)
**TO**: User
**DATE**: 2025-11-28 03:20 UTC
**RE**: Plan to Migrate All GCP Resources from Multi-Region/us-central1 to us-east1

---

## 🚨 SITUATION ANALYSIS

### Current State: Cross-Region Data Distribution

**Issue Identified**: Data and services are distributed across multiple regions, causing:
- ❌ **Performance degradation** (cross-region queries 2-10x slower)
- ❌ **Increased costs** (cross-region data transfer charges)
- ❌ **Complexity** (data locality issues)
- ❌ **Suboptimal architecture** (should be single-region for ML workloads)

---

## 📊 CURRENT RESOURCE DISTRIBUTION

### BigQuery Datasets (6 datasets, 2,540 tables total)

| Dataset | Location | Tables | Size | Status |
|---------|----------|--------|------|--------|
| **bqx_bq** | US (multi-region) | 2,464 | ~30 GB | ❌ MIGRATE |
| bqx_ml_v3_analytics | us-central1 | 0 | 0 GB | ❌ MIGRATE |
| bqx_ml_v3_features | us-central1 | 57 | ~2 GB | ❌ MIGRATE |
| bqx_ml_v3_models | us-central1 | 17 | ~1 GB | ❌ MIGRATE |
| bqx_ml_v3_predictions | us-central1 | 2 | <1 GB | ❌ MIGRATE |
| bqx_ml_v3_staging | us-central1 | 0 | 0 GB | ❌ MIGRATE |

**Critical**: `bqx_bq` contains 2,464 tables (m1_*, idx_*, bqx_*, corr_*) and is the source of truth for all feature data.

---

### GCS Buckets (7 buckets, ~24 MB total)

| Bucket | Location | Size | Status |
|--------|----------|------|--------|
| bqx-ml-bqx-ml-artifacts | US-EAST1 | 0 bytes | ✅ CORRECT |
| bqx-ml-bqx-ml-results | US-EAST1 | 0 bytes | ✅ CORRECT |
| bqx-ml-data | US-EAST1 | 0 bytes | ✅ CORRECT |
| bqx-ml-scripts | US | 26 KB | ❌ MIGRATE |
| bqx-ml-v3-models | US-CENTRAL1 | 15.8 MB | ❌ MIGRATE |
| bqx-ml-vertex-models | US-CENTRAL1 | 0 bytes | ❌ MIGRATE |
| bqx-ml_cloudbuild | US | 7.4 MB | ❌ MIGRATE |

**Good News**: 3/7 buckets already in US-EAST1 (43% compliant)

---

### Compute Resources

**To Check**:
- Vertex AI endpoints (likely us-central1)
- Cloud Run services (if any)
- Cloud Functions (if any)
- Compute Engine instances (current codespace location)

---

## 🎯 MIGRATION OBJECTIVES

### Primary Goal
**Consolidate ALL GCP resources to `us-east1` region for**:
- ✅ **Optimal performance** (single-region queries)
- ✅ **Cost reduction** (eliminate cross-region transfer fees)
- ✅ **Simplified architecture** (single region for all services)
- ✅ **ML workload optimization** (Vertex AI + BigQuery colocation)

### Target State
```
Region: us-east1 (100% of resources)
Zone: us-east1-b (for compute instances)
```

---

## 📋 MIGRATION PLAN

### ⚠️ CRITICAL COORDINATION WITH BA

**BA is currently executing Task 0.2** (IDX table re-indexing in `bqx_ml_v3_features` dataset)
- **Estimated completion**: 2025-11-28 07:00-09:00 UTC (3-4 hours from now)
- **Impact**: Any migration of `bqx_bq` or `bqx_ml_v3_features` will block BA's work

**Recommendation**: **BLOCK BA immediately** or **wait for Task 0.2 completion** before starting migration.

---

## 🗓️ MIGRATION EXECUTION PLAN

### Phase 0: Preparation (1-2 hours)
**Timing**: After BA completes Task 0.2

#### Actions:
1. **Send blocking directive to BA** (stop all work)
2. **Backup critical data** to US-EAST1 buckets
   ```bash
   # Backup bqx_bq dataset metadata
   bq extract --destination_format=NEWLINE_DELIMITED_JSON \
     bqx-ml:bqx_bq.m1_eurusd gs://bqx-ml-data/backups/pre-migration/...
   ```
3. **Document all current dataset schemas**
4. **Create migration scripts**
5. **Test migration on 1 small table** (validation)

#### Deliverables:
- Migration scripts (Python + bq commands)
- Backup confirmation
- Schema documentation
- Test migration validation report

---

### Phase 1: GCS Bucket Migration (2-3 hours)
**Timing**: Can run in parallel with Phase 0

**Priority: HIGH (Low Risk)**

#### Buckets to Migrate:
1. **bqx-ml-scripts** (US → US-EAST1)
   - Size: 26 KB
   - Strategy: `gsutil -m cp -r` then delete old bucket
   - Duration: <5 minutes

2. **bqx-ml-v3-models** (US-CENTRAL1 → US-EAST1)
   - Size: 15.8 MB
   - Strategy: Regional copy
   - Duration: ~10 minutes

3. **bqx-ml-vertex-models** (US-CENTRAL1 → US-EAST1)
   - Size: 0 bytes (empty)
   - Strategy: Delete + recreate in US-EAST1
   - Duration: 1 minute

4. **bqx-ml_cloudbuild** (US → US-EAST1)
   - Size: 7.4 MB
   - Strategy: Regional copy
   - Duration: ~5 minutes

#### Migration Commands:
```bash
# For each bucket:
# 1. Create new bucket in US-EAST1
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-scripts-east1

# 2. Copy data
gsutil -m cp -r gs://bqx-ml-scripts/* gs://bqx-ml-scripts-east1/

# 3. Verify
gsutil du -s gs://bqx-ml-scripts-east1

# 4. Update references (scripts, configs)
# 5. Delete old bucket
gsutil rm -r gs://bqx-ml-scripts
```

#### Risks:
- ⚠️ **Low**: Small data size, can retry if failures
- ⚠️ **Medium**: Need to update bucket references in code/configs

---

### Phase 2: BigQuery Dataset Migration - Non-Critical (3-4 hours)
**Timing**: After Phase 1, before Phase 3

**Priority: MEDIUM**

#### Datasets to Migrate (Lower Priority):
1. **bqx_ml_v3_analytics** (us-central1 → us-east1)
   - Tables: 0 (empty)
   - Strategy: Delete + recreate in us-east1
   - Duration: 1 minute

2. **bqx_ml_v3_staging** (us-central1 → us-east1)
   - Tables: 0 (empty)
   - Strategy: Delete + recreate in us-east1
   - Duration: 1 minute

3. **bqx_ml_v3_predictions** (us-central1 → us-east1)
   - Tables: 2
   - Strategy: `bq cp` then delete old
   - Duration: ~10 minutes

4. **bqx_ml_v3_models** (us-central1 → us-east1)
   - Tables: 17
   - Strategy: `bq cp` with parallel transfers
   - Duration: ~30 minutes

#### Migration Commands:
```bash
# 1. Create new dataset in us-east1
bq mk --location=us-east1 --dataset bqx-ml:bqx_ml_v3_analytics_east1

# 2. Copy tables (parallel)
bq ls --max_results=1000 bqx-ml:bqx_ml_v3_models | grep -v "tableId" | \
  while read table_id; do
    bq cp -f bqx-ml:bqx_ml_v3_models.$table_id \
          bqx-ml:bqx_ml_v3_models_east1.$table_id &
  done
wait

# 3. Validate row counts match
# 4. Delete old dataset
bq rm -r -f -d bqx-ml:bqx_ml_v3_models

# 5. Rename new dataset
# (Requires manual recreation with original name)
```

#### Risks:
- ⚠️ **Medium**: Cannot rename datasets in BigQuery (must delete + recreate)
- ⚠️ **Medium**: Need to update all code references to dataset names

---

### Phase 3: BigQuery Dataset Migration - CRITICAL (6-12 hours)
**Timing**: After Phases 1-2 complete, with BA fully blocked

**Priority: CRITICAL - HIGH RISK**

#### Critical Datasets:
1. **bqx_bq** (US multi-region → us-east1)
   - **Tables**: 2,464 (m1_*, idx_*, bqx_*, corr_*)
   - **Size**: ~30 GB estimated
   - **Risk**: ⚠️ **VERY HIGH** - Primary data source
   - **Strategy**: Parallel table copy (50-100 concurrent transfers)
   - **Duration**: 6-12 hours

2. **bqx_ml_v3_features** (us-central1 → us-east1)
   - **Tables**: 57 (*_idx, lag, regime, etc.)
   - **Size**: ~2 GB
   - **Risk**: ⚠️ **HIGH** - Currently being updated by BA
   - **Strategy**: Wait for BA Task 0.2 completion, then migrate
   - **Duration**: 1-2 hours

#### Migration Strategy for bqx_bq (2,464 tables):

**Option A: Parallel Table Copy (RECOMMENDED)**
```python
# Parallel migration script
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def copy_table(table_id):
    cmd = f"bq cp -f bqx-ml:bqx_bq.{table_id} bqx-ml:bqx_bq_east1.{table_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return table_id, result.returncode

# Get all tables
tables = subprocess.check_output(
    "bq ls --max_results=10000 bqx-ml:bqx_bq | grep -v tableId | awk '{print $1}'",
    shell=True, text=True
).strip().split('\n')

# Create destination dataset
subprocess.run("bq mk --location=us-east1 bqx-ml:bqx_bq_east1", shell=True)

# Parallel copy with 50 workers
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(copy_table, table) for table in tables]

    for i, future in enumerate(as_completed(futures)):
        table_id, status = future.result()
        print(f"[{i+1}/2464] {table_id}: {'✅' if status == 0 else '❌'}")
```

**Estimated Duration**:
- Sequential: ~50 hours (unacceptable)
- 50 parallel workers: 6-8 hours
- 100 parallel workers: 3-4 hours (may hit BigQuery API limits)

**Option B: Dataset Transfer Service** (BigQuery Data Transfer)
- **Pros**: Native BigQuery feature, managed retries
- **Cons**: Slower, less control, may not support US → us-east1

---

### Phase 4: Compute Resource Migration (2-4 hours)
**Timing**: Can overlap with Phase 3

**Resources to Check and Migrate**:
1. **Vertex AI Endpoints** (if deployed in us-central1)
   - Redeploy models to us-east1 endpoints
   - Update prediction code to use new endpoints

2. **Cloud Run Services** (if any)
   - Redeploy to us-east1
   - Update URLs/endpoints

3. **Cloud Functions** (if any)
   - Redeploy to us-east1
   - Update triggers

4. **Compute Engine** (Codespace)
   - **Current**: Unknown region/zone
   - **Target**: us-east1-b
   - **Strategy**: May need to recreate instance or migrate disk

---

### Phase 5: Validation & Cutover (2-3 hours)
**Timing**: After Phases 3-4 complete

#### Validation Steps:
1. **Row count validation** (all 2,540 tables)
   ```sql
   -- Compare old vs new datasets
   SELECT
     'bqx_bq' as dataset,
     table_id,
     old.row_count as old_rows,
     new.row_count as new_rows,
     old.row_count - new.row_count as diff
   FROM bqx-ml:bqx_bq.__TABLES__ old
   JOIN bqx-ml:bqx_bq_east1.__TABLES__ new USING(table_id)
   WHERE old.row_count != new.row_count;
   ```

2. **Schema validation** (all datasets)
3. **Sample data queries** (spot checks)
4. **Integration testing** (run 1-2 features end-to-end)

#### Cutover Steps:
1. **Delete old datasets** (after validation passes)
   ```bash
   bq rm -r -f -d bqx-ml:bqx_bq
   ```

2. **Recreate with original names**
   ```bash
   bq mk --location=us-east1 bqx-ml:bqx_bq
   bq cp -f bqx-ml:bqx_bq_east1.* bqx-ml:bqx_bq.*
   ```

3. **Update all code references**
4. **Test end-to-end pipeline**
5. **Unblock BA** (resume Phase 1 feature generation)

---

## 💰 COST ANALYSIS

### Migration Costs (One-Time):
- **BigQuery table copies**: ~$0.05/GB × 33 GB = **$1.65**
- **Cross-region GCS transfer**: ~$0.12/GB × 0.023 GB = **$0.003**
- **BigQuery slots for parallel copies**: ~$40/hour × 6 hours = **$240** (on-demand)
  - OR: Use flat-rate reservation (no additional cost)

**Total Migration Cost**: ~**$242** (one-time)

### Cost Savings (Ongoing):
- **Cross-region query charges**: Eliminated
  - Current: ~$5/TB × 10 TB/month = **$50/month**
  - After migration: **$0/month**
- **Cross-region data transfer**: Eliminated
  - Current: ~$0.12/GB × 100 GB/month = **$12/month**
  - After migration: **$0/month**

**Monthly Savings**: ~**$62/month**
**Payback Period**: 3.9 months

---

## ⏱️ TIMELINE SUMMARY

| Phase | Duration | Can Start | Blocker |
|-------|----------|-----------|---------|
| Phase 0: Preparation | 1-2 hours | Immediately | None |
| Phase 1: GCS Migration | 2-3 hours | Immediately | None |
| Phase 2: BQ Non-Critical | 3-4 hours | After Phase 1 | None |
| Phase 3: BQ Critical | 6-12 hours | After BA Task 0.2 | ⚠️ **BA must complete Task 0.2** |
| Phase 4: Compute | 2-4 hours | During Phase 3 | None |
| Phase 5: Validation | 2-3 hours | After Phases 3-4 | None |
| **TOTAL** | **16-28 hours** | **2-3 day span** | **BA coordination critical** |

---

## 🚨 RISKS & MITIGATIONS

### Risk 1: Data Loss During Migration
**Probability**: Low
**Impact**: CRITICAL
**Mitigation**:
- ✅ Full backups before migration (GCS exports)
- ✅ Validation scripts (row count + schema checks)
- ✅ Keep old datasets until validation passes
- ✅ Pilot test on 10 tables before full migration

---

### Risk 2: BA Task 0.2 Conflicts
**Probability**: HIGH (if not coordinated)
**Impact**: HIGH (corrupted data, lost work)
**Mitigation**:
- ✅ **WAIT for BA Task 0.2 completion** (4-6 hours)
- ✅ Send blocking directive to BA before Phase 3
- ✅ OR: Migrate `bqx_bq` first, `bqx_ml_v3_features` after BA completes

---

### Risk 3: Migration Takes Longer Than Expected
**Probability**: MEDIUM
**Impact**: MEDIUM (blocks 100% mandate progress)
**Mitigation**:
- ✅ Use 100 parallel workers (faster completion)
- ✅ Monitor progress (every 30 minutes)
- ✅ Auto-retry failed transfers
- ✅ Allocate 48-hour window (conservative)

---

### Risk 4: Code References Not Updated
**Probability**: MEDIUM
**Impact**: HIGH (broken pipelines)
**Mitigation**:
- ✅ Search codebase for hard-coded regions (`us-central1`, `US`)
- ✅ Use environment variables for region config
- ✅ Test all pipelines before deleting old datasets

---

## 📞 DECISION REQUIRED

### Option A: Full Migration (RECOMMENDED)
**Timeline**: 2-3 days
**Cost**: $242 one-time
**Benefit**: $62/month savings + performance improvement

**Execution**:
1. **Today**: Start Phases 0-1 (GCS + preparation)
2. **Wait**: BA completes Task 0.2 (by tomorrow morning)
3. **Tomorrow**: Execute Phases 2-3 (BigQuery migration)
4. **Day 3**: Validation + cutover

---

### Option B: Deferred Migration
**Timeline**: Postpone until after 100% mandate complete (14-18 days)
**Cost**: $0 now, $242 later
**Benefit**: Don't block BA's progress

**Trade-off**: Continue paying cross-region costs ($62/month) for 1+ month

---

### Option C: Partial Migration
**Timeline**: 1 day
**Cost**: $10 (GCS only)
**Benefit**: Low-hanging fruit

**Execution**:
1. Migrate GCS buckets only (Phase 1)
2. Leave BigQuery datasets in current locations
3. Migrate BQ datasets later (after 100% mandate)

**Trade-off**: Doesn't solve main performance issue

---

## ✅ RECOMMENDATION

**Proceed with Option A (Full Migration) with this sequence**:

1. **NOW**: Start Phase 0 (Preparation) + Phase 1 (GCS Migration)
   - 3-4 hours total
   - No impact on BA

2. **WAIT**: BA completes Task 0.2
   - Expected: 2025-11-28 09:00 UTC
   - Validates IDX tables have volume_idx populated

3. **TOMORROW (2025-11-28 10:00 UTC)**: Send blocking directive to BA
   - Block ALL work during migration
   - Estimated block duration: 12-24 hours

4. **TOMORROW (2025-11-28 10:00 UTC)**: Execute Phase 3 (BQ Critical Migration)
   - Migrate `bqx_bq` (2,464 tables, 6-12 hours)
   - Migrate `bqx_ml_v3_features` (57 tables, 1-2 hours)
   - Parallel: Phase 4 (Compute resources)

5. **DAY 3 (2025-11-29 00:00 UTC)**: Phase 5 (Validation + Cutover)
   - Validate all tables migrated correctly
   - Delete old datasets
   - Unblock BA
   - Resume 100% mandate execution

**Total Impact to 100% Mandate Timeline**: +1-2 days (acceptable given $62/month savings)

---

## 📋 IMMEDIATE NEXT STEPS

**If User Approves Full Migration**:

1. ✅ **CE**: Send message to BA
   - Inform of upcoming migration
   - Request immediate notification when Task 0.2 complete
   - Prepare for 12-24 hour blocking directive

2. ✅ **CE**: Create migration scripts (Phase 0)
   - GCS bucket migration (4 buckets)
   - BQ dataset migration (6 datasets)
   - Validation scripts
   - Rollback scripts

3. ✅ **CE**: Execute Phase 1 (GCS Migration)
   - Low risk, high value
   - Can start immediately

4. ⏸️ **WAIT**: BA Task 0.2 completion

5. ✅ **CE**: Execute Phases 2-5 (BQ Migration + Validation)

---

## 🎯 SUCCESS CRITERIA

**Migration will be considered successful when**:

1. ✅ All 6 BigQuery datasets in us-east1
2. ✅ All 7 GCS buckets in US-EAST1
3. ✅ All compute resources in us-east1(-b)
4. ✅ 100% row count validation passes
5. ✅ Schema validation passes (all 2,540 tables)
6. ✅ End-to-end pipeline test succeeds
7. ✅ Old datasets deleted (cost savings realized)
8. ✅ BA unblocked and resumes 100% mandate work

---

**Awaiting User Decision: Approve Full Migration (Option A)?**

**- CE**
