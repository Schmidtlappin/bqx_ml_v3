# Correlation Remediation Plan

## Problem Statement
Current correlations are incomplete compared to the original `correlation_matrix_817x72.csv`:

| Gap | Current | Required |
|-----|---------|----------|
| **BQX Windows** | 1 (bqx45 only) | 7 (bqx45, bqx90, bqx180, bqx360, bqx720, bqx1440, bqx2880) |
| **Feature Tables** | 2 (reg, reg_bqx) | 20+ table types |
| **Correlation Columns** | 7 | 49 (7 windows × 7 horizons) |

---

## Feature Table Inventory

### Core Tables (28 pairs each, IDX + BQX variants)

| Table Type | IDX Variant | BQX Variant | Features (est.) |
|------------|-------------|-------------|-----------------|
| reg | reg_{pair} | reg_bqx_{pair} | ~231 |
| agg | agg_{pair} | agg_bqx_{pair} | ~50 |
| mom | mom_{pair} | mom_bqx_{pair} | ~40 |
| der | der_{pair} | der_bqx_{pair} | ~30 |
| vol | vol_{pair} | vol_bqx_{pair} | ~30 |
| align | align_{pair} | align_bqx_{pair} | ~40 |
| div | div_{pair} | div_bqx_{pair} | ~20 |
| mrt | mrt_{pair} | mrt_bqx_{pair} | ~20 |
| rev | rev_{pair} | rev_bqx_{pair} | ~20 |
| cyc | - | cyc_bqx_{pair} | ~20 |
| ext | - | ext_bqx_{pair} | ~20 |

**Total estimated features**: ~500+ per pair × 2 variants = ~1,000 feature-variant combinations

---

## Phase 1: Expand BQX Windows (HIGH PRIORITY)

**Objective**: Add correlations for all 7 BQX target windows, not just bqx45.

### Targets to Add
- `target_bqx90_h{15,30,45,60,75,90,105}` - 7 correlations
- `target_bqx180_h{15,30,45,60,75,90,105}` - 7 correlations
- `target_bqx360_h{15,30,45,60,75,90,105}` - 7 correlations
- `target_bqx720_h{15,30,45,60,75,90,105}` - 7 correlations
- `target_bqx1440_h{15,30,45,60,75,90,105}` - 7 correlations
- `target_bqx2880_h{15,30,45,60,75,90,105}` - 7 correlations

### Output Schema
```
feature_id, pair, feature_name, variant, n_samples,
corr_w45_h15, corr_w45_h30, ..., corr_w45_h105,   (7 cols)
corr_w90_h15, corr_w90_h30, ..., corr_w90_h105,   (7 cols)
corr_w180_h15, ..., corr_w180_h105,               (7 cols)
corr_w360_h15, ..., corr_w360_h105,               (7 cols)
corr_w720_h15, ..., corr_w720_h105,               (7 cols)
corr_w1440_h15, ..., corr_w1440_h105,             (7 cols)
corr_w2880_h15, ..., corr_w2880_h105,             (7 cols)
avg_w45, avg_w90, avg_w180, avg_w360, avg_w720, avg_w1440, avg_w2880,
max_abs_corr
```

### Estimated Time
- 56 pair-variants × 7 windows = ~30s × 7 = ~3.5 hours
- Can parallelize by window

---

## Phase 2: Add Additional Feature Tables

**Objective**: Include all major feature table types beyond reg_.

### Feature Tables to Add (Priority Order)

#### Tier 1 (High Priority)
1. **agg / agg_bqx** - Aggregation features
2. **mom / mom_bqx** - Momentum features
3. **der / der_bqx** - Derivative features

#### Tier 2 (Medium Priority)
4. **vol / vol_bqx** - Volatility features
5. **align / align_bqx** - Alignment features
6. **div / div_bqx** - Divergence features

#### Tier 3 (Lower Priority)
7. **mrt / mrt_bqx** - Mean reversion features
8. **rev / rev_bqx** - Reversal features
9. **cyc_bqx** - Cycle features (BQX only)
10. **ext_bqx** - Extreme features (BQX only)

### Estimated Time per Table Type
- ~30 min per table type × 10 types = ~5 hours

---

## Phase 3: Create Unified Correlation Matrix

**Objective**: Merge all correlations into comprehensive matrix matching original format.

### Output Tables
1. `feature_correlations_full_7windows` - Full dataset, all windows
2. `feature_correlations_extreme_7windows` - Extreme 20%, all windows
3. `feature_correlation_matrix_complete` - Combined export

### CSV Export Format
Match original `correlation_matrix_817x72.csv` format with 72 columns.

---

## Phase 4: Create Comparison Analysis

**Objective**: Compare extreme vs full correlations across all windows.

### Deliverables
1. Per-window extreme vs full comparison
2. Feature rankings by window
3. Identification of window-specific predictors

---

## Execution Order

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1A | Expand reg_ tables to 7 windows (full dataset) | ~2 hours | None |
| 1B | Expand reg_ tables to 7 windows (extreme 20%) | ~1.5 hours | None |
| 2A | Add agg, mom, der tables (full dataset) | ~2 hours | Phase 1A |
| 2B | Add agg, mom, der tables (extreme 20%) | ~1.5 hours | Phase 1B |
| 3 | Create unified matrix and CSV exports | ~30 min | Phases 1-2 |
| 4 | Generate comparison analysis | ~30 min | Phase 3 |

**Total Estimated Time**: ~8 hours

---

## Key Deliverables

1. **`feature_correlations_full_7windows`** - ~90K rows (all features × all windows)
2. **`feature_correlations_extreme_7windows`** - ~90K rows
3. **`correlation_matrix_full_7windows.csv`** - Complete 72-column matrix
4. **`correlation_matrix_extreme_7windows.csv`** - Complete 72-column matrix
5. **`extreme_vs_full_7windows_comparison`** - Window-specific analysis

---

## Expected Outcomes

After remediation:
- Correlations will include 0.99+ values (from w2880 window)
- Feature coverage expands from ~231 to ~500+ per pair
- Direct comparison with original `correlation_matrix_817x72.csv` possible
- Extreme vs full analysis across all BQX windows

---

## Ready for Execution?

Confirm to proceed with Phase 1A (expand to 7 windows for full dataset).
