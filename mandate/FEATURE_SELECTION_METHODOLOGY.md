# Feature Evaluation & Selection Methodology for BQX ML V3

## Optimized for Oscillating BQX Prediction and Game Theory Trading

**Document Version**: 1.0.0
**Created**: 2025-11-29
**Author**: BQXML Chief Engineer
**Classification**: MANDATE - Feature Selection Reference

---

## EXECUTIVE SUMMARY

This document defines the feature evaluation and selection methodology for BQX ML V3, specifically designed for:
1. **Oscillating value prediction** - BQX values mean-revert around zero
2. **Direction accuracy** - 95%+ accuracy required for |BQX| > 1σ
3. **Extreme prediction** - High precision for |BQX| > 2σ events
4. **Game theory trading** - Features must predict momentum exhaustion

---

## PART I: THE OSCILLATION PREDICTION CHALLENGE

### 1.1 Why Oscillating Prediction is Different

```
STANDARD REGRESSION:
├── Predict continuous value
├── Optimize for overall R²
├── All data points weighted equally
└── Linear correlation is sufficient

OSCILLATING BQX PREDICTION:
├── Predict values that OSCILLATE around zero
├── Optimize for DIRECTION first, magnitude second
├── EXTREME values matter more than normal
├── Must capture REVERSAL dynamics, not just correlation
└── Features must predict WHEN oscillation turns
```

### 1.2 The Three Prediction Regimes

| Regime | BQX Range | Frequency | Prediction Priority | Feature Need |
|--------|-----------|-----------|---------------------|--------------|
| **EXTREME** | \|BQX\| > 2σ | ~4% | Direction (99%+), Magnitude | Reversal detection |
| **NORMAL** | 0.5σ < \|BQX\| < 2σ | ~64% | Direction (95%+) | Trend continuation/exhaustion |
| **CHAOS** | \|BQX\| < 0.5σ | ~32% | None (no trade) | N/A |

**Key Insight**: Standard feature evaluation weights the 32% chaos zone and 64% normal zone heavily, but we need features that excel in the 4% extreme zone.

### 1.3 What Makes a "Good" Feature for Oscillation Prediction?

```
TRADITIONAL "GOOD" FEATURE:
├── High overall correlation with target
├── Consistent relationship across all samples
└── Low variance

OSCILLATION-OPTIMAL "GOOD" FEATURE:
├── High correlation DURING EXTREMES (|BQX| > 2σ)
├── Predicts DIRECTION CHANGE, not just correlation
├── Different behavior at different oscillation phases
├── Captures EXHAUSTION signals
└── May have LOW overall correlation but HIGH extreme correlation
```

---

## PART II: FEATURE EVALUATION FRAMEWORK

### 2.1 The Four Evaluation Dimensions

Every candidate feature must be evaluated on four dimensions:

```
DIMENSION 1: DIRECTION DISCRIMINATION
├── Can this feature distinguish positive vs negative future BQX?
├── Metric: Direction accuracy when feature is strong
└── Target: ≥ 95% for extreme feature values

DIMENSION 2: EXTREME PREDICTIVE POWER
├── Does this feature predict when |BQX| will exceed 2σ?
├── Metric: Correlation calculated ONLY during extreme periods
└── Target: |extreme_correlation| > 0.15

DIMENSION 3: REVERSAL DETECTION
├── Does this feature signal when BQX will change direction?
├── Metric: Lead time before reversals
└── Target: Signal appears 5-15 intervals before reversal

DIMENSION 4: REGIME CONSISTENCY
├── Is this feature reliable across different market regimes?
├── Metric: Correlation stability across time periods
└── Target: Sign consistency > 70% across quarters
```

### 2.2 Evaluation Metrics by Dimension

**DIRECTION DISCRIMINATION METRICS**:

```sql
-- Direction accuracy when feature is in extreme zone
WITH feature_extremes AS (
    SELECT
        timestamp,
        feature_value,
        SIGN(target_value) AS actual_direction,
        SIGN(feature_value) AS predicted_direction
    FROM feature_target_joined
    WHERE ABS(feature_value) > 2 * (SELECT STDDEV(feature_value) FROM feature_target_joined)
)
SELECT
    feature_name,
    COUNT(*) AS extreme_samples,
    SUM(CASE WHEN actual_direction = -predicted_direction THEN 1 ELSE 0 END) / COUNT(*) AS direction_accuracy
    -- Note: -predicted_direction because we SHORT when feature is positive
FROM feature_extremes
GROUP BY feature_name
HAVING COUNT(*) >= 500
ORDER BY direction_accuracy DESC
```

**EXTREME PREDICTIVE POWER METRICS**:

```sql
-- Correlation during extreme BQX periods only
WITH extreme_bqx AS (
    SELECT *
    FROM feature_target_joined
    WHERE ABS(target_value) > 2 * (SELECT STDDEV(target_value) FROM feature_target_joined)
)
SELECT
    feature_name,
    CORR(feature_value, target_value) AS extreme_correlation,
    COUNT(*) AS extreme_samples
FROM extreme_bqx
GROUP BY feature_name
HAVING COUNT(*) >= 500
ORDER BY ABS(extreme_correlation) DESC
```

**REVERSAL DETECTION METRICS**:

```sql
-- Identify reversals and check if feature signaled in advance
WITH reversals AS (
    SELECT
        timestamp,
        target_value,
        LAG(target_value, 10) OVER (ORDER BY timestamp) AS target_lag10,
        SIGN(target_value) != SIGN(LAG(target_value, 10) OVER (ORDER BY timestamp)) AS is_reversal
    FROM target_table
    WHERE ABS(target_value) > 1 * STDDEV(target_value) OVER ()
)
SELECT
    feature_name,
    CORR(feature_value, CAST(is_reversal AS INT)) AS reversal_correlation
FROM feature_joined_reversals
WHERE is_reversal = TRUE
GROUP BY feature_name
```

### 2.3 The Evaluation Scoring System

Each feature receives a composite score:

```
FEATURE SCORE =
    0.30 × Direction_Score +
    0.40 × Extreme_Score +
    0.15 × Reversal_Score +
    0.15 × Regime_Score

Where:
├── Direction_Score = Direction accuracy (%) scaled to 0-100
├── Extreme_Score = |extreme_correlation| × 500 (scaled to 0-100)
├── Reversal_Score = reversal_lead_correlation × 100 (scaled to 0-100)
└── Regime_Score = sign_consistency (%) scaled to 0-100
```

**Selection Thresholds**:

| Category | Minimum Score | Action |
|----------|---------------|--------|
| MANDATORY | ≥ 80 | Include regardless |
| STRONG | 60-79 | Include |
| MODERATE | 40-59 | Include if diversity needed |
| WEAK | 20-39 | Exclude unless unique |
| REJECT | < 20 | Exclude |

---

## PART III: DETERMINING OPTIMAL FEATURE QUANTITY

### 3.1 The Feature Quantity Problem

```
TOO FEW FEATURES:
├── Miss important signals
├── Underfitting
├── Single point of failure
└── Poor generalization

TOO MANY FEATURES:
├── Overfitting
├── Noise amplification
├── Computational cost
├── Multicollinearity issues
└── Interpretability loss
```

### 3.2 The Optimal Feature Range

**Research-Based Guidance**:

| Sample Size (rows) | Optimal Feature Range | Ratio Guidance |
|-------------------|----------------------|----------------|
| 100,000 | 30-50 | 1:2000 - 1:3000 |
| 500,000 | 50-100 | 1:5000 - 1:10000 |
| 1,000,000 | 80-150 | 1:7000 - 1:12000 |
| 2,000,000+ (BQX) | **100-200** | 1:10000 - 1:20000 |

**BQX ML V3 Recommendation**:

```
OPTIMAL FEATURE COUNT: 120-180 features per model

BREAKDOWN:
├── Direction-critical features: 40-50 (30%)
├── Extreme-critical features: 50-70 (40%)
├── Regime features: 15-25 (15%)
├── Diversity/safety features: 15-35 (15%)
└── TOTAL: 120-180
```

### 3.3 Feature Quantity Validation

**Method: Recursive Feature Elimination with CV**

```python
def optimal_feature_count(X, y, model):
    """
    Find optimal feature count using RFE with cross-validation
    """
    from sklearn.feature_selection import RFECV

    rfecv = RFECV(
        estimator=model,
        step=0.1,  # Remove 10% at each step
        cv=TimeSeriesSplit(n_splits=5),
        scoring='neg_mean_squared_error',
        min_features_to_select=50
    )
    rfecv.fit(X, y)

    # Plot to find elbow
    optimal_n = rfecv.n_features_
    return optimal_n, rfecv.support_
```

**The 1-SE Rule**:
- Find the minimum features where CV score is within 1 standard error of maximum
- This prevents overfitting while maintaining performance

### 3.4 Per-Model vs Universal Features

```
FEATURE ALLOCATION STRATEGY:

UNIVERSAL FEATURES (80%):
├── Features that work across ALL 28 pairs
├── Selected from intersection of top features per pair
├── Provides consistency and interpretability
└── Count: ~100-150 features

PAIR-SPECIFIC FEATURES (20%):
├── Features unique to each currency pair
├── Captures pair-specific dynamics
├── Different for EURUSD vs NZDJPY
└── Count: ~20-30 features per pair
```

---

## PART IV: FEATURE DIVERSIFICATION STRATEGY

### 4.1 Why Diversification is Critical

```
THE HIDDEN DANGER:

If all selected features are highly correlated:
├── They all fail together during regime shifts
├── Model has no backup signals
├── Single point of failure
└── Catastrophic when primary signal fails

DIVERSIFICATION ENSURES:
├── Multiple independent information sources
├── Redundancy for robustness
├── Coverage of different market states
└── Graceful degradation, not catastrophic failure
```

### 4.2 The Diversification Framework

**DIMENSION 1: Feature Type Diversity**

```
8 FEATURE TYPES MUST ALL BE REPRESENTED:

| Type | Min % | Max % | Purpose |
|------|-------|-------|---------|
| LAG (lag_*) | 15% | 35% | Historical momentum patterns |
| MOMENTUM (mom_*) | 10% | 25% | Speed of movement |
| VOLATILITY (vol_*) | 8% | 20% | Stretch/reversion potential |
| REGIME (regime_*) | 10% | 25% | Market state classification |
| CORRELATION (corr_*) | 8% | 20% | Cross-pair relationships |
| REGRESSION (reg_*) | 5% | 15% | Trend estimation |
| AGGREGATION (agg_*) | 5% | 15% | Multi-scale summaries |
| ALIGNMENT (align_*) | 3% | 10% | Cross-timeframe alignment |
```

**Diversity Index Calculation**:

```python
def feature_type_diversity(selected_features):
    """
    Calculate Shannon entropy of feature type distribution
    Returns 0 (single type) to 1 (perfectly balanced)
    """
    from collections import Counter
    import numpy as np

    type_counts = Counter([f.split('_')[0] for f in selected_features])
    proportions = np.array(list(type_counts.values())) / len(selected_features)

    # Shannon entropy normalized
    entropy = -np.sum(proportions * np.log(proportions))
    max_entropy = np.log(8)  # 8 feature types

    return entropy / max_entropy

# REQUIREMENT: diversity_index >= 0.70
```

**DIMENSION 2: Centric Diversity**

```
6 CENTRICS MUST ALL BE REPRESENTED:

| Centric | Min Features | Purpose |
|---------|--------------|---------|
| PRIMARY | 50-100 | Core pair dynamics (EURUSD for EURUSD model) |
| VARIANT | 10-20 | Same-currency pairs (EUR* for EURUSD) |
| COVARIANT | 30-50 | Cross-pair dynamics (GBPUSD for EURUSD) |
| TRIANGULATION | 10-20 | Triangular arbitrage (EURGBP for EURUSD/GBPUSD) |
| SECONDARY | 10-20 | Currency strength indices |
| TERTIARY | 5-10 | Market-wide context |

TOTAL MINIMUM: 115-220 features
```

**DIMENSION 3: Temporal Diversity**

```
FEATURES MUST COVER MULTIPLE TIMESCALES:

| Timescale | Feature Examples | Min % |
|-----------|------------------|-------|
| Ultra-short (1-10 intervals) | lag_1, lag_5, mom_10 | 15% |
| Short (10-60 intervals) | lag_30, vol_60, regime_45 | 25% |
| Medium (60-360 intervals) | lag_180, agg_360 | 25% |
| Long (360-1440 intervals) | lag_720, regime_1440 | 20% |
| Extended (1440+ intervals) | lag_2880, trend_2880 | 15% |
```

**DIMENSION 4: Correlation Cluster Diversity**

```
ANTI-CORRELATION REQUIREMENT:

1. Calculate feature-to-feature correlation matrix
2. Cluster features with |corr| > 0.8
3. Select AT MOST one representative per cluster
4. Ensure selected features have |corr| < 0.5 with each other

GOAL: No two selected features should be >0.8 correlated
```

### 4.3 The Diversification Enforcement Algorithm

```python
def enforce_diversification(candidate_features, scores):
    """
    Select features while enforcing diversification constraints
    """
    selected = []

    # Step 1: Mandatory features (one per type/centric if score > threshold)
    for feature_type in FEATURE_TYPES:
        best = get_best_by_type(candidate_features, feature_type, scores)
        if scores[best] >= 40:
            selected.append(best)

    for centric in CENTRICS:
        best = get_best_by_centric(candidate_features, centric, scores)
        if scores[best] >= 40:
            selected.append(best)

    # Step 2: Fill remaining slots with best non-correlated features
    remaining = [f for f in candidate_features if f not in selected]
    remaining_sorted = sorted(remaining, key=lambda f: scores[f], reverse=True)

    for feature in remaining_sorted:
        if len(selected) >= MAX_FEATURES:
            break

        # Check correlation with already selected
        max_corr = max(abs(correlation(feature, s)) for s in selected)
        if max_corr < 0.5:
            selected.append(feature)

    # Step 3: Validate diversification
    diversity_score = feature_type_diversity(selected)
    if diversity_score < 0.70:
        raise ValueError("Diversification constraint violated")

    return selected
```

---

## PART V: THE COMPLETE FEATURE SELECTION PIPELINE

### 5.1 Phase 1: Candidate Generation

```
INPUT: All 8,000+ available features
OUTPUT: ~2,000 candidate features

STEPS:
1. Calculate basic statistics for all features
2. Remove features with >10% missing values
3. Remove features with zero variance
4. Remove features with >0.95 correlation to another feature
5. Keep best representative from each correlation cluster
```

### 5.2 Phase 2: Oscillation-Specific Evaluation

```
INPUT: ~2,000 candidate features
OUTPUT: Scored features with 4-dimension evaluation

STEPS:
1. Calculate direction discrimination score
2. Calculate extreme predictive power score
3. Calculate reversal detection score
4. Calculate regime consistency score
5. Compute composite score
6. Rank all features
```

### 5.3 Phase 3: Quantity Optimization

```
INPUT: Ranked features
OUTPUT: Optimal feature count

STEPS:
1. Run RFECV with TimeSeriesSplit
2. Apply 1-SE rule to find minimum features
3. Validate count is within 120-180 range
4. Adjust if outside range
```

### 5.4 Phase 4: Diversification Enforcement

```
INPUT: Top N features by score
OUTPUT: Diversified feature set

STEPS:
1. Ensure all 8 feature types represented
2. Ensure all 6 centrics represented
3. Ensure temporal diversity
4. Remove correlated features (keep best)
5. Calculate diversity index (must be ≥ 0.70)
6. Add diversity-required features if needed
```

### 5.5 Phase 5: Validation and Ablation

```
INPUT: Selected feature set
OUTPUT: Validated final feature set

STEPS:
1. Train model with selected features
2. Measure direction accuracy by zone
3. Measure extreme prediction precision/recall
4. Run ablation testing (remove each type/centric)
5. Identify any critical features (>5% impact)
6. Document feature justifications
```

---

## PART VI: SPECIALIZED FEATURE CATEGORIES

### 6.1 Direction-Critical Features

Features that distinguish positive vs negative future BQX:

```
SIGN-BASED FEATURES:
├── sign_bqx_45, sign_bqx_90, ... (current direction)
├── sign_change_count_N (recent direction changes)
├── sign_persistence_N (how long same direction)
└── sign_momentum (direction × magnitude)

ASYMMETRY FEATURES:
├── upside_downside_ratio_N
├── positive_streak_length
├── negative_streak_length
└── directional_acceleration
```

### 6.2 Extreme-Critical Features

Features that predict |BQX| > 2σ events:

```
VOLATILITY PRECURSORS:
├── vol_atr_expanding (ATR increasing)
├── vol_range_extreme (price range expanding)
├── vol_acceleration (second derivative of volatility)
└── vol_regime_shift (volatility regime changing)

HISTORICAL EXTREME PATTERNS:
├── extreme_count_last_N (recent extreme frequency)
├── time_since_last_extreme
├── extreme_clustering_score
└── mean_reversion_pressure (how far from zero)

CROSS-PAIR EXTREME SIGNALS:
├── corr_extreme_count (extremes in correlated pairs)
├── market_stress_index
├── correlation_breakdown (normal correlations failing)
└── contagion_score
```

### 6.3 Reversal Detection Features

Features that signal direction changes:

```
MOMENTUM EXHAUSTION:
├── momentum_deceleration (slowing down)
├── momentum_divergence (price vs momentum disagreement)
├── volume_exhaustion (volume declining at extreme)
└── buying/selling_pressure_shift

MEAN-REVERSION SIGNALS:
├── distance_from_zero (|BQX| as mean-reversion pressure)
├── time_at_extreme (duration at extreme level)
├── reversion_velocity_estimate
└── equilibrium_pull_strength

REGIME CHANGE SIGNALS:
├── regime_transition_probability
├── regime_instability_score
├── support_resistance_proximity
└── breakout_failure_signal
```

### 6.4 Regime-Conditional Features

Features that are important in specific regimes:

```
HIGH VOLATILITY REGIME:
├── vol_adjusted_momentum
├── vol_normalized_bqx
├── extreme_sensitivity
└── vol_regime_duration

TRENDING REGIME:
├── trend_strength
├── trend_persistence
├── trend_acceleration
└── trend_exhaustion_probability

RANGING REGIME:
├── range_width
├── range_position (high/mid/low)
├── range_breakout_probability
└── mean_reversion_strength
```

---

## PART VII: IMPLEMENTATION CHECKLIST

### 7.1 Pre-Selection Validation

- [ ] All 8 feature types have candidates
- [ ] All 6 centrics have candidates
- [ ] All 7 BQX windows represented
- [ ] Both IDX and BQX variants available
- [ ] Sufficient historical data (>1M rows)

### 7.2 Evaluation Validation

- [ ] Direction accuracy calculated for extreme feature values
- [ ] Extreme correlation calculated (|BQX| > 2σ only)
- [ ] Reversal detection metrics calculated
- [ ] Regime consistency (quarterly) validated
- [ ] Composite scores computed

### 7.3 Selection Validation

- [ ] Feature count in 120-180 range
- [ ] Diversity index ≥ 0.70
- [ ] All 8 feature types represented
- [ ] All 6 centrics represented
- [ ] No two features with |corr| > 0.8
- [ ] Temporal diversity achieved

### 7.4 Post-Selection Validation

- [ ] Direction accuracy ≥ 95% for |BQX| > 1σ
- [ ] Extreme recall ≥ 70%
- [ ] Extreme precision ≥ 60%
- [ ] Ablation testing complete
- [ ] Critical features documented

---

## PART VIII: SUCCESS CRITERIA

### 8.1 Feature Selection Success

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Feature count | 120-180 | Count of selected features |
| Diversity index | ≥ 0.70 | Shannon entropy normalized |
| Type coverage | 8/8 | All feature types represented |
| Centric coverage | 6/6 | All centrics represented |
| Max correlation | < 0.80 | No pair exceeds threshold |

### 8.2 Prediction Success (Post-Training)

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Direction accuracy (>2σ) | ≥ 99% | % correct when |BQX| > 2σ |
| Direction accuracy (>1σ) | ≥ 95% | % correct when |BQX| > 1σ |
| Extreme recall | ≥ 70% | % of extremes correctly predicted |
| Extreme precision | ≥ 60% | % of extreme predictions correct |

---

## APPENDIX: FEATURE SELECTION SQL TEMPLATES

### A.1 Direction Discrimination Query

```sql
CREATE OR REPLACE TABLE `bqx_ml_v3_analytics.feature_direction_scores` AS
WITH extreme_features AS (
    SELECT
        f.*,
        t.target_value,
        SIGN(t.target_value) AS actual_direction,
        SIGN(f.feature_value) AS feature_direction
    FROM `bqx_ml_v3_features.all_features` f
    JOIN `bqx_ml_v3_analytics.targets` t USING (timestamp)
    WHERE ABS(f.feature_value) > 2 * f.feature_stddev
)
SELECT
    feature_name,
    COUNT(*) AS extreme_samples,
    SUM(CASE WHEN actual_direction = -feature_direction THEN 1 ELSE 0 END)
        / COUNT(*) AS direction_accuracy
FROM extreme_features
GROUP BY feature_name
HAVING COUNT(*) >= 500;
```

### A.2 Extreme Correlation Query

```sql
CREATE OR REPLACE TABLE `bqx_ml_v3_analytics.feature_extreme_correlations` AS
WITH extreme_bqx AS (
    SELECT *
    FROM `bqx_ml_v3_features.feature_target_joined`
    WHERE ABS(target_value) > 2 * (SELECT STDDEV(target_value) FROM `bqx_ml_v3_features.feature_target_joined`)
)
SELECT
    feature_name,
    CORR(feature_value, target_value) AS extreme_correlation,
    COUNT(*) AS extreme_samples
FROM extreme_bqx
GROUP BY feature_name
HAVING COUNT(*) >= 500;
```

### A.3 Composite Score Query

```sql
CREATE OR REPLACE TABLE `bqx_ml_v3_analytics.feature_composite_scores` AS
SELECT
    d.feature_name,
    d.direction_accuracy * 100 AS direction_score,
    ABS(e.extreme_correlation) * 500 AS extreme_score,
    r.reversal_correlation * 100 AS reversal_score,
    c.sign_consistency * 100 AS regime_score,
    (0.30 * d.direction_accuracy * 100 +
     0.40 * ABS(e.extreme_correlation) * 500 +
     0.15 * r.reversal_correlation * 100 +
     0.15 * c.sign_consistency * 100) AS composite_score
FROM feature_direction_scores d
JOIN feature_extreme_correlations e USING (feature_name)
JOIN feature_reversal_scores r USING (feature_name)
JOIN feature_regime_consistency c USING (feature_name)
ORDER BY composite_score DESC;
```

---

**END OF DOCUMENT**
