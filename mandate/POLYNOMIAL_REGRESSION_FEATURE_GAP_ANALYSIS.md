# POLYNOMIAL REGRESSION FEATURE GAP ANALYSIS

**Date**: 2025-11-29
**Status**: CRITICAL GAP IDENTIFIED
**Impact**: 492 tables require refactoring
**Priority**: HIGH

---

## Executive Summary

A critical gap has been identified in the regression feature implementation. The mandate specifies **quadratic polynomial regression features** (lin_term, quad_term, residual, r2), but the current implementation only contains **simple linear regression features** (slope, deviation). This affects both IDX and BQX datasets and cascades to all downstream tables.

---

## 1. MANDATED FEATURES vs IMPLEMENTED FEATURES

### Mandated (BQX_ML_V3_FEATURE_INVENTORY.md + AirTable MP02.P16.S01)

```
Quadratic regression: y = ax² + bx + c

Per Window [45, 90, 180, 360, 720, 1440, 2880]:

POLYNOMIAL COEFFICIENTS:
- Quadratic coefficient (a)     → quad_term
- Linear coefficient (b)        → lin_term
- Constant term (c)             → const_term

VARIANCE METRICS (USER MANDATE v2.1 - AirTable MP02.P16.S01):
- Residual variance (MSE)       → resid_var = mean(residuals²)
- Total variance of y           → total_var = var(y)
- R² score                      → r2 = 1 - (resid_var / total_var)
- Root mean squared error       → rmse = sqrt(resid_var)
- Normalized residual           → resid_norm = residuals[-1] / mean(y)

RESIDUAL METRICS:
- Residual standard deviation   → residual_std
- Residual min/max              → residual_min, residual_max
- Prediction error              → pred_error = residuals[-1]
- Residual distribution metrics → resid_skew, resid_kurt

DERIVED FEATURES:
- Curvature sign                → curv_sign
- Trend strength                → trend_strength = lin_term / resid_std
- Acceleration                  → acceleration = 2 * quad_term
- Forecast next 5 intervals     → forecast_5
- Confidence interval bounds    → ci_lower, ci_upper
```

**Critical User Mandate (AirTable MP02.P16.S01):**
```
For each window N:
- lin_term = β₁ × N (linear slope at endpoint)
- quad_term = β₂ × N² (curvature at endpoint)
- resid_var = MSE (residual variance/noise)
- total_var = variance of y
- r2 = 1 - (MSR / total_var)

Endpoint Evaluation: x = N (not midpoint)
```

### Currently Implemented in reg_eurusd

```sql
-- Current columns (10 per window × 7 windows = 70 features)
reg_slope_{W}       -- Linear slope only (NOT from polynomial fit)
reg_deviation_{W}   -- Value deviation from regression line
reg_direction_{W}   -- Trend direction (+1/-1)
reg_mean_{W}        -- Mean value in window
reg_std_{W}         -- Standard deviation
reg_zscore_{W}      -- Z-score
reg_min_{W}         -- Minimum value
reg_max_{W}         -- Maximum value
reg_range_pct_{W}   -- Range as percentage
reg_first_{W}       -- First value in window
```

### Gap Analysis

**CRITICAL: These features apply to BOTH IDX and BQX variants:**
- **IDX**: `reg_{pair}` tables (28) - source = close price
- **BQX**: `reg_bqx_{pair}` tables (28) - source = BQX oscillator

| Feature | Mandated | Implemented | Status | Applies To |
|---------|----------|-------------|--------|------------|
| quad_term | ✓ | ✗ | **MISSING** | IDX + BQX |
| lin_term | ✓ | Partial (reg_slope) | **REBUILD** | IDX + BQX |
| const_term | ✓ | ✗ | **MISSING** | IDX + BQX |
| **resid_var** | ✓ (MSE) | ✗ | **MISSING** | IDX + BQX |
| **total_var** | ✓ | ✗ | **MISSING** | IDX + BQX |
| r2 | ✓ | ✗ | **MISSING** | IDX + BQX |
| rmse | ✓ | ✗ | **MISSING** | IDX + BQX |
| resid_norm | ✓ | ✗ | **MISSING** | IDX + BQX |
| residual_std | ✓ | ✗ | **MISSING** | IDX + BQX |
| residual_min | ✓ | ✗ | **MISSING** | IDX + BQX |
| residual_max | ✓ | ✗ | **MISSING** | IDX + BQX |
| pred_error | ✓ | ✗ | **MISSING** | IDX + BQX |
| curv_sign | ✓ | ✗ | **MISSING** | IDX + BQX |
| acceleration | ✓ | ✗ | **MISSING** | IDX + BQX |
| forecast_5 | ✓ | ✗ | **MISSING** | IDX + BQX |
| ci_lower/upper | ✓ | ✗ | **MISSING** | IDX + BQX |
| resid_skew/kurt | ✓ | ✗ | **MISSING** | IDX + BQX |

---

## 2. MATHEMATICAL SPECIFICATION

### Quadratic Polynomial Fit

```python
# For each rolling window of size W
x = np.arange(W)  # [0, 1, 2, ..., W-1]
y = values[-W:]   # Last W values (IDX prices or BQX values)

# Fit 2nd degree polynomial: y = ax² + bx + c
coeffs = np.polyfit(x, y, 2)  # Returns [a, b, c]

# Extract coefficients
quad_term = coeffs[0]    # Quadratic coefficient (curvature)
lin_term = coeffs[1]     # Linear coefficient (slope)
const_term = coeffs[2]   # Constant term (intercept)
```

### Residual Calculation

```python
# Fitted values
y_hat = np.polyval(coeffs, x)  # = a*x² + b*x + c

# Residuals
residuals = y - y_hat

# Residual metrics
residual_std = np.std(residuals)
residual_min = np.min(residuals)
residual_max = np.max(residuals)
resid_skew = scipy.stats.skew(residuals)
resid_kurt = scipy.stats.kurtosis(residuals)
```

### Variance Metrics (USER MANDATE v2.1 - AirTable MP02.P16.S01)

```python
# USER MANDATE: resid_var = MSE, total_var = variance of y
# Source: AirTable MP02.P16.S01 "Regression Table Generation"

# Variance calculations (CRITICAL - IDX and BQX)
resid_var = np.mean(residuals**2)  # MSE = Mean Squared Error
total_var = np.var(y)              # Total variance of y

# R² score (derived from variances)
r2 = 1 - (resid_var / total_var) if total_var > 0 else 0

# RMSE (derived from resid_var)
rmse = np.sqrt(resid_var)

# Prediction error (last residual)
pred_error = residuals[-1]
```

**Formula Verification (AirTable MP02.P16.S01):**
```
For each window N:
- resid_var = MSE (residual variance/noise)
- total_var = variance of y
- r2 = 1 - (MSR / total_var)
```

### Normalization (Mandated)

```python
y_mean = np.mean(y)

# Normalized coefficients (dimensionless)
quad_norm = (quad_term * (W-1)**2) / y_mean if y_mean != 0 else 0
lin_norm = (lin_term * (W-1)) / y_mean if y_mean != 0 else 0
resid_norm = residuals[-1] / y_mean if y_mean != 0 else 0
```

### Derived Features

```python
# Curvature sign (acceleration direction)
curv_sign = np.sign(quad_term)  # +1 = accelerating, -1 = decelerating

# Acceleration (2nd derivative)
acceleration = 2 * quad_term

# Trend strength (slope normalized by volatility)
trend_strength = lin_term / residual_std if residual_std > 0 else 0

# Forecast next 5 intervals
forecast_5 = np.polyval(coeffs, W + 5) - np.polyval(coeffs, W)

# Confidence intervals (95%)
se = residual_std / np.sqrt(W)
ci_lower = y_hat[-1] - 1.96 * se
ci_upper = y_hat[-1] + 1.96 * se
```

---

## 3. IDX vs BQX CONTEXT

### IDX Dataset (Price-Derived)

**Source**: Raw OHLCV price data from IBKR
**Table Pattern**: `reg_{pair}` (e.g., `reg_eurusd`)
**Source Column**: `close` price

**Polynomial Fit Interpretation**:
- **quad_term**: Price acceleration/deceleration
- **lin_term**: Price trend rate (pips per interval)
- **residual**: Deviation from polynomial trend
- **r2**: How well polynomial captures price movement

### BQX Dataset (Momentum-Derived)

**Source**: BQX oscillator values (bid-ask spread momentum)
**Table Pattern**: `reg_bqx_{pair}` (e.g., `reg_bqx_eurusd`)
**Source Column**: `bqx_{window}` values

**Polynomial Fit Interpretation**:
- **quad_term**: Momentum acceleration (oscillator curvature)
- **lin_term**: Momentum trend rate
- **residual**: Deviation from momentum trend
- **r2**: How well polynomial captures momentum behavior

### Key Difference

| Aspect | IDX | BQX |
|--------|-----|-----|
| Source | Price (close) | BQX oscillator |
| Unit | Pips | Dimensionless |
| Trend | Price direction | Momentum direction |
| Curvature | Price acceleration | Momentum acceleration |
| Predictive use | Price reversal | Momentum exhaustion |

---

## 4. TABLE DEPENDENCY CASCADE

### Primary Tables (56 total)

| Pattern | Count | Action |
|---------|-------|--------|
| reg_{pair} | 28 | REBUILD with polynomial features |
| reg_bqx_{pair} | 28 | REBUILD with polynomial features |

### Downstream Tables (436 total)

| Pattern | Count | Depends On | Action |
|---------|-------|------------|--------|
| cov_reg_{pair1}_{pair2} | 168 | reg_{pair} | REBUILD after reg_ |
| cov_reg_bqx_{pair1}_{pair2} | 168 | reg_bqx_{pair} | REBUILD after reg_bqx_ |
| var_reg_{currency} | 28 | reg_{pairs} | REBUILD after reg_ |
| csi_reg_{currency} | 32 | reg_{pairs} | REBUILD after reg_ |
| tri_reg_{curr1}_{curr2}_{curr3} | 36 | reg_{pairs} | REBUILD after reg_ |
| mkt_reg | 4 | All reg_ | REBUILD after all reg_ |

### Total Impact: 492 Tables

---

## 5. NEW COLUMN SPECIFICATION

### Per-Window Columns (IDX and BQX)

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

```sql
-- Polynomial coefficients (raw)
reg_quad_term_{W}     FLOAT64  -- Quadratic coefficient
reg_lin_term_{W}      FLOAT64  -- Linear coefficient
reg_const_term_{W}    FLOAT64  -- Constant term

-- Polynomial coefficients (normalized)
reg_quad_norm_{W}     FLOAT64  -- Normalized quadratic
reg_lin_norm_{W}      FLOAT64  -- Normalized linear

-- Goodness of fit
reg_r2_{W}            FLOAT64  -- R² score [0, 1]
reg_rmse_{W}          FLOAT64  -- Root mean squared error

-- Residual metrics
reg_resid_std_{W}     FLOAT64  -- Residual std deviation
reg_resid_min_{W}     FLOAT64  -- Minimum residual
reg_resid_max_{W}     FLOAT64  -- Maximum residual
reg_resid_last_{W}    FLOAT64  -- Last residual (pred error)
reg_resid_skew_{W}    FLOAT64  -- Residual skewness
reg_resid_kurt_{W}    FLOAT64  -- Residual kurtosis

-- Derived features
reg_curv_sign_{W}     INT64    -- Curvature sign (+1/-1)
reg_acceleration_{W}  FLOAT64  -- 2 * quad_term
reg_trend_str_{W}     FLOAT64  -- lin_term / resid_std
reg_forecast_5_{W}    FLOAT64  -- Predicted change in 5 intervals

-- Confidence intervals
reg_ci_lower_{W}      FLOAT64  -- 95% CI lower bound
reg_ci_upper_{W}      FLOAT64  -- 95% CI upper bound

-- Existing columns (retain)
reg_slope_{W}         FLOAT64  -- Simple slope (for backward compat)
reg_deviation_{W}     FLOAT64  -- Deviation from fit
reg_direction_{W}     INT64    -- Trend direction
reg_mean_{W}          FLOAT64  -- Window mean
reg_std_{W}           FLOAT64  -- Window std
reg_zscore_{W}        FLOAT64  -- Z-score
reg_min_{W}           FLOAT64  -- Window min
reg_max_{W}           FLOAT64  -- Window max
reg_range_pct_{W}     FLOAT64  -- Range percentage
reg_first_{W}         FLOAT64  -- First value
```

### New Column Count Per Table

- **New columns**: 18 per window × 7 windows = **126 new columns**
- **Existing columns**: 10 per window × 7 windows = 70 columns (retain)
- **Total per table**: **196 columns**

---

## 6. REMEDIATION PLAN

### Phase 1: Primary reg_ Tables (56 tables)

**Duration**: ~2 hours
**Parallel Workers**: 8

```
Step 1.1: Create SQL generator for polynomial features
Step 1.2: Execute for reg_{pair} (28 tables)
Step 1.3: Execute for reg_bqx_{pair} (28 tables)
Step 1.4: Validate row counts and column schemas
```

### Phase 2: Covariance Tables (336 tables)

**Duration**: ~4 hours
**Parallel Workers**: 16
**Dependency**: Phase 1 complete

```
Step 2.1: Update cov_ SQL generators to include new columns
Step 2.2: Execute for cov_reg_{pair1}_{pair2} (168 tables)
Step 2.3: Execute for cov_reg_bqx_{pair1}_{pair2} (168 tables)
Step 2.4: Validate covariance calculations
```

### Phase 3: Variance Tables (28 tables)

**Duration**: ~30 minutes
**Parallel Workers**: 8
**Dependency**: Phase 1 complete

```
Step 3.1: Update var_ SQL generators
Step 3.2: Execute for var_reg_{currency} (28 tables)
Step 3.3: Validate variance calculations
```

### Phase 4: Currency Strength & Triangular (68 tables)

**Duration**: ~1 hour
**Parallel Workers**: 8
**Dependency**: Phase 1 complete

```
Step 4.1: Update csi_ and tri_ SQL generators
Step 4.2: Execute for csi_reg_{currency} (32 tables)
Step 4.3: Execute for tri_reg_{curr1}_{curr2}_{curr3} (36 tables)
Step 4.4: Validate aggregations
```

### Phase 5: Market Tables (4 tables)

**Duration**: ~15 minutes
**Dependency**: All phases complete

```
Step 5.1: Update mkt_reg SQL
Step 5.2: Execute for mkt_reg, mkt_reg_bqx (4 tables)
Step 5.3: Final validation
```

### Total Estimated Duration: ~8 hours

---

## 7. CORRELATION ANALYSIS EXPANSION

### Current Correlation Features (817)

The extreme correlation analysis covered 817 features but **excluded** polynomial regression features because they don't exist.

### Expected Features After Remediation

| Category | Current | After Remediation |
|----------|---------|-------------------|
| reg_* | 70/table | 196/table |
| Per EURUSD pair | ~70 | ~196 |
| Total regression features | 140 | 392 |
| **Expected correlation features** | 817 | **1,069+** |

### New Features to Correlate

```
Per window [45, 90, 180, 360, 720, 1440, 2880]:
- reg_quad_term_{W}
- reg_lin_term_{W}
- reg_r2_{W}
- reg_resid_std_{W}
- reg_resid_last_{W}
- reg_curv_sign_{W}
- reg_acceleration_{W}
- reg_trend_str_{W}
- reg_forecast_5_{W}
```

**New features per variant**: 9 × 7 = 63
**New features total (IDX + BQX)**: 126

---

## 8. BA IMPLEMENTATION DIRECTIVE

### Immediate Actions

1. **HALT** current feature engineering tasks
2. **PRIORITIZE** polynomial regression remediation
3. **CREATE** SQL generators for all new columns
4. **EXECUTE** phased rebuild (492 tables)
5. **VALIDATE** completeness (100% mandate coverage)

### Implementation Order

```
1. scripts/remediate_reg_polynomial.py    -- Primary reg_ tables
2. scripts/remediate_cov_reg.py           -- Covariance tables
3. scripts/remediate_var_csi_tri_reg.py   -- Variance/CSI/Triangular
4. scripts/remediate_mkt_reg.py           -- Market tables
```

### Success Criteria

- [ ] All 56 primary reg_ tables rebuilt with 196 columns
- [ ] All 336 covariance tables rebuilt with new correlation pairs
- [ ] All 28 variance tables rebuilt
- [ ] All 68 CSI/triangular tables rebuilt
- [ ] All 4 market tables rebuilt
- [ ] Row counts preserved (no data loss)
- [ ] Correlation analysis re-run with expanded features
- [ ] Top 100 reports regenerated

---

## 9. AUTHORIZATION

**This remediation is AUTHORIZED and MANDATED.**

The polynomial regression features are core to the BQX ML V3 mandate. The current implementation represents a significant gap that must be closed to achieve 100% completeness.

**Signed**: Chief Engineer, BQX ML V3
**Date**: 2025-11-29

---

*Document created: 2025-11-29*
*Last updated: 2025-11-29*
