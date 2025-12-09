# BUILD AGENT CHARGE: V2.1 ROADMAP IMPLEMENTATION

**Document Type**: Official Agent Charge
**Date**: December 9, 2025
**From**: Chief Engineer (CE), BQX ML V3 Project
**To**: Build Agent (BA)
**Version**: 2.1.0
**Supersedes**: BQX_ML_V3_BUILDER_CHARGE.md (November 26, 2025)

---

## EXECUTIVE CHARGE

You are hereby charged with implementing the **V2.1 Roadmap** for BQX ML V3. This charge supersedes the previous v1 charge dated November 26, 2025. The architecture, targets, and methodology have significantly evolved.

**Core Mandate**: Build 784 production-ready ML models using Calibrated Probability Stacking with governance compliance.

---

## PROJECT STATE HANDOVER

### What Has Been Completed (Phases 1-3)

| Phase | Name | Status | Key Deliverables |
|-------|------|--------|------------------|
| 1 | Infrastructure | COMPLETE | V2 migration (4,888 tables), V1 deletion ($50/mo saved) |
| 2 | Feature Selection | COMPLETE | 399 stable features (Robust Group-First method) |
| 3 | Enhanced Stacking | COMPLETE | Pilot results: 82.52% called accuracy @ τ=0.70 |

### Pilot Results (EURUSD h15)

```
Overall Accuracy: 76.90%
Overall AUC:      0.8505
OOF Samples:      66,515

Base Model AUCs:
  - LightGBM:   0.8418
  - XGBoost:    0.8432
  - CatBoost:   0.8510
  - ElasticNet: 0.4578 (linear baseline)

Confidence Gating (τ thresholds):
  - τ=0.55: 78.16% acc, 95.30% coverage
  - τ=0.60: 79.48% acc, 90.36% coverage
  - τ=0.65: 80.87% acc, 84.99% coverage
  - τ=0.70: 82.52% acc, 78.84% coverage (RECOMMENDED)
```

### Critical Files

| File | Purpose |
|------|---------|
| `intelligence/roadmap_v2.json` | Authoritative roadmap specification |
| `intelligence/robust_feature_selection_eurusd_h15.json` | 399 stable features |
| `intelligence/calibrated_stack_eurusd_h15.json` | Pilot results |
| `pipelines/training/stack_calibrated.py` | Calibrated stacking pipeline |
| `pipelines/training/feature_selection_robust.py` | Group-first feature selection |
| `docs/roadmap_update_recommendations.md` | v2.1 governance source |

---

## YOUR IMPLEMENTATION RESPONSIBILITIES

### Phase 4: EURUSD Training Pipeline (READY)

**Objective**: Train EURUSD across all 7 horizons using calibrated stacking.

**Tasks**:
1. Run `stack_calibrated.py` for horizons h30, h45, h60, h75, h90, h105
2. Collect gating results for each horizon
3. Determine farthest horizon achieving ≥85% called accuracy
4. Document results in `intelligence/calibrated_stack_eurusd_h{N}.json`

**Expected Output**:
```
EURUSD × 7 horizons × 4 base models = 28 trained models
Per horizon: accuracy, AUC, recommended τ, coverage
```

### Phase 4.5: Governance Gate (NEW - v2.1)

**Objective**: Validation checkpoint before scaling to 784 models.

**Required Deliverables**:
1. `docs/governance/metrics_contract.md` - Define primary/secondary metrics
2. `docs/governance/persistence_contract.md` - Walk-forward stability requirements
3. `data/feature_ledger.parquet` - Full feature lineage accounting
4. `tests/leakage/` - Automated leakage guardrail tests
5. `docs/governance/phase_4_5_gate_checklist.md` - Gate passage documentation

**Gate Requirements**:
- [ ] Leakage audit tests pass
- [ ] Metric + persistence contracts locked
- [ ] Thresholds selected via nested evaluation
- [ ] Model registry + artifact storage working
- [ ] Pilot results stable across regimes

### Phase 5: Scale to 28 Pairs

**Only proceed after Phase 4.5 gate passes.**

**Execution Order**:
1. Major pairs (5): EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD
2. Cross pairs (15): EUR crosses, GBP crosses
3. Minor pairs (8): Remaining pairs

**Output**: 784 trained models (28 pairs × 7 horizons × 4 ensemble)

### Phase 6: Production Deployment

- Model serialization to GCS
- Inference pipeline
- Monitoring dashboard

---

## ARCHITECTURE SPECIFICATION

### Model Architecture (v2.1)

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT: 399 Stable Features               │
│                  (168 IDX + 270 BQX + 35 cov)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
     ┌────────────────┼────────────────┬────────────────┐
     ▼                ▼                ▼                ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐
│ LightGBM│    │ XGBoost │    │ CatBoost│    │ElasticNet│
│  View A │    │  View B │    │  View C │    │ All Feat │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬─────┘
     │              │              │               │
     │    [Walk-Forward OOF + Platt Calibration]  │
     │              │              │               │
     └──────────────┴──────┬───────┴───────────────┘
                           ▼
              ┌────────────────────────┐
              │   REGIME-AWARE         │
              │   META-LEARNER         │
              │  (LogReg + 6 regime    │
              │   features)            │
              └───────────┬────────────┘
                          ▼
              ┌────────────────────────┐
              │   CONFIDENCE GATING    │
              │   τ+ = 0.70 (UP)       │
              │   τ- = 0.30 (DOWN)     │
              │   else: NO SIGNAL      │
              └───────────┬────────────┘
                          ▼
              ┌────────────────────────┐
              │   OUTPUT:              │
              │   Direction + Conf %   │
              │   (Called accuracy:    │
              │    85-95% target)      │
              └────────────────────────┘
```

### Target Metrics

| Metric | Target | Priority |
|--------|--------|----------|
| Called Signal Accuracy | 85-95% | PRIMARY |
| Coverage | 30-50% | PRIMARY |
| Overall AUC | >0.80 | SECONDARY |
| Calibration (ECE) | <0.05 | MONITOR |

### Quality Gates (Updated from v1)

| Gate | V1 Target | V2.1 Target |
|------|-----------|-------------|
| Directional Accuracy | ≥55% | ≥85% (called) |
| R² Score | ≥0.35 | N/A (sign prediction) |
| Coverage | N/A | 30-50% |
| Persistence | N/A | Meet targets in ≥4/5 windows |

---

## COMMUNICATION PROTOCOL

### Reporting Structure

```
User (Project Owner)
       ↓
Chief Engineer (Strategic Direction)
       ↓
Build Agent (Implementation)
       ↓
[Artifacts: intelligence/, docs/governance/, tests/]
```

### Message Format

When reporting to CE, use this structure:

```markdown
## BA Status Report - [Date]

**Phase**: [Current phase]
**Task**: [Current task]
**Status**: [In Progress / Blocked / Complete]

### Progress
- [Bullet points of completed work]

### Results (if applicable)
- [Metrics, outputs]

### Blockers (if any)
- [Description of blocker]
- [Proposed resolution]

### Next Steps
- [Planned actions]
```

### Escalation Triggers

Escalate to CE when:
1. Accuracy target not met after 3 iterations
2. Leakage detected in pipeline
3. Resource/quota limits hit
4. Architectural decision required
5. Governance gate requirement unclear

---

## CRITICAL CONSTRAINTS

### DO NOT

1. Skip Phase 4.5 governance gate
2. Train all 784 models before validating EURUSD
3. Use centered windows or future-inclusive aggregations
4. Fit scalers on test data
5. Mark tasks complete without verification
6. Ignore low ElasticNet AUC (it's a linear baseline)

### DO

1. Generate OOF predictions with 30-interval embargo
2. Calibrate probabilities before stacking
3. Track both accuracy AND coverage
4. Document feature lineage
5. Test for leakage systematically
6. Report results per horizon, not just aggregate

---

## VERIFICATION COMMANDS

```bash
# Check V2 datasets
bq ls bqx-ml:bqx_ml_v3_features_v2

# Verify feature count matches 399
python3 -c "import json; f=json.load(open('intelligence/robust_feature_selection_eurusd_h15.json')); print(f'Features: {len(f[\"selected_features\"])}')"

# Check pilot results
cat intelligence/calibrated_stack_eurusd_h15.json | python3 -m json.tool

# Run stacking pipeline (example for h30)
timeout 1800 python3 pipelines/training/stack_calibrated.py --pair eurusd --horizon 30

# Validate no leakage
python3 -m pytest tests/leakage/ -v
```

---

## ACCEPTANCE CRITERIA

Phase 4 complete when:
- [ ] All 7 EURUSD horizons trained
- [ ] Results documented in intelligence/*.json
- [ ] Farthest viable horizon identified

Phase 4.5 complete when:
- [ ] All governance artifacts created
- [ ] Gate checklist passed
- [ ] CE approval received

Phase 5 complete when:
- [ ] 784 models trained
- [ ] All pairs achieve target metrics
- [ ] Model registry populated

---

## ACKNOWLEDGMENT REQUIRED

Upon receiving this charge, respond with:

```markdown
## BA Acknowledgment

**Charge Received**: [timestamp]
**Version**: 2.1.0
**Understood**: [YES/NO]

### Clarifications Needed (if any):
- [Questions]

### Proposed First Action:
- [What you will do first]
```

---

**Chief Engineer Signature**: Claude (CE, BQX ML V3)
**Date**: December 9, 2025
**Status**: CHARGE ISSUED - AWAITING BA ACKNOWLEDGMENT

---

## APPENDIX: V2.1 GOVERNANCE ARTIFACTS

Required artifacts for Phase 4.5 gate:

| Artifact | Purpose | Location |
|----------|---------|----------|
| metrics_contract.md | Define evaluation metrics | docs/governance/ |
| persistence_contract.md | Walk-forward stability | docs/governance/ |
| feature_ledger.parquet | Feature lineage | data/ |
| feature_ledger.md | Human-readable ledger | docs/governance/ |
| leakage_guardrails.md | Guardrail documentation | docs/governance/ |
| phase_4_5_gate_checklist.md | Gate passage | docs/governance/ |
| gating_policy.md | Threshold selection | docs/governance/ |
| calibration_report.md | Platt scaling analysis | docs/governance/ |

**END OF CHARGE DOCUMENT**
