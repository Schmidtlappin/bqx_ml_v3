# BQX ML Feature Matrix Architecture

## Overview

The BQX ML system uses a three-dimensional feature space organized as:

```
Feature × Centric × Variant
```

This architecture ensures comprehensive market coverage by analyzing data from multiple perspectives (centrics), applying multiple analytical techniques (features), and using both raw and transformed data sources (variants).

---

## Core Concepts

### What is a Feature?

A **Feature** is a type of analytical calculation applied to market data. Each feature captures different aspects of market behavior:

| Feature | Purpose | Example Outputs |
|---------|---------|-----------------|
| **Regression** | Fit polynomial curves to detect trends | Slope, curvature, R², residuals |
| **Lag** | Capture historical patterns | Previous values at various lookbacks |
| **Regime** | Detect market states | Trending, ranging, volatile regimes |
| **Aggregation** | Summarize statistics | Mean, std, min, max, percentiles |
| **Alignment** | Measure timeframe coherence | Multi-window agreement scores |
| **Correlation** | Measure relationships | Rolling correlations, cointegration |
| **Momentum** | Measure rate of change | ROC, acceleration, momentum persistence |
| **Volatility** | Measure dispersion | ATR, realized vol, vol regimes |

### What is a Centric?

A **Centric** is a perspective or aggregation level for analyzing market data:

| Centric | Scope | Entities | Purpose |
|---------|-------|----------|---------|
| **Primary** | Individual pair | 28 pairs | Intrinsic pair dynamics |
| **Variant** | Currency family | 7 families | Currency-specific momentum |
| **Covariant** | Pair relationships | ~50 relationships | Cross-pair dependencies |
| **Triangulation** | Arbitrage relationships | 18 triangles | Synthetic value vs actual |
| **Secondary** | Currency strength | 8 currencies | Fundamental flow signals |
| **Tertiary** | Market-wide | 1 market | Global conditions |

### What is a Variant?

A **Variant** is the underlying data source used for calculations:

| Variant | Source | Description |
|---------|--------|-------------|
| **IDX** | idx_* tables | Raw indexed OHLCM values |
| **BQX** | bqx_* tables | BQX-transformed values (backward-looking momentum) |

---

## The Feature Matrix

### Complete 3D Structure

Every combination of Feature × Centric × Variant produces a unique set of analytical tables:

```
Total Combinations = 8 Features × 6 Centrics × 2 Variants = 96 cell types
```

### Matrix Visualization

```
                              C E N T R I C S
              ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
              │ PRIMARY  │ VARIANT  │COVARIANT │ TRIANGUL │SECONDARY │ TERTIARY │
              │ (28)     │ (7)      │ (~50)    │ (18)     │ (8)      │ (1)      │
┌─────────────┼────┬─────┼────┬─────┼────┬─────┼────┬─────┼────┬─────┼────┬─────┤
│ F  │ REG    │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│ E  ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│ A  │ LAG    │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│ T  ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│ U  │ REGIME │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│ R  ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│ E  │ AGG    │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│ S  ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│    │ ALIGN  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│    ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│    │ CORR   │ -  │ -   │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│    ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│    │ MOM    │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
│    ├────────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┼────┼─────┤
│    │ VOL    │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │IDX │BQX  │
└────┴────────┴────┴─────┴────┴─────┴────┴─────┴────┴─────┴────┴─────┴────┴─────┘
```

---

## Centric Definitions

### 1. Primary (Pair-Centric)

**Scope**: Individual currency pair analysis

**Entities** (28 pairs):
- Majors: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD
- Crosses: EURGBP, EURJPY, EURCHF, EURCAD, EURAUD, EURNZD
- GBP Crosses: GBPJPY, GBPCHF, GBPCAD, GBPAUD, GBPNZD
- JPY Crosses: AUDJPY, CADJPY, CHFJPY, NZDJPY
- Others: AUDCAD, AUDCHF, AUDNZD, CADCHF, NZDCAD, NZDCHF

**Rationale**: Each pair has unique characteristics (volatility profile, trading hours, liquidity). Primary features capture intrinsic pair dynamics without cross-pair contamination.

**Tables**: `{feature}_*` (IDX), `{feature}_bqx_*` (BQX)

### 2. Variant (Family-Centric)

**Scope**: Currency family behavior (all pairs sharing a base currency)

**Entities** (7 families):
- EUR Family: EURUSD, EURGBP, EURJPY, EURCHF, EURCAD, EURAUD, EURNZD
- GBP Family: GBPUSD, GBPJPY, GBPCHF, GBPCAD, GBPAUD, GBPNZD
- AUD Family: AUDUSD, AUDJPY, AUDCAD, AUDCHF, AUDNZD
- NZD Family: NZDUSD, NZDJPY, NZDCAD, NZDCHF
- USD Family: USDJPY, USDCHF, USDCAD
- CAD Family: CADJPY, CADCHF
- CHF Family: CHFJPY

**Rationale**: When EUR is strong, all EUR pairs tend to move in the same direction (EUR appreciation). Variant features detect currency-specific momentum by aggregating behavior across all pairs in the family.

**Features**:
- Family agreement score (how many pairs moving same direction)
- Family dispersion (spread between strongest/weakest pair)
- Family momentum consensus
- Family BQX alignment

**Tables**: `var_{feature}_*` (IDX), `var_{feature}_bqx_*` (BQX)

### 3. Covariant (Cross-Pair Relationships)

**Scope**: Relationships between pairs that typically move together or opposite

**Entities** (~50 relationships):

**Positive Covariants** (move together):
- EURUSD ↔ GBPUSD (both vs USD)
- AUDUSD ↔ NZDUSD (commodity currencies)
- EURJPY ↔ GBPJPY (both vs JPY)
- EURUSD ↔ AUDUSD (risk-on currencies)

**Negative Covariants** (move opposite):
- EURUSD ↔ USDCHF (USD on opposite sides)
- EURUSD ↔ USDJPY (USD on opposite sides)
- AUDUSD ↔ USDCAD (commodity exporters)

**Rationale**: Pairs share common currencies, creating mathematical and behavioral relationships. When these relationships deviate from normal, it signals potential mean reversion or regime change.

**Features**:
- Rolling correlation (multiple windows)
- Correlation deviation from historical norm
- Correlation regime (normal, divergent, convergent)
- Cross-pair spread z-score
- Cointegration residuals

**Tables**: `cov_{feature}_*` (IDX), `cov_{feature}_bqx_*` (BQX)

### 4. Triangulation (Arbitrage Relationships)

**Scope**: Mathematical relationships between three currencies

**Entities** (18 triangles):
- EUR-USD-JPY: EURUSD × USDJPY = EURJPY
- EUR-USD-CHF: EURUSD × USDCHF = EURCHF
- EUR-USD-CAD: EURUSD × USDCAD = EURCAD
- EUR-USD-AUD: EURUSD / AUDUSD = EURAUD
- EUR-USD-NZD: EURUSD / NZDUSD = EURNZD
- GBP-USD-JPY: GBPUSD × USDJPY = GBPJPY
- GBP-USD-CHF: GBPUSD × USDCHF = GBPCHF
- GBP-USD-CAD: GBPUSD × USDCAD = GBPCAD
- GBP-USD-AUD: GBPUSD / AUDUSD = GBPAUD
- GBP-USD-NZD: GBPUSD / NZDUSD = GBPNZD
- AUD-USD-JPY: AUDUSD × USDJPY = AUDJPY
- AUD-USD-CAD: AUDUSD × USDCAD⁻¹ = AUDCAD
- AUD-USD-CHF: AUDUSD × USDCHF = AUDCHF
- AUD-USD-NZD: AUDUSD / NZDUSD = AUDNZD
- NZD-USD-JPY: NZDUSD × USDJPY = NZDJPY
- NZD-USD-CAD: NZDUSD × USDCAD⁻¹ = NZDCAD
- NZD-USD-CHF: NZDUSD × USDCHF = NZDCHF
- CAD-USD-CHF: USDCAD⁻¹ × USDCHF = CADCHF

**Rationale**: In a perfect market, synthetic prices equal actual prices. Deviations indicate:
- Temporary arbitrage opportunities
- Liquidity imbalances
- Market stress
- Mean reversion signals

**Features**:
- Triangulation error (actual - synthetic)
- Error mean reversion signal
- Error volatility
- Error regime (expanding, contracting)
- BQX triangulation alignment

**Tables**: `tri_{feature}_*` (IDX), `tri_{feature}_bqx_*` (BQX)

### 5. Secondary (Currency-Centric)

**Scope**: Aggregate strength of individual currencies

**Entities** (8 currencies):
- USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD

**Calculation Method**:
```sql
-- USD Strength Index
csi_usd = GEOMETRIC_MEAN(
    1/EURUSD,  -- USD vs EUR
    1/GBPUSD,  -- USD vs GBP
    USDJPY,    -- USD vs JPY
    USDCHF,    -- USD vs CHF
    USDCAD,    -- USD vs CAD
    1/AUDUSD,  -- USD vs AUD
    1/NZDUSD   -- USD vs NZD
)^(1/7)
```

**Rationale**: By aggregating how a currency performs against all others, we get a fundamental measure of demand/supply flow for that currency. This is more stable than any single pair.

**Features per currency**:
- Absolute strength level
- Strength momentum (rate of change)
- Strength regime (trending up/down/ranging)
- Strength percentile (relative to history)

**Differential Features**:
- For EURUSD model: EUR strength - USD strength = fundamental fair value signal

**Tables**: `csi_{feature}_*` (IDX), `csi_{feature}_bqx_*` (BQX)

### 6. Tertiary (Market-Centric)

**Scope**: Global market conditions

**Entity**: 1 (the entire FX market)

**Components**:

**a) Session Features**:
- Current session (Asian, European, American)
- Session overlap indicator
- Hours until session change
- Session-specific volatility ratio

**b) Volatility Regime**:
- Market-wide ATR (average across all pairs)
- Volatility percentile
- Volatility regime (low, normal, high, extreme)
- Cross-pair volatility dispersion

**c) Risk Sentiment**:
- Risk-on indicator (AUD, NZD strength; JPY, CHF weakness)
- Risk-off indicator (opposite)
- Risk sentiment score (-1 to +1)
- Risk momentum

**d) Market Microstructure**:
- Average spread across pairs
- Liquidity score
- Market efficiency ratio

**Rationale**: All pairs operate within the same global environment. Market-wide conditions affect all pairs and provide crucial context for model predictions.

**Tables**: `mkt_{feature}` (IDX), `mkt_{feature}_bqx` (BQX)

---

## Table Naming Convention

### Pattern

```
{prefix}_{feature}_{variant}_{entity}
```

### Components

| Component | Values | Required |
|-----------|--------|----------|
| Prefix | (none), var, cov, tri, csi, mkt | For centric |
| Feature | reg, lag, regime, agg, align, corr, mom, vol | Yes |
| Variant | (none)=IDX, bqx | Yes |
| Entity | Pair, family, relationship, currency | Yes |

### Examples

| Table Name | Feature | Variant | Centric | Entity |
|------------|---------|---------|---------|--------|
| `reg_eurusd` | Regression | IDX | Primary | EUR/USD |
| `reg_bqx_eurusd` | Regression | BQX | Primary | EUR/USD |
| `var_reg_eur` | Regression | IDX | Variant | EUR family |
| `var_reg_bqx_eur` | Regression | BQX | Variant | EUR family |
| `cov_reg_eurusd_gbpusd` | Regression | IDX | Covariant | EUR/USD↔GBP/USD |
| `cov_reg_bqx_eurusd_gbpusd` | Regression | BQX | Covariant | EUR/USD↔GBP/USD |
| `tri_reg_eur_usd_jpy` | Regression | IDX | Triangulation | EUR-USD-JPY |
| `tri_reg_bqx_eur_usd_jpy` | Regression | BQX | Triangulation | EUR-USD-JPY |
| `csi_reg_usd` | Regression | IDX | Secondary | USD |
| `csi_reg_bqx_usd` | Regression | BQX | Secondary | USD |
| `mkt_vol` | Volatility | IDX | Tertiary | Market |
| `mkt_vol_bqx` | Volatility | BQX | Tertiary | Market |

---

## Table Count Summary

| Feature | Primary | Variant | Covariant | Triangulation | Secondary | Tertiary | **Total** |
|---------|:-------:|:-------:|:---------:|:-------------:|:---------:|:--------:|:---------:|
| | 28×2 | 7×2 | 50×2 | 18×2 | 8×2 | 1×2 | |
| Regression | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Lag | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Regime | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Aggregation | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Alignment | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Correlation | 0 | 14 | 100 | 36 | 16 | 2 | 168 |
| Momentum | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| Volatility | 56 | 14 | 100 | 36 | 16 | 2 | 224 |
| **Total** | 392 | 112 | 800 | 288 | 128 | 16 | **1,736** |

---

## Why Both IDX and BQX Variants?

### IDX (Raw) Features Capture

- **Current price level** and its statistical properties
- **Raw market dynamics** (volatility, trend strength from price action)
- **Historical price patterns**
- **Absolute positioning** (where is price relative to history)

### BQX (Transformed) Features Capture

- **Momentum state** (how price is moving relative to recent history)
- **Trend persistence** (is the momentum increasing or decreasing)
- **Mean reversion signals** (is momentum at extremes)
- **Relative positioning** (where is momentum relative to its own history)

### Combined Predictive Power

The model learns relationships like:
- "When raw prices show consolidation (low IDX volatility) AND BQX shows building momentum → breakout imminent"
- "High BQX regression slope + declining IDX volatility → strong trend continuation"
- "BQX at historical extreme + IDX showing reversal pattern → mean reversion opportunity"

---

## Training Data Assembly

### For Each of 28 Models

Each pair gets its own model with features from all relevant matrix cells:

```python
train_eurusd_v2 = JOIN(
    # PRIMARY - Direct pair features
    reg_eurusd, reg_bqx_eurusd,
    lag_eurusd, lag_bqx_eurusd,
    regime_eurusd, regime_bqx_eurusd,
    agg_eurusd, agg_bqx_eurusd,
    align_eurusd, align_bqx_eurusd,
    mom_eurusd, mom_bqx_eurusd,
    vol_eurusd, vol_bqx_eurusd,

    # VARIANT - EUR family features
    var_reg_eur, var_reg_bqx_eur,
    var_lag_eur, var_lag_bqx_eur,
    # ... etc

    # COVARIANT - Related pairs
    cov_*_eurusd_gbpusd, cov_*_bqx_eurusd_gbpusd,
    cov_*_eurusd_usdchf, cov_*_bqx_eurusd_usdchf,
    # ... etc

    # TRIANGULATION - EUR-USD triangles
    tri_*_eur_usd_jpy, tri_*_bqx_eur_usd_jpy,
    # ... etc

    # SECONDARY - EUR and USD strength
    csi_*_eur, csi_*_bqx_eur,
    csi_*_usd, csi_*_bqx_usd,
    csd_*_eur_usd, csd_*_bqx_eur_usd,

    # TERTIARY - Market conditions
    mkt_*, mkt_*_bqx,

    # TARGET
    ON time
)
WHERE time > warmup_period

TARGET = bqx_eurusd.mid_360w (shifted forward N intervals)
```

### Expected Feature Count per Model

| Centric | Tables | Fields/Table | Est. Features |
|---------|--------|--------------|---------------|
| Primary | 14 | ~50 | 700 |
| Variant | 16 | ~30 | 480 |
| Covariant | ~20 | ~30 | 600 |
| Triangulation | ~10 | ~30 | 300 |
| Secondary | 12 | ~30 | 360 |
| Tertiary | 16 | ~20 | 320 |
| **Total** | ~88 | - | **~2,760** |

---

## Implementation Phases

### Phase 1: Primary Features (Current)

Complete all primary pair-centric features for both variants:

- [x] reg_* (IDX) - Existing
- [x] reg_bqx_* - Complete
- [ ] lag_bqx_*
- [ ] regime_bqx_*
- [ ] agg_bqx_*
- [ ] align_bqx_*
- [ ] mom_bqx_*
- [ ] vol_bqx_*

### Phase 2: Secondary Features

Currency strength indices:

- [ ] csi_*_usd, csi_*_eur, csi_*_gbp, etc.
- [ ] csi_*_bqx_usd, csi_*_bqx_eur, etc.
- [ ] csd_* (differentials)

### Phase 3: Covariant Features

Cross-pair relationships:

- [ ] cov_*_pair1_pair2
- [ ] cov_*_bqx_pair1_pair2

### Phase 4: Triangulation Features

Arbitrage relationships:

- [ ] tri_*_curr1_curr2_curr3
- [ ] tri_*_bqx_curr1_curr2_curr3

### Phase 5: Variant Features

Family aggregations:

- [ ] var_*_eur, var_*_gbp, etc.
- [ ] var_*_bqx_eur, var_*_bqx_gbp, etc.

### Phase 6: Tertiary Features

Market-wide features:

- [ ] mkt_*
- [ ] mkt_*_bqx

### Phase 7: Training & Modeling

- [ ] Assemble train_*_v2 tables
- [ ] Train 28 independent models
- [ ] Validate accuracy improvement
- [ ] Deploy to production

---

## Consistency Requirements

### All tables MUST use interval-centric calculations

```sql
-- CORRECT: Interval-centric (counts rows)
ORDER BY time ROWS BETWEEN 359 PRECEDING AND CURRENT ROW

-- INCORRECT: Time-centric (counts time units)
ORDER BY time RANGE BETWEEN INTERVAL 360 MINUTE PRECEDING AND CURRENT ROW
```

### Rationale

FX markets close on weekends and holidays. Time-based windows would contain fewer data points during these gaps. Interval-based windows always contain exactly N data points, ensuring consistent calculations regardless of market closures.

### Standard Windows

All features use the same window sizes for consistency:

```python
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]  # intervals
```

---

## Document History

- **Created**: 2025-11-24
- **Author**: BQX ML Architecture Team
- **Version**: 1.0

---

## References

- [BQX_FEATURES_NEW_PARADIGM.md](./BQX_FEATURES_NEW_PARADIGM.md) - Paradigm shift documentation
- [BQX_REFACTOR_PROGRESS.md](./BQX_REFACTOR_PROGRESS.md) - Implementation progress
- [BQX_TEMPORAL_ALIGNMENT_ANALYSIS.md](./BQX_TEMPORAL_ALIGNMENT_ANALYSIS.md) - Temporal alignment details
