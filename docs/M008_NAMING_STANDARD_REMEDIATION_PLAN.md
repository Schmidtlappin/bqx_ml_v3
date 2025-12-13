# ⚠️ DEPRECATED - DO NOT USE

**Status**: SUPERSEDED by comprehensive 10-phase remediation plan
**Superseded By**: [COMPREHENSIVE_REMEDIATION_PLAN_20251213.md](COMPREHENSIVE_REMEDIATION_PLAN_20251213.md)
**Deprecation Date**: 2025-12-14
**Reason**: Original plan was partial scope (M008 only, 269 tables). New plan addresses all 5 mandates with proper sequencing and 1,968 table remediation.

**Redirect**: See [docs/COMPREHENSIVE_REMEDIATION_PLAN_20251213.md](COMPREHENSIVE_REMEDIATION_PLAN_20251213.md) for the current authoritative plan.

**Why This Plan Is Obsolete**:
1. **Inaccurate table count**: Based on 6,069 tables (actual: 5,817)
2. **Inaccurate non-compliant count**: Claimed 269 tables (actual: 1,968 tables)
3. **Incomplete audit**: Did not identify COV, LAG, VAR, primary violations
4. **M008-only scope**: Did not address M005, M006, M007 mandate gaps
5. **No Phase 0**: Jumped directly to remediation without documentation reconciliation

**DO NOT EXECUTE THIS PLAN. USE THE COMPREHENSIVE PLAN INSTEAD.**

---

# M008 Naming Standard Remediation Plan (DEPRECATED)

**Mandate**: BQX-ML-M008 (Naming Standard Mandate)
**Date**: 2025-12-13
**Status**: ~~PLANNING~~ **DEPRECATED**
**Priority**: ~~P0-CRITICAL~~ **SUPERSEDED**
**Current Compliance**: ~~95.6% (5,800/6,069 tables)~~ **INACCURATE - See comprehensive plan**
**Non-Compliant**: ~~269 tables (4.4%)~~ **INACCURATE - Actual: 1,968 tables (33.8%)**

---

## EXECUTIVE SUMMARY

**Problem**: 269 tables (4.4%) are non-compliant with M008 naming standards. Additionally, the Feature Catalogue v3.1.0 marks all 1,604 base column names as "M008-compliant" **without verification**.

**Objective**: Achieve **100% M008 compliance** across all tables, columns, and features.

**Timeline**: 6 phases over 2-3 weeks (can run in parallel with Phase 0C REG regeneration)

---

## M008 NAMING STANDARD REQUIREMENTS

### Table Naming: `{type}_{variant}_{identifiers}`

**Pattern**: `^[a-z]+_[a-z]+_[a-z0-9_]+$`

**Rules**:
- All lowercase
- Underscore separators
- Type prefix (agg, mom, vol, reg, cov, corr, tri, mkt, csi, etc.)
- Variant indicator (bqx, idx, or other)
- Identifiers (pair names, currencies, ETF symbols)
- **Alphabetical sorting** for multi-entity tables (e.g., `eurusd_gbpusd` NOT `gbpusd_eurusd`)

**Valid Examples**:
```
✅ agg_bqx_eurusd
✅ cov_agg_bqx_eurusd_gbpusd
✅ tri_agg_idx_eur_usd_gbp
✅ corr_etf_idx_eurusd_spy
✅ csi_agg_usd
```

**Invalid Examples**:
```
❌ AGG_BQX_EURUSD (uppercase)
❌ agg-bqx-eurusd (hyphens instead of underscores)
❌ cov_agg_bqx_gbpusd_eurusd (wrong alphabetical order)
❌ corr_eurusd_spy_etf_idx (wrong component order)
```

### Column Naming: `{type}_{metric}_{window}`

**Pattern**: `^[a-z]+_[a-z0-9_]+_[0-9]+$`

**Rules**:
- All lowercase
- Underscore separators
- Type prefix matches table type
- Metric name (mean, std, lin_coef, bqx, etc.)
- Window size (45, 90, 180, 360, 720, 1440, 2880)

**Valid Examples**:
```
✅ agg_mean_45
✅ reg_lin_coef_180
✅ mom_bqx_90
✅ vol_atr_360
✅ cov_spread_45
```

**Invalid Examples**:
```
❌ AGG_MEAN_45 (uppercase)
❌ agg_Mean_45 (mixed case)
❌ aggMean45 (camelCase)
❌ agg_mean (missing window)
```

---

## PHASED REMEDIATION PLAN

### PHASE 1: Audit and Identification (Est: 4-6 hours)

**Objective**: Identify all 269 non-compliant tables and understand violation patterns.

**Tasks**:
1. Query BigQuery metadata to list all 6,069 tables
2. Apply M008 regex patterns to identify violations
3. Categorize violations by type:
   - Uppercase/mixed case
   - Wrong separator (hyphens, dots)
   - Wrong component order
   - Missing variant indicator
   - Alphabetical sorting violations
4. Generate violation report with examples

**Deliverables**:
- `M008_VIOLATION_REPORT_20251213.md` (categorized list of 269 tables)
- `M008_VIOLATION_PATTERNS.json` (violation types and counts)

**Script**: `scripts/audit_m008_table_compliance.py`

**Timeline**: Day 1

---

### PHASE 2: Feature Catalogue Validation (Est: 2-3 hours)

**Objective**: Verify M008 compliance of 1,604 base column names in Feature Catalogue v3.1.0.

**Tasks**:
1. Load Feature Catalogue v3.1.0
2. Apply M008 column naming regex to all 1,604 feature names
3. Identify non-compliant column names
4. Update catalogue to mark actual compliance status (not assumed)
5. Generate corrected Feature Catalogue v3.2.0

**Deliverables**:
- `intelligence/feature_catalogue_v3.2.0.json` (verified M008 compliance)
- `M008_COLUMN_VALIDATION_REPORT.md` (non-compliant columns)

**Script**: `scripts/validate_m008_column_compliance.py`

**Timeline**: Day 1 (parallel with Phase 1)

---

### PHASE 3: Remediation Planning (Est: 3-4 hours)

**Objective**: Create detailed remediation plan for each non-compliant table.

**Tasks**:
1. For each of 269 non-compliant tables:
   - Identify correct M008-compliant name
   - Check for naming conflicts (does corrected name already exist?)
   - Determine remediation strategy (rename vs recreate)
   - Estimate impact on downstream dependencies
2. Prioritize remediation by table family:
   - **Tier 1**: Core tables (agg, mom, vol, reg) - 0 violations expected
   - **Tier 2**: Comparison tables (cov, corr, tri) - likely violations
   - **Tier 3**: Specialized tables (csi, mkt, var) - unknown

**Deliverables**:
- `M008_REMEDIATION_PLAN_DETAILED.md` (table-by-table plan)
- `M008_RENAME_MAPPING.json` (old_name → new_name mappings)

**Script**: `scripts/plan_m008_remediation.py`

**Timeline**: Day 2

---

### PHASE 4: Implementation - Automated Remediation (Est: 6-12 hours)

**Objective**: Execute remediation for non-compliant tables.

**Strategy Options**:

#### Option A: Rename Tables (If Safe)
```sql
-- BigQuery supports table renaming
ALTER TABLE `bqx-ml.bqx_ml_v3_features_v2.{old_name}`
RENAME TO `{new_name}`;
```
**Pros**: Fast, preserves data and partitioning
**Cons**: Breaks any external references (unlikely - internal project only)

#### Option B: Recreate Tables (If Complex)
```sql
-- Create new table with correct name
CREATE TABLE `bqx-ml.bqx_ml_v3_features_v2.{new_name}`
PARTITION BY DATE(interval_time)
CLUSTER BY pair
AS SELECT * FROM `bqx-ml.bqx_ml_v3_features_v2.{old_name}`;

-- Verify row counts match
-- Delete old table
DROP TABLE `bqx-ml.bqx_ml_v3_features_v2.{old_name}`;
```
**Pros**: Clean slate, validates data integrity
**Cons**: Slower, temporary storage doubling

**Tasks**:
1. Backup table list before remediation
2. Execute remediation in batches (50 tables/batch)
3. Verify each batch before proceeding
4. Update BigQuery catalog after each batch

**Deliverables**:
- All 269 tables renamed/recreated to M008 compliance
- `M008_REMEDIATION_LOG.json` (execution results)

**Script**: `scripts/execute_m008_remediation.py`

**Timeline**: Days 3-4 (12 hours total, split across 2 days)

---

### PHASE 5: Prevention - Script Validation (Est: 4-6 hours)

**Objective**: Add M008 validation to all table/column generation scripts.

**Scripts to Update**:
1. `scripts/generate_cov_tables.py` - Add M008 table name validation
2. `scripts/generate_corr_tables_fixed.py` - Add M008 validation
3. `scripts/generate_tri_tables.py` - Add M008 validation
4. `scripts/generate_reg_tables_with_coefficients.py` - Add M008 validation
5. `scripts/generate_mkt_tables.py` - Add M008 validation
6. All other table generation scripts

**Validation Function**:
```python
import re

def validate_m008_table_name(table_name: str) -> tuple[bool, str]:
    """
    Validate table name against M008 standard.

    Returns:
        (is_valid, error_message)
    """
    pattern = r'^[a-z]+_[a-z]+_[a-z0-9_]+$'

    if not re.match(pattern, table_name):
        return False, f"Table name '{table_name}' does not match M008 pattern"

    # Additional checks: alphabetical sorting for multi-entity tables
    # ... (implementation details)

    return True, ""

def validate_m008_column_name(column_name: str) -> tuple[bool, str]:
    """
    Validate column name against M008 standard.

    Returns:
        (is_valid, error_message)
    """
    # Skip metadata columns
    if column_name in ['interval_time', 'pair', 'source_value']:
        return True, ""

    pattern = r'^[a-z]+_[a-z0-9_]+_[0-9]+$'

    if not re.match(pattern, column_name):
        return False, f"Column name '{column_name}' does not match M008 pattern"

    return True, ""
```

**Tasks**:
1. Create `scripts/m008_validation.py` module
2. Add validation to each generation script
3. **REJECT** table/column creation if validation fails
4. Add M008 validation to Cloud Run pipeline

**Deliverables**:
- `scripts/m008_validation.py` (reusable validation module)
- Updated generation scripts with M008 checks
- CI/CD validation (fail-fast on M008 violations)

**Timeline**: Day 5

---

### PHASE 6: Final Verification (Est: 2-3 hours)

**Objective**: Verify 100% M008 compliance across all tables, columns, and features.

**Tasks**:
1. Query all 6,069 tables in BigQuery
2. Validate all table names against M008
3. Sample-validate column names from each table family
4. Verify Feature Catalogue v3.2.0 reflects actual compliance
5. Update all documentation with "100% M008 compliant"

**Success Criteria**:
- ✅ 0 non-compliant tables (6,069/6,069 = 100%)
- ✅ 0 non-compliant columns (sampled validation)
- ✅ Feature Catalogue v3.2.0 verified
- ✅ All intelligence/mandate files updated

**Deliverables**:
- `M008_FINAL_COMPLIANCE_REPORT_20251213.md` (100% verification)
- Updated Feature Catalogue v3.2.0
- Updated documentation

**Timeline**: Day 6

---

## TIMELINE SUMMARY

| Phase | Duration | Timeline | Status |
|-------|----------|----------|--------|
| Phase 1: Audit | 4-6 hours | Day 1 | PENDING |
| Phase 2: Catalogue Validation | 2-3 hours | Day 1 (parallel) | PENDING |
| Phase 3: Planning | 3-4 hours | Day 2 | PENDING |
| Phase 4: Implementation | 12 hours | Days 3-4 | PENDING |
| Phase 5: Prevention | 4-6 hours | Day 5 | PENDING |
| Phase 6: Verification | 2-3 hours | Day 6 | PENDING |
| **TOTAL** | **27-34 hours** | **6 days** | **0% Complete** |

**Can Run in Parallel With**: Phase 0C REG table regeneration (currently in progress)

---

## COST ESTIMATE

### BigQuery Costs

**Table Renaming** (Option A):
- ALTER TABLE operations: Free
- Metadata updates: Free
- **Total**: $0

**Table Recreation** (Option B):
- Query processing: 269 tables × 1,479 GB / 6,069 tables × 269 = ~65 GB processed
- Cost: 65 GB × $5/TB = 65 GB × $0.000005/GB = **$0.33**
- Temporary storage: Negligible (deleted immediately)
- **Total**: ~$0.33

**Estimated Total Cost**: **$0** (if Option A) to **$0.33** (if Option B)

### Time Cost

**CE Time**: 27-34 hours over 6 days
**Cost**: $0 (internal labor)

---

## RISK ASSESSMENT

### Low Risk
- ✅ Table renaming is reversible
- ✅ No data loss (renaming preserves everything)
- ✅ Can validate before committing
- ✅ Minimal cost ($0-$0.33)

### Medium Risk
- ⚠️ Temporary disruption if external tools reference old names
- ⚠️ Mitigation: No known external dependencies (internal project only)

### High Risk
- ❌ None identified

---

## DEPENDENCIES

### Blocked By
- None (can start immediately)

### Blocks
- Feature Ledger generation (needs 100% M008 compliance)
- Production deployment (M008 is binding mandate)

### Parallel With
- Phase 0C: REG table regeneration (in progress)

---

## SUCCESS METRICS

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Compliant Tables | 5,800 (95.6%) | 6,069 (100%) | 🔴 Not Met |
| Non-Compliant Tables | 269 (4.4%) | 0 (0%) | 🔴 Not Met |
| Feature Catalogue Verified | No | Yes | 🔴 Not Met |
| Prevention Scripts Updated | 0 | 10+ | 🔴 Not Met |

---

## DELIVERABLES CHECKLIST

### Phase 1
- [ ] `M008_VIOLATION_REPORT_20251213.md`
- [ ] `M008_VIOLATION_PATTERNS.json`
- [ ] `scripts/audit_m008_table_compliance.py`

### Phase 2
- [ ] `intelligence/feature_catalogue_v3.2.0.json`
- [ ] `M008_COLUMN_VALIDATION_REPORT.md`
- [ ] `scripts/validate_m008_column_compliance.py`

### Phase 3
- [ ] `M008_REMEDIATION_PLAN_DETAILED.md`
- [ ] `M008_RENAME_MAPPING.json`
- [ ] `scripts/plan_m008_remediation.py`

### Phase 4
- [ ] All 269 tables remediated
- [ ] `M008_REMEDIATION_LOG.json`
- [ ] `scripts/execute_m008_remediation.py`

### Phase 5
- [ ] `scripts/m008_validation.py`
- [ ] Updated generation scripts (10+)
- [ ] Cloud Run pipeline M008 validation

### Phase 6
- [ ] `M008_FINAL_COMPLIANCE_REPORT_20251213.md`
- [ ] Feature Catalogue v3.2.0 (verified)
- [ ] All documentation updated

---

## AUTHORIZATION

**CE Recommendation**: APPROVED - Proceed with Phase 1 immediately

**Rationale**:
1. P0-CRITICAL: M008 is a binding mandate
2. Low risk, low cost ($0-$0.33)
3. Can run in parallel with Phase 0C
4. Required for 100% compliance before production

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: 2025-12-13
**Status**: AWAITING USER APPROVAL
