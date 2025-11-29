# Currency Strength Index Regression Features Specification

**Feature Type**: CSI_REG (Currency Strength from Regression)
**Table Patterns**: `csi_reg_{currency}`
**Total Tables**: 32 (8 currencies × 4 variants)
**Dependency**: reg_{pair}, var_reg_{currency} (polynomial features)

---

## Architecture Note

**CRITICAL: INTERVAL-CENTRIC**

All windows (W) refer to **INTERVALS (rows), NOT time units**:
- `W = 45` means 45 consecutive data rows
- Polynomial formula: `x = np.arange(W) = [0, 1, 2, ..., W-1]`

---

## Executive Summary

Currency Strength Index (CSI) regression features compute relative currency strength based on polynomial regression coefficients. By comparing trend characteristics across all pairs containing a currency, CSI captures whether a currency is trending stronger or weaker than its counterparts.

---

## Table Structure

### Naming Convention
```
csi_reg_{currency}              # IDX variant (8 tables)
csi_reg_bqx_{currency}          # BQX variant (8 tables)
csi_reg_relative_{currency}     # Relative strength (8 tables)
csi_reg_momentum_{currency}     # Momentum-weighted (8 tables)
```

### Currencies (8)
```
USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD
```

---

## Feature Columns

### Strength Index Components

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `csi_quad_str_{W}` | FLOAT64 | Quad-weighted strength | `SUM(sign_adj * quad_term) / n_pairs` |
| `csi_lin_str_{W}` | FLOAT64 | Linear-weighted strength | `SUM(sign_adj * lin_term) / n_pairs` |
| `csi_accel_str_{W}` | FLOAT64 | Acceleration strength | `SUM(sign_adj * acceleration) / n_pairs` |
| `csi_trend_str_{W}` | FLOAT64 | Trend strength index | `SUM(sign_adj * trend_str) / n_pairs` |

### Relative Rankings

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `csi_rank_quad_{W}` | INT64 | Rank by quad strength | `RANK() OVER (ORDER BY csi_quad_str)` |
| `csi_rank_lin_{W}` | INT64 | Rank by linear strength | `RANK() OVER (ORDER BY csi_lin_str)` |
| `csi_rank_overall_{W}` | INT64 | Combined rank | `AVG(rank_quad, rank_lin, rank_accel)` |

### Momentum Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `csi_momentum_{W}` | FLOAT64 | Rate of strength change | `csi_lin_str - LAG(csi_lin_str, 1)` |
| `csi_momentum_accel_{W}` | FLOAT64 | Acceleration of momentum | `csi_momentum - LAG(csi_momentum, 1)` |
| `csi_consistency_{W}` | FLOAT64 | How consistent across pairs | `1 - VAR(sign_adj*lin_term)/MAX²` |

### Cross-Currency Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `csi_vs_usd_{W}` | FLOAT64 | Strength vs USD | `csi_lin_str - usd_csi_lin_str` |
| `csi_vs_eur_{W}` | FLOAT64 | Strength vs EUR | `csi_lin_str - eur_csi_lin_str` |
| `csi_vs_avg_{W}` | FLOAT64 | Strength vs market avg | `csi_lin_str - AVG(all_csi_lin_str)` |

### Divergence Detection

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `csi_div_short_long_{W}` | FLOAT64 | Short vs long window div | `csi_lin_str_45 - csi_lin_str_2880` |
| `csi_div_idx_bqx_{W}` | FLOAT64 | IDX vs BQX divergence | `idx_csi - bqx_csi` |

---

## Column Count Per Table

- **Strength columns**: 4 per window × 7 windows = **28 columns**
- **Ranking columns**: 3 per window × 7 windows = **21 columns**
- **Momentum columns**: 3 per window × 7 windows = **21 columns**
- **Cross-currency columns**: 3 per window × 7 windows = **21 columns**
- **Divergence columns**: 2 per window × 7 windows = **14 columns**
- **Metadata**: interval_time, currency = 2 columns
- **Total per table**: **107 columns**

---

## SQL Template

```sql
-- Currency Strength Index from regression features for {currency}
WITH pair_contributions AS (
  -- For pairs where currency is BASE (positive contribution when pair rises)
  SELECT
    interval_time,
    '{pair}' as pair,
    1 as sign_adjustment,  -- Base currency: pair up = currency strong
    reg_quad_term_{W},
    reg_lin_term_{W},
    reg_acceleration_{W},
    reg_trend_str_{W}
  FROM `bqx_ml_v3_features.reg_{pair_with_base}`

  UNION ALL

  -- For pairs where currency is QUOTE (negative contribution when pair rises)
  SELECT
    interval_time,
    '{pair}' as pair,
    -1 as sign_adjustment,  -- Quote currency: pair up = currency weak
    reg_quad_term_{W},
    reg_lin_term_{W},
    reg_acceleration_{W},
    reg_trend_str_{W}
  FROM `bqx_ml_v3_features.reg_{pair_with_quote}`
),
strength_calc AS (
  SELECT
    interval_time,
    '{currency}' as currency,

    -- Strength indices
    AVG(sign_adjustment * reg_quad_term_{W}) as csi_quad_str_{W},
    AVG(sign_adjustment * reg_lin_term_{W}) as csi_lin_str_{W},
    AVG(sign_adjustment * reg_acceleration_{W}) as csi_accel_str_{W},
    AVG(sign_adjustment * reg_trend_str_{W}) as csi_trend_str_{W},

    -- Consistency
    1 - SAFE_DIVIDE(
      VARIANCE(sign_adjustment * reg_lin_term_{W}),
      POWER(MAX(ABS(sign_adjustment * reg_lin_term_{W})), 2)
    ) as csi_consistency_{W}

  FROM pair_contributions
  GROUP BY interval_time
),
with_momentum AS (
  SELECT
    *,
    csi_lin_str_{W} - LAG(csi_lin_str_{W}, 1) OVER (ORDER BY interval_time) as csi_momentum_{W}
  FROM strength_calc
)
SELECT
  *,
  csi_momentum_{W} - LAG(csi_momentum_{W}, 1) OVER (ORDER BY interval_time) as csi_momentum_accel_{W}
FROM with_momentum
ORDER BY interval_time
```

---

## Sign Adjustment Logic

| Currency | Pair | Position | Sign |
|----------|------|----------|------|
| USD | EURUSD | Quote | -1 |
| USD | USDJPY | Base | +1 |
| EUR | EURUSD | Base | +1 |
| EUR | EURJPY | Base | +1 |
| GBP | GBPUSD | Base | +1 |
| GBP | EURGBP | Quote | -1 |

**Rule**: When currency is BASE, pair rise = currency strength (+1).
When currency is QUOTE, pair rise = currency weakness (-1).

---

## IDX vs BQX Interpretation

### IDX (csi_reg_) - Price-Derived
- **Source**: Price polynomial trends
- **Interpretation**: Currency price strength
- **Use Case**: Fundamental strength assessment

### BQX (csi_reg_bqx_) - Momentum-Derived
- **Source**: BQX polynomial trends
- **Interpretation**: Currency momentum strength
- **Use Case**: Momentum exhaustion across currency

---

## Table List (32 Total)

### IDX Variant (8 tables)
```
csi_reg_usd, csi_reg_eur, csi_reg_gbp, csi_reg_jpy,
csi_reg_chf, csi_reg_aud, csi_reg_cad, csi_reg_nzd
```

### BQX Variant (8 tables)
```
csi_reg_bqx_usd, csi_reg_bqx_eur, csi_reg_bqx_gbp, csi_reg_bqx_jpy,
csi_reg_bqx_chf, csi_reg_bqx_aud, csi_reg_bqx_cad, csi_reg_bqx_nzd
```

### Relative Strength (8 tables)
```
csi_reg_relative_usd, csi_reg_relative_eur, csi_reg_relative_gbp, csi_reg_relative_jpy,
csi_reg_relative_chf, csi_reg_relative_aud, csi_reg_relative_cad, csi_reg_relative_nzd
```

### Momentum-Weighted (8 tables)
```
csi_reg_momentum_usd, csi_reg_momentum_eur, csi_reg_momentum_gbp, csi_reg_momentum_jpy,
csi_reg_momentum_chf, csi_reg_momentum_aud, csi_reg_momentum_cad, csi_reg_momentum_nzd
```

---

*Specification created: 2025-11-29*
