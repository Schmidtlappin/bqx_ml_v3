# BQX-ML-M007: Semantic Feature Compatibility Mandate
**Mandate ID**: BQX-ML-M007
**Status**: P0-CRITICAL ARCHITECTURAL REQUIREMENT
**Issued**: 2025-12-13
**Authority**: Chief Engineer
**Scope**: All feature comparison tables (COV, TRI, VAR)
**Supersedes**: None (complements M005, M006)

---

## Executive Summary

This mandate establishes **semantic compatibility rules** for cross-feature comparisons in COV/TRI/VAR tables. Features can only be compared if they share semantic meaning, units, and valid arithmetic operations.

**Critical Requirement**: All comparison tables MUST only compare features from the same semantic group.

---

## Mandate Statement

> **ALL feature-to-feature comparisons in COV, TRI, and VAR tables SHALL be restricted to features within the same semantic compatibility group. Comparisons across incompatible groups are PROHIBITED.**

---

## Rationale

### The Problem: Invalid Feature Comparisons

Without semantic compatibility rules, BQX-ML-M006 (Maximize Comparisons Mandate) would allow:

```sql
-- ❌ INVALID: Comparing raw price to oscillator
SELECT
  close_idx - bqx_45 AS spread  -- 1.1 - 0.5 = 0.6 (NONSENSE!)
FROM pair1, pair2
```

**Why this is wrong:**
- `close_idx`: Raw price in currency units (EURUSD ~1.1, USDJPY ~150)
- `bqx_45`: Normalized momentum oscillator (range: -1 to +1)
- Different scales, different units, different meanings
- The "spread" has no interpretable meaning
- ML models learn spurious patterns

### The Solution: Semantic Grouping

With semantic compatibility:

```sql
-- ✅ VALID: Comparing same semantic type
SELECT
  pair1_lin_term_45 - pair2_lin_term_45 AS trend_divergence  -- Both linear trend coefficients
FROM pair1_reg, pair2_reg
```

**Why this is correct:**
- Both features measure linear trend (same semantic meaning)
- Both in same units (rate of change per interval)
- Spread represents "difference in trend strength" (interpretable)
- ML can learn meaningful trend divergence patterns

---

## Semantic Compatibility Groups

### Group 1: Regression Features ✅
**Features**: 35 per pair (5 types × 7 windows)
```
lin_term_45...2880      (linear trend contribution)
quad_term_45...2880     (quadratic curvature contribution)
lin_coef_45...2880      (linear slope coefficient β₁)
quad_coef_45...2880     (quadratic curvature coefficient β₂)
residual_45...2880      (deviation from polynomial fit)
```

**Why comparable**: All derived from polynomial regression, represent trend components
**Valid operations**:
- Spread: `pair1_lin_term_45 - pair2_lin_term_45` (trend divergence)
- Ratio: `pair1_quad_term_45 / pair2_quad_term_45` (relative curvature)
- Correlation: `CORR(pair1_residual_45, pair2_residual_45)` (residual sync)
- Agreement: `SIGN(pair1_lin_term_45) = SIGN(pair2_lin_term_45)` (directional alignment)

**COV table example**:
```sql
CREATE TABLE cov_reg_bqx_eurusd_gbpusd AS
SELECT
  interval_time,
  p1.lin_term_45 AS pair1_lin_term_45,
  p2.lin_term_45 AS pair2_lin_term_45,
  p1.lin_term_45 - p2.lin_term_45 AS trend_divergence_45,
  SIGN(p1.lin_term_45) = SIGN(p2.lin_term_45) AS trend_agreement_45
FROM reg_bqx_eurusd p1
JOIN reg_bqx_gbpusd p2 USING (interval_time)
```

---

### Group 2: Statistical Aggregates ✅
**Features**: 63 per pair (9 types × 7 windows)
```
mean_45...2880, std_45...2880, min_45...2880, max_45...2880,
range_45...2880, sum_45...2880, count_45...2880,
first_45...2880, last_45...2880
```

**Why comparable**: All statistical summaries of same underlying data stream
**Valid operations**:
- Spread: `pair1_mean_45 - pair2_mean_45` (average divergence)
- Ratio: `pair1_std_45 / pair2_std_45` (relative volatility)
- Z-score: `(pair1_mean_45 - AVG(pair2_mean_45)) / STDDEV(pair2_mean_45)`

---

### Group 3: Normalized Metrics ✅
**Features**: 28 per pair (4 types × 7 windows)
```
zscore_45...2880      (z-score normalization)
position_45...2880    (percentile position 0-1)
cv_45...2880          (coefficient of variation)
deviation_45...2880   (deviation from mean)
```

**Why comparable**: All dimensionless, normalized to comparable scales
**Valid operations**:
- Spread: `pair1_zscore_45 - pair2_zscore_45` (normalized divergence)
- Agreement: `SIGN(pair1_zscore_45) = SIGN(pair2_zscore_45)` (directional sync)
- Magnitude: `ABS(pair1_zscore_45 - pair2_zscore_45)` (divergence strength)

---

### Group 4: Directional Indicators ✅
**Features**: 21 per pair (3 types × 7 windows)
```
dir_45...2880          (directional alignment: -1/0/+1)
direction_45...2880    (trend direction: up/down/flat)
slope_45...2880        (directional slope)
```

**Why comparable**: All measure directional tendency
**Valid operations**:
- Agreement: `pair1_dir_45 = pair2_dir_45` (directional sync)
- Spread: `pair1_slope_45 - pair2_slope_45` (slope divergence)
- Match rate: `AVG(pair1_direction_45 = pair2_direction_45)` (alignment frequency)

---

### Group 5: Momentum Oscillators ✅
**Features**: 7 per pair (1 type × 7 windows)
```
bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
mom_45, mom_90, mom_180, mom_360, mom_720, mom_1440, mom_2880
```

**Why comparable**: All measure momentum/rate of change, normalized oscillators
**Valid operations**:
- Spread: `pair1_bqx_45 - pair2_bqx_45` (momentum divergence)
- Ratio: `pair1_bqx_45 / pair2_bqx_45` (relative momentum)
- Correlation: `CORR(pair1_bqx_45, pair2_bqx_45)` (momentum sync)

**NOTE**: Current COV tables already implement this correctly (using bqx_45 as val1/val2)

---

### Group 6: Volatility Measures ✅
**Features**: 21 per pair (3 types × 7 windows)
```
atr_45...2880          (average true range)
volatility_45...2880   (realized volatility)
vol_ratio_45...2880    (volatility ratio)
```

**Why comparable**: All measure price/value variability
**Valid operations**:
- Ratio: `pair1_atr_45 / pair2_atr_45` (relative volatility)
- Spread: `pair1_volatility_45 - pair2_volatility_45` (volatility divergence)
- Regime: `IF(pair1_atr_45 > pair2_atr_45, 'p1_more_volatile', 'p2_more_volatile')`

---

### Group 7: Derivative Features ✅
**Features**: 14 per pair (2 types × 7 windows)
```
first_derivative_45...2880    (rate of change)
second_derivative_45...2880   (acceleration)
```

**Why comparable**: All measure rate of change (first) or acceleration (second)
**Valid operations**:
- Spread: `pair1_first_derivative_45 - pair2_first_derivative_45`
- Agreement: `SIGN(pair1_second_derivative_45) = SIGN(pair2_second_derivative_45)`

---

### Group 8: Mean Reversion Indicators ✅
**Features**: 14 per pair (2 types × 7 windows)
```
reversion_signal_45...2880     (binary signal: 0/1)
reversion_strength_45...2880   (strength: 0-1)
```

**Why comparable**: All measure mean reversion tendency
**Valid operations**:
- Agreement: `pair1_reversion_signal_45 = pair2_reversion_signal_45`
- Spread: `pair1_reversion_strength_45 - pair2_reversion_strength_45`

---

### Group 9: Correlation Coefficients ✅
**Features**: 56 per pair (8 ETFs × 7 windows)
```
corr_spy_45...2880, corr_gld_45...2880, corr_vix_45...2880,
corr_ewa_45...2880, corr_ewg_45...2880, corr_ewj_45...2880,
corr_ewu_45...2880, corr_uup_45...2880
```

**Why comparable**: All correlation coefficients, dimensionless [-1, 1]
**Valid operations**:
- Spread: `pair1_corr_spy_45 - pair2_corr_spy_45` (relative SPY exposure)
- Max/Min: `GREATEST(pair1_corr_spy_45, pair2_corr_spy_45)` (strongest correlation)
- Divergence: `ABS(pair1_corr_spy_45 - pair2_corr_spy_45)` (correlation gap)

---

## Incompatible Features (PROHIBITED)

### ❌ Raw Prices
```
close_idx, open, high, low, close
```
**Why incompatible**: Absolute values, different scales per pair (EURUSD ~1.1, USDJPY ~150)
**Prohibition**: NEVER compare raw prices across pairs in COV/TRI tables

### ❌ Count/Integer Features
```
count_*, bar_count_*
```
**Why incompatible**: Different semantic meaning from continuous metrics
**Prohibition**: NEVER use in spread/ratio operations

### ❌ Timestamp/Categorical Features
```
interval_time, session, regime, error_regime, pair
```
**Why incompatible**: Non-numerical or categorical
**Prohibition**: NEVER use in arithmetic operations

---

## Valid Comparison Operations by Group

### Spread (Divergence)
**Valid for**: Groups 1-9
**Formula**: `pair1_feature - pair2_feature`
**Interpretation**: Difference/divergence between pairs
**Example**: `pair1_lin_term_45 - pair2_lin_term_45` = trend divergence

### Ratio (Relative Magnitude)
**Valid for**: Groups 1, 2, 3, 5, 6, 9
**Formula**: `pair1_feature / NULLIF(pair2_feature, 0)`
**Interpretation**: Relative strength/magnitude
**Example**: `pair1_std_45 / pair2_std_45` = relative volatility

### Agreement (Directional Sync)
**Valid for**: Groups 3, 4, 7, 8
**Formula**: `SIGN(pair1_feature) = SIGN(pair2_feature)`
**Interpretation**: Directional alignment (returns 0 or 1)
**Example**: `SIGN(pair1_zscore_45) = SIGN(pair2_zscore_45)` = normalized direction match

### Correlation (Co-movement)
**Valid for**: Groups 1, 2, 5, 6
**Formula**: `CORR(pair1_feature, pair2_feature) OVER window`
**Interpretation**: Rolling correlation strength
**Example**: `CORR(pair1_bqx_45, pair2_bqx_45)` = momentum synchronization

---

## Schema Validation Rules

### Rule 1: Feature Group Homogeneity
**Requirement**: All pair features in a comparison table MUST come from the same semantic group

**Valid COV table**:
```sql
-- ✅ All features from Group 1 (Regression)
CREATE TABLE cov_reg_bqx_eurusd_gbpusd AS
SELECT
  interval_time,
  p1.lin_term_45, p1.quad_term_45, p1.residual_45,  -- Group 1
  p2.lin_term_45, p2.quad_term_45, p2.residual_45   -- Group 1
FROM reg_bqx_eurusd p1 JOIN reg_bqx_gbpusd p2 USING (interval_time)
```

**Invalid COV table**:
```sql
-- ❌ Mixing Group 1 (Regression) with Group 2 (Aggregates)
CREATE TABLE cov_mixed_eurusd_gbpusd AS  -- PROHIBITED!
SELECT
  interval_time,
  p1.lin_term_45,  -- Group 1: Regression
  p2.mean_45       -- Group 2: Aggregates ❌ INCOMPATIBLE!
FROM ...
```

### Rule 2: Window Consistency
**Requirement**: Compared features MUST use the same window size

**Valid**:
```sql
pair1_lin_term_45 - pair2_lin_term_45  -- ✅ Both window 45
```

**Invalid**:
```sql
pair1_lin_term_45 - pair2_lin_term_90  -- ❌ Different windows
```

### Rule 3: Variant Separation
**Requirement**: BQX and IDX variants MUST NOT be mixed in same comparison

**Valid**:
```sql
-- ✅ Both BQX variant
FROM reg_bqx_eurusd p1 JOIN reg_bqx_gbpusd p2
```

**Invalid**:
```sql
-- ❌ Mixing BQX and IDX variants
FROM reg_bqx_eurusd p1 JOIN reg_idx_gbpusd p2  -- PROHIBITED!
```

---

## Implementation Requirements

### Phase 1: COV Tables (BQX-ML-M005 Compliance)
**Requirement**: Add Group 1 (Regression) features to all COV tables

**Minimum schema** (56 columns):
```
-- Base features (14 columns) - existing
interval_time, pair1, pair2, val1, val2, spread, ratio,
spread_ma_45, spread_ma_180, spread_std_45, spread_zscore,
sign_agreement, rolling_agreement_45, mean_reversion_signal

-- Group 1: Regression features (42 columns) - NEW
pair1_lin_term_45...2880 (7 cols)
pair1_quad_term_45...2880 (7 cols)
pair1_residual_45...2880 (7 cols)
pair2_lin_term_45...2880 (7 cols)
pair2_quad_term_45...2880 (7 cols)
pair2_residual_45...2880 (7 cols)
```

### Phase 1.5: Multi-Group COV Tables (Extended)
**Requirement**: Create separate COV variant tables for each semantic group

**Table naming convention**:
```
cov_reg_bqx_{pair1}_{pair2}    -- Group 1: Regression features
cov_agg_bqx_{pair1}_{pair2}    -- Group 2: Aggregates (already exists)
cov_vol_bqx_{pair1}_{pair2}    -- Group 6: Volatility features
cov_corr_bqx_{pair1}_{pair2}   -- Group 9: Correlation features
```

**Rationale**: Each semantic group gets its own COV tables to maintain group homogeneity

### Phase 2: TRI Tables
**Requirement**: Add Group 1 (Regression) features from all 3 triangle legs

**Minimum schema** (78 columns):
```
-- Base features (15 columns) - existing
interval_time, base_curr, quote_curr, cross_curr,
pair1_val, pair2_val, pair3_val, synthetic_val, tri_error,
error_ma_45, error_ma_180, error_std_180, error_zscore,
arb_opportunity, error_regime

-- Group 1: Regression features (63 columns) - NEW
pair1_lin_term_45...2880, pair1_quad_term_45...2880, pair1_residual_45...2880 (21 cols)
pair2_lin_term_45...2880, pair2_quad_term_45...2880, pair2_residual_45...2880 (21 cols)
pair3_lin_term_45...2880, pair3_quad_term_45...2880, pair3_residual_45...2880 (21 cols)
```

### Phase 3: VAR Tables
**Requirement**: Add Group 1 (Regression) aggregated features across currency families

**Minimum schema** (150 columns):
```
-- Base features (129 columns) - existing (ALL 7 WINDOWS ALREADY!)
interval_time, currency_family, pairs_in_family,
var_mean_45...2880, avg_mean_45...2880 (×9 agg types × 7 windows)

-- Group 1: Regression features aggregated (21 columns) - NEW
var_lin_term_45...2880, avg_lin_term_45...2880 (×3 reg types × 7 windows)
```

---

## Validation & Enforcement

### Automated Validation
All generation scripts MUST include semantic compatibility checks:

```python
def validate_feature_compatibility(feature1, feature2):
    """Validate two features are semantically compatible."""
    group1 = get_semantic_group(feature1)
    group2 = get_semantic_group(feature2)

    if group1 != group2:
        raise ValueError(
            f"Semantic incompatibility: {feature1} (Group {group1}) "
            f"cannot be compared with {feature2} (Group {group2})"
        )

    window1 = extract_window(feature1)
    window2 = extract_window(feature2)

    if window1 != window2:
        raise ValueError(
            f"Window mismatch: {feature1} (window {window1}) "
            f"vs {feature2} (window {window2})"
        )

    return True
```

### Schema Audit
All COV/TRI/VAR tables MUST pass semantic compatibility audit:

```sql
-- Audit query to detect incompatible features
SELECT
  table_name,
  column_name,
  semantic_group,
  COUNT(DISTINCT semantic_group) OVER (PARTITION BY table_name) AS group_count
FROM information_schema.columns
WHERE table_name LIKE 'cov_%' OR table_name LIKE 'tri_%' OR table_name LIKE 'var_%'
HAVING group_count > 1  -- ❌ VIOLATION: Multiple semantic groups in one table
```

### Manual Review Checkpoints
Before regenerating any comparison table:
1. ✅ Identify semantic group of source features
2. ✅ Verify all features come from same group
3. ✅ Confirm window sizes match
4. ✅ Validate variant separation (BQX ≠ IDX)
5. ✅ Document group in table metadata

---

## Relationship to Other Mandates

### BQX-ML-M005: Regression Feature Architecture Mandate
**Relationship**: M007 ENABLES M005 implementation
**How**: Defines Group 1 (Regression) as semantically compatible group
**Impact**: Ensures regression features can be safely compared in COV/TRI/VAR

### BQX-ML-M006: Maximize Feature Comparisons Mandate
**Relationship**: M007 CONSTRAINS M006 execution
**How**: Limits "maximize" to semantically compatible features only
**Impact**: Prevents invalid comparisons while maximizing valid ones

**M006 without M007** = Chaos (invalid feature mixes)
**M006 with M007** = Structured maximization (only valid comparisons)

---

## Success Criteria

### Criterion 1: Zero Invalid Comparisons
**Metric**: 0 tables mixing incompatible semantic groups
**Validation**: Automated schema audit (SQL query above)
**Target**: 100% compliance across all 3,785 comparison tables

### Criterion 2: Complete Group Coverage
**Metric**: All 9 semantic groups represented in comparison tables
**Validation**: Table count per group
**Target**:
- Group 1 (Regression): 3,785 tables (COV 3,528 + TRI 194 + VAR 63)
- Group 2 (Aggregates): 1,848 tables (COV only, already exists)
- Groups 3-9: TBD based on Phase 3+ rollout

### Criterion 3: Documentation Completeness
**Metric**: Every comparison table has semantic_group metadata
**Validation**: Metadata completeness audit
**Target**: 100% of tables documented

---

## Cost & Timeline

### Phase 1: Regression Group Compliance (M005)
- **Tables**: 3,785 (COV 3,528 + TRI 194 + VAR 63)
- **Cost**: $150-200
- **Time**: 18-24 hours
- **Status**: MANDATORY for M005 compliance

### Phase 1.5: Multi-Group COV Tables
- **Tables**: +3,528 (Group 2), +3,528 (Group 6), +896 (Group 9) = 7,952 new tables
- **Cost**: $300-400
- **Time**: 24-36 hours
- **Status**: RECOMMENDED for full semantic coverage

### Phase 2-3: Extended Groups
- **Tables**: TBD (Groups 3, 4, 7, 8)
- **Cost**: $200-300
- **Time**: 18-24 hours
- **Status**: OPTIONAL (defer until Phase 1 complete)

---

## Approval & Authority

**Issued by**: Chief Engineer
**Date**: 2025-12-13
**Approval**: USER DIRECTIVE
**Binding**: YES - All future feature engineering MUST comply
**Review cycle**: Annual or when new feature types added

---

## Appendix A: Semantic Group Reference

| Group | Features | Count/Pair | Compatible Operations | Example |
|-------|----------|------------|----------------------|---------|
| 1. Regression | lin_term, quad_term, lin_coef, quad_coef, residual × 7 windows | 35 | spread, ratio, corr, agreement | `p1_lin_term_45 - p2_lin_term_45` |
| 2. Aggregates | mean, std, min, max, range, sum, count, first, last × 7 windows | 63 | spread, ratio, zscore | `p1_mean_45 / p2_mean_45` |
| 3. Normalized | zscore, position, cv, deviation × 7 windows | 28 | spread, agreement | `p1_zscore_45 - p2_zscore_45` |
| 4. Directional | dir, direction, slope × 7 windows | 21 | agreement, spread | `p1_dir_45 = p2_dir_45` |
| 5. Momentum | bqx, mom × 7 windows | 14 | spread, ratio, corr | `p1_bqx_45 - p2_bqx_45` |
| 6. Volatility | atr, volatility, vol_ratio × 7 windows | 21 | ratio, spread | `p1_atr_45 / p2_atr_45` |
| 7. Derivatives | first_derivative, second_derivative × 7 windows | 14 | spread, agreement | `p1_d1_45 - p2_d1_45` |
| 8. Mean Reversion | reversion_signal, reversion_strength × 7 windows | 14 | agreement, spread | `p1_rev_sig_45 = p2_rev_sig_45` |
| 9. Correlation | corr_spy, corr_gld, corr_vix, ... × 7 windows | 56 | spread, max/min | `p1_corr_spy_45 - p2_corr_spy_45` |

**Total comparable features per pair**: 266 (across all 9 groups)

---

## Appendix B: Incompatible Feature Reference

| Feature Type | Examples | Why Incompatible | Prohibition |
|--------------|----------|------------------|-------------|
| Raw Prices | close_idx, open, high, low | Different absolute scales per pair | NEVER compare across pairs |
| Counts | count_*, bar_count_* | Integer semantics, not continuous | NEVER use in spread/ratio |
| Timestamps | interval_time, date, hour | Non-numeric identifier | NEVER use in arithmetic |
| Categorical | session, regime, error_regime, pair | Non-numeric labels | NEVER use in arithmetic |

---

**END OF MANDATE**
