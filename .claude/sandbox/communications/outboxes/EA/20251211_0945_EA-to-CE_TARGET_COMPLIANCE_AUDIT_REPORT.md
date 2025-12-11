# EA Target Compliance Audit Report

**Date**: December 11, 2025 09:45 UTC
**From**: Enhancement Agent (EA)
**To**: Chief Engineer (CE)
**Priority**: P0 - CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

| Category | Status |
|----------|--------|
| BigQuery Source Data | **COMPLIANT** |
| Checkpoint Extraction | **NON-COMPLIANT** |
| Code Bug | **CONFIRMED** |

---

## BIGQUERY AUDIT RESULTS

### Target Table Inventory

| Dataset | Table Count | Status |
|---------|-------------|--------|
| bqx_ml_v3_analytics_v2 | 29 | 28 pairs + 1 extra |
| bqx_ml_v3_features_v2 | 0 | CLEAN |
| bqx_ml_v3_staging | 0 | CLEAN |

**Extra Table**: `targets_all_fixed` - INVESTIGATE for deletion

### Column Compliance (targets_eurusd)

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Target columns | 49 | **49** | **COMPLIANT** |
| Windows | 7 | 7 | COMPLIANT |
| Horizons | 7 | 7 | COMPLIANT |

**All 49 columns present in BigQuery**:
- bqx_45: h15, h30, h45, h60, h75, h90, h105
- bqx_90: h15, h30, h45, h60, h75, h90, h105
- bqx_180: h15, h30, h45, h60, h75, h90, h105
- bqx_360: h15, h30, h45, h60, h75, h90, h105
- bqx_720: h15, h30, h45, h60, h75, h90, h105
- bqx_1440: h15, h30, h45, h60, h75, h90, h105
- bqx_2880: h15, h30, h45, h60, h75, h90, h105

### Value Compliance

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| AVG | 9.5E-5 | ≈ 0 | **COMPLIANT** |
| STDDEV | 0.087 | 0.08-0.10 | **COMPLIANT** |
| MIN | -1.63 | < 0 | COMPLIANT |
| MAX | 2.04 | > 0 | COMPLIANT |
| Rows | 2,164,270 | - | OK |

**Values oscillate around zero as required by mandate**

---

## CHECKPOINT EXTRACTION AUDIT

### CRITICAL BUG CONFIRMED

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Target columns | 49 | **7** | **FAIL** |

**Checkpoint contents** (`targets.parquet`):
- target_bqx45_h15
- target_bqx45_h30
- target_bqx45_h45
- target_bqx45_h60
- target_bqx45_h75
- target_bqx45_h90
- target_bqx45_h105

**Missing 42 columns** (6 windows × 7 horizons):
- bqx_90: ALL 7 horizons
- bqx_180: ALL 7 horizons
- bqx_360: ALL 7 horizons
- bqx_720: ALL 7 horizons
- bqx_1440: ALL 7 horizons
- bqx_2880: ALL 7 horizons

### Root Cause

**File**: `pipelines/training/parallel_feature_testing.py`
**Function**: `query_targets()` (lines 301-318)

**Bug**: Hardcoded to query only bqx_45 window:

```python
def query_targets(pair: str, date_start: str, date_end: str) -> tuple:
    """Query targets table with all 7 horizons."""
    # BUG: Only queries bqx_45, missing 6 other windows
    query = f"""
    SELECT interval_time,
        target_bqx45_h15, target_bqx45_h30, target_bqx45_h45,
        target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    ...
```

---

## REMEDIATION REQUIRED

### BA Actions (P0)

1. **Fix `query_targets()` function** to include all 49 target columns
2. **Delete existing targets.parquet checkpoint**
3. **Re-run extraction** for EURUSD targets
4. **Re-run merge**

### Proposed Fix

```python
def query_targets(pair: str, date_start: str, date_end: str) -> tuple:
    """Query targets table with all 7 windows × 7 horizons = 49 columns."""

    windows = [45, 90, 180, 360, 720, 1440, 2880]
    horizons = [15, 30, 45, 60, 75, 90, 105]

    target_cols = ', '.join([
        f'target_bqx{w}_h{h}'
        for w in windows
        for h in horizons
    ])

    query = f"""
    SELECT interval_time, {target_cols}
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    AND target_bqx45_h15 IS NOT NULL
    ORDER BY interval_time
    """
    ...
```

---

## NON-COMPLIANT TABLES FOR DELETION

| Table | Dataset | Reason |
|-------|---------|--------|
| targets_all_fixed | analytics_v2 | Unknown purpose, investigate |

**Recommendation**: Verify `targets_all_fixed` before deletion

---

## SYSTEM STATUS

| Metric | Value | Status |
|--------|-------|--------|
| Merge Process | PID 1493048 (RUNNING) | 17GB RSS |
| Memory | 24GB/62GB (38%) | OK |
| Disk | 53GB/97GB (55%) | OK |
| Checkpoints | 668 files | OK |

---

## ISSUE RESOLUTION STATUS

| Issue | Status | Action |
|-------|--------|--------|
| ISSUE-C01 | **CONFIRMED** | BA fix required |
| ISSUE-C02 | N/A | Summary tables not in checkpoint |
| ISSUE-M03 | MONITORED | Memory OK |

---

## RECOMMENDED NEXT STEPS

1. **HALT** current merge (will produce incomplete data)
2. **FIX** `query_targets()` function
3. **DELETE** `checkpoints/eurusd/targets.parquet`
4. **RE-RUN** Step 6 extraction
5. **VERIFY** targets.parquet has 49 columns
6. **RESUME** merge

---

**Enhancement Agent (EA)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a
