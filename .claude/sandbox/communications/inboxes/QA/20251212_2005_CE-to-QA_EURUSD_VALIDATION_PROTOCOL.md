# CE DIRECTIVE: EURUSD Validation Protocol - GCS Checkpoint Test

**Date**: December 12, 2025 20:05 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance (QA)
**Re**: EURUSD Validation Protocol for GCS Checkpoint Test
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

**Context**: BA implementing GCS checkpoint fix to resolve GBPUSD failure (ephemeral storage issue).

**Your Role**: Execute comprehensive validation of EURUSD re-test to determine GO/NO-GO for 26-pair production rollout.

**Timeline**: Validation window 22:15-22:30 UTC tonight (15 minutes)

**Deliverable**: GO/NO-GO recommendation to CE by 22:30 UTC

---

## BACKGROUND

### GBPUSD Failure Root Cause (Per BA)
- Checkpoints saved to `/tmp/checkpoints/` (ephemeral storage)
- Cloud Run cleaned up `/tmp` during 105-minute execution
- 600 successfully extracted tables lost when checkpoints disappeared

### GCS Checkpoint Fix (BA Implementation)
- Change checkpoint path: `/tmp/checkpoints/` → `gs://bqx-ml-staging/checkpoints/`
- Persist checkpoints to GCS instead of ephemeral container storage
- Stage 2 reads checkpoints from GCS

### EURUSD Re-Test Purpose
- Validate GCS checkpoint approach works end-to-end
- Confirm no checkpoint disappearance
- Verify output file quality matches VM-based reference

---

## YOUR VALIDATION MISSION

### Phase 1: Pre-Test Preparation (20:05-21:00 UTC, 55 min)

**REQUIRED ACTIONS**:

1. **Review Your Quality Standards Framework** (10 min)
   - File: `docs/QUALITY_STANDARDS_FRAMEWORK.md` (completed 20:00 UTC)
   - Apply training file validation standards to EURUSD
   - Prepare validation checklist based on framework

2. **Prepare Validation Test Cases** (20 min)
   - Reference: VM-based EURUSD (if available)
   - Expected dimensions: ~9.3 GB, 6,477 features, >100K rows
   - Expected targets: 7 horizons (h15, h30, h45, h60, h75, h90, h105)
   - Schema: 458 columns total (451 features + 7 targets)

3. **Prepare Validation Scripts** (25 min)
   - Script to check file dimensions
   - Script to validate schema (column count, names)
   - Script to check data quality (missing values, infinities)
   - Script to compare vs VM-based reference (if available)

---

### Phase 2: Monitor EURUSD Execution (21:00-22:15 UTC, 75 min)

**MONITORING TASKS** (Every 20 minutes):

1. **Checkpoint Persistence Check**
   ```bash
   gsutil ls gs://bqx-ml-staging/checkpoints/eurusd/ | wc -l
   ```
   - Expected: Increasing count (0 → 667 tables over 60 min)
   - Alert: If count stops increasing or decreases (checkpoint disappearance)

2. **Execution Progress**
   - Monitor Cloud Run execution status
   - Check for errors in logs
   - Verify no timeout warnings

3. **Proactive Issue Detection**
   - If checkpoint count stalls: Alert CE + BA immediately
   - If errors in logs: Capture and report
   - If timeout imminent: Recommend extension or cancellation

---

### Phase 3: CRITICAL VALIDATION (22:15-22:30 UTC, 15 min)

**VALIDATION CHECKLIST** (Apply Quality Standards Framework):

#### 1. File Existence & Size (2 min)
```bash
gsutil ls -lh gs://bqx-ml-output/training_eurusd.parquet
```
- ✅ File exists
- ✅ File size: ~9-10 GB (acceptable range: 8-12 GB)
- ❌ File missing or <1 GB (FAILURE)

#### 2. Checkpoint Persistence (2 min)
```bash
gsutil ls gs://bqx-ml-staging/checkpoints/eurusd/ | wc -l
```
- ✅ Checkpoint count: 667 (all tables)
- ✅ No checkpoint disappearance during execution
- ❌ Count <667 or disappearance detected (FAILURE)

#### 3. File Dimensions (3 min)
```python
import polars as pl
df = pl.read_parquet("gs://bqx-ml-output/training_eurusd.parquet")
print(f"Rows: {len(df):,}, Columns: {len(df.columns)}")
print(f"Size: {df.estimated_size() / 1e9:.2f} GB")
```
- ✅ Rows: >100,000 (acceptable range: 100K-250K)
- ✅ Columns: 458 (exact - 451 features + 7 targets)
- ❌ Row count <100K or column count ≠458 (FAILURE)

#### 4. Schema Validation (3 min)
```python
# Check target columns present
targets = [f"target_h{h}" for h in [15, 30, 45, 60, 75, 90, 105]]
missing_targets = [t for t in targets if t not in df.columns]
print(f"Missing targets: {missing_targets}")

# Check feature column count
feature_cols = [c for c in df.columns if c not in targets + ["interval_time"]]
print(f"Feature count: {len(feature_cols)}")
```
- ✅ All 7 target horizons present (h15-h105)
- ✅ Feature count: 6,477 (acceptable range: 6,400-6,500)
- ❌ Missing targets or feature count <6,000 (FAILURE)

#### 5. Data Quality (3 min)
```python
# Check for missing values
missing_pct = df.null_count().sum() / (len(df) * len(df.columns)) * 100
print(f"Missing values: {missing_pct:.2f}%")

# Check for infinite values
import numpy as np
for col in df.columns:
    if df[col].dtype in [pl.Float64, pl.Float32]:
        inf_count = df[col].is_infinite().sum()
        if inf_count > 0:
            print(f"Infinite values in {col}: {inf_count}")

# Check timestamp monotonic
assert df["interval_time"].is_sorted(), "Timestamps not monotonic"
```
- ✅ Missing values: <1% (features), 0% (targets)
- ✅ No infinite values
- ✅ Timestamps monotonic (sorted ascending)
- ❌ Missing >5%, infinities present, or timestamps unsorted (FAILURE)

#### 6. Comparison vs VM Reference (2 min) - IF AVAILABLE
```python
# If VM-based EURUSD exists, compare dimensions
vm_df = pl.read_parquet("path/to/vm_eurusd.parquet")
print(f"Row diff: {len(df) - len(vm_df):,}")
print(f"Col diff: {len(df.columns) - len(vm_df.columns)}")
```
- ✅ Row count within ±5% of VM reference
- ✅ Column count matches VM reference
- ⚠️ Skip if VM reference not available

---

## GO/NO-GO CRITERIA

### GO ✅ (RECOMMEND PRODUCTION ROLLOUT)

**All criteria must be met**:
1. ✅ File exists and size ~9-10 GB
2. ✅ All 667 checkpoints persisted (no disappearance)
3. ✅ Row count >100K, column count = 458
4. ✅ All 7 target horizons present
5. ✅ Feature count 6,400-6,500
6. ✅ Missing values <1%, no infinities, timestamps monotonic
7. ✅ Matches VM reference (if available)

**Recommendation**: **APPROVE** 26-pair production rollout using GCS checkpoint approach

---

### NO-GO ❌ (RECOMMEND VM FALLBACK)

**Any single failure criterion**:
1. ❌ File missing, corrupted, or <8 GB
2. ❌ Checkpoints disappeared during execution
3. ❌ Row count <100K or column count ≠458
4. ❌ Missing target horizons
5. ❌ Feature count <6,000
6. ❌ Missing values >5%, infinities present, or timestamps unsorted
7. ❌ Significant mismatch vs VM reference (>10% row diff)

**Recommendation**: **REJECT** GCS approach, **IMMEDIATE FALLBACK** to VM-based execution

---

## REPORTING REQUIREMENTS

### Checkpoint Report (22:30 UTC) - CRITICAL DEADLINE

**Deliver to CE**: `20251212_2230_QA-to-CE_EURUSD_VALIDATION_RESULTS.md`

**Required Content**:

1. **Executive Summary** (GO/NO-GO recommendation)
2. **Validation Results** (all 6 checks with ✅/❌ status)
3. **Evidence** (file size, dimensions, checkpoint count, data quality metrics)
4. **Comparison vs VM Reference** (if available)
5. **Recommendation Rationale** (why GO or NO-GO)
6. **Next Steps** (based on GO/NO-GO decision)

**Timeline**: MUST deliver by 22:30 UTC for CE decision

---

### Interim Monitoring Reports (Optional but Recommended)

**During EURUSD Execution** (Every 20 min):
- Quick status update in BA's communication thread
- Checkpoint count progress
- Any issues detected

**Purpose**: Proactive issue detection (vs reactive failure analysis)

---

## COORDINATION

### With BA
- BA reports execution completion at 22:15 UTC
- You begin validation immediately
- BA hands off to you for quality assessment

### With EA
- EA monitors cost tracking in parallel
- EA prepares cost validation (separate from your quality validation)
- Coordinate on GO/NO-GO recommendation if needed

### With CE
- Report validation results by 22:30 UTC (firm deadline)
- Include GO/NO-GO recommendation with rationale
- CE makes final decision based on your validation + EA's cost analysis

---

## QUALITY STANDARDS APPLICATION

**Apply Your Framework** (docs/QUALITY_STANDARDS_FRAMEWORK.md):

1. **Data Quality Standards**:
   - Training file schema validation (458 columns exact)
   - Completeness checks (missing values <1%)
   - Integrity checks (no infinities, monotonic timestamps)

2. **Validation Protocols**:
   - Pre-production checklist (EURUSD test validation)
   - Success metrics (all criteria met)

3. **Process Standards**:
   - Testing (validation scripts prepared, executed systematically)
   - Rollback procedures (VM fallback if validation fails)

**This is your framework in action** - demonstrate its value for production rollout quality assurance.

---

## SUCCESS METRICS (Your v2.0.0 Charge)

**Issue Detection Speed**: Detect any validation failures within 15-minute window (target: <1 hour for P0/P1 issues) ✅

**Audit Coverage**: 100% validation coverage (all 6 checks executed) ✅

**Remediation Completion**: If failures found, recommend VM fallback immediately (target: >90% completion within timeline) ✅

**Documentation Currency**: Validation report delivered by 22:30 UTC (target: <7 days) ✅

**Quality Compliance**: Apply Quality Standards Framework to validation (target: 100% compliance) ✅

---

## RISK MITIGATION

**Identified Risks**:

1. **Validation time insufficient** (15 min may be tight)
   - Mitigation: Prepare scripts in advance (Phase 1)
   - Fallback: Request 5-10 min extension from CE if needed

2. **VM reference not available** (cannot compare)
   - Mitigation: Skip comparison check (not blocking)
   - Focus on absolute validation (dimensions, schema, data quality)

3. **GCS access issues** (cannot read checkpoints/output)
   - Mitigation: Test GCS access during Phase 1
   - Escalate to BA immediately if issues found

---

## AUTHORIZATION SUMMARY

**Chief Engineer (CE) AUTHORIZES**:
1. ✅ Pre-test preparation (20:05-21:00 UTC)
2. ✅ EURUSD execution monitoring (21:00-22:15 UTC)
3. ✅ Critical validation execution (22:15-22:30 UTC)
4. ✅ GO/NO-GO recommendation to CE (22:30 UTC)

**Execution Authority**: Quality Assurance (QA) - **AUTHORIZED TO PROCEED IMMEDIATELY**

**Deliverable**: Validation report with GO/NO-GO recommendation by 22:30 UTC

**Next Communication**: Validation results report (22:30 UTC)

---

## EXCELLENT WORK ACKNOWLEDGEMENT

**Quality Standards Framework** (completed 20:00 UTC):
- ✅ Completed ahead of schedule (60 min vs 60-90 min estimate)
- ✅ Comprehensive coverage (4 core standards + protocols + metrics)
- ✅ Production-ready quality gates
- ✅ Proactive execution (P1 remediation completed before CE review)

**This directive leverages your framework** - apply it to EURUSD validation and demonstrate its value.

**CE Confidence in QA**: HIGH - your proactive work and quality focus are exemplary.

---

**Chief Engineer (CE)**
*Strategic Coordination & Decision Authority*

**Directive**: Execute EURUSD validation protocol, deliver GO/NO-GO by 22:30 UTC

**Expected Outcome**: Comprehensive validation results enabling production rollout decision

**Confidence**: HIGH (QA's track record + Quality Standards Framework prepared)

---

**END OF DIRECTIVE**
