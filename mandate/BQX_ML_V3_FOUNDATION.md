# BQX ML V3 Foundation Document

## System Overview & Trading Strategy

**Document Version**: 1.0.0
**Created**: 2025-11-29
**Author**: BQXML Chief Engineer
**Classification**: MANDATE - Foundational Reference

---

## EXECUTIVE SUMMARY

BQX ML V3 is a machine learning system designed to predict future values of BQX momentum indicators across 28 forex currency pairs. The system's predictions directly inform a **game-theoretic contrarian trading strategy** where:

- **Positive predicted BQX** → SHORT position (sell)
- **Negative predicted BQX** → LONG position (buy)
- **Position size** scales proportionally with predicted BQX magnitude
- **Near-zero predicted BQX** → No trade (chaos zone)

The strategy exploits the predictable behavior of momentum traders by anticipating their forced exits and providing counter-liquidity at favorable prices.

---

## PART I: THE BQX PARADIGM

### 1.1 What is BQX?

BQX (pronounced "box") is a **normalized momentum indicator** calculated over rolling windows of price data. It measures the directional strength of price movement on a standardized scale.

```
BQX CALCULATION:

BQX_window = f(price momentum over N intervals)

Where:
├── Window sizes: [45, 90, 180, 360, 720, 1440, 2880] intervals
├── Each interval = 1 minute of price data
├── Output: Normalized value oscillating around zero
└── Units: Standard deviations from mean (σ)
```

### 1.2 BQX Oscillation Behavior

**Critical Property**: BQX values oscillate around zero and exhibit mean-reversion.

```
BQX DISTRIBUTION (Approximate):

     ←───────── NEGATIVE ─────────→│←───────── POSITIVE ─────────→
                                   │
  -3σ    -2σ    -1σ     0     +1σ    +2σ    +3σ
   │      │      │      │      │      │      │
   ▂      ▃      ▆      █      ▆      ▃      ▂
   │      │      │      │      │      │      │
  ~0.1%  ~2%   ~14%   ~68%   ~14%   ~2%   ~0.1%
         │             │             │
      EXTREME       NORMAL       EXTREME
      (rare)       (common)      (rare)
```

**Why BQX Oscillates**:
1. Price trends eventually exhaust (no trend is infinite)
2. Momentum traders take profits, reversing pressure
3. Mean-reversion forces push BQX back toward zero
4. This creates predictable cycles of extension and reversion

### 1.3 The Seven BQX Windows

| Window | Intervals | Time Equivalent | Characteristic |
|--------|-----------|-----------------|----------------|
| bqx_45 | 45 | ~45 minutes | Ultra-short momentum |
| bqx_90 | 90 | ~1.5 hours | Short-term momentum |
| bqx_180 | 180 | ~3 hours | Intraday momentum |
| bqx_360 | 360 | ~6 hours | Session momentum |
| bqx_720 | 720 | ~12 hours | Half-day momentum |
| bqx_1440 | 1440 | ~24 hours | Daily momentum |
| bqx_2880 | 2880 | ~48 hours | Multi-day momentum |

Each window captures momentum at different timescales, allowing the model to detect both short-term noise and long-term trends.

---

## PART II: THE PREDICTION SYSTEM

### 2.1 Model Architecture

```
BQX ML V3 ARCHITECTURE:

28 Currency Pairs × 7 Prediction Horizons = 196 Independent Models

Each model:
├── Input: 100-350 features (historical BQX, price, volatility, regime)
├── Algorithm: XGBoost (primary), ensemble with RF/LSTM
├── Output: Predicted BQX value at horizon H intervals forward
└── Targets: LEAD(bqx_*, H) where H ∈ [15, 30, 45, 60, 75, 90, 105]
```

### 2.2 Prediction Horizons

| Horizon | Intervals Forward | Time Equivalent | Trading Style |
|---------|-------------------|-----------------|---------------|
| h15 | 15 | ~15 minutes | Scalping |
| h30 | 30 | ~30 minutes | Day trading |
| h45 | 45 | ~45 minutes | Day trading |
| h60 | 60 | ~1 hour | Swing trading |
| h75 | 75 | ~1.25 hours | Swing trading |
| h90 | 90 | ~1.5 hours | Position trading |
| h105 | 105 | ~1.75 hours | Position trading |

### 2.3 The Dual Prediction Outputs

Every prediction generates TWO pieces of information:

```
PREDICTION OUTPUT:

1. DIRECTION (Sign of predicted BQX)
   ├── Positive (+) → Future momentum is upward (price rising)
   ├── Negative (-) → Future momentum is downward (price falling)
   └── Determines: LONG or SHORT decision

2. MAGNITUDE (Absolute value of predicted BQX)
   ├── |BQX| > 2σ → Extreme momentum expected
   ├── 1σ < |BQX| < 2σ → Moderate momentum expected
   ├── 0.5σ < |BQX| < 1σ → Weak momentum expected
   ├── |BQX| < 0.5σ → Chaos zone (no clear direction)
   └── Determines: Position SIZE
```

---

## PART III: THE GAME THEORY TRADING STRATEGY

### 3.1 Core Trading Logic

```
THE FUNDAMENTAL RULE:

Predicted BQX > 0 (positive momentum) → SELL (SHORT)
Predicted BQX < 0 (negative momentum) → BUY (LONG)
Predicted |BQX| < 0.5σ → NO TRADE (chaos zone)

Position Size = f(|Predicted BQX|)
```

**Why Contrarian?**

This is NOT simple mean-reversion. It is **game-theoretic exploitation** of predictable market participant behavior.

### 3.2 The Game-Theoretic Framework

```
MARKET PLAYER TYPES:

1. MOMENTUM TRADERS (60-70% of volume)
   ├── Strategy: Buy rising prices, sell falling prices
   ├── Behavior: Chase trends, amplify moves
   ├── Weakness: Predictable entry/exit points
   ├── BQX Signal: Their activity CREATES positive/negative BQX
   └── Vulnerability: Must eventually exit (profit-taking, stops, margin)

2. MEAN-REVERSION TRADERS (YOU - 10-15% of volume)
   ├── Strategy: Sell into strength, buy into weakness
   ├── Behavior: Fade extremes, provide liquidity
   ├── Edge: Act BEFORE momentum exhaustion
   ├── BQX Signal: Predicts WHEN momentum traders will exit
   └── Advantage: Provide liquidity at favorable prices

3. FUNDAMENTAL TRADERS (20-25% of volume)
   ├── Strategy: Trade on macro/news events
   ├── Behavior: Create regime shifts
   ├── BQX Signal: Regime features detect their entry
   └── Risk: Can invalidate technical signals
```

### 3.3 The Nash Equilibrium Insight

**Why does BQX always revert toward zero?**

```
EQUILIBRIUM DYNAMICS:

SCENARIO A: BQX >> 0 (Strong Positive Momentum)
├── Momentum traders: FULLY INVESTED (buying exhausted)
├── No new buyers left to continue the trend
├── Position unwinding begins (profit-taking, stops)
├── Mean-reversion traders: SELLING (providing exit liquidity)
├── Price pressure: Shifts downward
└── RESULT: BQX reverts toward zero

SCENARIO B: BQX << 0 (Strong Negative Momentum)
├── Momentum traders: FULLY SHORT (selling exhausted)
├── No new sellers left to continue the trend
├── Short covering begins (profit-taking, stops)
├── Mean-reversion traders: BUYING (providing cover liquidity)
├── Price pressure: Shifts upward
└── RESULT: BQX reverts toward zero
```

**The Edge**: Momentum traders MUST exit eventually. BQX magnitude tells you how "stretched" their positions are. The model predicts WHEN exhaustion occurs.

### 3.4 The Chaos Zone

```
CHAOS ZONE DEFINITION:

|Predicted BQX| < 0.5σ

Characteristics:
├── Momentum traders: No clear direction
├── Order flow: Balanced (buyers ≈ sellers)
├── Market state: Random walk / noise
├── Predictability: LOW
├── Edge: NONE
└── Action: DO NOT TRADE

WHY NO TRADE IN CHAOS:
├── No dominant player type to exploit
├── Direction prediction accuracy drops below 85%
├── Transaction costs exceed expected edge
├── Expected value: Negative (guaranteed loss over time)
└── Capital preservation is priority
```

### 3.5 The Complete Trading Spectrum

```
BQX = -3σ ────────────────────────────────────────────── BQX = +3σ
   │                                                           │
   │  LONG 3    LONG 2    LONG 1    FLAT    SHORT 1    SHORT 2    SHORT 3
   │    ↑         ↑         ↑        ↑         ↑          ↑          ↑
   │    │         │         │        │         │          │          │
   │  STRONG    CLEAR     WEAK    CHAOS     WEAK      CLEAR      STRONG
   │  SIGNAL    SIGNAL   SIGNAL    ZONE    SIGNAL    SIGNAL     SIGNAL
   │                              (NO TRADE)
   │
   └── Position size scales linearly with |BQX|
```

### 3.6 Proportional Position Sizing

**Core Principle**: Position size scales with predicted BQX magnitude.

| Predicted BQX | Position | Conviction |
|---------------|----------|------------|
| +3σ | SHORT 3 units | Maximum |
| +2σ | SHORT 2 units | High |
| +1σ | SHORT 1 unit | Moderate |
| +0.5σ to -0.5σ | FLAT | None (chaos zone) |
| -1σ | LONG 1 unit | Moderate |
| -2σ | LONG 2 units | High |
| -3σ | LONG 3 units | Maximum |

**Why Proportional Sizing is Optimal (Kelly Criterion)**:

```
KELLY CRITERION ALIGNMENT:

Optimal Bet Size = Edge Size / Odds

├── Larger |BQX| = More stretched momentum traders
├── More stretched = Higher reversal probability
├── Higher probability = Larger edge
├── Larger edge = Larger optimal bet size
└── Position size ∝ |BQX| achieves this automatically
```

---

## PART IV: DIRECTION & MAGNITUDE PREDICTION LOGIC

### 4.1 Why Direction Prediction is Foundation

```
DIRECTION DETERMINES TRADE SIDE:

Predicted BQX > 0 → You will SHORT (sell)
Predicted BQX < 0 → You will LONG (buy)

WRONG DIRECTION = WRONG SIDE OF TRADE
├── You SHORT when you should LONG
├── Or you LONG when you should SHORT
├── You are betting AGAINST the actual move
└── This is CATASTROPHIC for returns
```

**Direction Accuracy Requirements**:

| Predicted Zone | Accuracy Required | Rationale |
|----------------|-------------------|-----------|
| \|BQX\| > 2σ | **99%+** | MAX position, catastrophic if wrong |
| 1σ < \|BQX\| < 2σ | **95%+** | Large position, very costly if wrong |
| 0.5σ < \|BQX\| < 1σ | **85%+** | Small position, manageable if wrong |
| \|BQX\| < 0.5σ | N/A | No trade - chaos zone |

### 4.2 Why Magnitude Prediction is Position Sizing

```
MAGNITUDE DETERMINES POSITION SIZE:

Predicted |BQX| = 3σ → Position = 3 units
Predicted |BQX| = 2σ → Position = 2 units
Predicted |BQX| = 1σ → Position = 1 unit
Predicted |BQX| < 0.5σ → Position = 0 (no trade)

WRONG MAGNITUDE = WRONG POSITION SIZE
├── Overestimate magnitude → Position too large for actual edge
├── Underestimate magnitude → Position too small, missed opportunity
└── Overestimate is MORE DANGEROUS (amplified losses if wrong)
```

### 4.3 The Four Prediction Error Scenarios

```
SCENARIO MATRIX:

                        ACTUAL DIRECTION
                        Positive (+)    Negative (-)
PREDICTED       (+)     ✓ CORRECT       ✗ DISASTER
DIRECTION       (-)     ✗ DISASTER      ✓ CORRECT


                        ACTUAL MAGNITUDE
                        Large (>2σ)     Small (<1σ)
PREDICTED       Large   ✓ OPTIMAL       ✗ OVEREXPOSED
MAGNITUDE       Small   ✗ MISSED OPP    ✓ CORRECT
```

---

## PART V: RISK ANALYSIS - WRONG PREDICTIONS

### 5.1 Wrong Direction at Extreme (CATASTROPHIC)

```
EXAMPLE:

PREDICTION: BQX will be +2.5σ (positive extreme)
ACTION: SHORT 2.5 units (expecting mean-reversion DOWN)
REALITY: BQX becomes -2.5σ (negative extreme)

WHAT HAPPENED:
├── You SHORTED expecting price to fall
├── Price ROSE (BQX went more negative = upward momentum)
├── You are on the WRONG SIDE of a 5σ move
└── Position: -2.5 units × 5σ move = CATASTROPHIC LOSS

GAME THEORY FAILURE:
├── You predicted momentum exhaustion
├── Reality: Momentum ACCELERATED in opposite direction
├── Momentum traders profited FROM your liquidity
└── YOU became the "dumb money" they exploit
```

**Impact Quantification**:

| Error Type | Position Size | Move Against | Loss Magnitude |
|------------|---------------|--------------|----------------|
| Direction wrong at 3σ | 3 units | 6σ swing | **18σ equivalent** |
| Direction wrong at 2σ | 2 units | 4σ swing | **8σ equivalent** |
| Direction wrong at 1σ | 1 unit | 2σ swing | **2σ equivalent** |

### 5.2 Wrong Magnitude - Overestimate (Dangerous)

```
EXAMPLE:

PREDICTION: BQX will be +2.5σ (large positive)
ACTION: SHORT 2.5 units
REALITY: BQX becomes +0.8σ (small positive)

WHAT HAPPENED:
├── Direction CORRECT (positive → short was right idea)
├── But magnitude was 3x SMALLER than predicted
├── Position was 3x TOO LARGE for actual edge
├── Small profit, but RISK was disproportionate

KELLY CRITERION VIOLATION:
├── Optimal bet = f(edge size)
├── Actual edge = small (0.8σ)
├── Your bet = large (2.5 units)
└── Overbet → Suboptimal risk-adjusted returns
```

### 5.3 Wrong Magnitude - Underestimate (Acceptable)

```
EXAMPLE:

PREDICTION: BQX will be +0.8σ (small positive)
ACTION: SHORT 0.8 units (or skip if below threshold)
REALITY: BQX becomes +2.5σ (large positive extreme)

WHAT HAPPENED:
├── Direction CORRECT (if you traded)
├── You captured only 1/3 of the opportunity
├── Or you SKIPPED entirely (if below threshold)
├── Left money on the table

OPPORTUNITY COST:
├── Optimal profit: 2.5 units × 2.5σ = 6.25σ
├── Actual profit: 0.8 units × 2.5σ = 2.0σ
├── Missed: 4.25σ (68% of available profit)
└── NOT A LOSS - just suboptimal
```

**Key Insight**: Underestimating magnitude is LESS DANGEROUS than overestimating. Better to undersize than oversize.

### 5.4 The Risk Hierarchy

```
RISK PRIORITY (HIGHEST TO LOWEST):

1. WRONG DIRECTION AT EXTREME (|BQX| > 2σ)
   ├── Impact: 8-18σ equivalent loss
   ├── Frequency target: <1%
   └── This DESTROYS accounts

2. WRONG DIRECTION AT MODERATE (1σ < |BQX| < 2σ)
   ├── Impact: 2-8σ equivalent loss
   ├── Frequency target: <5%
   └── This causes significant drawdowns

3. MAGNITUDE OVERESTIMATE
   ├── Impact: Disproportionate risk
   ├── Frequency target: <20%
   └── Managed via conservative sizing

4. MAGNITUDE UNDERESTIMATE
   ├── Impact: Missed opportunity only
   ├── Frequency: Acceptable
   └── No capital risk

5. CHAOS ZONE VIOLATION
   ├── Impact: Transaction cost bleed
   ├── Frequency target: 0%
   └── Hard rule enforcement
```

### 5.5 Game Theory Risk Inversion

```
WHEN PREDICTIONS ARE WRONG, THE GAME INVERTS:

NORMAL GAME (predictions correct):
├── You: Mean-reversion trader (smart money)
├── Them: Momentum traders (predictable)
├── Edge: You fade their exhaustion
└── Result: You profit from their forced exits

INVERTED GAME (predictions wrong):
├── You: Predictable contrarian (dumb money)
├── Them: Trend followers (right this time)
├── Edge: They profit from YOUR forced exit
└── Result: They exploit your stop-losses

THE INVERSION IS ASYMMETRIC:
├── When you're right: You capture 1-3σ on controlled position
├── When you're wrong: You lose 2-6σ on aggressive position
└── REQUIRES 95%+ accuracy to overcome asymmetry
```

---

## PART VI: PERFORMANCE EXPECTATIONS

### 6.1 Accuracy → Profitability Math

```
PROFITABILITY MODEL:

Assumptions:
├── Average winning trade: +2σ (mean-reversion capture)
├── Average losing trade: -3σ (trend continuation against you)
├── Position sizing: Proportional to |BQX|
└── Trading only when |BQX| > 0.5σ

WITH 95% DIRECTION ACCURACY (|BQX| > 1σ):
├── Wins: 95% × +2σ = +1.9σ expected
├── Losses: 5% × -3σ = -0.15σ expected
├── Net: +1.75σ per trade (highly profitable)

WITH 90% DIRECTION ACCURACY:
├── Wins: 90% × +2σ = +1.8σ expected
├── Losses: 10% × -3σ = -0.3σ expected
├── Net: +1.5σ per trade (profitable, but 15% less)

WITH 80% DIRECTION ACCURACY:
├── Wins: 80% × +2σ = +1.6σ expected
├── Losses: 20% × -3σ = -0.6σ expected
├── Net: +1.0σ per trade (marginal)

WITH 70% DIRECTION ACCURACY:
├── Wins: 70% × +2σ = +1.4σ expected
├── Losses: 30% × -3σ = -0.9σ expected
├── Net: +0.5σ per trade (barely positive)

BELOW 65% ACCURACY: UNPROFITABLE
```

### 6.2 The 95% Threshold Rationale

```
WHY 95% IS THE TARGET (NOT 90% OR 99%):

90% accuracy:
├── Sounds good, but...
├── 10% wrong = 1 in 10 trades loses 3σ
├── On large positions, this compounds
└── Drawdowns become uncomfortable

95% accuracy:
├── 5% wrong = 1 in 20 trades loses 3σ
├── Manageable drawdowns
├── Strong positive expectancy
└── Sustainable for production

99% accuracy:
├── Ideal, but...
├── May require rejecting too many trades
├── Opportunity cost of being too conservative
└── Diminishing returns above 95%

SWEET SPOT: 95% direction accuracy for |BQX| > 1σ
```

### 6.3 Model Performance Targets

**TIER 1: DIRECTION ACCURACY (Critical Foundation)**

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Direction Accuracy (\|BQX\| > 2σ) | **≥ 99%** | % correct positive/negative during extremes |
| Direction Accuracy (\|BQX\| > 1σ) | **≥ 95%** | % correct during strong moves |
| Direction Accuracy (0.5σ-1σ) | ≥ 85% | % correct during moderate moves |
| Direction Accuracy (< 0.5σ) | N/A | Chaos zone - no trading signal |

**TIER 2: EXTREME PREDICTION (Alpha Generator)**

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Extreme Recall | ≥ 70% | % of actual extremes correctly predicted |
| Extreme Precision | ≥ 60% | % of predicted extremes that are actual |
| Extreme F1 | ≥ 0.65 | Harmonic mean of recall/precision |
| Tail R² | ≥ 0.40 | R² calculated only on extreme intervals |

**SECONDARY METRICS**

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Overall R² | ≥ 0.50 | Standard regression metric |
| Overall Direction Accuracy | ≥ 75% | Across all intervals |

---

## PART VII: FEATURE REQUIREMENTS

### 7.1 Feature Types for Game Theory Success

| Feature Type | Game Theory Value | Examples |
|--------------|-------------------|----------|
| **LAG** | Historical BQX patterns | bqx_lag_1 to bqx_lag_2880 |
| **MOMENTUM** | How fast momentum traders are moving | mom_acceleration_*, mom_velocity_* |
| **VOLATILITY** | How stretched the "rubber band" is | vol_atr_*, vol_range_* |
| **REGIME** | What game is being played | regime_trending, regime_ranging |
| **CORRELATION** | If momentum traders are crowded | corr_cross_pair_*, corr_bqx_* |
| **COVARIANCE** | Cross-pair relationships | cov_eurusd_gbpusd_* |

### 7.2 Feature Selection for Trading Strategy

Feature selection must prioritize features that predict:

1. **Direction** (30% weight): Features that distinguish positive vs negative future BQX
2. **Extremes** (40% weight): Features important during |BQX| > 2σ
3. **Regime** (15% weight): Features for HIGH_VOL, STRONG_UP/DOWN periods
4. **Overall** (10% weight): Standard correlation/importance
5. **Tail-risk** (5% weight): Mandatory safety features

---

## PART VIII: OPERATIONAL RULES

### 8.1 Hard Trading Rules

```
RULE 1: CHAOS ZONE
├── If |Predicted BQX| < 0.5σ → NO TRADE
├── No exceptions
└── Violation = guaranteed negative EV

RULE 2: POSITION SIZING
├── Position = floor(|Predicted BQX| / 1σ) units
├── Maximum = 3 units per pair
└── Scale in, not all at once

RULE 3: DIRECTION CONFIDENCE
├── Only trade if model confidence ≥ 85%
├── For extremes (|BQX| > 2σ), require ≥ 95%
└── Reject low-confidence predictions

RULE 4: MULTI-HORIZON CONFIRMATION
├── Prefer trades where multiple horizons agree
├── Short-term and long-term alignment = stronger signal
└── Conflicting horizons = reduce position or skip
```

### 8.2 Risk Management Rules

```
RULE 5: STOP LOSSES
├── Hard stop at 2σ adverse move
├── Trailing stop as profit develops
└── Never move stop against position

RULE 6: MAXIMUM EXPOSURE
├── Maximum 30% of capital at risk at any time
├── Diversify across pairs
└── Reduce exposure during high correlation periods

RULE 7: REGIME AWARENESS
├── Reduce size during unclear regimes
├── Increase size during clear trending/mean-reversion regimes
└── Exit all positions if regime shift detected
```

---

## PART IX: SUCCESS CRITERIA SUMMARY

### 9.1 Model Success

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| Direction Accuracy (>1σ) | 90% | **95%** | 98% |
| Direction Accuracy (>2σ) | 95% | **99%** | 99.5% |
| Extreme Recall | 60% | **70%** | 80% |
| Extreme Precision | 50% | **60%** | 70% |

### 9.2 Trading Success

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| Win Rate | 55% | **65%** | 75% |
| Profit Factor | 1.3 | **1.8** | 2.5 |
| Sharpe Ratio | 1.0 | **1.5** | 2.0 |
| Max Drawdown | -25% | **-15%** | -10% |

### 9.3 Operational Success

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| Prediction Latency | <5 sec | **<1 sec** | <0.5 sec |
| Model Uptime | 95% | **99%** | 99.9% |
| Feature Freshness | <5 min | **<1 min** | Real-time |

---

## APPENDIX A: GLOSSARY

| Term | Definition |
|------|------------|
| **BQX** | Normalized momentum indicator oscillating around zero |
| **Chaos Zone** | Region where \|BQX\| < 0.5σ, indicating no clear direction |
| **Direction** | Sign of BQX (positive or negative) |
| **Magnitude** | Absolute value of BQX (\|BQX\|) |
| **Mean-Reversion** | Tendency of BQX to return toward zero from extremes |
| **Momentum Traders** | Market participants who buy rising prices and sell falling prices |
| **Horizon** | Number of intervals into the future being predicted |
| **Interval** | One minute of price data (1-minute bar) |
| **σ (Sigma)** | Standard deviation, used as unit of BQX magnitude |

---

## APPENDIX B: DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-29 | CE | Initial creation |

---

**END OF DOCUMENT**
