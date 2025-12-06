# Phase Plan: 20% Extreme BQX Correlation Analysis

## Objective
Correlate the 20% most extreme bqx_ oscillation periods (top 10% + bottom 10%) for each pair with 5,000+ polynomial features, using pair-specific thresholds.

---

## Phase 1: Create Pair-Specific 20% Extreme Thresholds Table

**Purpose**: Store the z-score thresholds that define the 20% most extreme values for each pair.

**Output Table**: `bqx_ml_v3_analytics.pair_extreme_thresholds_20pct`

| Column | Description |
|--------|-------------|
| pair | Currency pair (e.g., eurusd) |
| total_observations | Total bqx_45 observations |
| mean_bqx45 | Mean of bqx_45 |
| stddev_bqx45 | Standard deviation (σ) |
| p10_zscore | 10th percentile z-score (bottom 10% threshold) |
| p90_zscore | 90th percentile z-score (top 10% threshold) |
| p10_bqx_value | Actual BQX value at 10th percentile |
| p90_bqx_value | Actual BQX value at 90th percentile |
| extreme_count | Count of observations in 20% extreme range |

**Key**: Each pair has UNIQUE thresholds based on its own distribution.

---

## Phase 2: Generate Pair-Specific Extreme Period Tables

**Purpose**: For each pair, identify timestamps where bqx_45 falls in the 20% extreme range.

**Approach**:
- Bottom 10%: z-score ≤ p10_zscore (pair-specific)
- Top 10%: z-score ≥ p90_zscore (pair-specific)

**Output Table**: `bqx_ml_v3_analytics.pair_extreme_periods_20pct`

| Column | Description |
|--------|-------------|
| pair | Currency pair |
| interval_time | Timestamp of extreme observation |
| bqx_45 | BQX oscillation value |
| zscore | Z-score of the observation |
| extreme_type | 'positive' (top 10%) or 'negative' (bottom 10%) |
| percentile_rank | Exact percentile rank (0-100) |

**Expected Output**:
- ~430K observations per pair (20% of ~2.15M)
- ~12M total observations across 28 pairs
- Equal representation: exactly 20% per pair

---

## Phase 3: Correlate 5,000+ Features Against Pair-Specific Extremes

**Purpose**: Calculate correlations between polynomial features and future price/BQX movements during each pair's extreme periods.

### 3A: Feature Sources
- `reg_bqx_{pair}` tables (BQX variant): ~154 polynomial features per pair
- `reg_{pair}` tables (IDX variant): ~154 polynomial features per pair
- Total: ~308 features × 28 pairs = 8,624 feature-pair combinations

### 3B: Target Variables
For each extreme timestamp, calculate future deltas:
- **Price deltas**: (price[t+h] - price[t]) / price[t]
- **BQX deltas**: bqx_45[t+h] - bqx_45[t]
- **Horizons**: h = [15, 30, 45, 60, 75, 90, 105] minutes

### 3C: Correlation Computation

For each pair:
1. Join `reg_bqx_{pair}` with `pair_extreme_periods_20pct` on interval_time
2. Calculate CORR(feature, delta_h{X}) for each feature × horizon combination
3. Store results with sample counts

**Output Table**: `bqx_ml_v3_analytics.feature_correlations_20pct_extreme`

| Column | Description |
|--------|-------------|
| pair | Currency pair |
| variant | 'bqx' or 'idx' |
| feature_name | Polynomial feature name |
| n_samples | Number of extreme observations used |
| corr_h15 | Correlation at 15-min horizon |
| corr_h30 | Correlation at 30-min horizon |
| corr_h45 | Correlation at 45-min horizon |
| corr_h60 | Correlation at 60-min horizon |
| corr_h75 | Correlation at 75-min horizon |
| corr_h90 | Correlation at 90-min horizon |
| corr_h105 | Correlation at 105-min horizon |
| avg_correlation | Average across all horizons |
| max_correlation | Maximum correlation (any horizon) |

---

## Phase 4: Aggregate and Rank Features

**Purpose**: Identify top-performing features across pairs.

### 4A: Per-Pair Rankings
- Rank features by avg_correlation within each pair
- Identify top 20 features per pair

### 4B: Cross-Pair Aggregation
- Calculate average correlation per feature across ALL 28 pairs
- Identify "universal" features that perform well across multiple pairs

**Output Table**: `bqx_ml_v3_analytics.feature_rankings_20pct_extreme`

| Column | Description |
|--------|-------------|
| feature_name | Polynomial feature name |
| variant | 'bqx' or 'idx' |
| pairs_with_data | Count of pairs with this feature |
| avg_corr_all_pairs | Average correlation across all pairs |
| std_corr_all_pairs | Standard deviation of correlations |
| max_corr_any_pair | Maximum correlation seen in any pair |
| top_pair | Pair with highest correlation |
| consistency_score | % of pairs where |corr| > 0.1 |

---

## Phase 5: Compare and Validate

### 5A: Comparison with 2σ Approach
- Compare new 20% correlations vs old 2σ correlations
- Validate that all pairs now have meaningful sample sizes

### 5B: Feature Classification
- **Universal**: High correlation (>0.3) in >20 pairs
- **Cluster-specific**: High in specific pair groups (majors, crosses, etc.)
- **Pair-specific**: High in only 1-3 pairs

### 5C: Documentation
- Update intelligence files with new methodology
- Document differential correlation based on dataset period factors

---

## Execution Estimates

| Phase | Tables Created | Estimated Rows | Complexity |
|-------|----------------|----------------|------------|
| 1 | 1 | 28 | Low |
| 2 | 1 | ~12M | Medium |
| 3 | 1 | ~8,624 | High (compute-intensive) |
| 4 | 1 | ~308 | Low |
| 5 | - | - | Analysis only |

---

## Key Differences from Previous Approach

| Aspect | Previous (2σ) | New (20%) |
|--------|---------------|-----------|
| Threshold | Fixed ±2σ | Pair-specific percentiles |
| Coverage | 0% - 7.5% (varies) | **20% (uniform)** |
| Pairs with data | 24 of 28 | **28 of 28** |
| Sample size | 0 - 153K per pair | **~430K per pair** |
| Bias | EURUSD-dominated | **Equal representation** |

---

## Ready for Execution?

Confirm to proceed with Phase 1.
