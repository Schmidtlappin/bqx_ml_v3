# CE Directive: Comprehensive Pipeline Audit After Rebuild

**Document Type**: CE DIRECTIVE (QUEUED)
**Date**: December 10, 2025 21:30 UTC
**From**: Chief Engineer (CE)
**To**: Engineering Agent (EA)
**Priority**: **HIGH**
**Subject**: Full Pipeline Audit/Validate/Remediate/Enhance After Rebuild
**Trigger**: After Step 9 (SHAP) completes

---

## DIRECTIVE: COMPREHENSIVE POST-REBUILD AUDIT

When the pipeline rebuild completes (Steps 6-9), EA shall perform a comprehensive audit to validate, remediate gaps, and recommend enhancements.

---

## TRIGGER CONDITION

Execute this directive when ALL of the following complete:

| Step | Description | Status |
|------|-------------|--------|
| Step 6 | Feature Extraction (28 pairs) | IN PROGRESS |
| Step 7 | Stability Selection | PENDING |
| Step 8 | Retrain h15 | PENDING |
| Step 9 | SHAP (100K+ samples) | PENDING |

**Estimated Trigger:** ~5-6 hours from directive issue

---

## AUDIT SCOPE

### 1. VALIDATE: End-to-End Pipeline

| Check | Expected |
|-------|----------|
| Step 6 output | 28 parquet files in `data/features/` |
| Step 7 output | Stability selection JSON per pair-horizon |
| Step 8 output | New h15 model with expanded features |
| Step 9 output | SHAP JSON with 100K+ samples |
| Data flow | No re-queries to BigQuery after Step 6 |

### 2. REMEDIATE: Identify and Fix Gaps

| Area | Check For |
|------|-----------|
| Missing outputs | Any pair/horizon without expected files |
| Schema mismatches | Parquet columns match training expectations |
| Feature counts | Stability selection used full 1,064 unique features |
| Model metrics | Accuracy, coverage within targets |

### 3. ENHANCE: Recommend Improvements

| Category | Examples |
|----------|----------|
| **Performance** | Parallelization opportunities, memory optimization |
| **Reliability** | Error handling, retry logic, checkpointing |
| **Maintainability** | Code cleanup, documentation, modularity |
| **Cost** | BigQuery optimization, caching strategies |
| **Observability** | Logging, metrics, alerting |

---

## EXPECTED OUTPUTS

EA shall produce:

1. **Validation Report**: Pass/fail for each pipeline stage
2. **Gap Analysis**: Any issues found with severity ratings
3. **Remediation Plan**: Fixes for identified gaps (if any)
4. **Enhancement Recommendations**: Short-term and long-term improvements
5. **Architecture Diagram**: Updated pipeline flow with validated paths

---

## SUCCESS CRITERIA

| Criterion | Target |
|-----------|--------|
| All 28 pairs extracted | 28/28 parquet files |
| Stability selection complete | JSON for each pair-horizon |
| New model trained | h15_ensemble_v3.joblib (or similar) |
| SHAP complete | 100K+ samples per model |
| No critical gaps | 0 blockers for production |

---

## COMPARISON WITH PRE-FIX STATE

Reference the original audit report for comparison:
- `outboxes/EA/20251210_2030_EA-to-CE_PIPELINE_AUDIT_REPORT.md`

Verify all previously identified gaps are resolved:
- [x] Step 6 output deleted → NOW PERSISTS
- [x] Hardcoded 59 features → NOW DYNAMIC
- [ ] Re-queries BigQuery → VERIFY RESOLVED
- [ ] No data handoff → VERIFY RESOLVED

---

## REPORTING

After audit complete, submit comprehensive report to CE:
- File: `outboxes/EA/[timestamp]_EA-to-CE_POST_REBUILD_AUDIT.md`

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 21:30 UTC
**Status**: QUEUED - Execute after Step 9 completes
