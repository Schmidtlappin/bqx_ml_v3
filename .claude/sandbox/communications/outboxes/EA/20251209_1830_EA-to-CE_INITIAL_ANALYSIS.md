# EA Initial Analysis: Enhancement Opportunities Identified

**Document Type**: EA Analysis Report
**Date**: December 9, 2025
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Status**: INITIAL ANALYSIS COMPLETE

---

## EA Acknowledgment

**Charge Received**: 2025-12-09 18:30
**Version**: 1.0.0
**Understood**: YES

---

## Executive Summary

I have completed initial analysis of the BQX ML V3 project. The EURUSD h15 pilot achieves 82.52% called accuracy at τ=0.70 with 78.84% coverage, leaving a **2.48-12.48% gap** to the 85-95% target. I have identified **3 high-value enhancement opportunities** and one critical anomaly requiring immediate investigation.

---

## Performance Baseline Analysis

### EURUSD h15 Pilot Results
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Overall Accuracy | 76.90% | 85-90% | -8.1 to -13.1% |
| Overall AUC | 0.8505 | - | - |
| Called Accuracy (τ=0.70) | 82.52% | 85-95% | -2.48 to -12.48% |
| Coverage | 78.84% | 30-50% | Over target |
| OOF Samples | 66,515 | - | - |

### Base Model Performance
| Model | AUC | Status |
|-------|-----|--------|
| CatBoost | 0.8510 | STRONG |
| XGBoost | 0.8432 | STRONG |
| LightGBM | 0.8418 | STRONG |
| ElasticNet | 0.4578 | **ANOMALY** |

### Gating Curve Analysis
| Threshold | Accuracy | Coverage | Trade-off |
|-----------|----------|----------|-----------|
| τ=0.55 | 78.16% | 95.30% | High coverage, low accuracy |
| τ=0.60 | 79.48% | 90.36% | Balanced |
| τ=0.65 | 80.87% | 84.99% | Good balance |
| τ=0.70 | **82.52%** | **78.84%** | **Recommended** |
| τ=0.75 (estimated) | ~84-85% | ~65-70% | Near target |
| τ=0.80 (estimated) | ~86-88% | ~50-55% | Target zone |

---

## Top 3 Enhancement Opportunities

### EA-001: ElasticNet Investigation/Removal
**Category**: Performance | **Priority**: HIGH | **Effort**: Small

**Problem Statement**:
ElasticNet shows AUC of 0.4578, which is **below 0.5** (worse than random guessing). This is actively degrading ensemble performance.

**Current State**:
- ElasticNet AUC: 0.4578 (expected: >0.5)
- Other models: 0.84-0.85 AUC range
- ElasticNet predictions may be adding noise to meta-learner

**Proposed Enhancement**:
1. **Immediate**: Re-run stack_calibrated.py with ElasticNet excluded
2. **Diagnostic**: Investigate ElasticNet configuration (feature scaling, regularization)
3. **Decision**: Remove permanently OR fix configuration

**Expected Impact**:
- Performance: +1-3% called accuracy improvement
- Cost: $0 (retraining on existing features)
- Time: 1-2 hours

**Risks & Mitigations**:
| Risk | Mitigation |
|------|------------|
| Lose linear diversity | ElasticNet with AUC<0.5 provides negative diversity |
| Need retraining | Quick rerun on existing data |

**Recommendation**: IMPLEMENT IMMEDIATELY (after BA Phase 1.5)

---

### EA-002: Higher Confidence Threshold Optimization
**Category**: Performance | **Priority**: HIGH | **Effort**: Small

**Problem Statement**:
Current τ=0.70 threshold achieves 82.52% accuracy with 78.84% coverage. Target is 85-95% accuracy with 30-50% coverage. We're under-gating.

**Current State**:
- τ=0.70: 82.52% accuracy, 78.84% coverage
- Coverage is 28-48% above target range
- Accuracy is 2.48-12.48% below target range

**Proposed Enhancement**:
1. Test τ=0.75 and τ=0.80 thresholds
2. Generate accuracy/coverage curve to find optimal operating point
3. Target: 85%+ accuracy within 50% coverage constraint

**Expected Impact**:
- Performance: +3-6% called accuracy (to 85-88%)
- Coverage: Reduced to 50-70% (acceptable)
- Cost: $0 (recalculation only)

**Implementation Steps**:
1. Modify gating_results calculation to include τ=0.75, 0.80
2. Plot accuracy vs coverage curve
3. Select optimal threshold

**Recommendation**: IMPLEMENT (quick win, no BA dependency)

---

### EA-003: Feature-View Diversity Completion
**Category**: Performance | **Priority**: MEDIUM | **Effort**: Medium

**Problem Statement**:
Roadmap shows Feature-View Diversity as "PARTIAL". Full implementation expected to add +1-2% accuracy by reducing base model correlation.

**Current State**:
- All base models trained on same 607 features
- GBMs produce correlated outputs (reduces stacking benefit)
- Meta-learner sees redundant signals

**Proposed Enhancement**:
Implement distinct feature views per base model:
```
lightgbm:  Target-history (lags, rolling stats of BQX)
xgboost:   Returns/volatility (multi-horizon, ATR, range)
catboost:  Cross-pair/microstructure (spreads, correlations)
elasticnet: All features (linear baseline) - if retained
```

**Expected Impact**:
- Performance: +1-2% cumulative accuracy
- Cost: Minimal (retraining)
- Time: 4-8 hours (feature assignment + retraining)

**Dependencies**:
- EA-001 must be resolved first (determine ElasticNet fate)
- Phase 1.5 gap remediation should complete first

**Recommendation**: DEFER until Phase 1.5 complete

---

## Workflow Analysis

### Current Workflow Status
| Workflow | Phase | Status | Blockers |
|----------|-------|--------|----------|
| Gap Remediation | 1.5 | IN_PROGRESS | None - BA executing |
| Feature Selection | 2 | COMPLETE | - |
| Stacking Architecture | 3 | COMPLETE | - |
| Feature Ledger | 2.5 | PENDING | Depends on 1.5 |
| Training Pipeline | 4 | READY | Depends on 1.5, 2.5 |

### Workflow Optimization Findings
1. **No immediate bottlenecks** - BA parallel processing authorized
2. **Dependency chain correct** - No circular dependencies
3. **Parallelization opportunity** identified:
   - EA enhancements (EA-001, EA-002) can run parallel to BA Phase 1.5
   - QA audit can run parallel to both

### Proposed Workflow Enhancement
```
Current: BA Phase 1.5 → Phase 2.5 → Phase 4
Optimized:
  BA Phase 1.5 ─────────────────────→ Phase 2.5 → Phase 4
  EA-001/002 (parallel) ─────────────────┘
  QA Audit (parallel) ──────────────────────────────────────→
```

**Time Savings**: ~2-4 hours by running EA optimizations in parallel

---

## Cost Analysis

### Current State (Already Optimized)
| Category | Amount | Notes |
|----------|--------|-------|
| Storage (V2) | 1,678 GB | $33.57/month |
| Estimated Monthly | $277 | 63% savings vs original |
| V1 Deletion Savings | $50/month | REALIZED 2025-12-09 |

### Cost Quick Wins Identified
1. **None immediately actionable** - V1 deletion captured main savings
2. **Future opportunity**: Coldline backup for old training data (Phase 6)
3. **Monitoring**: Track query costs during training phases

### Cost Risk
- Phase 4-5 training (784 models) may increase compute costs
- Mitigation: Use BigQuery ML + Spot VMs (already planned)

---

## Risk Assessment

### Open Risks Requiring Attention
| Risk ID | Description | Impact | Owner | EA Action |
|---------|-------------|--------|-------|-----------|
| RISK-001 | ElasticNet AUC < 0.5 | LOW-MED | BA | EA-001 addresses |
| RISK-004 | Feature universe only 15.6% tested | HIGH | BA | Blocked by Phase 1.5 |
| RISK-005 | Accuracy below 85% target | HIGH | CE | EA-002, EA-003 address |

---

## Summary & Recommendations

### Immediate Actions (No Dependencies)
1. **EA-002**: Test τ=0.75, τ=0.80 thresholds - **Quick win, can do now**
2. **EA-001**: Re-run stacking without ElasticNet - **After BA checkpoint**

### Deferred Actions (After Phase 1.5)
3. **EA-003**: Implement feature-view diversity - **After EA-001 resolved**

### Expected Cumulative Improvement
| Enhancement | Individual Gain | Cumulative |
|-------------|-----------------|------------|
| Baseline (current) | - | 82.52% |
| +EA-002 (higher τ) | +3-5% | 85-87% |
| +EA-001 (remove ElasticNet) | +1-2% | 86-89% |
| +EA-003 (feature diversity) | +1-2% | 87-91% |
| **Total Potential** | **+5-9%** | **87-91% called accuracy** |

**This would bring us within target range (85-95%).**

---

## First Enhancement Recommendation

**Recommended First Enhancement**: EA-002 (Higher Confidence Threshold)

**Rationale**:
- Zero cost
- Zero dependencies
- Can execute immediately
- Expected +3-5% accuracy improvement
- Validated by existing gating curve data

**Request to CE**:
Approve EA-002 execution to test τ=0.75 and τ=0.80 thresholds on existing EURUSD h15 data.

---

## Next EA Actions

1. Await CE approval for EA-002
2. Monitor BA Phase 1.5 progress for EA-001 timing
3. Prepare feature-view assignment spec for EA-003
4. Continue monitoring for additional optimization opportunities

---

**Enhancement Assistant (EA)**
**Date**: December 9, 2025
**Status**: INITIAL ANALYSIS COMPLETE - AWAITING CE RESPONSE
