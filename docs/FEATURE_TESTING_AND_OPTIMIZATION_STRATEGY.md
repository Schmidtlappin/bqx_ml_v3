# Feature Testing and Optimization Strategy for BQX ML V3

**Date**: November 27, 2025
**Objective**: Test ALL planned features, operationalize those that improve performance
**Target**: Maximize prediction accuracy through systematic feature evaluation

---

## ✅ REFINED UNDERSTANDING OF REQUIREMENTS

### User's Actual Expectation:
1. **Test Everything**: All discussed features must be evaluated
2. **Keep What Works**: Only operationalize performance-improving features
3. **Optimize Ruthlessly**: Remove features that add noise or complexity without benefit
4. **Performance First**: The goal is maximum accuracy, not maximum features

This is the **correct** interpretation - pragmatic optimization, not blind implementation.

---

## 🔬 SYSTEMATIC FEATURE TESTING FRAMEWORK

### Phase 1: Baseline Enhancement (Week 1)

#### Current Baseline:
- **12 Smart Dual Features**: R² = 0.7079
- **Single Model**: XGBoost

#### Testing Queue - Tier 1 (Highest Priority):
```python
tier_1_features = {
    'triangulation': {
        'count': 378,
        'expected_impact': '+3-5%',
        'test_first': ['EUR-GBP-USD', 'USD-JPY-EUR'],
        'decision_criteria': 'Keep if >1% improvement'
    },
    'correlation_network': {
        'count': 784,
        'expected_impact': '+4-6%',
        'test_first': ['Major pairs only (7x7 matrix)'],
        'decision_criteria': 'Keep if >2% improvement'
    },
    'extended_lags': {
        'count': 2800,
        'expected_impact': '+2-3%',
        'test_first': ['Lags 15-30 for EURUSD'],
        'decision_criteria': 'Keep if improves long-horizon accuracy'
    }
}
```

### Phase 2: Advanced Features (Week 2)

#### Testing Queue - Tier 2:
```python
tier_2_features = {
    'covariance_matrix': {
        'count': 378,
        'expected_impact': '+2-4%',
        'test_approach': 'PCA first, keep top 10 components'
    },
    'granger_causality': {
        'count': 784,
        'expected_impact': '+2-3%',
        'test_approach': 'Identify top 20 lead-lag pairs'
    },
    'technical_indicators': {
        'count': 420,
        'expected_impact': '+1-3%',
        'test_approach': 'Standard set (RSI, MACD, BB) first'
    },
    'market_microstructure': {
        'count': 500,
        'expected_impact': '+2-3%',
        'test_approach': 'If spread data available'
    }
}
```

### Phase 3: Complex Features (Week 3)

#### Testing Queue - Tier 3:
```python
tier_3_features = {
    'wavelets': {
        'count': 168,
        'expected_impact': '+1-2%',
        'test_approach': 'Frequency decomposition'
    },
    'regime_detection': {
        'count': 140,
        'expected_impact': '+2-3%',
        'test_approach': 'HMM states, volatility regimes'
    },
    'cross_asset': {
        'count': 200,
        'expected_impact': '+1-2%',
        'test_approach': 'If other asset data available'
    }
}
```

---

## 📊 FEATURE SELECTION METHODOLOGY

### Automated Feature Testing Pipeline:

```python
class FeatureTestingPipeline:
    """
    Systematic evaluation of all features
    """
    def __init__(self):
        self.baseline_score = 0.7079  # Current R²
        self.feature_performance = {}

    def test_feature_set(self, new_features, feature_name):
        """
        Test incremental value of new features
        """
        # 1. Baseline model (current 12 features)
        baseline_pred = self.baseline_model.predict(X_test)

        # 2. Enhanced model (12 + new features)
        X_enhanced = concat([X_baseline, new_features])
        enhanced_pred = self.enhanced_model.predict(X_enhanced)

        # 3. Measure improvement
        baseline_r2 = r2_score(y_test, baseline_pred)
        enhanced_r2 = r2_score(y_test, enhanced_pred)
        improvement = enhanced_r2 - baseline_r2

        # 4. Statistical significance test
        p_value = paired_t_test(baseline_pred, enhanced_pred)

        # 5. Decision
        keep_feature = (improvement > 0.01 and p_value < 0.05)

        # 6. Record results
        self.feature_performance[feature_name] = {
            'improvement': improvement,
            'p_value': p_value,
            'keep': keep_feature,
            'feature_count': new_features.shape[1],
            'complexity_cost': measure_training_time()
        }

        return keep_feature

    def optimize_feature_combination(self):
        """
        Find optimal combination of features
        """
        # Use recursive feature elimination
        # Or forward selection
        # Or genetic algorithm
        return optimal_features
```

---

## 🎯 PROGRESSIVE IMPROVEMENT TARGETS

### Realistic Performance Trajectory with Feature Selection:

| Week | Features Tested | Features Kept | Expected R² | Accuracy |
|------|----------------|---------------|-------------|----------|
| 0 | 12 | 12 | 0.71 | ~70% |
| 1 | 500 | 50-75 | 0.76 | ~75% |
| 2 | 1,500 | 100-150 | 0.80 | ~80% |
| 3 | 3,000 | 150-200 | 0.83 | ~83% |
| 4 | 4,500 | 200-250 | 0.85 | ~85% |
| 5 | 6,000 | 250-300 | 0.87 | ~87% |
| 6 | All tested | Optimal set | 0.88 | ~88% |

**Note**: Keeping only 5-10% of tested features is normal and expected.

---

## 🔧 IMPLEMENTATION PLAN

### Week 1: Foundation Testing
```python
# Priority 1: Triangulation
triangulation_impact = test_triangulation_features()
if triangulation_impact > 0.01:
    operationalize_triangulation()

# Priority 2: Correlation Network (simplified)
correlation_impact = test_correlation_matrix(top_10_pairs_only=True)
if correlation_impact > 0.02:
    expand_correlation_testing()

# Priority 3: Extended lags (selective)
lag_impact = test_extended_lags(lags=[15, 20, 30, 50])
if lag_impact > 0.01:
    optimize_lag_selection()
```

### Week 2: Algorithm Diversification
```python
# Test multiple algorithms on current best features
algorithms_to_test = [
    'lightgbm',     # Faster training
    'catboost',     # Categorical handling
    'extra_trees',  # Ensemble diversity
    'neural_net'    # Non-linear patterns
]

best_algorithm = compare_algorithms(current_features)
if ensemble_performs_better():
    implement_stacking()
```

### Week 3: Advanced Features (Conditional)
```python
# Only test if Week 1-2 show promising improvements
if current_improvement >= 0.10:  # 10% better than baseline
    test_advanced_features([
        'wavelets',
        'regime_detection',
        'market_microstructure'
    ])
```

---

## 📈 OPERATIONALIZATION CRITERIA

### Features Will Be Operationalized If:

1. **Performance Gain > 1%** absolute improvement in R²
2. **Statistical Significance** p-value < 0.05
3. **Computational Efficiency** training time increase < 2x
4. **Stability** consistent improvement across validation folds
5. **Interpretability** feature importance is logical

### Features Will Be Rejected If:

1. **No improvement** or negative impact
2. **Overfitting** train/test gap increases
3. **Computational burden** >5x training time for <2% gain
4. **Instability** inconsistent across time periods
5. **Multicollinearity** high correlation with existing features

---

## 🎯 REVISED EXPECTATIONS

### What's Realistic:

| Scenario | Final R² | Accuracy | Features Used | Timeline |
|----------|----------|----------|---------------|----------|
| **Conservative** | 0.80 | 80% | 50-100 | 2 weeks |
| **Moderate** | 0.85 | 85% | 150-250 | 4 weeks |
| **Aggressive** | 0.88 | 88% | 300-500 | 6 weeks |
| **Theoretical Max** | 0.92 | 92% | 500+ | 8+ weeks |

### Why 95% May Not Be Achievable:

1. **Market Efficiency**: Random walk hypothesis limits predictability
2. **Noise Floor**: ~10-15% of movement is pure randomness
3. **Regime Changes**: Models trained on history fail on new regimes
4. **Feature Saturation**: Diminishing returns after 200-300 features

---

## ✅ NEXT STEPS

### Immediate Actions (This Week):

1. **Set up automated testing pipeline**
2. **Test triangulation on major pairs**
3. **Evaluate simplified correlation matrix**
4. **Assess extended lags value**
5. **Report incremental improvements**

### Decision Points:

- **After 100 features tested**: Evaluate if continuing is worthwhile
- **At 85% accuracy**: Assess cost/benefit of pushing further
- **If plateau reached**: Focus on robustness over accuracy

---

## 📊 TRACKING DASHBOARD

```python
feature_testing_dashboard = {
    'total_planned': 6000,
    'tested': 0,
    'kept': 12,  # Current Smart Dual
    'rejected': 0,
    'current_r2': 0.7079,
    'target_r2': 0.95,  # Aspirational
    'realistic_target': 0.88,  # Achievable
    'testing_velocity': '100 features/day',
    'decision_threshold': 0.01  # 1% improvement to keep
}
```

---

## 🎯 KEY INSIGHT

**The goal is not to use all 6,000 features, but to TEST them all and KEEP only those that demonstrably improve performance.**

This is a much more reasonable and professional approach that will lead to:
- Optimal model performance
- Manageable complexity
- Faster inference
- Better generalization
- Easier maintenance

**Expected Outcome**: 200-500 high-value features achieving 85-88% accuracy.