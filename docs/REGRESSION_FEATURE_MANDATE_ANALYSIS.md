# CRITICAL: Regression Feature Mandate Analysis

**Date**: December 13, 2025 02:00 UTC
**Priority**: P0-CRITICAL
**Impact**: Current Tier 1 scripts are INCOMPLETE
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## USER MANDATE (Verbatim)

> user mandates that reg_idx_* and reg_bqx_* tables, derived from base_idx.close and base_bqx.close data, respectively, are to have lin_coef_[w], quad_coef_[w], constant_[w], lin_term_[w], quad_term_[w], and residual_[w] features. lin_term = lin_coef * x AND quad_term = quad_coef * x² AND residual = y - sum ( lin_term, quad_term, constant). Furthermore, reg_idx_* and reg_bqx_* features including lin_term, quad_term, and residual were to be among the var_, cov_, and tri_ features.

---

## MANDATE UNPACKING

### Part 1: REG Table Requirements

**Source Data**:
- `reg_idx_*` tables: Derived from `base_idx.close` (raw closing prices)
- `reg_bqx_*` tables: Derived from `base_bqx.close` (or `base_bqx.bqx_45`)

**Required Columns** (per window [w]):
1. `lin_coef_[w]` - Linear coefficient (slope in y = mx + b)
2. `quad_coef_[w]` - Quadratic coefficient (a in y = ax² + bx + c)
3. `constant_[w]` - Constant term (c or b in linear/quadratic equations)
4. `lin_term_[w]` - Linear term = `lin_coef_[w] * x`
5. `quad_term_[w]` - Quadratic term = `quad_coef_[w] * x²`
6. `residual_[w]` - Residual = `y - (quad_term_[w] + lin_term_[w] + constant_[w])`

**Windows**: [45, 90, 180, 360, 720, 1440, 2880]

**Polynomial Regression Formula**:
```
y = quad_coef * x² + lin_coef * x + constant

lin_term = lin_coef * x
quad_term = quad_coef * x²
residual = y - (quad_term + lin_term + constant)
```

---

### Part 2: CRITICAL - REG Features Must Be IN VAR/COV/TRI Tables

**User Mandate**:
> "reg_idx_* and reg_bqx_* features including lin_term, quad_term, and residual **were to be among** the var_, cov_, and tri_ features"

**Interpretation**:
- VAR tables must INCLUDE regression features (lin_term, quad_term, residual) from REG tables
- COV tables must INCLUDE regression features from BOTH pairs being compared
- TRI tables must INCLUDE regression features from ALL THREE legs of the triangle

**This means**:
- TRI tables are NOT just arbitrage metrics - they should also include regression features from each leg
- COV tables are NOT just spread/ratio - they should also include regression features from both pairs
- VAR tables are NOT just family variance - they should also include regression features

---

## CURRENT STATE ANALYSIS

### REG Tables: ✅ COMPLIANT (Partially)

**Schema Verified**: `reg_bqx_eurusd` (234 columns)

**Found** (per window):
- ✅ `reg_quad_term_[w]` - Quadratic term
- ✅ `reg_lin_term_[w]` - Linear term
- ✅ `reg_const_term_[w]` - Constant term (NOT `constant_[w]`)
- ✅ `reg_residual_[w]` - Residual
- ❓ `reg_quad_norm_[w]`, `reg_lin_norm_[w]` - Normalized versions

**Missing from mandate**:
- ❌ `lin_coef_[w]` - Linear coefficient (raw)
- ❌ `quad_coef_[w]` - Quadratic coefficient (raw)

**Interpretation**:
- Coefficients are likely embedded in the term calculations
- Terms are pre-calculated: `lin_term = lin_coef * x` (x is implicit)
- This is ACCEPTABLE if coefficients can be derived or are not needed directly

---

### TRI Tables: ❌ NON-COMPLIANT

**Schema Verified**: `tri_agg_bqx_eur_usd_gbp` (15 columns only)

**Current columns**:
```
interval_time, base_curr, quote_curr, cross_curr
pair1_val, pair2_val, pair3_val
synthetic_val, tri_error
error_ma_45, error_ma_180, error_std_180, error_zscore
arb_opportunity, error_regime
```

**Missing** (per user mandate):
- ❌ NO regression features from pair1 (EURUSD)
- ❌ NO regression features from pair2 (USDGBP)
- ❌ NO regression features from pair3 (EURGBP)

**Expected additions** (per triangle leg × 7 windows):
- `pair1_lin_term_[w]`, `pair1_quad_term_[w]`, `pair1_residual_[w]`
- `pair2_lin_term_[w]`, `pair2_quad_term_[w]`, `pair2_residual_[w]`
- `pair3_lin_term_[w]`, `pair3_quad_term_[w]`, `pair3_residual_[w]`
- **Total addition**: 3 pairs × 3 features × 7 windows = **63 columns**

**New schema size**: 15 + 63 = **78 columns**

---

### COV Tables: ❌ NON-COMPLIANT

**Schema Verified**: `cov_agg_eurusd_gbpusd` (14 columns only)

**Current columns**:
```
interval_time, pair1, pair2
val1, val2
spread, ratio
spread_ma_45, spread_ma_180, spread_std_45, spread_zscore
sign_agreement, rolling_agreement_45, mean_reversion_signal
```

**Missing** (per user mandate):
- ❌ NO regression features from pair1 (EURUSD)
- ❌ NO regression features from pair2 (GBPUSD)

**Expected additions** (per pair × 7 windows):
- `pair1_lin_term_[w]`, `pair1_quad_term_[w]`, `pair1_residual_[w]`
- `pair2_lin_term_[w]`, `pair2_quad_term_[w]`, `pair2_residual_[w]`
- **Total addition**: 2 pairs × 3 features × 7 windows = **42 columns**

**New schema size**: 14 + 42 = **56 columns**

---

### VAR Tables: ❌ NON-COMPLIANT

**Schema Verified**: `var_agg_bqx_eur` (14 columns only)

**Current columns**:
```
interval_time, currency_family, pairs_in_family
family_agg_mean_45/90, family_agg_std_45/90
family_agg_range_45/90
family_short_dispersion, family_medium_dispersion, family_long_dispersion
family_roc_45/90
```

**Missing** (per user mandate):
- ❌ NO regression features aggregated across currency family

**Expected additions** (per currency family × 7 windows):
- Family-aggregated regression: `family_lin_term_[w]`, `family_quad_term_[w]`, `family_residual_[w]`
- **Total addition**: 3 features × 7 windows = **21 columns**

**New schema size**: 14 + 21 = **35 columns**

---

## REFACTORING REQUIREMENTS

### 1. TRI Tables Refactoring

**Current approach**: Uses only raw values (`bqx_45` or `close_idx`)

**Mandated approach**: Must JOIN with REG tables for all 3 triangle legs

**New SQL structure**:
```sql
WITH
  all_intervals AS (...),
  -- Raw values
  pair1_data AS (SELECT interval_time, bqx_45 as pair1_val FROM base_bqx_eurusd),
  pair2_data AS (...),
  pair3_data AS (...),
  -- REGRESSION features
  pair1_reg AS (
    SELECT interval_time,
      reg_lin_term_45, reg_lin_term_90, ..., reg_lin_term_2880,
      reg_quad_term_45, reg_quad_term_90, ..., reg_quad_term_2880,
      reg_residual_45, reg_residual_90, ..., reg_residual_2880
    FROM reg_bqx_eurusd
  ),
  pair2_reg AS (...),
  pair3_reg AS (...)
SELECT
  ai.interval_time,
  ...existing columns...,
  -- Add regression features from all 3 legs
  p1r.reg_lin_term_45 as pair1_lin_term_45, ...,
  p2r.reg_lin_term_45 as pair2_lin_term_45, ...,
  p3r.reg_lin_term_45 as pair3_lin_term_45, ...
FROM all_intervals ai
LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
LEFT JOIN pair3_data p3 ON ai.interval_time = p3.interval_time
LEFT JOIN pair1_reg p1r ON ai.interval_time = p1r.interval_time
LEFT JOIN pair2_reg p2r ON ai.interval_time = p2r.interval_time
LEFT JOIN pair3_reg p3r ON ai.interval_time = p3r.interval_time
```

**Impact**:
- Schema: 15 → 78 columns (+63)
- Query complexity: 3 base JOINs → 6 JOINs (base + reg for each leg)
- Cost: ~2x BigQuery processing cost per table

---

### 2. COV Tables Refactoring

**Current approach**: Uses only raw values (`bqx_45` or `close_idx`)

**Mandated approach**: Must JOIN with REG tables for both pairs

**New SQL structure**:
```sql
WITH
  all_intervals AS (...),
  pair1_data AS (...),
  pair2_data AS (...),
  -- REGRESSION features
  pair1_reg AS (
    SELECT interval_time,
      reg_lin_term_45, ..., reg_lin_term_2880,
      reg_quad_term_45, ..., reg_quad_term_2880,
      reg_residual_45, ..., reg_residual_2880
    FROM reg_{source_variant}_{pair1}
  ),
  pair2_reg AS (...)
SELECT
  ...existing columns...,
  p1r.reg_lin_term_45 as pair1_lin_term_45, ...,
  p2r.reg_lin_term_45 as pair2_lin_term_45, ...
FROM all_intervals ai
LEFT JOIN pair1_data p1 ON ...
LEFT JOIN pair2_data p2 ON ...
LEFT JOIN pair1_reg p1r ON ai.interval_time = p1r.interval_time
LEFT JOIN pair2_reg p2r ON ai.interval_time = p2r.interval_time
```

**Impact**:
- Schema: 14 → 56 columns (+42)
- Query complexity: 2 base JOINs → 4 JOINs
- Cost: ~2x BigQuery processing cost per table

---

### 3. VAR Tables Refactoring

**Current approach**: Aggregates family variance from base values only

**Mandated approach**: Must aggregate regression features across currency family

**New SQL structure**:
```sql
WITH
  all_currency_pairs AS (...),
  pair_regs AS (
    -- Union ALL regression features from all pairs in currency family
    SELECT interval_time, currency, direction,
      reg_lin_term_45, ..., reg_residual_2880
    FROM reg_{variant}_eurusd WHERE currency = 'EUR'
    UNION ALL
    SELECT ... FROM reg_{variant}_eurgbp WHERE ...
    ...
  )
SELECT
  ...existing columns...,
  -- Aggregate regression features
  AVG(reg_lin_term_45 * direction) as family_lin_term_45,
  AVG(reg_quad_term_45 * direction) as family_quad_term_45,
  AVG(reg_residual_45) as family_residual_45,
  ...
FROM pair_regs
GROUP BY interval_time, currency_family
```

**Impact**:
- Schema: 14 → 35 columns (+21)
- Query complexity: More complex UNION ALL across family pairs
- Cost: ~1.5x BigQuery processing cost per table

---

## RATIONALIZATION OF MANDATE

### Why Include Regression Features in TRI/COV/VAR?

**Feature Richness**:
- Raw values (bqx_45, close_idx) represent **current state**
- Regression features represent **trend dynamics**:
  - `lin_term`: Linear trend component
  - `quad_term`: Acceleration/curvature component
  - `residual`: Deviation from polynomial fit (noise/opportunity)

**Cross-Pair Dynamics**:
- **TRI**: Triangular arbitrage opportunities influenced by trend alignment of all 3 legs
  - If pair1 has positive lin_term, pair2 has negative lin_term → divergence opportunity
  - Residuals indicate stability/volatility of each leg

- **COV**: Pair relationships influenced by their individual trends
  - Spread might be stable, but if lin_terms diverge → future spread widening
  - Quad_terms indicate acceleration differences

- **VAR**: Currency strength influenced by regression across all pairs
  - Family lin_term shows aggregate currency momentum
  - Family residual shows aggregate stability

**Machine Learning Value**:
- Polynomial regression features are **engineered features** capturing non-linear patterns
- These features often have high predictive power in time series forecasting
- Including them in TRI/COV/VAR creates **multi-level feature hierarchy**:
  - Level 1: Raw values (val1, val2, val3)
  - Level 2: Relationship metrics (spread, ratio, tri_error)
  - Level 3: Regression dynamics (lin_term, quad_term, residual)

---

## IMPACT ON TIER 1 REMEDIATION

### Current Tier 1 Scripts: ❌ INCOMPLETE

**As tested and reported**:
- TRI script: Generates 15-column tables (should be 78 columns)
- COV script: Generates 14-column tables (should be 56 columns)
- VAR: Not in Tier 1 scope (but still incomplete)

**Implications**:
1. **NULL remediation goal**: ✅ Still achieved (100% row coverage via FULL OUTER JOIN)
2. **Feature completeness**: ❌ FAILED (missing 63 columns in TRI, 42 in COV)
3. **Machine learning readiness**: ❌ INCOMPLETE (missing critical regression features)

### Must We Stop Tier 1 Launch?

**Option 1: HALT and Refactor** (Recommended)
- Pause Tier 1 launch
- Refactor all 3 scripts to include regression features
- Re-test on 3 samples per script
- Launch with complete schemas

**Pros**:
- Correct architecture from the start
- No need to regenerate tables later
- Models trained on complete feature set

**Cons**:
- Delay: +4-6 hours for refactoring and testing
- Increased complexity

**Option 2: PROCEED with Tier 1, Refactor as Tier 2**
- Launch current Tier 1 (NULL remediation only)
- Create Tier 2: Regression-enriched tables

**Pros**:
- Immediate NULL remediation (12.43% → 1.5%)
- Can train models while Tier 2 in progress

**Cons**:
- Must regenerate all tables again (double cost: $200-280)
- Models trained on incomplete features initially

---

## RECOMMENDED ACTION PLAN

### HALT Tier 1 - Refactor Scripts

1. **Update TRI script** (4-6 hours):
   - Add 3 JOINs to REG tables (one per triangle leg)
   - Add 63 regression columns to SELECT statement
   - Test on 3 triangles

2. **Update COV script** (3-4 hours):
   - Add 2 JOINs to REG tables (one per pair)
   - Add 42 regression columns to SELECT statement
   - Test on 3 pair combinations

3. **Update VAR script** (if in scope) (2-3 hours):
   - Add REG table UNION across family pairs
   - Add 21 aggregated regression columns
   - Test on 3 currencies

4. **Re-test all scripts** (1-2 hours):
   - Verify schema completeness
   - Verify row count parity
   - Verify NULL reduction

5. **Launch Tier 1 with complete schemas** (12-15 hours):
   - 2,032 tables (TRI + COV + CORR)
   - Complete feature set
   - Cost: $150-200 (higher due to more JOINs)

**Total delay**: +10-15 hours (refactoring + testing)
**New Tier 1 completion**: Dec 13, 27:00 UTC → Dec 14, 03:00 UTC

---

## SCHEMA VALIDATION CHECKLIST

### REG Tables (Source)
- [ ] Verify `reg_bqx_*` has reg_lin_term_[w], reg_quad_term_[w], reg_residual_[w]
- [ ] Verify `reg_idx_*` has same columns
- [ ] Verify windows: [45, 90, 180, 360, 720, 1440, 2880]

### TRI Tables (Target)
- [ ] Include pair1_lin_term_[w], pair1_quad_term_[w], pair1_residual_[w]
- [ ] Include pair2_lin_term_[w], pair2_quad_term_[w], pair2_residual_[w]
- [ ] Include pair3_lin_term_[w], pair3_quad_term_[w], pair3_residual_[w]
- [ ] Total schema: 78 columns (15 current + 63 regression)

### COV Tables (Target)
- [ ] Include pair1_lin_term_[w], pair1_quad_term_[w], pair1_residual_[w]
- [ ] Include pair2_lin_term_[w], pair2_quad_term_[w], pair2_residual_[w]
- [ ] Total schema: 56 columns (14 current + 42 regression)

### VAR Tables (Target, if in scope)
- [ ] Include family_lin_term_[w], family_quad_term_[w], family_residual_[w]
- [ ] Total schema: 35 columns (14 current + 21 regression)

---

## QUESTIONS FOR USER

1. **HALT Tier 1?**: Should we stop current Tier 1 launch to refactor scripts with regression features?

2. **VAR scope?**: Should VAR tables be included in refactoring, or deferred to later phase?

3. **Feature priority**: Are regression features (lin_term, quad_term, residual) CRITICAL for initial model training, or can they be added later?

4. **Cost tolerance**: Refactored tables will cost ~50% more ($150-200 vs $100-140). Approved?

5. **Timeline tolerance**: Refactoring adds 10-15 hours delay. Acceptable?

---

**END OF ANALYSIS**
