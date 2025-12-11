# BA Issue Report: Known Issues, Gaps, and Inconsistencies

**Date**: December 11, 2025 09:30 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: P1 - INFORMATIONAL
**Category**: Comprehensive Status Report

---

## EXECUTIVE SUMMARY

| Category | Count | Severity |
|----------|-------|----------|
| Active Issues | 2 | P1-P2 |
| Pending CE Directives | 1 | P1 |
| Data Gaps | 0 | Resolved |
| Inconsistencies | 3 | P2-P3 |

---

## 1. ACTIVE ISSUES

### 1.1 Step 6 Merge Phase Extended Duration (P1)

**Status**: IN PROGRESS
**Impact**: EURUSD extraction complete, merge taking longer than expected

| Metric | Value |
|--------|-------|
| Process PID | 1493048 |
| CPU | 99.4% |
| Memory | 6.7 GB |
| Extraction | 667/667 COMPLETE |
| Merge | IN PROGRESS (~10 min) |

**Root Cause**: Merging 667 parquet files with ~6,477 columns requires significant RAM
**Recommendation**: Consider chunked merge approach for future runs

---

### 1.2 Debug Output Still Enabled (P3)

**Status**: COSMETIC
**Location**: `pipelines/training/parallel_feature_testing.py:483`

```python
print(f"      [DEBUG] Starting extraction: {table_name}", flush=True)
```

**Impact**: Log verbosity, no functional issue
**Action**: Remove debug statements after Step 6 completes

---

## 2. PENDING CE DIRECTIVES (NOT YET EXECUTED)

### 2.1 Delete V1 Analytics Dataset (CE Directive 0825)

**Status**: PENDING - Will execute after Step 6 merge completes
**Dataset**: `bqx_ml_v3_analytics`
**Tables**: 31
**Rationale**: V2 migration complete, V1 is redundant

```bash
# Command ready to execute
bq rm -r -f bqx-ml:bqx_ml_v3_analytics
```

**Estimated savings**: ~$10-20/month

---

## 3. RESOLVED ISSUES (This Session)

| Issue | Resolution | Time |
|-------|------------|------|
| Summary tables blocking extraction | EXCLUDED per CE 0835 | 05:08 |
| CROSS JOIN for summary tables | REMOVED (not needed) | 05:08 |
| Worker count | Restored to 16 | 05:08 |
| Hardcoded 12-worker default | Fixed to use MAX_WORKERS | Earlier session |

---

## 4. INCONSISTENCIES IDENTIFIED

### 4.1 Table Count Discrepancy (P2)

| Source | Count | Notes |
|--------|-------|-------|
| Step 6 Extraction | 667 | Correct (excludes 2 summary) |
| Intelligence files | 669 | Needs update |
| CE Directive 0835 | 667 | Correct |

**Action Required**: QA to update intelligence files (context.json, ontology.json)

---

### 4.2 Monitor Script Header Inconsistency (P3)

**Location**: `scripts/monitor_step6.sh`
**Issue**: Header still says "16-WORKER" but actual workers depend on script

**Impact**: Cosmetic only
**Action**: Low priority cleanup

---

### 4.3 Code Comment Staleness (P3)

**Location**: `pipelines/training/parallel_feature_testing.py:555`

```python
PARALLEL MODE: Uses all 12 workers for table queries on ONE pair at a time.
```

**Issue**: Comment says 12 workers, but MAX_WORKERS=16
**Action**: Update comment on next code change

---

## 5. DATA QUALITY OBSERVATIONS

### 5.1 EURUSD Extraction Stats

| Metric | Value |
|--------|-------|
| Total tables | 667 |
| New extractions | 46 |
| Cached | 621 |
| Errors | 0 |
| Duration | 593s |
| Checkpoint size | ~5.6 GB |

### 5.2 Feature Coverage

| Category | Tables |
|----------|--------|
| pair_specific | 256 |
| triangulation | 194 |
| market_wide | 10 |
| variance | 63 |
| currency_strength | 144 |
| **TOTAL** | **667** |

---

## 6. RECOMMENDATIONS

1. **IMMEDIATE**: Wait for merge to complete, then execute V1 analytics deletion
2. **SHORT-TERM**: Remove debug statements from extraction code
3. **SHORT-TERM**: Update intelligence files with correct 667 table count
4. **MEDIUM-TERM**: Implement chunked merge to reduce memory footprint

---

## 7. NEXT STEPS (Pending Merge Completion)

1. Verify EURUSD merged parquet file created
2. Execute V1 analytics deletion (CE directive 0825)
3. Verify GBPUSD starts automatically
4. Continue monitoring remaining 27 pairs

---

**Build Agent (BA)**
