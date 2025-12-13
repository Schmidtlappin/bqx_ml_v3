# MAXIMIZATION IMPLEMENTATION PLAN
**BQX-ML-M006 Execution Roadmap**

**Document Version**: 1.0
**Created**: 2025-12-13 03:30 UTC
**Authority**: Chief Engineer
**Mandates**: BQX-ML-M005 + BQX-ML-M006

---

## EXECUTIVE SUMMARY

This document provides the complete implementation roadmap for executing BQX-ML-M006 (Maximize Feature Comparisons Mandate) in conjunction with BQX-ML-M005 (Regression Feature Architecture Mandate).

**Total Scope**: Transform 1,616 comparison tables → 7,312 tables across 5 phases
**Timeline**: 70-102 hours (3-4 days development + generation)
**Cost**: $1,180-1,620 one-time + $24/month ongoing storage

---

## PHASE 0: REG TABLE GENERATION (PREREQUISITE)

**Status**: IN PROGRESS
**Objective**: Complete regeneration of 84 REG tables with coefficient columns

### Tasks
- [x] Phase 0A: Update REG generation script with coefficient columns
- [x] Phase 0B: Test REG schema on 3 tables
- [ ] Phase 0C: Regenerate all 84 REG tables

### Completion Criteria
- ✅ All 84 REG tables have 248 columns (234 → 248, +14 coefficient columns)
- ✅ Coefficient verification complete (lin_coef, quad_coef verified)
- ✅ Schema validation passed

### Deliverables
- `/home/micha/bqx_ml_v3/scripts/generate_reg_tables_with_coefficients.py`
- `/home/micha/bqx_ml_v3/scripts/regenerate_all_reg_tables.sh`
- `/tmp/reg_coefficient_verification.txt`

**Timeline**: 2-3 hours (generation ongoing)
**Blockers**: None
**Status**: 14/84 tables complete (EURUSD, GBPUSD, USDJPY BQX variants + test tables)

---

## PHASE 1: REGRESSION FEATURE INTEGRATION (BQX-ML-M005)

**Priority**: P0-CRITICAL
**Objective**: Add regression features to ALL TRI/COV/VAR tables
**Deadline**: BEFORE model training launch

### 1.1 COV Script Refactoring

**Current Schema**: 14 columns
**Target Schema**: 62 columns (Phase 1 interim)
**Final Schema**: 104 columns (after Phase 2 window expansion)

**Script**: [scripts/generate_cov_tables.py](scripts/generate_cov_tables.py)

**Changes Required**:

1. Add REG table JOINs (2 per table):
```python
pair1_reg AS (
    SELECT
      interval_time,
      reg_lin_term_45, reg_lin_term_90, ..., reg_lin_term_2880,  # 7 cols
      reg_quad_term_45, reg_quad_term_90, ..., reg_quad_term_2880,  # 7 cols
      reg_residual_45, reg_residual_90, ..., reg_residual_2880  # 7 cols
    FROM `bqx-ml.bqx_ml_v3_features_v2.reg_{source_variant}_{pair1}`
  ),
  pair2_reg AS (...)
```

2. Add 42 regression feature columns to SELECT:
   - pair1_lin_term_45 through pair1_residual_2880 (21 cols)
   - pair2_lin_term_45 through pair2_residual_2880 (21 cols)

3. Add 6 cross-window divergence columns (Phase 1 preview):
   - pair1_short_medium_divergence
   - pair1_medium_long_divergence
   - pair2_short_medium_divergence
   - pair2_medium_long_divergence
   - pair_momentum_divergence_45
   - pair_momentum_divergence_1440

**Testing**: 3 tables (cov_agg_bqx_eurusd_gbpusd, cov_agg_idx_eurusd_gbpusd, cov_align_bqx_audusd_nzdusd)

**Timeline**: 4-6 hours (refactoring + testing)

### 1.2 TRI Script Refactoring

**Current Schema**: 15 columns
**Target Schema**: 84 columns (Phase 1 interim)
**Final Schema**: 126 columns (after Phase 2 window expansion)

**Script**: [scripts/generate_tri_tables.py](scripts/generate_tri_tables.py)

**Changes Required**:

1. Add REG table JOINs (3 per table - one for each triangle leg)
2. Add 63 regression feature columns to SELECT:
   - pair1_lin_term_45 through pair1_residual_2880 (21 cols)
   - pair2_lin_term_45 through pair2_residual_2880 (21 cols)
   - pair3_lin_term_45 through pair3_residual_2880 (21 cols)

3. Add 6 cross-leg divergence columns:
   - leg1_leg2_momentum_divergence_45
   - leg2_leg3_momentum_divergence_45
   - leg1_leg3_momentum_divergence_45
   - triangle_momentum_alignment (all 3 legs)
   - triangle_acceleration_consistency
   - triangle_stability_index (avg residuals)

**Testing**: 3 triangles (tri_agg_bqx_eur_usd_gbp, tri_agg_idx_eur_usd_gbp, tri_align_bqx_aud_usd_nzd)

**Timeline**: 4-6 hours (refactoring + testing)

### 1.3 VAR Script Creation

**Current Schema**: 14 columns
**Target Schema**: 35 columns

**Script**: `scripts/generate_var_tables.py` (NEW - expand from generate_var_usd.py)

**Implementation**:

1. Expand to all 8 currencies (currently only USD)
2. Add aggregated regression features:
```python
# Directionally adjusted aggregation
AVG(reg_lin_term_45 * direction) as family_lin_term_45,  # +1 BASE, -1 QUOTE
AVG(reg_quad_term_45 * direction) as family_quad_term_45,
AVG(reg_residual_45) as family_residual_45,  # Non-directional
...(all 7 windows)...
```

3. Handle currency family membership:
   - EUR: EURUSD (-1), EURGBP (+1), EURJPY (+1), etc.
   - USD: EURUSD (+1), USDJPY (+1), GBPUSD (-1), etc.

**Testing**: 3 currencies (var_agg_bqx_usd, var_agg_idx_eur, var_align_bqx_jpy)

**Timeline**: 3-4 hours (new script development + testing)

### 1.4 Integration Testing

**Objective**: Verify all scripts work correctly before production run

**Test Suite**:

| Script | Test Tables | Validation |
|--------|-------------|------------|
| COV | 6 tables (3 BQX + 3 IDX) | Schema = 62 cols, NULL rate < 5% |
| TRI | 6 tables (3 BQX + 3 IDX) | Schema = 84 cols, triangular arithmetic correct |
| VAR | 6 tables (3 BQX + 3 IDX) | Schema = 35 cols, directional adjustment correct |

**Validation Script**: `scripts/validate_phase1_schemas.py` (NEW)

```python
def validate_cov_schema(table_name):
    """Verify COV table has 62 columns with correct names."""
    expected_columns = [
        'interval_time', 'pair1', 'pair2', 'val1', 'val2',
        'spread', 'ratio', 'spread_ma_45', 'spread_ma_180', ...
        'pair1_lin_term_45', 'pair1_lin_term_90', ...,  # 21 cols
        'pair2_lin_term_45', 'pair2_lin_term_90', ...,  # 21 cols
        'pair1_short_medium_divergence', ...  # 6 cols
    ]
    actual_columns = get_table_schema(table_name)
    assert len(actual_columns) == 62
    assert set(expected_columns).issubset(set(actual_columns))
```

**Timeline**: 2-3 hours

### 1.5 Production Generation

**Execution Order**:
1. COV tables: 1,512 tables (parallel execution, 16 workers)
2. TRI tables: 72 tables (parallel execution, 8 workers)
3. VAR tables: 32 tables (sequential, single worker due to small count)

**Estimated Runtime**:
- COV: 2.5-3.5 hours (1,512 tables × 6-8 sec/table ÷ 16 workers)
- TRI: 0.5-0.75 hours (72 tables × 30-40 sec/table ÷ 8 workers)
- VAR: 0.25-0.5 hours (32 tables × 30-60 sec/table)
- **Total**: 3-5 hours

**Cost**:
- BigQuery processing: $140-180
- Storage: +$10-20
- **Total**: $150-200

**Timeline**: 3-5 hours (generation only, assumes scripts ready)

### Phase 1 Deliverables

- ✅ 1,616 tables regenerated with regression features
- ✅ COV: 1,512 tables × 62 columns
- ✅ TRI: 72 tables × 84 columns
- ✅ VAR: 32 tables × 35 columns
- ✅ BQX-ML-M005 COMPLIANT
- ✅ Ready for model training

**Total Phase 1 Timeline**: 18-24 hours
**Total Phase 1 Cost**: $150-200

---

## PHASE 2: WINDOW EXPANSION

**Priority**: P1-HIGH
**Objective**: Expand base features to all 7 windows
**Depends On**: Phase 1 complete

### 2.1 Window Expansion Implementation

**Changes to ALL scripts** (COV, TRI, VAR):

```sql
-- Add window definitions for all 7 windows
WINDOW
  w45 AS (ORDER BY interval_time ROWS BETWEEN 44 PRECEDING AND CURRENT ROW),
  w90 AS (ORDER BY interval_time ROWS BETWEEN 89 PRECEDING AND CURRENT ROW),
  w180 AS (ORDER BY interval_time ROWS BETWEEN 179 PRECEDING AND CURRENT ROW),
  w360 AS (ORDER BY interval_time ROWS BETWEEN 359 PRECEDING AND CURRENT ROW),
  w720 AS (ORDER BY interval_time ROWS BETWEEN 719 PRECEDING AND CURRENT ROW),
  w1440 AS (ORDER BY interval_time ROWS BETWEEN 1439 PRECEDING AND CURRENT ROW),
  w2880 AS (ORDER BY interval_time ROWS BETWEEN 2879 PRECEDING AND CURRENT ROW)

-- Expand spread statistics
AVG(spread) OVER w45 as spread_ma_45,
AVG(spread) OVER w90 as spread_ma_90,
...(all 7 windows)...,

STDDEV(spread) OVER w45 as spread_std_45,
STDDEV(spread) OVER w90 as spread_std_90,
...(all 7 windows)...
```

**Column Additions**:
- COV: +42 columns (7 windows × 3 metrics × 2 features)
- TRI: +42 columns (similar for error statistics)

**Final Schemas**:
- COV: 62 → 104 columns
- TRI: 84 → 126 columns
- VAR: 35 columns (no change, already uses all windows via regression)

### 2.2 Cross-Window Analytics

Add multi-timeframe features:

```sql
-- Trend alignment score
(
  CASE WHEN spread_ma_45 > 0 THEN 1 ELSE -1 END +
  CASE WHEN spread_ma_90 > 0 THEN 1 ELSE -1 END +
  ... (all 7 windows)
) / 7.0 as spread_trend_alignment,

-- Volatility regime
SAFE_DIVIDE(spread_std_45, NULLIF(spread_std_1440, 0)) as volatility_regime_ratio,

-- Short-long divergence
spread_ma_45 - spread_ma_1440 as short_long_divergence
```

### 2.3 Testing & Generation

**Testing**: Same 18 test tables as Phase 1
**Timeline**: 4-6 hours (script updates + testing)
**Generation**: 2-3 hours (regenerate all 1,616 tables)
**Cost**: $150-200 (full regeneration)

**Total Phase 2 Timeline**: 8-12 hours
**Total Phase 2 Cost**: $150-200

---

## PHASE 3: FEATURE TYPE EXPANSION

**Priority**: P2-MEDIUM
**Objective**: Create comparison tables for ALL feature types
**Depends On**: Phase 1 complete (Phase 2 optional)

### 3.1 New Table Variants

Create 6 new variant types for COV and TRI:

**New COV Variants**:
- `cov_mom_{source_variant}_{pair1}_{pair2}` - Momentum comparisons
- `cov_vol_{source_variant}_{pair1}_{pair2}` - Volatility comparisons
- `cov_der_{source_variant}_{pair1}_{pair2}` - Derivative comparisons
- `cov_rev_{source_variant}_{pair1}_{pair2}` - Reversal comparisons
- `cov_mrt_{source_variant}_{pair1}_{pair2}` - Mean reversion comparisons
- `cov_reg_{source_variant}_{pair1}_{pair2}` - Pure regression comparisons

**New TRI Variants**: Same 6 types

### 3.2 Implementation

**New Scripts**:
- `scripts/generate_cov_mom_tables.py`
- `scripts/generate_cov_vol_tables.py`
- `scripts/generate_tri_mom_tables.py`
- etc. (10 new scripts total)

**Template Pattern**:
```python
def generate_cov_mom_sql(source_variant, pair1, pair2):
    """Generate momentum comparison table."""
    return f"""
    CREATE OR REPLACE TABLE cov_mom_{source_variant}_{pair1}_{pair2}
    AS
    WITH
      pair1_mom AS (
        SELECT * FROM mom_{source_variant}_{pair1}
      ),
      pair2_mom AS (
        SELECT * FROM mom_{source_variant}_{pair2}
      )
    SELECT
      p1.interval_time,
      -- All momentum features from both pairs
      p1.mom_roc_45 as pair1_roc_45, ...,
      p2.mom_roc_45 as pair2_roc_45, ...,
      -- Momentum divergence
      p1.mom_roc_45 - p2.mom_roc_45 as roc_divergence_45, ...
    FROM pair1_mom p1
    JOIN pair2_mom p2 ON p1.interval_time = p2.interval_time
    """
```

### 3.3 Testing & Generation

**Testing**: 3 tables per variant type (30 test tables total)
**Timeline**: 16-24 hours (10 new scripts × 1.5-2.5 hours each)
**Generation**: 4-6 hours (parallel execution of 4,752 new tables)
**Cost**: $500-700

**Table Count Impact**:
- COV: 1,512 → 6,048 tables (+4,536)
- TRI: 72 → 288 tables (+216)
- Total new tables: +4,752

**Total Phase 3 Timeline**: 24-36 hours
**Total Phase 3 Cost**: $500-700

---

## PHASE 4: TRIANGLE EXPANSION

**Priority**: P2-MEDIUM
**Objective**: Generate ALL valid currency triangles
**Depends On**: Phase 1 complete

### 4.1 Triangle Enumeration

**Algorithm**: [scripts/enumerate_all_triangles.py](scripts/enumerate_all_triangles.py) (NEW)

```python
def enumerate_all_valid_triangles():
    """
    Generate all valid triangular arbitrage combinations.

    Returns:
        List of (curr1, curr2, curr3) tuples representing valid triangles
    """
    currencies = {'eur', 'gbp', 'usd', 'jpy', 'aud', 'cad', 'chf', 'nzd'}
    valid_pairs = query_existing_pairs()  # Get from BigQuery

    triangles = []
    for c1, c2, c3 in itertools.combinations(currencies, 3):
        if all_pairs_exist(c1, c2, c3, valid_pairs):
            triangles.append((c1, c2, c3))

    return triangles  # Expected: 56-84 triangles
```

**Verification**: Cross-reference with FX market conventions

### 4.2 Script Update

Update `generate_tri_tables.py` to use enumerated triangles:

```python
# OLD (hardcoded)
TRIANGLES = [
    ('eur', 'usd', 'gbp'),
    ('eur', 'usd', 'jpy'),
    ...(18 manual entries)
]

# NEW (programmatic)
TRIANGLES = enumerate_all_valid_triangles()  # Returns 70+ triangles
```

### 4.3 Testing & Generation

**Testing**: 10 new triangles (20 tables - 10 BQX + 10 IDX)
**Timeline**: 8-12 hours (enumeration + testing + generation)
**Generation**: 4-6 hours (generate ~1,120 tables)
**Cost**: $300-400

**Table Count Impact**:
- TRI (Phase 3): 288 tables
- TRI (Phase 4): 1,120 tables (+832)

**Total Phase 4 Timeline**: 12-18 hours
**Total Phase 4 Cost**: $300-400

---

## PHASE 5: CROSS-FAMILY COMPARISONS

**Priority**: P3-LOW
**Objective**: Currency family vs family comparisons
**Depends On**: Phase 1 complete

### 5.1 Cross-Family Table Design

**New Table Type**: `var_family_cov_{variant}_{source_variant}_{curr1}_{curr2}`

**Example**: EUR vs USD family comparison

```sql
CREATE OR REPLACE TABLE var_family_cov_agg_bqx_eur_usd
AS
SELECT
  v1.interval_time,
  'EUR' as family1,
  'USD' as family2,

  -- EUR family metrics
  v1.family_lin_term_45 as eur_lin_term_45,
  v1.family_quad_term_45 as eur_quad_term_45,

  -- USD family metrics
  v2.family_lin_term_45 as usd_lin_term_45,
  v2.family_quad_term_45 as usd_quad_term_45,

  -- Cross-family divergence
  v1.family_lin_term_45 - v2.family_lin_term_45 as momentum_divergence_45,

  -- Relative strength
  SAFE_DIVIDE(v1.family_lin_term_45, v2.family_lin_term_45) as relative_strength_45

FROM var_agg_bqx_eur v1
JOIN var_agg_bqx_usd v2 ON v1.interval_time = v2.interval_time
```

### 5.2 Implementation

**Script**: `scripts/generate_var_family_cov_tables.py` (NEW)

**Cross-family combinations**: C(8,2) = 28 combinations
- EUR-USD, EUR-GBP, EUR-JPY, EUR-AUD, EUR-CAD, EUR-CHF, EUR-NZD
- USD-GBP, USD-JPY, USD-AUD, USD-CAD, USD-CHF, USD-NZD
- GBP-JPY, GBP-AUD, GBP-CAD, GBP-CHF, GBP-NZD
- JPY-AUD, JPY-CAD, JPY-CHF, JPY-NZD
- AUD-CAD, AUD-CHF, AUD-NZD
- CAD-CHF, CAD-NZD
- CHF-NZD

### 5.3 Testing & Generation

**Testing**: 6 family pairs (12 tables)
**Timeline**: 6-9 hours (new script + testing + generation)
**Generation**: 2-3 hours (generate 112 tables)
**Cost**: $80-120

**Table Count Impact**:
- VAR (current): 32 tables
- VAR (Phase 5): 144 tables (+112)

**Total Phase 5 Timeline**: 8-12 hours
**Total Phase 5 Cost**: $80-120

---

## COMPREHENSIVE TIMELINE & COST SUMMARY

| Phase | Description | Timeline | Cost | Tables | Cumulative |
|-------|-------------|----------|------|--------|------------|
| **Phase 0** | REG tables (prerequisite) | 2-3h | $10 | 84 | 84 |
| **Phase 1** | Regression integration (M005) | 18-24h | $150-200 | 1,616 | 1,700 |
| **Phase 2** | Window expansion | 8-12h | $150-200 | 1,616 | 1,700 |
| **Phase 3** | Feature type expansion | 24-36h | $500-700 | 6,368 | 8,068 |
| **Phase 4** | Triangle expansion | 12-18h | $300-400 | 7,200 | 15,268 |
| **Phase 5** | Cross-family comparisons | 8-12h | $80-120 | 7,312 | 15,396 |
| **TOTAL** | **All phases** | **70-102h** | **$1,180-1,620** | **7,312** | **15,396** |

**Storage Cost**: +1,600 GB → +$24/month ongoing

---

## EXECUTION RECOMMENDATION

### Option A: Full Implementation (All 5 Phases)

**Pros**:
- ✅ Complete feature universe
- ✅ Maximum ML capability
- ✅ Future-proof architecture

**Cons**:
- ⏱️ 70-102 hours development time
- 💰 $1,180-1,620 cost
- 📊 7,312 tables to manage

**Recommendation**: Only if timeline allows 3-4 days development

### Option B: Phased Approach (Phase 1-2 Now, 3-5 Later)

**Pros**:
- ✅ Immediate compliance (M005 + M006 Phase 1)
- ✅ Lower initial cost ($300-400)
- ✅ Can start model training sooner
- ✅ Phases 3-5 add incremental value later

**Cons**:
- ⏱️ Will need to regenerate tables for Phases 3-5
- 💰 Higher total cost if all phases done eventually

**Recommendation**: **STRONGLY RECOMMENDED**
- Execute Phase 1-2 immediately (26-36 hours)
- Evaluate Phases 3-5 after initial model results
- Defer if model accuracy sufficient with Phase 1-2 features

### Option C: Phase 1 Only (Minimum Compliance)

**Pros**:
- ✅ Fastest path to compliance
- ✅ Lowest cost ($150-200)
- ✅ Can start training immediately

**Cons**:
- ❌ Only 2 windows used (w45, w180)
- ❌ Missing multi-timeframe features
- ❌ Lower ML performance

**Recommendation**: NOT RECOMMENDED
- Phase 2 window expansion is critical for ML
- Marginal additional cost ($150-200) for significant ML gain

---

## DECISION MATRIX

| Criterion | Option A (All) | Option B (1-2) | Option C (1 only) |
|-----------|---------------|----------------|-------------------|
| **Time to Training** | 70-102 hours | 26-36 hours | 18-24 hours |
| **Initial Cost** | $1,180-1,620 | $300-400 | $150-200 |
| **Feature Completeness** | 100% | 60% | 40% |
| **ML Performance** | Maximum | High | Medium |
| **Future-Proof** | Yes | Moderate | No |
| **Recommended** | ⭐⭐ (if time allows) | ⭐⭐⭐ (BEST) | ⭐ (not ideal) |

---

## NEXT STEPS (IMMEDIATE)

1. ✅ Complete Phase 0C (REG table regeneration)
2. ✅ Refactor COV script for Phase 1
3. ✅ Refactor TRI script for Phase 1
4. ✅ Create VAR script for Phase 1
5. ✅ Run integration tests (18 tables)
6. ✅ Execute Phase 1 production generation (1,616 tables)
7. ✅ Validate Phase 1 compliance
8. ⏸️ **DECISION POINT**: Proceed to Phase 2 or start model training?

---

**Document Status**: ACTIVE
**Owner**: Chief Engineer
**Review Date**: After Phase 1 completion
**Approval Required**: User decision on Phases 3-5 execution timing
