# BQX TARGET FORMULA MANDATE

**Date**: 2025-12-09
**Status**: AUTHORITATIVE - USER MANDATED
**Classification**: CRITICAL - Training Pipeline Foundation

---

## 1. MANDATE STATEMENT

All target data for BQX ML V3 model training MUST be derived from BQX values calculated using the canonical BQX formula. This mandate establishes the definitive formulas for both BQX features and prediction targets.

---

## 2. BQX FEATURE CALCULATION (Backward-Looking Momentum)

### 2.1 Canonical Formula

```sql
bqx_{window} = ((close[T] - close[T-window]) / close[T-window]) * 100
```

### 2.2 SQL Implementation

```sql
bqx_45 = ((close_idx - LAG(close_idx, 45) OVER (ORDER BY interval_time)) /
          NULLIF(LAG(close_idx, 45) OVER (ORDER BY interval_time), 0)) * 100
```

### 2.3 Interpretation

| Component | Meaning |
|-----------|---------|
| `close[T]` | Current close price at time T |
| `close[T-window]` | Close price `window` intervals ago |
| `* 100` | Convert to percentage |
| Result | Percentage price change over lookback period |

### 2.4 BQX Windows (Lookback Periods)

Seven standardized lookback windows:
- `bqx_45` - 45 intervals (~45 minutes)
- `bqx_90` - 90 intervals (~1.5 hours)
- `bqx_180` - 180 intervals (~3 hours)
- `bqx_360` - 360 intervals (~6 hours)
- `bqx_720` - 720 intervals (~12 hours)
- `bqx_1440` - 1440 intervals (~1 day)
- `bqx_2880` - 2880 intervals (~2 days)

### 2.5 Verified Data Characteristics

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| AVG | ~0.0001 | Oscillates around zero |
| MIN | -1.63 | Maximum negative momentum |
| MAX | +2.04 | Maximum positive momentum |
| STDDEV | 0.087 | Typical momentum range |

**CRITICAL**: BQX values MUST oscillate around zero. Values around 100 indicate incorrect calculation (likely using indexed prices instead of percentage change).

---

## 3. TARGET CALCULATION (Forward-Looking Prediction)

### 3.1 Canonical Formula

```sql
target_bqx{window}_h{horizon} = LEAD(bqx_{window}, horizon)
```

### 3.2 SQL Implementation

```sql
-- Target for bqx_45 at horizon h15 (15 intervals ahead)
target_bqx45_h15 = LEAD(bqx_45, 15) OVER (ORDER BY interval_time)

-- Target for bqx_45 at horizon h30 (30 intervals ahead)
target_bqx45_h30 = LEAD(bqx_45, 30) OVER (ORDER BY interval_time)

-- Continue for all horizon/window combinations...
```

### 3.3 Interpretation

| Component | Meaning |
|-----------|---------|
| `bqx_{window}` | The BQX momentum indicator for a specific lookback window |
| `horizon` | How many intervals into the future we're predicting |
| `LEAD(..., horizon)` | The BQX value `horizon` intervals from now |
| Result | What the BQX momentum will be at the prediction horizon |

### 3.4 Prediction Horizons

Seven standardized prediction horizons:
- `h15` - 15 intervals ahead (~15 minutes)
- `h30` - 30 intervals ahead (~30 minutes)
- `h45` - 45 intervals ahead (~45 minutes)
- `h60` - 60 intervals ahead (~1 hour)
- `h75` - 75 intervals ahead (~1.25 hours)
- `h90` - 90 intervals ahead (~1.5 hours)
- `h105` - 105 intervals ahead (~1.75 hours)

---

## 4. CRITICAL DISTINCTION: Windows vs Horizons

### 4.1 BQX Windows (7 values)

**Purpose**: Define the lookback period for calculating momentum
**Question Answered**: "How much has price changed over the LAST N intervals?"
**Values**: 45, 90, 180, 360, 720, 1440, 2880

```
TIME ←───────────────── PAST ─────────────────────→ NOW
     │                                              │
     close[T-window]                            close[T]
     │                                              │
     └──────────── BQX LOOKBACK WINDOW ────────────┘
```

### 4.2 Prediction Horizons (7 values)

**Purpose**: Define how far ahead we're predicting
**Question Answered**: "What will the BQX value be N intervals FROM NOW?"
**Values**: 15, 30, 45, 60, 75, 90, 105

```
TIME  NOW ─────────────── FUTURE ───────────────────→
      │                                              │
      bqx_{window}[T]                      bqx_{window}[T+horizon]
      │                                              │
      └──────────── PREDICTION HORIZON ─────────────┘
```

### 4.3 Target Matrix Structure

The complete target matrix has 49 target columns (7 windows × 7 horizons):

| Target Column | Formula | Meaning |
|---------------|---------|---------|
| `target_bqx45_h15` | `LEAD(bqx_45, 15)` | bqx_45 value 15 intervals from now |
| `target_bqx45_h30` | `LEAD(bqx_45, 30)` | bqx_45 value 30 intervals from now |
| `target_bqx45_h45` | `LEAD(bqx_45, 45)` | bqx_45 value 45 intervals from now |
| `target_bqx45_h60` | `LEAD(bqx_45, 60)` | bqx_45 value 60 intervals from now |
| `target_bqx45_h75` | `LEAD(bqx_45, 75)` | bqx_45 value 75 intervals from now |
| `target_bqx45_h90` | `LEAD(bqx_45, 90)` | bqx_45 value 90 intervals from now |
| `target_bqx45_h105` | `LEAD(bqx_45, 105)` | bqx_45 value 105 intervals from now |
| `target_bqx90_h15` | `LEAD(bqx_90, 15)` | bqx_90 value 15 intervals from now |
| ... | ... | ... |
| `target_bqx2880_h105` | `LEAD(bqx_2880, 105)` | bqx_2880 value 105 intervals from now |

---

## 5. MODEL PREDICTION SEMANTICS

### 5.1 What the Model Predicts

The model predicts: **"What will the BQX momentum indicator show N intervals from now?"**

NOT:
- Raw price prediction
- Price direction (binary)
- Forward price change percentage

### 5.2 Why This Approach

1. **Scale Invariance**: BQX values are percentages, comparable across all pairs
2. **Stationarity**: BQX oscillates around zero (stationary series)
3. **Trading Relevance**: Momentum persistence is actionable for trading
4. **Autoregressive Power**: Historical BQX patterns predict future BQX

### 5.3 Deployment Strategy

For each currency pair:
1. Train models for ALL 7 horizons (h15, h30, h45, h60, h75, h90, h105)
2. Evaluate directional accuracy for each horizon
3. Deploy the FARTHEST horizon achieving ≥95% accuracy
4. Expected: Most pairs deploy h30-h60

---

## 6. VERIFICATION REQUIREMENTS

### 6.1 BQX Value Validation

```sql
-- BQX values MUST oscillate around zero
SELECT
    AVG(bqx_45) as avg,  -- Should be ~0
    STDDEV(bqx_45) as std  -- Should be ~0.08-0.10
FROM targets_table
WHERE bqx_45 IS NOT NULL
```

**FAIL CONDITION**: AVG near 100 indicates indexed prices, not BQX.

### 6.2 Target Formula Validation

```sql
-- Verify target = LEAD(bqx, horizon)
WITH verification AS (
    SELECT
        target_bqx45_h15,
        LEAD(bqx_45, 15) OVER (ORDER BY interval_time) as computed
    FROM targets_table
)
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN ABS(target_bqx45_h15 - computed) < 0.0000001 THEN 1 ELSE 0 END) as matching
FROM verification
WHERE target_bqx45_h15 IS NOT NULL AND computed IS NOT NULL
```

**PASS CONDITION**: 100% match (matching = total)

---

## 7. SQL TEMPLATE FOR TARGET TABLE CREATION

```sql
CREATE OR REPLACE TABLE `project.dataset.targets_{pair}` AS
WITH source AS (
    SELECT
        interval_time,
        pair,
        bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
    FROM `project.dataset.base_bqx_{pair}`
    WHERE bqx_45 IS NOT NULL
)
SELECT
    interval_time,
    pair,
    -- Base BQX values (features)
    bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,

    -- Targets for bqx_45 at all horizons
    LEAD(bqx_45, 15) OVER (ORDER BY interval_time) as target_bqx45_h15,
    LEAD(bqx_45, 30) OVER (ORDER BY interval_time) as target_bqx45_h30,
    LEAD(bqx_45, 45) OVER (ORDER BY interval_time) as target_bqx45_h45,
    LEAD(bqx_45, 60) OVER (ORDER BY interval_time) as target_bqx45_h60,
    LEAD(bqx_45, 75) OVER (ORDER BY interval_time) as target_bqx45_h75,
    LEAD(bqx_45, 90) OVER (ORDER BY interval_time) as target_bqx45_h90,
    LEAD(bqx_45, 105) OVER (ORDER BY interval_time) as target_bqx45_h105,

    -- Targets for bqx_90 at all horizons
    LEAD(bqx_90, 15) OVER (ORDER BY interval_time) as target_bqx90_h15,
    LEAD(bqx_90, 30) OVER (ORDER BY interval_time) as target_bqx90_h30,
    LEAD(bqx_90, 45) OVER (ORDER BY interval_time) as target_bqx90_h45,
    LEAD(bqx_90, 60) OVER (ORDER BY interval_time) as target_bqx90_h60,
    LEAD(bqx_90, 75) OVER (ORDER BY interval_time) as target_bqx90_h75,
    LEAD(bqx_90, 90) OVER (ORDER BY interval_time) as target_bqx90_h90,
    LEAD(bqx_90, 105) OVER (ORDER BY interval_time) as target_bqx90_h105,

    -- Continue for bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880...

FROM source
```

---

## 8. COMMON ERRORS TO AVOID

### 8.1 Wrong: Using Forward Price Change as Target

```sql
-- INCORRECT - This is NOT the target formula
target_45 = ((LEAD(close_idx, 45) - close_idx) / close_idx) * 100
```

This calculates a NEW percentage change, not the future BQX value.

### 8.2 Wrong: Conflating Window and Horizon

```sql
-- INCORRECT - Window and horizon should be independent
target_45 = LEAD(bqx_45, 45)  -- Always predicting 45 ahead for bqx_45
```

Correct approach: 7 horizons per BQX window.

### 8.3 Wrong: Using Indexed Prices

```sql
-- INCORRECT - BQX values around 100 indicate indexed prices
bqx_45 = close_idx  -- This is price, not momentum!
```

BQX MUST be percentage change, oscillating around zero.

---

## 9. MANDATE COMPLIANCE CHECKLIST

- [ ] BQX values oscillate around zero (AVG ≈ 0)
- [ ] BQX calculated using `((close[T] - close[T-window]) / close[T-window]) * 100`
- [ ] Targets calculated using `LEAD(bqx_{window}, horizon)`
- [ ] Target table has 49 target columns (7 windows × 7 horizons)
- [ ] 100% formula verification passes
- [ ] All 28 pairs follow identical formula

---

## 10. REFERENCES

- Architecture: `/mandate/BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md`
- Dual Features: `/mandate/IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md`
- Semantics: `/intelligence/semantics.json`
- Context: `/intelligence/context.json`

---

**MANDATE AUTHORITY**: User-specified, non-negotiable requirement for all BQX ML V3 training pipelines.

**VERIFICATION DATE**: 2025-12-09
**VERIFICATION RESULT**: targets_eurusd - 100% formula match (2,164,270 / 2,164,270 rows)
