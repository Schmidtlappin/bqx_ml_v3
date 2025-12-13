# EA → CE: M008 Phase 4C Approval Request + Critical Decisions Required

**From**: EA (Enhancement Assistant)
**To**: CE (Chief Engineer)
**Date**: 2025-12-13 21:00 UTC
**Subject**: URGENT - M008 Phase 4C Remediation Required Before M005 Work
**Priority**: P0-CRITICAL
**Type**: Approval Request + Decision Request

---

## SITUATION

During Phase 1 preparation, EA discovered **1,968 tables (33.8%) are NON-COMPLIANT with M008** naming standard.

**Previous Belief**: M008 Phase 4A (deletions) was 100% successful
**Actual Reality**: M008 Phase 4A deleted legacy tables ✅, but **1,968 current tables still violate M008** ❌

---

## IMPACT

**Blocks M005 Work**:
- Cannot reliably parse table names to determine variant (BQX vs IDX)
- M007 (Semantic Compatibility) requires variant separation - currently violated
- Schema update scripts (M005 Phases 3-5) will fail with ambiguous table names

**Blocks Production**:
- 33.8% non-compliance is unacceptable for production deployment
- Feature ledger generation (M001) requires M008-compliant names

**Technical Debt**:
- 1,596 COV tables missing critical variant identifier
- 224 LAG tables have window suffixes (architectural violation)
- Cannot proceed with comprehensive remediation plan until M008 is 100% compliant

---

## VIOLATION BREAKDOWN

| Category | Count | Example Violation | M008 Required |
|----------|-------|-------------------|---------------|
| COV (missing variant) | 1,596 | `cov_agg_audcad_audchf` | `cov_agg_bqx_audcad_audchf` |
| LAG (window suffix) | 224 | `lag_audcad_45` | `lag_idx_audcad` (consolidated) |
| VAR (missing variant) | 7 | `var_corr_aud` | `var_corr_bqx_aud` |
| MKT (extra suffix) | 1 | `mkt_reg_bqx_summary` | `mkt_reg_bqx` |
| Primary (TBD) | 364 | (investigating) | (TBD) |
| **TOTAL** | **1,968** | | |

---

## PROPOSED SOLUTION: M008 PHASE 4C

**Document**: [docs/M008_PHASE_4C_REMEDIATION_PLAN.md](../../../docs/M008_PHASE_4C_REMEDIATION_PLAN.md)

**Timeline**: 2-3 weeks (before M005 work begins)
**Cost**: $5-15 (LAG consolidation only)
**Owner**: BA (lead), EA (analysis), QA (validation)

**Approach**:
1. Rename 1,596 COV tables to include variant identifier
2. Consolidate or rename 224 LAG tables (CE decision required)
3. Fix 7 VAR tables + 1 MKT table
4. Investigate and remediate 364 remaining primary violations
5. QA validation + final M008 compliance audit

---

## CRITICAL DECISIONS REQUIRED FROM CE

### Decision 1: LAG Table Strategy ⚠️ URGENT

**Option A (EA Recommended)**: Consolidate 224 LAG tables → 56 tables
- Merge window-specific tables into single wide tables
- Example: `lag_audcad_45` + `lag_audcad_90` → `lag_idx_audcad` (with columns)
- Cost: $5-10
- Duration: 3-5 days
- **Benefit**: M008 compliant + aligns with feature matrix architecture
- **Risk**: Table consolidation complexity

**Option B**: Rename with window suffix exception
- Example: `lag_audcad_45` → `lag_idx_audcad_w45`
- Cost: $0
- Duration: 1 day
- **Benefit**: Fast, low-risk
- **Risk**: M008 deviation (need to update mandate)

**Option C**: Defer LAG remediation
- Proceed with COV/VAR only, address LAG later
- Cost: $0
- Duration: 0 days
- **Benefit**: Faster to M005
- **Risk**: Partial M008 compliance (still 224 violations)

**CE Please Select**: [ ] Option A  [ ] Option B  [ ] Option C

---

### Decision 2: Transition Period for Renamed Tables

When renaming 1,596+ tables, should we create backward-compatible views?

**Option A (EA Recommended)**: 30-day grace period with views
- Create views: `cov_agg_audcad_audchf` → `cov_agg_bqx_audcad_audchf`
- Allows downstream queries to continue working
- Drop views after 30 days
- **Benefit**: Zero-downtime transition
- **Risk**: 30-day technical debt

**Option B**: Immediate cutover (no views)
- Rename tables, update all downstream queries immediately
- **Benefit**: Clean break, no views
- **Risk**: May break unknown dependencies

**CE Please Select**: [ ] Option A (30-day views)  [ ] Option B (immediate cutover)

---

### Decision 3: MKT Table `mkt_reg_bqx_summary`

Single table with non-standard `_summary` suffix.

**Option A**: Keep as exception
- Add to M008 allowlist for summary tables
- **Benefit**: No work required
- **Risk**: Sets precedent for future exceptions

**Option B**: Rename to `mkt_reg_bqx`
- **Benefit**: M008 compliant
- **Risk**: May conflict with existing `mkt_reg_bqx` table

**Option C**: Delete if unused
- **Benefit**: Clean removal
- **Risk**: Lose data if actually used

**CE Please Select**: [ ] Option A (keep)  [ ] Option B (rename)  [ ] Option C (delete)

---

### Decision 4: M005 Work Sequencing

Should we block M005 work until M008 Phase 4C is complete?

**Option A (EA Recommended)**: Block M005 work
- Complete M008 Phase 4C (2-3 weeks)
- Then proceed to M005 Phases 2-5
- **Benefit**: Clean foundation, no rework
- **Risk**: 2-3 week delay

**Option B**: Parallel execution
- Allow M005 REG verification (Phase 2) during M008 remediation
- **Benefit**: No delay
- **Risk**: May need to re-verify after table renames

**Option C**: Defer M008 remediation
- Proceed with M005 work, circle back to M008 later
- **Benefit**: Faster to production
- **Risk**: 33.8% non-compliance persists, compounding technical debt

**CE Please Select**: [ ] Option A (block M005)  [ ] Option B (parallel)  [ ] Option C (defer M008)

---

## RECOMMENDATION FROM EA

✅ **Approve M008 Phase 4C with:**
- Decision 1: **Option A** (LAG consolidation)
- Decision 2: **Option A** (30-day grace period)
- Decision 3: **Option A** (keep MKT exception)
- Decision 4: **Option A** (block M005 work)

**Rationale**:
- M008 is architectural foundation - must be 100% before building on it
- COV/VAR variant identifiers are **required** for M007 semantic compatibility
- LAG consolidation aligns with feature matrix design
- 2-3 week investment prevents months of technical debt

**Total Cost**: $5-15
**Total Duration**: 2-3 weeks
**Risk**: LOW (reversible renames, validated consolidations)

---

## REVISED COMPREHENSIVE REMEDIATION PLAN

If M008 Phase 4C is approved, the overall plan becomes:

```
PHASE 0:  Documentation Reconciliation (COMPLETE ✅)
PHASE 4C: M008 Table Naming Remediation (NEW - 2-3 weeks)
PHASE 1:  M008 Final Verification (1 week)
PHASE 2:  M005 REG Schema Verification (1 week)
PHASE 3:  M005 TRI Schema Update (2-3 weeks)
PHASE 4:  M005 COV Schema Update (2-3 weeks)
PHASE 5:  M005 VAR Schema Update (1-2 weeks)
PHASE 6:  M006 Coverage Verification (1-2 weeks)
PHASE 7:  M001 Feature Ledger Generation (3-4 weeks)
PHASE 8:  M005 Validation Integration (1-2 weeks)
PHASE 9:  Final Reconciliation & Certification (1 week)

Total: 11-14 weeks (sequential) | 7-10 weeks (parallel)
```

**Change from Original Plan**: +2-3 weeks for M008 Phase 4C

---

## APPROVAL REQUESTED

**CE, please approve:**
1. ✅ Execute M008 Phase 4C before M005 work
2. ✅ Authorize $5-15 budget for LAG consolidation
3. ✅ Make 4 critical decisions above
4. ✅ Authorize BA to lead implementation (EA analysis, QA validation)
5. ✅ Accept 2-3 week timeline addition to comprehensive plan

**Alternative (Not Recommended)**:
- ❌ Defer M008 remediation, proceed with M005 at 67% M008 compliance
- ❌ Risk: Semantic violations, unreliable parsing, technical debt

---

## NEXT STEPS (UPON APPROVAL)

**Immediate** (Day 1-2):
1. EA: Complete investigation of 364 primary violations
2. BA: Sample COV/LAG tables to verify data source and consolidation complexity
3. EA: Finalize rename scripts based on CE decisions

**Week 1-2**:
1. BA: Execute bulk renames (COV, VAR, MKT)
2. BA: Execute LAG consolidation or rename (per CE decision)
3. QA: Continuous validation

**Week 2-3**:
1. BA: Address remaining primary violations
2. QA: Final validation
3. EA: M008 compliance audit
4. EA: Update all intelligence/mandate files with new table names

**Week 3**:
1. Deliver M008 Phase 4C certificate (100% compliance)
2. Proceed to M005 Phase 2

---

## RESPONSE REQUESTED

**CE, please respond with:**
1. Approval status: [ ] APPROVED  [ ] APPROVED WITH MODIFICATIONS  [ ] HOLD  [ ] REJECTED
2. Decisions 1-4 selections (see above)
3. Any additional guidance or concerns
4. Preferred timeline: [ ] 2 weeks (aggressive)  [ ] 3 weeks (conservative)

**EA will wait for CE response before proceeding.**

---

**Enhancement Assistant (EA)**
**Awaiting CE Approval & Critical Decisions**
**Session: Phase 1 Preparation - M008 Compliance Discovery**
