# IMPLEMENTATION SCRIPT INVENTORY

**Audit Date**: December 13, 2025 20:35 UTC
**Auditor**: Build Agent (BA)
**Purpose**: Comprehensive catalog of all implementation files for M008 Phase 4C execution readiness
**Status**: Phase 1 Script Discovery - IN PROGRESS

---

## EXECUTIVE SUMMARY

**Total Files Discovered**:
- Python Scripts: **146** (scripts/) + **19** (pipelines/) = **165 total**
- Shell Scripts: **27**
- Dockerfiles: **4**
- CloudBuild Configs: **3**
- **GRAND TOTAL**: **199 implementation files**

**Critical Findings** (Preliminary):
- ✅ All key generation scripts (TRI/COV/CORR/MKT/REG) **EXIST**
- ✅ All M008 analysis scripts (audit, validation, remediation) **EXIST**
- ✅ All extraction/merge scripts (Cloud Run pipeline) **EXIST**
- ✅ All Docker containers and build configs **EXIST**
- ⚠️ Need to assess M008/M005 compliance for each script
- ⚠️ Need to verify missing scripts for Phase 4C (COV rename, LAG consolidation, etc.)

---

## PART 1: GENERATION SCRIPTS (Feature Table Creation)

### 1.1 TRI Table Generation

#### **Script**: `scripts/generate_tri_tables.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_tri_tables.py`
**Size**: 16K
**Lines**: 420 lines
**Last Modified**: December 13, 2025 00:53 UTC (19 hours ago)

**Purpose**: Generate 194 TRI tables (triangular arbitrage features)

**M008 Compliance**: ⚠️ **NEEDS ASSESSMENT**
- Script creates tables with pattern: `tri_{feature_type}_{variant}_{curr1}_{curr2}_{curr3}`
- Appears compliant with M008 naming standard Section 1.3
- **TODO**: Verify actual generated table names match M008 pattern

**M005 Readiness**: ❌ **NON-COMPLIANT**
- Current schema: 15 columns (pair values, synthetic, tri_error, etc.)
- Mandated schema: 78 columns (+63 regression features from REG tables)
- **Missing**: regression features (lin_term, quad_term, residual × 3 pairs × 7 windows)
- **Blocker**: Cannot add M005 features until M008 100% compliant (CE Decision 4)

**Dependencies**:
- `google-cloud-bigquery` (BigQuery Client API)
- `pandas` (data manipulation)

**Execution Mode**: Parallel (`--workers` flag supported)

**Cost Estimate**: $5-10 (194 tables)

**Blockers**:
- **BLOCKED** by M008 Phase 4C (must complete M008 first per CE directive)

**Recommendation**:
- ✅ **READY** for Phase 3 (TRI schema updates) AFTER M008 Phase 4C complete
- Script is functional but outputs non-M005-compliant schema
- Will require modification for M005 Phase 3

---

### 1.2 COV Table Generation

#### **Script**: `scripts/generate_cov_tables.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_cov_tables.py`
**Size**: 14K
**Lines**: 380 lines
**Last Modified**: December 13, 2025 01:03 UTC (19 hours ago)

**Purpose**: Generate 2,507 COV tables (cross-pair covariance features)

**M008 Compliance**: ⚠️ **NEEDS ASSESSMENT**
- Expected pattern: `cov_{feature_type}_{variant}_{pair1}_{pair2}`
- EA reported 1,596 COV tables MISSING variant identifier (33.8% non-compliant)
- **Critical**: This is the PRIMARY remediation target for M008 Phase 4C Week 1

**M005 Readiness**: ❌ **NON-COMPLIANT**
- Current schema: 14 columns (spread, ratio, rolling stats)
- Mandated schema: 56 columns (+42 regression features from 2 REG tables)
- **Missing**: regression features from pair1 and pair2

**Dependencies**:
- `google-cloud-bigquery`
- `pandas`

**Execution Mode**: Parallel (`--workers` flag)

**Cost Estimate**: $90-120 (2,507 tables)

**Blockers**:
- **BLOCKED** by M008 Phase 4C (script creates non-compliant table names)

**Recommendation**:
- ⚠️ **PARTIAL READY** - Script exists but creates M008-non-compliant tables
- **MUST NOT RUN** until M008 Phase 4C renames existing 1,596 tables
- After M008 complete: Modify for M005 compliance, then use for regeneration

---

### 1.3 CORR Table Generation

#### **Script**: `scripts/generate_corr_tables.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_corr_tables.py`
**Size**: 13K
**Lines**: 360 lines
**Last Modified**: December 12, 2025 23:28 UTC (21 hours ago)

**Purpose**: Generate 448 CORR tables (cross-asset correlation features)

**M008 Compliance**: ⚠️ **NEEDS ASSESSMENT**
- Expected pattern: `corr_{asset_type}_{variant}_{pair}_{asset}`
- Some tables validated as `corr_bqx_ibkr_*` (appears compliant)
- **TODO**: Verify all 448 tables match M008 pattern

**M005 Readiness**: ✅ **COMPLIANT** (CORR tables do not require regression features per M005)

**Dependencies**:
- `google-cloud-bigquery`
- `pandas`

**Execution Mode**: Parallel (`--workers` flag)

**Cost Estimate**: $10-15 (448 tables)

**Blockers**: None identified

**Recommendation**: ✅ **READY** for use after M008 Phase 4C (if M008 compliant)

---

#### **Script**: `scripts/generate_corr_tables_fixed.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_corr_tables_fixed.py`
**Size**: Not measured yet
**Last Modified**: Not measured yet

**Purpose**: Fixed version of CORR generation (addressed earlier bugs)

**Relationship**: Supersedes `generate_corr_tables.py` - verify which to use

**Recommendation**: ⚠️ **INVESTIGATE** which CORR script is authoritative

---

### 1.4 MKT Table Generation

#### **Script**: `scripts/generate_mkt_tables.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_mkt_tables.py`
**Size**: 6.8K
**Lines**: 238 lines
**Last Modified**: December 9, 2025 21:42 UTC (4 days ago)

**Purpose**: Generate 12 MKT tables (market-wide aggregation features)

**M008 Compliance**: ⚠️ **PARTIAL** (1 exception table approved)
- Expected pattern: `mkt_{feature_type}_{variant}`
- Exception: `mkt_reg_bqx_summary` approved by CE (Decision 3)
- **TODO**: Verify 11/12 tables match M008 pattern

**M005 Readiness**: ✅ **COMPLIANT** (MKT tables do not require regression features per M005)

**Dependencies**:
- `google-cloud-bigquery`
- `pandas`

**Execution Mode**: Parallel (`--workers` flag)

**Cost Estimate**: $5-10 (12 tables)

**Blockers**: None identified

**Recommendation**: ✅ **READY** for Phase 5 (after M008 complete)

---

### 1.5 REG Table Generation with Coefficients

#### **Script**: `scripts/generate_reg_tables_with_coefficients.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_reg_tables_with_coefficients.py`
**Size**: 13K
**Last Modified**: December 13, 2025 02:55 UTC (17 hours ago)

**Purpose**: Generate 84 REG tables with polynomial regression features (lin_term, quad_term, residual)

**M008 Compliance**: ✅ **COMPLIANT** (REG tables follow `reg_{variant}_{pair}` pattern)

**M005 Readiness**: ✅ **SOURCE COMPLIANT**
- These REG tables are the **SOURCE** for M005 compliance
- TRI/COV/VAR tables must JOIN with these REG tables to include regression features
- Schema includes: lin_term, quad_term, residual for all 7 windows

**Dependencies**:
- `google-cloud-bigquery`
- `pandas`
- `numpy` (polynomial regression calculations)

**Execution Mode**: Parallel (`--workers` flag)

**Cost Estimate**: $10-15 (84 tables)

**Blockers**: None identified

**Recommendation**: ✅ **READY** - Critical for M005 Phase 2 (REG schema verification)

---

### 1.6 Feature Catalogue Generation

#### **Script**: `scripts/generate_comprehensive_feature_catalogue.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/generate_comprehensive_feature_catalogue.py`
**Size**: Not measured yet
**Last Modified**: Not measured yet

**Purpose**: Generate `intelligence/feature_catalogue.json` with complete feature inventory

**M008 Compliance**: ✅ **COMPLIANT** (documentation tool, not table generator)

**M005 Readiness**: ⚠️ **NEEDS UPDATE**
- Must reflect new regression features after M005 schema updates
- Current catalogue may not include 63 new TRI features, 42 new COV features, etc.

**Dependencies**:
- `google-cloud-bigquery` (INFORMATION_SCHEMA queries)
- JSON serialization

**Execution Mode**: Single-threaded

**Cost Estimate**: $0-1 (read-only queries)

**Blockers**: None

**Recommendation**: ✅ **READY** - Will need re-run after M005 Phase 3-5

---

## PART 2: M008 ANALYSIS SCRIPTS (Phase 4C Required)

### 2.1 M008 Table Compliance Audit

#### **Script**: `scripts/audit_m008_table_compliance.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/audit_m008_table_compliance.py`
**Size**: 11K
**Last Modified**: December 13, 2025 05:35 UTC (15 hours ago)

**Purpose**: Audit all 5,817 tables for M008 naming standard compliance

**M008 Compliance**: ✅ **CRITICAL TOOL** for Phase 4C

**Functionality**:
- Queries INFORMATION_SCHEMA to list all tables
- Parses table names against M008 patterns
- Reports compliant vs non-compliant tables
- **Known Output**: 3,849 compliant (66.2%), 1,968 non-compliant (33.8%)

**Dependencies**:
- `google-cloud-bigquery`
- M008 pattern validation logic

**Execution Mode**: Single-threaded (query execution)

**Cost Estimate**: $0-1 (metadata queries)

**Blockers**: None

**Recommendation**: ✅ **READY** - Essential for Phase 4C monitoring

---

### 2.2 M008 Column Compliance Validation

#### **Script**: `scripts/validate_m008_column_compliance.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/validate_m008_column_compliance.py`
**Size**: 11K
**Last Modified**: December 13, 2025 10:20 UTC (10 hours ago)

**Purpose**: Validate column names within tables match M008 patterns

**M008 Compliance**: ✅ **SECONDARY VALIDATION TOOL**

**Functionality**:
- Queries table schemas
- Validates column naming conventions
- Reports mismatches

**Dependencies**:
- `google-cloud-bigquery`

**Execution Mode**: Single-threaded

**Cost Estimate**: $1-5 (schema queries for 5,817 tables)

**Blockers**: None

**Recommendation**: ✅ **READY** - Use for Phase 4C post-rename validation

---

### 2.3 M008 Table Remediation Execution

#### **Script**: `scripts/execute_m008_table_remediation.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/execute_m008_table_remediation.py`
**Size**: 13K
**Last Modified**: December 13, 2025 10:29 UTC (10 hours ago)

**Purpose**: Execute bulk table renames for M008 compliance

**M008 Compliance**: ✅ **PRIMARY EXECUTION TOOL** for Phase 4C

**Functionality**:
- Reads rename mapping (old_name → new_name)
- Executes BigQuery `ALTER TABLE RENAME` commands
- Batch processing with rollback capability
- **Critical for**: 1,968 table renames

**Dependencies**:
- `google-cloud-bigquery`
- Rename inventory CSV (from EA)

**Execution Mode**: Batched (100-200 tables per batch per CE directive)

**Cost Estimate**: $0 (metadata operations, no query cost)

**Blockers**:
- ⚠️ **REQUIRES INPUT**: Rename inventory CSV from EA (old → new mappings)

**Recommendation**: ✅ **READY** pending EA rename inventory delivery

---

### 2.4 TRI Table Rename (M008 Phase 4B)

#### **Script**: `scripts/rename_tri_tables_m008.py`

**Status**: ✅ **EXISTS** (Phase 4B COMPLETE)
**Location**: `/home/micha/bqx_ml_v3/scripts/rename_tri_tables_m008.py`
**Size**: 7.1K
**Last Modified**: December 13, 2025 13:05 UTC (7 hours ago)

**Purpose**: Rename 131 TRI tables for M008 Phase 4B compliance

**M008 Compliance**: ✅ **COMPLETE** (Phase 4B executed Dec 13)
- 65 renamed, 66 already compliant
- 100% success rate
- $0 cost

**Result**: **NO LONGER NEEDED** for Phase 4C (Phase 4B complete)

**Recommendation**: ✅ **ARCHIVED** - Reference for Phase 4C methodology

---

### 2.5 Table Gap Analysis

#### **Script**: `scripts/analyze_table_gaps.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/analyze_table_gaps.py`
**Size**: Not measured yet
**Last Modified**: Not measured yet

**Purpose**: Identify missing tables in feature universe

**M008 Compliance**: ✅ **ANALYSIS TOOL** (supports gap remediation)

**Functionality**:
- Compares expected vs actual tables
- Identifies missing tables by category
- Reports gaps for remediation

**Dependencies**:
- `google-cloud-bigquery`

**Execution Mode**: Single-threaded

**Cost Estimate**: $0-1

**Blockers**: None

**Recommendation**: ✅ **READY** - Useful for post-M008 verification

---

## PART 3: MISSING SCRIPTS FOR M008 PHASE 4C

### 3.1 COV Rename Script

**Status**: ❌ **MISSING**

**Required For**: M008 Phase 4C Week 1 - Rename 1,596 COV tables to add variant identifier

**Expected Pattern**: `cov_agg_{pair1}_{pair2}` → `cov_agg_{variant}_{pair1}_{pair2}`

**Functionality Needed**:
1. Query INFORMATION_SCHEMA for all `cov_*` tables
2. Parse table name to extract feature_type, pair1, pair2
3. Determine variant (BQX or IDX) from source data (sample 5 rows)
4. Generate new name: `cov_{feature_type}_{variant}_{pair1}_{pair2}`
5. Execute `ALTER TABLE RENAME` in batches

**Estimated Creation Time**: **4-6 hours**
- 2 hours: Script development
- 1 hour: Testing on 5 sample tables
- 1 hour: Dry-run validation
- 2 hours: Full execution (1,596 tables)

**Blocker Level**: 🔴 **P0-CRITICAL** (blocks Phase 4C Week 1 execution)

**Recommendation**: **CREATE IMMEDIATELY** (Dec 14 AM)

**Workaround**: Adapt `execute_m008_table_remediation.py` with COV-specific logic

---

### 3.2 LAG Consolidation Script

**Status**: ❌ **MISSING**

**Required For**: M008 Phase 4C Week 1-2 - Consolidate 224 LAG tables → 56 tables

**CE Decision**: Option A (consolidate) approved

**Expected Transformation**:
- `lag_idx_eurusd_45`, `lag_idx_eurusd_90`, `lag_idx_eurusd_180`, `lag_idx_eurusd_360`
  → `lag_idx_eurusd` (all windows as columns)

**Functionality Needed**:
1. Query all `lag_*` tables grouped by pair and variant
2. For each (pair, variant) group:
   - Create consolidated table with all window columns
   - Merge data from all window-specific tables
   - Validate row count preservation
   - Drop source tables after validation
3. **Gate at 5 pairs**: Validate pilot before full rollout

**Estimated Creation Time**: **6-8 hours**
- 3 hours: Script development (complex multi-table merge logic)
- 2 hours: Pilot testing (5 pairs)
- 1 hour: Validation protocol
- 2 hours: Full execution (56 consolidated tables)

**Blocker Level**: 🔴 **P0-CRITICAL** (blocks Phase 4C Week 1-2 execution)

**Cost**: $5-10 (approved by CE)

**Recommendation**: **CREATE IMMEDIATELY** (Dec 14 AM)

**Risk**: **MEDIUM** - Complex merge logic, row count validation critical

---

### 3.3 VAR Rename Script

**Status**: ⚠️ **POSSIBLY COVERED** by `execute_m008_table_remediation.py`

**Required For**: M008 Phase 4C - Rename 7 VAR tables

**Expected Pattern**: Likely missing variant identifier (similar to COV issue)

**Functionality Needed**:
- Same as COV rename (variant detection + rename)

**Estimated Creation Time**: **1-2 hours** (if not covered by generic script)

**Blocker Level**: ⚠️ **P1-HIGH** (7 tables only, can be done manually if needed)

**Recommendation**: **ASSESS** whether generic remediation script handles VAR tables

---

### 3.4 Primary Violation Script (364 tables)

**Status**: ❌ **MISSING** (EA investigating)

**Required For**: M008 Phase 4C - Address 364 "primary violation" tables

**Expected Functionality**: Depends on EA's investigation findings (not yet delivered)

**Estimated Creation Time**: **UNKNOWN** (pending EA analysis)

**Blocker Level**: ⚠️ **P1-HIGH** (significant count, but investigation ongoing)

**Recommendation**: **WAIT** for EA investigation completion (Dec 14-15)

---

### 3.5 View Creation Script (30-day grace period)

**Status**: ❌ **MISSING**

**Required For**: M008 Phase 4C - Create backward-compatible views for all 1,968 renamed tables

**CE Decision**: Option A (30-day grace) approved

**Functionality Needed**:
1. Read rename inventory (old_name → new_name mappings)
2. For each renamed table:
   - Create VIEW `old_name` AS `SELECT * FROM new_name`
3. Schedule view deletion for Jan 12, 2026 (30 days)

**Estimated Creation Time**: **2-3 hours**
- 1 hour: Script development
- 1 hour: Testing (validate views work correctly)
- 1 hour: Full execution (1,968 views)

**Blocker Level**: ⚠️ **P2-MEDIUM** (grace period, not critical path)

**Cost**: $0 (view creation is metadata operation)

**Recommendation**: **CREATE** during Week 2 (after renames complete)

---

### 3.6 Row Count Validation Tool

**Status**: ❌ **MISSING**

**Required For**: M008 Phase 4C - Validate LAG consolidation preserves row counts

**Functionality Needed**:
```python
def validate_row_counts(source_tables, dest_table):
    source_total = sum(query_row_count(t) for t in source_tables)
    dest_count = query_row_count(dest_table)
    assert source_total == dest_count, f"Mismatch: {source_total} != {dest_count}"
```

**Estimated Creation Time**: **1 hour** (simple SQL query script)

**Blocker Level**: 🔴 **P0-CRITICAL** for LAG consolidation validation

**Recommendation**: **CREATE IMMEDIATELY** (Dec 14 AM, before LAG consolidation)

---

## PART 4: EXTRACTION & MERGE SCRIPTS (Cloud Run Pipeline)

### 4.1 Parallel Feature Testing (Extraction Pipeline)

#### **Script**: `pipelines/training/parallel_feature_testing.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/pipelines/training/parallel_feature_testing.py`
**Size**: Not measured yet
**Last Modified**: Recently (Tier 2A implemented Dec 12)

**Purpose**: Extract all features + targets for a currency pair from BigQuery

**Cloud Run Integration**: ✅ **DEPLOYED** as `bqx-ml-extract` job

**Key Features**:
- Extracts 667 tables per pair (11,337 columns total)
- Tier 2A implemented: Excludes final 2,880 rows for target completeness
- Checkpoint-based resumption (GCS backup)
- Parallel worker optimization (4 workers on 4 CPUs)

**Dependencies**:
- `google-cloud-bigquery`
- `pandas`
- `pyarrow` (Parquet serialization)

**Execution Time**: 60-75 min per pair

**Cost**: $0.35 per pair (Cloud Run compute)

**Status**: ⏸️ **SUSPENDED** per user directive (pending NULL remediation)

**Blockers**:
- User suspended Cloud Run until NULL remediation complete
- **NOTE**: M008 Phase 4C does NOT resolve NULL issues (separate concern)

**Recommendation**:
- ✅ **READY** for resumption after M008 + NULL remediation
- Script is operational, just suspended by user

---

### 4.2 Polars Merge (Safe Variant)

#### **Script**: `scripts/merge_with_polars_safe.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/merge_with_polars_safe.py`
**Size**: Not measured yet
**Last Modified**: December 12, 2025 (recent)

**Purpose**: Merge extracted features into single training file using Polars

**Cloud Run Integration**: ✅ **DEPLOYED** as `bqx-ml-merge` job (user-mandated Polars)

**Key Features**:
- Polars-based merge (4.6× faster than BigQuery, per user mandate)
- Handles 11,337 columns × 177K rows
- Memory-efficient (12 GB container)
- Checkpoint validation

**Dependencies**:
- `polars` (DataFrame library)
- `pyarrow` (Parquet I/O)

**Execution Time**: 13-20 min per pair

**Cost**: $0.36 per pair (Cloud Run compute)

**Status**: ⏸️ **SUSPENDED** per user directive

**Recommendation**: ✅ **READY** for resumption

---

### 4.3 Training File Validation

#### **Script**: `scripts/validate_training_file.py`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/validate_training_file.py`
**Size**: Not measured yet
**Last Modified**: Not measured yet

**Purpose**: Validate merged training file meets all quality criteria

**Validation Checks**:
- Row count within expected range
- Column count matches expected
- NULL percentages below thresholds
- Target completeness (h15-h2880)
- Feature completeness
- Date range validation

**Dependencies**:
- `polars` or `pandas`
- `pyarrow`

**Execution Time**: 1-2 min per file

**Cost**: $0 (local validation)

**Recommendation**: ✅ **READY** - Critical for QA validation

---

#### **Script**: `scripts/validate_eurusd_training_file.py`

**Status**: ✅ **EXISTS** (EURUSD-specific variant)
**Location**: `/home/micha/bqx_ml_v3/scripts/validate_eurusd_training_file.py`

**Purpose**: EURUSD-specific validation (legacy script, may be superseded by generic validator)

**Recommendation**: ⚠️ **ASSESS** whether to keep or deprecate (prefer generic validator)

---

### 4.4 Cloud Run Orchestration Scripts

#### **Script**: `scripts/cloud_run_polars_pipeline.sh`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/cloud_run_polars_pipeline.sh`

**Purpose**: Orchestrate extract → merge → validate pipeline via Cloud Run jobs

**Cloud Run Jobs**:
- `bqx-ml-extract` (Dockerfile.extract)
- `bqx-ml-merge` (Dockerfile.merge)

**Dependencies**:
- `gcloud` CLI
- Cloud Run API access

**Status**: ⏸️ **SUSPENDED** per user directive

**Recommendation**: ✅ **READY** for resumption

---

#### **Script**: `scripts/extract_only.sh`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/extract_only.sh`

**Purpose**: Execute only extraction phase (bifurcated architecture)

**Recommendation**: ✅ **READY**

---

#### **Script**: `scripts/merge_only.sh`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/merge_only.sh`

**Purpose**: Execute only merge phase (bifurcated architecture)

**Recommendation**: ✅ **READY**

---

#### **Script**: `scripts/extract_all_remaining_pairs.sh`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/extract_all_remaining_pairs.sh`

**Purpose**: Sequential extraction for all 27 remaining pairs

**Recommendation**: ⚠️ **DEPRECATED** (use parallel variant for efficiency)

---

#### **Script**: `scripts/extract_all_remaining_pairs_parallel.sh`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/scripts/extract_all_remaining_pairs_parallel.sh`

**Purpose**: Parallel extraction for all 27 remaining pairs (4× concurrent)

**Issue**: Fixed Dec 12 but NOT DEPLOYED (Cloud Run suspended)
- Fixed: `--args="${PAIR}"` → `--set-env-vars "PAIR=${PAIR}"`
- Reason: Cloud Run uses environment variables, not args

**Recommendation**: ✅ **READY** for resumption after fixes deployed

---

## PART 5: DOCKER & DEPLOYMENT

### 5.1 Dockerfiles

#### **File**: `Dockerfile.extract`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/Dockerfile.extract`
**Last Modified**: December 12, 2025 20:46 UTC

**Purpose**: Container for bqx-ml-extract Cloud Run job

**Base Image**: python:3.10-slim

**Dependencies** (from logs/errors):
- ✅ `google-cloud-bigquery`
- ✅ `pandas`
- ✅ `pyarrow`
- ❌ `duckdb` (MISSING - caused Batch 1 failure)
- ❌ `numpy` (MISSING - caused Batch 1 failure)

**Critical Issue**: **INCOMPLETE DEPENDENCIES**
- Dec 12 Batch 1 extraction failed with `ModuleNotFoundError: duckdb`
- Fix identified but NOT DEPLOYED (Cloud Run suspended)

**Recommendation**:
- 🔴 **UPDATE REQUIRED** before Cloud Run resumption
- Add: `duckdb==0.9.2` and `numpy==1.24.3` to requirements

---

#### **File**: `Dockerfile.merge`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/Dockerfile.merge`
**Last Modified**: December 12, 2025 19:51 UTC

**Purpose**: Container for bqx-ml-merge Cloud Run job

**Base Image**: python:3.10-slim

**Dependencies**:
- `polars`
- `pyarrow`
- `google-cloud-storage` (GCS access)

**Status**: ✅ **READY** (user-mandated Polars merge working)

**Recommendation**: ✅ **NO CHANGES NEEDED**

---

#### **File**: `Dockerfile.cloudrun-polars`

**Status**: ✅ **EXISTS** (legacy unified container)
**Location**: `/home/micha/bqx_ml_v3/Dockerfile.cloudrun-polars`

**Purpose**: Original unified extract+merge container (before bifurcation)

**Status**: ⚠️ **DEPRECATED** (superseded by split architecture)

**Recommendation**: ⚠️ **ARCHIVE** (keep for reference, not for deployment)

---

#### **File**: `Dockerfile`

**Status**: ✅ **EXISTS** (base Dockerfile)
**Location**: `/home/micha/bqx_ml_v3/Dockerfile`

**Purpose**: General-purpose development container

**Recommendation**: ⚠️ **NOT FOR PRODUCTION** (use Dockerfile.extract / Dockerfile.merge)

---

### 5.2 CloudBuild Configs

#### **File**: `cloudbuild-extract.yaml`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/cloudbuild-extract.yaml`
**Last Modified**: December 12, 2025 19:52 UTC

**Purpose**: Build configuration for bqx-ml-extract container

**Image Target**: `gcr.io/bqx-ml/bqx-ml-extract:latest`

**Status**: ✅ **READY** (needs rebuild with Dockerfile.extract dependency fixes)

---

#### **File**: `cloudbuild-merge.yaml`

**Status**: ✅ **EXISTS**
**Location**: `/home/micha/bqx_ml_v3/cloudbuild-merge.yaml`
**Last Modified**: December 12, 2025 19:52 UTC

**Purpose**: Build configuration for bqx-ml-merge container

**Image Target**: `gcr.io/bqx-ml/bqx-ml-merge:latest`

**Status**: ✅ **READY**

---

#### **File**: `cloudbuild-polars.yaml`

**Status**: ✅ **EXISTS** (legacy)
**Location**: `/home/micha/bqx_ml_v3/cloudbuild-polars.yaml`

**Purpose**: Build configuration for unified container (before bifurcation)

**Status**: ⚠️ **DEPRECATED**

---

## PART 6: VALIDATION & QUALITY SCRIPTS

### 6.1 Existing Validation Scripts

1. `scripts/validate_training_file.py` - ✅ **EXISTS** (covered in Part 4)
2. `scripts/validate_eurusd_training_file.py` - ✅ **EXISTS** (covered in Part 4)
3. `scripts/validate_m008_column_compliance.py` - ✅ **EXISTS** (covered in Part 2)
4. `scripts/validate_polars_output.py` - ✅ **EXISTS** (Polars merge validation)
5. `scripts/validate_polynomial_features.py` - ✅ **EXISTS** (REG table validation)
6. `scripts/validate_v2_migration.py` - ✅ **EXISTS** (V2 migration validation)
7. `scripts/validate_coverage.py` - ✅ **EXISTS** (Feature coverage validation)
8. `scripts/validate_gate3.py` - ✅ **EXISTS** (GATE_3 validation for EURUSD h15)

**Total Validation Scripts**: 8+ scripts

**Recommendation**: ✅ **WELL-COVERED** for validation needs

---

## PART 7: ADDITIONAL SCRIPT CATEGORIES

### 7.1 Monitoring Scripts

- `scripts/monitor_eurusd_checkpoints.sh` - ✅ **EXISTS**
- `scripts/monitor_extraction.sh` - ✅ **EXISTS**
- `scripts/monitor_pipeline.sh` - ✅ **EXISTS**
- `scripts/monitor_step6.sh` - ✅ **EXISTS**
- `scripts/monitor_comprehensive_tests.py` - ✅ **EXISTS**

**Recommendation**: ✅ **READY** for Phase 4C execution monitoring

---

### 7.2 Analysis & Reporting Scripts

- `scripts/generate_performance_report.py` - ✅ **EXISTS**
- `scripts/estimate_query_cost.py` - ✅ **EXISTS**
- `scripts/gcp_ml_coverage_audit.py` - ✅ **EXISTS**

**Recommendation**: ✅ **READY** for Phase 4C cost tracking

---

### 7.3 Legacy/Archive Scripts

- Multiple `scripts/fix_*.py` scripts (AirTable remediation - legacy)
- Multiple `scripts/train_*.py` scripts (model training - pending)
- Multiple `scripts/vertex_*.py` scripts (Vertex AI - not currently used)

**Recommendation**: ⚠️ **LOW PRIORITY** - Not relevant for M008 Phase 4C

---

## CRITICAL GAPS SUMMARY

### P0-CRITICAL Gaps (Block Phase 4C Execution)

1. ❌ **COV Rename Script** (1,596 tables)
   - Estimated creation time: 4-6 hours
   - **Action**: Create immediately Dec 14 AM

2. ❌ **LAG Consolidation Script** (224→56 tables)
   - Estimated creation time: 6-8 hours
   - **Action**: Create immediately Dec 14 AM

3. ❌ **Row Count Validation Tool** (LAG consolidation validation)
   - Estimated creation time: 1 hour
   - **Action**: Create immediately Dec 14 AM (before LAG consolidation)

---

### P1-HIGH Gaps (Significant but not immediate blocker)

4. ⚠️ **VAR Rename Script** (7 tables)
   - May be covered by generic `execute_m008_table_remediation.py`
   - **Action**: Assess Dec 14 AM

5. ❌ **Primary Violation Script** (364 tables)
   - Pending EA investigation
   - **Action**: Wait for EA findings (Dec 14-15)

---

### P2-MEDIUM Gaps (Grace period, not critical path)

6. ❌ **View Creation Script** (1,968 backward-compatible views)
   - Estimated creation time: 2-3 hours
   - **Action**: Create during Week 2 (after renames complete)

---

## NEXT STEPS (IMMEDIATE)

1. **ASSESS** `execute_m008_table_remediation.py` for COV/VAR handling
2. **CREATE** COV rename script (4-6 hours, Dec 14 AM)
3. **CREATE** LAG consolidation script (6-8 hours, Dec 14 AM)
4. **CREATE** Row count validation tool (1 hour, Dec 14 AM)
5. **UPDATE** Dockerfile.extract dependencies (duckdb, numpy)

**Total Immediate Work**: **12-16 hours** (can be parallelized if needed)

---

## READINESS ASSESSMENT

**Can we execute M008 Phase 4C starting Dec 14 with ZERO delays?**

⚠️ **NO** - 3 critical scripts missing (12-16 hours creation time)

**Recommended Start Date**: **Dec 15** (after missing scripts created and tested)

**Alternative**: **Partial start Dec 14** (execute non-dependent tasks while scripts are created)

---

**Audit Status**: Phase 1 Script Discovery **COMPLETE**
**Next Phase**: Phase 2 Script Readiness Assessment (detailed M008/M005 compliance review)

**Document Updated**: December 13, 2025 21:30 UTC
**Auditor**: Build Agent (BA)
**Deliverable**: 1 of 6 required by CE

---

*End of Implementation Script Inventory*
