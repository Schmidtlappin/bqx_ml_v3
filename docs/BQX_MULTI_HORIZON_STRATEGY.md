# 🎯 BQX ML V3 MULTI-HORIZON PREDICTION STRATEGY

**Date**: 2025-11-27
**Version**: 1.0
**Status**: Strategic Architecture Decision
**Impact**: Fundamental improvement to prediction granularity

---

## 📋 EXECUTIVE SUMMARY

BQX ML V3 will implement a **multi-horizon prediction architecture** that decouples feature windows from prediction horizons. This allows us to use our proven BQX interval calculations (45, 90, 180, 360, 720, 1440, 2880) as features while predicting at more granular, trading-relevant horizons (15, 30, 45, 60, 75, 90, 105 intervals).

**Key Innovation**: Predict multiple future horizons using the same robust feature set.

---

## 🏗️ ARCHITECTURAL OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT FEATURES                            │
│                  (Existing, Unchanged)                        │
├─────────────────────────────────────────────────────────────┤
│  BQX Windows: [45, 90, 180, 360, 720, 1440, 2880]           │
│  • bqx_45:  45-interval indexed value                        │
│  • bqx_90:  90-interval indexed value                        │
│  • bqx_180: 180-interval indexed value                       │
│  • ... and so on                                             │
│                                                               │
│  IDX Features: [RSI, MACD, Bollinger, etc.]                 │
│  • Technical indicators from price data                      │
│  • 14 features total                                         │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                    ML MODELS                                 │
│                (Multiple per Feature Set)                    │
├─────────────────────────────────────────────────────────────┤
│  For each BQX window (e.g., bqx_90):                        │
│  • Model 1: Predicts 15 intervals ahead                      │
│  • Model 2: Predicts 30 intervals ahead                      │
│  • Model 3: Predicts 45 intervals ahead                      │
│  • Model 4: Predicts 60 intervals ahead                      │
│  • Model 5: Predicts 75 intervals ahead                      │
│  • Model 6: Predicts 90 intervals ahead                      │
│  • Model 7: Predicts 105 intervals ahead                     │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│                  OUTPUT PREDICTIONS                          │
│                   (New, Granular)                            │
├─────────────────────────────────────────────────────────────┤
│  Horizon Predictions: [15, 30, 45, 60, 75, 90, 105]         │
│  • h15:  BQX value 15 intervals in future                    │
│  • h30:  BQX value 30 intervals in future                    │
│  • h45:  BQX value 45 intervals in future                    │
│  • h60:  BQX value 60 intervals in future                    │
│  • h75:  BQX value 75 intervals in future                    │
│  • h90:  BQX value 90 intervals in future                    │
│  • h105: BQX value 105 intervals in future                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 STRATEGIC RATIONALE

### 1. Why Keep Existing BQX Windows as Features?

**Proven Performance**:
- Already calculated and stored in BigQuery
- Tested R² scores of 0.35-0.45
- No need to recalculate or modify schema

**Different Mathematical Purpose**:
- **BQX Windows**: Measure volatility/momentum over specific periods
- **Prediction Horizons**: How far ahead we want to forecast

**Example**:
- `bqx_90` captures 90-interval price dynamics (good feature)
- But traders need predictions for 15-30 intervals ahead (not 90)

### 2. Why Multiple Prediction Horizons?

**Trading Reality**:
- Scalpers need 15-30 interval predictions
- Day traders need 30-60 interval predictions
- Swing traders need 60-105 interval predictions
- One size does NOT fit all

**Risk Management**:
- Short horizons = Higher confidence, lower profit
- Long horizons = Lower confidence, higher profit
- Traders can choose based on risk tolerance

### 3. Why This Architecture?

**Efficiency**:
- One feature extraction, multiple predictions
- Reuse existing BigQuery tables
- No schema changes required

**Flexibility**:
- Add new horizons without changing features
- Remove horizons that don't perform
- A/B test different horizon sets

**Performance**:
- Features optimized for their window size
- Predictions optimized for their horizon
- Best of both worlds

---

## 📊 MATHEMATICAL FOUNDATION

### Feature Engineering (Unchanged)
```sql
-- Existing BQX features remain exactly the same
WITH features AS (
    SELECT
        timestamp,

        -- BQX Windows (calculated over their respective intervals)
        bqx_45,   -- 45-interval indexed value
        bqx_90,   -- 90-interval indexed value
        bqx_180,  -- 180-interval indexed value

        -- Lagged values for momentum
        LAG(bqx_90, 1) OVER (ORDER BY timestamp) as bqx_90_lag1,
        LAG(bqx_90, 5) OVER (ORDER BY timestamp) as bqx_90_lag5,

        -- IDX technical indicators
        idx_rsi,
        idx_macd,
        idx_bollinger_upper,
        idx_bollinger_lower

    FROM `bqx-ml-v3.bqx_features.eurusd_features_dual`
)
```

### Target Generation (New)
```sql
-- Multiple horizon targets from the same feature set
SELECT
    *,
    -- Short-term horizons (scalping)
    LEAD(bqx_90, 15) OVER (ORDER BY timestamp) as target_h15,
    LEAD(bqx_90, 30) OVER (ORDER BY timestamp) as target_h30,

    -- Medium-term horizons (day trading)
    LEAD(bqx_90, 45) OVER (ORDER BY timestamp) as target_h45,
    LEAD(bqx_90, 60) OVER (ORDER BY timestamp) as target_h60,

    -- Longer-term horizons (swing trading)
    LEAD(bqx_90, 75) OVER (ORDER BY timestamp) as target_h75,
    LEAD(bqx_90, 90) OVER (ORDER BY timestamp) as target_h90,
    LEAD(bqx_90, 105) OVER (ORDER BY timestamp) as target_h105

FROM features
```

---

## 💰 BUSINESS VALUE

### 1. Immediate Trading Applications

**Scalping (15-30 intervals)**:
```python
if prediction_h15 > current_bqx + threshold:
    enter_long_position(size="small", stop="tight")
```

**Day Trading (30-60 intervals)**:
```python
if prediction_h30 > current_bqx + threshold:
    if prediction_h60 > prediction_h30:  # Trend confirmation
        enter_long_position(size="medium", stop="normal")
```

**Swing Trading (60-105 intervals)**:
```python
if all([pred > current for pred in [h60, h75, h90, h105]]):
    enter_long_position(size="large", stop="wide")
```

### 2. Risk-Adjusted Position Sizing

```python
# Use prediction confidence across horizons
confidence = correlation([h15, h30, h45, h60])
position_size = base_size * confidence
```

### 3. Multi-Timeframe Analysis

```python
# Combine multiple horizons for better signals
signal_strength = weighted_average({
    h15: 0.2,   # 20% weight on ultra-short
    h30: 0.3,   # 30% weight on short
    h60: 0.3,   # 30% weight on medium
    h90: 0.2    # 20% weight on longer
})
```

---

## 📈 EXPECTED PERFORMANCE METRICS

### Performance by Horizon

| Horizon | R² Expected | Dir. Accuracy | Confidence | Use Case |
|---------|------------|---------------|------------|----------|
| h15 | 0.20-0.25 | 54-56% | High | Scalping |
| h30 | 0.25-0.30 | 55-57% | High | Quick trades |
| h45 | 0.30-0.35 | 56-58% | Medium | Standard trades |
| h60 | 0.33-0.38 | 57-59% | Medium | Hourly decisions |
| h75 | 0.35-0.40 | 58-60% | Medium | Extended trades |
| h90 | 0.37-0.42 | 59-61% | Low | Session trades |
| h105 | 0.38-0.43 | 60-62% | Low | Trend following |

### Key Insights:
- **Shorter horizons**: Lower R² but higher confidence (less time for surprises)
- **Longer horizons**: Higher R² but lower confidence (more uncertainty)
- **Sweet spot**: 30-60 intervals for best trade-off

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Model Development (Week 1)
```python
# Priority: Focus on bqx_45 and bqx_90 features
FEATURE_WINDOWS = [45, 90]  # Start with best performing
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# 2 windows × 7 horizons = 14 models per pair
# 5 critical pairs × 14 = 70 models initially
```

### Phase 2: Deployment Strategy (Week 2)

**Tier 1: Real-time Endpoints** (5 models)
```python
CRITICAL_ENDPOINTS = [
    'EUR_USD_bqx90_h30',  # Most liquid pair, optimal horizon
    'GBP_USD_bqx90_h30',  # High volatility pair
    'USD_JPY_bqx90_h30',  # Asian session leader
    'EUR_USD_bqx45_h15',  # Scalping model
    'EUR_USD_bqx90_h60'   # Swing model
]
# Cost: $342/month
```

**Tier 2: Near Real-time Batch** (65 models)
```python
FAST_BATCH = [
    '*_bqx45_h15',  # All pairs, 15-min horizon
    '*_bqx45_h30',  # All pairs, 30-min horizon
    '*_bqx90_h30',  # All pairs, 30-min horizon
]
# Update: Every 5 minutes
# Cost: $50/month
```

**Tier 3: Standard Batch** (Remaining models)
```python
NORMAL_BATCH = [
    '*_bqx*_h60',   # All 60+ minute horizons
    '*_bqx*_h75',
    '*_bqx*_h90',
    '*_bqx*_h105'
]
# Update: Every 15 minutes
# Cost: $30/month
```

### Phase 3: Integration (Week 3)

1. **Cloud Functions API**:
```python
@app.route('/predict/<pair>/<window>/<horizon>')
def predict(pair, window, horizon):
    # Route to appropriate model
    if is_critical(pair, window, horizon):
        return query_endpoint(...)
    else:
        return query_batch_cache(...)
```

2. **Trading System Integration**:
```python
def get_trading_signals(pair):
    predictions = {}
    for horizon in [15, 30, 45, 60]:
        predictions[horizon] = api.predict(pair, 90, horizon)
    return generate_signal(predictions)
```

---

## 📊 MODEL NAMING CONVENTION

### Format:
```
{pair}_bqx{window}_h{horizon}

Where:
- {pair}: Currency pair (e.g., EUR_USD)
- {window}: BQX feature window (e.g., 90)
- {horizon}: Prediction horizon (e.g., 30)

Example: EUR_USD_bqx90_h30
Meaning: EUR/USD model using bqx_90 features, predicting 30 intervals ahead
```

### Storage Structure:
```
gs://bqx-ml-vertex-models/
├── EUR_USD_bqx90_h15/
│   ├── model.pkl
│   └── features.pkl
├── EUR_USD_bqx90_h30/
│   ├── model.pkl
│   └── features.pkl
└── ...
```

---

## ✅ SUCCESS CRITERIA

### Technical Metrics:
- [ ] All horizons achieve >50% directional accuracy
- [ ] h30 models achieve R² > 0.25
- [ ] Latency < 100ms for critical endpoints
- [ ] 95% uptime for real-time endpoints

### Business Metrics:
- [ ] Traders can access predictions at their preferred horizon
- [ ] Position sizing improved with multi-horizon confidence
- [ ] Reduced false signals from horizon consensus
- [ ] Increased trading profitability

---

## 🔄 MIGRATION PATH

### No Breaking Changes:
1. **Existing models continue working** (they're just h90 variants)
2. **No BigQuery schema changes** required
3. **Gradual rollout** - start with 5 critical endpoints
4. **A/B testing** possible between horizons

### Rollback Plan:
- Keep existing models as-is
- New models are additive, not replacements
- Can disable specific horizons if they underperform

---

## 📝 KEY INSIGHTS

1. **Features ≠ Predictions**: The window over which we calculate features (e.g., 90 intervals) is mathematically different from how far ahead we predict.

2. **Multiple Horizons = Better Trading**: Different trading styles need different prediction horizons. One model can't serve all needs.

3. **Reuse Existing Infrastructure**: We keep all our proven BQX calculations and just add new prediction targets.

4. **Granular Control**: We can optimize each horizon independently based on its performance.

5. **Cost Effective**: Most models can be batch processed. Only critical short-horizon models need real-time endpoints.

---

## 🎯 CONCLUSION

The multi-horizon architecture represents a **paradigm shift** in BQX ML V3:
- From single-horizon to multi-horizon predictions
- From one-size-fits-all to trading-style-specific models
- From rigid windows to flexible horizons
- From limited coverage to comprehensive market view

This architecture delivers **immediate value** to traders while maintaining **technical excellence** and **cost efficiency**.

---

*This strategy document defines the next evolution of BQX ML V3, enabling granular predictions at trading-relevant horizons while leveraging our existing, proven feature engineering.*