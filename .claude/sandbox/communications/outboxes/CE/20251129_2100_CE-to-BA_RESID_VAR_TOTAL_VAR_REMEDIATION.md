# CE-to-BA: CRITICAL REMEDIATION - resid_var and total_var Features

**From**: Chief Engineer
**To**: Build Agent
**Date**: 2025-11-29 21:00 UTC
**Priority**: CRITICAL
**Subject**: Add resid_var (MSE) and total_var to Polynomial Regression Remediation

---

## URGENT AMENDMENT TO POLYNOMIAL REGRESSION IMPLEMENTATION

A critical gap has been identified in the feature specification. The following variance metrics were mandated by the user in AirTable MP02.P16.S01 but were not included in the initial directive.

---

## USER MANDATE (AirTable MP02.P16.S01)

```
For each window N:
- lin_term = β₁ × N (linear slope at endpoint)
- quad_term = β₂ × N² (curvature at endpoint)
- resid_var = MSE (residual variance/noise)    ← CRITICAL ADDITION
- total_var = variance of y                     ← CRITICAL ADDITION
- r2 = 1 - (MSR / total_var)

Endpoint Evaluation: x = N (not midpoint)
```

---

## REQUIRED COLUMNS (ADD TO EXISTING REMEDIATION)

### For BOTH IDX and BQX Variants:

| Column | Type | Formula | Description |
|--------|------|---------|-------------|
| `reg_resid_var_{W}` | FLOAT64 | `mean(residuals²)` | MSE - Residual variance |
| `reg_total_var_{W}` | FLOAT64 | `var(y)` | Total variance of y |
| `reg_resid_norm_{W}` | FLOAT64 | `residuals[-1] / mean(y)` | Normalized last residual |

### Update R² and RMSE formulas:
| Column | Type | Formula | Description |
|--------|------|---------|-------------|
| `reg_r2_{W}` | FLOAT64 | `1 - (resid_var / total_var)` | R² from variance ratio |
| `reg_rmse_{W}` | FLOAT64 | `sqrt(resid_var)` | RMSE from MSE |

---

## PYTHON IMPLEMENTATION

```python
# USER MANDATE v2.1: resid_var = MSE, total_var = variance of y
# Source: AirTable MP02.P16.S01 "Regression Table Generation"

def calculate_variance_metrics(y, y_hat):
    """Calculate user-mandated variance metrics."""
    residuals = y - y_hat
    y_mean = np.mean(y)

    # VARIANCE METRICS (USER MANDATE)
    resid_var = np.mean(residuals**2)  # MSE = Mean Squared Error
    total_var = np.var(y)              # Total variance of y

    # DERIVED FROM VARIANCES
    r2 = 1 - (resid_var / total_var) if total_var > 0 else 0
    rmse = np.sqrt(resid_var)
    resid_norm = residuals[-1] / y_mean if y_mean != 0 else 0

    return {
        'resid_var': resid_var,
        'total_var': total_var,
        'r2': r2,
        'rmse': rmse,
        'resid_norm': resid_norm
    }
```

---

## TABLES AFFECTED

All 56 primary regression tables:

### IDX Variant (28 tables):
```
reg_eurusd, reg_gbpusd, reg_usdjpy, reg_usdchf, reg_audusd, reg_usdcad, reg_nzdusd,
reg_eurgbp, reg_eurjpy, reg_eurchf, reg_euraud, reg_eurcad, reg_eurnzd,
reg_gbpjpy, reg_gbpchf, reg_gbpaud, reg_gbpcad, reg_gbpnzd,
reg_audjpy, reg_audchf, reg_audcad, reg_audnzd,
reg_nzdjpy, reg_nzdchf, reg_nzdcad,
reg_cadjpy, reg_cadchf, reg_chfjpy
```

### BQX Variant (28 tables):
```
reg_bqx_eurusd, reg_bqx_gbpusd, reg_bqx_usdjpy, reg_bqx_usdchf, ...
(same pattern as IDX)
```

---

## COLUMN COUNT UPDATE

Per table:
- Original polynomial columns: 19 × 7 windows = 133
- Additional variance columns: 3 × 7 windows = 21
- **New total: 154 columns per table**

---

## VALIDATION REQUIREMENTS

After implementation, verify:

1. **Schema Validation**:
   ```sql
   SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS
   WHERE table_name = 'reg_eurusd'
   AND column_name LIKE 'reg_resid_var_%' OR column_name LIKE 'reg_total_var_%'
   ```
   Expected: 14 columns (7 windows × 2 metrics)

2. **Formula Validation**:
   ```python
   # Verify: r2 = 1 - (resid_var / total_var)
   assert abs(r2 - (1 - resid_var/total_var)) < 0.0001

   # Verify: rmse = sqrt(resid_var)
   assert abs(rmse - np.sqrt(resid_var)) < 0.0001
   ```

3. **Coverage**: Both IDX and BQX variants must have identical column schemas

---

## PRIORITY

**CRITICAL** - These are user-mandated features from AirTable. Add to current remediation plan immediately.

---

## REFERENCE DOCUMENTS

- `/features/POLYNOMIAL_REG_FEATURES.md` (updated)
- `/mandate/POLYNOMIAL_REGRESSION_FEATURE_GAP_ANALYSIS.md` (updated)
- `/intelligence/metadata.json` (updated)
- AirTable MP02.P16.S01 - Regression Table Generation

---

**Status**: AWAITING BA ACKNOWLEDGMENT AND IMPLEMENTATION

*CE - 2025-11-29 21:00 UTC*
