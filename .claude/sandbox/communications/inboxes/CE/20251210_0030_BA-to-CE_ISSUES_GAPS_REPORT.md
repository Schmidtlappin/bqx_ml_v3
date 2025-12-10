# BA Comprehensive Issues, Errors & Gaps Report

**Document Type**: ISSUES REPORT
**Date**: December 10, 2025 00:30
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH

---

## EXECUTIVE SUMMARY

Comprehensive report of all known issues, errors, and gaps identified during Phase 1.5 and Phase 2.5.

---

## PHASE 1.5 ISSUES (RESOLVED)

### I1: CSI IDX Source Tables Missing
- **Status**: RESOLVED (accepted by CE)
- **Impact**: 48 CSI tables could not be created
- **Resolution**: CE accepted 144/192 CSI tables as complete
- **Root Cause**: IDX source tables don't exist for cyc, ext, lag, div feature types

### I2: VAR Align Column Mismatch
- **Status**: RESOLVED
- **Impact**: var_align_* tables initially failed
- **Resolution**: Fixed column references (dir_*, pos_*, zscore_* instead of align_ratio_*, etc.)
- **Root Cause**: Assumed column naming pattern differed from actual schema

### I3: Window Size Mismatch
- **Status**: RESOLVED
- **Impact**: Align tables don't have window 2880
- **Resolution**: Created WINDOWS_ALIGN = [45, 90, 180, 360, 720, 1440] without 2880
- **Root Cause**: Align tables use different window set than agg tables

### I4: MKT Regime Table Naming
- **Status**: RESOLVED
- **Impact**: mkt_regime generation initially failed
- **Resolution**: Changed from regime_* to reg_* source tables with correct columns
- **Root Cause**: Multiple regime table naming patterns in BQ

---

## PHASE 2.5 ISSUES (ACTIVE)

### I5: Feature Ledger Performance
- **Status**: ACTIVE - CE APPROVED OPTIMIZATION
- **Impact**: Initial script runs 30-60 minutes
- **Resolution**: Implementing batch INFORMATION_SCHEMA query
- **Root Cause**: Individual `bq show --schema` calls for ~14,000 tables

### I6: SHAP Sample Generation
- **Status**: PENDING
- **Impact**: USER MANDATE requires 100K+ SHAP samples
- **Resolution**: TBD after ledger generation
- **Root Cause**: SHAP computation requires model training which is Phase 4

---

## KNOWN GAPS

### G1: Feature Selection Results
- **Gap**: Only EURUSD h15 has robust feature selection results
- **Impact**: Other pair/horizon combinations will have CANDIDATE status (not RETAINED)
- **Recommendation**: Run feature selection for all 196 models after ledger generation

### G2: SHAP Values
- **Gap**: SHAP importance values not available for most features
- **Impact**: final_status will be populated, but shap_importance mostly NULL
- **Recommendation**: Generate SHAP during Phase 4 model training

### G3: Full Schema Compliance
- **Gap**: CE schema specification includes fields not yet implemented:
  - cluster_id, group_id, pruned_stage, prune_reason
  - screen_score, ablation_delta
- **Impact**: Ledger will have simplified schema initially
- **Recommendation**: Enhance schema incrementally as data becomes available

---

## TECHNICAL DEBT

### T1: Background Processes
- **Issue**: Old CSI generation processes still showing as "running"
- **Impact**: Noise in process monitoring
- **Recommendation**: Clean up stale process references

### T2: Script Consolidation
- **Issue**: Multiple generation scripts with similar patterns
- **Impact**: Code duplication
- **Recommendation**: Future refactor into unified generation framework

---

## RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ledger row count < 1.27M | LOW | HIGH | Batch query approach will capture all columns |
| NULL final_status | NONE | HIGH | All features will have status (RETAINED/CANDIDATE) |
| Performance issues | MEDIUM | MEDIUM | Optimized batch query approved |
| Schema evolution | LOW | MEDIUM | Incremental enhancement plan |

---

## RECOMMENDATIONS

1. **Immediate**: Complete ledger with batch optimization (in progress)
2. **Short-term**: Run feature selection on additional pairs after GATE_2
3. **Medium-term**: Generate SHAP values during Phase 4 training
4. **Long-term**: Refactor generation scripts into unified framework

---

## ACTION ITEMS

| # | Action | Owner | Status |
|---|--------|-------|--------|
| A1 | Implement batch query optimization | BA | IN PROGRESS |
| A2 | Restart feature ledger generation | BA | PENDING |
| A3 | Validate ledger row counts | BA | PENDING |
| A4 | Report GATE_2 completion | BA | PENDING |

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 10, 2025 00:30
**Status**: ISSUES REPORTED - OPTIMIZATION IN PROGRESS
