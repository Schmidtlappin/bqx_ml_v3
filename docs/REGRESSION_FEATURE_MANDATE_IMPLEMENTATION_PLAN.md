# Regression Feature Mandate Implementation Plan (REVISED)
## BQX-ML-M005 Full Compliance Roadmap v2.0

**Status**: PENDING USER APPROVAL
**Priority**: P0-CRITICAL
**Mandate**: REG tables MUST have BOTH coefficient AND term data; regression features MUST be among TRI/COV/VAR features
**Created**: 2025-12-13
**Revised**: 2025-12-13 (Added Phase 0 for REG table compliance)
**Approved By**: USER (pending)

---

## EXECUTIVE SUMMARY

**Decision**: HALT Tier 1 to fix REG table schemas AND refactor TRI/COV/VAR scripts for full compliance with BQX-ML-M005

**Current State**:
1. **REG Tables**: PARTIALLY COMPLIANT
   - ✅ Have term data: `reg_lin_term_*`, `reg_quad_term_*`, `reg_const_term_*`, `reg_residual_*`
   - ❌ Missing coefficient data: `reg_lin_coef_*`, `reg_quad_coef_*`
   - **Gap**: 14 columns per table (2 coef types × 7 windows)

2. **TRI/COV/VAR Tables**: NON-COMPLIANT
   - TRI: 15 columns (should be 78) - missing 63 regression features
   - COV: 14 columns (should be 56) - missing 42 regression features
   - VAR: 14 columns (should be 35) - missing 21 regression features

**Target State**: All tables compliant with full regression feature mandate
- REG: 234 → 248 columns (+14 coefficient features)
- TRI: 15 → 78 columns (+63 regression features from 3 legs)
- COV: 14 → 56 columns (+42 regression features from 2 pairs)
- VAR: 14 → 35 columns (+21 regression features aggregated)

**Total Timeline**: 16-22 hours (REG fix + script refactoring + testing + regeneration)
**Total Cost**: $160-220 (one-time, correct architecture from start)

---

## PHASE 0: FIX REG TABLE SCHEMA (NEW - 2-3 hours)

### Mandate Requirement

User mandate states REG tables must have **BOTH**:
- **Coefficient features**: `lin_coef_[w]`, `quad_coef_[w]`, `constant_[w]`
- **Term features**: `lin_term_[w]`, `quad_term_[w]`, `residual_[w]`

### Current REG Table Status (Verified 2025-12-13)

**Existing columns** (234 total):
```
✅ reg_lin_term_[w]      (β₁ × W - evaluated at endpoint)
✅ reg_quad_term_[w]     (β₂ × W² - evaluated at endpoint)
✅ reg_const_term_[w]    (β₀ - constant, already = coefficient)
✅ reg_residual_[w]      (y - predicted)

❌ reg_lin_coef_[w]      MISSING (raw β₁ coefficient)
❌ reg_quad_coef_[w]     MISSING (raw β₂ coefficient)
```

**Required additions**: 14 columns per table
- `reg_lin_coef_45`, `reg_lin_coef_90`, ..., `reg_lin_coef_2880` (7 columns)
- `reg_quad_coef_45`, `reg_quad_coef_90`, ..., `reg_quad_coef_2880` (7 columns)

### Phase 0A: Update REG Generation Script (1-1.5 hours)

**File**: `scripts/generate_reg_tables.py` (or SQL generation script)

**Add coefficient calculations**:
```sql
-- For each window W in [45, 90, 180, 360, 720, 1440, 2880]:

-- Linear coefficient (raw β₁)
reg_lin_coef_{W} = reg_lin_term_{W} / {W}

-- Quadratic coefficient (raw β₂)
reg_quad_coef_{W} = reg_quad_term_{W} / POW({W}, 2)

-- Constant coefficient (already exists)
-- reg_const_term_{W} IS the coefficient (β₀)
```

**Implementation approach**:

Option 1: **Regenerate REG tables with new schema** (RECOMMENDED)
- Update SQL generation to include coefficient calculations
- Regenerate all 84 REG tables (28 bqx + 28 idx + 28 other)
- Cost: $5-10
- Time: 1-1.5 hours

Option 2: **ALTER TABLE to add columns** (NOT RECOMMENDED - BigQuery limitation)
- BigQuery doesn't support ALTER TABLE ADD COLUMN with computed values
- Would require CREATE TABLE AS SELECT anyway
- Same cost and complexity as Option 1

**Decision**: Use Option 1 (regenerate with updated schema)

### Phase 0B: Test REG Schema Update (0.5-1 hour)

**Test on 3 REG tables**:
1. `reg_bqx_eurusd` (BQX variant)
2. `reg_idx_eurusd` (IDX variant)
3. `reg_bqx_gbpusd` (different pair)

**Verification**:
```sql
-- Verify column count
SELECT COUNT(*) as col_count
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'reg_bqx_eurusd';
-- Expected: 248 (was 234, +14 coef columns)

-- Verify coefficient columns exist
SELECT column_name
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'reg_bqx_eurusd'
  AND column_name LIKE 'reg_%_coef_%'
ORDER BY column_name;
-- Expected: 14 columns (lin_coef_* × 7 + quad_coef_* × 7)

-- Verify coefficient values are correct
SELECT
  reg_lin_term_45,
  reg_lin_coef_45,
  reg_lin_coef_45 * 45 as reconstructed_lin_term,
  ABS(reg_lin_term_45 - (reg_lin_coef_45 * 45)) as error
FROM `bqx-ml.bqx_ml_v3_features_v2.reg_bqx_eurusd`
WHERE reg_lin_term_45 IS NOT NULL
LIMIT 10;
-- Expected: error < 0.0001 (floating point precision)
```

**Success criteria**:
- ✅ All 3 test tables have 248 columns
- ✅ All 14 coefficient columns present
- ✅ Coefficient values mathematically correct (term = coef × W or W²)
- ✅ NULL rates same as term columns

### Phase 0C: Regenerate All REG Tables (0.5-1 hour)

**Scope**: 84 tables
- 28 `reg_bqx_*` tables
- 28 `reg_idx_*` tables
- 28 other variant tables

**Execution**:
```bash
python3 scripts/generate_reg_tables.py --workers 8 > /tmp/reg_regen.log 2>&1 &
```

**Monitoring**:
- Track completion every 10 minutes
- Sample validate 5 tables at 50% completion

**Expected outcomes**:
- 84/84 tables successful (100%)
- Average time: 30-40 seconds per table
- Total time: 30-60 minutes with 8 workers

**Cost**: $5-10

---

## PHASE 1: SCRIPT REFACTORING (11-16 hours)

### Phase 1A: TRI Script Refactoring (4-6 hours)

**File**: `scripts/generate_tri_tables.py`

**Current Schema** (15 columns):
```
interval_time, base_curr, quote_curr, cross_curr
pair1_val, pair2_val, pair3_val
synthetic_val, tri_error
error_ma_45, error_ma_180, error_std_180, error_zscore
arb_opportunity, error_regime
```

**Mandated Schema** (78 columns):
```
[Current 15 columns] +
[pair1_lin_coef_45...2880] (7 windows) +
[pair1_quad_coef_45...2880] (7 windows) +
[pair1_lin_term_45...2880] (7 windows) +
[pair1_quad_term_45...2880] (7 windows) +
[pair1_residual_45...2880] (7 windows) +
[pair2_lin_coef_45...2880] (7 windows) +
[pair2_quad_coef_45...2880] (7 windows) +
[pair2_lin_term_45...2880] (7 windows) +
[pair2_quad_term_45...2880] (7 windows) +
[pair2_residual_45...2880] (7 windows) +
[pair3_lin_coef_45...2880] (7 windows) +
[pair3_quad_coef_45...2880] (7 windows) +
[pair3_lin_term_45...2880] (7 windows) +
[pair3_quad_term_45...2880] (7 windows) +
[pair3_residual_45...2880] (7 windows)
```
**Total**: 15 + (3 legs × 5 features × 7 windows) = 15 + 105 = 120 columns

**CORRECTED FROM ORIGINAL PLAN**: Now including BOTH coefficient AND term data (5 features per leg, not 3)

**Implementation Steps**:

1. **Add REG Table CTEs** (1 hour)
   ```sql
   -- Add after all_intervals CTE
   pair1_reg AS (
     SELECT
       interval_time,
       -- Coefficients
       reg_lin_coef_45, reg_lin_coef_90, ..., reg_lin_coef_2880,
       reg_quad_coef_45, reg_quad_coef_90, ..., reg_quad_coef_2880,
       -- Terms
       reg_lin_term_45, reg_lin_term_90, ..., reg_lin_term_2880,
       reg_quad_term_45, reg_quad_term_90, ..., reg_quad_term_2880,
       reg_residual_45, reg_residual_90, ..., reg_residual_2880
     FROM `bqx-ml.bqx_ml_v3_features_v2.reg_{source_variant}_{pair1}`
   ),
   pair2_reg AS (...),
   pair3_reg AS (...)
   ```

2. **Add JOINs to Main Query** (1 hour)
   ```sql
   LEFT JOIN pair1_reg
     ON combined.interval_time = pair1_reg.interval_time
   LEFT JOIN pair2_reg
     ON combined.interval_time = pair2_reg.interval_time
   LEFT JOIN pair3_reg
     ON combined.interval_time = pair3_reg.interval_time
   ```

3. **Add Column Aliases in SELECT** (1.5 hours)
   ```sql
   -- Add after current columns
   -- Pair 1 coefficients
   pair1_reg.reg_lin_coef_45 as pair1_lin_coef_45,
   pair1_reg.reg_quad_coef_45 as pair1_quad_coef_45,
   ...
   -- Pair 1 terms
   pair1_reg.reg_lin_term_45 as pair1_lin_term_45,
   pair1_reg.reg_quad_term_45 as pair1_quad_term_45,
   pair1_reg.reg_residual_45 as pair1_residual_45,
   ...
   -- Repeat for pair2_reg and pair3_reg (105 columns total)
   ```

4. **Update Source Variant Logic** (0.5 hours)
   - Ensure BQX variant uses `reg_bqx_*` tables
   - Ensure IDX variant uses `reg_idx_*` tables

5. **Test on 3 Triangles** (1-2 hours)
   - EUR-USD-GBP (BQX)
   - EUR-USD-JPY (BQX)
   - EUR-USD-GBP (IDX)
   - Verify 120 columns in output (was 78 in original plan)
   - Verify row counts match current tables
   - Verify regression features populated (not NULL)

**Deliverables**:
- ✅ Updated `generate_tri_tables.py` with 120-column schema
- ✅ Test results: 3/3 successful
- ✅ Sample validation queries

---

### Phase 1B: COV Script Refactoring (3-4 hours)

**File**: `scripts/generate_cov_tables.py`

**Current Schema** (14 columns):
```
interval_time, pair1, pair2, val1, val2
spread, ratio
spread_ma_45, spread_ma_180
spread_std_45, spread_zscore
sign_agreement, rolling_agreement_45
mean_reversion_signal
```

**Mandated Schema** (84 columns):
```
[Current 14 columns] +
[pair1_lin_coef_45...2880] (7 windows) +
[pair1_quad_coef_45...2880] (7 windows) +
[pair1_lin_term_45...2880] (7 windows) +
[pair1_quad_term_45...2880] (7 windows) +
[pair1_residual_45...2880] (7 windows) +
[pair2_lin_coef_45...2880] (7 windows) +
[pair2_quad_coef_45...2880] (7 windows) +
[pair2_lin_term_45...2880] (7 windows) +
[pair2_quad_term_45...2880] (7 windows) +
[pair2_residual_45...2880] (7 windows)
```
**Total**: 14 + (2 pairs × 5 features × 7 windows) = 14 + 70 = 84 columns

**CORRECTED FROM ORIGINAL PLAN**: Now including BOTH coefficient AND term data (5 features per pair, not 3)

**Implementation Steps**:

1. **Add REG Table CTEs** (0.5 hours)
   ```sql
   pair1_reg AS (
     SELECT
       interval_time,
       reg_lin_coef_45, ..., reg_lin_coef_2880,
       reg_quad_coef_45, ..., reg_quad_coef_2880,
       reg_lin_term_45, ..., reg_lin_term_2880,
       reg_quad_term_45, ..., reg_quad_term_2880,
       reg_residual_45, ..., reg_residual_2880
     FROM `bqx-ml.bqx_ml_v3_features_v2.reg_{source_variant}_{pair1}`
   ),
   pair2_reg AS (...)
   ```

2. **Add JOINs to Main Query** (0.5 hours)
   ```sql
   LEFT JOIN pair1_reg
     ON combined.interval_time = pair1_reg.interval_time
   LEFT JOIN pair2_reg
     ON combined.interval_time = pair2_reg.interval_time
   ```

3. **Add Column Aliases in SELECT** (1.5 hours)
   ```sql
   -- Add after current columns
   pair1_reg.reg_lin_coef_45 as pair1_lin_coef_45,
   pair1_reg.reg_quad_coef_45 as pair1_quad_coef_45,
   pair1_reg.reg_lin_term_45 as pair1_lin_term_45,
   pair1_reg.reg_quad_term_45 as pair1_quad_term_45,
   pair1_reg.reg_residual_45 as pair1_residual_45,
   ...
   pair2_reg.reg_lin_coef_45 as pair2_lin_coef_45,
   ...
   -- (70 columns total)
   ```

4. **Test on 3 Pair Combinations** (1-2 hours)
   - AUDCAD-AUDCHF
   - AUDCAD-AUDJPY
   - AUDCAD-AUDNZD
   - Verify 84 columns in output (was 56 in original plan)
   - Verify row counts match current tables

**Deliverables**:
- ✅ Updated `generate_cov_tables.py` with 84-column schema
- ✅ Test results: 3/3 successful
- ✅ Sample validation queries

---

### Phase 1C: VAR Script Refactoring (2-3 hours)

**File**: `scripts/generate_var_tables.py` (may need creation)

**Current Schema** (14 columns):
```
interval_time, currency, family_size
family_mean, family_std, family_min, family_max
family_range, family_cv
outlier_flag, regime
divergence_from_mean, z_score
```

**Mandated Schema** (49 columns):
```
[Current 14 columns] +
[lin_coef_45...2880] (7 windows) +
[quad_coef_45...2880] (7 windows) +
[lin_term_45...2880] (7 windows) +
[quad_term_45...2880] (7 windows) +
[residual_45...2880] (7 windows)
```
**Total**: 14 + (5 features × 7 windows) = 14 + 35 = 49 columns

**CORRECTED FROM ORIGINAL PLAN**: Now including BOTH coefficient AND term data (5 features, not 3)

**Implementation Steps**:

1. **Add REG Aggregation Logic** (1 hour)
   ```sql
   -- Aggregate regression features across currency family
   -- Coefficients
   AVG(reg.reg_lin_coef_45) as lin_coef_45,
   AVG(reg.reg_quad_coef_45) as quad_coef_45,
   -- Terms
   AVG(reg.reg_lin_term_45) as lin_term_45,
   AVG(reg.reg_quad_term_45) as quad_term_45,
   AVG(reg.reg_residual_45) as residual_45,
   ...
   ```

2. **Add Family Member JOINs** (0.5 hours)
   - Join all pairs containing the currency
   - Aggregate regression features with AVG

3. **Test on 3 Currency Families** (0.5-1 hours)
   - EUR family
   - USD family
   - GBP family
   - Verify 49 columns in output (was 35 in original plan)

**Deliverables**:
- ✅ Updated/created VAR script with 49-column schema
- ✅ Test results: 3/3 successful
- ✅ Sample validation queries

---

### Phase 1D: Integration Testing (2-3 hours)

**Objective**: Verify all 3 scripts work correctly end-to-end with FULL regression features (coef + term)

**Test Plan**:

1. **Comprehensive Test Set** (1 hour)
   - TRI: 10 tables (5 BQX + 5 IDX, covering different currency combinations)
   - COV: 10 tables (5 agg + 5 align, different pair combinations)
   - VAR: 7 tables (all 8 currencies if available, or subset)

2. **Schema Validation** (0.5 hours)
   ```sql
   -- Verify column counts
   SELECT COUNT(*) as column_count
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name = 'tri_agg_bqx_eur_usd_gbp'
   -- Expected: 120 (was 78 in original plan)

   -- Verify BOTH coefficient AND term features present
   SELECT column_name
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name = 'tri_agg_bqx_eur_usd_gbp'
     AND (column_name LIKE '%_lin_coef_%' OR column_name LIKE '%_lin_term_%')
   -- Expected: 42 columns (3 legs × 7 windows × 2 feature types)
   ```

3. **Data Quality Validation** (0.5 hours)
   - NULL rate check: regression features should have ~0% NULL
   - Value range check: regression features should have reasonable values
   - Row count parity: new tables should match current row counts
   - **Coefficient consistency check**: Verify coef × W = term

4. **Performance Validation** (0.5 hours)
   - Measure generation time per table
   - Confirm within expected range (60-90 seconds per table due to additional columns)
   - Identify any performance regressions

**Success Criteria**:
- ✅ All 27 test tables generate successfully (100% success rate)
- ✅ All schemas have correct column counts (120/84/49)
- ✅ All regression features (BOTH coef AND term) populated (NULL rate < 1%)
- ✅ Coefficient math verified: `coef × W^n = term` (within floating point precision)
- ✅ Row counts match current tables (±1% tolerance)
- ✅ Performance within acceptable range

**Deliverables**:
- ✅ Integration test report
- ✅ Schema validation results
- ✅ Data quality metrics
- ✅ Performance benchmarks

---

## PHASE 2: FULL TABLE REGENERATION (3-5 hours)

### Phase 2A: TRI Table Regeneration (1-2 hours)

**Scope**: 72 tables (18 triangles × 2 variants × 2 source variants)

**Execution**:
```bash
python3 scripts/generate_tri_tables.py --workers 16 > /tmp/tri_regeneration.log 2>&1 &
```

**Monitoring**:
- Track completion rate every 15 minutes
- Alert if error rate > 5%
- Sample validate 10 tables at 50% completion

**Expected Outcomes**:
- 72/72 tables successful (100%)
- Average time: 60-70 seconds per table (increased due to additional columns)
- Total time: 70-100 minutes with 16 workers

---

### Phase 2B: COV Table Regeneration (1.5-2.5 hours)

**Scope**: 1,512 tables (756 agg + 756 align)

**Execution**:
```bash
python3 scripts/generate_cov_tables.py --workers 16 > /tmp/cov_regeneration.log 2>&1 &
```

**Monitoring**:
- Track completion rate every 30 minutes
- Sample validate 10 tables at 25%, 50%, 75% completion

**Expected Outcomes**:
- 1,512/1,512 tables successful (100%)
- Average time: 60-70 seconds per table
- Total time: 100-160 minutes with 16 workers

---

### Phase 2C: VAR Table Regeneration (0.5-1 hour)

**Scope**: 63 tables (currency family variance tables)

**Execution**:
```bash
python3 scripts/generate_var_tables.py --workers 16 > /tmp/var_regeneration.log 2>&1 &
```

**Expected Outcomes**:
- 63/63 tables successful (100%)
- Total time: 30-60 minutes

---

## PHASE 3: VALIDATION & VERIFICATION (1-2 hours)

### Phase 3A: Schema Compliance Verification (0.5 hours)

**Verification Steps**:

1. **Column Count Verification**:
   ```sql
   -- TRI tables should have 120 columns (was 78 in original plan)
   SELECT table_name, COUNT(*) as col_count
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name LIKE 'tri_%'
   GROUP BY table_name
   HAVING col_count != 120;
   -- Expected: 0 rows (all compliant)

   -- COV tables should have 84 columns (was 56 in original plan)
   SELECT table_name, COUNT(*) as col_count
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name LIKE 'cov_%'
   GROUP BY table_name
   HAVING col_count != 84;
   -- Expected: 0 rows

   -- VAR tables should have 49 columns (was 35 in original plan)
   SELECT table_name, COUNT(*) as col_count
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name LIKE 'var_%'
   GROUP BY table_name
   HAVING col_count != 49;
   -- Expected: 0 rows
   ```

2. **Regression Feature Presence Verification**:
   ```sql
   -- Verify all TRI tables have BOTH coefficient AND term features from 3 legs
   SELECT table_name
   FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name LIKE 'tri_%'
   GROUP BY table_name
   HAVING
     SUM(CASE WHEN column_name LIKE 'pair1_lin_coef_%' THEN 1 ELSE 0 END) != 7
     OR SUM(CASE WHEN column_name LIKE 'pair1_lin_term_%' THEN 1 ELSE 0 END) != 7
     OR SUM(CASE WHEN column_name LIKE 'pair2_quad_coef_%' THEN 1 ELSE 0 END) != 7
     OR SUM(CASE WHEN column_name LIKE 'pair2_quad_term_%' THEN 1 ELSE 0 END) != 7
     OR SUM(CASE WHEN column_name LIKE 'pair3_residual_%' THEN 1 ELSE 0 END) != 7;
   -- Expected: 0 rows
   ```

3. **Coefficient-Term Consistency Verification**:
   ```sql
   -- Verify coefficient × W = term (within floating point precision)
   SELECT
     pair1_lin_coef_45 * 45 as computed_term,
     pair1_lin_term_45 as stored_term,
     ABS(pair1_lin_coef_45 * 45 - pair1_lin_term_45) as error,
     CASE
       WHEN ABS(pair1_lin_coef_45 * 45 - pair1_lin_term_45) > 0.001 THEN 'FAIL'
       ELSE 'PASS'
     END as status
   FROM `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`
   WHERE pair1_lin_coef_45 IS NOT NULL
   LIMIT 100;
   -- Expected: All rows status = 'PASS'
   ```

**Success Criteria**:
- ✅ All TRI tables have exactly 120 columns
- ✅ All COV tables have exactly 84 columns
- ✅ All VAR tables have exactly 49 columns
- ✅ All tables have complete regression feature sets (BOTH coef AND term)
- ✅ Coefficient-term math is consistent

---

### Phase 3B: Data Quality Verification (0.5 hours)

**Verification Steps**:

1. **NULL Rate Check**:
   ```sql
   -- Sample NULL rates in regression features
   SELECT
     COUNTIF(pair1_lin_coef_45 IS NULL) * 100.0 / COUNT(*) as null_pct_pair1_lin_coef_45,
     COUNTIF(pair1_lin_term_45 IS NULL) * 100.0 / COUNT(*) as null_pct_pair1_lin_term_45,
     COUNTIF(pair2_quad_coef_90 IS NULL) * 100.0 / COUNT(*) as null_pct_pair2_quad_coef_90,
     COUNTIF(pair2_quad_term_90 IS NULL) * 100.0 / COUNT(*) as null_pct_pair2_quad_term_90,
     COUNTIF(pair3_residual_180 IS NULL) * 100.0 / COUNT(*) as null_pct_pair3_resid_180
   FROM `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`;
   -- Expected: < 1% for all columns
   ```

2. **Row Count Parity Check**:
   ```sql
   -- Compare row counts before/after regeneration
   SELECT
     'tri_agg_bqx_eur_usd_gbp' as table_name,
     COUNT(*) as new_row_count,
     2181765 as expected_row_count,
     ABS(COUNT(*) - 2181765) * 100.0 / 2181765 as pct_difference
   FROM `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`;
   -- Expected: pct_difference < 1%
   ```

3. **Value Range Sanity Check**:
   ```sql
   -- Check regression features have reasonable values
   SELECT
     MIN(pair1_lin_coef_45) as min_lin_coef,
     MAX(pair1_lin_coef_45) as max_lin_coef,
     AVG(pair1_lin_coef_45) as avg_lin_coef,
     MIN(pair1_lin_term_45) as min_lin_term,
     MAX(pair1_lin_term_45) as max_lin_term,
     AVG(pair1_lin_term_45) as avg_lin_term
   FROM `bqx-ml.bqx_ml_v3_features_v2.tri_agg_bqx_eur_usd_gbp`;
   -- Expected: Values in reasonable range (not all zeros, not extreme outliers)
   ```

**Success Criteria**:
- ✅ NULL rate < 1% for all regression features (BOTH coef AND term)
- ✅ Row count parity within 1% of original tables
- ✅ Regression feature values in expected ranges

---

### Phase 3C: Feature Universe Update (0.5 hours)

**Tasks**:

1. **Update Feature Count**:
   - Unique features per pair: 1,064 → 1,211 (+147)
   - **CORRECTED**: Original plan had +63, now +147 due to coefficient columns
   - Calculation: +105 from TRI (3 legs × 5 features × 7 windows)
                  +70 from COV (2 pairs × 5 features × 7 windows)
                  +35 from VAR (5 features × 7 windows)
                  -63 (overlap correction) = +147 unique features

2. **Regenerate Feature Ledger**:
   ```bash
   python3 scripts/generate_feature_ledger.py --pairs all --horizons all
   ```
   - Expected rows: 208,572 → 237,668 (+29,096)
   - Calculation: 28 pairs × 7 horizons × 1,211 features = 237,668
   - Verification: All 1,211 unique features present

3. **Update Intelligence Files**:
   - Mark TRI/COV/VAR as COMPLIANT in all intelligence files
   - Mark REG as COMPLIANT with full coefficient + term data
   - Update feature counts throughout documentation
   - Update roadmap status to "RISK-006 RESOLVED"

**Deliverables**:
- ✅ Updated feature_ledger.parquet with 237,668 rows
- ✅ Intelligence files updated with compliance status
- ✅ Feature counts verified across all documentation

---

## PHASE 4: STEP 6 CONTINUATION (after compliance)

**Objective**: Resume Step 6 feature extraction with compliant schemas

**Scope**: Extract features for remaining 25 pairs using Cloud Run pipeline

**Prerequisites**:
- ✅ All REG tables compliant (248 columns with coef + term data)
- ✅ All TRI/COV/VAR tables compliant (120/84/49 columns)
- ✅ Feature ledger regenerated
- ✅ Intelligence files updated

**Execution**:
- Continue with existing Cloud Run pipeline
- Extract 667 tables per pair (now with compliant schemas)
- Merge with Polars (user-mandated protocol)
- Validate training files

**Timeline**: Unchanged from original plan (77-101 minutes per pair)

---

## SUCCESS CRITERIA

### Mandatory Requirements (Must Pass All)

1. **REG Table Compliance**: ✅
   - All REG tables: 248 columns (234 + 14 coefficient columns)
   - BOTH coefficient AND term data present for lin and quad features

2. **Schema Compliance**: ✅
   - All TRI tables: 120 columns (15 + 105 regression)
   - All COV tables: 84 columns (14 + 70 regression)
   - All VAR tables: 49 columns (14 + 35 regression)

3. **Feature Presence**: ✅
   - All regression features (BOTH coef AND term: lin_coef, quad_coef, lin_term, quad_term, residual) present in all tables
   - NULL rate < 1% for regression features
   - Coefficient-term math verified

4. **Data Integrity**: ✅
   - Row count parity within 1% of original tables
   - No data corruption or loss
   - Partitioning and clustering preserved

5. **Feature Universe**: ✅
   - Feature count updated: 1,064 → 1,211 (+147)
   - Feature ledger regenerated: 208,572 → 237,668 rows
   - All intelligence files updated

6. **Mandate Compliance**: ✅
   - BQX-ML-M005 status: NON-COMPLIANT → COMPLIANT
   - REG tables: PARTIAL → COMPLIANT (full coef + term data)
   - TRI/COV/VAR tables: NON-COMPLIANT → COMPLIANT
   - RISK-006 status: PENDING → RESOLVED
   - User mandate requirement met: "REG tables MUST have BOTH coefficient AND term data; regression features MUST be among TRI/COV/VAR features"

---

## TIMELINE & MILESTONES

| Phase | Task | Duration | Cumulative | Status |
|-------|------|----------|------------|--------|
| **0A** | REG Script Update | 1-1.5 hours | 1-1.5h | PENDING |
| **0B** | REG Schema Testing | 0.5-1 hour | 1.5-2.5h | PENDING |
| **0C** | REG Table Regeneration (84 tables) | 0.5-1 hour | 2-3.5h | PENDING |
| **1A** | TRI Script Refactoring (120 cols) | 4-6 hours | 6-9.5h | PENDING |
| **1B** | COV Script Refactoring (84 cols) | 3-4 hours | 9-13.5h | PENDING |
| **1C** | VAR Script Refactoring (49 cols) | 2-3 hours | 11-16.5h | PENDING |
| **1D** | Integration Testing | 2-3 hours | 13-19.5h | PENDING |
| **2A** | TRI Regeneration (72 tables) | 1-2 hours | 14-21.5h | PENDING |
| **2B** | COV Regeneration (1,512 tables) | 1.5-2.5 hours | 15.5-24h | PENDING |
| **2C** | VAR Regeneration (63 tables) | 0.5-1 hour | 16-25h | PENDING |
| **3A** | Schema Verification | 0.5 hours | 16.5-25.5h | PENDING |
| **3B** | Data Quality Verification | 0.5 hours | 17-26h | PENDING |
| **3C** | Feature Universe Update | 0.5 hours | 17.5-26.5h | PENDING |

**Total Estimated Timeline**: 17.5-26.5 hours (realistic: 20-22 hours)

**HALT Point**: December 13, 2025 (current time)
**Expected Completion**: December 14-15, 2025

---

## COST BREAKDOWN

| Item | Cost (USD) | Notes |
|------|------------|-------|
| **PHASE 0: REG Table Fix** | | |
| REG Script Development & Testing | $0 | Local compute only |
| REG Regeneration (84 tables) | $5-10 | CREATE TABLE operations + compute |
| **PHASE 1: Script Development** | | |
| Script Development & Testing | $0 | Local compute only |
| **PHASE 2: Table Regeneration** | | |
| TRI Regeneration (72 tables) | $40-50 | CREATE TABLE operations + compute (increased due to more columns) |
| COV Regeneration (1,512 tables) | $85-105 | CREATE TABLE operations + compute (increased due to more columns) |
| VAR Regeneration (63 tables) | $15-25 | CREATE TABLE operations + compute (increased due to more columns) |
| **PHASE 3: Validation** | | |
| Validation Queries | $5-10 | Sampling and verification |
| Feature Ledger Regeneration | $10-15 | INFORMATION_SCHEMA queries (more features) |
| **TOTAL** | **$160-220** | One-time cost, correct architecture |

**Budget Status**: Slightly over original estimate ($140-190) due to Phase 0 and additional columns
**Cost Avoidance**: Prevents $200-300 future cost of regenerating non-compliant tables

---

## RISK MITIGATION

### Risk 1: REG Table Regeneration Issues

**Mitigation**:
- Test coefficient calculation on 3 sample tables first
- Verify math: `coef × W^n = term` before full regeneration
- Keep original REG tables until validation passes

### Risk 2: Script Refactoring Errors

**Mitigation**:
- Test each script on 3 sample tables before full deployment
- Incremental testing: 10 tables → 50 tables → full scope
- Keep rollback copies of original scripts

### Risk 3: Table Regeneration Failures

**Mitigation**:
- 16-worker parallelization for fault tolerance
- Automatic retry logic for transient errors
- Monitor error rate; halt if >5% failure
- Sample validation at 25%, 50%, 75% completion

### Risk 4: Data Quality Issues

**Mitigation**:
- Comprehensive validation suite (NULL rates, row counts, value ranges, coef-term consistency)
- Comparison with original table data
- Spot-check 10 tables manually
- Keep original tables until validation passes

### Risk 5: Timeline Overrun

**Mitigation**:
- Realistic time estimates with 20% buffer
- Parallel execution where possible (REG + TRI + COV + VAR regeneration)
- Early identification of bottlenecks
- Checkpoint reporting every 4 hours

---

## ROLLBACK PLAN

**If Critical Issues Arise**:

1. **Stop all table generation immediately**
2. **Preserve original tables** (do not delete until validation passes)
3. **Document specific failure mode**
4. **Revert to original scripts if needed**
5. **Escalate to user for decision**

**Rollback Criteria**:
- Error rate > 10% during regeneration
- Data corruption detected
- Performance degradation > 2x expected
- NULL rates > 5% in regression features
- Coefficient-term math inconsistency > 0.1%

---

## DELIVERABLES

### Code Artifacts
- ✅ `scripts/generate_reg_tables.py` (refactored with 248-column schema including coefficients)
- ✅ `scripts/generate_tri_tables.py` (refactored with 120-column schema)
- ✅ `scripts/generate_cov_tables.py` (refactored with 84-column schema)
- ✅ `scripts/generate_var_tables.py` (refactored with 49-column schema)

### Test Results
- ✅ REG test results (3 test tables)
- ✅ Integration test report (27 test tables)
- ✅ Schema validation results (all tables verified)
- ✅ Data quality metrics (NULL rates, row counts, value ranges, coef-term consistency)

### Regenerated Tables
- ✅ 84 REG tables (248 columns each)
- ✅ 72 TRI tables (120 columns each)
- ✅ 1,512 COV tables (84 columns each)
- ✅ 63 VAR tables (49 columns each)

### Documentation
- ✅ Updated intelligence files (context, ontology, semantics, catalogue, roadmap)
- ✅ Feature ledger (237,668 rows)
- ✅ Compliance verification report
- ✅ This implementation plan (REVISED v2.0)

---

## APPROVAL CHECKPOINTS

### Checkpoint 0: Pre-Execution Approval (USER) - **NEW**
- [ ] Review revised phased plan with Phase 0 (REG table fix)
- [ ] Approve scope and timeline (16-22 hours)
- [ ] Authorize budget ($160-220)
- [ ] Approve HALT of Tier 1
- [ ] Confirm requirement: BOTH coefficient AND term data in all tables

### Checkpoint 1: Post-REG-Fix Approval (CE)
- [ ] Review REG test results (3 test tables)
- [ ] Verify coefficient-term math consistency
- [ ] Authorize TRI/COV/VAR refactoring

### Checkpoint 2: Post-Refactoring Approval (CE)
- [ ] Review integration test results (27 test tables)
- [ ] Approve schema compliance (120/84/49 columns)
- [ ] Authorize full regeneration

### Checkpoint 3: Post-Regeneration Approval (QA)
- [ ] Review validation results
- [ ] Verify schema compliance (100%)
- [ ] Verify data quality
- [ ] Approve feature universe update

### Checkpoint 4: Final Approval (USER)
- [ ] Review compliance status (BQX-ML-M005 FULLY COMPLIANT)
- [ ] Verify BOTH coefficient AND term data present
- [ ] Approve continuation of Step 6
- [ ] Authorize resumption of 25-pair extraction

---

## EXECUTION COMMAND SEQUENCE

**Upon Approval, Execute in Order**:

```bash
# PHASE 0: REG Table Fix (2-3 hours)
# Update REG generation script (manual development)
# Test coefficient calculation
python3 scripts/generate_reg_tables.py --test-only --limit 3

# Regenerate all REG tables
python3 scripts/generate_reg_tables.py --workers 8 > /tmp/reg_regen.log 2>&1 &

# Monitor
tail -f /tmp/reg_regen.log

# PHASE 1: Script Refactoring & Testing (13-19 hours)
# (Manual development work)

# Test TRI script (120 columns)
python3 scripts/generate_tri_tables.py --test-only --workers 1 --limit 3

# Test COV script (84 columns)
python3 scripts/generate_cov_tables.py --test-only --workers 1 --limit 3

# Test VAR script (49 columns)
python3 scripts/generate_var_tables.py --test-only --workers 1 --limit 3

# Integration test (27 tables)
bash scripts/integration_test_reg_mandate.sh

# PHASE 2: Full Regeneration (3-5 hours parallel)
python3 scripts/generate_tri_tables.py --workers 16 > /tmp/tri_regen.log 2>&1 &
python3 scripts/generate_cov_tables.py --workers 16 > /tmp/cov_regen.log 2>&1 &
python3 scripts/generate_var_tables.py --workers 16 > /tmp/var_regen.log 2>&1 &

# Monitor all 3
tail -f /tmp/*_regen.log

# PHASE 3: Validation (1-2 hours)
python3 scripts/validate_reg_mandate_compliance.py --full-audit

# Regenerate feature ledger
python3 scripts/generate_feature_ledger.py --pairs all --horizons all

# PHASE 4: Resume Step 6
# (Continue with Cloud Run pipeline for remaining 25 pairs)
```

---

## CONCLUSION

This revised phased plan provides a comprehensive roadmap to achieve **100% compliance** with the Regression Feature Architecture Mandate (BQX-ML-M005 v2.0).

**KEY REVISIONS FROM v1.0**:
- ✅ Added Phase 0: Fix REG table schemas to include separate coefficient columns
- ✅ Updated TRI schema: 78 → 120 columns (added coefficient features)
- ✅ Updated COV schema: 56 → 84 columns (added coefficient features)
- ✅ Updated VAR schema: 35 → 49 columns (added coefficient features)
- ✅ Updated feature count: +63 → +147 unique features
- ✅ Updated feature ledger: 221,228 → 237,668 rows
- ✅ Updated cost: $140-190 → $160-220
- ✅ Updated timeline: 15.5-23 → 17.5-26.5 hours

**Full Mandate Compliance**:
1. ✅ REG tables will have BOTH coefficient AND term data
2. ✅ TRI/COV/VAR tables will have BOTH coefficient AND term regression features
3. ✅ Complete architectural correctness from the start

**Key Benefits**:
- ✅ Full compliance with P0-CRITICAL mandate (BOTH coef AND term)
- ✅ Correct architecture from the start
- ✅ One-time cost vs. double work later
- ✅ Enhanced feature universe (1,064 → 1,211 features, +147)
- ✅ Clean foundation for model training
- ✅ Mathematical consistency: coef × W^n = term

**Awaiting**: USER APPROVAL to proceed with execution

---

**Implementation Lead**: Chief Engineer (CE)
**Plan Created**: 2025-12-13
**Plan Revised**: 2025-12-13 (v2.0 - Added Phase 0 for REG table compliance)
**Status**: PENDING USER APPROVAL
**Priority**: P0-CRITICAL
