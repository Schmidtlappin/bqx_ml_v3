# BQX ML V3 COMPREHENSIVE TESTING ROADMAP

**Version**: 1.0
**Date**: November 27, 2025
**Mandate**: Test ALL strategies to determine impact on prediction capability
**Target**: Achieve 85-88% R² through systematic feature engineering

---

## 🎯 EXECUTIVE SUMMARY

Per user directive, ALL strategies must be tested comprehensively to determine their respective impact on the model's ability to predict. This roadmap defines exactly HOW and WHEN each strategy will be tested.

**Total Features to Test**: ~6,000
**Testing Duration**: 3-4 weeks
**Success Threshold**: >0.5% R² improvement per feature
**Current Baseline**: R² = 0.7079

---

## 📊 TESTING METHODOLOGY

### Core Testing Framework
```python
class ComprehensiveFeatureTester:
    """Framework for systematic feature testing"""

    def __init__(self, baseline_r2=0.7079):
        self.baseline_r2 = baseline_r2
        self.results = []
        self.kept_features = []

    def test_feature(self, feature, model):
        """Test single feature impact"""
        # Add feature to model
        enhanced_model = self.add_feature(model, feature)

        # Train with cross-validation
        scores = cross_val_score(enhanced_model, X, y, cv=5,
                                scoring='r2')

        # Calculate metrics
        new_r2 = scores.mean()
        std_dev = scores.std()
        improvement = (new_r2 - self.baseline_r2) / self.baseline_r2 * 100

        # Statistical significance test
        t_stat, p_value = stats.ttest_1samp(scores, self.baseline_r2)

        # Decision
        keep = (improvement > 0.5 and p_value < 0.05)

        return {
            'feature': feature,
            'new_r2': new_r2,
            'improvement': improvement,
            'p_value': p_value,
            'keep': keep
        }
```

---

## 🗓️ PHASE 2A: TRIANGULATION FEATURES (Days 1-5)

### What: Currency Triangle Arbitrage Features
**Total Features**: 378 triangles
**Expected Keep Rate**: 5-10% (20-40 features)
**Testing Order**: By liquidity tier

### How:
```python
def test_triangulation_features():
    """Test all 378 currency triangles systematically"""

    triangles = {
        'Tier_1_Majors': [  # Test first (21 triangles)
            'EUR-USD-GBP', 'EUR-USD-JPY', 'EUR-GBP-JPY',
            'USD-GBP-JPY', 'EUR-USD-CHF', 'EUR-GBP-CHF',
            # ... all major combinations
        ],
        'Tier_2_Commodity': [  # Test second (84 triangles)
            'AUD-USD-CAD', 'AUD-USD-NZD', 'CAD-USD-NZD',
            # ... all commodity combinations
        ],
        'Tier_3_Exotic': [  # Test last (273 triangles)
            # All remaining combinations
        ]
    }

    for tier, triangle_list in triangles.items():
        for triangle in triangle_list:
            # Calculate triangle arbitrage indicator
            feature = calculate_triangle_arbitrage(triangle)

            # Test impact
            result = test_feature(feature)

            # Real-time AirTable update
            update_airtable('MP03.P05.S05.T10', result)

            # Keep if significant
            if result['improvement'] > 0.5:
                selected_features.append(feature)
```

### When:
- **Day 1-2**: Tier 1 Majors (21 triangles)
- **Day 2-3**: Tier 2 Commodity (84 triangles)
- **Day 3-5**: Tier 3 Exotic (273 triangles)

### Success Criteria:
- All 378 triangles tested
- 20-40 features selected
- R² improvement > 1% cumulative

---

## 🗓️ PHASE 2B: CORRELATION NETWORK (Days 5-10)

### What: Cross-Pair Correlation Matrices
**Total Features**: 1,960 correlations (28x28x2.5 windows)
**Expected Keep Rate**: 2-5% (40-100 features)
**Testing Order**: Expanding matrix size

### How:
```python
def test_correlation_network():
    """Build and test expanding correlation matrices"""

    configurations = [
        {'size': 7, 'pairs': major_pairs},      # 49 correlations
        {'size': 14, 'pairs': major_commodity},  # 196 correlations
        {'size': 28, 'pairs': all_pairs}        # 784 correlations
    ]

    windows = [10, 20, 50, 100, 200]  # Rolling windows
    methods = ['pearson', 'spearman', 'kendall']

    for config in configurations:
        for window in windows:
            for method in methods:
                # Calculate correlation matrix
                corr_matrix = calculate_correlation(
                    pairs=config['pairs'],
                    window=window,
                    method=method
                )

                # Extract features (upper triangle)
                features = extract_correlation_features(corr_matrix)

                # Test each correlation pair
                for feature in features:
                    result = test_feature(feature)
                    update_airtable('MP03.P05.S05.T11', result)
```

### When:
- **Day 5-6**: 7x7 matrix all windows/methods
- **Day 7-8**: 14x14 matrix expansion
- **Day 9-10**: Full 28x28 matrix

### Success Criteria:
- All correlation configurations tested
- Network effects identified
- R² improvement > 2% cumulative

---

## 🗓️ PHASE 2C: EXTENDED LAGS (Days 10-14)

### What: Deep Historical Patterns
**Total Features**: ~1,400 lag combinations
**Expected Keep Rate**: 3-5% (40-70 features)
**Testing Order**: By lag depth and pair importance

### How:
```python
def test_extended_lags():
    """Test extended lag features systematically"""

    lag_configs = {
        'short_extension': range(15, 31),   # All pairs
        'medium_extension': range(31, 61),  # Top 10 pairs
        'long_extension': range(61, 101),   # Top 3 pairs
    }

    # Lag interactions
    interactions = {
        'ratios': lambda l1, l2: f'lag_{l1}/lag_{l2}',
        'differences': lambda l1, l2: f'lag_{l1}-lag_{l2}',
        'momentum': lambda l1, l2, l3: f'lag_{l1}-lag_{l2}-lag_{l3}'
    }

    for config_name, lag_range in lag_configs.items():
        pairs = get_pairs_for_config(config_name)

        for pair in pairs:
            for lag in lag_range:
                # Simple lag feature
                feature = create_lag_feature(pair, lag)
                result = test_feature(feature)

                # Interaction features
                for interaction_type in interactions:
                    interaction_feature = create_interaction(
                        pair, lag, interaction_type
                    )
                    result = test_feature(interaction_feature)

                update_airtable('MP03.P05.S05.T13', result)
```

### When:
- **Day 10-11**: Lags 15-30 all pairs
- **Day 12-13**: Lags 31-60 top pairs
- **Day 13-14**: Lags 61-100 majors only

### Success Criteria:
- Optimal lag window identified
- Interaction effects captured
- R² improvement > 1.5% cumulative

---

## 🗓️ PHASE 2D: ALGORITHM DIVERSIFICATION (Days 14-18)

### What: Alternative ML Algorithms
**Total Configurations**: ~200 hyperparameter combinations
**Expected Best**: LightGBM or Ensemble
**Testing Order**: By algorithm complexity

### How:
```python
def test_algorithm_diversification():
    """Test different algorithms with hyperparameter tuning"""

    algorithms = {
        'LightGBM': {
            'n_estimators': [100, 200, 500],
            'max_depth': [5, 8, 10],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.8, 0.9, 1.0]
        },
        'CatBoost': {
            'iterations': [100, 200, 500],
            'depth': [4, 6, 8],
            'learning_rate': [0.01, 0.05, 0.1],
            'l2_leaf_reg': [1, 3, 5]
        },
        'NeuralNetwork': {
            'architectures': [[32,16,8], [64,32,16], [128,64,32]],
            'activation': ['relu', 'tanh'],
            'dropout': [0.2, 0.3, 0.4],
            'batch_size': [32, 64, 128]
        },
        'Ensemble': {
            'voting': ['hard', 'soft'],
            'stacking': [True, False],
            'weights': ['uniform', 'optimized']
        }
    }

    for algo_name, param_grid in algorithms.items():
        # Grid search with cross-validation
        model = create_model(algo_name)
        grid_search = GridSearchCV(
            model, param_grid, cv=5,
            scoring='r2', n_jobs=-1
        )

        grid_search.fit(X_train, y_train)

        # Test best configuration
        best_model = grid_search.best_estimator_
        best_r2 = grid_search.best_score_

        result = {
            'algorithm': algo_name,
            'best_params': grid_search.best_params_,
            'r2': best_r2,
            'improvement': (best_r2 - baseline_r2) / baseline_r2 * 100
        }

        update_airtable('MP03.P06.S06.T01', result)
```

### When:
- **Day 14-15**: LightGBM full grid search
- **Day 15-16**: CatBoost optimization
- **Day 16-17**: Neural Network architectures
- **Day 17-18**: Ensemble methods

### Success Criteria:
- All algorithms tested with tuning
- Best configuration identified
- R² improvement > 3% for best model

---

## 🗓️ PHASE 2E: ADVANCED FEATURES (Days 18-21)

### What: Market Microstructure & Technical Indicators
**Total Features**: ~800 advanced features
**Expected Keep Rate**: 5-10% (40-80 features)
**Testing Order**: By feature complexity

### How:
```python
def test_advanced_features():
    """Test advanced market features"""

    feature_categories = {
        'Covariance': {
            'methods': ['dynamic', 'rolling', 'ewm'],
            'decomposition': ['eigenvalue', 'svd', 'pca'],
            'components': range(1, 11)
        },
        'Microstructure': {
            'spread_proxy': ['high_low', 'close_close', 'garman_klass'],
            'volume_patterns': ['vwap', 'volume_profile', 'accumulation'],
            'time_effects': ['hour', 'day_of_week', 'month']
        },
        'Technical': {
            'momentum': ['rsi', 'stochastic', 'williams_r'],
            'trend': ['macd', 'adx', 'ichimoku'],
            'volatility': ['bollinger', 'atr', 'keltner'],
            'volume': ['obv', 'cmf', 'mfi']
        },
        'Volatility': {
            'garch': ['garch11', 'egarch', 'gjr_garch'],
            'realized': ['rv5', 'rv10', 'rv20'],
            'implied': ['atm', 'skew', 'term_structure']
        }
    }

    for category, subcategories in feature_categories.items():
        for subcat, options in subcategories.items():
            features = generate_features(category, subcat, options)

            for feature in features:
                result = test_feature(feature)
                update_airtable('MP03.P05.S05.T12', result)

                if result['keep']:
                    selected_advanced.append(feature)
```

### When:
- **Day 18**: Covariance features
- **Day 19**: Market microstructure
- **Day 20**: Technical indicators
- **Day 21**: Volatility modeling

### Success Criteria:
- All advanced features tested
- Key patterns identified
- R² improvement > 2% cumulative

---

## 📈 PERFORMANCE TRACKING

### Daily Metrics Dashboard
```python
def generate_daily_report(day):
    """Generate comprehensive daily testing report"""

    report = {
        'date': datetime.now(),
        'day': day,
        'features_tested_today': count_today,
        'features_tested_total': count_total,
        'features_kept_today': kept_today,
        'features_kept_total': kept_total,
        'current_r2': current_r2,
        'improvement_from_baseline': improvement,
        'target_r2': 0.88,
        'gap_to_target': 0.88 - current_r2,
        'estimated_completion': estimate_completion_date()
    }

    # Generate visualizations
    plot_r2_trajectory()
    plot_feature_importance()
    plot_improvement_by_category()

    return report
```

### Success Milestones
| Milestone | Target Date | Success Criteria | R² Target |
|-----------|-------------|------------------|-----------|
| Phase 2A Complete | Day 5 | All triangulation tested | 0.72 |
| Phase 2B Complete | Day 10 | All correlations tested | 0.74 |
| Phase 2C Complete | Day 14 | All lags tested | 0.76 |
| Phase 2D Complete | Day 18 | All algorithms tested | 0.80 |
| Phase 2E Complete | Day 21 | All advanced tested | 0.85 |
| **Project Complete** | **Day 21** | **All strategies tested** | **0.85-0.88** |

---

## 🔄 CONTINUOUS IMPROVEMENT PROTOCOL

### After Each Testing Phase:
1. **Analyze Results**: Identify patterns in successful features
2. **Refine Strategy**: Adjust thresholds based on learnings
3. **Optimize Pipeline**: Incorporate successful features
4. **Update Models**: Retrain with enhanced feature set
5. **Validate Improvements**: Confirm R² gains are stable

### Feature Selection Criteria:
```python
def should_keep_feature(result):
    """Determine if feature should be kept"""

    criteria = [
        result['improvement'] > 0.5,      # Minimum improvement
        result['p_value'] < 0.05,         # Statistical significance
        result['stability'] > 0.8,        # Cross-validation stability
        result['correlation'] < 0.95,      # Not redundant
        result['computation_time'] < 1000  # Reasonable compute
    ]

    return all(criteria)
```

---

## 📊 EXPECTED OUTCOMES

### By Strategy:
| Strategy | Features to Test | Expected Keep | Expected R² Gain |
|----------|-----------------|---------------|------------------|
| Triangulation | 378 | 20-40 | +1-2% |
| Correlation | 1,960 | 40-100 | +2-3% |
| Extended Lags | 1,400 | 40-70 | +1-2% |
| Algorithms | 200 configs | 1 best | +3-5% |
| Advanced | 800 | 40-80 | +2-3% |
| **TOTAL** | **~4,738** | **~200-300** | **+10-15%** |

### Final Target Achievement:
- **Baseline R²**: 0.7079
- **Expected Final R²**: 0.85-0.88
- **Total Improvement**: 20-24%
- **Features in Final Model**: 200-300

---

## ⚡ ACCELERATION STRATEGIES

### To Speed Up Testing:
1. **Parallel Processing**: Test independent features concurrently
2. **Early Stopping**: Skip obviously poor features
3. **Batch Evaluation**: Test groups of similar features
4. **Cached Computations**: Reuse intermediate results
5. **Distributed Training**: Use multiple machines

### Implementation:
```python
from joblib import Parallel, delayed
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_feature_computation(feature_spec):
    """Cache expensive feature computations"""
    return compute_feature(feature_spec)

def parallel_feature_testing(features, n_jobs=-1):
    """Test features in parallel"""
    results = Parallel(n_jobs=n_jobs)(
        delayed(test_feature)(f) for f in features
    )
    return results
```

---

## 🚨 RISK MITIGATION

### Potential Risks:
1. **Computational Constraints**: Use sampling if needed
2. **Overfitting**: Strict cross-validation protocols
3. **Feature Explosion**: Aggressive selection criteria
4. **Time Overrun**: Parallel processing and optimization

### Contingency Plans:
- If testing takes too long: Increase parallelization
- If no improvements found: Test interaction effects
- If overfitting detected: Increase regularization
- If memory issues: Batch processing with cleanup

---

## ✅ COMPLIANCE & REPORTING

### User Mandate Compliance:
- ✅ ALL strategies will be tested
- ✅ Impact on prediction measured for each
- ✅ Comprehensive documentation maintained
- ✅ No early stopping without authorization

### Reporting Schedule:
- **Every 2 hours**: Progress update to BA
- **Daily**: Comprehensive report with visualizations
- **Weekly**: Executive summary with recommendations
- **On completion**: Final report with all results

---

## 📋 CONCLUSION

This roadmap ensures COMPREHENSIVE testing of ALL strategies as mandated by the user. Every feature will be tested, measured, and documented. The systematic approach guarantees we identify the optimal feature set to achieve the 85-88% R² target.

**Total Testing Time**: 21 days
**Total Features**: ~6,000
**Expected Outcome**: R² = 0.85-0.88
**Confidence Level**: HIGH

---

**Document Status**: ACTIVE
**Implementation**: IMMEDIATE
**Updates**: Real-time via AirTable
**Questions**: Escalate to Chief Engineer