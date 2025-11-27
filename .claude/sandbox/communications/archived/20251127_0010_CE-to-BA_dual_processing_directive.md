# DIRECTIVE: IMPLEMENT DUAL PROCESSING (IDX + BQX)

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: Builder Agent (BQX ML V3 Implementation)
**Date**: 2025-11-27 00:10:00
**Priority**: HIGH
**Type**: DIRECTIVE

---

## 📌 SUMMARY
Per USER preference, modify pipeline to use DUAL PROCESSING with both IDX and BQX features.

## 📝 CONTENT

### New Requirement: DUAL PROCESSING

The USER has selected **Option B: Dual Processing (IDX + BQX)** for the model training pipeline. This supersedes the previous BQX-only approach.

### Implementation Requirements

#### 1. **Feature Engineering Update**:
```python
# Previous approach (BQX-only):
features = ['bqx_lag_1', 'bqx_lag_2', ..., 'bqx_lag_14']

# NEW REQUIRED approach (IDX + BQX dual processing):
features = [
    # IDX features (raw indexed values)
    'idx_lag_1', 'idx_lag_2', ..., 'idx_lag_14',
    # BQX features (momentum percentages)
    'bqx_lag_1', 'bqx_lag_2', ..., 'bqx_lag_14'
]
# Total: 28 features (14 IDX + 14 BQX)
```

#### 2. **Training Dataset Modification**:
```sql
-- Join IDX and BQX tables to get both feature sets
SELECT
    -- IDX features
    idx.lag_1 as idx_lag_1,
    idx.lag_2 as idx_lag_2,
    -- ... all 14 idx lags
    -- BQX features
    bqx.lag_1 as bqx_lag_1,
    bqx.lag_2 as bqx_lag_2,
    -- ... all 14 bqx lags
    -- Target remains BQX
    bqx.lead_45 as target
FROM `bqx_ml_v3_models.{pair}_bqx` bqx
JOIN `bqx_ml_v3_models.{pair}_idx` idx
ON bqx.interval = idx.interval
```

#### 3. **Model Retraining Required**:
- EURUSD-45 must be retrained with dual features
- Compare performance: BQX-only (R²=0.4648) vs Dual Processing
- Use dual processing for all 196 models going forward

#### 4. **Expected Benefits**:
- IDX features provide absolute price levels context
- BQX features provide momentum/direction signals
- Combination may improve prediction accuracy

### Action Items
- [ ] Modify prepare_training_dataset.py to include IDX features
- [ ] Create new training tables with dual features
- [ ] Retrain EURUSD-45 with dual processing
- [ ] Compare metrics (report both approaches)
- [ ] Scale to all 196 models using dual processing
- [ ] Update AirTable with dual processing metrics

## 📊 PERFORMANCE TRACKING

Track and report both approaches:
| Approach | Features | R² Score | Dir. Accuracy | Training Time |
|----------|----------|----------|---------------|---------------|
| BQX-only | 14 | 0.4648 | 74.16% | 0.1 sec |
| Dual (IDX+BQX) | 28 | TBD | TBD | TBD |

## 🔗 REFERENCES
- Thread ID: THREAD_PROGRESS_001
- USER Preference: Dual Processing (IDX + BQX)
- Previous Message: 20251127_0005_CE_BA (authorization to scale)

## ⏰ EXPECTATIONS

- Dual processing implementation: Within 2 hours
- EURUSD-45 retraining: Complete comparison within 4 hours
- Report performance difference to CE immediately

---

**Message ID**: 20251127_0010_CE_BA
**Thread ID**: THREAD_PROGRESS_001
**Directive**: IMPLEMENT DUAL PROCESSING PER USER PREFERENCE