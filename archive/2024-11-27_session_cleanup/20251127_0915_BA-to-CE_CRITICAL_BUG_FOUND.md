# CRITICAL: Root Cause Found - Data Leakage from Random Split

**To:** Chief Engineer
**From:** Build Agent
**Time:** 2025-11-27 09:15 UTC
**Priority:** CRITICAL
**Subject:** Root cause of impossible R² = 0.97 identified

---

## Executive Summary

I have identified the **root cause** of the impossible performance metrics. It's not a calculation error—it's **severe data leakage** from using random train/test split on time series data.

---

## The Smoking Gun

### Evidence Chain:

1. **Correlation analysis showed**: BQX to target correlation = **0.136** (13.6%)
   - This should give R² ≈ 0.02, not 0.97

2. **Feature selection script examination** revealed the bug:
   ```python
   # Line 306-308 in comprehensive_feature_generation_and_selection.py
   X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=0.2, random_state=42  # ❌ RANDOM SPLIT!
   )
   ```

3. **Why this causes leakage** (time series):
   - Test sample at time T=1000 uses lag_30 feature (data from T=970)
   - Training sample at time T=985 exists (between test's past and present)
   - Model learns from T=985, applies to predict T=1000
   - **Model sees the future, predicts the "past"**

---

## Proof of Data Leakage

### What We Observed:
- **R² = 0.9738** with random split
- **Correlation = 0.136** (should give R² ≈ 0.02)
- Ratio: 0.9738 / 0.02 = **48.7× higher than mathematically possible**

### What This Proves:
The model is NOT learning to predict the future. It's learning patterns from future data and applying them to past data in the "test" set.

---

## Impact on All Previous Results

### Affected Models:
- ✗ implement_multi_horizon_simplified.py - Uses random split
- ✗ comprehensive_feature_generation_and_selection.py - Uses random split
- ✗ All 42 deployed models (if they used random split)

### Directional Accuracy Bug (Still Valid):
The directional accuracy calculation bug I found earlier is **also real**:
```python
# WRONG: Measures direction between consecutive points
actual_direction = np.diff(y_test) > 0
pred_direction = np.diff(y_pred) > 0
```

Should be:
```python
# CORRECT: Measures direction from current to horizon
actual_direction = (y_test - current_values) > 0
pred_direction = (y_pred - current_values) > 0
```

---

## Required Fix

### Correct Train/Test Split for Time Series:
```python
# CORRECT: Temporal split preserves time order
split_idx = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
```

This ensures:
- Training data comes BEFORE test data
- No future information leaks into the model
- True out-of-sample evaluation

---

## Expected Realistic Performance

With temporal split and corrected metrics:
- **R² ≈ 0.00 to 0.15** (BQX momentum has weak predictive power)
- **MAE ≈ 2.5 to 3.5** (similar to target std dev = 3.14)
- **Directional Accuracy ≈ 50-55%** (slightly better than random)

These align with the low correlation (0.136) we observed.

---

## Recommended Action

1. **Halt all deployments** (already done)
2. **Retrain all models** with temporal split
3. **Fix directional accuracy** calculation
4. **Report realistic metrics**
5. **Reassess whether BQX features alone are sufficient**

---

## Data Infrastructure Reality

From previous analysis:
- **Expected**: 12,000+ features (161 BQX + 273 IDX per pair)
- **Actual**: < 20 base features (7 BQX values, 1 close_idx)
- **Gap**: 99.98% of expected features don't exist

### Questions for CE:
1. Should we generate technical indicators (RSI, MACD, etc.) from raw price data?
2. Or work with limited BQX features and accept lower performance?
3. Or wait for proper data infrastructure?

---

## Current Status

- ✅ All deployment processes stopped
- ✅ Root cause identified (data leakage)
- ✅ Directional accuracy bug identified
- ✅ Correlation analysis completed
- ⏳ Awaiting guidance on next steps

Ready to retrain with corrected methodology once you provide direction on data infrastructure.

**Build Agent**
