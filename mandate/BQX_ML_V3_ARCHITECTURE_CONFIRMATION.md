# ✅ BQX ML V3 ARCHITECTURE CONFIRMATION & RATIONALIZATION
**Date**: 2025-11-27
**Status**: DEFINITIVE ARCHITECTURE SPECIFICATION
**Purpose**: Confirm and rationalize the 28-model, 7-horizon prediction architecture

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

3. **7 Prediction Horizons per Model**
   - h15: 15 intervals ahead
   - h30: 30 intervals ahead
   - h45: 45 intervals ahead
   - h60: 60 intervals ahead
   - h75: 75 intervals ahead
   - h90: 90 intervals ahead
   - h105: 105 intervals ahead

### 📊 Total Model Count

```
Architecture: 28 Independent Modeling Systems
├── Each system: 1 currency pair
├── Each system contains: 7 horizon-specific models
└── Total models: 28 pairs × 7 horizons = 196 models

Organization:
- 28 independent systems (one per pair)
- 196 total models (7 per system)
- Complete isolation between pairs
- Shared architecture across horizons
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

### The 7 Prediction Horizons

```
┌─────────────────────────────────────────────────────────────┐
│               TRADING TIMELINE (Intervals)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  NOW  ────→ 15 ────→ 30 ────→ 45 ────→ 60 ────→ 75 ────→ 90 ────→ 105
│   ↑         ↑         ↑         ↑         ↑         ↑         ↑         ↑
│   │         │         │         │         │         │         │         │
│ Current   h15       h30       h45       h60       h75       h90      h105
│           │         │         │         │         │         │         │
│      Scalping   Quick    Standard   Hourly   Extended  Session  Trend
│                 Trades    Trades    Trades    Trades   Trades  Following
│                                                                          │
└─────────────────────────────────────────────────────────────┘

Granularity: 15-interval steps
Range: 15 to 105 intervals (1.75 hours to 10.5 hours on 6-min bars)
Coverage: Complete short to medium-term prediction spectrum
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

### 3. Why 7 Prediction Horizons?

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
│  SWING TRADING (h60, h75, h90, h105)                           │
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
    'h90': 0.3,   # Weak positive
    'h105': 0.2   # Very weak positive
}
# All positive → High agreement → Larger position (1.5x base)

predictions_mixed = {
    'h15': 0.8,
    'h30': 0.4,
    'h45': -0.1,  # Negative!
    'h60': 0.2,
    'h75': -0.3,  # Negative!
    'h90': -0.5,  # Strong negative!
    'h105': -0.6
}
# Mixed signals → Low agreement → Smaller position (0.4x base)
```

#### **Performance Optimization Per Horizon**

**Different horizons have different predictability:**

```
Expected Performance by Horizon:
┌──────────┬────────────┬──────────────────┬─────────────┐
│ Horizon  │ R² Score   │ Dir. Accuracy    │ Difficulty  │
├──────────┼────────────┼──────────────────┼─────────────┤
│ h15      │ 0.20-0.25  │ 54-56%          │ Hard        │
│ h30      │ 0.25-0.30  │ 55-57%          │ Medium      │
│ h45      │ 0.30-0.35  │ 56-58%          │ Medium      │
│ h60      │ 0.33-0.38  │ 57-59%          │ Easier      │
│ h75      │ 0.35-0.40  │ 58-60%          │ Easier      │
│ h90      │ 0.37-0.42  │ 59-61%          │ Easier      │
│ h105     │ 0.38-0.43  │ 60-62%          │ Easiest     │
└──────────┴────────────┴──────────────────┴─────────────┘

Pattern: Longer horizons are EASIER to predict!
Why? More time for trends to establish and less noise impact
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

## 🎯 THE COMPLETE ARCHITECTURE

### System Organization

```
BQX ML V3 Architecture:
└── 28 Independent Currency Pair Systems
    ├── EURUSD System
    │   ├── Model h15 → Predicts BQX 15 intervals ahead
    │   ├── Model h30 → Predicts BQX 30 intervals ahead
    │   ├── Model h45 → Predicts BQX 45 intervals ahead
    │   ├── Model h60 → Predicts BQX 60 intervals ahead
    │   ├── Model h75 → Predicts BQX 75 intervals ahead
    │   ├── Model h90 → Predicts BQX 90 intervals ahead
    │   └── Model h105 → Predicts BQX 105 intervals ahead
    │
    ├── GBPUSD System (7 models)
    ├── USDJPY System (7 models)
    ├── ... (25 more pairs)
    └── CHFJPY System (7 models)

TOTAL: 28 systems × 7 models = 196 models
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

### Model Training Pipeline

```python
for pair in 28_currency_pairs:
    # 1. Load data for this pair ONLY
    data = load_pair_data(pair)  # Isolated data

    # 2. Engineer features
    features = engineer_features(data)

    # 3. For each horizon, train separate model
    for horizon in [15, 30, 45, 60, 75, 90, 105]:

        # Create target: BQX value at horizon
        target = LEAD(bqx_90, horizon)

        # Train model
        model = train_model(features, target)

        # Optimize for this specific horizon
        hyperparameters = optimize_for_horizon(horizon)
        model.set_params(**hyperparameters)

        # Evaluate
        performance = evaluate(model)

        # Save
        save_model(pair, horizon, model, performance)

    # Result: 7 models for this pair, all independent
```

---

## 📊 EXPECTED OUTCOMES

### Performance Targets

```
Per Model:
├── Directional Accuracy: 54-62% (depending on horizon)
├── R² Score: 0.20-0.43 (longer = better)
├── Sharpe Ratio: 1.2-1.8
└── Max Drawdown: < 15%

Per Pair System (7 models combined):
├── Directional Accuracy: 60-65% (consensus improves accuracy)
├── Signal Confidence: High (multiple horizon agreement)
├── Position Sizing: Optimized (based on horizon consensus)
└── Risk Management: Enhanced (horizon divergence = caution)

Overall System (28 pairs × 7 horizons):
├── Total Models: 196
├── Training Time: 3-4 hours (parallel)
├── Prediction Latency: < 50ms per model
├── Cost: $500-700/month (GCP)
└── Trading Coverage: Complete FX market
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

For Swing Traders (h60, h75, h90, h105):
├── Entry/exit timing: Trend following 60-105 intervals
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

**5. 196 Total Models → Manageable**
- Parallel training (3-4 hours)
- Independent deployment
- Clear performance attribution

---

## 🎯 CONCLUSION

**CONFIRMED AND RATIONALIZED:**

BQX ML V3's architecture of **28 independent currency pair systems**, each containing **7 horizon-specific models** that predict **future BQX momentum values**, represents an optimal balance of:

1. **Specialization** (independent per pair)
2. **Trading Relevance** (BQX momentum targets)
3. **Versatility** (multi-horizon predictions)
4. **Performance** (horizon-optimized models)
5. **Scalability** (manageable 196 total models)

This architecture directly addresses real trading needs while maintaining technical excellence and operational feasibility.

**Total: 28 systems × 7 horizons = 196 models**
**Purpose: Predict future BQX momentum at 7 trading-relevant horizons**
**Result: Complete FX market coverage for all trading styles**

---

*Architecture confirmed and rationalized: 2025-11-27*
*This is the definitive specification for BQX ML V3*
