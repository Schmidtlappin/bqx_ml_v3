# CE → BA DIRECTIVE: POLYNOMIAL REGRESSION REMEDIATION CONFIRMED

**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Date**: 2025-11-29 21:00 UTC
**Priority**: CRITICAL
**Status**: CONFIRMED AND MANDATED

---

## CONFIRMATION: USER MANDATE v2.1 FORMULAS

The following formulas are **CONFIRMED** for implementation across all 492 tables:

### Primary Features (USER MANDATE: Endpoint Scaled)

| Feature | Formula | Description |
|---------|---------|-------------|
| `reg_quad_term_{W}` | **β₂ × W²** | Scaled quadratic at endpoint |
| `reg_lin_term_{W}` | **β₁ × W** | Scaled linear at endpoint |
| `reg_const_term_{W}` | **β₀** | Constant term (unchanged) |
| `reg_residual_{W}` | **rate - (quad_term + lin_term + const_term)** | Deviation at endpoint |

### Variance Metrics (USER MANDATE v2.1)

| Feature | Formula | Description |
|---------|---------|-------------|
| `reg_resid_var_{W}` | **mean(residuals²)** | MSE - residual variance |
| `reg_total_var_{W}` | **var(y)** | Total variance of y |
| `reg_r2_{W}` | **1 - (resid_var / total_var)** | R² score |
| `reg_rmse_{W}` | **sqrt(resid_var)** | Root mean squared error |
| `reg_resid_norm_{W}` | **residual / mean(y)** | Normalized residual |

### Derived Features (ALL MUST BE CALCULATED)

| Feature | Formula | Description |
|---------|---------|-------------|
| `reg_quad_norm_{W}` | quad_term × (W-1)² / mean(y) | Normalized quadratic |
| `reg_lin_norm_{W}` | lin_term × (W-1) / mean(y) | Normalized linear |
| `reg_resid_std_{W}` | std(y - y_hat) | Residual std deviation |
| `reg_resid_min_{W}` | min(residuals) | Minimum residual |
| `reg_resid_max_{W}` | max(residuals) | Maximum residual |
| `reg_resid_last_{W}` | residuals[-1] | Last residual |
| `reg_resid_skew_{W}` | skew(residuals) | Residual skewness |
| `reg_resid_kurt_{W}` | kurtosis(residuals) | Residual kurtosis |
| `reg_curv_sign_{W}` | sign(β₂) | Curvature sign |
| `reg_acceleration_{W}` | 2 × β₂ | Second derivative |
| `reg_trend_str_{W}` | lin_term / resid_std | Trend strength |
| `reg_forecast_5_{W}` | polyval(x+5) - polyval(x) | 5-interval forecast |
| `reg_ci_lower_{W}` | y_hat[-1] - 1.96×se | 95% CI lower |
| `reg_ci_upper_{W}` | y_hat[-1] + 1.96×se | 95% CI upper |

---

## TABLES TO REBUILD

### Phase 1: Primary Tables (56)
| Pattern | Count | Action |
|---------|-------|--------|
| `reg_{pair}` | 28 | REBUILD with 203 columns |
| `reg_bqx_{pair}` | 28 | REBUILD with 203 columns |

### Phase 2: Downstream Tables (436)
| Pattern | Count | Depends On |
|---------|-------|------------|
| `cov_reg_{pair1}_{pair2}` | 168 | reg_{pair} |
| `cov_reg_bqx_{pair1}_{pair2}` | 168 | reg_bqx_{pair} |
| `var_reg_{currency}` | 28 | reg_{pairs} |
| `csi_reg_{currency}` | 32 | reg_{pairs} |
| `tri_reg_{c1}_{c2}_{c3}` | 36 | reg_{pairs} |
| `mkt_reg*` | 4 | All reg_ |

---

## CRITICAL REQUIREMENTS

1. **BOTH IDX AND BQX**: Identical formulas, different source data
   - IDX: rate = close price
   - BQX: rate = BQX oscillator

2. **INTERVAL-CENTRIC**: x = row indices [0, 1, 2, ..., W-1], NOT timestamps

3. **ALL 19 NEW COLUMNS**: Per window × 7 windows = 133 new columns per table

4. **EXISTING 10 COLUMNS**: Retain for backward compatibility = 70 columns

5. **TOTAL**: 203 columns per reg_ table

---

## PYTHON IMPLEMENTATION REFERENCE

```python
def calculate_polynomial_features(values, window):
    N = window
    x = np.arange(N)
    y = values[-N:]
    rate = y[-1]

    # Fit polynomial
    coeffs = np.polyfit(x, y, 2)  # [β₂, β₁, β₀]
    β₂, β₁, β₀ = coeffs[0], coeffs[1], coeffs[2]

    # USER MANDATE: Endpoint Evaluation
    quad_term = β₂ * (N ** 2)
    lin_term = β₁ * N
    const_term = β₀
    residual = rate - (quad_term + lin_term + const_term)

    # All derived features must be calculated
    y_hat = np.polyval(coeffs, x)
    residuals = y - y_hat
    resid_var = np.mean(residuals**2)  # MSE
    total_var = np.var(y)
    # ... (all 19 features per window)
```

---

## AUTHORIZATION

This remediation is **CONFIRMED AND MANDATED** by the Chief Engineer.

**Signed**: Chief Engineer (CE)
**Date**: 2025-11-29 21:00 UTC

---

*Directive created: 2025-11-29 21:00 UTC*
