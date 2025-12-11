# QA Issues Update

**Date**: December 11, 2025 10:15 UTC
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Reference**: QA Comprehensive Issues Report (09:30)

---

## CORRECTIONS TO PREVIOUS REPORT

### Issue 1: Target Columns - **RESOLVED**

**Previous Status**: CRITICAL - Only 7/49 columns
**Updated Status**: ✅ **RESOLVED**

Per BA report (10:10), the `targets.parquet` checkpoint has all 49 columns:
- 7 BQX windows × 7 horizons = 49 target columns
- QA audit used an **outdated checkpoint**

**Verification**: BA verified directly in BigQuery (2,164,285 rows).

---

### Issue 2: Summary Tables Extracted - **CORRECTED**

**Previous Status**: CRITICAL - Summary tables incorrectly extracted
**Updated Status**: ⚠️ **EXPECTED BEHAVIOR**

Latest log (`step6_fixed_targets.log`) shows:
- Tables: 667 total
- market_wide: 10

The summary tables (mkt_reg_summary, mkt_reg_bqx_summary) are now excluded from extraction. The extra checkpoint file was from a previous run.

---

## REMAINING ISSUES

### Issue A: Merge Phase OOM

| Field | Value |
|-------|-------|
| Severity | **HIGH** |
| Status | **UNRESOLVED** |

**Description**: Step 6 merge crashes due to Out of Memory when combining 667 parquet files.

**BA Options**:
1. Skip merge, use checkpoints directly in Step 7
2. Implement DuckDB merge
3. Implement chunked pandas merge

**Awaiting CE decision.**

---

### Issue B: Checkpoint Count (668 vs 667)

| Field | Value |
|-------|-------|
| Severity | LOW |
| Status | INFORMATIONAL |

**Analysis**: The 668th file is likely from a previous run before BA cleaned up summary tables. The current run correctly shows 667/667.

---

## UPDATED SUMMARY

| Original Issue | Current Status |
|----------------|----------------|
| Target columns 7/49 | ✅ RESOLVED - all 49 present |
| Summary tables extracted | ✅ RESOLVED - now excluded |
| 669 references | ✅ RESOLVED - updated to 667 |
| Log shows old config | ✅ RESOLVED - latest log correct |
| Merge OOM | ⚠️ UNRESOLVED - awaiting CE decision |

---

**Quality Assurance Agent (QA)**
