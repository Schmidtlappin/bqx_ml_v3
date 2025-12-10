# EA-003 Feature-View Diversity Specification

**Document Type**: ENHANCEMENT SPECIFICATION
**Date**: December 9, 2025
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Status**: SUBMITTED FOR APPROVAL

---

## Executive Summary

GATE_1 has passed (BA completed Phase 1.5). EA-003 Feature-View Diversity specification is ready for CE approval.

**Expected Impact**: +1-2% accuracy improvement (from 91.66% to 92-94%)

---

## Enhancement Overview

| Item | Value |
|------|-------|
| Enhancement ID | EA-003 |
| Title | Feature-View Diversity |
| Objective | Reduce base model correlation |
| Total Features | 607 stable |
| Features Per View | ~115-155 (mutually exclusive) |

---

## Feature View Assignments

### View 1: Target-History (LightGBM)
**Focus**: Temporal patterns, lags, rolling statistics

| Feature Group | Count | Type |
|---------------|-------|------|
| base_bqx/idx | 8 | BQX/IDX targets |
| lag_bqx/idx | 13 | Lagged values |
| aggregation_bqx/idx | 45 | Rolling stats |
| alignment_bqx/idx | 42 | Z-score alignment |
| cyclical | 3 | Cycle indicators |
| external | 4 | External positioning |
| **Total** | **115** | |

---

### View 2: Returns-Volatility (XGBoost)
**Focus**: Momentum, volatility, regime detection

| Feature Group | Count | Type |
|---------------|-------|------|
| momentum_bqx/idx | 49 | Momentum indicators |
| derivative_bqx/idx | 20 | Price derivatives |
| volatility_bqx/idx | 32 | Volatility measures |
| reversal_bqx/idx | 14 | Reversal signals |
| regime_bqx | 8 | Regime indicators |
| divergence_bqx/idx | 6 | Divergence signals |
| **Total** | **129** | |

---

### View 3: Cross-Pair Structure (CatBoost)
**Focus**: Cross-pair relationships, polynomial, microstructure

| Feature Group | Count | Type |
|---------------|-------|------|
| covariance | 24 | Cross-pair spreads |
| correlation | 1 | Cross-pair correlations |
| polynomial_bqx/idx | 72 | Polynomial regression |
| microstructure_bqx/idx | 13 | Microstructure |
| other | 45 | Miscellaneous IDX |
| **Total** | **155** | |

---

## Balance Analysis

| Model | Features | % of Total | Focus |
|-------|----------|------------|-------|
| LightGBM | 115 | 28.8% | Temporal/Lag |
| XGBoost | 129 | 32.3% | Momentum/Volatility |
| CatBoost | 155 | 38.8% | Structure/Cross-pair |
| **Total** | **399** | **100%** | |

---

## Success Criteria

| Metric | Current | Target | Minimum |
|--------|---------|--------|---------|
| Called Accuracy (τ=0.85) | 91.66% | ≥92.5% | ≥91.0% |
| Inter-Model Correlation | ~0.85 | <0.70 | <0.80 |
| Coverage | 38.27% | 35-45% | 30-50% |

---

## Implementation Plan

| Phase | Duration | Tasks |
|-------|----------|-------|
| Preparation | 1 hour | Generate feature lists, validate exclusivity |
| Pipeline Update | 2 hours | Modify stack_calibrated.py for views |
| Validation | 30 min | Run EURUSD h15, compare to baseline |

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Imbalanced views | LOW | Split is 115/129/155 |
| Missing critical features | MEDIUM | Each view has top features |
| Accuracy regression | LOW | Baseline fallback available |

---

## Specification File

Full specification available at:
`/intelligence/ea_003_feature_view_specification.json`

---

## Approval Request

**Action Required**: CE approval for EA-003 implementation

**Options**:
1. **APPROVE** - Proceed with implementation
2. **APPROVE WITH MODIFICATIONS** - Specify changes
3. **REJECT** - Provide rationale

---

**Enhancement Assistant (EA)**
**Date**: December 9, 2025
**Status**: AWAITING CE APPROVAL
