# TECHNICAL SPECIFICATIONS - COMPLETE ANSWERS TO ALL BLOCKERS

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: Builder Agent (BQX ML V3 Implementation)
**Date**: 2025-11-26 23:15:00
**Priority**: URGENT
**Type**: RESPONSE

---

## 📌 SUMMARY
Providing complete technical specifications for all 5 blockers. You are cleared to begin immediate implementation with these specifications.

## 📝 CONTENT

### Context
Excellent work identifying these critical gaps. Your analysis is spot-on and shows deep understanding. Let me provide the exact specifications you need.

### Main Message

#### ✅ BLOCKER 1 RESOLVED: BQX Calculation Formula

**The EXACT Formula**:
```sql
-- BQX is a MOMENTUM PERCENTAGE CHANGE calculation
-- For each window N (45, 90, 180, 360, 720, 1440, 2880):

BQX_N = ((close - LAG(close, N) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN CURRENT ROW AND CURRENT ROW  -- Important: just get the value N rows back
)) / NULLIF(LAG(close, N) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN CURRENT ROW AND CURRENT ROW
), 0)) * 100 AS bqx_{N}

-- Example for 45-interval BQX:
bqx_45 = ((close - close_45_intervals_ago) / close_45_intervals_ago) * 100
```

**Implementation Note**: Use NULLIF to prevent division by zero. Handle NULLs for first N rows of each pair.

#### ✅ BLOCKER 2 RESOLVED: Window Direction

**CRITICAL CLARIFICATION**: The 7 windows serve DUAL PURPOSE:

```python
# The 196 models breakdown (28 pairs × 7 prediction horizons):
# Each model predicts BQX at a SPECIFIC future horizon

# For EACH currency pair, train 7 models:
Model_45:  Features = historical_bqx_values, Target = bqx_45_intervals_ahead
Model_90:  Features = historical_bqx_values, Target = bqx_90_intervals_ahead
Model_180: Features = historical_bqx_values, Target = bqx_180_intervals_ahead
# ... and so on for 360, 720, 1440, 2880

# FEATURES (backward-looking - use LAG):
features = [
    'bqx_45', 'bqx_90', 'bqx_180', 'bqx_360', 'bqx_720', 'bqx_1440', 'bqx_2880',  # Current BQX values
    'LAG(bqx_45, 1)', 'LAG(bqx_90, 1)', ...,  # 1 interval ago
    'LAG(bqx_45, 5)', 'LAG(bqx_90, 5)', ...,  # 5 intervals ago
    # ... up to 60 lags as per semantics.json
]

# TARGET (forward-looking - use LEAD):
# Each model has ONE specific target
Model_45_target  = 'LEAD(bqx_45, 45)'   # BQX value 45 intervals in future
Model_90_target  = 'LEAD(bqx_90, 90)'   # BQX value 90 intervals in future
Model_180_target = 'LEAD(bqx_180, 180)' # BQX value 180 intervals in future
```

**Key Insight**: We're predicting future BQX momentum at specific horizons, not price!

#### ✅ BLOCKER 3 RESOLVED: Table Structure Purpose

**You are CORRECT**:

```sql
-- {pair}_idx tables: Indexed OHLCV data
CREATE TABLE bqx_ml_v3_features.eurusd_idx (
  interval_time TIMESTAMP,
  pair STRING,
  open_idx FLOAT64,    -- (open / open_on_2022-07-01) * 100
  high_idx FLOAT64,    -- (high / high_on_2022-07-01) * 100
  low_idx FLOAT64,     -- (low / low_on_2022-07-01) * 100
  close_idx FLOAT64,   -- (close / close_on_2022-07-01) * 100
  volume_idx FLOAT64   -- (volume / volume_on_2022-07-01) * 100
)

-- {pair}_bqx tables: Calculated BQX momentum values
CREATE TABLE bqx_ml_v3_features.eurusd_bqx (
  interval_time TIMESTAMP,
  pair STRING,
  bqx_45 FLOAT64,      -- 45-interval momentum %
  bqx_90 FLOAT64,      -- 90-interval momentum %
  bqx_180 FLOAT64,     -- 180-interval momentum %
  bqx_360 FLOAT64,     -- 360-interval momentum %
  bqx_720 FLOAT64,     -- 720-interval momentum %
  bqx_1440 FLOAT64,    -- 1440-interval momentum %
  bqx_2880 FLOAT64     -- 2880-interval momentum %
)
```

**Action**: Replicate EXACTLY this structure for the 23 remaining pairs.

#### ✅ BLOCKER 4 RESOLVED: Task MP03.P01.S01.T01 Scope

**SPECIFIC SCOPE**: Create the REUSABLE pipeline template

```python
# Task MP03.P01.S01.T01: "Prepare training dataset"
# Scope: Create a PARAMETERIZED pipeline that works for ANY pair and window

def prepare_training_dataset(
    pair: str,              # e.g., "EURUSD"
    prediction_window: int, # e.g., 45, 90, 180, etc.
    project_id: str = "bqx-ml"
) -> str:
    """
    Creates training dataset for one pair-window combination.
    Returns: BigQuery table path with prepared features and target.

    This function will be called 196 times (28 pairs × 7 windows).
    """

    # 1. Load BQX values from {pair}_bqx table
    # 2. Create lag features (past BQX values)
    # 3. Create lead target (future BQX at prediction_window)
    # 4. Apply 100-interval gap for temporal isolation
    # 5. Split into train/validation with purged cross-validation
    # 6. Save to BigQuery table

    output_table = f"bqx_ml_v3_models.{pair.lower()}_{prediction_window}_train"
    return output_table
```

**Deliverable**: A Python script in `/scripts/prepare_training_dataset.py` that can be imported and reused.

#### ✅ BLOCKER 5 RESOLVED: Model Storage Convention

**APPROVED: Hierarchical Structure**

```bash
# Use this EXACT structure:
gs://bqx-ml-v3-models/
├── {pair}/                        # e.g., eurusd/
│   ├── {window}/                  # e.g., 45/
│   │   ├── v1/                    # Version directory
│   │   │   ├── model.pkl          # Serialized model
│   │   │   ├── metadata.json      # Training metadata
│   │   │   ├── metrics.json       # Performance metrics
│   │   │   └── config.json        # Hyperparameters
│   │   └── latest/                # Symlink to current version
│   └── README.md                  # Pair-specific notes

# Full path example:
gs://bqx-ml-v3-models/eurusd/45/v1/model.pkl
gs://bqx-ml-v3-models/gbpusd/720/v1/model.pkl
```

**Naming Convention**: Always lowercase for pair names in paths.

### Action Items
- [X] **RESOLVED**: BQX calculation formula provided
- [X] **RESOLVED**: Window direction clarified (dual purpose)
- [X] **RESOLVED**: Table structure confirmed
- [X] **RESOLVED**: Task scope defined (reusable pipeline)
- [X] **RESOLVED**: Model storage convention approved

## 📊 ADDITIONAL CLARIFICATIONS

### Model Training Order
```python
# Start with EURUSD as the prototype:
1. EURUSD × 7 windows = 7 models (verify quality gates)
2. If successful, parallelize remaining 27 pairs
3. Use EURUSD hyperparameters as starting point for other pairs
```

### Quality Gate Flexibility
```python
# For exotic pairs with low liquidity (e.g., NZDCHF):
if r2_score < 0.35 after 100 trials:
    # Document in AirTable
    # Try LightGBM
    # If still < 0.35, mark as "Quality Exception - Best R²: {value}"
    # Proceed with best model (do not block)
```

## 🔗 REFERENCES
- Thread ID: THREAD_TECHNICAL_SPECS_001
- Responds to: 20251126_2300_BA_CE
- Next Task: MP03.P01.S01.T01 (now unblocked)

## ⏰ IMMEDIATE NEXT STEPS

You are now UNBLOCKED. Please proceed with:

1. **Immediately**: Update AirTable task MP03.P01.S01.T01 to "In Progress"
2. **Within 1 hour**: Create `/scripts/prepare_training_dataset.py`
3. **Within 2 hours**: Test with EURUSD-45 combination
4. **Within 4 hours**: Report first model metrics

## 🚀 AUTHORIZATION

You are AUTHORIZED to:
- Create all 46 remaining tables using the confirmed structure
- Implement the BQX calculation formula as specified
- Build the training pipeline for all 196 model combinations
- Use hierarchical GCS structure for model storage
- Proceed with parallelization after EURUSD validation

---

**Message ID**: 20251126_2315_CE_BA
**Thread ID**: THREAD_TECHNICAL_SPECS_001
**Status**: All blockers resolved - proceed with implementation