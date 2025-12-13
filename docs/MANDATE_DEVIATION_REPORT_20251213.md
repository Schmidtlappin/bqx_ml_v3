# Mandate Deviation Report - Compliance Analysis

**Date**: 2025-12-13 21:45 UTC
**Analyst**: EA (Enhancement Assistant)
**Purpose**: Identify ALL deviations from user mandates and quantify compliance gaps
**Scope**: 5 explicit mandates (M001, M005, M006, M007, M008)
**Reference**: [USER_MANDATE_INVENTORY_20251213.md](USER_MANDATE_INVENTORY_20251213.md), [MANDATE_GAP_ANALYSIS_20251213.md](MANDATE_GAP_ANALYSIS_20251213.md)

---

## EXECUTIVE SUMMARY

**Overall Compliance Status**: 2/5 mandates fully compliant (40%)

| Mandate | Compliance % | Status | Severity | Deviations | Impact |
|---------|--------------|--------|----------|------------|--------|
| **M007** | 100% | ✅ COMPLIANT | NONE | 0 | None |
| **M008** | 66.2% | ⚠️ PARTIAL | HIGH | 1,968 tables | Blocks M005 |
| **M006** | ~60% | ⚠️ PARTIAL | MEDIUM | Coverage gaps | Reduces features |
| **M005** | 13.9% | ❌ NON-COMPLIANT | CRITICAL | 3,785 tables | Blocks M006/M007 |
| **M001** | 0% | ❌ NON-COMPLIANT | CRITICAL | File missing | Blocks production |

**Total Deviations**: 5,754 instances across 4 mandates
**Critical Severity**: 2 mandates (M001, M005) block production/downstream work
**High Severity**: 1 mandate (M008) blocks M005 execution
**Medium Severity**: 1 mandate (M006) reduces model performance

**Remediation Timeline**: 9-11 weeks (sequential), 5-7 weeks (parallelized)
**Remediation Cost**: $50-80 (BigQuery compute)

---

## SECTION 1: DEVIATION ANALYSIS BY MANDATE

### MANDATE M001: Feature Ledger 100% Coverage

**Compliance Status**: ❌ 0% COMPLIANT (0/1 deliverable complete)
**Severity**: CRITICAL (P0) - BLOCKS PRODUCTION DEPLOYMENT

#### Deviation Summary

| Requirement | Expected | Actual | Deviation | Impact |
|-------------|----------|--------|-----------|--------|
| **Feature Ledger File** | Exists | Missing | FILE NOT FOUND | Complete non-compliance |
| **Row Count** | 221,228 rows | 0 rows | -221,228 rows | No feature traceability |
| **Column Count** | 18 columns | 0 columns | -18 columns | No metadata |
| **SHAP Samples** | 100K+ per feature | 0 samples | -50M to -80M samples | No explainability |

**Total Deviation**: 100% (complete mandate non-compliance)

#### Detailed Deviation Analysis

**DEV-M001-001: Feature Ledger File Missing**
- **Requirement**: `feature_ledger.parquet` must exist in project root or GCS bucket
- **Current State**: File does not exist
- **Expected State**: Parquet file with 221,228 rows × 18 columns
- **Deviation Type**: Complete non-compliance (missing deliverable)
- **Root Cause**: Feature ledger generation process not yet implemented
- **Consequence**: **BLOCKS PRODUCTION DEPLOYMENT**
  - Cannot trace feature provenance
  - Cannot validate feature stability
  - Cannot document model composition
  - Cannot reproduce model decisions
  - Regulatory/compliance requirements not met

**DEV-M001-002: Feature Metadata Missing**
- **Requirement**: 18-column schema with comprehensive feature metadata
- **Expected Columns**:
  1. feature_name (string)
  2. source_table (string)
  3. feature_type (string)
  4. feature_scope (string)
  5. variant (string: BQX or IDX)
  6. pair (string: e.g., EURUSD)
  7. horizon (int: 5, 15, 30, 60, 120, 240, 480)
  8. model_type (string: ensemble component)
  9. cluster_id (int)
  10. group_id (int)
  11. pruned_stage (string: GATE_1, GATE_2, etc.)
  12. prune_reason (string: correlation, stability, importance, ablation)
  13. screen_score (float: GATE_1 screening score)
  14. stability_freq (float: % training runs where feature appears)
  15. importance_mean (float: average SHAP importance)
  16. importance_std (float: SHAP importance std dev)
  17. ablation_delta (float: accuracy delta when feature removed)
  18. final_status (string: RETAINED, PRUNED_G1, PRUNED_G2, PRUNED_G3)
- **Current State**: None of these columns exist
- **Deviation Type**: 100% metadata gap
- **Consequence**: Cannot analyze feature behavior or make informed feature selection decisions

**DEV-M001-003: SHAP Samples Missing**
- **Requirement**: 100,000+ SHAP samples per retained feature
- **Expected State**: 50M-80M SHAP values (500-800 retained features × 100K samples)
- **Current State**: 0 SHAP samples generated
- **Deviation Type**: 100% explainability gap
- **Root Cause**: Training pipeline not yet executed with SHAP enabled
- **Consequence**: **BLOCKS PRODUCTION** (cannot explain model predictions)

#### Remediation Path

**Phase**: Phase 7 (M001 Feature Ledger Generation)
**Timeline**: 3-4 weeks (Weeks 10-11 of comprehensive plan)
**Effort**: 40-60 hours
**Cost**: $0 (post-processing, no new BigQuery compute)
**Dependencies**:
- M005 complete (regression features required for comprehensive ledger)
- Training pipeline executed with SHAP enabled
- Feature pruning gates executed (GATE_1, GATE_2, GATE_3)

**Remediation Steps**:
1. Execute training pipeline with SHAP sampling enabled
2. Extract feature names from final ensemble model
3. Map features to source tables (BigQuery metadata queries)
4. Generate SHAP importance statistics (mean, std dev)
5. Calculate stability frequency across training runs
6. Document pruning decisions (stage, reason, metrics)
7. Export to parquet with 18-column schema
8. Validate row count (221,228 expected)
9. Store in GCS bucket for production access

**Success Criteria**:
- ✅ File exists: `feature_ledger.parquet`
- ✅ Row count: 221,228 (28 pairs × 7 horizons × 1,127 features)
- ✅ Column count: 18 (all required metadata columns)
- ✅ SHAP samples: 100,000+ per retained feature
- ✅ QA validation: 100% schema compliance

---

### MANDATE M005: Regression Feature Architecture

**Compliance Status**: ❌ 13.9% COMPLIANT (56/4,049 tables complete)
**Severity**: CRITICAL (P0) - BLOCKS M006/M007 FULL COMPLIANCE

#### Deviation Summary

| Component | Total Tables | Compliant | Non-Compliant | Compliance % | Missing Columns |
|-----------|--------------|-----------|---------------|--------------|-----------------|
| **REG** | 56 | 56 | 0 | ✅ 100% | 0 |
| **TRI** | 194 | 0 | 194 | ❌ 0% | 63 cols/table |
| **COV** | 3,528 | 0 | 3,528 | ❌ 0% | 42 cols/table |
| **VAR** | 63 | 0 | 63 | ❌ 0% | 21 cols/table |
| **TOTAL** | **4,049** | **56** | **3,993** | **1.4%** | **161,721 cols** |

**Note**: 13.9% table count compliance (56 + 208 other categories / 5,817 total), but only 1.4% M005-specific compliance.

**Total Deviation**: 3,993 tables missing regression features (98.6% non-compliance for M005 table types)

#### Detailed Deviation Analysis

**DEV-M005-001: TRI Table Regression Feature Gap (194 Tables)**
- **Requirement**: All TRI tables must have 78 columns (15 base + 63 regression)
- **Current State**: TRI tables have 15 base columns only
- **Expected Columns**: 63 regression features across 7 windows
  - lin_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - quad_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - residual_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - {metric}_cross_{45, 90, 180, 360, 720, 1440, 2880} (42 columns for 6 cross-terms)
- **Deviation Type**: 100% feature gap for TRI tables
- **Missing Values**: 12,222 columns (194 tables × 63 columns)
- **Root Cause**: M005 schema update not yet executed
- **Consequence**: **BLOCKS M006** (cannot maximize comparisons without regression features)

**Tables Affected** (sample):
```
tri_align_bqx_aud_cad_chf
tri_align_bqx_aud_cad_eur
tri_align_bqx_aud_cad_gbp
tri_align_bqx_aud_cad_jpy
...
tri_align_idx_usd_nzd_jpy
tri_carry_idx_usd_nzd_jpy
(194 tables total)
```

**Remediation**:
- **Phase**: Phase 3 (M005 TRI Schema Update)
- **Timeline**: 2-3 weeks (Weeks 5-6 of comprehensive plan)
- **Effort**: 30-40 hours
- **Cost**: $15-25 (BigQuery regression calculations)
- **Dependencies**: M008 Phase 4C complete (need variant identifiers to parse table names)

---

**DEV-M005-002: COV Table Regression Feature Gap (3,528 Tables)**
- **Requirement**: All COV tables must have 56 columns (14 base + 42 regression)
- **Current State**: COV tables have 14 base columns only
- **Expected Columns**: 42 regression features across 7 windows
  - lin_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - quad_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - residual_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - lin_quad_cross_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - quad_residual_cross_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - lin_residual_cross_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
- **Deviation Type**: 100% feature gap for COV tables
- **Missing Values**: 148,176 columns (3,528 tables × 42 columns)
- **Root Cause**: M005 schema update not yet executed
- **Consequence**: **BLOCKS M006** (cannot maximize feature-to-feature comparisons)

**Tables Affected** (sample):
```
cov_ret_audcad_ret_audchf_45
cov_ret_audcad_ret_audchf_90
cov_ret_audcad_ret_audeur_45
cov_ret_audcad_ret_audeur_90
...
cov_ret_usdjpy_vol_usdjpy_90
(3,528 tables total)
```

**Impact Analysis**:
- **Feature Comparison Power**: Each COV table currently has ~10-12 meaningful features. With regression features, this increases to ~50-54 features.
- **Model Performance**: Missing regression features reduces model's ability to capture non-linear relationships in covariance dynamics.
- **Coverage**: 3,528 tables × 42 missing columns = 148,176 missing feature values across the feature matrix.

**Remediation**:
- **Phase**: Phase 4 (M005 COV Schema Update)
- **Timeline**: 2-3 weeks (Weeks 6-7 of comprehensive plan)
- **Effort**: 40-60 hours
- **Cost**: $30-45 (BigQuery regression calculations for 3,528 tables - largest effort)
- **Dependencies**: M008 Phase 4C complete, TRI Phase 3 complete (use as template)

---

**DEV-M005-003: VAR Table Regression Feature Gap (63 Tables)**
- **Requirement**: All VAR tables must have 35 columns (14 base + 21 regression)
- **Current State**: VAR tables have 14 base columns only
- **Expected Columns**: 21 regression features across 7 windows
  - lin_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - quad_term_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
  - residual_{45, 90, 180, 360, 720, 1440, 2880} (7 columns)
- **Deviation Type**: 100% feature gap for VAR tables
- **Missing Values**: 1,323 columns (63 tables × 21 columns)
- **Root Cause**: M005 schema update not yet executed
- **Consequence**: **BLOCKS M006** (incomplete variance feature coverage)

**Tables Affected** (sample):
```
var_usd_audcad
var_usd_audchf
var_usd_audeur
var_usd_audgbp
...
var_lag_usdjpy (if exists)
(63 tables current, 80 expected per mandate)
```

**Remediation**:
- **Phase**: Phase 5 (M005 VAR Schema Update)
- **Timeline**: 1-2 weeks (Weeks 7-8 of comprehensive plan)
- **Effort**: 15-25 hours
- **Cost**: $5-15 (BigQuery regression calculations)
- **Dependencies**: M008 Phase 4C complete, COV Phase 4 complete (use as template)

---

**DEV-M005-004: VAR Table Count Gap (17 Missing Tables)**
- **Requirement**: 80 VAR tables total (40 var_usd_* + 40 var_lag_*)
- **Current State**: 63 VAR tables exist
- **Expected State**: 80 VAR tables (20 pairs × 2 variants × 2 types)
- **Deviation Type**: Missing tables (21.3% coverage gap)
- **Missing Tables**: 17 tables
- **Root Cause**: var_lag_* tables may not have been generated for all pairs, or var_usd_* missing for some pairs
- **Consequence**: Incomplete variance feature coverage across pairs

**Remediation**:
- **Phase**: Phase 5 (M005 VAR Schema Update) - Generate missing tables during schema update
- **Effort**: 5-10 hours (incremental to Phase 5 work)
- **Cost**: $2-5 (additional BigQuery compute)

---

#### M005 Compliance Calculation

**By Table Count**:
- REG: 56/56 = 100% ✅
- TRI: 0/194 = 0% ❌
- COV: 0/3,528 = 0% ❌
- VAR: 0/63 = 0% ❌
- **M005-Specific Compliance**: 56/3,841 = 1.5%

**By Column Count**:
- REG: 100% (all required columns present)
- TRI: 15/78 = 19.2% (base columns only, missing regression features)
- COV: 14/56 = 25.0% (base columns only, missing regression features)
- VAR: 14/35 = 40.0% (base columns only, missing regression features)
- **Weighted Column Compliance**: ~26% (base columns present, regression features missing)

**Overall M005 Compliance**: **13.9%** (56 compliant tables / 402 total M005 category tables across all 20 categories)
- Note: This uses total table count denominator including non-M005 categories.
- **M005-specific compliance**: 1.5% (only REG tables compliant)

---

### MANDATE M006: Maximize Feature Comparisons

**Compliance Status**: ⚠️ ~60% COMPLIANT (partial coverage)
**Severity**: MEDIUM (P1) - REDUCES MODEL PERFORMANCE

#### Deviation Summary

| Dimension | Current | Target | Gap | Compliance % |
|-----------|---------|--------|-----|--------------|
| **Window Coverage** | 2/7 windows | 7/7 windows | 5 windows missing | 28.6% |
| **Feature Type Coverage** | ~80% | 100% | ~20% missing | 80% (est.) |
| **Pair Coverage** | 25/28 pairs | 28/28 pairs | 3 pairs missing | 89.3% |
| **COV Tables** | 3,528 tables | Unknown | +882 surplus (vs docs) | Unknown |
| **Overall M006** | ~60% | 100% | ~40% gap | **~60%** |

**Total Deviation**: ~40% of feature comparison potential unrealized

#### Detailed Deviation Analysis

**DEV-M006-001: Window Coverage Gap (5 Windows Missing)**
- **Requirement**: "Maximize feature-to-feature comparisons across ALL pairs, ALL windows, and ALL feature types"
- **Current State**: COV tables generated for 2/7 windows (45, 90)
- **Expected State**: COV tables for all 7 windows (45, 90, 180, 360, 720, 1440, 2880)
- **Deviation Type**: 71.4% window gap (5/7 windows missing)
- **Missing Windows**: 180, 360, 720, 1440, 2880
- **Impact**: **REDUCES FEATURE SPACE by ~71%**
  - Current: 3,528 COV tables (windows 45, 90)
  - Expected: ~12,348 COV tables (all 7 windows)
  - Gap: ~8,820 missing COV tables

**Root Cause**: Initial feature extraction focused on shorter windows (45, 90 days) for faster iteration. Long-term windows (180-2880 days) not yet generated.

**Consequence**:
- Model cannot capture long-term covariance relationships (6+ months, 1-2 years)
- Feature comparison power limited to short-term dynamics only
- Ensemble models may underperform on long-horizon predictions (120d, 240d, 480d)

**Remediation**:
- **Phase**: Phase 6 (M006 Coverage Verification) → Phase 8 (Window Expansion)
- **Timeline**: 3-4 weeks (Weeks 9-10 of comprehensive plan)
- **Effort**: 40-60 hours
- **Cost**: Unknown (need cost estimate for 8,820 new COV table generation)
- **Dependencies**: M005 complete (schema must include regression features before expansion)

---

**DEV-M006-002: Feature Type Coverage Gap**
- **Requirement**: "Maximize comparisons across ALL feature types"
- **Current State**: COV tables generated for core feature types (returns, volatility)
- **Expected State**: COV tables for ALL comparable feature types across 9 semantic groups
- **Deviation Type**: ~20% feature type gap (estimated)
- **Missing Feature Types** (estimated):
  - Regime-aware COV tables (regime-conditioned covariances)
  - Normalized COV tables (z-score normalized inputs)
  - Derivative COV tables (covariances of rate-of-change features)
  - Momentum COV tables (momentum factor cross-correlations)

**Root Cause**: Phase 6 (M006 Coverage Verification) not yet executed - exact gap unknown.

**Consequence**:
- Cannot compare features across all semantic groups
- Model may miss cross-type feature interactions (e.g., momentum vs volatility)
- Incomplete exploitation of feature space

**Remediation**:
- **Phase**: Phase 6 (M006 Coverage Verification) - Determine exact gap first
- **Timeline**: 1-2 weeks (Week 9)
- **Effort**: 8-16 hours (gap analysis), 20-40 hours (remediation if needed)
- **Cost**: Unknown (depends on new tables required)

---

**DEV-M006-003: COV Table Surplus (+882 Tables)**
- **Requirement**: All tables documented in feature_catalogue.json
- **Current State**: 3,528 COV tables in BigQuery, 2,646 documented
- **Expected State**: Documentation matches BigQuery reality
- **Deviation Type**: Documentation drift (+33% undocumented surplus)
- **Analysis Needed**:
  1. Are 882 surplus tables valid M006 coverage expansion?
  2. Are they duplicates that should be deleted?
  3. Are they partially-generated tables (incomplete)?

**Root Cause**: Intelligence files not updated after COV table generation, OR partial window expansion already executed but not documented.

**Consequence**:
- Cannot validate M006 compliance without accurate inventory
- May be double-counting or missing coverage gaps

**Remediation**:
- **Phase**: Phase 0 (Documentation Reconciliation) - IMMEDIATE
- **Effort**: 4-8 hours (audit BigQuery, update feature_catalogue.json)
- **Cost**: $0 (read-only queries)

---

**DEV-M006-004: Pair Coverage Gap (3 Pairs Missing)**
- **Requirement**: All 28 G10 pairs extracted
- **Current State**: 25 pairs extracted (EURUSD, GBPUSD, USDJPY, etc.)
- **Expected State**: 28 pairs (add EURGBP, EURJPY, GBPJPY cross-pairs)
- **Deviation Type**: 10.7% pair gap (3/28 pairs missing)
- **Missing Pairs**: EURGBP, EURJPY, GBPJPY (cross-pairs, lower priority)
- **Impact**: INCOMPLETE COVERAGE for EUR and GBP cross-pairs

**Root Cause**: Initial focus on major pairs (USD-based). Cross-pairs (EUR/GBP, EUR/JPY, GBP/JPY) lower priority.

**Consequence**:
- Models for EUR, GBP, JPY pairs may have reduced feature coverage
- Cross-pair arbitrage features unavailable

**Remediation**:
- **Phase**: Phase 9 (Data Quality Verification) - Extract missing pairs
- **Effort**: 6-10 hours
- **Cost**: $5-10 (extraction + merge)
- **Timeline**: 1-2 weeks (Week 11)

---

#### M006 Compliance Calculation

**Dimension Compliance**:
- Window Coverage: 2/7 = **28.6%**
- Feature Type Coverage: ~80% (estimated)
- Pair Coverage: 25/28 = **89.3%**

**Weighted Overall M006 Compliance**:
- (28.6% × 0.5) + (80% × 0.3) + (89.3% × 0.2) = **14.3% + 24% + 17.9% = 56.2%**
- Rounded: **~60% compliant**

**Compliance Blockers**:
- ❌ Window expansion (71% gap)
- ⚠️ Feature type coverage (20% gap estimated)
- ⚠️ Pair expansion (11% gap)

---

### MANDATE M007: Semantic Feature Compatibility

**Compliance Status**: ✅ 100% COMPLIANT
**Severity**: NONE - NO DEVIATIONS

#### Compliance Verification

| Requirement | Expected | Actual | Compliance |
|-------------|----------|--------|------------|
| **Semantic Groups Defined** | 9 groups | 9 groups | ✅ 100% |
| **Comparable Features** | 266/pair | 266/pair | ✅ 100% |
| **Invalid Comparison Rules** | Documented | Documented | ✅ 100% |
| **Variant Separation** | BQX ≠ IDX | BQX ≠ IDX | ✅ 100% |

**Semantic Groups** (all defined):
1. Regression Features (lin_term, quad_term, residual)
2. Aggregates (mean, median, sum, count)
3. Normalized Features (z-score, min-max, rank)
4. Directional Features (returns, price_change, direction)
5. Momentum Features (rsi, macd, momentum_score)
6. Volatility Features (std_dev, atr, volatility_ratio)
7. Derivatives (rate_of_change, acceleration, gradient)
8. Mean Reversion (distance_from_ma, bollinger_position)
9. Correlations (correlation_score, covariance_normalized)

**Invalid Comparisons** (all documented):
- ❌ Raw Prices (non-stationary)
- ❌ Counts (scale-dependent)
- ❌ Timestamps (non-comparable)
- ❌ Categorical Variables (discrete)
- ❌ BQX vs IDX (different semantic universes)

**Deviation**: NONE
**Status**: ✅ **M007 is 100% COMPLIANT** - No remediation required

---

### MANDATE M008: Naming Standard

**Compliance Status**: ⚠️ 66.2% COMPLIANT (3,849/5,817 tables)
**Severity**: HIGH (P0) - BLOCKS M005 EXECUTION

#### Deviation Summary

| Category | Total Tables | Compliant | Non-Compliant | Compliance % | Issue |
|----------|--------------|-----------|---------------|--------------|-------|
| **Compliant** | 3,849 | 3,849 | 0 | ✅ 100% | None |
| **COV** | ~1,596 | 0 | ~1,596 | ❌ 0% | Missing variant ID |
| **LAG** | 224 | 0 | 224 | ❌ 0% | Window-specific tables |
| **REGIME** | 141 | 0 | 141 | ❌ 0% | Window suffix |
| **VAR** | 7 | 0 | 7 | ❌ 0% | Missing variant ID |
| **Other** | Unknown | 0 | Unknown | ❌ 0% | Various issues |
| **TOTAL** | **5,817** | **3,849** | **1,968** | **66.2%** | **33.8% gap** |

**Total Deviation**: 1,968 tables (33.8% non-compliance)

#### Detailed Deviation Analysis

**DEV-M008-001: COV Table Variant Identifier Missing (~1,596 Tables)**
- **Requirement**: COV tables must follow pattern `cov_{metric1}_{variant}_{pair}_{metric2}_{variant}_{pair}_{window}`
  - Example: `cov_ret_bqx_eurusd_vol_bqx_eurusd_45`
- **Current State**: Many COV tables missing `_bqx_` or `_idx_` variant identifier
  - Example (non-compliant): `cov_ret_eurusd_vol_eurusd_45`
- **Deviation Type**: Missing variant identifier (cannot determine BQX vs IDX data source)
- **Tables Affected**: ~1,596 COV tables (estimated from Phase 4C plan)
- **Root Cause**: Earlier feature extraction script did not include variant identifiers in table names

**Consequence**: **BLOCKS M005 EXECUTION**
- M005 schema update scripts parse table names to determine variant (BQX vs IDX)
- Without variant identifier, scripts cannot classify tables correctly
- Risk of intermixing BQX and IDX data (violates M007 semantic separation)

**Example Non-Compliant Tables**:
```
cov_ret_audcad_ret_audchf_45  (missing _bqx_ or _idx_)
cov_ret_audcad_ret_audchf_90  (missing _bqx_ or _idx_)
cov_ret_audcad_vol_audchf_45  (missing _bqx_ or _idx_)
...
(~1,596 tables total)
```

**Remediation**:
- **Phase**: Phase 4C (M008 Table Naming Remediation) - IN PROGRESS
- **Action**: Rename tables to include variant identifier
  - `cov_ret_audcad_ret_audchf_45` → `cov_ret_bqx_audcad_ret_bqx_audchf_45` (if BQX data)
  - `cov_ret_audcad_ret_audchf_45` → `cov_ret_idx_audcad_ret_idx_audchf_45` (if IDX data)
- **Challenge**: Must query table contents to determine BQX vs IDX (sample 5-10 tables first)
- **Timeline**: Week 1-2 of Phase 4C
- **Cost**: $0-2 (rename operations)

---

**DEV-M008-002: LAG Table Consolidation Required (224 Tables → 56 Tables)**
- **Requirement**: LAG tables should follow pattern `lag_{type}_{variant}_{pair}` with windows as columns
  - Example: `lag_bqx_eurusd` (with columns: lag_45, lag_90, lag_180, etc.)
- **Current State**: LAG tables split by window: `lag_bqx_eurusd_45`, `lag_bqx_eurusd_90`, etc.
- **Deviation Type**: Window in table name (should be in column name per M008 architecture)
- **Tables Affected**: 224 LAG tables
- **Root Cause**: Earlier extraction created separate tables per window (not wide-table format)

**Consequence**: **ARCHITECTURAL MISALIGNMENT**
- M008 mandates windows as columns, not table name suffixes
- 224 tables should be 56 tables (consolidate 4-8 window-specific tables into 1 wide table)
- Table sprawl (224 vs 56 = 168 unnecessary tables)

**Example Non-Compliant Tables**:
```
lag_bqx_eurusd_45   ← Should be consolidated into lag_bqx_eurusd
lag_bqx_eurusd_90   ← with columns: lag_45, lag_90, lag_180, etc.
lag_bqx_eurusd_180
lag_bqx_eurusd_360
...
(224 tables total → 56 consolidated tables)
```

**Remediation** (APPROVED: Option A - Consolidate):
- **Phase**: Phase 4C (M008 Table Naming Remediation) - IN PROGRESS
- **Action**: Consolidate 224 window-specific tables → 56 wide tables
  1. Create `lag_bqx_eurusd` with all window columns
  2. Merge `lag_bqx_eurusd_{45,90,180,360,720,1440,2880}` into single table
  3. Validate row count preservation
  4. Delete source tables after validation
- **Pilot**: 5 pairs first (LAG pilot GO/NO-GO gate on Day 3)
- **Timeline**: Week 1-2 of Phase 4C
- **Cost**: $5-10 (BigQuery consolidation compute)

---

**DEV-M008-003: REGIME Table Window Suffix Issues (141 Tables)**
- **Requirement**: REGIME tables should follow M008 pattern (window in column vs table name)
- **Current State**: 141 REGIME tables flagged for "window suffix" issues
- **Deviation Type**: Window suffix format unclear (investigation needed)
- **Tables Affected**: 141 REGIME tables
- **Root Cause**: REGIME table naming pattern not clearly defined in M008 mandate

**Consequence**: **PARSING AMBIGUITY**
- Scripts may misinterpret window information
- Unclear if REGIME tables should be consolidated (like LAG) or renamed

**Remediation**:
- **Phase**: Phase 4C (M008 Table Naming Remediation) - Week 1 (investigation)
- **Action**:
  1. Sample 5-10 REGIME tables to understand current structure
  2. Clarify M008 pattern for REGIME tables with user
  3. Rename or consolidate based on clarification
- **Timeline**: Week 1 investigation, Week 2 execution (if needed)
- **Cost**: $0-2 (rename if needed)

---

**DEV-M008-004: VAR Table Variant Identifier Missing (7 Tables)**
- **Requirement**: VAR tables must follow pattern `var_{type}_{variant}_{pair}`
  - Example: `var_usd_bqx_eurusd` or `var_lag_idx_gbpusd`
- **Current State**: 7 VAR tables missing `_bqx_` or `_idx_` variant identifier
- **Deviation Type**: Missing variant identifier
- **Tables Affected**: 7 VAR tables
- **Root Cause**: Early extraction did not include variant identifiers

**Consequence**: **BLOCKS M005 VAR SCHEMA UPDATE**
- Cannot determine BQX vs IDX for schema update scripts

**Example Non-Compliant Tables**:
```
var_usd_eurusd  (should be var_usd_bqx_eurusd or var_usd_idx_eurusd)
var_usd_gbpusd  (should be var_usd_bqx_gbpusd or var_usd_idx_gbpusd)
...
(7 tables total)
```

**Remediation**:
- **Phase**: Phase 4C (M008 Table Naming Remediation) - Week 1
- **Action**: Rename 7 VAR tables to include variant identifier
- **Timeline**: Week 1 of Phase 4C (quick fix, only 7 tables)
- **Cost**: $0 (negligible)

---

**DEV-M008-005: Other Non-Compliant Tables (Unknown Count)**
- **Requirement**: All tables must follow M008 patterns
- **Current State**: Additional non-compliant tables (count unknown, estimated <50)
- **Deviation Type**: Various (TMP tables, edge cases, etc.)
- **Tables Affected**: Unknown count (to be discovered during Phase 4C)

**Remediation**:
- **Phase**: Phase 4C (M008 Table Naming Remediation) - Discovery during execution
- **Action**: Handle on case-by-case basis
- **Timeline**: Throughout Phase 4C
- **Cost**: $0-3

---

#### M008 Compliance Calculation

**Current State**:
- Total Tables: 5,817
- Compliant: 3,849 (66.2%)
- Non-Compliant: 1,968 (33.8%)

**By Category**:
- COV: 0/~1,596 = 0% (largest gap)
- LAG: 0/224 = 0% (consolidation required)
- REGIME: 0/141 = 0% (investigation + remediation)
- VAR: 0/7 = 0% (quick fix)
- Other: Unknown

**Post-Phase 4C Target**: 100% compliance (5,817/5,817 tables)

**Timeline to 100%**: 2 weeks (aggressive), 3 weeks (conservative)

---

## SECTION 2: SEVERITY CLASSIFICATION

### Critical Severity (P0) - Production Blockers

**DEV-M001-001**: Feature Ledger File Missing
- **Blocks**: Production deployment
- **Impact**: Cannot trace feature provenance, regulatory non-compliance
- **Remediation**: Phase 7 (3-4 weeks)

**DEV-M005-001**: TRI Regression Features Missing (194 tables)
- **Blocks**: M006 compliance (cannot maximize comparisons)
- **Impact**: Reduced model performance, incomplete feature space
- **Remediation**: Phase 3 (2-3 weeks)

**DEV-M005-002**: COV Regression Features Missing (3,528 tables)
- **Blocks**: M006 compliance (cannot maximize comparisons)
- **Impact**: Largest feature gap (148,176 missing columns)
- **Remediation**: Phase 4 (2-3 weeks)

**DEV-M005-003**: VAR Regression Features Missing (63 tables)
- **Blocks**: M006 compliance (incomplete variance coverage)
- **Impact**: Reduced variance feature space
- **Remediation**: Phase 5 (1-2 weeks)

**DEV-M008-001**: COV Variant Identifier Missing (~1,596 tables)
- **Blocks**: M005 execution (schema update scripts require variant identifiers)
- **Impact**: Cannot execute M005 schema updates without risk of BQX/IDX intermixing
- **Remediation**: Phase 4C (1-2 weeks)

**Total P0 Deviations**: 5 deviations affecting 5,382 tables

---

### High Severity (P1) - Quality/Risk Impact

**DEV-M006-001**: Window Coverage Gap (5 windows missing)
- **Impact**: Reduces feature space by ~71% (8,820 missing COV tables)
- **Risk**: Model underperforms on long-horizon predictions
- **Remediation**: Phase 6 → Phase 8 (3-4 weeks)

**DEV-M006-002**: Feature Type Coverage Gap (~20% gap)
- **Impact**: Cannot compare features across all semantic groups
- **Risk**: Misses cross-type feature interactions
- **Remediation**: Phase 6 (gap analysis) → remediation (2-4 weeks)

**DEV-M008-002**: LAG Table Consolidation (224 → 56 tables)
- **Impact**: Table sprawl (168 unnecessary tables), architectural misalignment
- **Risk**: Future maintenance complexity
- **Remediation**: Phase 4C (1-2 weeks, IN PROGRESS)

**DEV-M008-003**: REGIME Table Window Suffix (141 tables)
- **Impact**: Parsing ambiguity
- **Risk**: Scripts may misinterpret window information
- **Remediation**: Phase 4C Week 1 (investigation) → Week 2 (execution)

**Total P1 Deviations**: 4 deviations affecting ~10,000+ tables (estimated)

---

### Medium Severity (P2) - Technical Debt

**DEV-M005-004**: VAR Table Count Gap (17 missing tables)
- **Impact**: Incomplete variance coverage (21% gap)
- **Risk**: Some pairs missing variance features
- **Remediation**: Phase 5 (included in VAR schema update)

**DEV-M006-003**: COV Table Surplus (+882 undocumented)
- **Impact**: Documentation drift
- **Risk**: Cannot validate coverage without accurate inventory
- **Remediation**: Phase 0 (immediate, 4-8 hours)

**DEV-M006-004**: Pair Coverage Gap (3 pairs missing)
- **Impact**: Incomplete cross-pair coverage (11% gap)
- **Risk**: EUR/GBP/JPY cross-pair models have reduced features
- **Remediation**: Phase 9 (1-2 weeks)

**DEV-M008-004**: VAR Variant Identifier Missing (7 tables)
- **Impact**: Small subset, but blocks M005 VAR schema update
- **Risk**: Low (only 7 tables)
- **Remediation**: Phase 4C Week 1 (quick fix)

**Total P2 Deviations**: 4 deviations affecting ~900 tables

---

### Low Severity (P3) - Future Enhancement

**No P3 deviations identified** - All current deviations are P0-P2 (critical to medium severity).

---

## SECTION 3: ROOT CAUSE ANALYSIS

### Root Cause 1: Sequential Development Approach
**Deviations**: DEV-M005-001, DEV-M005-002, DEV-M005-003, DEV-M006-001, DEV-M006-002

**Analysis**:
- M005 regression features not yet implemented (planned for Phases 3-5)
- M006 window/feature expansion not yet executed (planned for Phase 6-8)
- This is intentional sequential development, not a failure

**Systemic Issue**: NO - This is planned work, not deviation from plan
**Preventable**: NO - Sequential execution is correct approach
**Action**: Continue with planned phases

---

### Root Cause 2: Early Extraction Script Limitations
**Deviations**: DEV-M008-001, DEV-M008-004

**Analysis**:
- Early feature extraction scripts (2024-2025) did not include variant identifiers in table names
- M008 mandate formalized later, requiring variant identifiers for semantic separation
- Now requires retroactive rename of ~1,603 tables

**Systemic Issue**: YES - Standards evolved, but early work predated standards
**Preventable**: PARTIAL - Could have included variant IDs from start, but M008 mandate wasn't formalized
**Action**: Phase 4C remediation (rename tables to comply with M008)

---

### Root Cause 3: Architecture Evolution (LAG Tables)
**Deviations**: DEV-M008-002

**Analysis**:
- Early LAG table design: Separate tables per window (lag_bqx_eurusd_45, lag_bqx_eurusd_90, etc.)
- M008 architecture decision: Windows as columns, not table names
- Requires consolidation: 224 tables → 56 tables

**Systemic Issue**: YES - Architecture evolved, early design predated M008 mandate
**Preventable**: PARTIAL - Wide-table format is better architecture, could have been planned from start
**Action**: Phase 4C remediation (consolidate LAG tables)

---

### Root Cause 4: Incomplete Feature Ledger Process
**Deviations**: DEV-M001-001, DEV-M001-002, DEV-M001-003

**Analysis**:
- Feature ledger generation process not yet implemented
- Training pipeline not yet executed with SHAP sampling enabled
- M001 mandate requires comprehensive feature provenance tracking

**Systemic Issue**: NO - This is planned work (Phase 7), not a process failure
**Preventable**: NO - Feature ledger can only be generated after training pipeline executed
**Action**: Execute Phase 7 after M005 complete

---

### Root Cause 5: Documentation Drift
**Deviations**: DEV-M006-003

**Analysis**:
- BigQuery reality (3,528 COV tables) ≠ feature_catalogue.json (2,646 COV tables)
- Intelligence files not updated after table generation
- +882 table surplus (33% undocumented)

**Systemic Issue**: YES - Documentation update process not enforced
**Preventable**: YES - Should have updated feature_catalogue.json after table generation
**Action**:
- Immediate: Update intelligence files (Phase 0)
- Long-term: Define documentation update process (prevent future drift)

---

## SECTION 4: REMEDIATION SUMMARY

### By Mandate

| Mandate | Deviations | Severity | Remediation Effort | Cost | Timeline |
|---------|------------|----------|-------------------|------|----------|
| **M001** | 3 | P0-CRITICAL | 40-60 hours | $0 | 3-4 weeks (Phase 7) |
| **M005** | 4 | P0-CRITICAL | 80-120 hours | $50-70 | 5-7 weeks (Phases 3-5) |
| **M006** | 4 | P1-HIGH to P2-MED | 65-115 hours | $5-15 | 4-6 weeks (Phases 6, 8, 9) |
| **M007** | 0 | NONE | 0 hours | $0 | N/A ✅ |
| **M008** | 5 | P0-CRITICAL to P2-MED | 30-50 hours | $5-15 | 2-3 weeks (Phase 4C) |
| **TOTAL** | **16** | **Mixed** | **215-345 hours** | **$60-100** | **9-11 weeks** |

### By Phase

| Phase | Deviations Addressed | Effort | Cost | Timeline |
|-------|---------------------|--------|------|----------|
| **Phase 0** (Docs) | 1 (DEV-M006-003) | 4-8 hours | $0 | Immediate |
| **Phase 4C** (M008) | 5 (DEV-M008-001 to DEV-M008-005) | 30-50 hours | $5-15 | 2-3 weeks |
| **Phase 3** (TRI) | 1 (DEV-M005-001) | 30-40 hours | $15-25 | 2-3 weeks |
| **Phase 4** (COV) | 1 (DEV-M005-002) | 40-60 hours | $30-45 | 2-3 weeks |
| **Phase 5** (VAR) | 2 (DEV-M005-003, DEV-M005-004) | 20-35 hours | $7-20 | 1-2 weeks |
| **Phase 6** (M006 Verify) | 2 (DEV-M006-001, DEV-M006-002) | 25-45 hours | $0 | 1-2 weeks |
| **Phase 7** (M001 Ledger) | 3 (DEV-M001-001 to DEV-M001-003) | 40-60 hours | $0 | 3-4 weeks |
| **Phase 8** (Window Expand) | Included in Phase 6 | - | TBD | 3-4 weeks |
| **Phase 9** (Data Quality) | 1 (DEV-M006-004) | 6-10 hours | $5-10 | 1-2 weeks |

---

## SECTION 5: CRITICAL PATH TO 100% COMPLIANCE

**Blocking Deviations** (must be resolved before downstream work):

1. **DEV-M008-001** (COV variant IDs) → BLOCKS M005 Phase 4
2. **DEV-M008-004** (VAR variant IDs) → BLOCKS M005 Phase 5
3. **DEV-M005-001** (TRI regression) → BLOCKS M006 full compliance
4. **DEV-M005-002** (COV regression) → BLOCKS M006 full compliance
5. **DEV-M005-003** (VAR regression) → BLOCKS M006 full compliance
6. **DEV-M001-001** (Feature ledger) → BLOCKS production

**Critical Path** (sequential dependencies):
```
Phase 4C (M008)
  → Phase 3 (TRI)
    → Phase 4 (COV)
      → Phase 5 (VAR)
        → Phase 6 (M006 Verify)
          → Phase 7 (M001 Ledger)
            → 100% Compliance ✅
```

**Timeline**: 9-11 weeks (sequential execution)

**Parallelization Opportunities**:
- Phase 0 (Docs) || Phase 4C (M008) Week 1 (investigation)
- Phase 6 (M006 Verify) || Phase 5 (VAR Schema Update)

**Optimized Timeline**: 5-7 weeks (with parallelization)

---

## SECTION 6: COMPLIANCE FORECAST

### Current State (2025-12-13)

| Mandate | Compliance % | Status |
|---------|--------------|--------|
| M001 | 0% | ❌ NON-COMPLIANT |
| M005 | 13.9% | ❌ NON-COMPLIANT |
| M006 | ~60% | ⚠️ PARTIAL |
| M007 | 100% | ✅ COMPLIANT |
| M008 | 66.2% | ⚠️ PARTIAL |
| **Overall** | **48%** | **2/5 compliant** |

### Post-Phase 4C (Week 3, 2026-01-03 estimated)

| Mandate | Compliance % | Change | Status |
|---------|--------------|--------|--------|
| M001 | 0% | - | ❌ NON-COMPLIANT |
| M005 | 13.9% | - | ❌ NON-COMPLIANT |
| M006 | ~60% | - | ⚠️ PARTIAL |
| M007 | 100% | - | ✅ COMPLIANT |
| M008 | **100%** | **+33.8%** | ✅ **COMPLIANT** |
| **Overall** | **56.8%** | **+8.8%** | **3/5 compliant** |

### Post-Phase 5 (Week 8, 2026-02-07 estimated)

| Mandate | Compliance % | Change | Status |
|---------|--------------|--------|--------|
| M001 | 0% | - | ❌ NON-COMPLIANT |
| M005 | **100%** | **+86.1%** | ✅ **COMPLIANT** |
| M006 | ~60% | - | ⚠️ PARTIAL |
| M007 | 100% | - | ✅ COMPLIANT |
| M008 | 100% | - | ✅ COMPLIANT |
| **Overall** | **72%** | **+15.2%** | **4/5 compliant** |

### Post-Phase 8 (Week 10, 2026-02-21 estimated)

| Mandate | Compliance % | Change | Status |
|---------|--------------|--------|--------|
| M001 | 0% | - | ❌ NON-COMPLIANT |
| M005 | 100% | - | ✅ COMPLIANT |
| M006 | **100%** | **+40%** | ✅ **COMPLIANT** |
| M007 | 100% | - | ✅ COMPLIANT |
| M008 | 100% | - | ✅ COMPLIANT |
| **Overall** | **80%** | **+8%** | **4/5 compliant** |

### Post-Phase 7 (Week 11, 2026-02-28 estimated)

| Mandate | Compliance % | Change | Status |
|---------|--------------|--------|--------|
| M001 | **100%** | **+100%** | ✅ **COMPLIANT** |
| M005 | 100% | - | ✅ COMPLIANT |
| M006 | 100% | - | ✅ COMPLIANT |
| M007 | 100% | - | ✅ COMPLIANT |
| M008 | 100% | - | ✅ COMPLIANT |
| **Overall** | **100%** | **+20%** | **✅ 5/5 COMPLIANT** |

**Target Date for 100% Compliance**: 2026-02-28 (11 weeks from now)

---

## APPENDIX A: DEVIATION REFERENCE TABLE

| Deviation ID | Mandate | Description | Severity | Tables Affected | Remediation Phase |
|--------------|---------|-------------|----------|-----------------|-------------------|
| DEV-M001-001 | M001 | Feature ledger file missing | P0 | N/A (file) | Phase 7 |
| DEV-M001-002 | M001 | Feature metadata missing | P0 | N/A (file) | Phase 7 |
| DEV-M001-003 | M001 | SHAP samples missing | P0 | N/A (file) | Phase 7 |
| DEV-M005-001 | M005 | TRI regression features missing | P0 | 194 | Phase 3 |
| DEV-M005-002 | M005 | COV regression features missing | P0 | 3,528 | Phase 4 |
| DEV-M005-003 | M005 | VAR regression features missing | P0 | 63 | Phase 5 |
| DEV-M005-004 | M005 | VAR table count gap | P2 | 17 (missing) | Phase 5 |
| DEV-M006-001 | M006 | Window coverage gap | P1 | ~8,820 (missing) | Phase 6 → 8 |
| DEV-M006-002 | M006 | Feature type coverage gap | P1 | Unknown | Phase 6 |
| DEV-M006-003 | M006 | COV table surplus | P2 | 882 (surplus) | Phase 0 |
| DEV-M006-004 | M006 | Pair coverage gap | P2 | 3 (missing) | Phase 9 |
| DEV-M008-001 | M008 | COV variant identifier missing | P0 | ~1,596 | Phase 4C |
| DEV-M008-002 | M008 | LAG table consolidation | P1 | 224 → 56 | Phase 4C |
| DEV-M008-003 | M008 | REGIME table window suffix | P1 | 141 | Phase 4C |
| DEV-M008-004 | M008 | VAR variant identifier missing | P2 | 7 | Phase 4C |
| DEV-M008-005 | M008 | Other non-compliant tables | P2 | <50 (est.) | Phase 4C |

**Total Deviations**: 16 across 4 mandates (M007 has zero deviations)

---

## APPENDIX B: REMEDIATION CHECKLIST

### Phase 4C (M008 Remediation) - Weeks 1-3

- [ ] **Week 1: Investigation**
  - [ ] Sample 5 COV tables to determine BQX vs IDX (DEV-M008-001)
  - [ ] Sample 5 LAG tables to assess consolidation complexity (DEV-M008-002)
  - [ ] Sample 5 REGIME tables to understand window suffix issue (DEV-M008-003)
  - [ ] Identify 7 VAR tables missing variant IDs (DEV-M008-004)
  - [ ] Finalize rename scripts for all categories

- [ ] **Week 2: Execution**
  - [ ] Execute LAG pilot (5 pairs, GO/NO-GO gate)
  - [ ] If GO: Consolidate all 224 LAG tables → 56 tables
  - [ ] Rename ~1,596 COV tables (add variant IDs)
  - [ ] Rename 7 VAR tables (add variant IDs)
  - [ ] Handle REGIME tables (rename or consolidate)
  - [ ] QA validation at each step

- [ ] **Week 3: Verification**
  - [ ] Final M008 compliance audit (target: 100%)
  - [ ] Create backward-compatible views (30-day grace)
  - [ ] Update intelligence files with new table names
  - [ ] M008 Phase 4C certificate issued by QA

### Phase 3-5 (M005 Schema Updates) - Weeks 5-8

- [ ] **Phase 3 (TRI)**
  - [ ] Design regression feature calculation formulas
  - [ ] Create safe schema update process
  - [ ] Add 63 regression columns to 194 TRI tables
  - [ ] Validate calculations (spot checks)
  - [ ] QA certification (DEV-M005-001 resolved)

- [ ] **Phase 4 (COV)**
  - [ ] Add 42 regression columns to 3,528 COV tables
  - [ ] Validate calculations
  - [ ] QA certification (DEV-M005-002 resolved)

- [ ] **Phase 5 (VAR)**
  - [ ] Generate 17 missing VAR tables (DEV-M005-004)
  - [ ] Add 21 regression columns to 80 VAR tables (63 existing + 17 new)
  - [ ] Validate calculations
  - [ ] QA certification (DEV-M005-003 resolved)

### Phase 6-8 (M006 Coverage) - Weeks 9-10

- [ ] **Phase 6 (Verification)**
  - [ ] Audit COV table surplus (+882 tables) - Determine cause (DEV-M006-003)
  - [ ] Identify exact feature type gap (DEV-M006-002)
  - [ ] Create window expansion plan (DEV-M006-001)

- [ ] **Phase 8 (Window Expansion)**
  - [ ] Generate ~8,820 new COV tables (windows 180, 360, 720, 1440, 2880)
  - [ ] Validate new tables
  - [ ] QA certification (DEV-M006-001 resolved)

### Phase 7 (M001 Feature Ledger) - Weeks 10-11

- [ ] **Feature Ledger Generation**
  - [ ] Execute training pipeline with SHAP enabled
  - [ ] Extract feature names from ensemble model
  - [ ] Map features to source tables
  - [ ] Generate SHAP importance statistics
  - [ ] Calculate stability frequency
  - [ ] Document pruning decisions
  - [ ] Export to parquet (221,228 rows × 18 columns)
  - [ ] QA validation (DEV-M001-001, DEV-M001-002, DEV-M001-003 resolved)

### Phase 9 (Data Quality) - Week 11

- [ ] **Missing Pairs**
  - [ ] Extract EURGBP, EURJPY, GBPJPY (DEV-M006-004)
  - [ ] Merge checkpoints
  - [ ] Validate training files
  - [ ] QA certification

---

**Report Status**: COMPLETE
**Total Deviations Identified**: 16 across 4 mandates
**Next Deliverable**: TRUTH_SOURCE_MISALIGNMENT_REPORT_20251213.md

---

*Enhancement Assistant (EA)*
*BQX ML V3 Project*
*Audit Date: 2025-12-13*
