# BQX Target Critical Mandate: Managing Forward-Looking Values
**Date**: November 24, 2025
**Status**: CRITICAL USER MANDATE
**Author**: BQX ML Remediation Team

---

## Executive Summary

BQX values are **intentionally forward-looking** target variables that use future data. This document establishes the **permanent mandate** for managing this critical architectural decision throughout the ML pipeline.

---

## The BQX Formula Truth

### Mathematical Definition
```
bqx_Nw[T] = idx_mid[T] - AVG(idx_mid[T+1..T+N])
```

### SQL Implementation
```sql
-- USES FUTURE DATA - This is CORRECT and INTENTIONAL
bqx_45w = mid - AVG(mid) OVER (ORDER BY time ROWS BETWEEN 1 FOLLOWING AND 45 FOLLOWING)
```

### What This Means
- **T+1..T+N**: These are FUTURE intervals (not past)
- **FOLLOWING**: Looks forward in time, not backward
- **Target Variable**: What we're trying to predict

---

## Critical Understanding

### 1. BQX Values ARE Targets, NOT Features

**NEVER use bqx_ values as input features:**
```python
# ❌ WRONG - Never do this
features = ['idx_mid', 'bqx_45w', 'atr_60']  # bqx_ is a target!

# ✅ CORRECT
features = ['idx_mid', 'atr_60', 'spread_vol']
targets = ['bqx_45w', 'bqx_90w', 'bqx_180w']
```

### 2. Training vs Inference Paradigm

#### During Training (Historical Data)
```python
# We HAVE future data, so we CAN calculate bqx values
train_features = data[['idx_mid', 'atr_60', 'regime']].loc[T]
train_target = data['bqx_360w'].loc[T]  # Uses T+1..T+360 future data
model.fit(train_features, train_target)
```

#### During Inference (Production)
```python
# We DON'T have future data, so we PREDICT bqx values
current_features = get_current_features()  # Only uses T and earlier
predicted_bqx = model.predict(current_features)  # Predicts future behavior
```

### 3. Temporal Alignment is Critical

```
Time T Features → Model → Time T BQX Target
    ↑                           ↑
    Uses T and earlier         Uses T+1..T+N (future)
```

---

## The ML Logic Rationalization

### Why Forward-Looking Targets Make Sense

1. **Prediction Goal**: We want to predict if price will rise or fall
2. **BQX Interpretation**:
   - **Positive BQX**: Current > Future Average = Overbought (expect fall)
   - **Negative BQX**: Current < Future Average = Oversold (expect rise)
3. **Model Learning**: The model learns patterns that precede these conditions

### Example Scenario
```
At time T:
- Features show: High volatility, regime change, triangulation error
- BQX target shows: -5 (current price 5 points below future average)
- Model learns: These conditions often precede price rises
```

---

## Implementation Safeguards

### 1. Table Naming Convention
```sql
-- Features tables (use past/current data)
CREATE TABLE microstructure_*  -- ✅ Feature table
CREATE TABLE lag_*              -- ✅ Feature table
CREATE TABLE regime_*           -- ✅ Feature table

-- Target tables (use future data)
CREATE TABLE bqx_*              -- ⚠️ TARGET ONLY
```

### 2. Code Documentation Requirements
Every script that touches bqx_ must include:
```python
"""
WARNING: bqx_* values are TARGETS that use FUTURE data.
- Training: Use as y (target) values only
- Inference: These are what we predict
- NEVER include bqx_* in feature sets
"""
```

### 3. Validation Checks
```python
def validate_no_bqx_in_features(feature_list):
    """Ensure no bqx_ columns in feature set."""
    bqx_features = [f for f in feature_list if 'bqx_' in f]
    if bqx_features:
        raise ValueError(f"BQX values found in features: {bqx_features}")
    return True
```

---

## Data Pipeline Architecture

### Correct Flow
```
1. Raw Data (m1_*)
   ↓
2. Indexed Data (idx_*)
   ↓
3. Feature Engineering
   ├── microstructure_* (backward-looking)
   ├── lag_* (backward-looking)
   ├── regime_* (backward-looking)
   └── arbitrage_* (current)
   ↓
4. Target Calculation
   └── bqx_* (FORWARD-LOOKING)
   ↓
5. Training Tables (train_*)
   ├── All features from step 3
   └── BQX targets from step 4
```

### What Each Table Contains
| Table Type | Temporal Direction | Use in ML |
|------------|-------------------|------------|
| idx_* | Current | Feature |
| microstructure_* | Backward-looking | Feature |
| lag_* | Backward-looking | Feature |
| regime_* | Backward-looking | Feature |
| bqx_* | **FORWARD-LOOKING** | **TARGET** |

---

## Managing This Dynamic Moving Forward

### 1. Development Standards

**Every new feature script MUST:**
- [ ] Verify it doesn't read from bqx_* tables
- [ ] Use only idx_* or m1_* as source
- [ ] Calculate features using PRECEDING windows
- [ ] Include temporal direction in documentation

### 2. Training Pipeline

```python
class BQXTrainer:
    def __init__(self):
        self.feature_cols = self.get_feature_columns()
        self.target_cols = ['bqx_45w', 'bqx_90w', ...]

        # Validation on init
        validate_no_bqx_in_features(self.feature_cols)

    def prepare_data(self, df):
        X = df[self.feature_cols]  # No bqx_*
        y = df[self.target_cols]   # Only bqx_*
        return X, y
```

### 3. Production Pipeline

```python
class BQXPredictor:
    def predict(self, current_data):
        # Extract features (no future data available)
        features = self.extract_features(current_data)

        # Predict future bqx values
        predicted_bqx = self.model.predict(features)

        # Interpret prediction
        signal = self.interpret_bqx(predicted_bqx)
        return signal
```

### 4. Monitoring & Alerts

```sql
-- Alert if bqx_ appears in feature queries
CREATE OR REPLACE PROCEDURE check_feature_queries()
AS BEGIN
    IF EXISTS (
        SELECT 1 FROM query_history
        WHERE query_text LIKE '%FROM%bqx_%'
        AND query_text LIKE '%feature%'
    ) THEN
        RAISE EXCEPTION 'BQX tables used in feature extraction!';
    END IF;
END;
```

---

## Critical Success Factors

### DO ✅
- Use bqx_* as targets (y values) in training
- Calculate bqx_* using FOLLOWING windows
- Predict bqx_* values during inference
- Document forward-looking nature prominently
- Validate feature sets exclude bqx_*

### DON'T ❌
- Include bqx_* in feature sets
- Use bqx_* as input to other features
- Calculate bqx_* using PRECEDING windows
- Expose future bqx_* values during training
- Mix features and targets in same query

---

## Verification Commands

### Check Feature Tables Don't Use BQX
```bash
# Should return empty
grep "FROM.*bqx_" scripts/create_*_features.py

# Should return matches (only in train and target scripts)
grep "FROM.*bqx_" scripts/create_train_*.py scripts/create_bqx_*.py
```

### Validate Train Table Structure
```sql
-- Features should NOT have bqx_ prefix
SELECT column_name
FROM `bqx-ml.bqx_bq.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'train_eurusd'
  AND column_name LIKE 'bqx_%'
  AND column_name NOT IN ('bqx_45w', 'bqx_90w', 'bqx_180w',
                          'bqx_360w', 'bqx_720w', 'bqx_1440w', 'bqx_2880w');
-- Should return 0 rows
```

---

## Conclusion

The forward-looking nature of bqx_ values is **BY DESIGN** and **CRITICAL** to the ML system. This mandate ensures:

1. **Correct ML Architecture**: Features predict targets, not themselves
2. **No Data Leakage**: Future information stays in targets only
3. **Valid Predictions**: Models learn to predict future from current state
4. **Production Ready**: Clear separation enables real-world deployment

**This mandate must persist throughout all development, training, and production phases.**

---

## References

- [BQX_VALUE_SPECIFICATION.md](BQX_VALUE_SPECIFICATION.md) - Line 35: "Uses FOLLOWING (future data)"
- [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) - Line 147: "BQX values are TARGET variables"
- [create_train_tables_v2.py](../scripts/create_train_tables_v2.py) - Line 147: "Add target columns"

---

*This document represents a CRITICAL USER MANDATE that must be preserved and enforced.*