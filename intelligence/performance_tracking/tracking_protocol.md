# Performance Tracking Protocol

**Version**: 1.0.0
**Created**: December 9, 2025
**Author**: Enhancement Assistant (EA)
**Status**: ACTIVE

---

## Overview

This protocol defines how model performance is tracked, monitored, and reported for the BQX ML V3 project.

---

## Metrics Tracked

### Primary Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Called Accuracy (τ=0.85) | Accuracy of high-confidence predictions | ≥85% |
| Coverage (τ=0.85) | Percentage of intervals with predictions | 30-50% |
| Overall AUC | Area under ROC curve | ≥0.85 |

### Per-Model Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| LightGBM AUC | Individual model AUC | <0.80 |
| XGBoost AUC | Individual model AUC | <0.80 |
| CatBoost AUC | Individual model AUC | <0.80 |

### Gating Curve

Track accuracy and coverage at each threshold:
- τ = 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85

---

## Alert Thresholds

| Level | Condition | Action |
|-------|-----------|--------|
| GREEN | No change or improvement | Continue monitoring |
| YELLOW | Accuracy drops >2% | Investigate cause |
| ORANGE | Accuracy drops >5% | Report to CE |
| RED | Accuracy below 85% | Escalate immediately |

---

## Tracking Frequency

| Event | Tracking Action |
|-------|-----------------|
| Training run | Update pair-horizon JSON file |
| Weekly | Generate summary report |
| Monthly | Trend analysis |
| Per enhancement | Before/after comparison |

---

## File Structure

```
/intelligence/performance_tracking/
├── tracking_protocol.md      # This file
├── template.json             # Template for new pairs
├── eurusd_h15.json          # EURUSD h15 baseline (first)
├── gbpusd_h15.json          # Future: GBPUSD
├── usdjpy_h15.json          # Future: USDJPY
└── ...                       # Other pair-horizons
```

---

## History Tracking

Each JSON file maintains a history array:

```json
"history": [
  {
    "date": "2025-12-09",
    "event": "Initial baseline",
    "accuracy_tau_85": 0.9166,
    "coverage_tau_85": 0.3827,
    "notes": "Post EA-001 and EA-002"
  },
  {
    "date": "2025-12-10",
    "event": "EA-003 applied",
    "accuracy_tau_85": 0.9250,
    "coverage_tau_85": 0.3900,
    "notes": "Feature-view diversity"
  }
]
```

---

## Reporting Format

### Per-Run Report

```markdown
## Performance Report: [PAIR] [HORIZON]
Date: [DATE]

### Model AUCs
| Model | AUC | Change |
|-------|-----|--------|
| LightGBM | X.XX | +/-X.XX |
| XGBoost | X.XX | +/-X.XX |
| CatBoost | X.XX | +/-X.XX |

### Operating Point (τ=0.85)
- Accuracy: XX.XX% (Δ: +/-X.XX%)
- Coverage: XX.XX% (Δ: +/-X.XX%)
- Signals: XXXXX

### Status: [GREEN/YELLOW/ORANGE/RED]
```

### Weekly Summary

```markdown
## Weekly Performance Summary
Week of: [DATE]

| Pair | Horizon | Accuracy | Coverage | Status |
|------|---------|----------|----------|--------|
| EURUSD | h15 | 91.66% | 38.27% | GREEN |
| ... | ... | ... | ... | ... |

### Alerts This Week
- [List any YELLOW/ORANGE/RED alerts]

### Recommendations
- [Any suggested actions]
```

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| EA | Update tracking files after runs |
| EA | Generate weekly summaries |
| QA | Validate tracking data accuracy |
| CE | Review alerts, approve actions |

---

## Integration

### After Training Run

1. Pipeline outputs metrics to `/tmp/`
2. EA reads metrics and updates JSON file
3. EA compares to baseline
4. EA generates alert if threshold breached
5. EA reports to CE if ORANGE or RED

### Automation (Future)

- Integrate tracking into `stack_calibrated.py`
- Auto-generate JSON updates
- Auto-send alerts

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2025-12-09 | 1.0.0 | Initial protocol |

---

**Enhancement Assistant (EA)**
**Date**: December 9, 2025
