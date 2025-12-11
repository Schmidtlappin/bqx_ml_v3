# QA Issue Report: Known Issues, Errors, and Gaps

**Date**: December 11, 2025 00:05 UTC
**From**: QA Agent
**To**: Chief Engineer (CE)
**Reference**: 20251211_0000_CE-to-QA_ISSUE_REPORT_REQUEST

---

## SUMMARY

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 2 |
| LOW | 2 |
| **TOTAL** | **5** |

---

## ISSUES

### ISSUE-QA-001: Coverage Below Target (17.33% vs 30-50%)

- **Severity**: HIGH
- **Category**: Validation
- **Description**: Current 59-feature h15 model achieves 91.70% accuracy but only 17.33% coverage, below the 30-50% target range.
- **Impact**: Model only makes predictions on 17% of market conditions, reducing utility.
- **Remediation Options**:
  1. **Complete full feature universe testing (11,337 columns)** - HIGH effort - LOW risk - Expected to improve coverage
  2. **Lower confidence threshold** - LOW effort - MEDIUM risk - Would sacrifice accuracy
  3. **Accept current coverage** - NO effort - HIGH risk - Does not meet mandate
- **Recommended**: Option 1 (BA currently executing Step 6)
- **Owner**: BA (pipeline execution) / QA (re-validation after)

---

### ISSUE-QA-002: REM-009 Pending (Accuracy Baseline Update)

- **Severity**: MEDIUM
- **Category**: Documentation
- **Description**: CE_MASTER_REMEDIATION_PLAN.md has REM-009 still pending - requires updating accuracy baseline in roadmap after new model trained.
- **Impact**: Roadmap contains placeholder/projected values instead of actual post-training metrics.
- **Remediation Options**:
  1. **Update after Step 8 completion** - LOW effort - NO risk - Wait for actual metrics
  2. **Update now with projected values** - LOW effort - LOW risk - May need revision
- **Recommended**: Option 1 (wait for actual metrics)
- **Owner**: QA

---

### ISSUE-QA-003: Step 6 Output Not Yet Validated

- **Severity**: MEDIUM
- **Category**: Validation
- **Description**: Step 6 feature extraction is in progress but output parquet files not yet validated by QA.
- **Impact**: Cannot proceed to Step 7 until validation complete.
- **Remediation Options**:
  1. **Execute validation checklist when BA notifies completion** - LOW effort - NO risk
- **Recommended**: Option 1 (already queued in QA_TODO.md)
- **Owner**: QA (after BA completion)

---

### ISSUE-QA-004: F3b Cleanup Count Discrepancy

- **Severity**: LOW
- **Category**: Documentation
- **Description**: QA_GATE1_PREFLIGHT_CHECKLIST.md mentions "86 misplaced tables" in Non-Blocking Issues, but actual cleanup was 56 tables.
- **Impact**: Minor documentation inconsistency, no functional impact.
- **Remediation Options**:
  1. **Update checklist to reflect 56** - LOW effort - NO risk
  2. **Leave as-is (archived document)** - NO effort - NO risk
- **Recommended**: Option 2 (document is archived, historical reference)
- **Owner**: QA

---

### ISSUE-QA-005: Missing GATE_4 Validation Script

- **Severity**: LOW
- **Category**: Validation
- **Description**: No dedicated validate_gate4.py script exists yet for post-full-feature-universe model validation.
- **Impact**: Will need to create or adapt validate_gate3.py when Step 8 completes.
- **Remediation Options**:
  1. **Create validate_gate4.py now** - MEDIUM effort - NO risk
  2. **Adapt validate_gate3.py when needed** - LOW effort - NO risk - Already supports model versioning
- **Recommended**: Option 2 (validate_gate3.py v2 already supports --model-version and --model-path)
- **Owner**: QA

---

## NO ISSUES FOUND IN

| Area | Status |
|------|--------|
| Intelligence file consistency | ALIGNED |
| Mandate compliance (except coverage) | COMPLIANT |
| GATE_1, GATE_2, GATE_3 | PASSED |
| Cost monitoring | GREEN (12.2% of budget) |
| BigQuery table counts | VERIFIED (219 gap tables) |
| Documentation currency | CURRENT |

---

## RECOMMENDED PRIORITY

1. **ISSUE-QA-001** - Awaiting BA Step 6 completion (in progress)
2. **ISSUE-QA-003** - Execute when Step 6 complete
3. **ISSUE-QA-002** - Execute after Step 8 complete
4. **ISSUE-QA-004/005** - LOW priority, defer

---

**QA Agent**
**Session**: 72a1c1a7-c564-4ac8-974a-13ed0ce87dca
