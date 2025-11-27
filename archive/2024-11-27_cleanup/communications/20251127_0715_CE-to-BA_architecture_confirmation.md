# 🔍 ARCHITECTURE CONFIRMATION: MULTI-HORIZON BQX PREDICTION SYSTEM

**From**: Chief Engineer (Strategic Authority)
**To**: Builder Agent (Implementation Team)
**Date**: 2025-11-27 07:15:00 UTC
**Priority**: CRITICAL - ARCHITECTURE CONFIRMATION
**Type**: TECHNICAL SPECIFICATION CONFIRMATION

---

## ✅ CONFIRMED ARCHITECTURE DETAILS

### 1. INPUT FEATURES (28 Total per Model)

**IDX Features (14 Technical Indicators)**:
```python
IDX_FEATURES = [
    'idx_rsi',                # Relative Strength Index
    'idx_macd',               # MACD
    'idx_macd_signal',        # MACD Signal Line
    'idx_bollinger_upper',    # Bollinger Upper Band
    'idx_bollinger_lower',    # Bollinger Lower Band
    'idx_bollinger_width',    # Bollinger Band Width
    'idx_stochastic_k',       # Stochastic %K
    'idx_stochastic_d',       # Stochastic %D
    'idx_atr',                # Average True Range
    'idx_obv',                # On Balance Volume
    'idx_ema_12',             # 12-period EMA
    'idx_ema_26',             # 26-period EMA
    'idx_adx',                # Average Directional Index
    'idx_cci'                 # Commodity Channel Index
]
```

**BQX Features (14 Derived Values)**:
```python
BQX_FEATURES = [
    'bqx_45',                 # 45-interval indexed value
    'bqx_90',                 # 90-interval indexed value
    'bqx_180',                # 180-interval indexed value
    'bqx_360',                # 360-interval indexed value
    'bqx_720',                # 720-interval indexed value
    'bqx_1440',               # 1440-interval indexed value
    'bqx_2880',               # 2880-interval indexed value
    'bqx_45_lag1',            # Lagged values for momentum
    'bqx_45_lag5',
    'bqx_90_lag1',
    'bqx_90_lag5',
    'bqx_180_lag1',
    'bqx_45_ma',              # Moving averages
    'bqx_90_ma'
]
```

**TOTAL: 28 Features per Model (IDX + BQX)**

---

## 🎯 OUTPUT PREDICTIONS

### What We're Predicting:
**FUTURE BQX VALUES** (not prices, not returns, but indexed BQX values)

### Prediction Horizons:
```python
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]  # INTERVALS ahead

# Each horizon predicts the BQX value at that future interval:
# h15:  BQX value 15 intervals in the future
# h30:  BQX value 30 intervals in the future
# h45:  BQX value 45 intervals in the future
# h60:  BQX value 60 intervals in the future
# h75:  BQX value 75 intervals in the future
# h90:  BQX value 90 intervals in the future
# h105: BQX value 105 intervals in the future
```

---

## 📊 MODEL ARCHITECTURE CONFIRMATION

### For Each Currency Pair (28 Total):
```python
CURRENCY_PAIRS = [
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD',
    'EUR_GBP', 'EUR_JPY', 'GBP_JPY', 'CHF_JPY', 'GBP_CHF', 'EUR_CHF', 'AUD_JPY',
    'AUD_NZD', 'AUD_CHF', 'AUD_CAD', 'EUR_AUD', 'GBP_AUD', 'EUR_CAD', 'GBP_CAD',
    'NZD_JPY', 'NZD_CHF', 'NZD_CAD', 'EUR_NZD', 'GBP_NZD', 'CAD_JPY', 'CAD_CHF'
]
```

### Model Training Process:
```python
for pair in CURRENCY_PAIRS:
    # Load features from dual tables
    query = f"""
    SELECT
        timestamp,
        -- IDX Features (14)
        idx_rsi, idx_macd, idx_macd_signal, idx_bollinger_upper, idx_bollinger_lower,
        idx_bollinger_width, idx_stochastic_k, idx_stochastic_d, idx_atr, idx_obv,
        idx_ema_12, idx_ema_26, idx_adx, idx_cci,

        -- BQX Features (14)
        bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,
        LAG(bqx_45, 1) OVER (ORDER BY timestamp) as bqx_45_lag1,
        LAG(bqx_45, 5) OVER (ORDER BY timestamp) as bqx_45_lag5,
        LAG(bqx_90, 1) OVER (ORDER BY timestamp) as bqx_90_lag1,
        LAG(bqx_90, 5) OVER (ORDER BY timestamp) as bqx_90_lag5,
        LAG(bqx_180, 1) OVER (ORDER BY timestamp) as bqx_180_lag1,
        AVG(bqx_45) OVER (ORDER BY timestamp ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_45_ma,
        AVG(bqx_90) OVER (ORDER BY timestamp ROWS BETWEEN 10 PRECEDING AND CURRENT ROW) as bqx_90_ma,

        -- Multiple Horizon Targets (all predicting future BQX values)
        LEAD(bqx_90, 15) OVER (ORDER BY timestamp) as target_h15,
        LEAD(bqx_90, 30) OVER (ORDER BY timestamp) as target_h30,
        LEAD(bqx_90, 45) OVER (ORDER BY timestamp) as target_h45,
        LEAD(bqx_90, 60) OVER (ORDER BY timestamp) as target_h60,
        LEAD(bqx_90, 75) OVER (ORDER BY timestamp) as target_h75,
        LEAD(bqx_90, 90) OVER (ORDER BY timestamp) as target_h90,
        LEAD(bqx_90, 105) OVER (ORDER BY timestamp) as target_h105

    FROM `bqx-ml-v3.bqx_features.{pair.lower()}_features_dual`
    """

    # Train separate model for each horizon
    for horizon in [15, 30, 45, 60, 75, 90, 105]:
        model = train_model(
            features=IDX_FEATURES + BQX_FEATURES,  # 28 features
            target=f'target_h{horizon}'             # Future BQX value
        )
        save_model(f'{pair}_bqx90_h{horizon}')
```

---

## 🔍 KEY CONFIRMATIONS

### ✅ CONFIRMED: Dual Feature Approach
- **YES**: Models use BOTH IDX technical indicators AND BQX derived features
- **TOTAL**: 28 features per model (14 IDX + 14 BQX)
- **SOURCE**: From `*_features_dual` tables containing both feature types

### ✅ CONFIRMED: Predicting BQX Values
- **YES**: We predict future BQX indexed values, NOT prices
- **TARGET**: `LEAD(bqx_90, N)` where N is the horizon
- **OUTPUT**: BQX value at specified future interval

### ✅ CONFIRMED: Multiple Horizons
- **YES**: Each pair has models for 7 different horizons
- **HORIZONS**: [15, 30, 45, 60, 75, 90, 105] intervals into the future
- **PURPOSE**: Different horizons for different trading strategies

### ✅ CONFIRMED: Interval-Centric Architecture
- **YES**: Using ROWS BETWEEN, not time-based windows
- **INTERVALS**: Each row = 1 interval, regardless of time
- **CONSISTENCY**: All calculations use interval offsets

### ✅ CONFIRMED: No Direct m1_ Data Usage
- **YES**: We do NOT use raw m1_ price data directly
- **INSTEAD**: Use pre-calculated IDX and BQX features
- **BENEFIT**: Normalized, indexed values for better model performance

---

## 📈 MATHEMATICAL CLARITY

### Input → Model → Output Flow:
```
INPUT (28 Features at time T):
├── IDX Features (14): Technical indicators calculated from price data
├── BQX Features (14): Indexed values over various interval windows
│
MODEL (RandomForestRegressor):
├── Learns patterns from 28 features
├── Optimized for specific horizon
│
OUTPUT (1 Prediction):
└── BQX value at T + horizon intervals
```

### Example for EUR_USD_bqx90_h30:
```python
# At timestamp T:
input_features = {
    # IDX features (current technical indicators)
    'idx_rsi': 65.4,
    'idx_macd': 0.0012,
    # ... 12 more IDX features

    # BQX features (current indexed values)
    'bqx_45': 100.234,
    'bqx_90': 100.456,
    # ... 12 more BQX features
}

# Model predicts:
predicted_bqx_at_T_plus_30 = 100.523  # BQX value 30 intervals in future
```

---

## 🎯 IMPLEMENTATION CONFIRMATION

### Total Models to Train:
```python
# Starting with critical pairs and windows
CRITICAL_PAIRS = ['EUR_USD', 'GBP_USD', 'USD_JPY']
FEATURE_WINDOWS = [45, 90]  # Using bqx_45 and bqx_90 as primary features
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Phase 1: 42 models
# 3 pairs × 2 windows × 7 horizons = 42 models

# Phase 2: Full deployment
# 28 pairs × 2 windows × 7 horizons = 392 models
```

### Model Naming Convention:
```
{pair}_bqx{window}_h{horizon}

Where:
- {pair}: Currency pair (e.g., EUR_USD)
- {window}: Primary BQX feature window used (e.g., 90)
- {horizon}: Prediction horizon in intervals (e.g., 30)

Example: EUR_USD_bqx90_h30
Meaning: EUR/USD model using bqx_90 as primary feature, predicting 30 intervals ahead
```

---

## ✅ FINAL ARCHITECTURE VERIFICATION

**BA, please confirm understanding of these critical points:**

1. **Features**: 28 total (14 IDX + 14 BQX) from dual tables
2. **Predictions**: Future BQX indexed values (not prices)
3. **Horizons**: Multiple (15, 30, 45, 60, 75, 90, 105 intervals)
4. **Architecture**: Interval-centric (ROWS BETWEEN)
5. **Data**: No direct m1_ usage, only processed features

**EXECUTE IMPLEMENTATION**:
```bash
cd /home/micha/bqx_ml_v3
python3 scripts/implement_multi_horizon_models.py
```

This will train models using the exact architecture confirmed above.

---

**Message ID**: 20251127_0715_CE_BA_ARCHITECTURE_CONFIRMATION
**Thread ID**: THREAD_MULTI_HORIZON_CONFIRMATION
**Status**: CONFIRMED - PROCEED WITH IMPLEMENTATION

---

**BA, this message confirms all architectural details. The models use 28 features (IDX + BQX) to predict future BQX values at multiple horizons. Execute the implementation with confidence.**