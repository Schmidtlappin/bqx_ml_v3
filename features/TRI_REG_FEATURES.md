# Triangular Regression Features Specification

**Feature Type**: TRI_REG (Triangular Regression Analysis)
**Table Patterns**: `tri_reg_{curr1}_{curr2}_{curr3}`
**Total Tables**: 36 (56 valid triangles × variant reduction)
**Dependency**: reg_{pair}, csi_reg_{currency} (polynomial features)

---

## Architecture Note

**CRITICAL: INTERVAL-CENTRIC**

All windows (W) refer to **INTERVALS (rows), NOT time units**:
- `W = 45` means 45 consecutive data rows
- Polynomial formula: `x = np.arange(W) = [0, 1, 2, ..., W-1]`

---

## Executive Summary

Triangular regression features capture polynomial trend relationships between three currencies that form a triangular arbitrage relationship. These features detect when polynomial trends diverge across the triangle, indicating potential arbitrage opportunities or trend exhaustion.

---

## Triangular Arbitrage Concept

For currencies A, B, C:
```
A/B × B/C × C/A = 1  (theoretical equilibrium)
```

When polynomial trends diverge:
```
trend(A/B) + trend(B/C) ≠ -trend(A/C)
```
This divergence signals opportunity.

---

## Table Structure

### Naming Convention
```
tri_reg_{curr1}_{curr2}_{curr3}         # IDX variant
tri_reg_bqx_{curr1}_{curr2}_{curr3}     # BQX variant
```

### Valid Triangles (56 unique)
Formed by selecting 3 currencies from 8:
C(8,3) = 56 triangles

Example triangles:
- EUR-USD-GBP (eurusd, gbpusd, eurgbp)
- EUR-USD-JPY (eurusd, usdjpy, eurjpy)
- USD-JPY-CHF (usdjpy, usdchf, chfjpy)

---

## Feature Columns

### Polynomial Coefficient Triangular Sum

For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `tri_quad_sum_{W}` | FLOAT64 | Sum of quad terms (should → 0) | `sign1*q1 + sign2*q2 + sign3*q3` |
| `tri_lin_sum_{W}` | FLOAT64 | Sum of lin terms (should → 0) | `sign1*l1 + sign2*l2 + sign3*l3` |
| `tri_accel_sum_{W}` | FLOAT64 | Sum of acceleration | `sign1*a1 + sign2*a2 + sign3*a3` |

### Divergence Metrics

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `tri_quad_div_{W}` | FLOAT64 | Quad divergence (abs) | `ABS(tri_quad_sum)` |
| `tri_lin_div_{W}` | FLOAT64 | Lin divergence (abs) | `ABS(tri_lin_sum)` |
| `tri_div_score_{W}` | FLOAT64 | Combined divergence | `sqrt(quad_div² + lin_div²)` |
| `tri_div_zscore_{W}` | FLOAT64 | Divergence z-score | `(div_score - avg) / std` |

### Trend Alignment

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `tri_alignment_{W}` | FLOAT64 | How aligned are trends | `1 - div_score / max_possible` |
| `tri_consensus_{W}` | INT64 | Trend consensus (-3 to +3) | `sign(l1) + sign(l2) + sign(l3)` |
| `tri_dominant_pair_{W}` | STRING | Strongest trend pair | `argmax(abs(lin_term))` |

### Goodness of Fit Comparison

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `tri_r2_min_{W}` | FLOAT64 | Min R² across triangle | `MIN(r2_1, r2_2, r2_3)` |
| `tri_r2_max_{W}` | FLOAT64 | Max R² across triangle | `MAX(r2_1, r2_2, r2_3)` |
| `tri_r2_spread_{W}` | FLOAT64 | R² spread | `r2_max - r2_min` |

### Arbitrage Signals

| Column | Type | Description | Formula |
|--------|------|-------------|---------|
| `tri_arb_signal_{W}` | INT64 | Arbitrage signal (±1, 0) | `IF(div_zscore > 2, sign(div), 0)` |
| `tri_arb_strength_{W}` | FLOAT64 | Arbitrage opportunity size | `div_score * avg_r2` |
| `tri_reversal_prob_{W}` | FLOAT64 | Probability of convergence | `sigmoid(div_zscore - 2)` |

---

## Column Count Per Table

- **Sum columns**: 3 per window × 7 windows = **21 columns**
- **Divergence columns**: 4 per window × 7 windows = **28 columns**
- **Alignment columns**: 3 per window × 7 windows = **21 columns**
- **R² columns**: 3 per window × 7 windows = **21 columns**
- **Arbitrage columns**: 3 per window × 7 windows = **21 columns**
- **Metadata**: interval_time, curr1, curr2, curr3, pair1, pair2, pair3 = 7 columns
- **Total per table**: **119 columns**

---

## SQL Template

```sql
-- Triangular regression features for {curr1}-{curr2}-{curr3}
WITH triangle_data AS (
  SELECT
    p1.interval_time,

    -- Pair 1: {pair1} (curr1/curr2 or curr2/curr1)
    {sign1} as sign1,
    p1.reg_quad_term_{W} as q1,
    p1.reg_lin_term_{W} as l1,
    p1.reg_acceleration_{W} as a1,
    p1.reg_r2_{W} as r2_1,

    -- Pair 2: {pair2} (curr2/curr3 or curr3/curr2)
    {sign2} as sign2,
    p2.reg_quad_term_{W} as q2,
    p2.reg_lin_term_{W} as l2,
    p2.reg_acceleration_{W} as a2,
    p2.reg_r2_{W} as r2_2,

    -- Pair 3: {pair3} (curr3/curr1 or curr1/curr3)
    {sign3} as sign3,
    p3.reg_quad_term_{W} as q3,
    p3.reg_lin_term_{W} as l3,
    p3.reg_acceleration_{W} as a3,
    p3.reg_r2_{W} as r2_3

  FROM `bqx_ml_v3_features.reg_{pair1}` p1
  JOIN `bqx_ml_v3_features.reg_{pair2}` p2 ON p1.interval_time = p2.interval_time
  JOIN `bqx_ml_v3_features.reg_{pair3}` p3 ON p1.interval_time = p3.interval_time
),
with_sums AS (
  SELECT
    *,
    '{curr1}' as curr1, '{curr2}' as curr2, '{curr3}' as curr3,

    -- Triangular sums (should approach 0 in equilibrium)
    (sign1 * q1 + sign2 * q2 + sign3 * q3) as tri_quad_sum_{W},
    (sign1 * l1 + sign2 * l2 + sign3 * l3) as tri_lin_sum_{W},
    (sign1 * a1 + sign2 * a2 + sign3 * a3) as tri_accel_sum_{W},

    -- R² comparison
    LEAST(r2_1, r2_2, r2_3) as tri_r2_min_{W},
    GREATEST(r2_1, r2_2, r2_3) as tri_r2_max_{W},
    GREATEST(r2_1, r2_2, r2_3) - LEAST(r2_1, r2_2, r2_3) as tri_r2_spread_{W},

    -- Consensus
    SIGN(l1) + SIGN(l2) + SIGN(l3) as tri_consensus_{W}

  FROM triangle_data
),
with_div AS (
  SELECT
    *,
    ABS(tri_quad_sum_{W}) as tri_quad_div_{W},
    ABS(tri_lin_sum_{W}) as tri_lin_div_{W},
    SQRT(POWER(tri_quad_sum_{W}, 2) + POWER(tri_lin_sum_{W}, 2)) as tri_div_score_{W},
    1 - SAFE_DIVIDE(
      SQRT(POWER(tri_quad_sum_{W}, 2) + POWER(tri_lin_sum_{W}, 2)),
      SQRT(POWER(ABS(q1)+ABS(q2)+ABS(q3), 2) + POWER(ABS(l1)+ABS(l2)+ABS(l3), 2))
    ) as tri_alignment_{W}
  FROM with_sums
),
with_zscore AS (
  SELECT
    *,
    (tri_div_score_{W} - AVG(tri_div_score_{W}) OVER ()) /
      NULLIF(STDDEV(tri_div_score_{W}) OVER (), 0) as tri_div_zscore_{W}
  FROM with_div
)
SELECT
  *,
  IF(ABS(tri_div_zscore_{W}) > 2, SIGN(tri_lin_sum_{W}), 0) as tri_arb_signal_{W},
  tri_div_score_{W} * (tri_r2_min_{W} + tri_r2_max_{W}) / 2 as tri_arb_strength_{W},
  1 / (1 + EXP(-(tri_div_zscore_{W} - 2))) as tri_reversal_prob_{W}
FROM with_zscore
ORDER BY interval_time
```

---

## Sign Adjustment Logic

For triangle EUR-USD-GBP with pairs EURUSD, GBPUSD, EURGBP:
- EURUSD: EUR/USD (EUR strong when up) → sign = +1
- GBPUSD: GBP/USD (USD weak when up) → sign = -1 for USD path
- EURGBP: EUR/GBP (EUR strong vs GBP) → sign = +1 for EUR path

The signs ensure: `EUR→USD + USD→GBP + GBP→EUR = 0` at equilibrium.

---

## Table List (36 Total)

### IDX Variant (18 tables - most liquid triangles)
```
tri_reg_eur_usd_gbp, tri_reg_eur_usd_jpy, tri_reg_eur_usd_chf,
tri_reg_eur_gbp_jpy, tri_reg_eur_gbp_chf, tri_reg_eur_jpy_chf,
tri_reg_usd_gbp_jpy, tri_reg_usd_gbp_chf, tri_reg_usd_jpy_chf,
tri_reg_gbp_jpy_chf, tri_reg_eur_usd_aud, tri_reg_eur_usd_cad,
tri_reg_usd_aud_cad, tri_reg_usd_aud_nzd, tri_reg_aud_cad_nzd,
tri_reg_eur_gbp_aud, tri_reg_gbp_aud_nzd, tri_reg_jpy_chf_cad
```

### BQX Variant (18 tables)
```
tri_reg_bqx_eur_usd_gbp, tri_reg_bqx_eur_usd_jpy, tri_reg_bqx_eur_usd_chf,
tri_reg_bqx_eur_gbp_jpy, tri_reg_bqx_eur_gbp_chf, tri_reg_bqx_eur_jpy_chf,
tri_reg_bqx_usd_gbp_jpy, tri_reg_bqx_usd_gbp_chf, tri_reg_bqx_usd_jpy_chf,
tri_reg_bqx_gbp_jpy_chf, tri_reg_bqx_eur_usd_aud, tri_reg_bqx_eur_usd_cad,
tri_reg_bqx_usd_aud_cad, tri_reg_bqx_usd_aud_nzd, tri_reg_bqx_aud_cad_nzd,
tri_reg_bqx_eur_gbp_aud, tri_reg_bqx_gbp_aud_nzd, tri_reg_bqx_jpy_chf_cad
```

---

*Specification created: 2025-11-29*
