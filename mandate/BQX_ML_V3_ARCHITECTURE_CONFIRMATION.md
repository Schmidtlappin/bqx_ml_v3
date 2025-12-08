# ✅ BQX ML V3 ARCHITECTURE CONFIRMATION & RATIONALIZATION
**Date**: 2025-12-08 (Updated)
**Status**: DEFINITIVE ARCHITECTURE SPECIFICATION
**Purpose**: Confirm and rationalize the 784-model multi-horizon ensemble architecture

> **IMPORTANT UPDATE (2025-12-08)**: Architecture updated to 784 models (28 pairs × 7 horizons × 4 ensemble members). Target accuracy: 95%+. Deploy farthest horizon achieving threshold.

---

## 🎯 ARCHITECTURE CONFIRMATION

### ✅ CONFIRMED: Core Architecture

**YES - BQX ML V3 consists of:**

1. **28 Independent Currency Pair Models**
   - One complete modeling system per currency pair
   - Absolute isolation between pairs (no cross-contamination)
   - Each pair's model operates independently

2. **Predicting Future BQX Values**
   - Target: BQX momentum values (NOT raw prices)
   - Direction: Future intervals (forward-looking)
   - Source: Derived from historical price movements

3. **7 Prediction Horizons per Model (Updated 2025-12-08)**
   - h15: 15 intervals ahead (highest accuracy, ~94-98%)
   - h30: 30 intervals ahead (~91-96%)
   - h45: 45 intervals ahead (~88-94%)
   - h60: 60 intervals ahead (~85-92%)
   - h75: 75 intervals ahead (~82-90%)
   - h90: 90 intervals ahead (~78-88%)
   - h105: 105 intervals ahead (~75-85%)
   - **Deployment**: Use FARTHEST horizon achieving ≥95% accuracy

4. **4 Ensemble Members per Horizon (NEW 2025-12-08)**
   - LightGBM (Base Learner 1)
   - XGBoost (Base Learner 2)
   - CatBoost (Base Learner 3)
   - Meta-learner (LSTM/LogReg stacking)

### 📊 Total Model Count (Updated 2025-12-08)

```
Architecture: 28 Independent Modeling Systems with Multi-Horizon Ensembles
├── Each system: 1 currency pair
├── Each system contains: 7 horizon-specific ensembles
├── Each ensemble contains: 4 models (3 base + 1 meta-learner)
└── Total models: 28 pairs × 7 horizons × 4 ensemble = 784 models

Organization:
- 28 independent systems (one per pair)
- 784 total models (28 per pair = 7 horizons × 4 ensemble)
- Complete isolation between pairs
- Ensemble stacking: LightGBM + XGBoost + CatBoost → Meta-learner
- Target accuracy: 95%+ directional accuracy
- Deployment: Farthest horizon achieving ≥95% per pair
```

---

## 🏗️ ARCHITECTURAL DEEP DIVE

### The 28 Currency Pairs

```
Majors (7):
├── EURUSD  (EUR/USD - Euro vs US Dollar)
├── GBPUSD  (GBP/USD - British Pound vs US Dollar)
├── USDJPY  (USD/JPY - US Dollar vs Japanese Yen)
├── USDCHF  (USD/CHF - US Dollar vs Swiss Franc)
├── AUDUSD  (AUD/USD - Australian Dollar vs US Dollar)
├── USDCAD  (USD/CAD - US Dollar vs Canadian Dollar)
└── NZDUSD  (NZD/USD - New Zealand Dollar vs US Dollar)

EUR Crosses (6):
├── EURGBP  (EUR/GBP)
├── EURJPY  (EUR/JPY)
├── EURCHF  (EUR/CHF)
├── EURAUD  (EUR/AUD)
├── EURCAD  (EUR/CAD)
└── EURNZD  (EUR/NZD)

GBP Crosses (5):
├── GBPJPY  (GBP/JPY)
├── GBPCHF  (GBP/CHF)
├── GBPAUD  (GBP/AUD)
├── GBPCAD  (GBP/CAD)
└── GBPNZD  (GBP/NZD)

AUD Crosses (4):
├── AUDJPY  (AUD/JPY)
├── AUDCHF  (AUD/CHF)
├── AUDCAD  (AUD/CAD)
└── AUDNZD  (AUD/NZD)

NZD Crosses (3):
├── NZDJPY  (NZD/JPY)
├── NZDCHF  (NZD/CHF)
└── NZDCAD  (NZD/CAD)

Other Crosses (3):
├── CADJPY  (CAD/JPY)
├── CADCHF  (CAD/CHF)
└── CHFJPY  (CHF/JPY)

TOTAL: 28 currency pairs
```

### What Each Model Predicts: BQX Values

**BQX = Backward-looking Momentum Indicator**

```python
# BQX Calculation
BQX[window] = ((price[t] - price[t-window]) / price[t-window]) * 100

# Example for EURUSD at time T:
bqx_90 = ((close[T] - close[T-90]) / close[T-90]) * 100
bqx_90 = ((1.0850 - 1.0800) / 1.0800) * 100
bqx_90 = 0.463%  # Price moved up 0.463% over last 90 intervals
```

**Prediction Target**:
```python
# Model predicts FUTURE BQX values
target_h30 = BQX value 30 intervals in the future
target_h60 = BQX value 60 intervals in the future

# NOT predicting raw price!
# Predicting: "How much momentum will there be N intervals ahead?"
```

### The 7 Prediction Horizons (Updated 2025-12-08)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               TRADING TIMELINE (Intervals)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NOW  ────→ 15 ────→ 30 ────→ 45 ────→ 60 ────→ 75 ────→ 90 ────→ 105      │
│   ↑         ↑         ↑         ↑         ↑         ↑         ↑         ↑   │
│   │         │         │         │         │         │         │         │   │
│ Current   h15       h30       h45       h60       h75       h90      h105   │
│           │         │         │         │         │         │         │     │
│      Scalping   Quick    Standard   Hourly   Extended  Session  Long-term  │
│        94-98%   91-96%    88-94%    85-92%    82-90%    78-88%    75-85%   │
│                                                                              │
│  DEPLOYMENT: Select farthest horizon achieving ≥95% accuracy                │
└─────────────────────────────────────────────────────────────────────────────┘

Granularity: 15-interval steps
Range: 15 to 105 intervals (h15 to h105)
Deployment Strategy: Train all 7 horizons, deploy farthest ≥95% per pair
Expected: Most pairs deploy h30-h60 (optimal accuracy-lookahead tradeoff)
```

---

## 💡 STRATEGIC RATIONALE

### 1. Why 28 Independent Models?

#### **Unique Market Dynamics Per Pair**

**Each currency pair has distinct characteristics:**

```
EURUSD Characteristics:
├── Most liquid pair (40% of daily FX volume)
├── Tight spreads (0.1-0.2 pips)
├── Driven by: ECB policy, USD strength, EU-US economic differentials
├── Volatility: Low to medium (50-80 pips/day)
└── Trading sessions: 24-hour, peak during EU-US overlap

USDJPY Characteristics:
├── Second most liquid (14% of volume)
├── Medium spreads (0.3-0.5 pips)
├── Driven by: BOJ interventions, risk sentiment, carry trades
├── Volatility: Medium (60-100 pips/day)
└── Trading sessions: Peak during Tokyo and NY sessions

GBPJPY Characteristics:
├── Lower liquidity (3% of volume)
├── Wider spreads (2-4 pips)
├── Driven by: BOE vs BOJ policy, Brexit impacts, risk appetite
├── Volatility: High (120-180 pips/day)
└── Trading sessions: Peak during London hours
```

**Why This Matters:**
- EURUSD needs high-precision, low-noise models
- USDJPY needs models that capture intervention patterns
- GBPJPY needs models that handle high volatility

**One unified model CANNOT capture these differences effectively.**

#### **Prevents Cross-Contamination**

```python
# WRONG: Shared model
model.fit(all_pairs_data)  # EURUSD patterns pollute GBPJPY predictions

# CORRECT: Independent models
eurusd_model.fit(eurusd_data)  # Pure EURUSD patterns
gbpjpy_model.fit(gbpjpy_data)  # Pure GBPJPY patterns
```

**Benefits:**
- Each model learns ONLY its pair's patterns
- No dilution of signal from unrelated pairs
- Optimal feature weighting per pair
- Can tune hyperparameters per pair

#### **Scalability and Maintenance**

```
Advantages:
├── Parallel Training: All 28 can train simultaneously
├── Independent Updates: Update EURUSD without affecting GBPUSD
├── Fault Isolation: GBPJPY model failure doesn't impact EURUSD
├── Performance Tracking: Clear attribution per pair
└── Easy Expansion: Add new pairs without retraining existing
```

---

### 2. Why Predict BQX Values (Not Raw Prices)?

#### **BQX Captures Pure Momentum Signal**

**Raw Price Prediction Problems:**
```python
# Problem 1: Scale Variance
EURUSD: price = 1.0850 (small numbers)
USDJPY: price = 149.50 (large numbers)
GBPJPY: price = 186.20 (very large)
# Models struggle with different scales

# Problem 2: Non-Stationarity
Price series have trends, making them non-stationary
Models trained on trending data fail on ranging markets

# Problem 3: Absolute vs Relative
Price = 1.0850 means nothing without context
Is this high or low? Trending or stable?
```

**BQX Solution:**
```python
# BQX is scale-invariant (always percentages)
EURUSD bqx_90 = 0.463%
USDJPY bqx_90 = 0.487%
GBPJPY bqx_90 = 0.521%
# All on same scale! Models can compare directly

# BQX is stationary (bounded by market moves)
BQX typically ranges from -5% to +5%
Extreme moves are rare and meaningful
Distribution is relatively stable

# BQX captures MOMENTUM not absolute levels
bqx_90 = 0.463% → "Moving up at moderate pace"
bqx_90 = -2.1% → "Strong downward momentum"
bqx_90 = 0.05% → "Virtually no momentum"
```

#### **Trading Relevance**

**Traders care about MOMENTUM, not absolute price:**

```
Question: "Will EURUSD go up?"
├── Unhelpful answer: "Price will be 1.0875"
└── Helpful answer: "Strong positive momentum (+0.8% BQX predicted)"

Question: "Should I enter this trade?"
├── Unhelpful: Price target of 1.0900 (means nothing alone)
└── Helpful: BQX prediction shows accelerating upward momentum

Question: "How confident is this signal?"
├── Unhelpful: Price may or may not reach 1.0900
└── Helpful: BQX shows sustained positive momentum across multiple horizons
```

#### **Paradigm Shift Advantage (2024-11-24)**

**BQX as BOTH feature AND target:**
```python
# Historical BQX as features (autoregressive)
features = [
    LAG(bqx_90, 1),   # BQX 1 interval ago
    LAG(bqx_90, 5),   # BQX 5 intervals ago
    LAG(bqx_90, 10),  # BQX 10 intervals ago
    ...
]

# Future BQX as target
target = LEAD(bqx_90, 30)  # BQX 30 intervals ahead

# This is POWERFUL: Use momentum to predict future momentum!
# Momentum has persistence and patterns
# Like using velocity to predict future velocity (physics)
```

---

### 3. Why 7 Prediction Horizons? (Updated 2025-12-08)

#### **Different Trading Styles Need Different Horizons**

**The Trading Spectrum:**

```
┌────────────────────────────────────────────────────────────────┐
│                     TRADING STYLES                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  SCALPING (h15, h30)                                           │
│  ├── Hold time: 2-15 minutes                                   │
│  ├── Needs: Ultra-short predictions                            │
│  ├── Priority: High confidence, quick execution                │
│  └── Risk: Very tight stops, small profits                     │
│                                                                │
│  DAY TRADING (h30, h45, h60)                                   │
│  ├── Hold time: 15 minutes - 4 hours                           │
│  ├── Needs: Short to medium predictions                        │
│  ├── Priority: Balance of confidence and profit potential      │
│  └── Risk: Medium stops, medium profits                        │
│                                                                │
│  SWING TRADING (h60, h75, h90)                                 │
│  ├── Hold time: 4 hours - 2 days                               │
│  ├── Needs: Medium to longer predictions                       │
│  ├── Priority: Trend following, larger profits                 │
│  └── Risk: Wider stops, larger profits                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Why Not Just One Horizon?**

```python
# Problem: One size does NOT fit all

# Scalper with h90 model:
prediction_90_intervals = model.predict()  # 9 hours ahead!
# ❌ TOO FAR: Scalper needs to know next 15-30 intervals
# ❌ USELESS: Market can change 10 times before horizon reached

# Swing trader with h15 model:
prediction_15_intervals = model.predict()  # 1.5 hours ahead
# ❌ TOO SHORT: Doesn't capture the multi-hour trend
# ❌ NOISY: Too granular, missing the bigger picture
```

#### **Multi-Horizon Consensus Signals**

**Combine multiple horizons for confirmation:**

```python
def generate_trading_signal(predictions):
    """
    Use multiple horizons to build conviction
    """

    # All short horizons positive = Strong BUY
    if predictions['h15'] > 0 and predictions['h30'] > 0 and predictions['h45'] > 0:
        if predictions['h60'] > 0:  # Medium-term confirmation
            return Signal.STRONG_BUY

    # Short positive but medium negative = CAUTION
    if predictions['h30'] > 0 but predictions['h60'] < 0:
        return Signal.NEUTRAL  # Conflicting signals

    # All horizons aligned = High confidence
    if all(p > 0 for p in predictions.values()):
        return Signal.VERY_STRONG_BUY

    # Divergence = Risk
    if predictions['h15'] > 0 but predictions['h90'] < 0:
        return Signal.SHORT_TERM_ONLY  # Quick profit, don't hold
```

#### **Risk-Adjusted Position Sizing**

```python
def calculate_position_size(predictions, base_size=1.0):
    """
    Larger positions when horizons agree
    """

    # Calculate horizon agreement
    positive_count = sum(1 for p in predictions.values() if p > 0)
    agreement_ratio = positive_count / len(predictions)

    # Calculate prediction strength
    avg_magnitude = np.mean([abs(p) for p in predictions.values()])

    # Position size multiplier
    confidence_multiplier = agreement_ratio * (avg_magnitude / 0.5)

    position_size = base_size * confidence_multiplier

    return min(position_size, base_size * 2.0)  # Cap at 2x

# Example:
predictions = {
    'h15': 0.8,   # Strong positive
    'h30': 0.6,   # Medium positive
    'h45': 0.5,   # Medium positive
    'h60': 0.7,   # Strong positive
    'h75': 0.4,   # Weak positive
    'h90': 0.3    # Weak positive
}
# All positive → High agreement → Larger position (1.5x base)

predictions_mixed = {
    'h15': 0.8,
    'h30': 0.4,
    'h45': -0.1,  # Negative!
    'h60': 0.2,
    'h75': -0.3,  # Negative!
    'h90': -0.5   # Strong negative!
}
# Mixed signals → Low agreement → Smaller position (0.4x base)
```

#### **Performance Optimization Per Horizon**

**Different horizons have different predictability:**

```
Expected Performance by Horizon (Updated 2025-12-08):
┌──────────┬────────────┬──────────────────┬─────────────┬────────────┐
│ Horizon  │ R² Score   │ Dir. Accuracy    │ Difficulty  │ Deploy?    │
├──────────┼────────────┼──────────────────┼─────────────┼────────────┤
│ h15      │ 0.40-0.50  │ 94-98%          │ Easiest     │ Likely ✓   │
│ h30      │ 0.38-0.45  │ 91-96%          │ Easy        │ Likely ✓   │
│ h45      │ 0.35-0.42  │ 88-94%          │ Medium      │ Maybe      │
│ h60      │ 0.32-0.40  │ 85-92%          │ Medium      │ Maybe      │
│ h75      │ 0.30-0.38  │ 82-90%          │ Harder      │ Less likely│
│ h90      │ 0.28-0.35  │ 78-88%          │ Hard        │ Unlikely   │
│ h105     │ 0.25-0.32  │ 75-85%          │ Hardest     │ Rare       │
└──────────┴────────────┴──────────────────┴─────────────┴────────────┘

DEPLOYMENT STRATEGY: Deploy FARTHEST horizon achieving ≥95% accuracy
Expected: Most pairs will deploy h30-h45 (optimal lookahead with high accuracy)
Target: 95%+ directional accuracy per horizon-pair combination
```

**Horizon-Specific Optimization:**

```python
# Short horizons: Need fast, lightweight models
if horizon <= 30:
    model = RandomForestRegressor(
        n_estimators=100,  # Fewer trees (speed)
        max_depth=10,      # Shallower (speed)
        min_samples_split=20  # Less overfitting
    )

# Medium horizons: Balanced complexity
elif horizon <= 60:
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_split=15
    )

# Long horizons: Can handle complexity
else:
    model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1  # Capture subtler patterns
    )
```

---

## 🎯 THE COMPLETE ARCHITECTURE (Updated 2025-12-08)

### System Organization

```
BQX ML V3 Architecture (Multi-Horizon Ensemble):
└── 28 Independent Currency Pair Systems
    ├── EURUSD System (28 models = 7 horizons × 4 ensemble)
    │   ├── h15 Ensemble → Predicts BQX 15 intervals ahead
    │   │   ├── LightGBM (base learner)
    │   │   ├── XGBoost (base learner)
    │   │   ├── CatBoost (base learner)
    │   │   └── Meta-learner (LSTM/LogReg stacking)
    │   ├── h30 Ensemble → Predicts BQX 30 intervals ahead
    │   ├── h45 Ensemble → Predicts BQX 45 intervals ahead
    │   ├── h60 Ensemble → Predicts BQX 60 intervals ahead
    │   ├── h75 Ensemble → Predicts BQX 75 intervals ahead
    │   ├── h90 Ensemble → Predicts BQX 90 intervals ahead
    │   └── h105 Ensemble → Predicts BQX 105 intervals ahead
    │
    ├── GBPUSD System (28 models)
    ├── USDJPY System (28 models)
    ├── ... (25 more pairs)
    └── CHFJPY System (28 models)

TOTAL: 28 systems × 7 horizons × 4 ensemble = 784 models
ACCURACY TARGET: 95%+ directional accuracy
DEPLOYMENT: Farthest horizon achieving ≥95% per pair
```

### Data Flow

```
Market Data (OHLCV)
         ↓
    ┌────┴────┐
    ↓         ↓
  IDX        BQX
(Prices)  (Momentum)
    ↓         ↓
  Features Engineering
    ├── BQX lags (1, 2, 3, 5, 10, ...)
    ├── IDX indicators (RSI, MACD, ...)
    ├── BQX windows (45, 90, 180, ...)
    ├── Statistical features
    └── Time features (session, hour)
         ↓
    Feature Matrix
    (30-50 features)
         ↓
    ┌────┴────────────────────┐
    ↓                         ↓
Model h15                 Model h105
    ↓                         ↓
Prediction               Prediction
BQX @ t+15              BQX @ t+105
         ↓
    Trading System
    ├── Combine horizons
    ├── Generate signals
    ├── Size positions
    └── Execute trades
```

### Model Training Pipeline (Updated 2025-12-08)

```python
for pair in 28_currency_pairs:
    # 1. Load data for this pair ONLY
    data = load_pair_data(pair)  # Isolated data

    # 2. Feature Selection (SHAP-based, run once per pair)
    top_features = shap_feature_selection(data, n_features=500)

    # 3. Walk-forward data split (MANDATORY for time series)
    train = data[T-365:T-30]
    val = data[T-30:T-7]
    test = data[T-7:T]

    # 4. For each horizon, train ensemble
    for horizon in [15, 30, 45, 60, 75, 90, 105]:
        # Create target: BQX value at horizon
        target = LEAD(bqx_90, horizon)

        # Train 3 base learners
        lgb = LightGBM().fit(train[top_features], train[target])
        xgb = XGBoost().fit(train[top_features], train[target])
        cat = CatBoost().fit(train[top_features], train[target])

        # Train meta-learner on base predictions
        base_preds = stack([lgb.predict(val), xgb.predict(val), cat.predict(val)])
        meta = MetaLearner().fit(base_preds, val[target])

        # Evaluate ensemble
        ensemble_pred = meta.predict(stack([lgb.predict(test), ...]))
        accuracy = directional_accuracy(ensemble_pred, test[target])

        # Save if meets threshold
        save_ensemble(pair, horizon, [lgb, xgb, cat, meta], accuracy)

    # Result: 28 models (7 horizons × 4 ensemble) for this pair
    # Deploy: Farthest horizon achieving ≥95% accuracy
```

---

## 📊 EXPECTED OUTCOMES (Updated 2025-12-08)

### Performance Targets

```
Per Ensemble (4 models per horizon):
├── Directional Accuracy: 75-98% (depending on horizon)
├── Target: ≥95% for deployment
├── R² Score: 0.25-0.50
├── Sharpe Ratio: 1.5-2.5
└── Max Drawdown: < 10%

Per Pair System (7 horizons × 4 ensemble = 28 models):
├── Directional Accuracy: 95%+ (deployed horizon)
├── Deployed Horizon: Farthest achieving ≥95%
├── Expected Deploy: h30-h60 for most pairs
├── Signal Confidence: Very high (ensemble + multi-horizon)
└── Risk Management: Enhanced (horizon selection based on accuracy)

Overall System (28 pairs × 7 horizons × 4 ensemble):
├── Total Models: 784
├── Training Time: 24-48 hours (parallel, BigQuery ML)
├── Prediction Latency: < 100ms per ensemble
├── Cost: ~$277/month (optimized - BigQuery ML + Spot VMs)
└── Trading Coverage: Complete FX market with 95%+ accuracy
```

### Business Value

```
For Scalpers (h15, h30):
├── Entry/exit timing: Precise 15-30 interval windows
├── Risk: Tight stops (5-10 pips)
└── Profit: Small but frequent (2-5 pips per trade)

For Day Traders (h30, h45, h60):
├── Entry/exit timing: Optimal 30-60 interval positioning
├── Risk: Medium stops (15-25 pips)
└── Profit: Medium, moderate frequency (10-30 pips per trade)

For Swing Traders (h60, h75, h90):
├── Entry/exit timing: Trend following 60-90 intervals
├── Risk: Wide stops (30-50 pips)
└── Profit: Large, less frequent (40-100 pips per trade)
```

---

## ✅ ARCHITECTURE VALIDATION

### Why This Architecture is Optimal

**1. Independence → Specialization**
- Each pair gets a specialist model
- No dilution from unrelated pairs
- Optimal feature weighting per pair

**2. BQX Target → Trading Relevance**
- Momentum is what traders need
- Scale-invariant predictions
- Stationary, bounded target space

**3. Multi-Horizon → Versatility**
- Serves all trading styles
- Enables consensus signals
- Optimizes per-horizon performance

**4. 7 Horizons → Complete Coverage**
- Scalping to swing trading
- Short, medium, long-term
- 15-interval granularity
- Deploy farthest horizon achieving ≥95%

**5. 784 Total Models → Comprehensive Ensemble**
- Parallel training (24-48 hours)
- 4-member ensemble per horizon (LightGBM, XGBoost, CatBoost, Meta-learner)
- Clear performance attribution
- 95%+ directional accuracy target

---

## 🎯 CONCLUSION (Updated 2025-12-08)

**CONFIRMED AND RATIONALIZED:**

BQX ML V3's architecture of **28 independent currency pair systems**, each containing **7 horizon-specific 4-member ensembles** that predict **future BQX momentum values**, represents an optimal balance of:

1. **Specialization** (independent per pair)
2. **Trading Relevance** (BQX momentum targets)
3. **Versatility** (multi-horizon predictions)
4. **Performance** (ensemble stacking for 95%+ accuracy)
5. **Scalability** (784 models with BigQuery ML cost optimization)
6. **Intelligent Deployment** (farthest horizon achieving threshold)

This architecture directly addresses real trading needs while maintaining technical excellence and operational feasibility.

**Total: 28 systems × 7 horizons × 4 ensemble = 784 models**
**Ensemble: LightGBM + XGBoost + CatBoost → Meta-learner (LSTM/LogReg)**
**Purpose: Predict future BQX momentum at 7 trading-relevant horizons**
**Target: 95%+ directional accuracy (deploy farthest horizon achieving this)**
**Cost: ~$277/month (optimized with BigQuery ML + Spot VMs)**
**Result: Complete FX market coverage for all trading styles**

---

*Architecture confirmed: 2025-11-27*
*Updated: 2025-12-08 (784 models, 7 horizons, 4-member ensemble, 95%+ target)*
*This is the definitive specification for BQX ML V3*
