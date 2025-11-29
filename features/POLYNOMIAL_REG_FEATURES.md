# Polynomial Regression Features Specification

**Feature Type**: REG (Regression)
**Table Patterns**: `reg_{pair}`, `reg_bqx_{pair}`
**Windows**: [45, 90, 180, 360, 720, 1440, 2880]
**Variants**: IDX (price-derived), BQX (momentum-derived)

---

## Polynomial Fit Definition

For each window W, the polynomial regression is fitted as:

```
y = ax² + bx + c

Where:
- x = np.arange(W) = [0, 1, 2, ..., W-1]  (W data points)
- y = values[-W:]                          (last W source values)
- a = quad_term (curvature coefficient)
- b = lin_term (slope coefficient)
- c = const_term (intercept)
```

**Example for W=45**:
- x = [0, 1, 2, 3, ..., 44] (45 integers)
- y = last 45 values of close price (IDX) or BQX oscillator (BQX)

The polynomial is fitted using least squares (`np.polyfit(x, y, 2)`).

---

## Feature Columns

### Polynomial Coefficients

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `reg_quad_term_{W}` | FLOAT64 | Quadratic coefficient (curvature) | `np.polyfit(x,y,2)[0]` |
| `reg_lin_term_{W}` | FLOAT64 | Linear coefficient (slope) | `np.polyfit(x,y,2)[1]` |
| `reg_const_term_{W}` | FLOAT64 | Constant term (intercept) | `np.polyfit(x,y,2)[2]` |

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
    """Calculate polynomial regression features for a window."""
    x = np.arange(window)
    y = values[-window:]

    # Fit polynomial
    coeffs = np.polyfit(x, y, 2)  # [a, b, c]
    y_hat = np.polyval(coeffs, x)
    residuals = y - y_hat

    # Metrics
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum(residuals**2)

    # USER MANDATE v2.1: resid_var = MSE, total_var = variance of y
    resid_var = np.mean(residuals**2)  # MSE
    total_var = np.var(y)               # Total variance
    y_mean = np.mean(y)

    return {
        'quad_term': coeffs[0],
        'lin_term': coeffs[1],
        'const_term': coeffs[2],
        # VARIANCE METRICS (USER MANDATE v2.1)
        'resid_var': resid_var,         # MSE - residual variance
        'total_var': total_var,         # Total variance of y
        'r2': 1 - (resid_var / total_var) if total_var > 0 else 0,
        'rmse': np.sqrt(resid_var),     # sqrt(MSE)
        'resid_norm': residuals[-1] / y_mean if y_mean != 0 else 0,
        # RESIDUAL METRICS
        'resid_std': np.std(residuals),
        'resid_min': np.min(residuals),
        'resid_max': np.max(residuals),
        'resid_last': residuals[-1],
        'resid_skew': stats.skew(residuals),
        'resid_kurt': stats.kurtosis(residuals),
        # DERIVED FEATURES
        'curv_sign': np.sign(coeffs[0]),
        'acceleration': 2 * coeffs[0],
        'trend_str': coeffs[1] / np.std(residuals) if np.std(residuals) > 0 else 0,
        'forecast_5': np.polyval(coeffs, window+5) - np.polyval(coeffs, window)
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

### IDX (Price-Derived)

- **Source**: Close price
- **quad_term**: Price acceleration (pips/interval²)
- **lin_term**: Price velocity (pips/interval)
- **residual**: Deviation from polynomial price trend
- **Use**: Detect price trend exhaustion

### BQX (Momentum-Derived)

- **Source**: BQX oscillator value
- **quad_term**: Momentum acceleration
- **lin_term**: Momentum velocity
- **residual**: Deviation from momentum trend
- **Use**: Detect momentum exhaustion/reversal

---

*Specification created: 2025-11-29*
