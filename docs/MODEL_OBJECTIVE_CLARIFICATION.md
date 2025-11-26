# Model Objective Clarification - INTERVAL-CENTRIC Precision

## Critical Restatement of Model Objective

### ❌ Previous (Imprecise) Statement:
> "Models predict future BQX values"

### ✅ Corrected (Precise) Statement:
> **"Models predict BQX values at specific future intervals"**

---

## 🎯 Why This Distinction Matters

### 1. **INTERVAL-CENTRIC Architecture**
- All calculations use `ROWS BETWEEN` (intervals), never time-based windows
- Features are computed over specific interval counts (45i, 90i, 180i, etc.)
- Predictions target specific interval horizons, not time periods

### 2. **Precision in Prediction Targets**
```sql
-- We're NOT predicting:
"BQX value 90 minutes from now"  -- Time-based ❌

-- We ARE predicting:
"BQX value at interval N+90"     -- Interval-based ✅
```

### 3. **Market Gap Handling**
- Intervals are continuous regardless of market closures
- Weekend/holiday gaps don't affect interval counting
- Predictions maintain consistency across all market conditions

---

## 📊 Restated Model Objectives by Horizon

| Horizon | Previous Statement | Corrected Statement |
|---------|-------------------|-------------------|
| Short-term | "Predict BQX 45 minutes ahead" | **"Predict BQX at interval N+45"** |
| Medium-term | "Predict BQX 90 minutes ahead" | **"Predict BQX at interval N+90"** |
| Long-term | "Predict BQX 24 hours ahead" | **"Predict BQX at interval N+1440"** |

---

## 🔄 Updated Mathematical Formulation

### Previous (Time-based thinking):
```python
prediction = f(features_at_time_t) → bqx_at_time_t+Δt
```

### Corrected (Interval-based reality):
```python
prediction = f(features_at_interval_N) → bqx_at_interval_N+H

Where:
- N = current interval index
- H = horizon in intervals (45, 90, 180, 360, 720, 1440, 2880)
- No time component involved
```

---

## 📝 Implementation Implications

### 1. **Feature Engineering**
```sql
-- All features use interval-based windows
bqx_45w = idx_mid - AVG(idx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 1 FOLLOWING AND 45 FOLLOWING  -- 45 intervals, not minutes
)
```

### 2. **Model Training**
```python
# Target variable creation
y_train = LEAD(bqx_mid, 90)  # BQX at interval N+90, not "90 minutes later"
```

### 3. **Prediction Serving**
```python
def predict_bqx(current_interval_N, horizon_H):
    """
    Predict BQX value at interval N+H

    Args:
        current_interval_N: Current interval index
        horizon_H: Number of intervals ahead (45, 90, 180, etc.)

    Returns:
        Predicted BQX value at interval N+H
    """
    features = compute_interval_features(current_interval_N)
    prediction = model.predict(features, horizon=horizon_H)
    return prediction
```

---

## 🎯 Updated Project Mission Statement

### Original:
> "BQX ML V3 predicts future BQX values for 28 currency pairs"

### Restated with INTERVAL-CENTRIC Precision:
> **"BQX ML V3 predicts BQX values at specific future intervals (45i, 90i, 180i, 360i, 720i, 1440i, 2880i) for 28 currency pairs using an INTERVAL-CENTRIC architecture where all calculations are based on interval counts, not time periods"**

---

## ✅ Key Takeaways

1. **Models predict at specific interval offsets**, not time-based future points
2. **All horizons are measured in intervals** (45i, 90i, etc.), not minutes or hours
3. **INTERVAL-CENTRIC consistency** throughout the entire pipeline
4. **Market gaps don't affect predictions** because intervals are continuous
5. **Precision in terminology** prevents confusion and ensures correct implementation

---

## 📊 Practical Example

Given current interval N = 1000:
- Model predicts BQX at interval 1045 (N+45)
- Model predicts BQX at interval 1090 (N+90)
- Model predicts BQX at interval 1180 (N+180)

These are **specific interval indices**, not time-based projections.

---

*This clarification ensures that all stakeholders understand the precise, INTERVAL-CENTRIC nature of the BQX ML V3 prediction objectives.*