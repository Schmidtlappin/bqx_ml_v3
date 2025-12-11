# MASTER ISSUE LIST - December 11, 2025 09:35 UTC

**Aggregated From**: QA, BA, EA Reports
**Chief Engineer (CE)**: Master List with Remediation Assignments

---

## EXECUTIVE SUMMARY

| Severity | New | Carried | Total |
|----------|-----|---------|-------|
| **CRITICAL (P0)** | 2 | 0 | **2** |
| **HIGH (P1)** | 1 | 2 | **3** |
| **MEDIUM (P2)** | 4 | 3 | **7** |
| **LOW (P3)** | 3 | 4 | **7** |
| **TOTAL OPEN** | **10** | **9** | **19** |

---

## CRITICAL ISSUES (P0) - IMMEDIATE ACTION REQUIRED

### ISSUE-C01: Target Columns Incomplete (7 vs 49)
| Field | Value |
|-------|-------|
| **Source** | QA Report 09:30 |
| **Severity** | **CRITICAL** |
| **Owner** | **BA** |
| **Status** | UNRESOLVED |

**Description**: `targets_eurusd` checkpoint has only **7 target columns** (bqx_45 window only). Expected 49 columns (7 windows × 7 horizons).

**Missing**:
- bqx_90 targets (7 columns)
- bqx_180 targets (7 columns)
- bqx_360 targets (7 columns)
- bqx_720 targets (7 columns)
- bqx_1440 targets (7 columns)
- bqx_2880 targets (7 columns)

**Impact**: **CANNOT TRAIN MODELS** without complete target data per mandate.

**Remediation**:
1. BA: Verify BigQuery `targets_eurusd` has all 49 columns
2. BA: If missing in BQ, regenerate targets per `/mandate/BQX_TARGET_FORMULA_MANDATE.md`
3. BA: Update extraction to include all 49 target columns

---

### ISSUE-C02: Summary Tables Extracted Despite Exclusion Directive
| Field | Value |
|-------|-------|
| **Source** | QA Report 09:30 |
| **Severity** | **CRITICAL** |
| **Owner** | **BA** |
| **Status** | UNRESOLVED |

**Description**: Log shows `mkt_reg_summary` and `mkt_reg_bqx_summary` were EXTRACTED (277 cols each) despite CE directive to exclude.

**Evidence**:
```
[620/669] mkt_reg_summary: +277 cols SAVED
[622/669] mkt_reg_bqx_summary: +277 cols SAVED
```

**Impact**: 554 extraneous metadata columns in feature set, may cause training failures.

**Remediation**:
1. BA: Delete checkpoints `mkt_reg_summary.parquet`, `mkt_reg_bqx_summary.parquet`
2. BA: Re-run merge excluding these files
3. BA: Verify extraction script has exclusion filter

---

## HIGH PRIORITY ISSUES (P1)

### ISSUE-H01: V1 Analytics Dataset Pending Deletion
| Field | Value |
|-------|-------|
| **Source** | CE Directive 08:25, BA Report |
| **Owner** | **BA** |
| **Status** | PENDING (after merge) |

**Dataset**: `bqx_ml_v3_analytics` (29 rogue tables)
**Action**: Execute `bq rm -r -f bqx-ml:bqx_ml_v3_analytics` after EURUSD merge completes

---

### ISSUE-H02: Parquet Output Validation Required
| Field | Value |
|-------|-------|
| **Source** | Multiple agents (EA-004, BA-006, QA-003) |
| **Owner** | **QA** |
| **Status** | PENDING (await merge) |

**Action**: Execute validation checklist when merged parquet is created

---

### ISSUE-H03: Coverage Below Target (17.33% vs 30-50%)
| Field | Value |
|-------|-------|
| **Source** | GATE_3, QA-001 |
| **Owner** | **QA** (after Step 6) |
| **Status** | IN PROGRESS |

**Action**: Re-validate coverage after full feature universe testing

---

## MEDIUM PRIORITY ISSUES (P2)

### ISSUE-M01: Intelligence Files May Reference 669
| Field | Value |
|-------|-------|
| **Source** | QA Report 09:30 |
| **Owner** | **QA** |
| **Status** | PARTIAL |

**Checked**: context.json, ontology.json, semantics.json ✅
**Unchecked**: mandate/*.md, README files

**Action**: Full grep for "669" across codebase

---

### ISSUE-M02: 668 Checkpoints vs 667 Expected
| Field | Value |
|-------|-------|
| **Source** | QA Report 09:30 |
| **Owner** | **QA** |
| **Status** | INFORMATIONAL |

**Cause**: Summary tables were extracted before exclusion
**Action**: Verify after merge completes

---

### ISSUE-M03: Step 6 Merge Extended Duration
| Field | Value |
|-------|-------|
| **Source** | BA Report 09:30 |
| **Owner** | **BA** |
| **Status** | IN PROGRESS |

**Action**: Monitor; consider chunked merge for future runs

---

### ISSUE-M04: Debug Output Still Enabled
| Field | Value |
|-------|-------|
| **Source** | BA Report |
| **Owner** | **BA** |
| **Location** | `parallel_feature_testing.py:483` |

**Action**: Remove after Step 6 completes

---

### ISSUE-M05-M07: Stale Comments/Headers
Various cosmetic issues in code comments. Low impact.

---

## LOW PRIORITY ISSUES (P3)

| ID | Issue | Owner | Decision |
|----|-------|-------|----------|
| L01 | Python 3.10 deprecation | CE | DEFER (2026) |
| L02 | BQ Storage API optimization | BA | DEFER |
| L03 | Hardcoded date range | BA | DEFER |
| L04 | No retry logic | BA | DEFER |
| L05 | Monitor script header | BA | DEFER |
| L06 | Code comment 12→16 workers | BA | DEFER |
| L07 | Centralized error logging | EA | DEFER |

---

## REMEDIATION ASSIGNMENTS

### BA (Build Agent) - 5 Items
| Priority | Issue | Action |
|----------|-------|--------|
| **P0** | ISSUE-C01 | Verify/regenerate 49 target columns |
| **P0** | ISSUE-C02 | Delete summary checkpoints, re-merge |
| **P1** | ISSUE-H01 | Delete V1 analytics after merge |
| **P2** | ISSUE-M03 | Monitor merge completion |
| **P2** | ISSUE-M04 | Remove debug output |

### QA (Quality Assurance) - 4 Items
| Priority | Issue | Action |
|----------|-------|--------|
| **P1** | ISSUE-H02 | Validate merged parquet |
| **P1** | ISSUE-H03 | Re-validate coverage |
| **P2** | ISSUE-M01 | Grep for "669" references |
| **P2** | ISSUE-M02 | Verify checkpoint count |

### EA (Enhancement Agent) - 1 Item
| Priority | Issue | Action |
|----------|-------|--------|
| **P2** | ISSUE-M03 | Monitor memory during merge |

---

## IMMEDIATE ACTIONS (Next 30 Minutes)

1. **BA**: Verify `bqx-ml.bqx_ml_v3_analytics_v2.targets_eurusd` has 49 columns
2. **BA**: If targets incomplete, report to CE immediately
3. **BA**: Delete summary checkpoints if present
4. **BA**: Monitor merge completion
5. **QA**: Prepare validation script for merged parquet

---

## SUCCESS CRITERIA

- [ ] ISSUE-C01: targets_eurusd has 49 columns (7×7)
- [ ] ISSUE-C02: Summary tables excluded from merge
- [ ] ISSUE-H01: V1 analytics deleted
- [ ] ISSUE-H02: Merged parquet passes validation
- [ ] All intelligence files use 667 (not 669)

---

**Chief Engineer (CE)**
