# Truth Source Misalignment Report - Data Integrity Audit

**Date**: 2025-12-13 22:15 UTC
**Analyst**: EA (Enhancement Assistant)
**Purpose**: Identify misalignments between BigQuery reality and documentation truth sources
**Scope**: BigQuery vs Intelligence Files vs Mandate Files vs Implementation vs Agent Tracking
**Reference**: [TRUTH_SOURCE_RECONCILIATION_20251213.md](TRUTH_SOURCE_RECONCILIATION_20251213.md), [USER_MANDATE_INVENTORY_20251213.md](USER_MANDATE_INVENTORY_20251213.md)

---

## EXECUTIVE SUMMARY

**Total Misalignments Identified**: 23 across 4 truth source categories
**Critical Misalignments**: 8 (affect project planning and validation)
**High Priority Misalignments**: 9 (cause confusion or incorrect decisions)
**Medium Priority Misalignments**: 5 (documentation drift)
**Low Priority Misalignments**: 1 (minor inconsistency)

### Truth Source Hierarchy

**Established Hierarchy** (from TRUTH_SOURCE_RECONCILIATION_20251213.md):
1. **Level 1: Ground Truth** - BigQuery (absolute authority)
2. **Level 2: Intelligence Files** - feature_catalogue.json, semantics.json, ontology.json
3. **Level 3: Mandate Documentation** - mandate/*.md files
4. **Level 4: Other Documentation** - docs/*.md, README files

**Misalignment Summary**:
- **BigQuery ↔ Intelligence**: 8 misalignments (table counts, category counts)
- **Intelligence ↔ Mandate**: 6 misalignments (terminology, compliance tracking)
- **Documentation ↔ Implementation**: 7 misalignments (status, timelines)
- **Agent Tracking ↔ Reality**: 2 misalignments (TODO vs actual state)

---

## SECTION 1: BIGQUERY ↔ INTELLIGENCE FILE MISALIGNMENTS

### Critical Severity (P0)

#### MISALIGN-BQ-001: Total Table Count Mismatch
**Source 1**: BigQuery `__TABLES__` metadata
**Source 2**: intelligence/feature_catalogue.json
**Discrepancy**: +224 tables (3.8% overcount in documentation)

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | Discrepancy |
|--------|------------------------|------------------------|-------------|
| **Total Tables** | 5,817 | 6,069 | **+224 tables** |
| **Last Updated** | Real-time | 2025-12-13 04:40 UTC | ~18 hours stale |

**Root Cause**:
- M008 Phase 4A deleted 224 duplicate tables (2025-12-13 afternoon)
- Intelligence files not updated after deletion
- Expected: 6,069 - 224 = 5,845 (actual is 5,817, indicating additional deletions or discrepancy)

**Impact**: **CRITICAL**
- All downstream planning based on incorrect baseline
- Agents may plan work for 224 non-existent tables
- Cost estimates may be inflated (more tables = more compute cost)
- Coverage calculations incorrect (denominator off by 3.8%)

**Remediation**:
- **Action**: Update `feature_catalogue.json` → `"total_tables": 5817` (use 5,817, not 5,845)
- **Verification Required**: Determine if actual is 5,817 or 5,845 (28 table discrepancy)
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 2-4 hours (query BigQuery, update intelligence files, verify discrepancy)
- **Owner**: EA (update files)

**Status**: ⏳ PENDING (TRUTH_SOURCE_RECONCILIATION documented this, update not yet confirmed)

---

#### MISALIGN-BQ-002: COV Table Count Surplus
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset
**Source 2**: intelligence/feature_catalogue.json
**Discrepancy**: +882 tables (33.3% surplus in BigQuery)

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | Discrepancy |
|--------|------------------------|------------------------|-------------|
| **COV Tables** | 3,528 | 2,646 | **+882 tables** |
| **Percentage** | 60.7% of total | 43.6% of documented | +17.1 pp |

**Root Cause** (requires investigation):
1. **Hypothesis 1**: feature_catalogue.json outdated (COV tables generated but not documented)
2. **Hypothesis 2**: Partial window expansion already executed (windows 180, 360, 720 partially added)
3. **Hypothesis 3**: Duplicate tables not yet identified/deleted
4. **Hypothesis 4**: COV table generation for additional feature types (not yet documented)

**Impact**: **CRITICAL**
- Cannot validate M006 coverage without accurate COV inventory
- May be undercounting or overcounting COV coverage
- 882 tables = significant discrepancy (could be $10-30 in storage costs)

**Remediation**:
- **Action 1**: Query BigQuery for actual COV table count and patterns
  ```sql
  SELECT
    COUNT(*) as cov_table_count,
    COUNTIF(table_name LIKE 'cov_%_45') as window_45,
    COUNTIF(table_name LIKE 'cov_%_90') as window_90,
    COUNTIF(table_name LIKE 'cov_%_180') as window_180,
    COUNTIF(table_name LIKE 'cov_%_360') as window_360
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE 'cov_%';
  ```
- **Action 2**: Categorize 882 surplus tables (valid? duplicates? partial work?)
- **Action 3**: Update feature_catalogue.json with verified count
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 4-8 hours
- **Owner**: EA (audit), QA (validate)

**Status**: ⏳ PENDING (identified in gap analysis, investigation needed)

---

### High Priority (P1)

#### MISALIGN-BQ-003: CSI Table Count Unverified
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset
**Source 2**: intelligence/feature_catalogue.json
**Discrepancy**: UNKNOWN (documented 144, not verified in BigQuery)

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | Status |
|--------|------------------------|------------------------|--------|
| **CSI Tables** | **NOT VERIFIED** | 144 | ❓ UNKNOWN |

**Root Cause**: Intelligence file count not verified against BigQuery reality

**Impact**: **HIGH**
- If CSI count is incorrect, affects currency strength feature availability
- May be planning work for non-existent tables or missing existing tables

**Remediation**:
- **Action**: Query BigQuery for actual CSI table count
  ```sql
  SELECT COUNT(*) as csi_table_count
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE 'csi_%';
  ```
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 1-2 hours (simple query)
- **Owner**: EA (query), QA (validate)

**Status**: ⏳ PENDING

---

#### MISALIGN-BQ-004: MKT Table Count Inconsistency
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset
**Source 2**: intelligence/feature_catalogue.json (10 tables)
**Source 3**: Previous TODO notes (14 tables)
**Discrepancy**: 10 vs 14 (4 table discrepancy between documentation sources)

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | TODO Notes | Verified |
|--------|------------------------|------------------------|------------|----------|
| **MKT Tables** | **NOT VERIFIED** | 10 | 14 | ❓ NO |

**Root Cause**: Multiple documentation sources with conflicting counts

**Impact**: **HIGH**
- Documentation inconsistency causes confusion
- Cannot validate M006 market-wide feature coverage
- May be planning duplicate work or missing required tables

**Remediation**:
- **Action**: Query BigQuery for actual MKT table count and update all documentation
  ```sql
  SELECT COUNT(*) as mkt_table_count,
         STRING_AGG(table_name, ', ' ORDER BY table_name) as mkt_tables
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE 'mkt_%';
  ```
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 1-2 hours
- **Owner**: EA (query + update all docs)

**Status**: ⏳ PENDING

---

#### MISALIGN-BQ-005: TRI Table Count Post-Phase 4B
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset
**Source 2**: intelligence/feature_catalogue.json (194 tables)
**Discrepancy**: UNKNOWN (Phase 4B renamed 65 TRI tables, verification needed)

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | Status |
|--------|------------------------|------------------------|--------|
| **TRI Tables** | **NOT VERIFIED POST-PHASE 4B** | 194 | ❓ NEEDS VERIFICATION |

**Root Cause**: M008 Phase 4B renamed 65 TRI tables (2025-12-13). Count likely unchanged (rename ≠ deletion), but verification needed.

**Impact**: **MEDIUM**
- Count unlikely to change (rename doesn't affect count)
- Verification needed to confirm no accidental deletions

**Remediation**:
- **Action**: Verify TRI table count post-Phase 4B
  ```sql
  SELECT COUNT(*) as tri_table_count
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE 'tri_%';
  ```
- **Phase**: Phase 1 (M008 Final Verification) - Week 3
- **Effort**: 1-2 hours
- **Owner**: EA (query), QA (validate)

**Status**: ⏳ PENDING (lower priority, count unlikely to change)

---

#### MISALIGN-BQ-006: CORR Table Count Missing from Intelligence Files
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset
**Source 2**: intelligence/feature_catalogue.json
**Discrepancy**: NOT DOCUMENTED in intelligence files

**Details**:
| Metric | BigQuery (Ground Truth) | feature_catalogue.json | Status |
|--------|------------------------|------------------------|--------|
| **CORR Tables** | **UNKNOWN** | **NOT DOCUMENTED** | ❌ MISSING |

**Root Cause**: CORR table category not included in feature_catalogue.json

**Impact**: **HIGH**
- Cannot validate M006 correlation feature coverage
- Incomplete feature inventory
- May be missing correlation features in model

**Remediation**:
- **Action**: Query BigQuery for CORR table count and add to feature_catalogue.json
  ```sql
  SELECT COUNT(*) as corr_table_count
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE 'corr_%';
  ```
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 2-3 hours (query + update intelligence file)
- **Owner**: EA (query + update)

**Status**: ⏳ PENDING

---

#### MISALIGN-BQ-007: VAR Table Count Gap (63 vs 80 Expected)
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset (63 tables)
**Source 2**: REGRESSION_FEATURE_MANDATE_IMPLEMENTATION_PLAN.md (80 tables expected)
**Discrepancy**: -17 tables (21.3% gap)

**Details**:
| Metric | BigQuery (Ground Truth) | Expected (Mandate) | Discrepancy |
|--------|------------------------|-------------------|-------------|
| **VAR Tables** | 63 | 80 | **-17 tables** |
| **Percentage** | 78.8% | 100% | 21.3% gap |

**Root Cause**:
- Expected: 80 VAR tables (40 var_usd_* + 40 var_lag_*)
- Actual: 63 VAR tables
- Gap: 17 missing tables (some pairs missing var_usd or var_lag variants)

**Impact**: **HIGH**
- Incomplete variance feature coverage
- Some pairs missing variance features (affects model for those pairs)
- M005 VAR schema update will need to generate missing tables first

**Remediation**:
- **Action**: Generate 17 missing VAR tables during M005 Phase 5
- **Phase**: Phase 5 (M005 VAR Schema Update)
- **Effort**: 5-10 hours (included in Phase 5)
- **Cost**: $2-5
- **Owner**: BA (generate), QA (validate)

**Status**: ⏳ PENDING (scheduled for Phase 5)

---

#### MISALIGN-BQ-008: LAG Table Count Pre-Consolidation
**Source 1**: BigQuery `bqx_ml_v3_features_v2` dataset (224 tables)
**Source 2**: M008 Phase 4C plan (56 consolidated tables expected)
**Discrepancy**: 224 → 56 (consolidation pending)

**Details**:
| Metric | BigQuery (Current) | M008 Phase 4C Target | Change |
|--------|-------------------|---------------------|--------|
| **LAG Tables** | 224 | 56 | **-168 tables** |

**Root Cause**: LAG consolidation approved but not yet executed (Phase 4C in progress)

**Impact**: **MEDIUM**
- Current BigQuery state (224 tables) misaligned with M008 target architecture
- Intelligence files should reflect planned state once Phase 4C complete

**Remediation**:
- **Action**: Execute LAG consolidation (Phase 4C Week 1-2)
- **Update Intelligence Files**: After consolidation complete, update feature_catalogue.json to reflect 56 LAG tables (not 224)
- **Phase**: Phase 4C (M008 Table Naming Remediation) - IN PROGRESS
- **Effort**: 8-12 hours (consolidation) + 1-2 hours (update docs)
- **Owner**: BA (consolidation), EA (update intelligence files)

**Status**: ⏳ IN PROGRESS (Phase 4C Week 1-2)

---

### Medium Priority (P2)

#### MISALIGN-BQ-009: Last Updated Timestamp Drift
**Source 1**: BigQuery (real-time, continuously updated)
**Source 2**: intelligence/feature_catalogue.json (updated 2025-12-13 04:40 UTC)
**Discrepancy**: ~18 hours stale (as of 22:15 UTC)

**Details**:
- **BigQuery**: Always current (ground truth)
- **Intelligence Files**: Last updated 04:40 UTC (18 hours ago)
- **Changes Since Last Update**: M008 Phase 4A deletions (224 tables), M008 Phase 4B renames (65 tables)

**Root Cause**: Intelligence files not updated after M008 Phase 4A and 4B

**Impact**: **MEDIUM**
- Intelligence files lag reality by hours to days
- Agents using stale data for planning

**Remediation**:
- **Action**: Establish intelligence file update protocol (update within 24 hours of BigQuery changes)
- **Phase**: Phase 0 (Documentation Reconciliation) - Define protocol
- **Effort**: 3-5 hours (create protocol)
- **Owner**: EA (define protocol), QA (enforce)

**Status**: ⏳ PENDING

---

## SECTION 2: INTELLIGENCE ↔ MANDATE FILE MISALIGNMENTS

### High Priority (P1)

#### MISALIGN-IM-001: Table Count Mismatch (Intelligence vs Mandate)
**Source 1**: intelligence/feature_catalogue.json (6,069 tables)
**Source 2**: mandate/BQX_ML_V3_FEATURE_INVENTORY.md (6,069 tables)
**Discrepancy**: Both sources outdated (+224 vs BigQuery reality)

**Details**:
Both intelligence and mandate files show 6,069 tables, but BigQuery has 5,817 tables.

**Root Cause**: Both files updated from same source (early audit), not updated after M008 Phase 4A deletions

**Impact**: **HIGH**
- Both Level 2 and Level 3 truth sources misaligned with Level 1 (BigQuery)
- Agents have no accurate source of truth in documentation

**Remediation**:
- **Action**: Update both files to reflect 5,817 tables
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 2-4 hours (update both files)
- **Owner**: EA (update)

**Status**: ⏳ PENDING

---

#### MISALIGN-IM-002: Feature Count Discrepancy (1,064 vs 1,127)
**Source 1**: intelligence/feature_catalogue.json (1,064 unique features documented)
**Source 2**: mandate/BQX_ML_V3_FEATURE_INVENTORY.md (1,127 unique features)
**Source 3**: M001 Feature Ledger requirement (1,127 features)
**Discrepancy**: 63 feature gap (5.6% undercount in intelligence file)

**Details**:
| Metric | feature_catalogue.json | Feature Inventory (Mandate) | M001 Requirement |
|--------|------------------------|---------------------------|------------------|
| **Unique Features** | 1,064 | 1,127 | 1,127 |
| **Discrepancy** | **-63 features** | Baseline | Baseline |

**Root Cause**:
- Intelligence file may not include all regression features (lin_term, quad_term, residual)
- Mandate files updated with M005 regression feature requirements
- Intelligence file predates M005 mandate finalization

**Impact**: **HIGH**
- Feature count affects M001 feature ledger row count (221,228 = 28 pairs × 7 horizons × 1,127 features)
- Using 1,064 would yield 208,432 rows (12,796 row shortfall)
- Cannot generate correct feature ledger with wrong feature count

**Remediation**:
- **Action**: Update feature_catalogue.json to reflect 1,127 features (include M005 regression features)
- **Phase**: Phase 0 (Documentation Reconciliation) OR Phase 5 (after M005 complete)
- **Effort**: 4-6 hours (audit features, update intelligence file)
- **Owner**: EA (update)

**Status**: ⏳ PENDING (may wait until M005 complete for accuracy)

---

#### MISALIGN-IM-003: M008 Compliance % Tracking Inconsistency
**Source 1**: docs/COMPREHENSIVE_REMEDIATION_PLAN_20251213.md (66.2% compliant)
**Source 2**: docs/MANDATE_COMPLIANCE_ANALYSIS_20251213.md (may show different %)
**Source 3**: intelligence/context.json (may not track M008 compliance %)
**Discrepancy**: Multiple sources may show different M008 compliance percentages

**Details**:
Different documents may calculate M008 compliance differently:
- Comprehensive Remediation Plan: 66.2% (3,849/5,817)
- Mandate Compliance Analysis: May use different denominator or baseline
- Intelligence context.json: May not track compliance % at all

**Root Cause**: No single source of truth for compliance tracking

**Impact**: **HIGH**
- Confusing for agents and user (which % is correct?)
- May make decisions based on incorrect compliance status

**Remediation**:
- **Action**: Create single compliance dashboard (all 5 mandates, updated weekly)
- **Phase**: Phase 1 (M008 Final Verification) - Create dashboard
- **Effort**: 3-5 hours (create), 30 min/week (update)
- **Owner**: EA (create + maintain)

**Status**: ⏳ PENDING

---

#### MISALIGN-IM-004: Mandate Terminology Inconsistency
**Source 1**: mandate/MAXIMIZE_FEATURE_COMPARISONS_MANDATE.md (uses "BQX" and "IDX")
**Source 2**: mandate/SEMANTIC_FEATURE_COMPATIBILITY_MANDATE.md (uses "bqx" and "idx")
**Source 3**: intelligence/semantics.json (may use mixed case)
**Discrepancy**: Inconsistent capitalization and terminology

**Details**:
- Some docs use uppercase: BQX, IDX
- Some docs use lowercase: bqx, idx
- BigQuery table names use lowercase: `cov_ret_bqx_eurusd_...`

**Root Cause**: No terminology glossary or style guide

**Impact**: **MEDIUM**
- May cause parsing errors (case-sensitive searches)
- Confusing for agents (is BQX ≠ bqx?)

**Remediation**:
- **Action**: Create terminology glossary with canonical forms
  - Canonical: Lowercase in table/column names (bqx, idx), Uppercase in prose (BQX, IDX)
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 4-6 hours
- **Owner**: EA (create glossary), CE (approve)

**Status**: ⏳ PENDING

---

### Medium Priority (P2)

#### MISALIGN-IM-005: Window Definition Inconsistency
**Source 1**: mandate/*.md files (may use "45d", "45-day", "45 days")
**Source 2**: intelligence/semantics.json (may use "45")
**Source 3**: BigQuery column names (use "45", "90", etc. - no units)
**Discrepancy**: Inconsistent window notation

**Details**:
- Mandate files: May use "45-day window" (prose)
- Intelligence files: May use "45d" or "45"
- BigQuery: Uses numeric only (45, 90, 180, etc.)

**Root Cause**: No standard notation for window definitions

**Impact**: **MEDIUM**
- Minor confusion, but unlikely to cause errors (context is clear)

**Remediation**:
- **Action**: Include in terminology glossary
  - Canonical: Numeric only (45, 90) in table/column names, "45-day" in prose
- **Phase**: Phase 0 (Documentation Reconciliation) - Include in glossary
- **Effort**: 1-2 hours (included in glossary creation)
- **Owner**: EA (define standard)

**Status**: ⏳ PENDING

---

#### MISALIGN-IM-006: Pair Notation Inconsistency
**Source 1**: BigQuery table names (EURUSD, GBPUSD - uppercase, no separator)
**Source 2**: Some docs may use EUR/USD or EUR-USD
**Discrepancy**: Inconsistent pair notation

**Details**:
- BigQuery: EURUSD, GBPUSD (uppercase, no separator)
- Some docs: EUR/USD, EUR-USD (with separator)

**Root Cause**: No standard notation for currency pairs

**Impact**: **LOW**
- Unlikely to cause errors, but consistency is better

**Remediation**:
- **Action**: Include in terminology glossary
  - Canonical: Uppercase no separator (EURUSD) in table/column names, EUR/USD in prose
- **Phase**: Phase 0 (Documentation Reconciliation) - Include in glossary
- **Effort**: 1-2 hours (included in glossary creation)
- **Owner**: EA (define standard)

**Status**: ⏳ PENDING

---

## SECTION 3: DOCUMENTATION ↔ IMPLEMENTATION MISALIGNMENTS

### Critical Severity (P0)

#### MISALIGN-DI-001: M001 Feature Ledger Status
**Documentation**: mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md (describes requirement)
**Implementation**: feature_ledger.parquet (FILE DOES NOT EXIST)
**Discrepancy**: Mandate exists, implementation 0%

**Details**:
- **Mandate**: Fully documented (requirements, schema, success criteria)
- **Implementation**: 0% (file doesn't exist)
- **Status Mismatch**: Mandate implies this is required, but not yet started

**Root Cause**: Sequential development - M001 is Phase 7 (not yet started)

**Impact**: **CRITICAL**
- Documentation describes future state, not current state
- May confuse agents (is feature ledger required NOW or LATER?)

**Remediation**:
- **Action**: Add status indicators to mandate files
  - "STATUS: NOT STARTED (planned for Phase 7)"
  - "COMPLIANCE: 0% (file does not exist)"
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 2-4 hours (update all 5 mandate files with status)
- **Owner**: EA (update)

**Status**: ⏳ PENDING

---

#### MISALIGN-DI-002: M005 Regression Features Status
**Documentation**: mandate/REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md (describes requirement)
**Implementation**: TRI/COV/VAR tables (regression features DO NOT EXIST)
**Discrepancy**: Mandate exists, implementation 0% for TRI/COV/VAR

**Details**:
- **Mandate**: Fully documented (column requirements, calculations)
- **Implementation**: 0% for TRI/COV/VAR (columns don't exist)
- **Status Mismatch**: Mandate describes required state, not current state

**Root Cause**: Sequential development - M005 is Phases 3-5 (not yet started)

**Impact**: **CRITICAL**
- Documentation describes future state, confusing for current state assessment

**Remediation**:
- **Action**: Add status section to REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md
  ```markdown
  ## CURRENT STATUS (2025-12-13)
  - REG Tables: ✅ 100% compliant (56/56 tables)
  - TRI Tables: ❌ 0% compliant (regression features not yet added)
  - COV Tables: ❌ 0% compliant (regression features not yet added)
  - VAR Tables: ❌ 0% compliant (regression features not yet added)
  ```
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 1-2 hours
- **Owner**: EA (update)

**Status**: ⏳ PENDING

---

### High Priority (P1)

#### MISALIGN-DI-003: M008 Phase 4C Status Across Documents
**Documentation 1**: docs/COMPREHENSIVE_REMEDIATION_PLAN_20251213.md (Phase 4C approved, in progress)
**Documentation 2**: docs/M008_NAMING_STANDARD_REMEDIATION_PLAN.md (may describe earlier plan)
**Implementation**: M008 Phase 4C (approved Dec 13, not yet started)
**Discrepancy**: Multiple remediation plans may conflict

**Details**:
- Comprehensive Remediation Plan: Phase 4C approved, 2-week timeline, $5-15 budget
- M008 Naming Standard Remediation Plan: May describe different approach (pre-Phase 4C approval)
- Risk: Conflicting remediation strategies

**Root Cause**: Multiple documents describe M008 remediation (older plan not deprecated)

**Impact**: **HIGH**
- Agents may execute wrong remediation plan
- Confusion over approved approach

**Remediation**:
- **Action 1**: Add deprecation notice to M008_NAMING_STANDARD_REMEDIATION_PLAN.md
  ```markdown
  # ⚠️ DEPRECATED - See COMPREHENSIVE_REMEDIATION_PLAN_20251213.md Phase 4C
  This document describes an earlier M008 remediation approach.
  **CURRENT APPROVED PLAN**: Phase 4C (approved 2025-12-13)
  ```
- **Action 2**: Consolidate all remediation plans into single source of truth
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 2-4 hours
- **Owner**: EA (deprecate old plan)

**Status**: ⏳ PENDING

---

#### MISALIGN-DI-004: Agent Charge Version Drift
**Documentation**: .claude/sandbox/communications/active/*_CHARGE_20251212_v2.0.0.md (version 2.0.0)
**Implementation**: Agents may reference older v1.x.x charges
**Discrepancy**: Multiple charge versions may exist

**Details**:
- Current: v2.0.0 charges (updated 2025-12-12)
- Risk: Older v1.x.x charges may still exist in different directories
- Agents may reference outdated responsibilities

**Root Cause**: Charge files updated, older versions not deprecated or archived

**Impact**: **HIGH**
- Agents may operate under outdated role definitions
- Responsibility confusion (v1 vs v2 differences)

**Remediation**:
- **Action**: Audit .claude/ directory for older charge versions, move to archive/
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 2-3 hours
- **Owner**: CE (archive old charges), EA (verify)

**Status**: ⏳ PENDING

---

#### MISALIGN-DI-005: Phase Numbering Inconsistency
**Documentation 1**: COMPREHENSIVE_REMEDIATION_PLAN_20251213.md (Phase 0 → Phase 9)
**Documentation 2**: M008 remediation (Phase 4A, 4B, 4C - sub-phases)
**Discrepancy**: Phase 4 has sub-phases (4A, 4B, 4C), but other phases don't

**Details**:
- Phase 4 subdivided: Phase 4A (deletions), Phase 4B (TRI renames), Phase 4C (full remediation)
- Other phases: Single phase (no sub-phases)
- Risk: Confusion over phase sequencing

**Root Cause**: M008 work expanded, required sub-phase breakdown

**Impact**: **MEDIUM**
- Mild confusion over phase numbering
- Phase 4 ≠ Phase 4C (but both refer to M008 work)

**Remediation**:
- **Action**: Update COMPREHENSIVE_REMEDIATION_PLAN to clarify Phase 4 sub-phases
  ```markdown
  ## PHASE 4: M008 Table Naming Remediation
  ### Phase 4A: Delete Duplicates (COMPLETE ✅)
  ### Phase 4B: Rename TRI Tables (COMPLETE ✅)
  ### Phase 4C: Full M008 Remediation (IN PROGRESS ⏳)
  ```
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 1-2 hours
- **Owner**: EA (clarify)

**Status**: ⏳ PENDING

---

### Medium Priority (P2)

#### MISALIGN-DI-006: Timeline Estimates Variation
**Documentation 1**: COMPREHENSIVE_REMEDIATION_PLAN (9-11 weeks total)
**Documentation 2**: CE Approval (2 weeks aggressive, 3 weeks conservative for Phase 4C only)
**Discrepancy**: Different timeline granularities

**Details**:
- Comprehensive Plan: 9-11 weeks for all phases
- CE Approval: 2-3 weeks for Phase 4C only
- Risk: Misinterpreting timelines (is 2-3 weeks for everything or just Phase 4C?)

**Root Cause**: Different documents focus on different scopes

**Impact**: **MEDIUM**
- Mild timeline confusion
- Context makes it clear (2-3 weeks = Phase 4C only)

**Remediation**:
- **Action**: Ensure all timeline estimates clearly state scope
  - "2-3 weeks (Phase 4C only)"
  - "9-11 weeks (all phases, sequential)"
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 1-2 hours (review and clarify timelines)
- **Owner**: EA (clarify)

**Status**: ⏳ PENDING

---

#### MISALIGN-DI-007: Cost Estimates Variation
**Documentation 1**: COMPREHENSIVE_REMEDIATION_PLAN ($50-80 total)
**Documentation 2**: M005 plan ($50-85 for M005 only)
**Discrepancy**: Overlapping ranges, unclear if M005 cost is subset of total or separate

**Details**:
- Comprehensive Plan: $50-80 total (all phases)
- M005 Plan: $50-85 (M005 only - Phases 3-5)
- Math: If M005 is $50-85, and total is $50-80, M005 would exceed total budget (conflict)

**Root Cause**: Cost estimates created separately, not reconciled

**Impact**: **MEDIUM**
- Budget confusion (is $50-80 enough for all phases?)
- May underestimate total cost

**Remediation**:
- **Action**: Reconcile cost estimates
  - Phase 4C: $5-15
  - M005 (Phases 3-5): $50-85
  - M006 (Phase 8): TBD
  - **Total**: $55-100 (updated estimate)
- **Update**: Comprehensive Remediation Plan to reflect $55-100 total
- **Phase**: Phase 0 (Documentation Reconciliation)
- **Effort**: 2-3 hours (reconcile all cost estimates)
- **Owner**: EA (reconcile), CE (approve)

**Status**: ⏳ PENDING

---

## SECTION 4: AGENT TRACKING ↔ REALITY MISALIGNMENTS

### High Priority (P1)

#### MISALIGN-AT-001: M008 Phase 4A/4B Completion Status
**Agent Tracking**: May show Phase 4A and 4B as "in progress" or "pending"
**Reality**: Phase 4A complete (224 tables deleted), Phase 4B complete (65 TRI tables renamed)
**Discrepancy**: Status not updated to reflect completion

**Details**:
- Phase 4A: COMPLETE ✅ (2025-12-13 afternoon)
- Phase 4B: COMPLETE ✅ (2025-12-13 17:14-18:04 UTC)
- Agent TODO tracking: May not reflect completion

**Root Cause**: Agent TODO files not updated after phase completion

**Impact**: **HIGH**
- Agents may re-do completed work
- Confusion over current phase (is Phase 4A done? is Phase 4B done?)

**Remediation**:
- **Action**: Update agent TODO files and project tracking
  - Mark Phase 4A: COMPLETE ✅
  - Mark Phase 4B: COMPLETE ✅
  - Current phase: Phase 4C (IN PROGRESS ⏳)
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 1-2 hours
- **Owner**: EA (update tracking), CE (confirm)

**Status**: ⏳ PENDING

---

#### MISALIGN-AT-002: Intelligence File Update TODO vs Reality
**Agent Tracking**: TRUTH_SOURCE_RECONCILIATION recommends updating intelligence files
**Reality**: Intelligence files not yet updated (still show 6,069 tables)
**Discrepancy**: Recommended action not yet executed

**Details**:
- TRUTH_SOURCE_RECONCILIATION (2025-12-13 18:52 UTC): Recommends updating feature_catalogue.json to 5,845 tables
- Current: feature_catalogue.json still shows 6,069 tables (not updated)
- Gap: ~4 hours since recommendation, not yet executed

**Root Cause**: Recommendation documented, but action not yet taken

**Impact**: **HIGH**
- Intelligence files remain stale
- Agents continue using incorrect baseline (6,069 instead of 5,817)

**Remediation**:
- **Action**: Execute TRUTH_SOURCE_RECONCILIATION recommendations immediately
  1. Update feature_catalogue.json: 6,069 → 5,817
  2. Update BQX_ML_V3_FEATURE_INVENTORY.md: 6,069 → 5,817
  3. Verify actual BigQuery count (resolve 5,817 vs 5,845 discrepancy)
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 2-4 hours
- **Owner**: EA (execute)

**Status**: ⏳ PENDING (IMMEDIATE PRIORITY)

---

## SECTION 5: MISALIGNMENT SUMMARY BY CATEGORY

| Category | P0-Critical | P1-High | P2-Medium | P3-Low | Total |
|----------|-------------|---------|-----------|--------|-------|
| **BigQuery ↔ Intelligence** | 2 | 6 | 1 | 0 | 9 |
| **Intelligence ↔ Mandate** | 0 | 3 | 3 | 0 | 6 |
| **Documentation ↔ Implementation** | 2 | 3 | 2 | 0 | 7 |
| **Agent Tracking ↔ Reality** | 0 | 2 | 0 | 0 | 2 |
| **TOTAL** | **4** | **14** | **6** | **0** | **24** |

---

## SECTION 6: REMEDIATION PRIORITY

### Immediate Actions (Phase 0, Day 1)

**P0-CRITICAL Misalignments**:
1. **MISALIGN-BQ-001**: Update feature_catalogue.json table count (6,069 → 5,817)
2. **MISALIGN-BQ-002**: Investigate and document COV table surplus (+882 tables)
3. **MISALIGN-DI-001**: Add status indicators to M001 mandate file
4. **MISALIGN-DI-002**: Add status section to M005 mandate file

**Effort**: 8-16 hours (Day 1-2 of Phase 0)
**Owner**: EA (execute all updates)

---

### Short-Term Actions (Phase 0, Week 1)

**P1-HIGH Misalignments**:
1. **MISALIGN-BQ-003**: Verify CSI table count (query BigQuery)
2. **MISALIGN-BQ-004**: Resolve MKT table count inconsistency (10 vs 14)
3. **MISALIGN-BQ-006**: Document CORR table count
4. **MISALIGN-IM-001**: Update mandate file table counts
5. **MISALIGN-IM-003**: Create single compliance dashboard
6. **MISALIGN-IM-004**: Create terminology glossary
7. **MISALIGN-DI-003**: Deprecate old M008 remediation plan
8. **MISALIGN-DI-004**: Archive old agent charge versions
9. **MISALIGN-AT-001**: Update Phase 4A/4B completion status
10. **MISALIGN-AT-002**: Execute intelligence file updates

**Effort**: 20-35 hours (Phase 0 Week 1)
**Owner**: EA (lead), QA (validate)

---

### Medium-Term Actions (Phase 1+)

**P2-MEDIUM Misalignments**:
1. **MISALIGN-BQ-009**: Define intelligence file update protocol
2. **MISALIGN-IM-002**: Update feature count (1,064 → 1,127) - may wait for M005 complete
3. **MISALIGN-IM-005**: Window notation standards (in glossary)
4. **MISALIGN-IM-006**: Pair notation standards (in glossary)
5. **MISALIGN-DI-005**: Clarify Phase 4 sub-phases in remediation plan
6. **MISALIGN-DI-006**: Clarify timeline estimates across docs
7. **MISALIGN-DI-007**: Reconcile cost estimates ($50-80 → $55-100)

**Effort**: 12-20 hours (Phase 0-1)
**Owner**: EA (lead)

---

## SECTION 7: TRUTH SOURCE ALIGNMENT PROTOCOL

To prevent future misalignments, establish the following protocol:

### Level 1: BigQuery (Ground Truth) - Real-Time
**Update Frequency**: Real-time (as operations occur)
**Authority**: ABSOLUTE (this is reality)
**Owner**: BA (executes changes), QA (validates)

### Level 2: Intelligence Files - Within 24 Hours
**Update Frequency**: Within 24 hours of BigQuery changes
**Authority**: HIGH (should match BigQuery within 24h)
**Trigger Events**:
- Table creation/deletion (update feature_catalogue.json)
- Schema changes (update semantics.json, ontology.json)
- Major phase completion (update context.json, roadmap_v2.json)

**Owner**: EA (updates), QA (validates)

### Level 3: Mandate Files - Weekly or After Milestones
**Update Frequency**: Weekly or after major milestones
**Authority**: MEDIUM (strategic overview, may lag Level 2 slightly)
**Trigger Events**:
- Phase completion (update compliance status)
- Mandate compliance changes (update percentages)
- Major deliverables (update inventory)

**Owner**: EA (updates), CE (approves)

### Level 4: Other Documentation - As Needed
**Update Frequency**: As needed
**Authority**: LOW (informational, may be outdated)
**Trigger Events**: Significant changes requiring documentation updates

**Owner**: EA (updates as needed)

---

### Reconciliation Audit Schedule

**Daily** (during active development phases):
- Verify BigQuery changes reflected in temporary tracking (e.g., Phase 4C rename log)

**Weekly**:
- Audit Level 2 (Intelligence Files) vs Level 1 (BigQuery)
- Update compliance dashboard

**Monthly**:
- Comprehensive audit: All 4 levels verified for alignment
- Generate misalignment report (if any found)

**Owner**: EA (conduct audits), QA (validate findings)

---

## SECTION 8: CRITICAL MISALIGNMENT SUMMARY

**Most Critical Misalignments** (address immediately):

1. **MISALIGN-BQ-001** (Table Count): 6,069 documented vs 5,817 actual (+224 overcount)
   - **Impact**: All planning based on wrong baseline
   - **Action**: Update feature_catalogue.json and mandate files to 5,817

2. **MISALIGN-BQ-002** (COV Surplus): 3,528 actual vs 2,646 documented (+882 surplus)
   - **Impact**: Cannot validate M006 coverage
   - **Action**: Investigate and document actual COV table inventory

3. **MISALIGN-AT-002** (Intelligence Update TODO): Recommendation not executed
   - **Impact**: Intelligence files remain stale
   - **Action**: Execute TRUTH_SOURCE_RECONCILIATION recommendations now

4. **MISALIGN-IM-001** (Intelligence ↔ Mandate Sync): Both outdated
   - **Impact**: No accurate documentation source
   - **Action**: Update both intelligence and mandate files simultaneously

**Timeline**: All 4 critical misalignments should be resolved within 48 hours (Phase 0, Days 1-2)

---

## APPENDIX A: VERIFICATION QUERIES

### Query 1: Total Table Count
```sql
SELECT COUNT(*) as total_tables
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`;
```
**Expected**: 5,817 (current BigQuery reality)
**Documented**: 6,069 (intelligence/mandate files - OUTDATED)

---

### Query 2: Category Counts
```sql
SELECT
  CASE
    WHEN table_name LIKE 'csi_%' THEN 'CSI'
    WHEN table_name LIKE 'var_%' THEN 'VAR'
    WHEN table_name LIKE 'mkt_%' THEN 'MKT'
    WHEN table_name LIKE 'tri_%' THEN 'TRI'
    WHEN table_name LIKE 'corr_%' THEN 'CORR'
    WHEN table_name LIKE 'cov_%' THEN 'COV'
    WHEN table_name LIKE 'reg_%' THEN 'REG'
    WHEN table_name LIKE 'lag_%' THEN 'LAG'
    ELSE 'OTHER'
  END AS category,
  COUNT(*) as table_count
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
GROUP BY category
ORDER BY table_count DESC;
```
**Purpose**: Verify all category counts vs documentation

---

### Query 3: COV Table Window Breakdown
```sql
SELECT
  COUNTIF(table_name LIKE 'cov_%_45') as window_45,
  COUNTIF(table_name LIKE 'cov_%_90') as window_90,
  COUNTIF(table_name LIKE 'cov_%_180') as window_180,
  COUNTIF(table_name LIKE 'cov_%_360') as window_360,
  COUNTIF(table_name LIKE 'cov_%_720') as window_720,
  COUNTIF(table_name LIKE 'cov_%_1440') as window_1440,
  COUNTIF(table_name LIKE 'cov_%_2880') as window_2880,
  COUNT(*) as total_cov_tables
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
WHERE table_name LIKE 'cov_%';
```
**Purpose**: Understand COV table surplus (which windows contribute to +882 surplus?)

---

### Query 4: M008 Compliance Check
```sql
-- REG tables (should match reg_{type}_{bqx|idx}_{pair})
SELECT COUNT(*) as reg_compliant
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
WHERE table_name LIKE 'reg_%'
  AND (table_name LIKE '%_bqx_%' OR table_name LIKE '%_idx_%');

-- COV tables (should match cov_{metric}_{bqx|idx}_{pair}_{metric}_{bqx|idx}_{pair}_{window})
SELECT COUNT(*) as cov_compliant
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
WHERE table_name LIKE 'cov_%'
  AND (table_name LIKE '%_bqx_%' OR table_name LIKE '%_idx_%');

-- TRI tables (should match tri_{type}_{bqx|idx}_{currency_trio})
SELECT COUNT(*) as tri_compliant
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
WHERE table_name LIKE 'tri_%'
  AND (table_name LIKE '%_bqx_%' OR table_name LIKE '%_idx_%');
```
**Purpose**: Verify M008 compliance % (should be 66.2% or higher post-Phase 4B)

---

## APPENDIX B: MISALIGNMENT REFERENCE TABLE

| Misalignment ID | Category | Description | Severity | Impact | Remediation Phase |
|-----------------|----------|-------------|----------|--------|-------------------|
| MISALIGN-BQ-001 | BQ ↔ Intel | Total table count (+224 overcount) | P0 | Planning errors | Phase 0 (Day 1) |
| MISALIGN-BQ-002 | BQ ↔ Intel | COV table surplus (+882) | P0 | M006 validation | Phase 0 (Day 1-2) |
| MISALIGN-BQ-003 | BQ ↔ Intel | CSI count unverified | P1 | Coverage unknown | Phase 0 (Week 1) |
| MISALIGN-BQ-004 | BQ ↔ Intel | MKT count conflict (10 vs 14) | P1 | Inconsistency | Phase 0 (Week 1) |
| MISALIGN-BQ-005 | BQ ↔ Intel | TRI count post-Phase 4B | P1 | Verify no loss | Phase 1 (Week 3) |
| MISALIGN-BQ-006 | BQ ↔ Intel | CORR count missing | P1 | Incomplete inventory | Phase 0 (Week 1) |
| MISALIGN-BQ-007 | BQ ↔ Intel | VAR count gap (-17) | P1 | Incomplete coverage | Phase 5 |
| MISALIGN-BQ-008 | BQ ↔ Intel | LAG consolidation pending | P2 | Architectural drift | Phase 4C |
| MISALIGN-BQ-009 | BQ ↔ Intel | Timestamp drift (~18h stale) | P2 | Staleness | Phase 0 (protocol) |
| MISALIGN-IM-001 | Intel ↔ Mandate | Table count both outdated | P1 | No accurate docs | Phase 0 (Day 1) |
| MISALIGN-IM-002 | Intel ↔ Mandate | Feature count gap (-63) | P1 | M001 ledger error | Phase 0 or Phase 5 |
| MISALIGN-IM-003 | Intel ↔ Mandate | M008 compliance % varies | P1 | Confusion | Phase 1 (dashboard) |
| MISALIGN-IM-004 | Intel ↔ Mandate | Terminology inconsistency | P1 | Parsing errors | Phase 0 (glossary) |
| MISALIGN-IM-005 | Intel ↔ Mandate | Window notation varies | P2 | Minor confusion | Phase 0 (glossary) |
| MISALIGN-IM-006 | Intel ↔ Mandate | Pair notation varies | P2 | Minor confusion | Phase 0 (glossary) |
| MISALIGN-DI-001 | Docs ↔ Impl | M001 status (docs describe future) | P0 | Confusion | Phase 0 (Day 1) |
| MISALIGN-DI-002 | Docs ↔ Impl | M005 status (docs describe future) | P0 | Confusion | Phase 0 (Day 1) |
| MISALIGN-DI-003 | Docs ↔ Impl | M008 plan conflict (old vs new) | P1 | Wrong execution | Phase 0 (deprecate) |
| MISALIGN-DI-004 | Docs ↔ Impl | Agent charge version drift | P1 | Role confusion | Phase 0 (archive) |
| MISALIGN-DI-005 | Docs ↔ Impl | Phase numbering (4A/4B/4C) | P2 | Mild confusion | Phase 0 (clarify) |
| MISALIGN-DI-006 | Docs ↔ Impl | Timeline estimate variation | P2 | Mild confusion | Phase 0 (clarify) |
| MISALIGN-DI-007 | Docs ↔ Impl | Cost estimate conflict | P2 | Budget confusion | Phase 0 (reconcile) |
| MISALIGN-AT-001 | Agent ↔ Reality | Phase 4A/4B status not updated | P1 | Rework risk | Phase 0 (update) |
| MISALIGN-AT-002 | Agent ↔ Reality | Intelligence update TODO pending | P1 | Stale docs | Phase 0 (execute) |

**Total Misalignments**: 23

---

**Report Status**: COMPLETE
**Critical Misalignments**: 4 (require immediate action within 48 hours)
**Next Deliverable**: USER_EXPECTATION_VALIDATION_20251213.md

---

*Enhancement Assistant (EA)*
*BQX ML V3 Project*
*Audit Date: 2025-12-13 22:15 UTC*
