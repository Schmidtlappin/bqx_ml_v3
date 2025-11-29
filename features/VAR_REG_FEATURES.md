# Variance Regression Features Specification

**Feature Type**: VAR_REG (Regression Variance)
**Table Patterns**: `var_reg_{currency}`
**Total Tables**: 28 (8 currencies × variant combinations)
**Dependency**: reg_{pair}, reg_bqx_{pair} (polynomial features)

---

## Architecture Note

**CRITICAL: INTERVAL-CENTRIC**

All windows (W) refer to **INTERVALS (rows), NOT time units**:
- `W = 45` means 45 consecutive data rows
- Polynomial formula: `x = np.arange(W) = [0, 1, 2, ..., W-1]`

---

## Executive Summary

Variance regression features aggregate polynomial regression metrics across all pairs containing a specific currency. These features capture currency-specific trend behavior and enable currency-level analysis.

---

## Table Structure

### Naming Convention
```
var_reg_{currency}           # IDX variant (8 tables)
var_reg_bqx_{currency}       # BQX variant (8 tables)
var_reg_cross_{currency}     # IDX-BQX cross variance (8 tables)
var_reg_combined_{currency}  # Combined IDX+BQX (4 tables)
```

### Currencies (8)
```
USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD
```

### Pairs Per Currency (7 each)
| Currency | Pairs |
|----------|-------|
| USD | eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd |
| EUR | eurusd, eurgbp, eurjpy, eurchf, euraud, eurcad, eurnzd |
| GBP | gbpusd, eurgbp, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd |
| JPY | usdjpy, eurjpy, gbpjpy, audjpy, nzdjpy, cadjpy, chfjpy |
| CHF | usdchf, eurchf, gbpchf, audchf, nzdchf, cadchf, chfjpy |
| AUD | audusd, euraud, gbpaud, audjpy, audchf, audcad, audnzd |
| CAD | usdcad, eurcad, gbpcad, audcad, nzdcad, cadjpy, cadchf |
| NZD | nzdusd, eurnzd, gbpnzd, audnzd, nzdjpy, nzdchf, nzdcad |

---

## Feature Columns

### Polynomial Coefficient Variance

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `var_quad_term_{W}` | FLOAT64 | Variance of quad across pairs | `VAR(pairs.quad_term_W)` |
| `var_lin_term_{W}` | FLOAT64 | Variance of lin across pairs | `VAR(pairs.lin_term_W)` |
| `var_const_term_{W}` | FLOAT64 | Variance of const across pairs | `VAR(pairs.const_term_W)` |

### Aggregation Statistics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `avg_quad_term_{W}` | FLOAT64 | Mean quad across pairs | `AVG(pairs.quad_term_W)` |
| `avg_lin_term_{W}` | FLOAT64 | Mean lin across pairs | `AVG(pairs.lin_term_W)` |
| `avg_r2_{W}` | FLOAT64 | Mean R² across pairs | `AVG(pairs.r2_W)` |
| `min_r2_{W}` | FLOAT64 | Min R² across pairs | `MIN(pairs.r2_W)` |
| `max_r2_{W}` | FLOAT64 | Max R² across pairs | `MAX(pairs.r2_W)` |

### Derived Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `avg_acceleration_{W}` | FLOAT64 | Mean acceleration | `AVG(pairs.acceleration_W)` |
| `var_acceleration_{W}` | FLOAT64 | Variance of acceleration | `VAR(pairs.acceleration_W)` |
| `avg_trend_str_{W}` | FLOAT64 | Mean trend strength | `AVG(pairs.trend_str_W)` |
| `var_trend_str_{W}` | FLOAT64 | Variance of trend strength | `VAR(pairs.trend_str_W)` |
| `consensus_curv_sign_{W}` | FLOAT64 | Agreement on curvature | `AVG(pairs.curv_sign_W)` |

### Cross-Window Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `quad_coherence_{W}` | FLOAT64 | How aligned are quad terms | `1 - VAR/MAX²` |
| `trend_alignment_{W}` | FLOAT64 | How aligned are trends | `1 - VAR(lin)/MAX(lin)²` |

---

## Column Count Per Table

- **Variance columns**: 5 per window × 7 windows = **35 columns**
- **Aggregation columns**: 5 per window × 7 windows = **35 columns**
- **Derived columns**: 5 per window × 7 windows = **35 columns**
- **Cross-window columns**: 2 per window × 7 windows = **14 columns**
- **Metadata**: interval_time, currency, n_pairs = 3 columns
- **Total per table**: **122 columns**

---

## SQL Template

```sql
-- Variance regression features for {currency}
WITH currency_pairs AS (
  SELECT interval_time, '{pair1}' as pair, reg_quad_term_{W}, reg_lin_term_{W}, ... FROM reg_{pair1}
  UNION ALL
  SELECT interval_time, '{pair2}' as pair, reg_quad_term_{W}, reg_lin_term_{W}, ... FROM reg_{pair2}
  -- ... (7 pairs for this currency)
),
aggregated AS (
  SELECT
    interval_time,
    '{currency}' as currency,
    COUNT(DISTINCT pair) as n_pairs,

    -- Variance metrics
    VARIANCE(reg_quad_term_{W}) as var_quad_term_{W},
    VARIANCE(reg_lin_term_{W}) as var_lin_term_{W},
    VARIANCE(reg_const_term_{W}) as var_const_term_{W},

    -- Aggregation metrics
    AVG(reg_quad_term_{W}) as avg_quad_term_{W},
    AVG(reg_lin_term_{W}) as avg_lin_term_{W},
    AVG(reg_r2_{W}) as avg_r2_{W},
    MIN(reg_r2_{W}) as min_r2_{W},
    MAX(reg_r2_{W}) as max_r2_{W},

    -- Derived metrics
    AVG(reg_acceleration_{W}) as avg_acceleration_{W},
    VARIANCE(reg_acceleration_{W}) as var_acceleration_{W},
    AVG(reg_trend_str_{W}) as avg_trend_str_{W},
    VARIANCE(reg_trend_str_{W}) as var_trend_str_{W},
    AVG(reg_curv_sign_{W}) as consensus_curv_sign_{W},

    -- Coherence metrics
    1 - SAFE_DIVIDE(VARIANCE(reg_quad_term_{W}), POWER(MAX(ABS(reg_quad_term_{W})), 2)) as quad_coherence_{W},
    1 - SAFE_DIVIDE(VARIANCE(reg_lin_term_{W}), POWER(MAX(ABS(reg_lin_term_{W})), 2)) as trend_alignment_{W}

  FROM currency_pairs
  GROUP BY interval_time
)
SELECT * FROM aggregated
ORDER BY interval_time
```

---

## IDX vs BQX Interpretation

### IDX (var_reg_) - Price-Derived
- **Source**: Price polynomial fits aggregated
- **Interpretation**: Currency-wide price trend consensus
- **Use Case**: Identify USD strength/weakness across pairs

### BQX (var_reg_bqx_) - Momentum-Derived
- **Source**: BQX polynomial fits aggregated
- **Interpretation**: Currency-wide momentum consensus
- **Use Case**: Identify momentum exhaustion patterns

---

## Table List (28 Total)

### IDX Variant (8 tables)
```
var_reg_usd, var_reg_eur, var_reg_gbp, var_reg_jpy,
var_reg_chf, var_reg_aud, var_reg_cad, var_reg_nzd
```

### BQX Variant (8 tables)
```
var_reg_bqx_usd, var_reg_bqx_eur, var_reg_bqx_gbp, var_reg_bqx_jpy,
var_reg_bqx_chf, var_reg_bqx_aud, var_reg_bqx_cad, var_reg_bqx_nzd
```

### Cross Variance (8 tables)
```
var_reg_cross_usd, var_reg_cross_eur, var_reg_cross_gbp, var_reg_cross_jpy,
var_reg_cross_chf, var_reg_cross_aud, var_reg_cross_cad, var_reg_cross_nzd
```

### Combined (4 tables)
```
var_reg_combined_major, var_reg_combined_minor,
var_reg_combined_commodity, var_reg_combined_all
```

---

*Specification created: 2025-11-29*
