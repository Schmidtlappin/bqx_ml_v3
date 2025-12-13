# REGRESSION FEATURE ARCHITECTURE MANDATE

**Mandate ID**: BQX-ML-M005
**Status**: ACTIVE
**Priority**: P0-CRITICAL
**Issued**: December 13, 2025 02:00 UTC
**Authority**: User (System Architect)
**Scope**: ALL cross-pair relationship tables (TRI, COV, VAR)
**Supersedes**: None (New mandate)
**Related Mandates**:
- BQX-ML-M001: Feature Ledger 100% Coverage Mandate
- BQX-ML-M002: BQX ML V3 Feature Inventory
- BQX-ML-M003: Data Source Integrity Mandate

---

## MANDATE STATEMENT

**User mandates that**:

1. `reg_idx_*` and `reg_bqx_*` tables, derived from `base_idx.close` and `base_bqx.bqx_45` data respectively, are to have:
   - `lin_coef_[w]` - Linear coefficient
   - `quad_coef_[w]` - Quadratic coefficient
   - `constant_[w]` - Constant term
   - `lin_term_[w]` - Linear term = `lin_coef * x`
   - `quad_term_[w]` - Quadratic term = `quad_coef * x²`
   - `residual_[w]` - Residual = `y - sum(lin_term, quad_term, constant)`

2. **CRITICAL**: `reg_idx_*` and `reg_bqx_*` features **including** `lin_term`, `quad_term`, and `residual` **were to be among** the `var_*`, `cov_*`, and `tri_*` features.

Where `[w]` represents window sizes: [45, 90, 180, 360, 720, 1440, 2880]

---

## MANDATE INTERPRETATION AND RATIONALE

### Part 1: Polynomial Regression Formula

**Mathematical Model**:
```
y = quad_coef × x² + lin_coef × x + constant

Where:
  x = normalized time position within window
  y = value at time x (close_idx or bqx_45)

Decomposition:
  lin_term = lin_coef × x
  quad_term = quad_coef × x²
  residual = y - (quad_term + lin_term + constant)
```

**Feature Purpose**:
- **lin_coef**: Rate of linear change (slope)
- **quad_coef**: Rate of acceleration/deceleration (curvature)
- **constant**: Baseline value (y-intercept)
- **lin_term**: Actual linear component contribution
- **quad_term**: Actual quadratic component contribution
- **residual**: Unexplained variance (noise, opportunity signal)

**Why Both Coefficients AND Terms?**
- **Coefficients**: Normalize across different x scales, represent rate of change
- **Terms**: Actual magnitude contributions at current time position
- **Residual**: Model error, critical for detecting regime changes and opportunities

---

### Part 2: Regression Features in Cross-Pair Tables

**User Statement**: "were to be among the var_, cov_, and tri_ features"

**Interpretation**: Cross-pair relationship tables MUST INCLUDE regression features from their constituent pairs.

**Architectural Principle**: **Multi-Level Feature Hierarchy**

```
Level 1: Raw State (Current Values)
  └─ bqx_45, close_idx, pair values

Level 2: Relationship Metrics (Pair Dynamics)
  └─ spread, ratio, tri_error, family_variance

Level 3: Regression Features (Trend Dynamics)
  └─ lin_term, quad_term, residual from each constituent pair
```

**Rationale**:

1. **Triangular Arbitrage (TRI) Enhanced by Trend Alignment**:
   - Triangle EUR-USD-GBP has 3 legs: EURUSD, USDGBP (inverted GBPUSD), EURGBP
   - Arbitrage opportunity = f(pair values, trend dynamics)
   - If EURUSD has positive lin_term (uptrend) but GBPUSD has negative lin_term → convergence opportunity
   - Residuals indicate stability/volatility of each leg → risk assessment

2. **Covariance (COV) Enhanced by Trend Divergence**:
   - Pair relationship EURUSD-GBPUSD: spread, ratio
   - Current spread may be stable, but diverging lin_terms → future spread widening
   - Quad_terms indicate acceleration differences → leading indicator
   - Residual correlation → synchronized vs independent noise

3. **Variance (VAR) Enhanced by Currency Momentum**:
   - EUR currency family: EURUSD, EURGBP, EURJPY, EURCHF, etc.
   - Family_lin_term (aggregate) → overall EUR momentum across all pairs
   - Family_quad_term (aggregate) → EUR acceleration/deceleration
   - Family_residual (aggregate) → EUR stability index

**Machine Learning Value**:
- Polynomial regression features capture **non-linear temporal patterns**
- High predictive power in time series forecasting
- Multi-level hierarchy creates **feature interactions** critical for ensemble models
- Residuals provide **regime change detection** signals

---

## COMPLIANCE REQUIREMENTS

### REG Tables (Source Tables)

**Status**: ✅ COMPLIANT (with minor naming variance)

**Schema Validation** (reg_bqx_eurusd verified - 234 columns):

Per window [45, 90, 180, 360, 720, 1440, 2880]:
- ✅ `reg_lin_term_[w]` - Linear term
- ✅ `reg_quad_term_[w]` - Quadratic term
- ✅ `reg_const_term_[w]` - Constant term (naming: `const_term` vs `constant`)
- ✅ `reg_residual_[w]` - Residual
- ✅ Additional: `reg_quad_norm_[w]`, `reg_lin_norm_[w]` - Normalized versions
- ✅ Additional: `reg_slope_[w]`, `reg_direction_[w]`, `reg_zscore_[w]` - Derived features

**Coefficient Storage**:
- Coefficients appear to be embedded in term calculations
- Terms are pre-calculated with implicit x values
- **Acceptable**: As long as terms and residuals are available for downstream use

**Source Data Verification**:
- ✅ `reg_bqx_*`: Derived from `base_bqx.bqx_45` (45-minute BQX oscillator)
- ✅ `reg_idx_*`: Derived from `base_idx.close_idx` (closing price index)

---

### TRI Tables (Target Tables)

**Status**: ❌ NON-COMPLIANT - Missing 63 columns

**Current Schema**: `tri_agg_bqx_eur_usd_gbp` (15 columns)
```
interval_time, base_curr, quote_curr, cross_curr
pair1_val, pair2_val, pair3_val
synthetic_val, tri_error
error_ma_45, error_ma_180, error_std_180, error_zscore
arb_opportunity, error_regime
```

**Mandated Schema**: 78 columns (15 current + 63 regression features)

**Required Additions** (per triangle):

**Pair 1 Regression** (21 columns):
- `pair1_lin_term_45`, `pair1_lin_term_90`, ..., `pair1_lin_term_2880` (7 columns)
- `pair1_quad_term_45`, `pair1_quad_term_90`, ..., `pair1_quad_term_2880` (7 columns)
- `pair1_residual_45`, `pair1_residual_90`, ..., `pair1_residual_2880` (7 columns)

**Pair 2 Regression** (21 columns):
- `pair2_lin_term_[w]` × 7 windows
- `pair2_quad_term_[w]` × 7 windows
- `pair2_residual_[w]` × 7 windows

**Pair 3 Regression** (21 columns):
- `pair3_lin_term_[w]` × 7 windows
- `pair3_quad_term_[w]` × 7 windows
- `pair3_residual_[w]` × 7 windows

**Total Addition**: 3 pairs × 3 features × 7 windows = **63 columns**

**Implementation Requirements**:
1. JOIN with `reg_{source_variant}_{pair1}` table
2. JOIN with `reg_{source_variant}_{pair2}` table
3. JOIN with `reg_{source_variant}_{pair3}` table
4. Extract regression features from all 3 REG tables
5. Maintain 100% row coverage using FULL OUTER JOIN strategy

---

### COV Tables (Target Tables)

**Status**: ❌ NON-COMPLIANT - Missing 42 columns

**Current Schema**: `cov_agg_eurusd_gbpusd` (14 columns)
```
interval_time, pair1, pair2
val1, val2
spread, ratio
spread_ma_45, spread_ma_180, spread_std_45, spread_zscore
sign_agreement, rolling_agreement_45, mean_reversion_signal
```

**Mandated Schema**: 56 columns (14 current + 42 regression features)

**Required Additions** (per pair combination):

**Pair 1 Regression** (21 columns):
- `pair1_lin_term_45`, `pair1_lin_term_90`, ..., `pair1_lin_term_2880` (7 columns)
- `pair1_quad_term_45`, `pair1_quad_term_90`, ..., `pair1_quad_term_2880` (7 columns)
- `pair1_residual_45`, `pair1_residual_90`, ..., `pair1_residual_2880` (7 columns)

**Pair 2 Regression** (21 columns):
- `pair2_lin_term_[w]` × 7 windows
- `pair2_quad_term_[w]` × 7 windows
- `pair2_residual_[w]` × 7 windows

**Total Addition**: 2 pairs × 3 features × 7 windows = **42 columns**

**Implementation Requirements**:
1. JOIN with `reg_{source_variant}_{pair1}` table
2. JOIN with `reg_{source_variant}_{pair2}` table
3. Extract regression features from both REG tables
4. Maintain 100% row coverage using FULL OUTER JOIN strategy

---

### VAR Tables (Target Tables)

**Status**: ❌ NON-COMPLIANT - Missing 21 columns

**Current Schema**: `var_agg_bqx_eur` (14 columns)
```
interval_time, currency_family, pairs_in_family
family_agg_mean_45, family_agg_mean_90
family_agg_std_45, family_agg_std_90
family_agg_range_45, family_agg_range_90
family_short_dispersion, family_medium_dispersion, family_long_dispersion
family_roc_45, family_roc_90
```

**Mandated Schema**: 35 columns (14 current + 21 regression features)

**Required Additions** (per currency family):

**Family Regression Aggregates** (21 columns):
- `family_lin_term_45`, `family_lin_term_90`, ..., `family_lin_term_2880` (7 columns)
- `family_quad_term_45`, `family_quad_term_90`, ..., `family_quad_term_2880` (7 columns)
- `family_residual_45`, `family_residual_90`, ..., `family_residual_2880` (7 columns)

**Aggregation Logic**:
```sql
-- Aggregate regression features across all pairs in currency family
-- Apply directional adjustment:
--   direction = +1 when currency is BASE (e.g., USD in USDJPY)
--   direction = -1 when currency is QUOTE (e.g., USD in EURUSD)

AVG(reg_lin_term_45 * direction) as family_lin_term_45,
AVG(reg_quad_term_45 * direction) as family_quad_term_45,
AVG(reg_residual_45) as family_residual_45,  -- Residual is non-directional
...
```

**Implementation Requirements**:
1. UNION ALL regression features from all pairs in currency family
2. Apply directional adjustment (+1 for BASE, -1 for QUOTE)
3. Aggregate using AVG() for lin_term and quad_term
4. Aggregate using AVG() for residual (non-directional)
5. Maintain 100% row coverage

---

## IMPLEMENTATION SPECIFICATIONS

### TRI Table Generation SQL Template

```sql
CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.tri_{variant}_{source_variant}_{base}_{quote}_{cross}`
PARTITION BY DATE(interval_time)
AS
WITH
  all_intervals AS (
    -- Get ALL unique interval_times from all 3 pairs
    SELECT DISTINCT interval_time
    FROM `{PROJECT}.{FEATURES_DATASET}.base_{source_variant}_{pair1}`
    UNION DISTINCT
    SELECT DISTINCT interval_time
    FROM `{PROJECT}.{FEATURES_DATASET}.base_{source_variant}_{pair2}`
    UNION DISTINCT
    SELECT DISTINCT interval_time
    FROM `{PROJECT}.{FEATURES_DATASET}.base_{source_variant}_{pair3}`
  ),
  -- Raw values
  pair1_data AS (
    SELECT interval_time, {value_col} as pair1_val
    FROM `{PROJECT}.{FEATURES_DATASET}.base_{source_variant}_{pair1}`
  ),
  pair2_data AS (...),
  pair3_data AS (...),
  -- REGRESSION FEATURES (NEW)
  pair1_reg AS (
    SELECT
      interval_time,
      reg_lin_term_45, reg_lin_term_90, reg_lin_term_180, reg_lin_term_360,
      reg_lin_term_720, reg_lin_term_1440, reg_lin_term_2880,
      reg_quad_term_45, reg_quad_term_90, reg_quad_term_180, reg_quad_term_360,
      reg_quad_term_720, reg_quad_term_1440, reg_quad_term_2880,
      reg_residual_45, reg_residual_90, reg_residual_180, reg_residual_360,
      reg_residual_720, reg_residual_1440, reg_residual_2880
    FROM `{PROJECT}.{FEATURES_DATASET}.reg_{source_variant}_{pair1}`
  ),
  pair2_reg AS (...),
  pair3_reg AS (...)
SELECT
  ai.interval_time,
  -- Existing columns (15)
  '{base}' as base_curr,
  '{quote}' as quote_curr,
  '{cross}' as cross_curr,
  p1.pair1_val,
  p2.pair2_val,
  p3.pair3_val,
  ...existing triangulation logic...,

  -- NEW: Pair 1 regression features (21 columns)
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

  -- NEW: Pair 2 regression features (21 columns)
  p2r.reg_lin_term_45 as pair2_lin_term_45,
  ...(repeat for all windows)...,

  -- NEW: Pair 3 regression features (21 columns)
  p3r.reg_lin_term_45 as pair3_lin_term_45,
  ...(repeat for all windows)...

FROM all_intervals ai
LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
LEFT JOIN pair3_data p3 ON ai.interval_time = p3.interval_time
LEFT JOIN pair1_reg p1r ON ai.interval_time = p1r.interval_time
LEFT JOIN pair2_reg p2r ON ai.interval_time = p2r.interval_time
LEFT JOIN pair3_reg p3r ON ai.interval_time = p3r.interval_time
```

**Key Changes**:
1. Added 3 new CTEs: `pair1_reg`, `pair2_reg`, `pair3_reg`
2. Added 3 new LEFT JOINs to regression tables
3. Added 63 new columns (21 per pair × 3 pairs)
4. Maintains 100% row coverage via all_intervals strategy

---

### COV Table Generation SQL Template

```sql
CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.cov_{variant}_{source_variant}_{pair1}_{pair2}`
PARTITION BY DATE(interval_time)
CLUSTER BY pair1
AS
WITH
  all_intervals AS (...),
  pair1_data AS (...),
  pair2_data AS (...),
  -- REGRESSION FEATURES (NEW)
  pair1_reg AS (
    SELECT
      interval_time,
      reg_lin_term_45, reg_lin_term_90, ..., reg_lin_term_2880,
      reg_quad_term_45, reg_quad_term_90, ..., reg_quad_term_2880,
      reg_residual_45, reg_residual_90, ..., reg_residual_2880
    FROM `{PROJECT}.{FEATURES_DATASET}.reg_{source_variant}_{pair1}`
  ),
  pair2_reg AS (...)
SELECT
  -- Existing columns (14)
  interval_time,
  '{pair1}' as pair1,
  '{pair2}' as pair2,
  ...existing spread/ratio logic...,

  -- NEW: Pair 1 regression features (21 columns)
  p1r.reg_lin_term_45 as pair1_lin_term_45,
  ...(all windows)...,

  -- NEW: Pair 2 regression features (21 columns)
  p2r.reg_lin_term_45 as pair2_lin_term_45,
  ...(all windows)...

FROM all_intervals ai
LEFT JOIN pair1_data p1 ON ai.interval_time = p1.interval_time
LEFT JOIN pair2_data p2 ON ai.interval_time = p2.interval_time
LEFT JOIN pair1_reg p1r ON ai.interval_time = p1r.interval_time
LEFT JOIN pair2_reg p2r ON ai.interval_time = p2r.interval_time
```

---

### VAR Table Generation SQL Template

```sql
CREATE OR REPLACE TABLE `{PROJECT}.{FEATURES_DATASET}.var_{variant}_{source_variant}_{currency}`
PARTITION BY DATE(interval_time)
AS
WITH
  currency_pairs AS (
    -- Define all pairs containing this currency with direction
    ...
  ),
  pair_regs AS (
    -- UNION ALL regression features from all pairs in family
    SELECT
      interval_time,
      '{currency}' as currency_family,
      +1 as direction,  -- Currency is BASE
      reg_lin_term_45, reg_quad_term_45, reg_residual_45,
      ...(all windows)...
    FROM `{PROJECT}.{FEATURES_DATASET}.reg_{source_variant}_eurusd`
    WHERE '{currency}' = 'EUR'

    UNION ALL

    SELECT
      interval_time,
      '{currency}' as currency_family,
      -1 as direction,  -- Currency is QUOTE
      reg_lin_term_45, reg_quad_term_45, reg_residual_45,
      ...(all windows)...
    FROM `{PROJECT}.{FEATURES_DATASET}.reg_{source_variant}_gbpeur`
    WHERE '{currency}' = 'EUR'

    ...(UNION ALL for all pairs in family)...
  )
SELECT
  interval_time,
  currency_family,
  -- Existing aggregates (14 columns)
  ...,

  -- NEW: Family regression aggregates (21 columns)
  AVG(reg_lin_term_45 * direction) as family_lin_term_45,
  AVG(reg_lin_term_90 * direction) as family_lin_term_90,
  ...(all windows)...,

  AVG(reg_quad_term_45 * direction) as family_quad_term_45,
  AVG(reg_quad_term_90 * direction) as family_quad_term_90,
  ...(all windows)...,

  AVG(reg_residual_45) as family_residual_45,  -- Non-directional
  AVG(reg_residual_90) as family_residual_90,
  ...(all windows)...

FROM pair_regs
GROUP BY interval_time, currency_family
```

---

## COMPLIANCE VERIFICATION CHECKLIST

### Pre-Generation Verification

- [ ] **REG Source Tables Exist**:
  - [ ] Verify all 28 `reg_bqx_{pair}` tables exist
  - [ ] Verify all 28 `reg_idx_{pair}` tables exist
  - [ ] Verify REG tables contain all 21 regression features (lin_term, quad_term, residual × 7 windows)

- [ ] **REG Schema Validation**:
  - [ ] Sample 3 REG tables and verify column presence
  - [ ] Verify no NULL values in regression features (or acceptable NULL rate)
  - [ ] Verify row count matches base table row count

### Generation Script Compliance

- [ ] **TRI Script**:
  - [ ] Adds 3 REG table JOINs (one per triangle leg)
  - [ ] Adds 63 regression columns to SELECT
  - [ ] Maintains PARTITION BY DATE(interval_time)
  - [ ] Maintains NO clustering (per existing schema)
  - [ ] Test on 3 triangles before full generation

- [ ] **COV Script**:
  - [ ] Adds 2 REG table JOINs (one per pair)
  - [ ] Adds 42 regression columns to SELECT
  - [ ] Maintains PARTITION BY DATE(interval_time)
  - [ ] Maintains CLUSTER BY pair1
  - [ ] Test on 3 pair combinations before full generation

- [ ] **VAR Script**:
  - [ ] UNION ALL REG tables across currency family
  - [ ] Applies directional adjustment (+1 BASE, -1 QUOTE)
  - [ ] Aggregates 21 regression features using AVG()
  - [ ] Maintains PARTITION BY DATE(interval_time)
  - [ ] Test on 3 currencies before full generation

### Post-Generation Validation

- [ ] **Schema Compliance**:
  - [ ] TRI tables: 78 columns (15 base + 63 regression)
  - [ ] COV tables: 56 columns (14 base + 42 regression)
  - [ ] VAR tables: 35 columns (14 base + 21 regression)

- [ ] **Data Quality**:
  - [ ] Row count matches existing tables (100% coverage maintained)
  - [ ] NULL rate in regression features ≤ existing NULL rate
  - [ ] Sample 10 rows per table and verify regression values are reasonable

- [ ] **Feature Ledger Integration**:
  - [ ] Update feature ledger to include all regression features
  - [ ] Verify 1,064 → 1,127 features per pair (EURUSD example)
  - [ ] Recalculate expected ledger rows: 28 pairs × 7 horizons × 1,127 features

---

## IMPACT ASSESSMENT

### Tier 1 Remediation Impact

**Original Tier 1 Scope** (INCOMPLETE):
- TRI: 72 tables × 15 columns = 1,080 feature columns
- COV: 1,512 tables × 14 columns = 21,168 feature columns
- CORR: 448 tables (unchanged, no regression features)
- **Total**: 2,032 tables, ~22,248 feature columns

**Revised Tier 1 Scope** (COMPLIANT):
- TRI: 72 tables × 78 columns = 5,616 feature columns (+4,536)
- COV: 1,512 tables × 56 columns = 84,672 feature columns (+63,504)
- CORR: 448 tables (unchanged)
- **Total**: 2,032 tables, ~90,288 feature columns (+68,040)

**Feature Increase**: +68,040 columns (+305% increase in TRI/COV features)

### Cost Impact

**BigQuery Processing**:
- Original estimate: $100-140 (simple JOINs)
- Revised estimate: $150-200 (+50% due to additional JOINs)
- Increase: +$50-60

**BigQuery Storage**:
- Additional 68,040 columns × ~2.2M rows each
- Estimated additional storage: ~150 GB
- Monthly cost: +$2.25/month (negligible)

**Total Cost Increase**: +$50-60 one-time, +$2.25/month ongoing

### Timeline Impact

**Refactoring Time**:
- TRI script: +4-6 hours (add 3 JOINs, 63 columns)
- COV script: +3-4 hours (add 2 JOINs, 42 columns)
- VAR script: +2-3 hours (add UNION ALL, 21 columns)
- Testing: +2-3 hours (3 samples per script)
- **Total**: +11-16 hours

**Generation Time**:
- Additional JOINs: +20-30% processing time per table
- Original estimate: 12-15 hours
- Revised estimate: 15-20 hours
- **Total delay**: +14-19 hours (refactoring + longer generation)

**New Tier 1 Completion**: Dec 14, 04:00-08:00 UTC (was Dec 13, 17:00 UTC)

### Machine Learning Impact

**Positive**:
- ✅ Complete feature set from the start
- ✅ No need to retrain models later
- ✅ Polynomial regression features have high predictive power
- ✅ Multi-level feature hierarchy enables feature interactions
- ✅ Residuals provide regime change detection

**Neutral**:
- Feature selection will filter to most predictive features anyway
- Additional features increase initial feature pool but not necessarily final model features

**Negative**:
- None - more features is always better for ML (can be filtered during selection)

---

## DECISION MATRIX

### Option 1: HALT and Refactor (RECOMMENDED)

**Approach**: Stop Tier 1 launch, refactor all scripts, launch with complete schemas

**Pros**:
- ✅ Correct architecture from day 1
- ✅ No need to regenerate tables later (saves $100-140)
- ✅ Models trained on complete feature set immediately
- ✅ Compliance with user mandate

**Cons**:
- ⏱️ Delay: +14-19 hours
- 💰 Cost: +$50-60

**Recommendation**: **STRONGLY RECOMMENDED**
- One-time delay is acceptable
- Cost increase is minimal (<40% total)
- Avoids double work and double cost later
- Ensures architectural correctness

---

### Option 2: Proceed Then Refactor (NOT RECOMMENDED)

**Approach**: Launch current Tier 1 (NULL fix only), create Tier 2 for regression features

**Pros**:
- ⏱️ Immediate NULL remediation (12.43% → 1.5%)
- 🚀 Can start model training sooner

**Cons**:
- ❌ Non-compliant with user mandate
- 💰 Double cost: $100-140 (Tier 1) + $150-200 (Tier 2) = $250-340
- ⏱️ Double work: regenerate all tables again
- 🔄 Must retrain models with complete features later
- 📊 Models initially trained on incomplete feature set

**Recommendation**: **NOT RECOMMENDED**
- Higher total cost
- More total time (when accounting for Tier 2)
- Violates user mandate
- Creates technical debt

---

## MANDATE ENFORCEMENT

### Authority
This mandate is issued by the User (System Architect) and has **P0-CRITICAL** priority.

### Compliance Deadline
All TRI, COV, and VAR table generation scripts MUST be refactored to include regression features BEFORE launching Tier 1 remediation.

### Verification
Chief Engineer (CE) is responsible for:
1. Verifying script compliance before launch
2. Testing refactored scripts on sample data
3. Validating schema compliance post-generation
4. Reporting compliance status to User

### Exceptions
None. This is a foundational architecture requirement.

---

## RELATED DOCUMENTATION

### Mandates
- `BQX_ML_V3_FEATURE_INVENTORY.md` - Feature count implications
- `FEATURE_LEDGER_100_PERCENT_MANDATE.md` - Ledger row count updates

### Intelligence Files
- `intelligence/ontology.json` - Feature entity definitions
- `intelligence/feature_catalogue.json` - Feature type taxonomy
- `intelligence/semantics.json` - Regression feature semantics
- `intelligence/roadmap_v2.json` - Implementation roadmap

### Technical Documentation
- `docs/REGRESSION_FEATURE_MANDATE_ANALYSIS.md` - Detailed analysis
- `scripts/generate_tri_tables.py` - TRI generation (TO BE REFACTORED)
- `scripts/generate_cov_tables.py` - COV generation (TO BE REFACTORED)
- `scripts/generate_var_tables.py` - VAR generation (TO BE CREATED)

---

## REVISION HISTORY

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-13 02:00 UTC | 1.0 | CE | Initial mandate creation |

---

**END OF MANDATE**

**Status**: ACTIVE - AWAITING IMPLEMENTATION
**Next Action**: Refactor TRI/COV/VAR generation scripts
**Compliance Deadline**: BEFORE Tier 1 launch
