# CE Directive: Additional Feature Implementation Plan

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 07:00 UTC
**Priority**: MEDIUM (After cov_* completion)
**Subject**: Implementation of 7 Additional Feature Types for Oscillation Prediction

---

## DIRECTIVE SUMMARY

Implement 7 new feature types (280 tables) optimized for oscillating BQX prediction and game theory trading strategy.

### Prerequisites
- **MUST COMPLETE**: Current cov_* remediation (1,798 tables)
- **DO NOT START** until cov_* remediation is 100% validated

---

## PHASE SCHEDULE

| Phase | Feature Types | Tables | Priority | Start Condition |
|-------|---------------|--------|----------|-----------------|
| 0 (Current) | cov_* | 1,798 | CRITICAL | IN PROGRESS |
| 1 | rev_, der_ | 112 | HIGH | After Phase 0 complete |
| 2 | ext_, cyc_ | 56 | MEDIUM | After Phase 1 complete |
| 3 | div_, mrt_ | 84 | MEDIUM | After Phase 2 complete |
| 4 | tmp_ | 28 | LOW | After Phase 3 complete |

---

## PHASE 1: REVERSAL & DERIVATIVE (112 tables)

### 1.1 Reversal Detection (rev_) - 56 tables

**Purpose**: Detect when BQX oscillation is about to change direction

**Tables**:
```
rev_{pair}           # IDX variant (28 tables)
rev_bqx_{pair}       # BQX variant (28 tables)
```

**Key Columns** (per table):
- rev_decel_{W} for W in [45, 90, 180, 360, 720, 1440, 2880]
- rev_exhaustion (composite score)
- rev_divergence (price-momentum divergence)
- rev_turning_prob (probability of direction change)

**SQL Pattern** (Interval-Centric):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.rev_bqx_{pair}` AS
SELECT
  interval_id,
  -- Deceleration: Second derivative
  (bqx_45 - LAG(bqx_45, 1) OVER w) - LAG(bqx_45 - LAG(bqx_45, 1) OVER w, 1) OVER w AS rev_decel_45,
  -- ... repeat for other windows
  -- Exhaustion score
  ABS(bqx_composite) * SIGN(rev_decel_composite) * -1 AS rev_exhaustion
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}`
WINDOW w AS (ORDER BY interval_id)
```

### 1.2 Derivative (der_) - 56 tables

**Purpose**: Velocity and acceleration of BQX changes

**Tables**:
```
der_{pair}           # IDX variant (28 tables)
der_bqx_{pair}       # BQX variant (28 tables)
```

**Key Columns**:
- der_v1_{W} (first derivative/velocity)
- der_v2_{W} (second derivative/acceleration)
- der_v3_composite (third derivative/jerk)

**SQL Pattern** (Interval-Centric):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.der_bqx_{pair}` AS
SELECT
  interval_id,
  -- First derivative (velocity)
  bqx_45 - LAG(bqx_45, 1) OVER w AS der_v1_45,
  -- Second derivative (acceleration)
  (bqx_45 - LAG(bqx_45, 1) OVER w) - LAG(bqx_45 - LAG(bqx_45, 1) OVER w, 1) OVER w AS der_v2_45,
  -- ... repeat for other windows
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}`
WINDOW w AS (ORDER BY interval_id)
```

---

## PHASE 2: EXTREMITY & CYCLE (56 tables)

### 2.1 Extremity Metrics (ext_) - 28 tables (BQX ONLY)

**Purpose**: Quantify how extreme current BQX is

**Tables**:
```
ext_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Key Columns**:
- ext_zscore_{W} (z-score vs rolling window)
- ext_percentile_{W} (percentile rank 0-100)
- ext_distance_zero (absolute distance from equilibrium)
- ext_sigma_band (discrete band -3 to +3)

**SQL Pattern** (Interval-Centric):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.ext_bqx_{pair}` AS
SELECT
  interval_id,
  (bqx_45 - AVG(bqx_45) OVER (ORDER BY interval_id ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING))
    / NULLIF(STDDEV(bqx_45) OVER (ORDER BY interval_id ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING), 0)
    AS ext_zscore_45,
  -- ... repeat for other windows
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}`
```

### 2.2 Cycle Position (cyc_) - 28 tables (BQX ONLY)

**Purpose**: Position in BQX oscillation cycle

**Tables**:
```
cyc_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Key Columns**:
- cyc_intervals_since_zero (intervals since last zero crossing)
- cyc_intervals_since_ext (intervals since last extreme)
- cyc_avg_cycle_length (rolling average cycle duration)
- cyc_current_cycle_progress (estimated % through cycle)

**Note**: Requires tracking zero-crossings - implement as multi-step query.

---

## PHASE 3: DIVERGENCE & TENSION (84 tables)

### 3.1 Cross-Window Divergence (div_) - 56 tables

**Purpose**: Detect disagreement between BQX windows

**Tables**:
```
div_{pair}           # IDX variant (28 tables)
div_bqx_{pair}       # BQX variant (28 tables)
```

**Key Columns**:
- div_45_2880 (short vs long divergence)
- div_sign_alignment (count of aligned signs)
- div_cascade_direction (predicted reversal direction)
- div_short_leading (boolean: short reversed first?)

**SQL Pattern** (Interval-Centric):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.div_bqx_{pair}` AS
SELECT
  interval_id,
  bqx_45 - bqx_2880 AS div_45_2880,
  (CASE WHEN SIGN(bqx_45) = SIGN(bqx_90) THEN 1 ELSE 0 END +
   CASE WHEN SIGN(bqx_90) = SIGN(bqx_180) THEN 1 ELSE 0 END +
   -- ... continue for all adjacent pairs
  ) AS div_sign_alignment
FROM `bqx-ml.bqx_ml_v3_features.lag_bqx_{pair}`
```

### 3.2 Mean-Reversion Tension (mrt_) - 28 tables (BQX ONLY)

**Purpose**: Quantify spring force pulling BQX to zero

**Tables**:
```
mrt_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Key Columns**:
- mrt_tension_{W} (reversion tension per window)
- mrt_tension_composite (weighted composite)
- mrt_half_life (estimated decay half-life)
- mrt_reversion_probability (logistic probability)

---

## PHASE 4: TEMPORAL (28 tables)

### 4.1 Temporal Patterns (tmp_) - 28 tables (TIME-CENTRIC EXCEPTION)

**Purpose**: Calendar and session effects

**Tables**:
```
tmp_{pair}           # Per-pair (28 tables) - No variant
```

**Architecture Note**: This is the ONLY time-centric feature type. Extracts time metadata but does NOT use time-based windows.

**Key Columns**:
- tmp_hour_utc (0-23)
- tmp_day_of_week (0-6)
- tmp_is_london, tmp_is_ny, tmp_is_asian (boolean)
- tmp_is_overlap_london_ny (boolean)
- tmp_session_phase (categorical)

**SQL Pattern** (Time-Based Extraction):
```sql
CREATE TABLE `bqx-ml.bqx_ml_v3_features.tmp_{pair}` AS
SELECT
  interval_id,
  EXTRACT(HOUR FROM timestamp) AS tmp_hour_utc,
  EXTRACT(DAYOFWEEK FROM timestamp) - 1 AS tmp_day_of_week,
  EXTRACT(HOUR FROM timestamp) >= 8 AND EXTRACT(HOUR FROM timestamp) < 16 AS tmp_is_london,
  EXTRACT(HOUR FROM timestamp) >= 13 AND EXTRACT(HOUR FROM timestamp) < 21 AS tmp_is_ny,
  -- ... other extractions
FROM `bqx-ml.bqx_bq_uscen1.m1_{pair}`
```

---

## VALIDATION REQUIREMENTS

### Per-Table Validation

| Check | Criterion | Action if Fail |
|-------|-----------|----------------|
| Row count | Matches source (2.17M) | Investigate join |
| Null rate | < 5% per column | Check formula edge cases |
| Value range | Within expected bounds | Review calculation |

### Per-Phase Validation

| Check | Criterion |
|-------|-----------|
| Table count | Matches specification |
| All pairs covered | 28 pairs per table type |
| IDX/BQX parity | Same row counts |

---

## REPORTING REQUIREMENTS

### Progress Reports
Send status report after completing each phase:
1. Tables created (count + list)
2. Validation results
3. Any issues encountered
4. ETA for next phase

### Completion Report
After all phases complete:
1. Full table inventory (280 tables)
2. Validation summary
3. Total execution time
4. Recommendations for optimization

---

## REFERENCE DOCUMENTS

1. **[/mandate/ADDITIONAL_FEATURE_SPECIFICATION.md](../../../mandate/ADDITIONAL_FEATURE_SPECIFICATION.md)** - Complete column definitions, SQL templates
2. **[/mandate/FEATURE_TABLE_DIRECTORY.md](../../../mandate/FEATURE_TABLE_DIRECTORY.md)** - Updated directory with all tables

---

## AUTHORIZATION

This directive is authorized by the Chief Engineer.

**Execution Model**: SEQUENTIAL (complete each phase before starting next)
**Priority**: MEDIUM (after current cov_* remediation)
**Mandate Alignment**: PERFORMANCE_FIRST, GAME_THEORY_OPTIMIZATION

---

*Directive issued: 2025-11-29 07:00 UTC*
*Chief Engineer, BQX ML V3*
