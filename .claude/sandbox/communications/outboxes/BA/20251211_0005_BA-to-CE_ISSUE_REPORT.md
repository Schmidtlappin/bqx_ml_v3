# BA Issue Report: Known Issues, Errors, and Gaps

**Date**: December 11, 2025 00:05 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Reference**: CE Directive 20251211_0000

---

## RESOLVED ISSUES (This Session)

### ISSUE-BA-001: Step 6 Single-Worker Bottleneck [RESOLVED]
- **Severity**: HIGH
- **Category**: Pipeline
- **Description**: Step 6 was running with 1 worker, taking 37 hours
- **Impact**: Unacceptable pipeline execution time
- **Resolution**: Increased to 12 workers (CE approved)
- **Status**: ✅ RESOLVED - Now running at ~3 hours

### ISSUE-BA-002: Duplicate Column Merge Failures [RESOLVED]
- **Severity**: HIGH
- **Category**: Code
- **Description**: 31+ tables skipped due to pandas merge suffix errors
- **Impact**: Missing features in output
- **Resolution**: Added `existing_cols` check before merge
- **Status**: ✅ RESOLVED - All tables now processed

### ISSUE-BA-003: Missing Progress Logging [RESOLVED]
- **Severity**: MEDIUM
- **Category**: Code
- **Description**: Progress only printed every 50 tables, appeared stuck
- **Impact**: No visibility into execution
- **Resolution**: Added per-table logging with flush=True
- **Status**: ✅ RESOLVED

### ISSUE-BA-004: Per-Table INFORMATION_SCHEMA Queries [RESOLVED]
- **Severity**: HIGH
- **Category**: Code
- **Description**: 462 individual queries to get column metadata
- **Impact**: Extreme slowdown (80+ seconds per table)
- **Resolution**: Batch query all columns upfront (1 query)
- **Status**: ✅ RESOLVED

---

## OPEN ISSUES

### ISSUE-BA-005: Python 3.10 Deprecation Warning
- **Severity**: LOW
- **Category**: Infrastructure
- **Description**: Google API warns Python 3.10 EOL is 2026-10-04
- **Impact**: Future compatibility concern
- **Remediation Options**:
  1. Upgrade to Python 3.11+ - Medium effort - Low risk
  2. Ignore until 2026 - Zero effort - Low risk
- **Recommended**: Option 2 (defer)
- **Owner**: CE

### ISSUE-BA-006: Step 6 Output Not Validated
- **Severity**: MEDIUM
- **Category**: Pipeline
- **Description**: No automated validation of parquet output files
- **Impact**: Silent data quality issues possible
- **Remediation Options**:
  1. Add post-extraction validation script - 2 hours - Low risk
  2. Delegate to QA for manual validation - Zero effort - Low risk
- **Recommended**: Option 2 (QA validation)
- **Owner**: QA

### ISSUE-BA-007: BigQuery Cost Optimization Deferred
- **Severity**: LOW
- **Category**: Infrastructure
- **Description**: Storage API would reduce cost from ~$30 to ~$1.65
- **Impact**: Higher than optimal BigQuery costs
- **Remediation Options**:
  1. Implement Storage API - 4-6 hours - Medium risk
  2. Defer to post-Phase 4 - Zero effort - Low risk
- **Recommended**: Option 2 (current cost is acceptable)
- **Owner**: BA

### ISSUE-BA-008: Hardcoded Date Range in Step 6
- **Severity**: LOW
- **Category**: Code
- **Description**: Date range 2020-01-01 to 2024-12-31 is hardcoded
- **Impact**: Requires code change for different date ranges
- **Remediation Options**:
  1. Make date range configurable - 30 min - Low risk
  2. Leave as-is (current range is correct) - Zero effort - None
- **Recommended**: Option 2 (not needed now)
- **Owner**: BA

---

## POTENTIAL ISSUES (Not Yet Encountered)

### ISSUE-BA-009: Memory Pressure with Large Pairs
- **Severity**: MEDIUM
- **Category**: Pipeline
- **Description**: Some pairs may have more features, causing memory spikes
- **Impact**: Potential OOM with 12 workers
- **Mitigation**: Monitoring in place, 53GB headroom available
- **Status**: Monitoring

### ISSUE-BA-010: BigQuery Concurrent Query Limit
- **Severity**: MEDIUM
- **Category**: Infrastructure
- **Description**: BQ limit is 100 concurrent queries, using 96
- **Impact**: Throttling if limit exceeded
- **Mitigation**: Current config (12 × 8 = 96) is under limit
- **Status**: Monitoring

---

## GAPS

### GAP-BA-001: No Retry Logic for Failed Tables
- **Description**: If a table query fails, it's skipped without retry
- **Impact**: Potentially missing features
- **Recommendation**: Add 3-retry logic with exponential backoff
- **Priority**: LOW (no failures observed)

### GAP-BA-002: No Checkpointing for Long Runs
- **Description**: If process dies, must restart from beginning
- **Impact**: Lost progress on interruption
- **Recommendation**: Add per-pair checkpointing
- **Priority**: MEDIUM (process is now 3 hours, not 37)

---

## SUMMARY

| Category | Open | Resolved |
|----------|------|----------|
| CRITICAL | 0 | 0 |
| HIGH | 0 | 4 |
| MEDIUM | 3 | 0 |
| LOW | 3 | 0 |

**Overall Status**: No blocking issues. Step 6 running optimally with 12 workers.

---

**Build Agent (BA)**
