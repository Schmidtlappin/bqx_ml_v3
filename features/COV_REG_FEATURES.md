# Covariance Regression Features Specification

**Feature Type**: COV_REG (Regression Covariance)
**Table Patterns**: `cov_reg_{pair1}_{pair2}`, `cov_reg_bqx_{pair1}_{pair2}`
**Total Tables**: 336 (168 IDX + 168 BQX)
**Dependency**: reg_{pair}, reg_bqx_{pair} (polynomial features)

---

## Architecture Note

**CRITICAL: INTERVAL-CENTRIC**

All windows (W) refer to **INTERVALS (rows), NOT time units**:
- `W = 45` means 45 consecutive data rows
- Polynomial formula: `x = np.arange(W) = [0, 1, 2, ..., W-1]`

---

## Executive Summary

Covariance regression features capture the statistical relationship between polynomial regression features across currency pairs that share a common currency. These features enable cross-pair momentum analysis and correlation-based prediction.

---

## Table Structure

### Naming Convention
```
cov_reg_{pair1}_{pair2}        # IDX variant (price-derived)
cov_reg_bqx_{pair1}_{pair2}    # BQX variant (momentum-derived)
```

### Pair Selection Rule
Only pairs sharing a **common currency** have covariance tables:
- EUR pairs: 21 combinations
- USD pairs: 21 combinations
- GBP pairs: 21 combinations
- JPY pairs: 21 combinations
- CHF pairs: 21 combinations
- AUD pairs: 21 combinations
- CAD pairs: 21 combinations
- NZD pairs: 21 combinations

**Total unique combinations**: 168 (deduplicated)

---

## Feature Columns

### Polynomial Coefficient Covariances

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `cov_quad_term_{W}` | FLOAT64 | Covariance of quadratic coefficients | `COV(p1.quad_term_W, p2.quad_term_W)` |
| `cov_lin_term_{W}` | FLOAT64 | Covariance of linear coefficients | `COV(p1.lin_term_W, p2.lin_term_W)` |
| `cov_const_term_{W}` | FLOAT64 | Covariance of constant terms | `COV(p1.const_term_W, p2.const_term_W)` |

### Normalized Coefficient Covariances

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `cov_quad_norm_{W}` | FLOAT64 | Covariance of normalized quadratic | `COV(p1.quad_norm_W, p2.quad_norm_W)` |
| `cov_lin_norm_{W}` | FLOAT64 | Covariance of normalized linear | `COV(p1.lin_norm_W, p2.lin_norm_W)` |

### Goodness of Fit Covariances

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `cov_r2_{W}` | FLOAT64 | Covariance of R² scores | `COV(p1.r2_W, p2.r2_W)` |
| `cov_rmse_{W}` | FLOAT64 | Covariance of RMSE | `COV(p1.rmse_W, p2.rmse_W)` |

### Residual Metric Covariances

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `cov_resid_std_{W}` | FLOAT64 | Covariance of residual std | `COV(p1.resid_std_W, p2.resid_std_W)` |
| `cov_resid_last_{W}` | FLOAT64 | Covariance of last residuals | `COV(p1.resid_last_W, p2.resid_last_W)` |
| `cov_resid_skew_{W}` | FLOAT64 | Covariance of residual skewness | `COV(p1.resid_skew_W, p2.resid_skew_W)` |
| `cov_resid_kurt_{W}` | FLOAT64 | Covariance of residual kurtosis | `COV(p1.resid_kurt_W, p2.resid_kurt_W)` |

### Derived Feature Covariances

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `cov_acceleration_{W}` | FLOAT64 | Covariance of acceleration | `COV(p1.acceleration_W, p2.acceleration_W)` |
| `cov_trend_str_{W}` | FLOAT64 | Covariance of trend strength | `COV(p1.trend_str_W, p2.trend_str_W)` |
| `cov_forecast_5_{W}` | FLOAT64 | Covariance of 5-interval forecasts | `COV(p1.forecast_5_W, p2.forecast_5_W)` |

### Cross-Feature Correlations

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `corr_quad_lin_{W}` | FLOAT64 | Correlation: quad vs lin | `CORR(p1.quad_term_W, p2.lin_term_W)` |
| `corr_quad_accel_{W}` | FLOAT64 | Correlation: quad vs accel | `CORR(p1.quad_term_W, p2.acceleration_W)` |
| `corr_lin_trend_{W}` | FLOAT64 | Correlation: lin vs trend | `CORR(p1.lin_term_W, p2.trend_str_W)` |

---

## Column Count Per Table

- **Covariance columns**: 14 per window × 7 windows = **98 columns**
- **Cross-correlation columns**: 3 per window × 7 windows = **21 columns**
- **Metadata**: interval_time, pair1, pair2, common_currency = 4 columns
- **Total per table**: **123 columns**

---

## SQL Template

```sql
-- Covariance regression features between pair1 and pair2
WITH aligned_data AS (
  SELECT
    p1.interval_time,
    -- Pair 1 polynomial features
    p1.reg_quad_term_{W} as p1_quad_term,
    p1.reg_lin_term_{W} as p1_lin_term,
    p1.reg_const_term_{W} as p1_const_term,
    p1.reg_quad_norm_{W} as p1_quad_norm,
    p1.reg_lin_norm_{W} as p1_lin_norm,
    p1.reg_r2_{W} as p1_r2,
    p1.reg_rmse_{W} as p1_rmse,
    p1.reg_resid_std_{W} as p1_resid_std,
    p1.reg_resid_last_{W} as p1_resid_last,
    p1.reg_acceleration_{W} as p1_acceleration,
    p1.reg_trend_str_{W} as p1_trend_str,
    p1.reg_forecast_5_{W} as p1_forecast_5,
    -- Pair 2 polynomial features
    p2.reg_quad_term_{W} as p2_quad_term,
    p2.reg_lin_term_{W} as p2_lin_term,
    p2.reg_const_term_{W} as p2_const_term,
    p2.reg_quad_norm_{W} as p2_quad_norm,
    p2.reg_lin_norm_{W} as p2_lin_norm,
    p2.reg_r2_{W} as p2_r2,
    p2.reg_rmse_{W} as p2_rmse,
    p2.reg_resid_std_{W} as p2_resid_std,
    p2.reg_resid_last_{W} as p2_resid_last,
    p2.reg_acceleration_{W} as p2_acceleration,
    p2.reg_trend_str_{W} as p2_trend_str,
    p2.reg_forecast_5_{W} as p2_forecast_5
  FROM `bqx_ml_v3_features.reg_{pair1}` p1
  JOIN `bqx_ml_v3_features.reg_{pair2}` p2
    ON p1.interval_time = p2.interval_time
)
SELECT
  interval_time,
  '{pair1}' as pair1,
  '{pair2}' as pair2,
  '{common_currency}' as common_currency,

  -- Rolling covariances (window function)
  COVAR_POP(p1_quad_term, p2_quad_term) OVER w as cov_quad_term_{W},
  COVAR_POP(p1_lin_term, p2_lin_term) OVER w as cov_lin_term_{W},
  COVAR_POP(p1_const_term, p2_const_term) OVER w as cov_const_term_{W},
  COVAR_POP(p1_quad_norm, p2_quad_norm) OVER w as cov_quad_norm_{W},
  COVAR_POP(p1_lin_norm, p2_lin_norm) OVER w as cov_lin_norm_{W},
  COVAR_POP(p1_r2, p2_r2) OVER w as cov_r2_{W},
  COVAR_POP(p1_rmse, p2_rmse) OVER w as cov_rmse_{W},
  COVAR_POP(p1_resid_std, p2_resid_std) OVER w as cov_resid_std_{W},
  COVAR_POP(p1_resid_last, p2_resid_last) OVER w as cov_resid_last_{W},
  COVAR_POP(p1_acceleration, p2_acceleration) OVER w as cov_acceleration_{W},
  COVAR_POP(p1_trend_str, p2_trend_str) OVER w as cov_trend_str_{W},
  COVAR_POP(p1_forecast_5, p2_forecast_5) OVER w as cov_forecast_5_{W},

  -- Cross-feature correlations
  CORR(p1_quad_term, p2_lin_term) OVER w as corr_quad_lin_{W},
  CORR(p1_quad_term, p2_acceleration) OVER w as corr_quad_accel_{W},
  CORR(p1_lin_term, p2_trend_str) OVER w as corr_lin_trend_{W}

FROM aligned_data
WINDOW w AS (
  ORDER BY interval_time
  ROWS BETWEEN {W}-1 PRECEDING AND CURRENT ROW
)
```

---

## IDX vs BQX Interpretation

### IDX (cov_reg_) - Price-Derived
- **Source**: Close price polynomial fits
- **Interpretation**: Price trend covariance between pairs
- **Use Case**: Identify price momentum divergence/convergence

### BQX (cov_reg_bqx_) - Momentum-Derived
- **Source**: BQX oscillator polynomial fits
- **Interpretation**: Momentum behavior covariance
- **Use Case**: Cross-pair momentum exhaustion detection

---

## Dependency Chain

```
reg_{pair} (polynomial features)
    ↓
cov_reg_{pair1}_{pair2} (covariance)
    ↓
var_reg_{currency} (variance aggregation)
    ↓
csi_reg_{currency} (currency strength index)
    ↓
mkt_reg (market-wide regression)
```

---

## Table List (336 Total)

### IDX Variant (168 tables)
```
cov_reg_eurusd_gbpusd, cov_reg_eurusd_usdjpy, cov_reg_eurusd_usdchf, ...
(168 tables following common currency rule)
```

### BQX Variant (168 tables)
```
cov_reg_bqx_eurusd_gbpusd, cov_reg_bqx_eurusd_usdjpy, ...
(168 tables following common currency rule)
```

---

*Specification created: 2025-11-29*
