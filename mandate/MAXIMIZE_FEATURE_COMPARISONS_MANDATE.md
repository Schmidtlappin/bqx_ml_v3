# MAXIMIZE FEATURE COMPARISONS MANDATE

**Mandate ID**: BQX-ML-M006
**Status**: ACTIVE
**Priority**: P0-CRITICAL
**Issued**: December 13, 2025 03:30 UTC
**Authority**: User (System Architect)
**Scope**: ALL cross-entity relationship tables (TRI, COV, VAR)
**Supersedes**: None (Extends BQX-ML-M005)
**Related Mandates**:
- BQX-ML-M005: Regression Feature Architecture Mandate
- BQX-ML-M001: Feature Ledger 100% Coverage Mandate
- BQX-ML-M002: BQX ML V3 Feature Inventory

---

## MANDATE STATEMENT

**User mandates that**:

The system SHALL maximize feature-to-feature comparisons across **ALL pairs**, **ALL windows**, and **ALL feature types** while maintaining **strict variant separation** (IDX and BQX NEVER intermix).

**Maximization Dimensions**:
1. ✅ **Pairs**: ALL 28 currency pairs participate in comparisons
2. ✅ **Windows**: ALL 7 windows [45, 90, 180, 360, 720, 1440, 2880] used in calculations
3. ✅ **Feature Types**: ALL available feature types included in comparisons
4. ✅ **Comparisons**: Maximum valid combinations (COV all pairs, TRI all triangles, VAR all currencies)
5. ❌ **Variants**: BQX and IDX remain separate universes (NO cross-contamination)

---

## ARCHITECTURAL PRINCIPLES

### Principle 1: **Maximum Coverage Across Dimensions**

**Pairs**: Use ALL 28 pairs in comparison calculations
- COV: C(28,2) = 378 pair combinations
- TRI: All valid 3-currency triangles (56-84 triangles)
- VAR: All 8 major currencies + cross-family comparisons

**Windows**: Use ALL 7 temporal windows
- Current: Only 2 windows (45, 180) used in base features
- Mandated: All 7 windows for spread/error statistics
- Extended: Cross-window divergence and alignment features

**Feature Types**: Include ALL feature table types in comparisons
- Current: 2 types (agg, align)
- Mandated: +1 type (reg - regression features)
- Extended: +5 types (mom, vol, der, rev, mrt)

### Principle 2: **Perfect Variant Symmetry**

**BQX Universe**: Momentum-based features (bqx_45 oscillator)
- All comparisons use ONLY BQX-sourced data
- Table naming: `cov_agg_bqx_eurusd_gbpusd`

**IDX Universe**: Price-based features (close_idx)
- All comparisons use ONLY IDX-sourced data
- Table naming: `cov_agg_idx_eurusd_gbpusd`

**Invariant**: `count(pattern='*_bqx_*') == count(pattern='*_idx_*')`

**Rationale**: BQX and IDX measure fundamentally different properties. Mixing them creates meaningless comparisons (like comparing temperature to pressure).

### Principle 3: **Multi-Level Feature Hierarchy**

```
Level 0: Raw Data (OHLC, timestamps)
  ↓
Level 1: Pair-Level Features (agg, mom, vol, reg, align, der, rev, mrt)
  ↓
Level 2: Pair-to-Pair Comparisons (COV - 378 combinations)
  ↓
Level 3A: Triangle Arbitrage (TRI - 70+ triangles)
Level 3B: Currency Family Aggregates (VAR - 8 families + 28 cross-family)
  ↓
Level 4: Cross-Window & Cross-Feature Analytics (NEW)
```

Each level builds on previous levels, creating exponentially richer feature interactions.

---

## PHASE 1: MANDATE COMPLIANCE (IMMEDIATE)

### Objective: Achieve BQX-ML-M005 Compliance

**Scope**: Add regression features to TRI/COV/VAR tables

**Implementation**:

#### COV Tables Schema (14 → 98 columns)

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.cov_{variant}_{source_variant}_{pair1}_{pair2}`
PARTITION BY DATE(interval_time)
CLUSTER BY pair1
AS
WITH
  all_intervals AS (
    SELECT DISTINCT interval_time
    FROM `bqx-ml.bqx_ml_v3_features_v2.base_{source_variant}_{pair1}`
    UNION DISTINCT
    SELECT DISTINCT interval_time
    FROM `bqx-ml.bqx_ml_v3_features_v2.base_{source_variant}_{pair2}`
  ),
  pair1_data AS (
    SELECT interval_time, {value_col} as val1
    FROM `bqx-ml.bqx_ml_v3_features_v2.base_{source_variant}_{pair1}`
  ),
  pair2_data AS (
    SELECT interval_time, {value_col} as val2
    FROM `bqx-ml.bqx_ml_v3_features_v2.base_{source_variant}_{pair2}`
  ),
  -- **NEW: Regression features from both pairs**
  pair1_reg AS (
    SELECT
      interval_time,
      reg_lin_term_45, reg_lin_term_90, reg_lin_term_180, reg_lin_term_360,
      reg_lin_term_720, reg_lin_term_1440, reg_lin_term_2880,
      reg_quad_term_45, reg_quad_term_90, reg_quad_term_180, reg_quad_term_360,
      reg_quad_term_720, reg_quad_term_1440, reg_quad_term_2880,
      reg_residual_45, reg_residual_90, reg_residual_180, reg_residual_360,
      reg_residual_720, reg_residual_1440, reg_residual_2880
    FROM `bqx-ml.bqx_ml_v3_features_v2.reg_{source_variant}_{pair1}`
  ),
  pair2_reg AS (
    SELECT
      interval_time,
      reg_lin_term_45, reg_lin_term_90, reg_lin_term_180, reg_lin_term_360,
      reg_lin_term_720, reg_lin_term_1440, reg_lin_term_2880,
      reg_quad_term_45, reg_quad_term_90, reg_quad_term_180, reg_quad_term_360,
      reg_quad_term_720, reg_quad_term_1440, reg_quad_term_2880,
      reg_residual_45, reg_residual_90, reg_residual_180, reg_residual_360,
      reg_residual_720, reg_residual_1440, reg_residual_2880
    FROM `bqx-ml.bqx_ml_v3_features_v2.reg_{source_variant}_{pair2}`
  ),
  combined_data AS (
    SELECT
      ai.interval_time,
      p1.val1,
      p2.val2,
      p1.val1 - p2.val2 as spread,
      SAFE_DIVIDE(p1.val1, p2.val2) as ratio,
      IF(SIGN(p1.val1) = SIGN(p2.val2), 1, 0) as sign_agreement
    FROM all_intervals ai
    LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
    LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
  )
SELECT
  cd.interval_time,
  '{pair1}' as pair1,
  '{pair2}' as pair2,

  -- Base features (14 columns)
  cd.val1,
  cd.val2,
  cd.spread,
  cd.ratio,
  AVG(cd.spread) OVER w45 as spread_ma_45,
  AVG(cd.spread) OVER w180 as spread_ma_180,
  STDDEV(cd.spread) OVER w45 as spread_std_45,
  SAFE_DIVIDE(
    cd.spread - AVG(cd.spread) OVER w180,
    NULLIF(STDDEV(cd.spread) OVER w180, 0)
  ) as spread_zscore,
  cd.sign_agreement,
  AVG(cd.sign_agreement) OVER w45 as rolling_agreement_45,
  IF(ABS(SAFE_DIVIDE(
    cd.spread - AVG(cd.spread) OVER w180,
    NULLIF(STDDEV(cd.spread) OVER w180, 0)
  )) > 2, 1, 0) as mean_reversion_signal,

  -- **PHASE 1: Pair 1 regression features (21 columns)**
  p1r.reg_lin_term_45 as pair1_lin_term_45,
  p1r.reg_lin_term_90 as pair1_lin_term_90,
  p1r.reg_lin_term_180 as pair1_lin_term_180,
  p1r.reg_lin_term_360 as pair1_lin_term_360,
  p1r.reg_lin_term_720 as pair1_lin_term_720,
  p1r.reg_lin_term_1440 as pair1_lin_term_1440,
  p1r.reg_lin_term_2880 as pair1_lin_term_2880,

  p1r.reg_quad_term_45 as pair1_quad_term_45,
  p1r.reg_quad_term_90 as pair1_quad_term_90,
  p1r.reg_quad_term_180 as pair1_quad_term_180,
  p1r.reg_quad_term_360 as pair1_quad_term_360,
  p1r.reg_quad_term_720 as pair1_quad_term_720,
  p1r.reg_quad_term_1440 as pair1_quad_term_1440,
  p1r.reg_quad_term_2880 as pair1_quad_term_2880,

  p1r.reg_residual_45 as pair1_residual_45,
  p1r.reg_residual_90 as pair1_residual_90,
  p1r.reg_residual_180 as pair1_residual_180,
  p1r.reg_residual_360 as pair1_residual_360,
  p1r.reg_residual_720 as pair1_residual_720,
  p1r.reg_residual_1440 as pair1_residual_1440,
  p1r.reg_residual_2880 as pair1_residual_2880,

  -- **PHASE 1: Pair 2 regression features (21 columns)**
  p2r.reg_lin_term_45 as pair2_lin_term_45,
  p2r.reg_lin_term_90 as pair2_lin_term_90,
  p2r.reg_lin_term_180 as pair2_lin_term_180,
  p2r.reg_lin_term_360 as pair2_lin_term_360,
  p2r.reg_lin_term_720 as pair2_lin_term_720,
  p2r.reg_lin_term_1440 as pair2_lin_term_1440,
  p2r.reg_lin_term_2880 as pair2_lin_term_2880,

  p2r.reg_quad_term_45 as pair2_quad_term_45,
  p2r.reg_quad_term_90 as pair2_quad_term_90,
  p2r.reg_quad_term_180 as pair2_quad_term_180,
  p2r.reg_quad_term_360 as pair2_quad_term_360,
  p2r.reg_quad_term_720 as pair2_quad_term_720,
  p2r.reg_quad_term_1440 as pair2_quad_term_1440,
  p2r.reg_quad_term_2880 as pair2_quad_term_2880,

  p2r.reg_residual_45 as pair2_residual_45,
  p2r.reg_residual_90 as pair2_residual_90,
  p2r.reg_residual_180 as pair2_residual_180,
  p2r.reg_residual_360 as pair2_residual_360,
  p2r.reg_residual_720 as pair2_residual_720,
  p2r.reg_residual_1440 as pair2_residual_1440,
  p2r.reg_residual_2880 as pair2_residual_2880,

  -- **PHASE 2 PREVIEW: Cross-window divergence (6 columns)**
  p1r.reg_lin_term_45 - p1r.reg_lin_term_180 as pair1_short_medium_divergence,
  p1r.reg_lin_term_180 - p1r.reg_lin_term_1440 as pair1_medium_long_divergence,
  p2r.reg_lin_term_45 - p2r.reg_lin_term_180 as pair2_short_medium_divergence,
  p2r.reg_lin_term_180 - p2r.reg_lin_term_1440 as pair2_medium_long_divergence,

  -- Cross-pair momentum divergence
  p1r.reg_lin_term_45 - p2r.reg_lin_term_45 as pair_momentum_divergence_45,
  p1r.reg_lin_term_1440 - p2r.reg_lin_term_1440 as pair_momentum_divergence_1440

FROM combined_data cd
LEFT JOIN pair1_reg p1r ON cd.interval_time = p1r.interval_time
LEFT JOIN pair2_reg p2r ON cd.interval_time = p2r.interval_time
WINDOW
  w45 AS (ORDER BY cd.interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
  w180 AS (ORDER BY cd.interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
```

**Phase 1 Column Count**:
- Base: 14 columns
- Pair 1 regression: 21 columns
- Pair 2 regression: 21 columns
- Cross-window preview: 6 columns
- **Total: 62 columns** (interim, before full Phase 2)

#### TRI Tables Schema (15 → 108 columns)

Similar pattern: Add 63 regression columns (3 pairs × 21 features)

#### VAR Tables Schema (14 → 35 columns)

Similar pattern: Add 21 aggregated regression columns

**Phase 1 Deliverables**:
- ✅ 1,616 tables (no count change)
- ✅ COV: 14 → 62 columns (interim)
- ✅ TRI: 15 → 84 columns (interim)
- ✅ VAR: 14 → 35 columns (complete for Phase 1)
- ✅ BQX-ML-M005 compliant

---

## PHASE 2: WINDOW EXPANSION

### Objective: Expand base features to all 7 windows

**Current**: Only w45 and w180 used in spread/error calculations

**Mandated**: All 7 windows [45, 90, 180, 360, 720, 1440, 2880]

**Implementation**:

```sql
-- Expand spread statistics to all windows
AVG(cd.spread) OVER w45 as spread_ma_45,
AVG(cd.spread) OVER w90 as spread_ma_90,
AVG(cd.spread) OVER w180 as spread_ma_180,
AVG(cd.spread) OVER w360 as spread_ma_360,
AVG(cd.spread) OVER w720 as spread_ma_720,
AVG(cd.spread) OVER w1440 as spread_ma_1440,
AVG(cd.spread) OVER w2880 as spread_ma_2880,

STDDEV(cd.spread) OVER w45 as spread_std_45,
STDDEV(cd.spread) OVER w90 as spread_std_90,
STDDEV(cd.spread) OVER w180 as spread_std_180,
STDDEV(cd.spread) OVER w360 as spread_std_360,
STDDEV(cd.spread) OVER w720 as spread_std_720,
STDDEV(cd.spread) OVER w1440 as spread_std_1440,
STDDEV(cd.spread) OVER w2880 as spread_std_2880,

-- Z-score for each window
SAFE_DIVIDE(
  cd.spread - AVG(cd.spread) OVER w45,
  NULLIF(STDDEV(cd.spread) OVER w45, 0)
) as spread_zscore_45,
...(repeat for all 7 windows)...

-- Window definitions
WINDOW
  w45 AS (ORDER BY interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
  w90 AS (ORDER BY interval_time ROWS BETWEEN 89 PRECEDING AND CURRENT ROW),
  w180 AS (ORDER BY interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW),
  w360 AS (ORDER BY interval_time ROWS BETWEEN 359 PRECEDING AND CURRENT ROW),
  w720 AS (ORDER BY interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW),
  w1440 AS (ORDER BY interval_time ROWS BETWEEN 1439 PRECEDING AND CURRENT ROW),
  w2880 AS (ORDER BY interval_time ROWS BETWEEN 2879 PRECEDING AND CURRENT ROW)
```

**Additional Features**:

```sql
-- Multi-timeframe trend alignment score
(
  CASE WHEN AVG(cd.spread) OVER w45 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w90 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w180 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w360 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w720 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w1440 > 0 THEN 1 ELSE -1 END +
  CASE WHEN AVG(cd.spread) OVER w2880 > 0 THEN 1 ELSE -1 END
) / 7.0 as spread_trend_alignment,

-- Volatility regime (short vs long)
SAFE_DIVIDE(
  STDDEV(cd.spread) OVER w45,
  NULLIF(STDDEV(cd.spread) OVER w1440, 0)
) as spread_volatility_regime,

-- Cross-window momentum
AVG(cd.spread) OVER w45 - AVG(cd.spread) OVER w180 as spread_short_medium_momentum,
AVG(cd.spread) OVER w180 - AVG(cd.spread) OVER w1440 as spread_medium_long_momentum
```

**Phase 2 Column Additions**:
- COV: +42 columns (7 windows × 3 metrics × 2 pairs)
- TRI: +42 columns (similar expansion for error statistics)
- **COV Total: 62 → 104 columns**
- **TRI Total: 84 → 126 columns**

---

## PHASE 3: FEATURE TYPE EXPANSION

### Objective: Add comparisons for ALL feature types

**Current Feature Types in Comparisons**: 2 (agg, align)

**Expanded Feature Types**: 8 total

1. **agg** (aggregation) - mean, std, min, max, range
2. **align** (alignment) - direction, position, zscore
3. **reg** (regression) - lin_term, quad_term, residual [MANDATORY]
4. **mom** (momentum) - roc, acceleration, persistence
5. **vol** (volatility) - atr, realized_vol, bollinger
6. **der** (derivative) - velocity, acceleration
7. **rev** (reversal) - reversal patterns
8. **mrt** (mean reversion) - tension, z-scores

**Implementation Strategy**:

Create variant-specific comparison tables:

```bash
# COV tables by feature type
cov_agg_{source_variant}_{pair1}_{pair2}   # Aggregation comparison
cov_align_{source_variant}_{pair1}_{pair2} # Alignment comparison
cov_reg_{source_variant}_{pair1}_{pair2}   # Regression comparison (NEW)
cov_mom_{source_variant}_{pair1}_{pair2}   # Momentum comparison (NEW)
cov_vol_{source_variant}_{pair1}_{pair2}   # Volatility comparison (NEW)
cov_der_{source_variant}_{pair1}_{pair2}   # Derivative comparison (NEW)
cov_rev_{source_variant}_{pair1}_{pair2}   # Reversal comparison (NEW)
cov_mrt_{source_variant}_{pair1}_{pair2}   # Mean reversion comparison (NEW)
```

**Example: Momentum Comparison Table**

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.cov_mom_{source_variant}_{pair1}_{pair2}`
AS
WITH
  pair1_mom AS (
    SELECT
      interval_time,
      mom_roc_45, mom_roc_90, ..., mom_roc_2880,
      mom_acceleration_45, ..., mom_acceleration_2880,
      mom_persistence_45, ..., mom_persistence_2880
    FROM `bqx-ml.bqx_ml_v3_features_v2.mom_{source_variant}_{pair1}`
  ),
  pair2_mom AS (
    SELECT
      interval_time,
      mom_roc_45, mom_roc_90, ..., mom_roc_2880,
      mom_acceleration_45, ..., mom_acceleration_2880,
      mom_persistence_45, ..., mom_persistence_2880
    FROM `bqx-ml.bqx_ml_v3_features_v2.mom_{source_variant}_{pair2}`
  )
SELECT
  p1.interval_time,
  '{pair1}' as pair1,
  '{pair2}' as pair2,

  -- Pair 1 momentum features (21 columns)
  p1.mom_roc_45 as pair1_roc_45,
  p1.mom_roc_90 as pair1_roc_90,
  ...(all windows)...,

  -- Pair 2 momentum features (21 columns)
  p2.mom_roc_45 as pair2_roc_45,
  ...(all windows)...,

  -- Momentum divergence (7 columns)
  p1.mom_roc_45 - p2.mom_roc_45 as roc_divergence_45,
  ...(all windows)...,

  -- Momentum correlation (rolling)
  CORR(p1.mom_roc_45, p2.mom_roc_45) OVER w180 as roc_correlation_45

FROM pair1_mom p1
JOIN pair2_mom p2 ON p1.interval_time = p2.interval_time
WINDOW w180 AS (ORDER BY p1.interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
```

**Phase 3 Table Count Impact**:
- **COV**: 1,512 → 6,048 tables (378 combos × 8 variants × 2 source_variants)
- **TRI**: 72 → 288 tables (18 triangles × 8 variants × 2 source_variants)
- **Total**: 1,616 → 6,336 tables

---

## PHASE 4: TRIANGLE EXPANSION

### Objective: Enumerate ALL valid currency triangles

**Current**: 18 manually defined triangles

**Maximized**: Programmatically generated valid triangles

**Triangle Validation Rules**:
1. Three distinct currencies form a closed loop
2. All three constituent pairs exist in the dataset
3. FX market conventions respected (pair direction)
4. No redundant triangles (EUR-USD-GBP ≡ USD-GBP-EUR)

**Triangle Generation Algorithm**:

```python
def generate_all_valid_triangles():
    """Generate all valid triangular arbitrage combinations."""

    currencies = {'eur', 'gbp', 'usd', 'jpy', 'aud', 'cad', 'chf', 'nzd'}
    valid_pairs = get_all_existing_pairs()  # Query BigQuery for existing pairs

    triangles = set()

    for curr1 in currencies:
        for curr2 in currencies:
            for curr3 in currencies:
                if len({curr1, curr2, curr3}) != 3:
                    continue  # Skip if not 3 distinct currencies

                # Check if all three pairs exist
                pair1 = find_existing_pair(curr1, curr2, valid_pairs)
                pair2 = find_existing_pair(curr2, curr3, valid_pairs)
                pair3 = find_existing_pair(curr1, curr3, valid_pairs)

                if pair1 and pair2 and pair3:
                    # Normalize to canonical form (alphabetical order)
                    triangle = tuple(sorted([curr1, curr2, curr3]))
                    triangles.add(triangle)

    return list(triangles)

# Expected result: 56-84 valid triangles (vs current 18)
```

**New Triangle Categories**:

1. **Major Triangles** (current 18):
   - EUR-USD-GBP, EUR-USD-JPY, GBP-USD-JPY, etc.

2. **Commodity Currency Triangles** (NEW):
   - AUD-CAD-NZD
   - AUD-CAD-USD
   - NZD-CAD-USD

3. **European Triangles** (NEW):
   - EUR-CHF-GBP
   - EUR-GBP-NOK (if NOK data available)

4. **Safe Haven Triangles** (NEW):
   - JPY-CHF-USD
   - JPY-CHF-EUR

5. **Cross-Regional Triangles** (NEW):
   - AUD-JPY-NZD
   - CAD-JPY-CHF

**Phase 4 Table Count Impact**:
- **TRI (Phase 3)**: 288 tables (18 triangles × 8 variants × 2 source)
- **TRI (Phase 4)**: 1,120 tables (70 triangles × 8 variants × 2 source)
- **Additional**: +832 tables

---

## PHASE 5: CROSS-FAMILY COMPARISONS

### Objective: Currency family vs currency family comparisons

**Current VAR Tables**: 32 tables (8 currencies × 2 variants × 2 source_variants)

**Extended**: Add cross-family comparison tables

**Family Comparison Logic**:

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.var_family_cov_{variant}_{source_variant}_{curr1}_{curr2}`
AS
SELECT
  v1.interval_time,
  '{curr1}' as family1,
  '{curr2}' as family2,

  -- Family 1 aggregates
  v1.family_lin_term_45 as family1_lin_term_45,
  v1.family_quad_term_45 as family1_quad_term_45,
  v1.family_residual_45 as family1_residual_45,
  ...(all windows)...,

  -- Family 2 aggregates
  v2.family_lin_term_45 as family2_lin_term_45,
  v2.family_quad_term_45 as family2_quad_term_45,
  v2.family_residual_45 as family2_residual_45,
  ...(all windows)...,

  -- Cross-family divergence
  v1.family_lin_term_45 - v2.family_lin_term_45 as momentum_divergence_45,
  v1.family_quad_term_45 - v2.family_quad_term_45 as acceleration_divergence_45,

  -- Relative strength
  SAFE_DIVIDE(
    v1.family_lin_term_45,
    NULLIF(v2.family_lin_term_45, 0)
  ) as relative_strength_45,

  -- Correlation
  CORR(v1.family_lin_term_45, v2.family_lin_term_45) OVER w180 as momentum_correlation

FROM `bqx-ml.bqx_ml_v3_features_v2.var_{variant}_{source_variant}_{curr1}` v1
JOIN `bqx-ml.bqx_ml_v3_features_v2.var_{variant}_{source_variant}_{curr2}` v2
  ON v1.interval_time = v2.interval_time
WINDOW w180 AS (ORDER BY v1.interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW)
```

**Cross-Family Combinations**:
- EUR vs USD
- EUR vs GBP
- EUR vs JPY
- USD vs JPY
- USD vs AUD
- GBP vs JPY
- AUD vs NZD
- CAD vs CHF
- ...(all C(8,2) = 28 combinations)

**Phase 5 Table Count Impact**:
- **VAR (current)**: 32 tables
- **VAR (Phase 5)**: 32 + 112 = 144 tables
  - Base: 32 (8 currencies × 2 variants × 2 source)
  - Cross-family: 28 combos × 2 variants × 2 source = 112
- **Additional**: +112 tables

---

## COMPLETE MAXIMIZATION SUMMARY

### Table Count Evolution

| Phase | COV | TRI | VAR | Total | Description |
|-------|-----|-----|-----|-------|-------------|
| **Current** | 1,512 | 72 | 32 | **1,616** | Baseline |
| **Phase 1** | 1,512 | 72 | 32 | **1,616** | +Regression (BQX-ML-M005) |
| **Phase 2** | 1,512 | 72 | 32 | **1,616** | +All windows (columns only) |
| **Phase 3** | 6,048 | 288 | 32 | **6,368** | +6 feature type variants |
| **Phase 4** | 6,048 | 1,120 | 32 | **7,200** | +52 triangles |
| **Phase 5** | 6,048 | 1,120 | 144 | **7,312** | +28 cross-family |

### Column Count Evolution (Example: COV)

| Phase | Columns | Description |
|-------|---------|-------------|
| **Current** | 14 | Base spread/ratio features |
| **Phase 1** | 62 | +42 regression, +6 cross-window |
| **Phase 2** | 104 | +42 all-window expansions |
| **Phase 3** | 104 | (Applies to new variant tables) |
| **Phase 4** | 104 | (No column change) |
| **Phase 5** | 104 | (No column change) |

### Feature Universe Impact

| Metric | Current | Phase 1 | Phase 5 |
|--------|---------|---------|---------|
| **Total Tables** | 4,888 | 4,888 | 10,584 |
| **Comparison Tables** | 1,616 | 1,616 | 7,312 |
| **Unique Features per Pair** | 1,064 | 1,127 | 2,450+ |
| **Feature Columns (EURUSD)** | 11,337 | 11,548 | 24,800+ |
| **Storage (est.)** | 1,610 GB | 1,750 GB | 3,200 GB |

---

## COST & TIMELINE ESTIMATES

### Phase 1: BQX-ML-M005 Compliance

**Timeline**: 18-24 hours
- Script refactoring: 12-16 hours
- Testing: 3-4 hours
- Generation: 3-4 hours (parallel execution)

**Cost**: $150-200
- BigQuery processing: $140-180
- Storage: $10-20

### Phase 2: Window Expansion

**Timeline**: 8-12 hours
- Script updates: 4-6 hours
- Testing: 2-3 hours
- Regeneration: 2-3 hours

**Cost**: $150-200 (regenerate all tables)

### Phase 3: Feature Type Expansion

**Timeline**: 24-36 hours
- New variant scripts: 16-24 hours
- Testing: 4-6 hours
- Generation: 4-6 hours

**Cost**: $500-700
- 4× table count increase
- More complex JOINs

### Phase 4: Triangle Expansion

**Timeline**: 12-18 hours
- Triangle enumeration: 4-6 hours
- Script updates: 4-6 hours
- Generation: 4-6 hours

**Cost**: $300-400
- 4× triangle count increase

### Phase 5: Cross-Family Comparisons

**Timeline**: 8-12 hours
- New table type development: 4-6 hours
- Testing: 2-3 hours
- Generation: 2-3 hours

**Cost**: $80-120
- Smaller table count (+112)

**Total Maximum Investment**:
- **Timeline**: 70-102 hours (3-4 days of development)
- **Cost**: $1,180-1,620 (one-time)
- **Storage**: +$24/month ongoing

---

## COMPLIANCE VERIFICATION

### Phase 1 Verification Checklist

- [ ] **COV Tables**: 1,512 tables × 62 columns minimum
  - [ ] Sample 10 tables: verify 42 regression columns present
  - [ ] Verify NULL rate ≤ 5% in regression features
  - [ ] Verify row count unchanged (100% coverage maintained)

- [ ] **TRI Tables**: 72 tables × 84 columns minimum
  - [ ] Sample 10 tables: verify 63 regression columns present
  - [ ] Verify triangular relationship calculations correct
  - [ ] Verify row count unchanged

- [ ] **VAR Tables**: 32 tables × 35 columns minimum
  - [ ] Sample 8 tables: verify 21 aggregated regression columns
  - [ ] Verify directional adjustment (+1 BASE, -1 QUOTE)
  - [ ] Verify row count unchanged

- [ ] **Variant Symmetry**:
  - [ ] `count(*_bqx_*)` == `count(*_idx_*)`
  - [ ] All BQX tables have corresponding IDX mirror
  - [ ] Schema identical for BQX and IDX variants

### Phase 2-5 Verification

Similar checklists for each phase, focusing on:
- New table creation
- Schema compliance
- Data quality (NULL rates, value ranges)
- Variant symmetry maintained

---

## RISK MITIGATION

### Risk 1: Storage Cost Explosion

**Risk**: 7,312 tables × 104 columns × 2.2M rows = massive storage

**Mitigation**:
- Partitioning by DATE(interval_time) reduces query costs
- Clustering by pair/currency optimizes access patterns
- Feature selection will use <10% of features anyway
- Monitor storage monthly, archive if needed

### Risk 2: Generation Time

**Risk**: Generating 7,312 tables could take weeks

**Mitigation**:
- Parallel execution (16-32 workers)
- Phase approach (incremental delivery)
- Prioritize high-value phases (1-2 first)
- Can skip Phase 4-5 if timeline critical

### Risk 3: Schema Evolution Complexity

**Risk**: Managing 7,312 table schemas is complex

**Mitigation**:
- Programmatic schema generation (no manual table creation)
- Automated testing on sample tables
- Version control for all SQL templates
- Schema validation scripts

---

## MANDATE ENFORCEMENT

### Authority

This mandate is issued by the User (System Architect) and has **P0-CRITICAL** priority.

### Compliance Deadline

**Phase 1** (BQX-ML-M005 Compliance): BEFORE launching model training
**Phases 2-5**: Progressive enhancement, timeline flexible

### Verification

Chief Engineer (CE) is responsible for:
1. Implementing phased rollout
2. Testing each phase on sample data
3. Validating schema and data quality
4. Reporting phase completion to User

### Exceptions

Phases 3-5 may be deferred if:
- Timeline constraints require immediate model training
- Storage costs exceed budget
- User explicitly approves phased approach

Phase 1 and Phase 2 are MANDATORY (no exceptions).

---

## REVISION HISTORY

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-13 03:30 UTC | 1.0 | CE | Initial mandate creation |

---

**END OF MANDATE**

**Status**: ACTIVE - PHASED IMPLEMENTATION REQUIRED
**Next Action**: Refactor TRI/COV/VAR scripts for Phase 1
**Compliance Deadline**: Phase 1 BEFORE model training launch
