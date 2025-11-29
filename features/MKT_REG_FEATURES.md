# Market-Wide Regression Features Specification

**Feature Type**: MKT_REG (Market-Wide Regression Aggregation)
**Table Patterns**: `mkt_reg`, `mkt_reg_bqx`
**Total Tables**: 4
**Dependency**: reg_{pair}, var_reg_{currency}, csi_reg_{currency} (all polynomial features)

---

## Architecture Note

**CRITICAL: INTERVAL-CENTRIC**

All windows (W) refer to **INTERVALS (rows), NOT time units**:
- `W = 45` means 45 consecutive data rows
- Polynomial formula: `x = np.arange(W) = [0, 1, 2, ..., W-1]`

---

## Executive Summary

Market-wide regression features aggregate polynomial regression characteristics across all 28 currency pairs and 8 currencies to capture market-level trend dynamics. These features indicate overall market momentum, coordination, and regime characteristics.

---

## Table Structure

### Tables (4)
```
mkt_reg                # IDX market-wide aggregation
mkt_reg_bqx            # BQX market-wide aggregation
mkt_reg_cross          # IDX-BQX cross-market metrics
mkt_reg_regime         # Market regime classification
```

---

## Feature Columns

### Market-Wide Polynomial Aggregates

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_avg_quad_{W}` | FLOAT64 | Avg quadratic across all pairs | `AVG(pairs.quad_term_W)` |
| `mkt_avg_lin_{W}` | FLOAT64 | Avg linear across all pairs | `AVG(pairs.lin_term_W)` |
| `mkt_avg_accel_{W}` | FLOAT64 | Avg acceleration | `AVG(pairs.acceleration_W)` |
| `mkt_avg_r2_{W}` | FLOAT64 | Avg R² across all pairs | `AVG(pairs.r2_W)` |

### Market-Wide Variance

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_var_quad_{W}` | FLOAT64 | Variance of quad across pairs | `VAR(pairs.quad_term_W)` |
| `mkt_var_lin_{W}` | FLOAT64 | Variance of lin across pairs | `VAR(pairs.lin_term_W)` |
| `mkt_var_accel_{W}` | FLOAT64 | Variance of acceleration | `VAR(pairs.acceleration_W)` |

### Market Coordination Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_coordination_{W}` | FLOAT64 | How coordinated are trends | `1 - VAR(lin) / MAX(lin)²` |
| `mkt_consensus_{W}` | FLOAT64 | Direction consensus [-1, 1] | `AVG(SIGN(lin_term))` |
| `mkt_strength_{W}` | FLOAT64 | Market-wide trend strength | `AVG(ABS(lin_term)) * consensus` |

### Regime Indicators

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_regime_{W}` | INT64 | Market regime (1-4) | Classification based on metrics |
| `mkt_volatility_regime_{W}` | INT64 | Vol regime (1-3) | Based on r2 and acceleration var |
| `mkt_trend_regime_{W}` | INT64 | Trend regime (1-3) | Based on consensus and strength |

### Cross-Currency Dispersion

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_csi_spread_{W}` | FLOAT64 | CSI max-min spread | `MAX(csi) - MIN(csi)` |
| `mkt_csi_concentration_{W}` | FLOAT64 | CSI Herfindahl index | `SUM(csi²) / SUM(csi)²` |
| `mkt_strongest_currency_{W}` | STRING | Strongest currency | `ARGMAX(csi_lin_str)` |
| `mkt_weakest_currency_{W}` | STRING | Weakest currency | `ARGMIN(csi_lin_str)` |

### Momentum Distribution

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_pct_accelerating_{W}` | FLOAT64 | % pairs with quad > 0 | `SUM(IF(quad>0,1,0)) / 28` |
| `mkt_pct_decelerating_{W}` | FLOAT64 | % pairs with quad < 0 | `SUM(IF(quad<0,1,0)) / 28` |
| `mkt_pct_strong_trend_{W}` | FLOAT64 | % pairs with high r2 | `SUM(IF(r2>0.7,1,0)) / 28` |

### Cross-Window Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `mkt_short_long_div_{W}` | FLOAT64 | Short vs long window divergence | `avg_lin_45 - avg_lin_2880` |
| `mkt_momentum_change_{W}` | FLOAT64 | Market momentum delta | `mkt_avg_lin - LAG(mkt_avg_lin)` |

---

## Column Count Per Table

- **Aggregate columns**: 4 per window × 7 windows = **28 columns**
- **Variance columns**: 3 per window × 7 windows = **21 columns**
- **Coordination columns**: 3 per window × 7 windows = **21 columns**
- **Regime columns**: 3 per window × 7 windows = **21 columns**
- **Dispersion columns**: 4 per window × 7 windows = **28 columns**
- **Distribution columns**: 3 per window × 7 windows = **21 columns**
- **Cross-window columns**: 2 per window × 7 windows = **14 columns**
- **Metadata**: interval_time = 1 column
- **Total per table**: **155 columns**

---

## SQL Template

```sql
-- Market-wide regression features
WITH all_pairs AS (
  SELECT interval_time, 'eurusd' as pair, reg_quad_term_{W}, reg_lin_term_{W}, reg_acceleration_{W}, reg_r2_{W}, reg_curv_sign_{W}, reg_trend_str_{W} FROM reg_eurusd
  UNION ALL
  SELECT interval_time, 'gbpusd' as pair, reg_quad_term_{W}, reg_lin_term_{W}, reg_acceleration_{W}, reg_r2_{W}, reg_curv_sign_{W}, reg_trend_str_{W} FROM reg_gbpusd
  -- ... (all 28 pairs)
),
all_csi AS (
  SELECT interval_time, 'usd' as currency, csi_lin_str_{W} FROM csi_reg_usd
  UNION ALL
  SELECT interval_time, 'eur' as currency, csi_lin_str_{W} FROM csi_reg_eur
  -- ... (all 8 currencies)
),
market_agg AS (
  SELECT
    interval_time,

    -- Averages
    AVG(reg_quad_term_{W}) as mkt_avg_quad_{W},
    AVG(reg_lin_term_{W}) as mkt_avg_lin_{W},
    AVG(reg_acceleration_{W}) as mkt_avg_accel_{W},
    AVG(reg_r2_{W}) as mkt_avg_r2_{W},

    -- Variances
    VARIANCE(reg_quad_term_{W}) as mkt_var_quad_{W},
    VARIANCE(reg_lin_term_{W}) as mkt_var_lin_{W},
    VARIANCE(reg_acceleration_{W}) as mkt_var_accel_{W},

    -- Coordination
    1 - SAFE_DIVIDE(VARIANCE(reg_lin_term_{W}), POWER(MAX(ABS(reg_lin_term_{W})), 2)) as mkt_coordination_{W},
    AVG(SIGN(reg_lin_term_{W})) as mkt_consensus_{W},

    -- Distribution
    SUM(IF(reg_quad_term_{W} > 0, 1, 0)) / 28.0 as mkt_pct_accelerating_{W},
    SUM(IF(reg_quad_term_{W} < 0, 1, 0)) / 28.0 as mkt_pct_decelerating_{W},
    SUM(IF(reg_r2_{W} > 0.7, 1, 0)) / 28.0 as mkt_pct_strong_trend_{W}

  FROM all_pairs
  GROUP BY interval_time
),
csi_agg AS (
  SELECT
    interval_time,
    MAX(csi_lin_str_{W}) - MIN(csi_lin_str_{W}) as mkt_csi_spread_{W},
    MAX_BY(currency, csi_lin_str_{W}) as mkt_strongest_currency_{W},
    MIN_BY(currency, csi_lin_str_{W}) as mkt_weakest_currency_{W}
  FROM all_csi
  GROUP BY interval_time
)
SELECT
  m.*,
  c.mkt_csi_spread_{W},
  c.mkt_strongest_currency_{W},
  c.mkt_weakest_currency_{W},

  -- Derived
  m.mkt_avg_lin_{W} * m.mkt_consensus_{W} as mkt_strength_{W},

  -- Regime classification
  CASE
    WHEN m.mkt_consensus_{W} > 0.5 AND m.mkt_coordination_{W} > 0.7 THEN 1  -- Strong coordinated trend
    WHEN m.mkt_consensus_{W} > 0.5 AND m.mkt_coordination_{W} <= 0.7 THEN 2 -- Weak coordinated trend
    WHEN m.mkt_consensus_{W} <= 0.5 AND m.mkt_var_lin_{W} > 0.5 THEN 3      -- High dispersion
    ELSE 4                                                                   -- Mixed/consolidation
  END as mkt_regime_{W},

  -- Momentum change
  m.mkt_avg_lin_{W} - LAG(m.mkt_avg_lin_{W}, 1) OVER (ORDER BY m.interval_time) as mkt_momentum_change_{W}

FROM market_agg m
JOIN csi_agg c ON m.interval_time = c.interval_time
ORDER BY m.interval_time
```

---

## Regime Definitions

### Market Regime (mkt_regime)
| Value | Name | Criteria |
|-------|------|----------|
| 1 | Strong Coordinated | consensus > 0.5 AND coordination > 0.7 |
| 2 | Weak Coordinated | consensus > 0.5 AND coordination ≤ 0.7 |
| 3 | High Dispersion | consensus ≤ 0.5 AND variance > 0.5 |
| 4 | Consolidation | All other |

### Volatility Regime (mkt_volatility_regime)
| Value | Name | Criteria |
|-------|------|----------|
| 1 | Low Vol | avg_r2 > 0.8 AND var_accel < 0.3 |
| 2 | Normal Vol | 0.5 < avg_r2 ≤ 0.8 |
| 3 | High Vol | avg_r2 ≤ 0.5 OR var_accel > 0.5 |

### Trend Regime (mkt_trend_regime)
| Value | Name | Criteria |
|-------|------|----------|
| 1 | Trending | |consensus| > 0.7 AND strength > 0.5 |
| 2 | Transitioning | 0.3 < |consensus| ≤ 0.7 |
| 3 | Ranging | |consensus| ≤ 0.3 |

---

## IDX vs BQX Interpretation

### IDX (mkt_reg) - Price-Derived
- **Source**: Price polynomial fits from all pairs
- **Interpretation**: Market-wide price trend behavior
- **Use Case**: Fundamental market regime detection

### BQX (mkt_reg_bqx) - Momentum-Derived
- **Source**: BQX polynomial fits from all pairs
- **Interpretation**: Market-wide momentum behavior
- **Use Case**: Momentum exhaustion regime detection

### Cross (mkt_reg_cross) - IDX-BQX Comparison
- **Source**: Both IDX and BQX metrics
- **Interpretation**: Price vs momentum divergence
- **Use Case**: Leading indicator for regime changes

---

## Table List (4 Total)

```
mkt_reg              # IDX market aggregation (155 columns)
mkt_reg_bqx          # BQX market aggregation (155 columns)
mkt_reg_cross        # IDX-BQX cross metrics (~80 columns)
mkt_reg_regime       # Regime classification focus (~50 columns)
```

---

*Specification created: 2025-11-29*
