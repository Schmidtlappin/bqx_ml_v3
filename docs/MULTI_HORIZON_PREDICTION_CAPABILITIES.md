# MULTI-HORIZON PREDICTION CAPABILITIES

## 15-Interval Increments: From 15 Minutes to 105 Minutes

**Key Achievement**: Models predict accurately up to 105 intervals (1hr 45min) ahead
**Model Count**: 28 pairs x 7 horizons = 196 total models
**Architecture**: Each pair has 7 dedicated models for different prediction horizons

---

## Seven Prediction Horizons (CORRECT VALUES)

### Horizon Configuration
```
PREDICTION HORIZONS = [15, 30, 45, 60, 75, 90, 105] intervals forward
Models = 28 pairs x 7 horizons = 196 total models
```

### CRITICAL DISTINCTION
| Type | Values | Purpose |
|------|--------|---------|
| **Prediction Horizons** | [15, 30, 45, 60, 75, 90, 105] | How far into the FUTURE we predict (intervals forward) |
| **BQX Lookback Windows** | [45, 90, 180, 360, 720, 1440, 2880] | Used to CALCULATE bqx_* values (backward-looking) |

**DO NOT CONFUSE THESE TWO CONCEPTS**

### Horizon Breakdown

| Horizon | Intervals | Time | Trading Style | Status |
|---------|-----------|------|---------------|--------|
| H1 | 15 | 15 min | Scalping | Validated |
| H2 | 30 | 30 min | Quick Trade | Validated |
| H3 | 45 | 45 min | Short Trade | Validated |
| H4 | 60 | 1 hour | Intraday | Validated |
| H5 | 75 | 1hr 15min | Medium Trade | Testing |
| H6 | 90 | 1hr 30min | Session Trade | Testing |
| H7 | 105 | 1hr 45min | Position Entry | Testing |

---

## Implementation Architecture

### Target Definition (LEAD Operations)
Each model predicts the bqx_* value N intervals into the future:

```sql
-- For horizon H1 (15 intervals forward):
target_h15 = LEAD(bqx_45, 15) OVER (ORDER BY interval_time)

-- For horizon H2 (30 intervals forward):
target_h30 = LEAD(bqx_45, 30) OVER (ORDER BY interval_time)

-- For horizon H3 (45 intervals forward):
target_h45 = LEAD(bqx_45, 45) OVER (ORDER BY interval_time)

-- And so on for 60, 75, 90, 105...
```

### Per-Horizon Model Structure
```python
# CORRECT prediction horizons
PREDICTION_HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# BQX lookback windows (for feature calculation, NOT prediction)
BQX_LOOKBACK_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

for horizon in PREDICTION_HORIZONS:
    for pair in currency_pairs:
        model = XGBRegressor()
        # Target: bqx value N intervals into the future
        target = f"bqx_45_lead_{horizon}"
        # Features: historical data using BQX lookback windows
        features = idx_features + bqx_features + lag_features
        model.fit(features, target)
        models[f"{pair}_h{horizon}"] = model
```

---

## Feature vs Target Distinction

### Features (BACKWARD-LOOKING)
Features use historical data with LAG operations:
- `bqx_45_lag_1`: bqx_45 value 1 interval ago
- `bqx_45_lag_5`: bqx_45 value 5 intervals ago
- `close_lag_10`: close price 10 intervals ago
- Uses BQX lookback windows [45, 90, 180, 360, 720, 1440, 2880] to calculate bqx_* values

### Targets (FORWARD-LOOKING)
Targets use future data with LEAD operations:
- `target_h15`: bqx_45 value 15 intervals into the future
- `target_h30`: bqx_45 value 30 intervals into the future
- Uses prediction horizons [15, 30, 45, 60, 75, 90, 105]

---

## Trading Applications

### H1 (15 intervals = 15 min)
- **Use Case**: Scalping, quick momentum trades
- **Confidence**: Highest (shortest prediction window)
- **Execution**: Automated only

### H2 (30 intervals = 30 min)
- **Use Case**: Quick intraday trades
- **Confidence**: Very High
- **Execution**: Semi-automated

### H3 (45 intervals = 45 min)
- **Use Case**: Short-term directional trades
- **Confidence**: High
- **Execution**: Automated with alerts

### H4 (60 intervals = 1 hour)
- **Use Case**: Hourly trend capture
- **Confidence**: High
- **Execution**: Manual with model guidance

### H5 (75 intervals = 1hr 15min)
- **Use Case**: Extended momentum plays
- **Confidence**: Good
- **Execution**: Strategic entries

### H6 (90 intervals = 1hr 30min)
- **Use Case**: Session-based trading
- **Confidence**: Good
- **Execution**: Position building

### H7 (105 intervals = 1hr 45min)
- **Use Case**: Trend confirmation
- **Confidence**: Moderate
- **Execution**: Position entry/exit planning

---

## Model Count Verification

| Component | Count |
|-----------|-------|
| Currency Pairs | 28 |
| Prediction Horizons | 7 |
| **Total Models** | **196** |

Calculation: 28 pairs x 7 horizons = 196 independent models

---

## Why 15-Interval Increments

The 15-interval horizon structure provides:
1. **Consistent Spacing**: Equal 15-interval gaps between horizons
2. **Practical Trading Windows**: From scalping (15min) to position trading (1hr 45min)
3. **Manageable Model Count**: 7 horizons per pair is computationally efficient
4. **Forecast Degradation Curve**: Performance declines gracefully with horizon length

---

## IMPORTANT NOTES

### What [45, 90, 180, 360, 720, 1440, 2880] ARE:
These are **BQX CALCULATION LOOKBACK WINDOWS** used to compute:
- `bqx_45`: % change over 45 intervals (45 min lookback)
- `bqx_90`: % change over 90 intervals (90 min lookback)
- `bqx_180`: % change over 180 intervals (3 hour lookback)
- `bqx_360`: % change over 360 intervals (6 hour lookback)
- `bqx_720`: % change over 720 intervals (12 hour lookback)
- `bqx_1440`: % change over 1440 intervals (24 hour lookback)
- `bqx_2880`: % change over 2880 intervals (48 hour lookback)

### What [45, 90, 180, 360, 720, 1440, 2880] ARE NOT:
These are **NOT prediction horizons**. Do not confuse lookback calculation windows with forward prediction horizons.

### The Correct Prediction Horizons:
`[15, 30, 45, 60, 75, 90, 105]` - 7 horizons at 15-interval increments

---

*Documentation corrected: 2025-11-28*
*Previous version incorrectly stated prediction horizons as [45, 90, 180, 360, 720, 1440, 2880]*
