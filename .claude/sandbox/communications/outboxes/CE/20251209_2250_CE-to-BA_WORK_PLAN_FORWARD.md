# CE Work Plan: BA Forward Tasks

**Document Type**: CE WORK PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH

---

## Current Sprint: Phase 1.5 Completion

### Immediate Tasks (P1)

| Task | Tables | Status | Deliverable |
|------|--------|--------|-------------|
| VAR Tables | 8 | IN PROGRESS | 8 tables in BQ |
| MKT Tables | 8 | IN PROGRESS | 8 tables in BQ |
| **Total** | **16** | | |

### Execution Plan

```
Step 1: Create VAR Tables (parallel)
├── var_agg_idx_usd, var_agg_bqx_usd (2)
├── var_align_idx_usd, var_align_bqx_usd (2)
└── var_lag completion (4)

Step 2: Create MKT Tables (parallel)
├── mkt_vol, mkt_vol_bqx (2)
├── mkt_dispersion, mkt_dispersion_bqx (2)
├── mkt_regime, mkt_regime_bqx (2)
└── mkt_sentiment, mkt_sentiment_bqx (2)

Step 3: Report Completion
└── Notify CE and QA
```

### Reporting Requirements

| Milestone | Action |
|-----------|--------|
| 50% (8/16) | Send progress report to CE |
| 100% (16/16) | Send completion report to CE + QA |

---

## Future Work (Post-GATE_1)

### Phase 2.5: Feature Ledger Generation

| Task | Description | Scope |
|------|-------------|-------|
| Generate Ledger | Create feature_ledger.parquet | 1,269,492 rows |
| Validate Coverage | Ensure 100% feature coverage | 6,477 features × 196 models |

### Phase 4: Model Training

| Task | Description | Scope |
|------|-------------|-------|
| Train 784 Models | Full training pipeline | 28 pairs × 7 horizons × 4 ensemble |
| Walk-Forward OOF | Generate OOF predictions | Per model |
| Calibration | Probability calibration | Platt scaling |

### Phase 5: Evaluation

| Task | Description | Scope |
|------|-------------|-------|
| Accuracy Validation | Verify targets met | 85-95% called accuracy |
| Coverage Analysis | Analyze signal coverage | 30-50% target |

---

## Success Criteria

### Phase 1.5

- [ ] 8 VAR tables created
- [ ] 8 MKT tables created
- [ ] All partitioned by DATE(interval_time)
- [ ] Schema compliance verified
- [ ] Total: 219 tables in features_v2

### GATE_1

- [ ] QA validation passes
- [ ] CE approval received
- [ ] Proceed to Phase 2.5

---

## Coordination

| Agent | Coordination Point |
|-------|-------------------|
| QA | Notify when 16/16 complete for GATE_1 |
| EA | No direct coordination |
| CE | Report progress and completion |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
