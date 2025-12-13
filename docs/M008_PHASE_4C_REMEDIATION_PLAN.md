# M008 Phase 4C: Table Naming Remediation Plan

**Date**: 2025-12-13 21:00 UTC
**Phase**: M008 Phase 4C - Table Name Compliance
**Owner**: BA (lead), EA (analysis), QA (validation)
**Priority**: P0-CRITICAL (blocks M005 work)
**Status**: ⏳ PENDING CE APPROVAL

---

## EXECUTIVE SUMMARY

**Discovery**: During Phase 1 preparation, EA discovered **1,968 tables (33.8%) are non-compliant** with M008 naming standard.

**Impact**:
- ❌ M008 compliance is **NOT 100%** as previously believed
- ❌ Non-compliant tables block M005 schema updates (cannot reliably parse table names)
- ❌ Cannot proceed with Phase 3-5 until M008 is 100% compliant

**Recommended Action**: Execute M008 Phase 4C remediation **before** M005 work begins.

---

## VIOLATION BREAKDOWN

### 1. COV Tables: Missing Variant Identifier (1,596 tables)

**Current Pattern**: `cov_{feature}_{pair1}_{pair2}` (4 parts)
**M008 Required**: `cov_{feature}_{variant}_{pair1}_{pair2}` (5 parts)

**Examples**:
```
Current:  cov_agg_audcad_audchf
Required: cov_agg_bqx_audcad_audchf  OR  cov_agg_idx_audcad_audchf
```

**Issue**: Cannot determine if covariance is calculated from BQX or IDX values
- M007 (Semantic Compatibility) **requires** variant separation
- Mixing BQX and IDX in comparisons is **semantically invalid**

**Remediation Strategy**:
1. Query 5 sample COV tables to determine actual data source
2. If all COV tables use BQX values → rename all to `cov_{feature}_bqx_{pair1}_{pair2}`
3. If mixed → create inventory, rename individually
4. **Cost**: $0 (table renames are free in BigQuery)
5. **Duration**: 2-3 days (scripted bulk rename)

**Critical Decision Required**:
- Are current COV tables BQX-only, IDX-only, or mixed?
- **EA Hypothesis**: All COV tables likely use BQX values (user preference for momentum-based features)
- **Verification Required**: Query schema/data of `cov_agg_audcad_audchf` to confirm column names

---

### 2. LAG Tables: Window Suffix in Table Name (224 tables)

**Current Patterns**:
- `lag_{pair}_{window}` - 56 tables (e.g., `lag_audcad_45`, `lag_audcad_90`)
- `lag_bqx_{pair}_{window}` - 112 tables (e.g., `lag_bqx_audcad_45`, `lag_bqx_audcad_w45`)
- `lag_idx_{pair}` - 56 tables (M008 compliant, but inconsistent with above)

**M008 Required**: `lag_{variant}_{pair}` (3 parts, windows as COLUMNS not table names)

**Examples**:
```
Current:  lag_audcad_45, lag_audcad_90 (2 separate tables)
Required: lag_idx_audcad (1 table with columns: lag_45, lag_90, etc.)
```

**Issue**: LAG features for different windows are in separate tables instead of columns
- This violates the feature matrix architecture
- Creates 224 tables when 56 would suffice
- Cannot extract LAG data efficiently (need to union 4-8 tables per pair)

**Remediation Strategy**:

**Option A: Consolidate LAG Tables** (Recommended by EA)
1. For each pair, create new tables:
   - `lag_idx_{pair}`: Consolidate all `lag_{pair}_{window}` tables
   - `lag_bqx_{pair}`: Consolidate all `lag_bqx_{pair}_{window}` tables
2. Merge columns from multiple source tables into single wide table
3. Delete old window-specific tables
4. **Cost**: $5-10 (BigQuery compute for 56 pair consolidations)
5. **Duration**: 3-5 days (design + implementation + validation)
6. **Table Count Change**: 224 → 56 (reduce by 168 tables)

**Option B: Rename LAG Tables to Include Window**
1. Accept that LAG tables have window suffixes (deviation from M008)
2. Rename to: `lag_{variant}_{pair}_w{window}`
3. Update M008 mandate to allow window suffixes for LAG tables
4. **Cost**: $0 (renames are free)
5. **Duration**: 1 day (scripted rename)
6. **Table Count Change**: 224 → 224 (no reduction)

**CE Decision Required**: Option A (consolidate) or Option B (rename exception)?

---

### 3. VAR Tables: Missing Variant Identifier (7 tables)

**Current Pattern**: `var_corr_{currency}` (3 parts)
**M008 Required**: `var_corr_{variant}_{currency}` (4 parts)

**Violations**:
```
var_corr_aud  →  var_corr_bqx_aud  OR  var_corr_idx_aud
var_corr_cad  →  var_corr_bqx_cad  OR  var_corr_idx_cad
var_corr_chf  →  var_corr_bqx_chf  OR  var_corr_idx_chf
var_corr_eur  →  var_corr_bqx_eur  OR  var_corr_idx_eur
var_corr_gbp  →  var_corr_bqx_gbp  OR  var_corr_idx_gbp
var_corr_jpy  →  var_corr_bqx_jpy  OR  var_corr_idx_jpy
var_corr_usd  →  var_corr_bqx_usd  OR  var_corr_idx_usd
```

**Remediation Strategy**:
1. Query schema to determine BQX vs IDX source
2. Rename all 7 tables with correct variant
3. **Cost**: $0 (renames are free)
4. **Duration**: 1 hour (manual verification + scripted rename)

---

### 4. MKT Table: Extra Suffix (1 table)

**Current**: `mkt_reg_bqx_summary`
**M008 Pattern**: `mkt_{feature}_{variant}` (3 parts max)
**Issue**: Has extra `_summary` suffix

**Options**:
1. **Rename** to `mkt_reg_bqx` (may conflict with existing table)
2. **Delete** if redundant/unused
3. **Keep** and update M008 to allow `_summary` suffix for aggregation tables

**CE Decision Required**: Keep, rename, or delete?

---

## ADDITIONAL VIOLATIONS (Primary Tables)

**Count**: 364 primary table violations (excluding LAG)
**Status**: Requires further investigation

**Possible Causes**:
- Window suffixes in other table types (agg, mom, vol, etc.)
- Missing variant identifiers
- Incorrect part ordering

**Action Required**:
1. EA to investigate remaining 364 violations
2. Categorize by violation type
3. Create remediation sub-plan

---

## REMEDIATION TIMELINE

### Conservative Approach (Sequential)

**Week 1**:
- Day 1-2: EA investigation of all violation patterns
- Day 3: CE decision on LAG strategy (consolidate vs rename)
- Day 4-5: BA design LAG consolidation (if Option A)

**Week 2**:
- Day 1-3: BA implement COV variant addition (1,596 renames)
- Day 4-5: BA implement LAG remediation (56-224 operations)

**Week 3**:
- Day 1: BA implement VAR/MKT fixes (8 renames)
- Day 2-3: BA address remaining 364 primary violations
- Day 4: QA validation (sample 10% of renamed tables)
- Day 5: EA final M008 compliance audit

**Total**: 3 weeks

### Optimized Approach (Parallel)

**Week 1**:
- Day 1: EA investigation + CE decisions
- Day 2-5: BA parallel execution:
  - Thread 1: COV renames (1,596 tables)
  - Thread 2: LAG remediation (56-224 operations)
  - Thread 3: VAR/MKT fixes (8 tables)

**Week 2**:
- Day 1-3: BA address remaining 364 primary violations
- Day 4: QA validation (comprehensive)
- Day 5: EA final audit + certification

**Total**: 2 weeks

---

## COST ESTIMATE

| Component | Tables | Operation | Cost |
|-----------|--------|-----------|------|
| COV renames | 1,596 | Rename (free) | $0 |
| LAG consolidation (Option A) | 224→56 | Merge + delete | $5-10 |
| LAG renames (Option B) | 224 | Rename (free) | $0 |
| VAR renames | 7 | Rename (free) | $0 |
| MKT rename | 1 | Rename (free) | $0 |
| Primary investigation | 364 | TBD | $0-5 |
| **TOTAL (Option A)** | 1,968+ | | **$5-15** |
| **TOTAL (Option B)** | 1,968+ | | **$0-5** |

---

## RISK ASSESSMENT

### High-Confidence Risks (Mitigated)
1. **Breaking Change Risk**: Renaming 1,968 tables may break downstream queries
   - **Mitigation**: Create views with old names pointing to new tables (grace period)
   - **Duration**: 30-day transition period

2. **Data Loss Risk**: Table consolidation (LAG Option A) may lose data
   - **Mitigation**: Validate row counts pre/post consolidation
   - **Rollback**: Keep source tables until validation complete

3. **Cost Overrun Risk**: LAG consolidation may exceed $10 estimate
   - **Mitigation**: Pilot with 5 pairs, measure cost, extrapolate
   - **Gate**: If pilot cost >$2, escalate to CE before full rollout

### Medium Risks (Managed)
4. **Timeline Risk**: 364 primary violations may take longer than estimated
   - **Mitigation**: Prioritize COV/LAG/VAR (1,827 tables), defer primary if needed

5. **M008 Interpretation Risk**: Current naming may be intentional deviation
   - **Mitigation**: CE final decision on all ambiguous cases

---

## CRITICAL DECISIONS REQUIRED FROM CE

### Decision 1: LAG Table Strategy
- [ ] **Option A**: Consolidate 224 LAG tables → 56 tables (cost: $5-10, M008 compliant)
- [ ] **Option B**: Rename with window suffix exception (cost: $0, M008 deviation)
- [ ] **Option C**: Defer LAG remediation, proceed with COV/VAR only

**Recommendation**: Option A (consolidation aligns with feature matrix architecture)

### Decision 2: MKT Table `mkt_reg_bqx_summary`
- [ ] **Rename** to `mkt_reg_bqx` (may conflict)
- [ ] **Delete** if unused
- [ ] **Keep** and allow `_summary` suffix exception

**Recommendation**: Keep (1 table exception vs architectural change)

### Decision 3: Transition Period
- [ ] **30-day grace period**: Create views with old names for backward compatibility
- [ ] **Immediate cutover**: No views, update all downstream queries immediately
- [ ] **Permanent views**: Keep old name views forever (not recommended)

**Recommendation**: 30-day grace period with views

### Decision 4: Sequencing
- [ ] **Block M005 work**: Complete M008 Phase 4C before any M005 phases
- [ ] **Parallel execution**: Allow M005 REG verification (Phase 2) during M008 remediation
- [ ] **Defer M008**: Proceed with M005, circle back to M008 later (not recommended)

**Recommendation**: Block M005 work until M008 100% compliant

---

## SUCCESS CRITERIA

1. ✅ **100% M008 Compliance**: All 5,817 tables match M008 patterns
2. ✅ **Zero Data Loss**: Row counts preserved for all consolidated tables
3. ✅ **QA Validation**: 100% sample validation for renames, 10% for content
4. ✅ **Documentation Updated**: Intelligence files reflect new table names
5. ✅ **Grace Period Implemented**: Views created for backward compatibility (if approved)
6. ✅ **Cost ≤$15**: BigQuery compute within budget

---

## DELIVERABLES

1. **M008 Compliance Report**: Final audit showing 100% compliance
2. **Rename Inventory**: CSV with old_name → new_name mappings
3. **View Creation Scripts**: SQL scripts for backward compatibility views
4. **Updated Intelligence Files**: feature_catalogue.json with new table names
5. **M008 Phase 4C Certificate**: QA-signed compliance certification

---

## NEXT STEPS (UPON CE APPROVAL)

1. **Immediate** (Day 1):
   - EA: Investigate remaining 364 primary violations
   - BA: Sample 5 COV tables to verify BQX vs IDX data source
   - BA: Sample 5 LAG tables to assess consolidation complexity

2. **Day 2**:
   - CE: Provide decisions on 4 critical questions above
   - EA: Finalize remediation script designs
   - BA: Set up pilot environment for LAG consolidation (if Option A)

3. **Day 3-10**:
   - BA: Execute bulk renames and consolidations
   - QA: Continuous validation during execution
   - EA: Monitor progress, update documentation

4. **Day 11-14**:
   - QA: Final validation
   - EA: M008 compliance audit
   - CE: Review and approve M008 Phase 4C certificate

5. **Week 3**:
   - Proceed to M005 Phase 2 (REG schema verification)

---

## RECOMMENDATION

**EA Recommendation**: ✅ **APPROVE M008 Phase 4C with Option A (LAG consolidation)**

**Rationale**:
1. **Architectural Integrity**: Consolidating LAG tables aligns with feature matrix design
2. **Low Cost**: $5-15 is minimal for 100% M008 compliance
3. **Blocks Production**: Cannot proceed to production with 33.8% non-compliance
4. **Semantic Requirements**: COV/VAR variant identifiers **required** for M007 compliance
5. **Technical Debt**: Fixing now prevents compounding issues in M005 work

**Risk**: 2-week delay before M005 work begins
**Benefit**: 100% M008 compliance, clean foundation for all subsequent work

---

**Enhancement Assistant (EA)**
**BQX ML V3 Project - M008 Phase 4C Remediation**
**Prepared for CE Approval**
