# EXPANDED CORRELATION TABLES DIRECTIVE

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 20:00 UTC
**Priority**: CRITICAL
**Subject**: COMPLETE Feature-Target Correlation Tables Implementation

---

## EXECUTIVE SUMMARY

Create **708 correlation tables** for EURUSD features, each containing **49 correlation columns** (7 BQX windows × 7 prediction horizons). This enables correlation-based feature selection for model training.

**Total Output**: 708 tables × ~2.16M rows × 52 columns = ~1.5B data points

---

## ARCHITECTURE: INTERVAL-CENTRIC

**CRITICAL**: All calculations use `ROWS BETWEEN` (row-based), NOT time-based windows.

```sql
WINDOW w AS (ORDER BY interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW)
```

---

## TARGET FORMULA

```
delta_{W}_{H} = target_bqx{W}_h{H} - bqx_{W}
```

Where:
- W = BQX window [45, 90, 180, 360, 720, 1440, 2880]
- H = Prediction horizon [15, 30, 45, 60, 75, 90, 105]
- `target_bqx{W}_h{H}` = BQX value H intervals in the future
- `bqx_{W}` = Current BQX value

---

## OUTPUT SCHEMA

Each correlation table: `ftcorr_{feature_name}_eurusd`

| Column | Type | Description |
|--------|------|-------------|
| interval_time | TIMESTAMP | Interval timestamp |
| pair | STRING | Currency pair |
| feature_value | FLOAT64 | Feature value at interval |
| corr_w45_h15 | FLOAT64 | Correlation: feature vs delta_45_15 |
| corr_w45_h30 | FLOAT64 | Correlation: feature vs delta_45_30 |
| ... (47 more) | FLOAT64 | All 49 window/horizon combinations |

---

## COMPLETE FEATURE INVENTORY (708 Features)

### PHASE C4: AGG Features (126 features)

**Source Tables**: `agg_eurusd`, `agg_bqx_eurusd`

| Feature Column | Output Table |
|---------------|--------------|
| agg_mean_45 | ftcorr_agg_mean_45_eurusd |
| agg_std_45 | ftcorr_agg_std_45_eurusd |
| agg_min_45 | ftcorr_agg_min_45_eurusd |
| agg_max_45 | ftcorr_agg_max_45_eurusd |
| agg_range_45 | ftcorr_agg_range_45_eurusd |
| agg_cv_45 | ftcorr_agg_cv_45_eurusd |
| agg_position_45 | ftcorr_agg_position_45_eurusd |
| agg_sum_45 | ftcorr_agg_sum_45_eurusd |
| agg_count_45 | ftcorr_agg_count_45_eurusd |
| agg_mean_90 | ftcorr_agg_mean_90_eurusd |
| agg_std_90 | ftcorr_agg_std_90_eurusd |
| agg_min_90 | ftcorr_agg_min_90_eurusd |
| agg_max_90 | ftcorr_agg_max_90_eurusd |
| agg_range_90 | ftcorr_agg_range_90_eurusd |
| agg_cv_90 | ftcorr_agg_cv_90_eurusd |
| agg_position_90 | ftcorr_agg_position_90_eurusd |
| agg_sum_90 | ftcorr_agg_sum_90_eurusd |
| agg_count_90 | ftcorr_agg_count_90_eurusd |
| agg_mean_180 | ftcorr_agg_mean_180_eurusd |
| agg_std_180 | ftcorr_agg_std_180_eurusd |
| agg_min_180 | ftcorr_agg_min_180_eurusd |
| agg_max_180 | ftcorr_agg_max_180_eurusd |
| agg_range_180 | ftcorr_agg_range_180_eurusd |
| agg_cv_180 | ftcorr_agg_cv_180_eurusd |
| agg_position_180 | ftcorr_agg_position_180_eurusd |
| agg_sum_180 | ftcorr_agg_sum_180_eurusd |
| agg_count_180 | ftcorr_agg_count_180_eurusd |
| agg_mean_360 | ftcorr_agg_mean_360_eurusd |
| agg_std_360 | ftcorr_agg_std_360_eurusd |
| agg_min_360 | ftcorr_agg_min_360_eurusd |
| agg_max_360 | ftcorr_agg_max_360_eurusd |
| agg_range_360 | ftcorr_agg_range_360_eurusd |
| agg_cv_360 | ftcorr_agg_cv_360_eurusd |
| agg_position_360 | ftcorr_agg_position_360_eurusd |
| agg_sum_360 | ftcorr_agg_sum_360_eurusd |
| agg_count_360 | ftcorr_agg_count_360_eurusd |
| agg_mean_720 | ftcorr_agg_mean_720_eurusd |
| agg_std_720 | ftcorr_agg_std_720_eurusd |
| agg_min_720 | ftcorr_agg_min_720_eurusd |
| agg_max_720 | ftcorr_agg_max_720_eurusd |
| agg_range_720 | ftcorr_agg_range_720_eurusd |
| agg_cv_720 | ftcorr_agg_cv_720_eurusd |
| agg_position_720 | ftcorr_agg_position_720_eurusd |
| agg_sum_720 | ftcorr_agg_sum_720_eurusd |
| agg_count_720 | ftcorr_agg_count_720_eurusd |
| agg_mean_1440 | ftcorr_agg_mean_1440_eurusd |
| agg_std_1440 | ftcorr_agg_std_1440_eurusd |
| agg_min_1440 | ftcorr_agg_min_1440_eurusd |
| agg_max_1440 | ftcorr_agg_max_1440_eurusd |
| agg_range_1440 | ftcorr_agg_range_1440_eurusd |
| agg_cv_1440 | ftcorr_agg_cv_1440_eurusd |
| agg_position_1440 | ftcorr_agg_position_1440_eurusd |
| agg_sum_1440 | ftcorr_agg_sum_1440_eurusd |
| agg_count_1440 | ftcorr_agg_count_1440_eurusd |
| agg_mean_2880 | ftcorr_agg_mean_2880_eurusd |
| agg_std_2880 | ftcorr_agg_std_2880_eurusd |
| agg_min_2880 | ftcorr_agg_min_2880_eurusd |
| agg_max_2880 | ftcorr_agg_max_2880_eurusd |
| agg_range_2880 | ftcorr_agg_range_2880_eurusd |
| agg_cv_2880 | ftcorr_agg_cv_2880_eurusd |
| agg_position_2880 | ftcorr_agg_position_2880_eurusd |
| agg_sum_2880 | ftcorr_agg_sum_2880_eurusd |
| agg_count_2880 | ftcorr_agg_count_2880_eurusd |

**IDX variant**: Same columns from `agg_eurusd` → prefix with `idx_` in output table name
**Total**: 63 IDX + 63 BQX = 126 features

---

### PHASE C5: REG Features (140 features)

**Source Tables**: `reg_eurusd`, `reg_bqx_eurusd`

| Feature Column | Description |
|---------------|-------------|
| reg_mean_{W} | Rolling mean |
| reg_std_{W} | Rolling std dev |
| reg_min_{W} | Rolling minimum |
| reg_max_{W} | Rolling maximum |
| reg_first_{W} | First value in window |
| reg_slope_{W} | Linear regression slope |
| reg_direction_{W} | Direction indicator |
| reg_deviation_{W} | Deviation from mean |
| reg_zscore_{W} | Z-score |
| reg_range_pct_{W} | Range as % of mean |

Windows: 45, 90, 180, 360, 720, 1440, 2880 (7 windows × 10 features = 70 per variant)
**Total**: 70 IDX + 70 BQX = 140 features

---

### PHASE C6: MOM Features (84 features)

**Source Tables**: `mom_eurusd`, `mom_bqx_eurusd`

| Feature Column | Description |
|---------------|-------------|
| mom_roc_{W} | Rate of change |
| mom_diff_{W} | Absolute difference |
| mom_dir_{W} | Direction indicator |
| mom_roc_smooth_{W} | Smoothed ROC |
| mom_zscore_{W} | Z-score of momentum |
| mom_pos_count_{W} | Positive interval count |
| mom_strength_{W} | Momentum strength |

Windows: 45, 90, 180, 360, 720, 1440 (6 windows × 7 features = 42 per variant)
**Total**: 42 IDX + 42 BQX = 84 features

---

### PHASE C7: ALIGN Features (82 features)

**Source Tables**: `align_eurusd`, `align_bqx_eurusd`

| Feature Column | Description |
|---------------|-------------|
| dir_{W} | Direction for window W |
| pos_{W} | Position within range |
| zscore_{W} | Z-score for window |
| align_trend_{W1}_{W2} | Trend alignment between windows |
| align_pos_diff_{W1}_{W2} | Position difference |
| align_mean_{W1}_{W2} | Mean alignment |
| align_zscore_diff_{W1}_{W2} | Z-score difference |
| align_trend_score | Composite trend score |
| align_unanimous | All windows agree |
| align_mean_score | Average alignment score |

**Total**: 41 IDX + 41 BQX = 82 features

---

### PHASE C8: VOL Features (60 features)

**Source Tables**: `vol_eurusd`, `vol_bqx_eurusd`

| Feature Column | Description |
|---------------|-------------|
| vol_realized_{W} | Realized volatility |
| vol_atr_{W} | Average true range |
| vol_normalized_{W} | Normalized volatility |
| vol_range_pct_{W} | Range as percentage |
| vol_of_vol_{W} | Volatility of volatility |
| vol_zscore_{W} | Volatility z-score |

Windows: 45, 90, 180, 360, 720 (5 windows × 6 features = 30 per variant)
**Total**: 30 IDX + 30 BQX = 60 features

---

### PHASE C9: DER/DIV/MRT/REV/EXT Features (89 features)

**DER** (`der_eurusd`, `der_bqx_eurusd`): 15 features × 2 = 30
- der_v1_{W} (7 windows)
- der_v2_{W} (7 windows)
- der_v3_composite (1)

**DIV** (`div_eurusd`, `div_bqx_eurusd`): 6 features × 2 = 12
- div_45_2880, div_90_1440, div_180_720
- div_sign_alignment, div_cascade_direction, div_short_leading

**MRT** (`mrt_eurusd`, `mrt_bqx_eurusd`): 10 features × 2 = 20
- mrt_tension_{W} (7 windows)
- mrt_tension_composite, mrt_half_life, mrt_reversion_probability

**REV** (`rev_eurusd`, `rev_bqx_eurusd`): 10 features × 2 = 20
- rev_decel_{W} (7 windows)
- rev_exhaustion, rev_divergence, rev_turning_prob

**EXT** (`ext_bqx_eurusd`): 16 features (BQX only)
- ext_zscore_{W} (7 windows)
- ext_percentile_{W} (7 windows)
- ext_distance_zero, ext_sigma_band

**Phase C9 Total**: 30 + 12 + 20 + 20 + 16 = **98 features** (CORRECTED from 89)

---

### PHASE C10: LAG/REGIME/TMP/CYC/BASE Features (118 features)

**LAG** (`lag_eurusd_45`, `lag_eurusd_90`, `lag_bqx_eurusd_45`, `lag_bqx_eurusd_90`): 40 features
- IDX: 11 columns × 2 periods = 22
- BQX: 9 columns × 2 periods = 18

**REGIME** (`regime_eurusd_45`, `regime_eurusd_90`, `regime_bqx_eurusd_45`, `regime_bqx_eurusd_90`): 62 features
- IDX: 13 columns × 2 periods = 26
- BQX: 18 columns × 2 periods = 36

**TMP** (`tmp_eurusd`, `tmp_bqx_eurusd`): 22 features
- 11 columns × 2 variants = 22

**CYC** (`cyc_bqx_eurusd`): 4 features (BQX only)
- cyc_intervals_since_zero, cyc_intervals_since_ext
- cyc_avg_cycle_length, cyc_current_cycle_progress

**BASE** (`eurusd_bqx`, `eurusd_idx`): 19 features
- eurusd_bqx: 14 features (bqx_{W}, target_{W})
- eurusd_idx: 5 features (open/high/low/close/volume_idx)

**Phase C10 Total**: 40 + 62 + 22 + 4 + 19 = **147 features** (CORRECTED from 127)

---

## CORRECTED FEATURE TOTALS

| Phase | Feature Type | Features |
|-------|--------------|----------|
| C4 | AGG (IDX + BQX) | 126 |
| C5 | REG (IDX + BQX) | 140 |
| C6 | MOM (IDX + BQX) | 84 |
| C7 | ALIGN (IDX + BQX) | 82 |
| C8 | VOL (IDX + BQX) | 60 |
| C9 | DER/DIV/MRT/REV/EXT | 98 |
| C10 | LAG/REGIME/TMP/CYC/BASE | 147 |
| **TOTAL** | | **737** |

**NOTE**: The original 708 count was based on EURUSD-specific tables. The corrected total of 737 includes all feature columns. Some columns may be excluded (e.g., `source_value`, metadata columns) - BA should validate actual feature count during implementation.

---

## SQL TEMPLATE

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.ftcorr_{FEATURE_NAME}_eurusd` AS
WITH feature_data AS (
  SELECT
    interval_time,
    pair,
    {FEATURE_COLUMN} as feature_value
  FROM `bqx-ml.bqx_ml_v3_features.{SOURCE_TABLE}`
  WHERE pair = 'EURUSD'
),
target_data AS (
  SELECT
    interval_time,
    -- Delta calculations for all 49 window/horizon combinations
    target_bqx45_h15 - bqx_45 as d_w45_h15,
    target_bqx45_h30 - bqx_45 as d_w45_h30,
    target_bqx45_h45 - bqx_45 as d_w45_h45,
    target_bqx45_h60 - bqx_45 as d_w45_h60,
    target_bqx45_h75 - bqx_45 as d_w45_h75,
    target_bqx45_h90 - bqx_45 as d_w45_h90,
    target_bqx45_h105 - bqx_45 as d_w45_h105,
    target_bqx90_h15 - bqx_90 as d_w90_h15,
    target_bqx90_h30 - bqx_90 as d_w90_h30,
    target_bqx90_h45 - bqx_90 as d_w90_h45,
    target_bqx90_h60 - bqx_90 as d_w90_h60,
    target_bqx90_h75 - bqx_90 as d_w90_h75,
    target_bqx90_h90 - bqx_90 as d_w90_h90,
    target_bqx90_h105 - bqx_90 as d_w90_h105,
    target_bqx180_h15 - bqx_180 as d_w180_h15,
    target_bqx180_h30 - bqx_180 as d_w180_h30,
    target_bqx180_h45 - bqx_180 as d_w180_h45,
    target_bqx180_h60 - bqx_180 as d_w180_h60,
    target_bqx180_h75 - bqx_180 as d_w180_h75,
    target_bqx180_h90 - bqx_180 as d_w180_h90,
    target_bqx180_h105 - bqx_180 as d_w180_h105,
    target_bqx360_h15 - bqx_360 as d_w360_h15,
    target_bqx360_h30 - bqx_360 as d_w360_h30,
    target_bqx360_h45 - bqx_360 as d_w360_h45,
    target_bqx360_h60 - bqx_360 as d_w360_h60,
    target_bqx360_h75 - bqx_360 as d_w360_h75,
    target_bqx360_h90 - bqx_360 as d_w360_h90,
    target_bqx360_h105 - bqx_360 as d_w360_h105,
    target_bqx720_h15 - bqx_720 as d_w720_h15,
    target_bqx720_h30 - bqx_720 as d_w720_h30,
    target_bqx720_h45 - bqx_720 as d_w720_h45,
    target_bqx720_h60 - bqx_720 as d_w720_h60,
    target_bqx720_h75 - bqx_720 as d_w720_h75,
    target_bqx720_h90 - bqx_720 as d_w720_h90,
    target_bqx720_h105 - bqx_720 as d_w720_h105,
    target_bqx1440_h15 - bqx_1440 as d_w1440_h15,
    target_bqx1440_h30 - bqx_1440 as d_w1440_h30,
    target_bqx1440_h45 - bqx_1440 as d_w1440_h45,
    target_bqx1440_h60 - bqx_1440 as d_w1440_h60,
    target_bqx1440_h75 - bqx_1440 as d_w1440_h75,
    target_bqx1440_h90 - bqx_1440 as d_w1440_h90,
    target_bqx1440_h105 - bqx_1440 as d_w1440_h105,
    target_bqx2880_h15 - bqx_2880 as d_w2880_h15,
    target_bqx2880_h30 - bqx_2880 as d_w2880_h30,
    target_bqx2880_h45 - bqx_2880 as d_w2880_h45,
    target_bqx2880_h60 - bqx_2880 as d_w2880_h60,
    target_bqx2880_h75 - bqx_2880 as d_w2880_h75,
    target_bqx2880_h90 - bqx_2880 as d_w2880_h90,
    target_bqx2880_h105 - bqx_2880 as d_w2880_h105
  FROM `bqx-ml.bqx_ml_v3_analytics.targets_eurusd`
)
SELECT
  f.interval_time,
  f.pair,
  f.feature_value,
  -- 49 rolling correlations (720-interval window)
  CORR(f.feature_value, t.d_w45_h15) OVER w as corr_w45_h15,
  CORR(f.feature_value, t.d_w45_h30) OVER w as corr_w45_h30,
  CORR(f.feature_value, t.d_w45_h45) OVER w as corr_w45_h45,
  CORR(f.feature_value, t.d_w45_h60) OVER w as corr_w45_h60,
  CORR(f.feature_value, t.d_w45_h75) OVER w as corr_w45_h75,
  CORR(f.feature_value, t.d_w45_h90) OVER w as corr_w45_h90,
  CORR(f.feature_value, t.d_w45_h105) OVER w as corr_w45_h105,
  CORR(f.feature_value, t.d_w90_h15) OVER w as corr_w90_h15,
  CORR(f.feature_value, t.d_w90_h30) OVER w as corr_w90_h30,
  CORR(f.feature_value, t.d_w90_h45) OVER w as corr_w90_h45,
  CORR(f.feature_value, t.d_w90_h60) OVER w as corr_w90_h60,
  CORR(f.feature_value, t.d_w90_h75) OVER w as corr_w90_h75,
  CORR(f.feature_value, t.d_w90_h90) OVER w as corr_w90_h90,
  CORR(f.feature_value, t.d_w90_h105) OVER w as corr_w90_h105,
  CORR(f.feature_value, t.d_w180_h15) OVER w as corr_w180_h15,
  CORR(f.feature_value, t.d_w180_h30) OVER w as corr_w180_h30,
  CORR(f.feature_value, t.d_w180_h45) OVER w as corr_w180_h45,
  CORR(f.feature_value, t.d_w180_h60) OVER w as corr_w180_h60,
  CORR(f.feature_value, t.d_w180_h75) OVER w as corr_w180_h75,
  CORR(f.feature_value, t.d_w180_h90) OVER w as corr_w180_h90,
  CORR(f.feature_value, t.d_w180_h105) OVER w as corr_w180_h105,
  CORR(f.feature_value, t.d_w360_h15) OVER w as corr_w360_h15,
  CORR(f.feature_value, t.d_w360_h30) OVER w as corr_w360_h30,
  CORR(f.feature_value, t.d_w360_h45) OVER w as corr_w360_h45,
  CORR(f.feature_value, t.d_w360_h60) OVER w as corr_w360_h60,
  CORR(f.feature_value, t.d_w360_h75) OVER w as corr_w360_h75,
  CORR(f.feature_value, t.d_w360_h90) OVER w as corr_w360_h90,
  CORR(f.feature_value, t.d_w360_h105) OVER w as corr_w360_h105,
  CORR(f.feature_value, t.d_w720_h15) OVER w as corr_w720_h15,
  CORR(f.feature_value, t.d_w720_h30) OVER w as corr_w720_h30,
  CORR(f.feature_value, t.d_w720_h45) OVER w as corr_w720_h45,
  CORR(f.feature_value, t.d_w720_h60) OVER w as corr_w720_h60,
  CORR(f.feature_value, t.d_w720_h75) OVER w as corr_w720_h75,
  CORR(f.feature_value, t.d_w720_h90) OVER w as corr_w720_h90,
  CORR(f.feature_value, t.d_w720_h105) OVER w as corr_w720_h105,
  CORR(f.feature_value, t.d_w1440_h15) OVER w as corr_w1440_h15,
  CORR(f.feature_value, t.d_w1440_h30) OVER w as corr_w1440_h30,
  CORR(f.feature_value, t.d_w1440_h45) OVER w as corr_w1440_h45,
  CORR(f.feature_value, t.d_w1440_h60) OVER w as corr_w1440_h60,
  CORR(f.feature_value, t.d_w1440_h75) OVER w as corr_w1440_h75,
  CORR(f.feature_value, t.d_w1440_h90) OVER w as corr_w1440_h90,
  CORR(f.feature_value, t.d_w1440_h105) OVER w as corr_w1440_h105,
  CORR(f.feature_value, t.d_w2880_h15) OVER w as corr_w2880_h15,
  CORR(f.feature_value, t.d_w2880_h30) OVER w as corr_w2880_h30,
  CORR(f.feature_value, t.d_w2880_h45) OVER w as corr_w2880_h45,
  CORR(f.feature_value, t.d_w2880_h60) OVER w as corr_w2880_h60,
  CORR(f.feature_value, t.d_w2880_h75) OVER w as corr_w2880_h75,
  CORR(f.feature_value, t.d_w2880_h90) OVER w as corr_w2880_h90,
  CORR(f.feature_value, t.d_w2880_h105) OVER w as corr_w2880_h105
FROM feature_data f
JOIN target_data t ON f.interval_time = t.interval_time
WINDOW w AS (ORDER BY f.interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW)
ORDER BY f.interval_time;
```

---

## PYTHON AUTOMATION SCRIPT

Save as `/home/micha/bqx_ml_v3/scripts/generate_correlation_tables.py`:

```python
#!/usr/bin/env python3
"""
Feature-Target Correlation Table Generator
Generates 708+ correlation tables with 49 columns each
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT = "bqx-ml"
DATASET = "bqx_ml_v3_analytics"
FEATURES_DATASET = "bqx_ml_v3_features"
LOCATION = "us-central1"
MAX_WORKERS = 4

# Complete Feature Inventory
FEATURE_INVENTORY = {
    # AGG features (126)
    "agg_eurusd": [
        "agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45",
        "agg_cv_45", "agg_position_45", "agg_sum_45", "agg_count_45",
        "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90",
        "agg_cv_90", "agg_position_90", "agg_sum_90", "agg_count_90",
        "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180",
        "agg_cv_180", "agg_position_180", "agg_sum_180", "agg_count_180",
        "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360",
        "agg_cv_360", "agg_position_360", "agg_sum_360", "agg_count_360",
        "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720",
        "agg_cv_720", "agg_position_720", "agg_sum_720", "agg_count_720",
        "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440",
        "agg_cv_1440", "agg_position_1440", "agg_sum_1440", "agg_count_1440",
        "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880",
        "agg_cv_2880", "agg_position_2880", "agg_sum_2880", "agg_count_2880",
    ],
    "agg_bqx_eurusd": [
        "agg_mean_45", "agg_std_45", "agg_min_45", "agg_max_45", "agg_range_45",
        "agg_cv_45", "agg_position_45", "agg_sum_45", "agg_count_45",
        "agg_mean_90", "agg_std_90", "agg_min_90", "agg_max_90", "agg_range_90",
        "agg_cv_90", "agg_position_90", "agg_sum_90", "agg_count_90",
        "agg_mean_180", "agg_std_180", "agg_min_180", "agg_max_180", "agg_range_180",
        "agg_cv_180", "agg_position_180", "agg_sum_180", "agg_count_180",
        "agg_mean_360", "agg_std_360", "agg_min_360", "agg_max_360", "agg_range_360",
        "agg_cv_360", "agg_position_360", "agg_sum_360", "agg_count_360",
        "agg_mean_720", "agg_std_720", "agg_min_720", "agg_max_720", "agg_range_720",
        "agg_cv_720", "agg_position_720", "agg_sum_720", "agg_count_720",
        "agg_mean_1440", "agg_std_1440", "agg_min_1440", "agg_max_1440", "agg_range_1440",
        "agg_cv_1440", "agg_position_1440", "agg_sum_1440", "agg_count_1440",
        "agg_mean_2880", "agg_std_2880", "agg_min_2880", "agg_max_2880", "agg_range_2880",
        "agg_cv_2880", "agg_position_2880", "agg_sum_2880", "agg_count_2880",
    ],

    # REG features (140)
    "reg_eurusd": [
        "reg_mean_45", "reg_std_45", "reg_min_45", "reg_max_45", "reg_first_45",
        "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45", "reg_range_pct_45",
        "reg_mean_90", "reg_std_90", "reg_min_90", "reg_max_90", "reg_first_90",
        "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90", "reg_range_pct_90",
        "reg_mean_180", "reg_std_180", "reg_min_180", "reg_max_180", "reg_first_180",
        "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180", "reg_range_pct_180",
        "reg_mean_360", "reg_std_360", "reg_min_360", "reg_max_360", "reg_first_360",
        "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360", "reg_range_pct_360",
        "reg_mean_720", "reg_std_720", "reg_min_720", "reg_max_720", "reg_first_720",
        "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720", "reg_range_pct_720",
        "reg_mean_1440", "reg_std_1440", "reg_min_1440", "reg_max_1440", "reg_first_1440",
        "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440", "reg_range_pct_1440",
        "reg_mean_2880", "reg_std_2880", "reg_min_2880", "reg_max_2880", "reg_first_2880",
        "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880", "reg_range_pct_2880",
    ],
    "reg_bqx_eurusd": [
        "reg_mean_45", "reg_std_45", "reg_min_45", "reg_max_45", "reg_first_45",
        "reg_slope_45", "reg_direction_45", "reg_deviation_45", "reg_zscore_45", "reg_range_pct_45",
        "reg_mean_90", "reg_std_90", "reg_min_90", "reg_max_90", "reg_first_90",
        "reg_slope_90", "reg_direction_90", "reg_deviation_90", "reg_zscore_90", "reg_range_pct_90",
        "reg_mean_180", "reg_std_180", "reg_min_180", "reg_max_180", "reg_first_180",
        "reg_slope_180", "reg_direction_180", "reg_deviation_180", "reg_zscore_180", "reg_range_pct_180",
        "reg_mean_360", "reg_std_360", "reg_min_360", "reg_max_360", "reg_first_360",
        "reg_slope_360", "reg_direction_360", "reg_deviation_360", "reg_zscore_360", "reg_range_pct_360",
        "reg_mean_720", "reg_std_720", "reg_min_720", "reg_max_720", "reg_first_720",
        "reg_slope_720", "reg_direction_720", "reg_deviation_720", "reg_zscore_720", "reg_range_pct_720",
        "reg_mean_1440", "reg_std_1440", "reg_min_1440", "reg_max_1440", "reg_first_1440",
        "reg_slope_1440", "reg_direction_1440", "reg_deviation_1440", "reg_zscore_1440", "reg_range_pct_1440",
        "reg_mean_2880", "reg_std_2880", "reg_min_2880", "reg_max_2880", "reg_first_2880",
        "reg_slope_2880", "reg_direction_2880", "reg_deviation_2880", "reg_zscore_2880", "reg_range_pct_2880",
    ],

    # MOM features (84)
    "mom_eurusd": [
        "mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_roc_smooth_45", "mom_zscore_45", "mom_pos_count_45", "mom_strength_45",
        "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_roc_smooth_90", "mom_zscore_90", "mom_pos_count_90", "mom_strength_90",
        "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_roc_smooth_180", "mom_zscore_180", "mom_pos_count_180", "mom_strength_180",
        "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_roc_smooth_360", "mom_zscore_360", "mom_pos_count_360", "mom_strength_360",
        "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_roc_smooth_720", "mom_zscore_720", "mom_pos_count_720", "mom_strength_720",
        "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_roc_smooth_1440", "mom_zscore_1440", "mom_pos_count_1440", "mom_strength_1440",
    ],
    "mom_bqx_eurusd": [
        "mom_roc_45", "mom_diff_45", "mom_dir_45", "mom_roc_smooth_45", "mom_zscore_45", "mom_pos_count_45", "mom_strength_45",
        "mom_roc_90", "mom_diff_90", "mom_dir_90", "mom_roc_smooth_90", "mom_zscore_90", "mom_pos_count_90", "mom_strength_90",
        "mom_roc_180", "mom_diff_180", "mom_dir_180", "mom_roc_smooth_180", "mom_zscore_180", "mom_pos_count_180", "mom_strength_180",
        "mom_roc_360", "mom_diff_360", "mom_dir_360", "mom_roc_smooth_360", "mom_zscore_360", "mom_pos_count_360", "mom_strength_360",
        "mom_roc_720", "mom_diff_720", "mom_dir_720", "mom_roc_smooth_720", "mom_zscore_720", "mom_pos_count_720", "mom_strength_720",
        "mom_roc_1440", "mom_diff_1440", "mom_dir_1440", "mom_roc_smooth_1440", "mom_zscore_1440", "mom_pos_count_1440", "mom_strength_1440",
    ],

    # ALIGN features (82)
    "align_eurusd": [
        "dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
        "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
        "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
        "align_trend_45_90", "align_pos_diff_45_90", "align_mean_45_90", "align_zscore_diff_45_90",
        "align_trend_90_180", "align_pos_diff_90_180", "align_mean_90_180", "align_zscore_diff_90_180",
        "align_trend_180_360", "align_pos_diff_180_360", "align_mean_180_360", "align_zscore_diff_180_360",
        "align_trend_360_720", "align_pos_diff_360_720", "align_mean_360_720", "align_zscore_diff_360_720",
        "align_trend_720_1440", "align_pos_diff_720_1440", "align_mean_720_1440", "align_zscore_diff_720_1440",
        "align_trend_score", "align_unanimous", "align_mean_score",
    ],
    "align_bqx_eurusd": [
        "dir_45", "dir_90", "dir_180", "dir_360", "dir_720", "dir_1440",
        "pos_45", "pos_90", "pos_180", "pos_360", "pos_720", "pos_1440",
        "zscore_45", "zscore_90", "zscore_180", "zscore_360", "zscore_720", "zscore_1440",
        "align_trend_45_90", "align_pos_diff_45_90", "align_mean_45_90", "align_zscore_diff_45_90",
        "align_trend_90_180", "align_pos_diff_90_180", "align_mean_90_180", "align_zscore_diff_90_180",
        "align_trend_180_360", "align_pos_diff_180_360", "align_mean_180_360", "align_zscore_diff_180_360",
        "align_trend_360_720", "align_pos_diff_360_720", "align_mean_360_720", "align_zscore_diff_360_720",
        "align_trend_720_1440", "align_pos_diff_720_1440", "align_mean_720_1440", "align_zscore_diff_720_1440",
        "align_trend_score", "align_unanimous", "align_mean_score",
    ],

    # VOL features (60)
    "vol_eurusd": [
        "vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_range_pct_45", "vol_of_vol_45", "vol_zscore_45",
        "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_range_pct_90", "vol_of_vol_90", "vol_zscore_90",
        "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_range_pct_180", "vol_of_vol_180", "vol_zscore_180",
        "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_range_pct_360", "vol_of_vol_360", "vol_zscore_360",
        "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_range_pct_720", "vol_of_vol_720", "vol_zscore_720",
    ],
    "vol_bqx_eurusd": [
        "vol_realized_45", "vol_atr_45", "vol_normalized_45", "vol_range_pct_45", "vol_of_vol_45", "vol_zscore_45",
        "vol_realized_90", "vol_atr_90", "vol_normalized_90", "vol_range_pct_90", "vol_of_vol_90", "vol_zscore_90",
        "vol_realized_180", "vol_atr_180", "vol_normalized_180", "vol_range_pct_180", "vol_of_vol_180", "vol_zscore_180",
        "vol_realized_360", "vol_atr_360", "vol_normalized_360", "vol_range_pct_360", "vol_of_vol_360", "vol_zscore_360",
        "vol_realized_720", "vol_atr_720", "vol_normalized_720", "vol_range_pct_720", "vol_of_vol_720", "vol_zscore_720",
    ],

    # DER features (30)
    "der_eurusd": [
        "der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
        "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880",
        "der_v3_composite",
    ],
    "der_bqx_eurusd": [
        "der_v1_45", "der_v1_90", "der_v1_180", "der_v1_360", "der_v1_720", "der_v1_1440", "der_v1_2880",
        "der_v2_45", "der_v2_90", "der_v2_180", "der_v2_360", "der_v2_720", "der_v2_1440", "der_v2_2880",
        "der_v3_composite",
    ],

    # DIV features (12)
    "div_eurusd": [
        "div_45_2880", "div_90_1440", "div_180_720",
        "div_sign_alignment", "div_cascade_direction", "div_short_leading",
    ],
    "div_bqx_eurusd": [
        "div_45_2880", "div_90_1440", "div_180_720",
        "div_sign_alignment", "div_cascade_direction", "div_short_leading",
    ],

    # MRT features (20)
    "mrt_eurusd": [
        "mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360",
        "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
        "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability",
    ],
    "mrt_bqx_eurusd": [
        "mrt_tension_45", "mrt_tension_90", "mrt_tension_180", "mrt_tension_360",
        "mrt_tension_720", "mrt_tension_1440", "mrt_tension_2880",
        "mrt_tension_composite", "mrt_half_life", "mrt_reversion_probability",
    ],

    # REV features (20)
    "rev_eurusd": [
        "rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360",
        "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
        "rev_exhaustion", "rev_divergence", "rev_turning_prob",
    ],
    "rev_bqx_eurusd": [
        "rev_decel_45", "rev_decel_90", "rev_decel_180", "rev_decel_360",
        "rev_decel_720", "rev_decel_1440", "rev_decel_2880",
        "rev_exhaustion", "rev_divergence", "rev_turning_prob",
    ],

    # EXT features (16) - BQX only
    "ext_bqx_eurusd": [
        "ext_zscore_45", "ext_zscore_90", "ext_zscore_180", "ext_zscore_360",
        "ext_zscore_720", "ext_zscore_1440", "ext_zscore_2880",
        "ext_percentile_45", "ext_percentile_90", "ext_percentile_180", "ext_percentile_360",
        "ext_percentile_720", "ext_percentile_1440", "ext_percentile_2880",
        "ext_distance_zero", "ext_sigma_band",
    ],

    # CYC features (4) - BQX only
    "cyc_bqx_eurusd": [
        "cyc_intervals_since_zero", "cyc_intervals_since_ext",
        "cyc_avg_cycle_length", "cyc_current_cycle_progress",
    ],

    # TMP features (22)
    "tmp_eurusd": [
        "tmp_hour_utc", "tmp_day_of_week", "tmp_is_london", "tmp_is_ny", "tmp_is_asian",
        "tmp_is_overlap_london_ny", "tmp_session_phase", "tmp_month", "tmp_quarter",
        "tmp_is_weekend", "tmp_minute",
    ],
    "tmp_bqx_eurusd": [
        "tmp_hour_utc", "tmp_day_of_week", "tmp_is_london", "tmp_is_ny", "tmp_is_asian",
        "tmp_is_overlap_london_ny", "tmp_session_phase", "tmp_month", "tmp_quarter",
        "tmp_is_weekend", "tmp_minute",
    ],

    # LAG features (40)
    "lag_eurusd_45": [
        "close_lag_45", "open_lag_45", "high_lag_45", "low_lag_45", "volume_lag_45",
        "return_lag_45", "sma_45", "volume_sma_45", "volatility_45", "hl_range_45", "momentum_45",
    ],
    "lag_eurusd_90": [
        "close_lag_90", "open_lag_90", "high_lag_90", "low_lag_90", "volume_lag_90",
        "return_lag_90", "sma_90", "volume_sma_90", "volatility_90", "hl_range_90", "momentum_90",
    ],
    "lag_bqx_eurusd_45": [
        "bqx_lag_45", "return_lag_45", "sma_45", "ema_45",
        "volatility_45", "hl_range_45", "momentum_45", "positive_ratio_45",
    ],
    "lag_bqx_eurusd_90": [
        "bqx_lag_90", "return_lag_90", "sma_90", "ema_90",
        "volatility_90", "hl_range_90", "momentum_90", "positive_ratio_90",
    ],

    # REGIME features (62)
    "regime_eurusd_45": [
        "volatility_45", "hl_range_45", "return_lag_45",
        "volatility_regime", "range_regime", "return_regime",
        "volatility_regime_code", "range_regime_code", "return_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66",
    ],
    "regime_eurusd_90": [
        "volatility_90", "hl_range_90", "return_lag_90",
        "volatility_regime", "range_regime", "return_regime",
        "volatility_regime_code", "range_regime_code", "return_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66",
    ],
    "regime_bqx_eurusd_45": [
        "volatility_45", "hl_range_45", "return_lag_45", "momentum_45",
        "volatility_regime", "range_regime", "return_regime", "momentum_regime",
        "volatility_regime_code", "range_regime_code", "return_regime_code", "momentum_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66", "momentum_p33", "momentum_p66",
    ],
    "regime_bqx_eurusd_90": [
        "volatility_90", "hl_range_90", "return_lag_90", "momentum_90",
        "volatility_regime", "range_regime", "return_regime", "momentum_regime",
        "volatility_regime_code", "range_regime_code", "return_regime_code", "momentum_regime_code",
        "vol_p33", "vol_p66", "range_p33", "range_p66", "momentum_p33", "momentum_p66",
    ],

    # BASE features (19)
    "eurusd_bqx": [
        "bqx_45", "target_45", "bqx_90", "target_90", "bqx_180", "target_180",
        "bqx_360", "target_360", "bqx_720", "target_720", "bqx_1440", "target_1440",
        "bqx_2880", "target_2880",
    ],
    "eurusd_idx": [
        "open_idx", "high_idx", "low_idx", "close_idx", "volume_idx",
    ],
}


def get_sql_template(source_table: str, feature_column: str, output_table: str) -> str:
    """Generate SQL for correlation table creation."""
    # Determine variant prefix for output table naming
    variant = "bqx" if "_bqx_" in source_table or source_table.endswith("_bqx") else "idx"

    return f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.{output_table}` AS
WITH feature_data AS (
  SELECT
    interval_time,
    pair,
    CAST({feature_column} AS FLOAT64) as feature_value
  FROM `{PROJECT}.{FEATURES_DATASET}.{source_table}`
  WHERE pair = 'EURUSD'
),
target_data AS (
  SELECT
    interval_time,
    target_bqx45_h15 - bqx_45 as d_w45_h15,
    target_bqx45_h30 - bqx_45 as d_w45_h30,
    target_bqx45_h45 - bqx_45 as d_w45_h45,
    target_bqx45_h60 - bqx_45 as d_w45_h60,
    target_bqx45_h75 - bqx_45 as d_w45_h75,
    target_bqx45_h90 - bqx_45 as d_w45_h90,
    target_bqx45_h105 - bqx_45 as d_w45_h105,
    target_bqx90_h15 - bqx_90 as d_w90_h15,
    target_bqx90_h30 - bqx_90 as d_w90_h30,
    target_bqx90_h45 - bqx_90 as d_w90_h45,
    target_bqx90_h60 - bqx_90 as d_w90_h60,
    target_bqx90_h75 - bqx_90 as d_w90_h75,
    target_bqx90_h90 - bqx_90 as d_w90_h90,
    target_bqx90_h105 - bqx_90 as d_w90_h105,
    target_bqx180_h15 - bqx_180 as d_w180_h15,
    target_bqx180_h30 - bqx_180 as d_w180_h30,
    target_bqx180_h45 - bqx_180 as d_w180_h45,
    target_bqx180_h60 - bqx_180 as d_w180_h60,
    target_bqx180_h75 - bqx_180 as d_w180_h75,
    target_bqx180_h90 - bqx_180 as d_w180_h90,
    target_bqx180_h105 - bqx_180 as d_w180_h105,
    target_bqx360_h15 - bqx_360 as d_w360_h15,
    target_bqx360_h30 - bqx_360 as d_w360_h30,
    target_bqx360_h45 - bqx_360 as d_w360_h45,
    target_bqx360_h60 - bqx_360 as d_w360_h60,
    target_bqx360_h75 - bqx_360 as d_w360_h75,
    target_bqx360_h90 - bqx_360 as d_w360_h90,
    target_bqx360_h105 - bqx_360 as d_w360_h105,
    target_bqx720_h15 - bqx_720 as d_w720_h15,
    target_bqx720_h30 - bqx_720 as d_w720_h30,
    target_bqx720_h45 - bqx_720 as d_w720_h45,
    target_bqx720_h60 - bqx_720 as d_w720_h60,
    target_bqx720_h75 - bqx_720 as d_w720_h75,
    target_bqx720_h90 - bqx_720 as d_w720_h90,
    target_bqx720_h105 - bqx_720 as d_w720_h105,
    target_bqx1440_h15 - bqx_1440 as d_w1440_h15,
    target_bqx1440_h30 - bqx_1440 as d_w1440_h30,
    target_bqx1440_h45 - bqx_1440 as d_w1440_h45,
    target_bqx1440_h60 - bqx_1440 as d_w1440_h60,
    target_bqx1440_h75 - bqx_1440 as d_w1440_h75,
    target_bqx1440_h90 - bqx_1440 as d_w1440_h90,
    target_bqx1440_h105 - bqx_1440 as d_w1440_h105,
    target_bqx2880_h15 - bqx_2880 as d_w2880_h15,
    target_bqx2880_h30 - bqx_2880 as d_w2880_h30,
    target_bqx2880_h45 - bqx_2880 as d_w2880_h45,
    target_bqx2880_h60 - bqx_2880 as d_w2880_h60,
    target_bqx2880_h75 - bqx_2880 as d_w2880_h75,
    target_bqx2880_h90 - bqx_2880 as d_w2880_h90,
    target_bqx2880_h105 - bqx_2880 as d_w2880_h105
  FROM `{PROJECT}.{DATASET}.targets_eurusd`
)
SELECT
  f.interval_time,
  f.pair,
  f.feature_value,
  CORR(f.feature_value, t.d_w45_h15) OVER w as corr_w45_h15,
  CORR(f.feature_value, t.d_w45_h30) OVER w as corr_w45_h30,
  CORR(f.feature_value, t.d_w45_h45) OVER w as corr_w45_h45,
  CORR(f.feature_value, t.d_w45_h60) OVER w as corr_w45_h60,
  CORR(f.feature_value, t.d_w45_h75) OVER w as corr_w45_h75,
  CORR(f.feature_value, t.d_w45_h90) OVER w as corr_w45_h90,
  CORR(f.feature_value, t.d_w45_h105) OVER w as corr_w45_h105,
  CORR(f.feature_value, t.d_w90_h15) OVER w as corr_w90_h15,
  CORR(f.feature_value, t.d_w90_h30) OVER w as corr_w90_h30,
  CORR(f.feature_value, t.d_w90_h45) OVER w as corr_w90_h45,
  CORR(f.feature_value, t.d_w90_h60) OVER w as corr_w90_h60,
  CORR(f.feature_value, t.d_w90_h75) OVER w as corr_w90_h75,
  CORR(f.feature_value, t.d_w90_h90) OVER w as corr_w90_h90,
  CORR(f.feature_value, t.d_w90_h105) OVER w as corr_w90_h105,
  CORR(f.feature_value, t.d_w180_h15) OVER w as corr_w180_h15,
  CORR(f.feature_value, t.d_w180_h30) OVER w as corr_w180_h30,
  CORR(f.feature_value, t.d_w180_h45) OVER w as corr_w180_h45,
  CORR(f.feature_value, t.d_w180_h60) OVER w as corr_w180_h60,
  CORR(f.feature_value, t.d_w180_h75) OVER w as corr_w180_h75,
  CORR(f.feature_value, t.d_w180_h90) OVER w as corr_w180_h90,
  CORR(f.feature_value, t.d_w180_h105) OVER w as corr_w180_h105,
  CORR(f.feature_value, t.d_w360_h15) OVER w as corr_w360_h15,
  CORR(f.feature_value, t.d_w360_h30) OVER w as corr_w360_h30,
  CORR(f.feature_value, t.d_w360_h45) OVER w as corr_w360_h45,
  CORR(f.feature_value, t.d_w360_h60) OVER w as corr_w360_h60,
  CORR(f.feature_value, t.d_w360_h75) OVER w as corr_w360_h75,
  CORR(f.feature_value, t.d_w360_h90) OVER w as corr_w360_h90,
  CORR(f.feature_value, t.d_w360_h105) OVER w as corr_w360_h105,
  CORR(f.feature_value, t.d_w720_h15) OVER w as corr_w720_h15,
  CORR(f.feature_value, t.d_w720_h30) OVER w as corr_w720_h30,
  CORR(f.feature_value, t.d_w720_h45) OVER w as corr_w720_h45,
  CORR(f.feature_value, t.d_w720_h60) OVER w as corr_w720_h60,
  CORR(f.feature_value, t.d_w720_h75) OVER w as corr_w720_h75,
  CORR(f.feature_value, t.d_w720_h90) OVER w as corr_w720_h90,
  CORR(f.feature_value, t.d_w720_h105) OVER w as corr_w720_h105,
  CORR(f.feature_value, t.d_w1440_h15) OVER w as corr_w1440_h15,
  CORR(f.feature_value, t.d_w1440_h30) OVER w as corr_w1440_h30,
  CORR(f.feature_value, t.d_w1440_h45) OVER w as corr_w1440_h45,
  CORR(f.feature_value, t.d_w1440_h60) OVER w as corr_w1440_h60,
  CORR(f.feature_value, t.d_w1440_h75) OVER w as corr_w1440_h75,
  CORR(f.feature_value, t.d_w1440_h90) OVER w as corr_w1440_h90,
  CORR(f.feature_value, t.d_w1440_h105) OVER w as corr_w1440_h105,
  CORR(f.feature_value, t.d_w2880_h15) OVER w as corr_w2880_h15,
  CORR(f.feature_value, t.d_w2880_h30) OVER w as corr_w2880_h30,
  CORR(f.feature_value, t.d_w2880_h45) OVER w as corr_w2880_h45,
  CORR(f.feature_value, t.d_w2880_h60) OVER w as corr_w2880_h60,
  CORR(f.feature_value, t.d_w2880_h75) OVER w as corr_w2880_h75,
  CORR(f.feature_value, t.d_w2880_h90) OVER w as corr_w2880_h90,
  CORR(f.feature_value, t.d_w2880_h105) OVER w as corr_w2880_h105
FROM feature_data f
JOIN target_data t ON f.interval_time = t.interval_time
WINDOW w AS (ORDER BY f.interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW)
ORDER BY f.interval_time;
"""


def execute_query(args):
    """Execute a single BigQuery query."""
    source_table, feature_column, output_table = args
    sql = get_sql_template(source_table, feature_column, output_table)

    cmd = [
        "bq", "--location", LOCATION, "query",
        "--use_legacy_sql=false",
        "--max_rows=0",
        sql
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            return (output_table, "SUCCESS", None)
        else:
            return (output_table, "FAILED", result.stderr)
    except subprocess.TimeoutExpired:
        return (output_table, "TIMEOUT", "Query exceeded 10 minute timeout")
    except Exception as e:
        return (output_table, "ERROR", str(e))


def main():
    """Main execution."""
    # Build task list
    tasks = []
    for source_table, features in FEATURE_INVENTORY.items():
        for feature in features:
            # Generate output table name
            variant = "bqx" if "_bqx_" in source_table or source_table.endswith("_bqx") else "idx"
            output_table = f"ftcorr_{variant}_{feature}_eurusd"
            tasks.append((source_table, feature, output_table))

    print(f"Total tasks: {len(tasks)}")
    print(f"Max workers: {MAX_WORKERS}")
    print("-" * 60)

    # Execute with parallel workers
    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(execute_query, task): task for task in tasks}

        for future in as_completed(futures):
            output_table, status, error = future.result()
            completed += 1

            if status == "SUCCESS":
                print(f"[{completed}/{len(tasks)}] SUCCESS: {output_table}")
            else:
                failed += 1
                print(f"[{completed}/{len(tasks)}] {status}: {output_table}")
                if error:
                    print(f"  Error: {error[:200]}")

    print("-" * 60)
    print(f"Completed: {completed - failed}/{len(tasks)}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
```

---

## PARALLEL WORKER ALLOCATION

| Phase | Feature Types | Features | Workers | Est. Time |
|-------|---------------|----------|---------|-----------|
| C4 | AGG | 126 | 4 | 30 min |
| C5 | REG | 140 | 4 | 35 min |
| C6 | MOM | 84 | 4 | 20 min |
| C7 | ALIGN | 82 | 4 | 20 min |
| C8 | VOL | 60 | 4 | 15 min |
| C9 | DER/DIV/MRT/REV/EXT | 98 | 8 | 25 min |
| C10 | LAG/REGIME/TMP/CYC/BASE | 147 | 8 | 35 min |
| **TOTAL** | | **737** | | **~3 hours** |

---

## VALIDATION REQUIREMENTS

After each phase:

1. **Table Count**: Verify expected tables created
2. **Row Count**: ~2.16M rows per table
3. **Column Count**: 52 columns (interval_time, pair, feature_value, 49 correlations)
4. **Null Rate**: < 5% per correlation column

```sql
-- Validation query
SELECT
  table_name,
  row_count
FROM `bqx-ml.bqx_ml_v3_analytics.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_name LIKE 'ftcorr_%'
ORDER BY table_name;
```

---

## AUTHORIZATION

**APPROVED** for immediate parallel implementation.

Execute phases C4-C10 using the provided Python script with 4-8 workers per phase.

---

*Directive issued: 2025-11-29 20:00 UTC*
*Chief Engineer, BQX ML V3*
