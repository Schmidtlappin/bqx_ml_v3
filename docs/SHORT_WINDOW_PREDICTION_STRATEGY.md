# 📈 SHORT WINDOW PREDICTION STRATEGY FOR BQX ML V3

**Date**: 2025-11-27
**Status**: Revised Strategy
**Focus**: 15, 30, 45, 60 minute predictions

---

## 🎯 WHY SHORT WINDOWS?

The original 90-minute+ windows are too long for practical forex trading. Here's why shorter windows are critical:

### Market Dynamics
- **Forex markets move fast**: Major moves happen in minutes, not hours
- **Trading sessions matter**: London open, NY open, overlaps create volatility
- **News impacts**: Economic releases cause immediate moves (< 5 minutes)
- **Technical levels**: Support/resistance tested multiple times per hour

### Trading Reality
- **Position holding times**:
  - Scalpers: 1-15 minutes
  - Day traders: 15-60 minutes
  - Swing traders: 1-4 hours
  - Position traders: Days/weeks (not our focus)

- **Risk management**:
  - Stop losses: Usually 10-30 pips (happens in minutes)
  - Take profits: 20-50 pips (achievable within an hour)

---

## 📊 OPTIMAL WINDOW SELECTION

### Tier 1: Ultra-Short (Deploy First)
- **15-minute**: Most actionable for automated trading
- **30-minute**: Best balance of signal quality vs timeliness

### Tier 2: Short-Term (Deploy Second)
- **45-minute**: Good for trend confirmation
- **60-minute**: Hourly pivots and session changes

### Tier 3: Medium-Term (Batch Process)
- **90-minute**: Session overlap analysis
- **180-minute**: 3-hour trend blocks
- **360-minute**: 6-hour session blocks

### Tier 4: Long-Term (Batch Only)
- **720-minute**: Half-day trends
- **1440-minute**: Daily bias
- **2880-minute**: 2-day swing positions

---

## 🚀 REVISED DEPLOYMENT PLAN

### Phase 1: Critical Short Windows (Real-time Endpoints)
```python
CRITICAL_MODELS = [
    ('EUR_USD', 15),  # Highest volume pair, shortest window
    ('EUR_USD', 30),  # Most liquid, day trading window
    ('GBP_USD', 30),  # "Cable" - high volatility
    ('USD_JPY', 30),  # Asian session leader
    ('EUR_GBP', 30),  # Cross pair for triangulation
]
```
**Cost**: $342/month (5 endpoints)
**Latency**: <50ms required

### Phase 2: Extended Coverage (Batch Predictions)
```python
BATCH_MODELS = [
    # All pairs × [45, 60, 90, 180] windows
    # 28 pairs × 4 windows = 112 models
]
```
**Cost**: $50/month (hourly batch)
**Latency**: Not critical (batch processed)

### Phase 3: Long-term Bias (Daily Batch)
```python
DAILY_MODELS = [
    # All pairs × [360, 720, 1440, 2880] windows
    # 28 pairs × 4 windows = 112 models
]
```
**Cost**: $30/month (daily batch)
**Latency**: Not critical (daily update)

---

## 📈 EXPECTED PERFORMANCE

### Short Windows (15-30 min)
- **R² Score**: 0.25-0.35 (lower but acceptable)
- **Directional Accuracy**: 55-60% (more important metric)
- **Feature importance**: Recent momentum, volatility, session

### Medium Windows (45-90 min)
- **R² Score**: 0.35-0.45 (better trend capture)
- **Directional Accuracy**: 58-62%
- **Feature importance**: Moving averages, RSI, patterns

### Long Windows (180+ min)
- **R² Score**: 0.40-0.50 (strong trend signals)
- **Directional Accuracy**: 60-65%
- **Feature importance**: Long-term averages, support/resistance

---

## 🔧 TECHNICAL IMPLEMENTATION

### Feature Engineering by Window Size

#### 15-Minute Features
```python
# Ultra-short features
- Last 5 candles (5, 10, 15 min ago)
- 3-period moving average
- Immediate momentum (1-candle change)
- Current volatility (3-candle STD)
- Session flags (London open, NY open)
```

#### 30-Minute Features
```python
# Short-term features
- Last 10 candles (30 min history)
- 5 & 10 period moving averages
- 5-candle momentum
- 10-candle volatility
- Session overlaps
```

#### 45-60 Minute Features
```python
# Medium-term features
- Last 20 candles (1-2 hour history)
- 10, 20, 30 period moving averages
- RSI(14)
- Bollinger Bands
- MACD signals
```

---

## 💰 TRADING APPLICATION

### How Traders Will Use Predictions:

#### Scalping (15-min predictions)
```python
if prediction_15min > current_price + 5_pips:
    enter_long()
    set_stop_loss(5_pips)
    set_take_profit(10_pips)
```

#### Day Trading (30-min predictions)
```python
if prediction_30min > current_price + 10_pips:
    if prediction_15min > current_price:  # Confirmation
        enter_long()
        set_stop_loss(10_pips)
        set_take_profit(20_pips)
```

#### Swing Trading (60-min predictions)
```python
if all([
    prediction_60min > current_price + 20_pips,
    prediction_30min > current_price + 10_pips,
    prediction_15min > current_price
]):
    enter_long()
    set_stop_loss(20_pips)
    set_take_profit(40_pips)
```

---

## 📊 SUCCESS METRICS

### For Short Windows:
1. **Directional Accuracy > 55%** (more important than R²)
2. **Latency < 50ms** (critical for execution)
3. **Model refresh every 5 minutes** (stay current)
4. **Profit factor > 1.2** (in backtesting)

### Business Impact:
- **Scalpers**: 50-100 trades/day × 5 pips = 250-500 pips potential
- **Day traders**: 10-20 trades/day × 15 pips = 150-300 pips potential
- **Swing traders**: 2-5 trades/day × 30 pips = 60-150 pips potential

---

## 🚀 IMMEDIATE ACTIONS

1. **Deploy 15 & 30 minute models first** (highest value)
2. **Test with live market data** (paper trading)
3. **Monitor directional accuracy** (not just R²)
4. **Optimize for speed** (every millisecond counts)
5. **Add session-specific features** (London, NY, Tokyo)

---

## 📝 KEY INSIGHT

**The forex market doesn't care about 90-minute or 3-hour predictions. Traders need to know what happens in the NEXT 15-30 minutes to make profitable decisions.**

By focusing on short windows, we align BQX ML V3 with actual trading behavior and create immediate value for users.

---

*This revised strategy prioritizes practical trading applications over theoretical model performance.*