# M008 Phase 4C: Complete Violation Inventory

**Date**: 2025-12-13 21:15 UTC
**Investigator**: EA (Enhancement Assistant)
**Status**: ✅ INVESTIGATION COMPLETE
**Total Violations**: 1,968 tables (33.8% of 5,817 total)

---

## EXECUTIVE SUMMARY

**All 1,968 M008 violations have been categorized and inventoried.**

### Violation Categories

| Category | Count | Violation Type | Remediation Strategy |
|----------|-------|----------------|---------------------|
| COV | 1,596 | Missing variant identifier | Rename: add `_bqx_` or `_idx_` |
| LAG | 224 | Window suffix in table name | Consolidate or rename |
| REGIME | 112 | Mixed (window suffix + missing variant) | Rename: remove suffix, add variant |
| TMP | 28 | Missing variant identifier | Rename: add `_bqx_` or `_idx_` |
| VAR | 7 | Missing variant identifier | Rename: add `_bqx_` or `_idx_` |
| MKT | 1 | Extra suffix | Keep as exception OR rename |
| **TOTAL** | **1,968** | | |

---

## DETAILED BREAKDOWN

### 1. COV Tables (1,596 violations)

**Pattern Violation**: Missing variant identifier

**Current**: `cov_{feature}_{pair1}_{pair2}` (4 parts)
**Required**: `cov_{feature}_{variant}_{pair1}_{pair2}` (5 parts)

**Examples**:
```
cov_agg_audcad_audchf   →  cov_agg_bqx_audcad_audchf
cov_align_eurusd_gbpusd →  cov_align_idx_eurusd_gbpusd
cov_mom_usdjpy_eurjpy   →  cov_mom_bqx_usdjpy_eurjpy
```

**Feature Types Affected**:
- agg, align, mom, vol, reg, lag, regime (all COV-compatible features)

**Remediation**:
1. Sample 10 COV tables to determine BQX vs IDX data source
2. If homogeneous (all BQX or all IDX), bulk rename with single variant
3. If mixed, create inventory and rename individually
4. **Cost**: $0 (renames are free)
5. **Duration**: 2 days

---

### 2. LAG Tables (224 violations)

**Pattern Violation**: Window suffix in table name

**Current Patterns**:
- `lag_{pair}_{window}` - 56 tables (e.g., `lag_audcad_45`)
- `lag_bqx_{pair}_{window}` - 112 tables (e.g., `lag_bqx_audcad_45`)
- `lag_idx_{pair}_{window}` - 56 tables (e.g., `lag_audcad_90` implies IDX)

**Required**: `lag_{variant}_{pair}` (3 parts, windows as columns)

**Issue**: LAG features for different windows (45, 90) are in separate tables instead of columns within a single table.

**Remediation Options**:

**Option A: Consolidate** (Recommended)
```
Before:
- lag_audcad_45 (56 tables, window=45)
- lag_audcad_90 (56 tables, window=90)
- lag_bqx_audcad_45 (56 tables, window=45)
- lag_bqx_audcad_90 (56 tables, window=90)

After:
- lag_idx_audcad (columns: lag_45, lag_90, etc.)
- lag_bqx_audcad (columns: lag_bqx_45, lag_bqx_90, etc.)

Result: 224 tables → 56 tables
```

**Option B: Rename with Exception**
```
Before: lag_audcad_45
After:  lag_idx_audcad_w45 (add variant, keep window suffix)

Result: 224 tables → 224 tables (but M008 compliant with exception)
```

**Cost**: Option A = $5-10 | Option B = $0
**Duration**: Option A = 3-5 days | Option B = 1 day

---

### 3. REGIME Tables (112 violations)

**Pattern Violations**: Mixed

#### Type 1: Window Suffix (56 tables)
**Current**: `regime_bqx_{pair}_{window}` (4 parts)
**Required**: `regime_bqx_{pair}` (3 parts)

**Examples**:
```
regime_bqx_audcad_45  →  regime_bqx_audcad (consolidate windows to columns)
regime_bqx_eurusd_90  →  regime_bqx_eurusd (consolidate windows to columns)
```

#### Type 2: Missing Variant (56 tables)
**Current**: `regime_{pair}_{window}` (3 parts, but wrong structure)
**Required**: `regime_idx_{pair}` OR `regime_bqx_{pair}` (3 parts, correct structure)

**Examples**:
```
regime_audcad_45  →  regime_idx_audcad (add variant, remove window)
regime_eurusd_90  →  regime_idx_eurusd (add variant, remove window)
```

**Remediation Strategy**:

**Same as LAG tables** - need to consolidate windows:
1. For each pair, consolidate `regime_{pair}_45` + `regime_{pair}_90` → `regime_idx_{pair}`
2. For each pair, consolidate `regime_bqx_{pair}_45` + `regime_bqx_{pair}_90` → `regime_bqx_{pair}`
3. **Cost**: $2-5 (similar to LAG consolidation but smaller tables)
4. **Duration**: 2-3 days

---

### 4. TMP Tables (28 violations)

**Pattern Violation**: Missing variant identifier

**Current**: `tmp_{pair}` (2 parts)
**Required**: `tmp_{variant}_{pair}` (3 parts)

**Examples**:
```
tmp_audcad  →  tmp_bqx_audcad  OR  tmp_idx_audcad
tmp_eurusd  →  tmp_bqx_eurusd  OR  tmp_idx_eurusd
tmp_gbpusd  →  tmp_bqx_gbpusd  OR  tmp_idx_gbpusd
```

**Remediation**:
1. Sample 5 TMP tables to determine data source (BQX vs IDX)
2. Rename all 28 tables with correct variant
3. **Cost**: $0 (renames are free)
4. **Duration**: 1 day

---

### 5. VAR Tables (7 violations)

**Pattern Violation**: Missing variant identifier

**Current**: `var_corr_{currency}` (3 parts)
**Required**: `var_corr_{variant}_{currency}` (4 parts)

**Violations**:
```
var_corr_aud  →  var_corr_bqx_aud
var_corr_cad  →  var_corr_bqx_cad
var_corr_chf  →  var_corr_bqx_chf
var_corr_eur  →  var_corr_bqx_eur
var_corr_gbp  →  var_corr_bqx_gbp
var_corr_jpy  →  var_corr_bqx_jpy
var_corr_usd  →  var_corr_bqx_usd
```

**Remediation**:
1. Sample 2 VAR tables to verify data source
2. Rename all 7 tables
3. **Cost**: $0 (renames are free)
4. **Duration**: 1 hour

---

### 6. MKT Table (1 violation)

**Pattern Violation**: Extra suffix

**Current**: `mkt_reg_bqx_summary` (4 parts)
**Required**: `mkt_reg_bqx` (3 parts)

**Remediation Options**:
- **Option A**: Keep as exception (allow `_summary` suffix for aggregate tables)
- **Option B**: Rename to `mkt_reg_bqx` (may conflict with existing table)
- **Option C**: Delete if unused

**EA Recommendation**: Option A (single exception vs mandate change)

---

## CONSOLIDATED REMEDIATION STRATEGY

### Phase 4C.1: Simple Renames (1-2 days)
**Tables**: 1,596 COV + 28 TMP + 7 VAR = 1,631 tables
**Cost**: $0
**Operations**:
1. Sample 15 tables (10 COV, 5 TMP) to determine variant
2. Bulk rename script execution
3. QA validation (sample 5%)

### Phase 4C.2: Window Consolidations (3-5 days)
**Tables**: 224 LAG + 112 REGIME = 336 tables → 84 tables
**Cost**: $5-10
**Operations**:
1. Design consolidation query template
2. Pilot with 5 pairs (2 LAG + 2 REGIME + 1 combined validation)
3. Measure cost, validate row counts
4. Bulk execution for remaining 23 pairs
5. QA validation (100% row count checks)

### Phase 4C.3: Exception Handling (1 hour)
**Tables**: 1 MKT table
**Cost**: $0
**Operations**:
1. CE decision on MKT handling
2. Execute (keep/rename/delete)

---

## UPDATED COST & TIMELINE

### Conservative Approach
**Timeline**: 3 weeks
- Week 1: Planning + pilots + CE decisions
- Week 2: Execution (renames + consolidations)
- Week 3: QA validation + final audit

**Cost**: $5-15

### Optimized Approach
**Timeline**: 2 weeks
- Week 1: Planning + pilots + execution (parallel)
- Week 2: QA validation + final audit

**Cost**: $5-15

---

## IMPACT ON COMPREHENSIVE PLAN

**Original Plan** (without M008 Phase 4C):
- Phase 0: 1 day ✅
- Phases 1-9: 9-11 weeks
- **Total**: 9-11 weeks

**Revised Plan** (with M008 Phase 4C):
- Phase 0: 1 day ✅
- **Phase 4C: 2-3 weeks** ⬅️ NEW
- Phases 1-9: 9-11 weeks
- **Total**: 11-14 weeks (+2-3 weeks)

**Parallel Execution Option**:
- Some M008 Phase 4C work can overlap with Phase 2 (REG verification)
- Possible reduction: 11-12 weeks instead of 14

---

## RISK ASSESSMENT

### Low Risk (High Confidence)
1. ✅ Simple renames (1,631 tables): Minimal risk, reversible
2. ✅ Cost estimate: Conservative, based on BigQuery pricing
3. ✅ QA validation: Sample-based for renames, 100% for consolidations

### Medium Risk (Managed)
4. ⚠️ Window consolidations (336→84 tables): Complexity in JOIN logic
   - **Mitigation**: Pilot with 5 pairs first, validate thoroughly
5. ⚠️ Downstream dependencies: Unknown queries may break
   - **Mitigation**: 30-day grace period with views (if CE approves)

### Dependency Risks
6. ⚠️ CE decision delays: Waiting for 4 critical decisions
   - **Mitigation**: EA prepared 2-3 options per decision point
7. ⚠️ Data source ambiguity: COV/TMP/VAR variant unknown
   - **Mitigation**: Sampling 15 tables to determine empirically

---

## DELIVERABLES

1. ✅ **This Document**: Complete violation inventory
2. ⏳ **Rename Script**: Bulk rename for 1,631 tables (pending CE decisions)
3. ⏳ **Consolidation Script**: Window merge for 336 tables (pending LAG decision)
4. ⏳ **Validation Report**: Pre/post row count verification
5. ⏳ **M008 Compliance Certificate**: 100% compliance sign-off (QA + EA)

---

## NEXT STEPS

**Waiting on CE**:
1. Approval of M008 Phase 4C execution
2. Decision 1: LAG strategy (consolidate vs rename)
3. Decision 2: Transition period (30-day views vs immediate)
4. Decision 3: MKT table handling
5. Decision 4: M005 sequencing (block vs parallel)

**EA Ready to Execute** (upon approval):
1. Sample 15 tables to determine variants
2. Design consolidation queries
3. Create rename/consolidation scripts
4. Execute pilot (5 pairs)
5. Execute full rollout
6. Final M008 audit

---

**Investigation Status**: ✅ COMPLETE
**Awaiting**: CE Approval & Decisions

---

**Enhancement Assistant (EA)**
**M008 Phase 4C Investigation Complete**
**Ready for BA Execution Upon CE Approval**
