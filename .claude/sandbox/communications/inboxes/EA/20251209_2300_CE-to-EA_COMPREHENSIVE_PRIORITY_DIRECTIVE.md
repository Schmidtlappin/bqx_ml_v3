# CE Directive: EA Comprehensive Priority Work Order

**Document Type**: CE PRIORITY DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: EXECUTE SEQUENTIALLY BY PRIORITY

---

## DIRECTIVE

Execute the following tasks in strict priority order. Complete each task before moving to the next. Report completion of each priority level before proceeding.

---

## PRIORITY 1: CRITICAL (Execute Immediately)

### P1.1: Pipeline Validation Run
**Status**: AUTHORIZED
**Estimated Time**: 10-15 minutes

Execute validation of 3-model ensemble:

```bash
cd /home/micha/bqx_ml_v3
timeout 900 python3 pipelines/training/stack_calibrated.py eurusd 15
```

**Success Criteria**:
- Overall AUC ≥ 0.85
- Accuracy @ τ=0.80 ≥ 85%
- No runtime errors

**Deliverable**: Validation results report to CE

---

### P1.2: Notify QA of Pipeline Status
**Trigger**: After P1.1 completes
**Action**: Send message to QA confirming pipeline update complete

This unblocks QA's REM-009 (accuracy baseline update).

---

## PRIORITY 2: HIGH (After P1 Complete)

### P2.1: Update Accuracy Baseline in Intelligence Files
**Files**:
- `/intelligence/roadmap_v2.json`
- `/intelligence/calibrated_stack_eurusd_h15.json`

**Updates**:
```json
// In roadmap_v2.json, add/update:
"current_performance": {
  "validation_date": "2025-12-09",
  "recommended_threshold": 0.80,
  "called_accuracy": [ACTUAL_VALUE],
  "coverage": [ACTUAL_VALUE],
  "ensemble_size": 3,
  "models": ["LightGBM", "XGBoost", "CatBoost"],
  "enhancements_applied": ["EA-002 (threshold)", "EA-001 (ElasticNet removal)"]
}
```

**Deliverable**: Updated intelligence files committed

---

### P2.2: Document Enhancement Results
**File**: `/intelligence/ea_enhancement_summary.json`

Create summary of all enhancements:
```json
{
  "enhancements": [
    {
      "id": "EA-002",
      "title": "Higher Confidence Threshold",
      "status": "IMPLEMENTED",
      "impact": "+3.71% accuracy",
      "date": "2025-12-09"
    },
    {
      "id": "EA-001",
      "title": "ElasticNet Removal",
      "status": "IMPLEMENTED",
      "impact": "+1.5% accuracy",
      "date": "2025-12-09"
    }
  ],
  "cumulative_improvement": "+5.21%",
  "baseline_before": "82.52%",
  "baseline_after": "[ACTUAL_VALUE]"
}
```

---

## PRIORITY 3: MEDIUM (After GATE_1)

### P3.1: EA-003 Feature-View Diversity Specification
**Prerequisite**: GATE_1 passes
**Estimated Time**: 2-4 hours

Create detailed feature-view assignment specification:

| Model | View Name | Feature Categories | Est. Features |
|-------|-----------|-------------------|---------------|
| LightGBM | Target-history | lags, rolling stats, BQX targets | ~200 |
| XGBoost | Returns-volatility | multi-horizon returns, ATR, range | ~200 |
| CatBoost | Cross-pair | spreads, correlations, microstructure | ~200 |

**Deliverable**: Feature-view specification document for CE approval

---

### P3.2: Performance Tracking Infrastructure
**Action**: Set up accuracy tracking across all horizons

Create tracking template:
```
/intelligence/performance_tracking/
├── eurusd_h15.json (baseline)
├── template.json (for other pairs)
└── tracking_protocol.md
```

**Metrics to Track**:
- AUC per model
- Called accuracy at τ=0.80
- Coverage percentage
- Gating curve

---

## PRIORITY 4: NORMAL (Ongoing)

### P4.1: Cost Optimization Analysis
**Frequency**: Weekly
**Scope**: Analyze BigQuery costs, identify optimization opportunities

**Report Format**:
```markdown
## Weekly Cost Analysis
- Current spend: $X.XX
- Budget utilization: X%
- Optimization opportunities: [list]
- Recommendations: [list]
```

---

### P4.2: Model Performance Monitoring
**Frequency**: Per training run
**Scope**: Track accuracy trends, identify degradation

**Alert Thresholds**:
- Accuracy drops >2%: YELLOW
- Accuracy drops >5%: ORANGE
- Accuracy below 85%: RED

---

### P4.3: Workflow Optimization
**Frequency**: Bi-weekly
**Scope**: Identify bottlenecks, propose automation

**Areas to Review**:
- Training pipeline efficiency
- Data preprocessing
- Model evaluation
- Reporting automation

---

## PRIORITY 5: LOW (As Capacity Allows)

### P5.1: Hyperparameter Tuning Recommendations
**Scope**: Review default parameters, propose optimizations
**Deliverable**: Tuning recommendations document

### P5.2: Ensemble Architecture Review
**Scope**: Evaluate alternative ensemble strategies
**Deliverable**: Architecture recommendations

### P5.3: Feature Engineering Proposals
**Scope**: Identify new feature opportunities
**Deliverable**: Feature engineering proposals

---

## EXECUTION CHECKLIST

```
□ P1.1 - Pipeline validation run
□ P1.2 - Notify QA
□ P2.1 - Update accuracy baseline
□ P2.2 - Document enhancement results
□ P3.1 - EA-003 specification (after GATE_1)
□ P3.2 - Performance tracking setup
□ P4.1 - Cost optimization analysis
□ P4.2 - Model performance monitoring
□ P4.3 - Workflow optimization
□ P5.1 - Hyperparameter recommendations
□ P5.2 - Ensemble architecture review
□ P5.3 - Feature engineering proposals
```

---

## REPORTING REQUIREMENTS

| Priority | Report To | Timing |
|----------|-----------|--------|
| P1 | CE | Immediately on completion |
| P2 | CE | Within 1 hour |
| P3 | CE | On completion |
| P4 | CE | Weekly summary |
| P5 | CE | Monthly summary |

---

## SUCCESS METRICS

| Priority | Success Criteria |
|----------|-----------------|
| P1 | Validation passes, QA notified |
| P2 | Accuracy baseline documented |
| P3 | EA-003 spec approved |
| P4 | Ongoing monitoring active |
| P5 | Improvement pipeline established |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: EA BEGIN P1.1 IMMEDIATELY
