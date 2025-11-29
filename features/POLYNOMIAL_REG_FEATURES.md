# Polynomial Regression Features Specification

**Feature Type**: REG (Regression)
**Table Patterns**: `reg_{pair}`, `reg_bqx_{pair}`
**Windows**: [45, 90, 180, 360, 720, 1440, 2880]
**Variants**: IDX (price-derived), BQX (momentum-derived)

---

## Polynomial Fit Definition

For each window N, the polynomial regression is fitted as:

```
y = β₂x² + β₁x + β₀

Where:
- x = np.arange(N) = [0, 1, 2, ..., N-1]  (N data points)
- y = values[-N:]                          (last N source values)
- β₂ = raw quadratic coefficient (from polyfit)
- β₁ = raw linear coefficient (from polyfit)
- β₀ = raw constant term (from polyfit)
```

**Example for N=45**:
- x = [0, 1, 2, 3, ..., 44] (45 integers)
- y = last 45 values of close price (IDX) or BQX oscillator (BQX)

The polynomial is fitted using least squares (`np.polyfit(x, y, 2)`).

### USER MANDATE: Endpoint Evaluation (v2.1)

**CRITICAL: Output features use SCALED coefficients evaluated at x = N:**

```python
# Raw coefficients from polyfit
coeffs = np.polyfit(x, y, 2)  # → [β₂, β₁, β₀]

# USER MANDATE: Scale by window N for endpoint evaluation
quad_term = β₂ × N²    # Quadratic contribution at x = N
lin_term = β₁ × N      # Linear contribution at x = N
const_term = β₀        # Constant term (unchanged)

# Residual at endpoint
residual = rate - (lin_term + quad_term + const_term)
         = y[-1] - (β₂×N² + β₁×N + β₀)
```

---

## Feature Columns

### Polynomial Coefficients (USER MANDATE: Endpoint Scaled)

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_quad_term_{W}` | FLOAT64 | **Scaled quadratic at endpoint** | `β₂ × W²` |
| `reg_lin_term_{W}` | FLOAT64 | **Scaled linear at endpoint** | `β₁ × W` |
| `reg_const_term_{W}` | FLOAT64 | Constant term (intercept) | `β₀` |
| `reg_residual_{W}` | FLOAT64 | **Residual at endpoint** | `rate - (quad_term + lin_term + const_term)` |

### Normalized Coefficients

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_quad_norm_{W}` | FLOAT64 | Normalized quadratic | `quad * (W-1)² / mean(y)` |
| `reg_lin_norm_{W}` | FLOAT64 | Normalized linear | `lin * (W-1) / mean(y)` |

### Variance Metrics (USER MANDATE v2.1)

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_resid_var_{W}` | FLOAT64 | **Residual variance (MSE)** | `mean(residuals²) = MSE` |
| `reg_total_var_{W}` | FLOAT64 | **Total variance of y** | `var(y) = SS_tot / W` |
| `reg_r2_{W}` | FLOAT64 | R² score [0,1] | `1 - (resid_var / total_var)` |
| `reg_rmse_{W}` | FLOAT64 | Root mean squared error | `sqrt(resid_var) = sqrt(MSE)` |
| `reg_resid_norm_{W}` | FLOAT64 | Normalized last residual | `residuals[-1] / mean(y)` |

**User Mandate (AirTable MP02.P16.S01):**
```
For each window N:
- resid_var = MSE (residual variance/noise)
- total_var = variance of y
- r2 = 1 - (MSR / total_var)
```

### Residual Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_resid_std_{W}` | FLOAT64 | Residual std deviation | `std(y - y_hat)` |
| `reg_resid_min_{W}` | FLOAT64 | Minimum residual | `min(y - y_hat)` |
| `reg_resid_max_{W}` | FLOAT64 | Maximum residual | `max(y - y_hat)` |
| `reg_resid_last_{W}` | FLOAT64 | Last residual (pred error) | `(y - y_hat)[-1]` |
| `reg_resid_skew_{W}` | FLOAT64 | Residual skewness | `skew(residuals)` |
| `reg_resid_kurt_{W}` | FLOAT64 | Residual kurtosis | `kurtosis(residuals)` |

### Derived Features

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_curv_sign_{W}` | INT64 | Curvature sign | `sign(quad_term)` |
| `reg_acceleration_{W}` | FLOAT64 | 2nd derivative | `2 * quad_term` |
| `reg_trend_str_{W}` | FLOAT64 | Trend strength | `lin_term / resid_std` |
| `reg_forecast_5_{W}` | FLOAT64 | Forecast 5 intervals | `polyval(x+5) - polyval(x)` |

### Confidence Intervals

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_ci_lower_{W}` | FLOAT64 | 95% CI lower | `y_hat[-1] - 1.96*se` |
| `reg_ci_upper_{W}` | FLOAT64 | 95% CI upper | `y_hat[-1] + 1.96*se` |

---

## SQL Template

```sql
-- Polynomial regression features for window W
WITH window_data AS (
  SELECT
    interval_time,
    {source_column} as y,
    ROW_NUMBER() OVER (ORDER BY interval_time) as x
  FROM source_table
),
regression AS (
  SELECT
    interval_time,
    -- Polynomial coefficients via least squares
    -- Using window function for rolling calculation
    ...
)
SELECT
  interval_time,
  quad_term as reg_quad_term_{W},
  lin_term as reg_lin_term_{W},
  const_term as reg_const_term_{W},
  quad_term * POWER(W-1, 2) / NULLIF(y_mean, 0) as reg_quad_norm_{W},
  lin_term * (W-1) / NULLIF(y_mean, 0) as reg_lin_norm_{W},
  -- VARIANCE METRICS (USER MANDATE v2.1)
  ss_res / W as reg_resid_var_{W},                    -- MSE = resid_var
  ss_tot / W as reg_total_var_{W},                    -- Total variance
  1 - (ss_res / NULLIF(ss_tot, 0)) as reg_r2_{W},    -- R² = 1 - MSE/total_var
  SQRT(ss_res / W) as reg_rmse_{W},                  -- RMSE = sqrt(MSE)
  resid_last / NULLIF(y_mean, 0) as reg_resid_norm_{W},  -- Normalized residual
  -- RESIDUAL METRICS
  resid_std as reg_resid_std_{W},
  resid_min as reg_resid_min_{W},
  resid_max as reg_resid_max_{W},
  resid_last as reg_resid_last_{W},
  -- DERIVED FEATURES
  SIGN(quad_term) as reg_curv_sign_{W},
  2 * quad_term as reg_acceleration_{W},
  lin_term / NULLIF(resid_std, 0) as reg_trend_str_{W}
FROM regression
```

---

## Implementation Notes

### BigQuery Polynomial Fit

BigQuery does not have native `POLYFIT`. Use:

1. **ML.LINEAR_REGRESSION** with polynomial features
2. **JavaScript UDF** for `np.polyfit` equivalent
3. **Pre-computed in Python** and loaded to BQ

### Recommended Approach

```python
# Python-side calculation
import numpy as np
from scipy import stats

def calculate_poly_features(values, window):
    """
    Calculate polynomial regression features for a window.

    USER MANDATE v2.1: Endpoint Evaluation
    - lin_term = β₁ × N (scaled by window)
    - quad_term = β₂ × N² (scaled by window squared)
    - residual = rate - (lin_term + quad_term + const_term)
    """
    N = window
    x = np.arange(N)
    y = values[-N:]
    rate = y[-1]  # Current value (last in window)

    # Fit polynomial: y = β₂x² + β₁x + β₀
    coeffs = np.polyfit(x, y, 2)  # [β₂, β₁, β₀]
    β₂ = coeffs[0]  # Raw quadratic coefficient
    β₁ = coeffs[1]  # Raw linear coefficient
    β₀ = coeffs[2]  # Raw constant term

    # USER MANDATE: Endpoint evaluation at x = N
    quad_term = β₂ * (N ** 2)  # Scaled quadratic: β₂ × N²
    lin_term = β₁ * N          # Scaled linear: β₁ × N
    const_term = β₀            # Constant (unchanged)

    # USER MANDATE: Residual at endpoint
    residual = rate - (quad_term + lin_term + const_term)

    # Standard residuals for variance metrics (across all points)
    y_hat = np.polyval(coeffs, x)
    residuals = y - y_hat

    # USER MANDATE v2.1: resid_var = MSE, total_var = variance of y
    resid_var = np.mean(residuals**2)  # MSE
    total_var = np.var(y)               # Total variance
    y_mean = np.mean(y)

    return {
        # USER MANDATE: Scaled coefficients at endpoint
        'quad_term': quad_term,         # β₂ × N²
        'lin_term': lin_term,           # β₁ × N
        'const_term': const_term,       # β₀
        'residual': residual,           # rate - (quad_term + lin_term + const_term)

        # VARIANCE METRICS (USER MANDATE v2.1)
        'resid_var': resid_var,         # MSE = mean(residuals²)
        'total_var': total_var,         # var(y)
        'r2': 1 - (resid_var / total_var) if total_var > 0 else 0,
        'rmse': np.sqrt(resid_var),     # sqrt(MSE)
        'resid_norm': residual / y_mean if y_mean != 0 else 0,

        # RESIDUAL METRICS (across window)
        'resid_std': np.std(residuals),
        'resid_min': np.min(residuals),
        'resid_max': np.max(residuals),
        'resid_last': residuals[-1],
        'resid_skew': stats.skew(residuals),
        'resid_kurt': stats.kurtosis(residuals),

        # DERIVED FEATURES
        'curv_sign': np.sign(β₂),
        'acceleration': 2 * β₂,
        'trend_str': lin_term / np.std(residuals) if np.std(residuals) > 0 else 0,
        'forecast_5': np.polyval(coeffs, N+5) - np.polyval(coeffs, N)
    }
```

---

## Window Specifications

**CRITICAL: INTERVAL-CENTRIC ARCHITECTURE**

Windows are measured in **INTERVALS (rows), NOT time units**. This is fundamental to the BQX ML V3 architecture.

- `W = 45` means the last **45 rows** (intervals), regardless of time gaps
- The polynomial regression uses interval-based indexing: `x = np.arange(W) = [0, 1, 2, ..., W-1]`
- This ensures consistent feature calculation across market gaps (weekends, holidays)

| Window | Intervals | ~Time (15-min bars) | Use Case |
|--------|-----------|---------------------|----------|
| 45 | 45 intervals | ~11 hours | Short-term |
| 90 | 90 intervals | ~22 hours | Intraday |
| 180 | 180 intervals | ~45 hours | 2-day |
| 360 | 360 intervals | ~90 hours | Weekly |
| 720 | 720 intervals | ~180 hours | 1-week |
| 1440 | 1440 intervals | ~360 hours | 2-week |
| 2880 | 2880 intervals | ~720 hours | Monthly |

---

## IDX vs BQX Interpretation

**CRITICAL: Both IDX and BQX use IDENTICAL formulas with different source data.**

### IDX (Price-Derived) - `reg_{pair}` tables

- **Source**: Close price (y = close[-N:])
- **rate**: Current close price (y[-1])
- **Formulas (USER MANDATE v2.1)**:
  - `quad_term = β₂ × N²` (price curvature at endpoint)
  - `lin_term = β₁ × N` (price velocity at endpoint)
  - `residual = rate - (quad_term + lin_term + const_term)`
- **Use**: Detect price trend exhaustion

### BQX (Momentum-Derived) - `reg_bqx_{pair}` tables

- **Source**: BQX oscillator value (y = bqx[-N:])
- **rate**: Current BQX value (y[-1])
- **Formulas (USER MANDATE v2.1)**:
  - `quad_term = β₂ × N²` (momentum curvature at endpoint)
  - `lin_term = β₁ × N` (momentum velocity at endpoint)
  - `residual = rate - (quad_term + lin_term + const_term)`
- **Use**: Detect momentum exhaustion/reversal

### Tables Affected

| Variant | Table Pattern | Count | Source |
|---------|--------------|-------|--------|
| IDX | `reg_{pair}` | 28 | Close price |
| BQX | `reg_bqx_{pair}` | 28 | BQX oscillator |
| **Total** | | **56** | |

---

*Specification created: 2025-11-29*
