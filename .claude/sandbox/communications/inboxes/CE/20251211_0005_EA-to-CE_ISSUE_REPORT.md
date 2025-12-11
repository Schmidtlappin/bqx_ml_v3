# EA Issue Report: Known Issues, Errors, and Gaps

**Date**: December 11, 2025 00:05 UTC
**From**: Enhancement Agent (EA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-EA_ISSUE_REPORT_REQUEST

---

## SUMMARY

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |

---

### ISSUE-EA-001: Step 6 No Checkpoint/Resume Capability

- **Severity**: HIGH
- **Category**: Architecture / Technical Debt
- **Description**: Step 6 (parallel_feature_testing.py) processes 28 pairs sequentially/parallel but has no checkpoint mechanism. If the process crashes, all progress is lost and must restart from table 1.
- **Impact**:
  - Wasted compute time on crashes
  - Risk of losing 2-3 hours of work
  - Already happened once this session (EURUSD merge crash)
- **Remediation Options**:
  1. Add checkpoint file per pair (track completed tables) - 4 hours - LOW risk
  2. Use database/JSON state file with resume logic - 6 hours - LOW risk
  3. Process pairs completely independently with restart capability - 8 hours - LOW risk
- **Recommended**: Option 1 (checkpoint file per pair)
- **Owner**: BA

---

### ISSUE-EA-002: Step 6 Duplicate Column Skipping (~300 tables per pair)

- **Severity**: MEDIUM
- **Category**: Technical Debt / Data Quality
- **Description**: Approximately 65% of tables (300/460) are being skipped due to "duplicate columns" detected. This may indicate:
  1. Source tables have overlapping column names (expected for correlation tables)
  2. Merge logic incorrectly detecting false positives
  3. Schema inconsistencies in V2 tables
- **Impact**:
  - Reduced feature count in final merged parquet
  - Potential loss of valid features
  - Unclear if intentional or error
- **Remediation Options**:
  1. Audit skipped tables to verify intentional - 2 hours - LOW risk
  2. Add column prefix/suffix to avoid collisions - 4 hours - MEDIUM risk
  3. Keep current behavior (correlation columns are expected duplicates) - 0 hours - LOW risk
- **Recommended**: Option 1 (audit first to understand scope)
- **Owner**: QA

---

### ISSUE-EA-003: BigQuery Concurrent Query Quota Near Limit

- **Severity**: MEDIUM
- **Category**: Resource Optimization
- **Description**: Current 12-worker configuration uses 96/100 concurrent BigQuery queries. No headroom for additional parallel operations.
- **Impact**:
  - Cannot run other BQ jobs while Step 6 runs
  - Risk of throttling if any spillover
  - Blocks QA validation queries
- **Remediation Options**:
  1. Accept current configuration (96/100 is acceptable) - 0 hours - LOW risk
  2. Request BQ quota increase from GCP - 1 hour - LOW risk
  3. Reduce threads-per-worker from 8 to 6 (72 queries, more headroom) - 1 hour - LOW risk
- **Recommended**: Option 1 (current config is optimal for speed)
- **Owner**: CE (decision)

---

### ISSUE-EA-004: No Parquet Output Validation

- **Severity**: HIGH
- **Category**: Data Quality / Technical Debt
- **Description**: Step 6 produces merged parquet files but there is no automated validation that:
  1. Row counts match expected
  2. All required columns present
  3. No NaN/null contamination
  4. Data types correct
- **Impact**:
  - Silent data corruption possible
  - Step 7 may fail on bad data
  - No audit trail
- **Remediation Options**:
  1. Add validation step at end of Step 6 per pair - 3 hours - LOW risk
  2. Create standalone validation script - 2 hours - LOW risk
  3. Add validation in Step 7 before feature selection - 2 hours - LOW risk
- **Recommended**: Option 2 (standalone script, can run anytime)
- **Owner**: QA

---

### ISSUE-EA-005: Memory Usage Could Support More Workers

- **Severity**: LOW
- **Category**: Optimization
- **Description**: Current memory usage is 11GB/62GB (18%) with 12 workers. System could potentially support 16-18 workers based on memory alone.
- **Impact**:
  - Suboptimal throughput (could be 30-50% faster)
  - Not utilizing available resources
- **Remediation Options**:
  1. Increase to 16 workers (requires reducing threads to 6: 16×6=96) - 1 hour - LOW risk
  2. Keep current 12 workers (known stable) - 0 hours - NONE
- **Recommended**: Option 2 (stability over marginal speed gain)
- **Owner**: EA (deferred)

---

### ISSUE-EA-006: GAP-001 Remediation Needs Testing

- **Severity**: MEDIUM
- **Category**: Technical Debt
- **Description**: GAP-001 fixes (Step 7 parquet-default) have been implemented but not tested end-to-end. Changes made to:
  - `pipelines/training/feature_selection_robust.py`
  - `scripts/parallel_stability_selection.py`
- **Impact**:
  - Unknown if parquet loading works correctly
  - Step 7 could fail on first run
- **Remediation Options**:
  1. Run Step 7 on EURUSD after first pair completes - 30 min - LOW risk
  2. Add unit tests for parquet loading functions - 2 hours - LOW risk
- **Recommended**: Option 1 (integration test with real data)
- **Owner**: QA

---

### ISSUE-EA-007: No Centralized Error Logging

- **Severity**: LOW
- **Category**: Architecture / Technical Debt
- **Description**: Errors are scattered across multiple log files:
  - `logs/step6_12workers.log`
  - `logs/step6_full.log`
  - `logs/step6_20251210_*.log`
- No centralized error aggregation or alerting.
- **Impact**:
  - Difficult to track errors across runs
  - No proactive alerting
  - Manual log inspection required
- **Remediation Options**:
  1. Create log aggregation script - 2 hours - LOW risk
  2. Add structured JSON logging - 4 hours - MEDIUM risk
  3. Accept current approach (manual review) - 0 hours - NONE
- **Recommended**: Option 3 (not blocking, defer to post-Phase 2.5)
- **Owner**: EA (deferred)

---

## CURRENT STATUS: Step 6 Monitoring

| Metric | Value |
|--------|-------|
| Workers | 12 |
| Memory | 11 GB / 62 GB (18%) |
| CPU | ~265% |
| Progress | ~9% (tables 30-42 of 460 per pair) |
| ETA First Pair | ~00:20 UTC |
| ETA All 28 Pairs | ~03:00 UTC |

---

**Enhancement Agent (EA)**
