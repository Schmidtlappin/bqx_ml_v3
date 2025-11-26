# BQX ML V3 Pipeline - Visual Summary

## 🎯 THE CORE CONCEPT: Predicting Future BQX Values

```
PAST                    NOW                     FUTURE
[Historical Data] --> [Features] --> [Model] --> [BQX Predictions]
     ↓                    ↓                           ↓
 IDX + BQX            280 Features              Future BQX Values
```

---

## 📊 SIMPLIFIED DATA FLOW

```
┌─────────────────────────────────────────────────────────────┐
│                     RAW OHLCV DATA                          │
│                   (1-minute bars)                           │
└──────────────┬──────────────────┬──────────────────────────┘
               ↓                  ↓
        ┌──────v──────┐    ┌─────v──────┐
        │ IDX TABLES  │    │ BQX TABLES │
        │  (Raw Values)│    │ (Momentum) │
        └──────┬──────┘    └─────┬──────┘
               │                  │
               └─────────┬────────┘
                        ↓
                ┌───────v────────┐
                │ FEATURE MATRIX │
                │  280 Features  │
                └───────┬────────┘
                        ↓
                ┌───────v────────┐
                │     MODEL      │
                │ (28 Independent)│
                └───────┬────────┘
                        ↓
                ┌───────v────────┐
                │  PREDICTIONS   │
                │ Future BQX     │
                └────────────────┘
```

---

## 🔄 THE DUAL FEATURE ADVANTAGE

### **What Makes This Different:**

```python
Traditional Approach:          BQX ML V3 Approach:
────────────────────          ────────────────────

Features → Price              Features → BQX Values
   ↓                             ↓
Just price history            IDX (price) + BQX (momentum)
   ↓                             ↓
Predict next price           Predict future momentum (BQX)
```

### **Why Two Feature Types?**

| Feature Type | What It Captures | Example Features | Purpose |
|-------------|------------------|------------------|---------|
| **IDX** | Market State | `idx_mid = (high+low)/2` | Absolute price levels |
| **BQX** | Market Momentum | `bqx = idx - future_avg` | Direction & strength |

---

## 🎯 HOW PREDICTIONS WORK

### **Step-by-Step Process:**

```
Time: T-180 ... T-2, T-1, T (NOW)         T+90 (FUTURE)
        │         │    │   │                │
        └─────────┴────┴───┘                │
                │                            │
        Historical Features            Target to Predict
                │                            │
        ┌───────v────────┐                  │
        │  Extract:      │                  │
        │  - IDX lags    │                  │
        │  - BQX lags    │                  │
        │  - Derivatives │                  │
        │  - Aggregations│                  │
        └───────┬────────┘                  │
                │                            │
                ↓                            │
        ┌────────────────┐                  │
        │  Feed to Model │                  │
        └───────┬────────┘                  │
                │                            │
                └──────────────────────────→ BQX at T+90
```

---

## 📈 EXAMPLE: EURUSD PREDICTION

### **Input Features (at time T):**

```python
# IDX Features (Raw market state)
idx_mid_current = 1.0850          # Current price level
idx_mid_lag_1i = 1.0849           # Price 1 interval ago
idx_mid_lag_5i = 1.0847           # Price 5 intervals ago
idx_mean_45i = 1.0845             # Average over 45 intervals
idx_std_45i = 0.0003              # Volatility over 45 intervals

# BQX Features (Momentum indicators)
bqx_45w_current = 0.0002          # Current 45-interval momentum
bqx_45w_lag_1i = 0.0001           # Momentum 1 interval ago
bqx_velocity_5i = 0.00001         # Rate of momentum change
bqx_acceleration_1i = 0.000001    # Momentum acceleration

# Total: ~280 features
```

### **Model Processing:**

```python
def predict_eurusd_bqx():
    # 1. Combine all features
    X = np.array([idx_features + bqx_features])  # Shape: (1, 280)

    # 2. Apply trained model
    model = load_model('EURUSD_model.pkl')

    # 3. Get prediction
    future_bqx_90 = model.predict(X)  # Predicts BQX 90 intervals ahead

    return future_bqx_90  # e.g., 0.0003 (bullish momentum expected)
```

### **Interpretation:**

```
Predicted BQX_90 = 0.0003

What this means:
- Positive value → Bullish momentum expected
- Magnitude 0.0003 → Moderate strength
- In 90 intervals, price expected to be above future average
- Trading signal: Consider long position
```

---

## 🔑 KEY INSIGHTS

### **1. Why Predict BQX Instead of Price?**

```
Price Prediction:              BQX Prediction:
├─ Harder (absolute levels)    ├─ Easier (relative momentum)
├─ Non-stationary              ├─ More stationary
├─ Large range                 ├─ Bounded range
└─ Noisy                       └─ Smoother patterns
```

### **2. The Power of Dual Features**

```python
# IDX tells us WHERE we are
idx_level = "Price is at 1.0850"

# BQX tells us WHERE WE'RE GOING
bqx_momentum = "Momentum is positive and accelerating"

# Combined: Full market picture
prediction = f"From {idx_level}, with {bqx_momentum}, expect continued rise"
```

### **3. INTERVAL-CENTRIC Advantage**

```sql
-- All calculations use ROWS BETWEEN (intervals, not time)
AVG(bqx_mid) OVER (ROWS BETWEEN 89 PRECEDING AND CURRENT ROW)
                    ↑
            This means exactly 90 intervals
            regardless of time gaps (weekends, holidays)
```

---

## 🚀 PRODUCTION FLOW

### **Real-Time Pipeline:**

```
Every Minute:
────────────
1. New OHLCV bar arrives
   ↓
2. Calculate IDX values
   ↓
3. Calculate BQX values (using historical window)
   ↓
4. Update feature tables
   ↓
5. Generate feature vector
   ↓
6. Run model prediction
   ↓
7. Output: Future BQX for multiple horizons
   - BQX_45: Short-term momentum
   - BQX_90: Medium-term momentum
   - BQX_180: Long-term momentum
```

---

## 📊 WHY THIS WORKS

### **The Secret Sauce:**

1. **Autoregressive Power**: BQX values are autocorrelated
   - Past momentum predicts future momentum
   - Patterns repeat at different scales

2. **Dual Signal Strength**:
   - IDX provides context (where in the range)
   - BQX provides direction (which way we're heading)

3. **Temporal Consistency**:
   - INTERVAL-CENTRIC = no weekend gaps
   - Features always comparable
   - Models learn stable patterns

4. **Multiple Horizons**:
   - Different patterns at different scales
   - Ensemble combines all horizons
   - Robust to noise

---

## 🎯 BOTTOM LINE

```
Input:  280 features (IDX + BQX) from last 180 intervals
Model:  Ensemble of Linear + XGBoost + LSTM
Output: Future BQX value at chosen horizon

Result: Accurate momentum predictions that can drive trading decisions
```

**The pipeline transforms raw price data into momentum predictions through a sophisticated dual-feature architecture, leveraging both absolute price levels (IDX) and relative momentum (BQX) to predict where the market momentum will be in the future.**