# CE Master Remediation Plan

**Document Type**: CE MASTER PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**Status**: ACTIVE
**Version**: 1.0.0

---

## Executive Summary

This plan addresses all known issues, errors, and gaps identified across the BQX ML V3 project. Each item is assigned to an agent with clear deliverables and priorities.

---

## Remediation Matrix

| ID | Category | Description | Owner | Priority | Status |
|----|----------|-------------|-------|----------|--------|
| REM-001 | Data Gap | VAR tables (8 remaining) | BA | P1 | IN PROGRESS |
| REM-002 | Data Gap | MKT tables (8 remaining) | BA | P1 | IN PROGRESS |
| REM-003 | Issue | ElasticNet removal implementation | EA | P1 | APPROVED |
| REM-004 | Documentation | roadmap_v2.json CSI count (192→144) | QA | P2 | PENDING |
| REM-005 | Documentation | Gap total in roadmap (265→219) | QA | P2 | PENDING |
| REM-006 | Housekeeping | F3b misplaced tables cleanup (86) | QA | P3 | AUTHORIZED |
| REM-007 | Validation | GATE_1 pre-flight check | QA | P2 | BLOCKED (by REM-001,002) |
| REM-008 | Pipeline | Update stack_calibrated.py | EA | P2 | PENDING |
| REM-009 | Documentation | Update accuracy baseline in roadmap | QA | P2 | BLOCKED (by REM-008) |

---

## Phase 1: Immediate (Today)

### REM-001: VAR Tables (BA)
**Target**: Create 8 VAR tables
**Tables**:
- var_agg_idx_usd, var_agg_bqx_usd
- var_align_idx_usd, var_align_bqx_usd
- var_lag completion (4 tables)

**Deliverable**: 8 new tables in bqx_ml_v3_features_v2
**Validation**: Schema compliance, partition by DATE(interval_time)

### REM-002: MKT Tables (BA)
**Target**: Create 8 MKT tables
**Tables**:
- mkt_vol, mkt_vol_bqx
- mkt_dispersion, mkt_dispersion_bqx
- mkt_regime, mkt_regime_bqx
- mkt_sentiment, mkt_sentiment_bqx

**Deliverable**: 8 new tables in bqx_ml_v3_features_v2
**Validation**: Schema compliance, market-wide aggregation

### REM-003: ElasticNet Removal (EA)
**Target**: Remove ElasticNet from production ensemble
**Action**:
1. Approve EA-001 findings
2. Implement removal in stack_calibrated.py
3. Validate 3-model ensemble performance

**Deliverable**: Updated stack_calibrated.py, validation report
**Expected Impact**: +1.5% accuracy (86.23% → 87.73%)

---

## Phase 2: Short-term (24-48 hours)

### REM-004: Roadmap CSI Count (QA)
**Target**: Update roadmap_v2.json
**Current**: CSI = 192
**Correct**: CSI = 144 (IDX sources unavailable)

**File**: `/intelligence/roadmap_v2.json`
**Sections to update**:
- phase_1_5.milestones[0].count: 192 → 144
- phase_1_5.total_gap_tables: 265 → 219

### REM-005: Roadmap Gap Total (QA)
**Target**: Update all gap references
**Files to check**:
- roadmap_v2.json
- semantics.json
- feature_catalogue.json

**Correct values**:
- CSI: 144 (complete)
- VAR: 63
- MKT: 12
- Total: 219

### REM-007: GATE_1 Pre-flight (QA)
**Target**: Prepare GATE_1 validation checklist
**Prerequisites**: REM-001, REM-002 complete
**Checklist**:
- [ ] 219 tables exist in bqx_ml_v3_features_v2
- [ ] Schema compliance verified
- [ ] Row counts validated (10% sampling)
- [ ] No NULL in required columns
- [ ] Documentation aligned

### REM-008: Pipeline Update (EA)
**Target**: Implement ElasticNet removal in pipeline
**Prerequisites**: REM-003 CE approval
**Changes**:
```python
# stack_calibrated.py modifications:
# 1. Remove ElasticNet from base_models dict
# 2. Update meta_X to use 3 OOF columns
# 3. Update model artifacts paths
```

**Validation**: Re-run EURUSD h15, verify accuracy matches projection

### REM-009: Accuracy Baseline Update (QA)
**Target**: Update roadmap with new accuracy baseline
**Prerequisites**: REM-008 complete
**Updates**:
- recommended_threshold: 0.80
- baseline_accuracy: 87.73%
- ensemble_size: 3 models

---

## Phase 3: Low Priority (This Week)

### REM-006: F3b Cleanup (QA)
**Target**: Clean up 86 misplaced tables in source_v2
**Steps**:
1. Verify duplicates exist in features_v2
2. Delete confirmed duplicates
3. Archive training artifacts
4. Update table counts

**Estimated Savings**: ~$0.30/month (organizational benefit)

---

## Agent Assignments Summary

### BA (Build Agent)
| Task | Priority | ETA |
|------|----------|-----|
| REM-001 VAR tables | P1 | Today |
| REM-002 MKT tables | P1 | Today |

### QA (Quality Assurance)
| Task | Priority | ETA |
|------|----------|-----|
| REM-004 Roadmap CSI | P2 | Today |
| REM-005 Gap totals | P2 | Today |
| REM-007 GATE_1 prep | P2 | After BA |
| REM-009 Accuracy baseline | P2 | After EA |
| REM-006 F3b cleanup | P3 | This week |

### EA (Enhancement Assistant)
| Task | Priority | ETA |
|------|----------|-----|
| REM-003 ElasticNet removal | P1 | Today |
| REM-008 Pipeline update | P2 | After approval |

---

## Success Criteria

### Phase 1.5 Complete (GATE_1):
- [ ] 219 tables in bqx_ml_v3_features_v2
- [ ] Schema compliance 100%
- [ ] Documentation aligned

### Accuracy Target Met:
- [ ] Called accuracy ≥ 85% at optimal threshold
- [ ] Current: 87.73% projected ✓

### Cost Within Budget:
- [ ] Monthly cost < $277
- [ ] Current: $35.46 (12.8%) ✓

---

## Progress Tracking

| Date | Completed | Notes |
|------|-----------|-------|
| 2025-12-09 | CSI 144/144 | BA complete |
| 2025-12-09 | EA-002 | 86.23% achieved |
| 2025-12-09 | EA-001 | Analysis complete |
| TBD | VAR 8/8 | BA in progress |
| TBD | MKT 8/8 | BA in progress |
| TBD | GATE_1 | Pending |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Next Review**: After GATE_1 completion
