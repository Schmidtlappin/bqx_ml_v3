# CE Directive: Phase 2.5 BEGIN IMMEDIATELY

**Document Type**: CE EXECUTION DIRECTIVE
**Date**: December 9, 2025 23:50
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: CRITICAL

---

## DIRECTIVE: BEGIN PHASE 2.5 NOW

Phase 2.5 (Feature Ledger Generation) is the **critical path** to 784 models.

---

## Phase 2.5 Scope

### Deliverable
Generate `feature_ledger.parquet` with 100% coverage.

### Requirements (USER MANDATES)

| Requirement | Value | Source |
|-------------|-------|--------|
| Total Rows | 1,269,492 | 28 pairs × 7 horizons × 6,477 features |
| Coverage | 100% | USER MANDATE |
| SHAP Samples | 100,000+ | USER MANDATE (BINDING) |
| Stability Threshold | 50% | USER MANDATE (BINDING) |

### Schema

```
feature_name, source_table, feature_type, feature_scope, variant,
pair, horizon, model_type, cluster_id, group_id, pruned_stage,
prune_reason, screen_score, stability_freq, importance_mean,
importance_std, ablation_delta, final_status
```

---

## Execution Steps

1. **Create script**: `scripts/generate_feature_ledger.py`
2. **Enumerate features**: All 6,477 per pair-horizon
3. **Run feature selection**: 50% stability threshold
4. **Generate SHAP**: 100K+ samples for RETAINED features
5. **Output**: `feature_ledger.parquet`
6. **Report**: Completion to CE for GATE_2 trigger

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Row count | 1,269,492 exactly |
| NULL in final_status | 0 |
| RETAINED per model | 500-700 (estimated) |
| SHAP coverage | 100% of RETAINED |

---

## Timeline

| Step | Estimated |
|------|-----------|
| Script creation | 1-2 hours |
| Feature enumeration | 30 min |
| Selection + SHAP | 6-12 hours (parallelized) |
| Validation | 30 min |

---

## Coordination

| Agent | Action |
|-------|--------|
| QA | GATE_2 criteria ready, awaiting ledger |
| EA | EA-003 approved, queued after GATE_2 |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025 23:50
**Status**: PHASE 2.5 AUTHORIZED - BEGIN IMMEDIATELY
