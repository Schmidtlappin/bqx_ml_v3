# CE → BA DIRECTIVE: POLYNOMIAL REGRESSION FEATURE IMPLEMENTATION

**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Date**: 2025-11-29 19:30 UTC
**Priority**: CRITICAL
**Status**: AUTHORIZED AND MANDATED

---

## EXECUTIVE SUMMARY

A critical gap has been identified in the regression feature implementation. The mandate specifies **quadratic polynomial regression features** (quad_term, lin_term, residual, r2), but the current implementation only contains **simple linear regression features** (slope, deviation).

**This directive authorizes and mandates the full remediation of 492 tables.**

---

## SCOPE

### Primary Tables (56)
| Pattern | Count | Action |
|---------|-------|--------|
| reg_{pair} | 28 | REBUILD with polynomial features |
| reg_bqx_{pair} | 28 | REBUILD with polynomial features |

### Derived Tables (436)
| Pattern | Count | Depends On | Action |
|---------|-------|------------|--------|
| cov_reg_{pair1}_{pair2} | 168 | reg_{pair} | REBUILD after reg_ |
| cov_reg_bqx_{pair1}_{pair2} | 168 | reg_bqx_{pair} | REBUILD after reg_bqx_ |
| var_reg_{currency} | 28 | reg_{pairs} | REBUILD after reg_ |
| csi_reg_{currency} | 32 | reg_{pairs} | REBUILD after reg_ |
| tri_reg_{c1}_{c2}_{c3} | 36 | reg_{pairs} | REBUILD after reg_ |
| mkt_reg* | 4 | All reg_ | REBUILD last |

---

## POLYNOMIAL FIT SPECIFICATION (USER MANDATE v2.1)

**CRITICAL: Endpoint Evaluation with Scaled Coefficients**

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

```python
# Input (INTERVAL-CENTRIC: x = row indices, NOT timestamps)
x = np.arange(W)      # [0, 1, 2, ..., W-1]
y = values[-W:]       # Last W values (close price for IDX, BQX for BQX)
rate = y[-1]          # Current value (last in window)

# Fit 2nd degree polynomial: y = β₂x² + β₁x + β₀
coeffs = np.polyfit(x, y, 2)  # Returns [β₂, β₁, β₀]
β₂ = coeffs[0]  # Raw quadratic coefficient
β₁ = coeffs[1]  # Raw linear coefficient
β₀ = coeffs[2]  # Raw constant term

# USER MANDATE: Endpoint Evaluation at x = W (NOT raw coefficients)
quad_term = β₂ * (W ** 2)     # Quadratic contribution at endpoint
lin_term = β₁ * W             # Linear contribution at endpoint
const_term = β₀               # Constant term (unchanged)

# USER MANDATE: Residual at endpoint
residual = rate - (quad_term + lin_term + const_term)

# Standard residuals for variance metrics (across all points)
y_hat = np.polyval(coeffs, x)
residuals = y - y_hat
```

**APPLIES TO BOTH IDX AND BQX VARIANTS:**
- **IDX**: `reg_{pair}` tables (28) - rate = close price
- **BQX**: `reg_bqx_{pair}` tables (28) - rate = BQX oscillator

---

## NEW COLUMN SPECIFICATION

### Per-Window Columns (19 new columns × 7 windows = 133 total)

```sql
-- Polynomial coefficients (USER MANDATE: Endpoint Scaled)
reg_quad_term_{W}     FLOAT64  -- β₂ × W² (quadratic at endpoint)
reg_lin_term_{W}      FLOAT64  -- β₁ × W (linear at endpoint)
reg_const_term_{W}    FLOAT64  -- β₀ (constant term)
reg_residual_{W}      FLOAT64  -- rate - (quad_term + lin_term + const_term)

-- Polynomial coefficients (normalized)
reg_quad_norm_{W}     FLOAT64  -- quad * (W-1)² / mean(y)
reg_lin_norm_{W}      FLOAT64  -- lin * (W-1) / mean(y)

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
reg_curv_sign_{W}     INT64    -- SIGN(quad_term)
reg_acceleration_{W}  FLOAT64  -- 2 * quad_term
reg_trend_str_{W}     FLOAT64  -- lin_term / resid_std
reg_forecast_5_{W}    FLOAT64  -- polyval(x+5) - polyval(x)

-- Confidence intervals
reg_ci_lower_{W}      FLOAT64  -- y_hat[-1] - 1.96*se
reg_ci_upper_{W}      FLOAT64  -- y_hat[-1] + 1.96*se
```

### Retain Existing Columns (10 × 7 = 70)
```sql
reg_slope_{W}         -- Keep for backward compatibility
reg_deviation_{W}
reg_direction_{W}
reg_mean_{W}
reg_std_{W}
reg_zscore_{W}
reg_min_{W}
reg_max_{W}
reg_range_pct_{W}
reg_first_{W}
```

**Total columns per reg_ table: 203**

---

## IMPLEMENTATION PHASES

### Phase 1: Primary reg_ Tables (56 tables)
**Duration**: ~2 hours
**Workers**: 8 parallel

```
Step 1.1: Create polynomial calculation script
Step 1.2: Execute for reg_{pair} (28 tables)
Step 1.3: Execute for reg_bqx_{pair} (28 tables)
Step 1.4: Validate row counts and schemas
```

### Phase 2: Covariance Tables (336 tables)
**Duration**: ~4 hours
**Workers**: 16 parallel
**Dependency**: Phase 1 complete

```
Step 2.1: Update cov_ SQL generators for polynomial columns
Step 2.2: Execute cov_reg_{pair1}_{pair2} (168 tables)
Step 2.3: Execute cov_reg_bqx_{pair1}_{pair2} (168 tables)
Step 2.4: Validate covariance calculations
```

### Phase 3: Variance Tables (28 tables)
**Duration**: ~30 minutes
**Workers**: 8 parallel
**Dependency**: Phase 1 complete

```
Step 3.1: Update var_ SQL generators
Step 3.2: Execute var_reg_{currency} (28 tables)
Step 3.3: Validate variance calculations
```

### Phase 4: CSI/Triangular Tables (68 tables)
**Duration**: ~1 hour
**Workers**: 8 parallel
**Dependency**: Phase 1 complete

```
Step 4.1: Update csi_ and tri_ SQL generators
Step 4.2: Execute csi_reg_{currency} (32 tables)
Step 4.3: Execute tri_reg_{c1}_{c2}_{c3} (36 tables)
Step 4.4: Validate aggregations
```

### Phase 5: Market Tables (4 tables)
**Duration**: ~15 minutes
**Dependency**: All phases complete

```
Step 5.1: Update mkt_reg SQL
Step 5.2: Execute mkt_reg, mkt_reg_bqx (4 tables)
Step 5.3: Final validation
```

---

## PYTHON IMPLEMENTATION TEMPLATE (USER MANDATE v2.1)

```python
import numpy as np
from scipy import stats

def calculate_polynomial_features(values: np.ndarray, window: int) -> dict:
    """
    Calculate polynomial regression features for a rolling window.

    USER MANDATE v2.1: Endpoint Evaluation
    - lin_term = β₁ × N (scaled by window)
    - quad_term = β₂ × N² (scaled by window squared)
    - residual = rate - (quad_term + lin_term + const_term)

    Args:
        values: Array of source values (close price for IDX, BQX for BQX)
        window: Window size N

    Returns:
        Dictionary of feature values
    """
    N = window
    x = np.arange(N)              # [0, 1, 2, ..., N-1]
    y = values[-N:]               # Last N values
    rate = y[-1]                  # Current value (last in window)

    if len(y) < N or np.all(np.isnan(y)):
        return {k: np.nan for k in [
            'quad_term', 'lin_term', 'const_term', 'residual',
            'quad_norm', 'lin_norm', 'resid_var', 'total_var',
            'r2', 'rmse', 'resid_norm', 'resid_std', 'resid_min', 'resid_max',
            'resid_last', 'resid_skew', 'resid_kurt', 'curv_sign', 'acceleration',
            'trend_str', 'forecast_5', 'ci_lower', 'ci_upper'
        ]}

    # Fit polynomial: y = β₂x² + β₁x + β₀
    coeffs = np.polyfit(x, y, 2)  # Returns [β₂, β₁, β₀]
    β₂ = coeffs[0]  # Raw quadratic coefficient
    β₁ = coeffs[1]  # Raw linear coefficient
    β₀ = coeffs[2]  # Raw constant term

    # USER MANDATE: Endpoint Evaluation at x = N
    quad_term = β₂ * (N ** 2)     # Quadratic contribution at endpoint
    lin_term = β₁ * N             # Linear contribution at endpoint
    const_term = β₀               # Constant term (unchanged)

    # USER MANDATE: Residual at endpoint
    residual = rate - (quad_term + lin_term + const_term)

    # Standard residuals for variance metrics (across all points)
    y_hat = np.polyval(coeffs, x)
    residuals = y - y_hat

    # Variance metrics (USER MANDATE v2.1)
    y_mean = np.mean(y)
    resid_var = np.mean(residuals**2)     # MSE
    total_var = np.var(y)                  # Total variance
    r2 = 1 - (resid_var / total_var) if total_var > 0 else 0
    rmse = np.sqrt(resid_var)
    resid_std = np.std(residuals)
    se = resid_std / np.sqrt(N)

    return {
        # USER MANDATE: Scaled coefficients at endpoint
        'quad_term': quad_term,           # β₂ × N²
        'lin_term': lin_term,             # β₁ × N
        'const_term': const_term,         # β₀
        'residual': residual,             # rate - (quad_term + lin_term + const_term)

        # Normalized coefficients
        'quad_norm': quad_term * (N-1)**2 / y_mean if y_mean != 0 else 0,
        'lin_norm': lin_term * (N-1) / y_mean if y_mean != 0 else 0,

        # Variance metrics (USER MANDATE v2.1)
        'resid_var': resid_var,           # MSE = mean(residuals²)
        'total_var': total_var,           # var(y)
        'r2': r2,                         # 1 - (resid_var / total_var)
        'rmse': rmse,                     # sqrt(resid_var)
        'resid_norm': residual / y_mean if y_mean != 0 else 0,

        # Residual metrics
        'resid_std': resid_std,
        'resid_min': np.min(residuals),
        'resid_max': np.max(residuals),
        'resid_last': residuals[-1],
        'resid_skew': stats.skew(residuals) if len(residuals) > 2 else 0,
        'resid_kurt': stats.kurtosis(residuals) if len(residuals) > 2 else 0,

        # Derived features
        'curv_sign': int(np.sign(β₂)),
        'acceleration': 2 * β₂,
        'trend_str': lin_term / resid_std if resid_std > 0 else 0,
        'forecast_5': np.polyval(coeffs, N + 5) - np.polyval(coeffs, N),

        # Confidence intervals
        'ci_lower': y_hat[-1] - 1.96 * se,
        'ci_upper': y_hat[-1] + 1.96 * se
    }
```

---

## VALIDATION REQUIREMENTS

### Row Count Validation
- Each rebuilt table must have same row count as original
- No data loss allowed

### Schema Validation
- All 196 columns present
- All columns have correct FLOAT64/INT64 types
- No unexpected NULL values (except edges)

### Statistical Validation
- R² values in [0, 1]
- Residual distributions reasonable
- Quad/lin terms have expected signs for known trends

---

## SUCCESS CRITERIA

- [ ] All 56 primary reg_ tables rebuilt with 196 columns
- [ ] All 336 covariance tables rebuilt with polynomial correlations
- [ ] All 28 variance tables rebuilt with polynomial aggregations
- [ ] All 68 CSI/triangular tables rebuilt
- [ ] All 4 market tables rebuilt
- [ ] Row counts preserved (zero data loss)
- [ ] All statistical validations pass

---

## REFERENCE DOCUMENTS

- [/mandate/POLYNOMIAL_REGRESSION_FEATURE_GAP_ANALYSIS.md](../../../mandate/POLYNOMIAL_REGRESSION_FEATURE_GAP_ANALYSIS.md)
- [/features/POLYNOMIAL_REG_FEATURES.md](../../../features/POLYNOMIAL_REG_FEATURES.md)
- [/features/COV_REG_FEATURES.md](../../../features/COV_REG_FEATURES.md)
- [/features/VAR_REG_FEATURES.md](../../../features/VAR_REG_FEATURES.md)
- [/features/CSI_REG_FEATURES.md](../../../features/CSI_REG_FEATURES.md)
- [/features/TRI_REG_FEATURES.md](../../../features/TRI_REG_FEATURES.md)
- [/features/MKT_REG_FEATURES.md](../../../features/MKT_REG_FEATURES.md)

---

## AUTHORIZATION

This remediation is **AUTHORIZED AND MANDATED** by the Chief Engineer.

The polynomial regression features are core to the BQX ML V3 mandate. The current implementation represents a significant gap that must be closed to achieve 100% feature completeness.

**Signed**: Chief Engineer (CE)
**Date**: 2025-11-29

---

*Directive created: 2025-11-29 19:30 UTC*
