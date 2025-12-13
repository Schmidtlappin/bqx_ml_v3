# 25-Pair Production Rollout Quality Checklist

**Version**: 1.0.0
**Created**: December 12, 2025 20:10 UTC
**Author**: Quality Assurance (QA)
**Purpose**: Quality validation checklist for 25-pair Cloud Run production rollout
**Applies To**: 25 remaining pairs after EURUSD, AUDUSD, GBPUSD complete
**Status**: ACTIVE

---

## TABLE OF CONTENTS

1. [Pre-Execution Validation](#pre-execution-validation)
2. [Execution Monitoring](#execution-monitoring)
3. [Post-Execution Validation](#post-execution-validation)
4. [Pass/Fail Criteria](#passfail-criteria)
5. [Escalation Procedure](#escalation-procedure)
6. [Rollout Progress Tracking](#rollout-progress-tracking)
7. [Quality Metrics](#quality-metrics)

---

## PRE-EXECUTION VALIDATION (Per Pair)

### Environment Checks

Execute these checks BEFORE starting each pair execution:

- [ ] **Cloud Run job operational**: `gcloud run jobs describe bqx-ml-pipeline --region=us-central1`
  - Status: READY
  - Image: `gcr.io/bqx-ml/bqx-ml-pipeline:optimized`
  - Build ID: `bf5beb92-2d82-49ea-9cfe-d15d2c654ae8`

- [ ] **GCS bucket writable**: `gsutil ls gs://bqx-ml-output/`
  - Bucket exists and accessible
  - Write permissions confirmed

- [ ] **BigQuery datasets accessible**:
  ```bash
  bq show bqx-ml:bqx_ml_v3_features_v2
  bq show bqx-ml:bqx_bq_uscen1_v2
  ```
  - Both datasets accessible
  - No permission errors

- [ ] **Service account permissions valid**:
  - Account: `bqx-ml-pipeline@bqx-ml.iam.gserviceaccount.com`
  - Roles: Cloud Run Invoker, BigQuery Data Viewer, Storage Object Admin

---

### Input Validation

Verify pair data exists in BigQuery:

- [ ] **Pair exists in source dataset**:
  ```sql
  SELECT COUNT(*) as row_count
  FROM `bqx-ml.bqx_bq_uscen1_v2.base_bqx_{pair}`
  ```
  - Expected: >100,000 rows
  - Actual: __________ rows

- [ ] **Feature tables present**:
  ```bash
  bq ls bqx-ml:bqx_ml_v3_features_v2 | grep -i {pair} | wc -l
  ```
  - Expected: 667 tables
  - Actual: __________ tables

- [ ] **Target table exists**:
  ```sql
  SELECT COUNT(*) as target_count
  FROM `bqx-ml.bqx_ml_v3_analytics_v2.targets_{pair}`
  ```
  - Expected: >100,000 rows
  - Actual: __________ rows

---

### Resource Availability

- [ ] **BigQuery quota available**:
  ```bash
  # Check current slot usage
  bq show --location=us-central1 --reservation
  ```
  - Current usage: <80% of quota
  - Available slots: ________

- [ ] **GCS storage quota**:
  ```bash
  gsutil du -s gs://bqx-ml-output/
  ```
  - Current usage: <80% of quota
  - Available GB: ________

- [ ] **Cloud Run concurrent executions**:
  ```bash
  gcloud run jobs executions list --job=bqx-ml-pipeline --region=us-central1 --filter="status.runningCount>0" --limit=10
  ```
  - Running executions: ________
  - Within concurrency limit: YES / NO

---

## EXECUTION MONITORING (Per Pair)

### Stage 1: BigQuery Extraction (Expected: 60-75 min)

Check every 15 minutes during extraction:

- [ ] **Execution started**:
  ```bash
  gcloud run jobs executions describe {execution-id} --region=us-central1
  ```
  - Start time: __________ UTC
  - Status: RUNNING

- [ ] **No errors in logs**:
  ```bash
  gcloud run jobs executions logs {execution-id} --region=us-central1 | grep -i error
  ```
  - Errors found: __________ (Expected: 0)

- [ ] **Checkpoints created**:
  ```bash
  gsutil ls gs://bqx-ml-staging/checkpoints/{pair}/*.parquet | wc -l
  ```
  - Current count: __________ (approaching 667)

- [ ] **Memory usage monitoring**:
  - Check Cloud Run logs for memory warnings
  - Expected: <12 GB
  - Current: __________ GB

---

### Stage 2: Polars Merge (Expected: 13-20 min)

- [ ] **Merge started**:
  - Log message: "Starting Polars merge"
  - Timestamp: __________ UTC

- [ ] **Memory stable**:
  - No rapid memory growth
  - No OOM warnings

- [ ] **Progress logging**:
  - Checkpoint count logged
  - Merge time estimated

---

### Stage 3: Validation (Expected: 1-2 min)

- [ ] **Validation script executed**:
  - Script: `validate_merged_output.py`
  - Exit code: 0 (success)

- [ ] **All checks passed**:
  - Schema validation: PASS
  - Row count validation: PASS
  - Column count validation: PASS
  - Data quality validation: PASS

---

### Stage 4: GCS Backup (Expected: 2-3 min)

- [ ] **File uploaded to GCS**:
  ```bash
  gsutil ls gs://bqx-ml-output/training_{pair}_h15-h105.parquet
  ```
  - File exists: YES / NO
  - Upload time: __________ UTC

- [ ] **File size matches local**:
  - Local size: __________ MB
  - GCS size: __________ MB
  - Match: YES / NO

---

### Stage 5: Cleanup (Expected: 1 min)

- [ ] **Checkpoints removed**:
  ```bash
  gsutil ls gs://bqx-ml-staging/checkpoints/{pair}/ 2>&1 | grep "CommandException"
  ```
  - Checkpoints deleted: YES / NO

- [ ] **Local files removed**:
  - Training file removed from Cloud Run container
  - Cleanup logged

---

## POST-EXECUTION VALIDATION (Per Pair)

### File Validation

- [ ] **File exists in GCS**:
  ```bash
  gsutil ls -lh gs://bqx-ml-output/training_{pair}_h15-h105.parquet
  ```
  - File exists: YES / NO
  - File size: __________ GB

- [ ] **File readable**:
  ```python
  import polars as pl
  df = pl.read_parquet(f'gs://bqx-ml-output/training_{pair}_h15-h105.parquet')
  print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
  ```
  - Readable: YES / NO
  - No corruption errors

---

### Dimension Validation

Based on benchmarks (updated after GBPUSD):

| Metric | EURUSD | AUDUSD | GBPUSD | Expected Range |
|--------|--------|--------|--------|----------------|
| Rows | 177,748 | ~177K | TBD | 150K-200K |
| Columns | 17,038 | ~17K | TBD | 16K-18K |
| File Size (GB) | 9.3 | 9.0 | TBD | 8-11 GB |

**Validation**:
- [ ] **Row count**: __________ (within 150K-200K range)
- [ ] **Column count**: __________ (within 16K-18K range)
- [ ] **File size**: __________ GB (within 8-11 GB range)

---

### Target Coverage Validation

All 49 targets must be present (7 horizons × 7 BQX windows):

- [ ] **h15 targets**: 7 columns (bqx_45_h15, bqx_90_h15, ..., bqx_2880_h15)
- [ ] **h30 targets**: 7 columns
- [ ] **h45 targets**: 7 columns
- [ ] **h60 targets**: 7 columns
- [ ] **h75 targets**: 7 columns
- [ ] **h90 targets**: 7 columns
- [ ] **h105 targets**: 7 columns

**Total targets**: __________ (Expected: 49)

---

### Data Quality Validation

- [ ] **No NULL values in critical columns**:
  ```python
  null_counts = df.select([
      pl.col('interval_time').is_null().sum().alias('interval_time_nulls'),
      pl.col('pair').is_null().sum().alias('pair_nulls')
  ])
  ```
  - interval_time NULLs: __________ (Expected: 0)
  - pair NULLs: __________ (Expected: 0)

- [ ] **Feature columns NULL check**:
  ```python
  feature_nulls = df.select([
      pl.col(c).is_null().mean() for c in feature_columns
  ])
  max_null_pct = feature_nulls.max()
  ```
  - Max NULL percentage: __________% (Expected: <5%)

- [ ] **Target columns NULL check**:
  ```python
  target_nulls = df.select([
      pl.col(c).is_null().mean() for c in target_columns
  ])
  max_target_null_pct = target_nulls.max()
  ```
  - Max NULL percentage: __________% (Expected: <1%)

- [ ] **No duplicate rows**:
  ```python
  duplicates = len(df) - df.unique(subset=['interval_time', 'pair']).shape[0]
  ```
  - Duplicate count: __________ (Expected: 0)

---

### Performance Metrics

- [ ] **Execution time**:
  - Start time: __________ UTC
  - End time: __________ UTC
  - Duration: __________ minutes
  - Expected: 77-150 minutes
  - Within range: YES / NO

- [ ] **Cost estimate**:
  - BigQuery processing: $__________
  - Cloud Run execution: $__________
  - GCS storage/transfer: $__________
  - **Total**: $__________ (Expected: <$1.50)

- [ ] **Retry count**:
  - Retries: __________ (Expected: ≤2)
  - Retry reason (if any): __________

---

## PASS/FAIL CRITERIA

### PASS Criteria

**All of the following must be true**:

- ✅ File exists in GCS and is readable
- ✅ Row count within 150K-200K range (±25% of benchmark)
- ✅ Column count within 16K-18K range (±10% of benchmark)
- ✅ File size within 8-11 GB range (±20% of benchmark)
- ✅ All 49 targets present
- ✅ No NULL values in interval_time, pair
- ✅ <5% NULL values in features
- ✅ <1% NULL values in targets
- ✅ No duplicate rows
- ✅ Execution time <180 minutes (3 hours)
- ✅ Cost <$2.00

**If ALL criteria met** → **PASS**

---

### FAIL Criteria

**Any of the following causes FAIL**:

- ❌ File missing or corrupted (cannot read)
- ❌ Row count outside 150K-200K range (>25% variance)
- ❌ Column count outside 16K-18K range (>10% variance)
- ❌ Missing targets (< 49 targets present)
- ❌ NULL values in interval_time or pair
- ❌ >5% NULL values in any feature
- ❌ >1% NULL values in any target
- ❌ Execution time >180 minutes (timeout)
- ❌ Cost >$2.00

**If ANY failure criterion met** → **FAIL**

---

## ESCALATION PROCEDURE

### If PASS

**Actions**:
1. ✅ Document validation results in tracking sheet
2. ✅ Mark pair as COMPLETE in progress tracker
3. ✅ Proceed to next pair execution
4. ✅ Update intelligence files (every 5 pairs)

**No escalation needed - continue rollout**

---

### If FAIL

**STOP Rollout Immediately**

**Escalation Steps**:

1. **STOP**: Pause all executions immediately
   - Do NOT start next pair
   - Document failure timestamp and details

2. **ALERT**: Notify CE within 15 minutes
   ```markdown
   Subject: P0-CRITICAL: {PAIR} Validation FAILED

   Pair: {pair}
   Failure: {specific criterion failed}
   Impact: Production rollout paused
   Next: Root cause analysis required
   ```

3. **ANALYZE**: Root cause analysis
   - Review Cloud Run logs
   - Check BigQuery data
   - Compare to successful pairs
   - Identify failure pattern

4. **FIX**: Implement corrective action
   - Fix identified issue
   - Test fix in isolation
   - Document fix in remediation log

5. **RETRY**: Re-run failed pair
   - Use same validation checklist
   - Monitor closely for recurrence
   - Document retry results

6. **VALIDATE**: Full validation on retry
   - All validation criteria must pass
   - No partial passes accepted

7. **RESUME**: Continue rollout only after validation passes
   - Do NOT resume if second failure occurs
   - Escalate to CE for comprehensive review

---

## ROLLOUT PROGRESS TRACKING

### 25 Pairs Remaining (After EURUSD, AUDUSD, GBPUSD)

**Major Pairs** (8):
- [ ] USDJPY
- [ ] USDCHF
- [ ] USDCAD
- [ ] NZDUSD

**EUR Crosses** (5):
- [ ] EURGBP
- [ ] EURJPY
- [ ] EURCHF
- [ ] EURAUD
- [ ] EURCAD
- [ ] EURNZD

**GBP Crosses** (5):
- [ ] GBPJPY
- [ ] GBPCHF
- [ ] GBPAUD
- [ ] GBPCAD
- [ ] GBPNZD

**Other Crosses** (7):
- [ ] AUDJPY
- [ ] AUDCHF
- [ ] AUDCAD
- [ ] AUDNZD
- [ ] NZDJPY
- [ ] NZDCHF
- [ ] NZDCAD
- [ ] CADJPY
- [ ] CADCHF
- [ ] CHFJPY

**Total**: 25 pairs (verify count = 28 total - 3 complete)

---

### Execution Timeline Estimates

Based on EURUSD (77 min), AUDUSD (90 min), GBPUSD (TBD):

**Sequential Execution**:
- Average time per pair: [Update after GBPUSD] minutes
- Total time: 25 × [avg_time] = __________ hours
- Calendar time: __________ days (assuming 24/7 execution)

**Parallel Execution (2x)**:
- Concurrent pairs: 2
- Total executions: 13 batches (25 pairs / 2)
- Total time: 13 × [avg_time] = __________ hours
- Calendar time: __________ days

**Parallel Execution (4x)**:
- Concurrent pairs: 4
- Total executions: 7 batches (25 pairs / 4, rounded up)
- Total time: 7 × [avg_time] = __________ hours
- Calendar time: __________ days

**Recommended Approach**: [CE to determine based on cost/timeline trade-offs]

---

## QUALITY METRICS

### Per-Pair Metrics

Track for each pair execution:

| Metric | Value | Target |
|--------|-------|--------|
| Execution time (min) | __________ | 77-150 |
| Cost ($) | __________ | <$1.50 |
| Retry count | __________ | ≤2 |
| Validation status | PASS / FAIL | PASS |
| Issues identified | __________ | 0 |
| Row count | __________ | 150K-200K |
| Column count | __________ | 16K-18K |
| File size (GB) | __________ | 8-11 |

---

### Aggregate Metrics (Rolling)

Update after each pair:

| Metric | Current | Target |
|--------|---------|--------|
| **Pairs completed** | ____ / 25 | 25 |
| **Pass rate** | ____% | 100% |
| **Average execution time** | ____ min | 77-150 |
| **Average cost** | $____ | <$1.50 |
| **Total cost** | $____ | <$37.50 |
| **Total time** | ____ hours | Variable |
| **Issues encountered** | ____ | 0 |
| **Retries required** | ____ | <5 |

---

### Quality Dashboard

**Daily Summary Report** (At end of each day):

```markdown
# Daily Rollout Progress Report

**Date**: YYYY-MM-DD
**Pairs Completed Today**: X
**Pairs Remaining**: Y

## Metrics
- Pass Rate: XX%
- Average Execution Time: XX min
- Average Cost: $X.XX
- Issues: X

## Status
- On track: YES / NO
- Blockers: [List any blockers]
- ETA to completion: [Date]

## Next Actions
- [List next day's planned pairs]
```

---

## APPENDIX A: VALIDATION SCRIPT USAGE

### Quick Validation Command

```bash
python3 scripts/validate_merged_output.py {pair} \
  --check-schema \
  --check-row-count \
  --check-column-count \
  --check-targets \
  --check-nulls \
  --check-duplicates \
  --output-report validation_report_{pair}.txt
```

**Expected Output**:
```
✅ Schema validation: PASS
✅ Row count: 177,748 (within range)
✅ Column count: 17,038 (within range)
✅ Targets: 49/49 present
✅ NULL check: PASS (<5% features, <1% targets)
✅ Duplicate check: PASS (0 duplicates)

OVERALL: PASS
```

---

## APPENDIX B: TROUBLESHOOTING GUIDE

### Common Issues and Resolutions

**Issue 1: Execution timeout (>180 min)**
- **Cause**: Large pair data, BigQuery throttling, memory pressure
- **Resolution**: Review logs, check BigQuery quotas, retry with monitoring
- **Prevention**: Monitor execution time proactively, escalate at 120 min

**Issue 2: Validation fails - missing targets**
- **Cause**: Target table incomplete, feature selection error
- **Resolution**: Check target table in BigQuery, verify feature list
- **Prevention**: Pre-validate target table exists and has 49 columns

**Issue 3: NULL values exceed threshold**
- **Cause**: Data quality issue in source tables, merge error
- **Resolution**: Investigate source tables, check merge logic
- **Prevention**: Pre-validate source table completeness

**Issue 4: Cost exceeds $2.00**
- **Cause**: Execution time exceeded, multiple retries, inefficient queries
- **Resolution**: Review BigQuery query costs, optimize extraction
- **Prevention**: Monitor cost during execution, use dry_run for estimates

---

## VERSION HISTORY

**v1.0.0** (2025-12-12 20:10 UTC):
- Initial checklist creation
- Based on EURUSD/AUDUSD benchmarks
- To be updated after GBPUSD validation with actual metrics

**Next Update**: After GBPUSD validation (update benchmarks and ranges)

---

**Quality Assurance Agent (QA)**
*Documentation Validation & Project Consistency*

**Checklist Status**: ACTIVE
**Last Updated**: 2025-12-12 20:10 UTC
**Next Review**: After GBPUSD validation (update with actual GBPUSD metrics)

---

**END OF CHECKLIST**
