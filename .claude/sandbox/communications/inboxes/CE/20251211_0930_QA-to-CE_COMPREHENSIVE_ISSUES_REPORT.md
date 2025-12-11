# QA Comprehensive Issues Report

**Date**: December 11, 2025 09:30 UTC
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Priority**: P1 - HIGH
**Category**: Issues Audit

---

## EXECUTIVE SUMMARY

5 issues identified requiring remediation. 2 critical, 2 medium, 1 low.

---

## CRITICAL ISSUES (P0)

### Issue 1: Target Columns Incomplete

| Field | Value |
|-------|-------|
| Severity | **CRITICAL** |
| Status | UNRESOLVED |
| Reported | 2025-12-11 08:25 |

**Description**: `targets_eurusd` checkpoint has only **7 target columns** (expected 49).

**Current State**:
- Only `bqx_45` window present
- Missing windows: `bqx_90`, `bqx_180`, `bqx_360`, `bqx_720`, `bqx_1440`, `bqx_2880`
- Expected: 7 windows × 7 horizons = 49 target columns

**Impact**: Cannot train models without complete target data.

**Remediation**: BA must regenerate all 49 target columns per mandate.

---

### Issue 2: Step 6 Summary Tables Extracted

| Field | Value |
|-------|-------|
| Severity | **CRITICAL** |
| Status | UNRESOLVED |
| Reported | 2025-12-11 09:30 |

**Description**: Log shows `mkt_reg_summary` and `mkt_reg_bqx_summary` were EXTRACTED despite CE directive to exclude them.

**Evidence**:
```
[620/669] mkt_reg_summary: +277 cols SAVED
[622/669] mkt_reg_bqx_summary: +277 cols SAVED
```

**Impact**:
- 554 extraneous columns added to feature set (277 × 2)
- These are metadata tables without `interval_time`
- May cause JOIN failures in training pipeline

**Remediation**:
1. Delete checkpoint files: `mkt_reg_summary.parquet`, `mkt_reg_bqx_summary.parquet`
2. Re-run merge to exclude these files
3. Update extraction script to exclude summary tables

---

## MEDIUM ISSUES (P1)

### Issue 3: Intelligence Files Still Reference 669

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Status | PARTIAL |
| Reported | 2025-12-11 09:30 |

**Description**: Some files may still reference 669 instead of 667.

**Files Updated**: ✅
- context.json
- ontology.json
- semantics.json
- roadmap_v2.json
- feature_catalogue.json

**Files NOT Checked**:
- mandate/BQX_ML_V3_FEATURE_INVENTORY.md
- README files
- Other markdown documentation

**Remediation**: Full grep for "669" across codebase.

---

### Issue 4: Log File Shows Old Configuration

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Status | INFORMATIONAL |

**Description**: Log `step6_debug_20251211_050225.log` shows:
```
Tables: 669 total
market_wide: 12
```

But current configuration should be:
```
Tables: 667 total
market_wide: 10
```

**Impact**: Script may not be using updated configuration.

**Remediation**: Verify extraction script reads updated table count.

---

## LOW ISSUES (P2)

### Issue 5: 668 Checkpoints vs 667 Expected

| Field | Value |
|-------|-------|
| Severity | LOW |
| Status | INFORMATIONAL |

**Description**: 668 checkpoint files exist, but only 667 tables expected.

**Possible Causes**:
1. Summary tables (mkt_reg_summary, mkt_reg_bqx_summary) were extracted
2. Retry created duplicate checkpoint
3. Off-by-one in checkpoint counting

**Remediation**: Verify checkpoint contents after merge completes.

---

## STEP 6 CURRENT STATUS

| Metric | Value |
|--------|-------|
| Process | PID 1493048 |
| CPU | 99.3% |
| Memory | 8.6 GB (13.2%) |
| Phase | **MERGE IN PROGRESS** |
| Checkpoints | 668 |
| Merged file | Not yet created |

---

## INTELLIGENCE FILE CONSISTENCY

| Metric | Status |
|--------|--------|
| Model count (588) | ✅ Consistent |
| Table count (667) | ✅ Updated |
| Market wide (10) | ✅ Updated |
| Ensemble (3 members) | ✅ Consistent |
| Horizons (7) | ✅ Consistent |

---

## RECOMMENDATIONS

### Immediate (Today)
1. **DELETE** summary table checkpoints before training
2. **VERIFY** merged parquet excludes summary tables
3. **FIX** target columns (7 → 49) per mandate

### Short-term
4. Update extraction script to exclude summary tables permanently
5. Full codebase grep for "669" references
6. Validate merged parquet schema matches expected columns

---

**Quality Assurance Agent (QA)**
