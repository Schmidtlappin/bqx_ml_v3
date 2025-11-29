# Additional Feature Type Specification for BQX ML V3

## Optimized for Oscillating BQX Prediction and Game Theory Trading

**Document Version**: 1.0.0
**Created**: 2025-11-29
**Author**: BQXML Chief Engineer
**Classification**: MANDATE - Feature Engineering Reference

---

## EXECUTIVE SUMMARY

This document specifies 7 additional feature types designed to enhance BQX ML V3's ability to:
1. **Detect reversals** in oscillating BQX values
2. **Predict extremes** (|BQX| > 2σ) with high precision
3. **Capture cycle dynamics** of mean-reverting behavior
4. **Support game theory trading** strategy execution

### Feature Type Summary

| Type | Name | Variant | Tables | Architecture | Purpose |
|------|------|---------|--------|--------------|---------|
| rev_ | Reversal Detection | IDX + BQX | 56 | INTERVAL-CENTRIC | Detect momentum exhaustion |
| der_ | Derivative | IDX + BQX | 56 | INTERVAL-CENTRIC | Velocity/acceleration of change |
| ext_ | Extremity Metrics | BQX only | 28 | INTERVAL-CENTRIC | Quantify how extreme BQX is |
| cyc_ | Cycle Position | BQX only | 28 | INTERVAL-CENTRIC | Position in oscillation cycle |
| div_ | Cross-Window Divergence | IDX + BQX | 56 | INTERVAL-CENTRIC | Detect window disagreement |
| mrt_ | Mean-Reversion Tension | BQX only | 28 | INTERVAL-CENTRIC | Quantify reversion force |
| tmp_ | Temporal Patterns | Per-pair | 28 | **TIME-CENTRIC** | Session/calendar effects |

**Total New Tables: 280**

---

## ARCHITECTURAL PRINCIPLES

### Interval-Centric Computation (6 of 7 types)

All calculations use `ROWS BETWEEN` clauses, NOT time-based windows:

```sql
-- CORRECT (Interval-Centric)
AVG(bqx_45) OVER (ORDER BY interval_id ROWS BETWEEN 45 PRECEDING AND 1 PRECEDING)

-- INCORRECT (Time-Centric) - DO NOT USE except for tmp_
AVG(bqx_45) OVER (ORDER BY timestamp RANGE BETWEEN INTERVAL '45 minutes' PRECEDING AND CURRENT ROW)
```

### Time-Centric Exception (tmp_ only)

The `tmp_` feature type is the **sole exception** to interval-centric architecture:
- Captures calendar/session effects that are inherently time-based
- Encoded as row metadata (each row knows its timestamp)
- Does NOT use time-based window functions
- Simply extracts time components from each row's timestamp

### IDX vs BQX Variant Logic

| Feature Type | IDX Variant | BQX Variant | Rationale |
|--------------|-------------|-------------|-----------|
| rev_ | Price-based reversal signals | Momentum-based reversal signals | Both provide value |
| der_ | Price velocity/acceleration | BQX velocity/acceleration | Both provide value |
| ext_ | N/A | BQX extremity only | Extremity is about BQX, not price |
| cyc_ | N/A | BQX cycle only | Cycles are in BQX oscillation |
| div_ | Price window divergence | BQX window divergence | Both provide value |
| mrt_ | N/A | BQX tension only | Tension is about BQX reversion |
| tmp_ | N/A | N/A | Time is universal |

---

## FEATURE TYPE 1: REVERSAL DETECTION (rev_)

### Purpose
Detect when BQX oscillation is about to change direction - critical for game theory timing.

### Game Theory Value
- Predicts WHEN momentum traders will exit
- Enables entry BEFORE reversal (not reaction)
- Highest ROI feature type for contrarian strategy

### Table Structure

```
rev_{pair}           # IDX variant (28 tables)
rev_bqx_{pair}       # BQX variant (28 tables)
```

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| rev_decel_45 | FLOAT64 | Deceleration in bqx_45 | See formula |
| rev_decel_90 | FLOAT64 | Deceleration in bqx_90 | See formula |
| rev_decel_180 | FLOAT64 | Deceleration in bqx_180 | See formula |
| rev_decel_360 | FLOAT64 | Deceleration in bqx_360 | See formula |
| rev_decel_720 | FLOAT64 | Deceleration in bqx_720 | See formula |
| rev_decel_1440 | FLOAT64 | Deceleration in bqx_1440 | See formula |
| rev_decel_2880 | FLOAT64 | Deceleration in bqx_2880 | See formula |
| rev_exhaustion | FLOAT64 | Composite exhaustion score | See formula |
| rev_divergence | FLOAT64 | Price-momentum divergence | See formula |
| rev_turning_prob | FLOAT64 | Probability of direction change | See formula |

### SQL Formulas (Interval-Centric)

```sql
-- Deceleration: Second derivative (acceleration of BQX change)
-- Positive deceleration during positive BQX = slowing momentum = reversal signal
rev_decel_{W} = (
  (bqx_{W} - LAG(bqx_{W}, 1) OVER (ORDER BY interval_id))
  - LAG(bqx_{W} - LAG(bqx_{W}, 1) OVER (ORDER BY interval_id), 1) OVER (ORDER BY interval_id)
)

-- Exhaustion Score: Combination of high magnitude + decelerating
rev_exhaustion = ABS(bqx_composite) * SIGN(rev_decel_composite) * -1
-- High when: Large BQX AND decelerating toward zero

-- Price-Momentum Divergence (IDX variant only)
rev_divergence = CORR(close_change, bqx_change) OVER (ROWS BETWEEN 20 PRECEDING AND CURRENT ROW)
-- Low/negative correlation = divergence = reversal signal

-- Turning Probability (logistic transformation)
rev_turning_prob = 1 / (1 + EXP(-1 * (rev_exhaustion / STDDEV(rev_exhaustion))))
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| High exhaustion | rev_exhaustion > 1.5 | Momentum traders overextended |
| Negative decel at +BQX | rev_decel < 0 AND bqx > 1σ | Upward momentum slowing |
| Positive decel at -BQX | rev_decel > 0 AND bqx < -1σ | Downward momentum slowing |
| High turning prob | rev_turning_prob > 0.7 | 70%+ chance of reversal |

---

## FEATURE TYPE 2: DERIVATIVE (der_)

### Purpose
Capture velocity and acceleration of BQX changes - rate information not in raw values.

### Game Theory Value
- Velocity tells HOW FAST momentum is building/fading
- Acceleration tells if momentum is gaining or losing steam
- Jerk (third derivative) captures sudden changes before they manifest

### Table Structure

```
der_{pair}           # IDX variant (28 tables)
der_bqx_{pair}       # BQX variant (28 tables)
```

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| der_v1_45 | FLOAT64 | First derivative (velocity) bqx_45 | d(bqx)/d(interval) |
| der_v1_90 | FLOAT64 | First derivative bqx_90 | d(bqx)/d(interval) |
| der_v1_180 | FLOAT64 | First derivative bqx_180 | d(bqx)/d(interval) |
| der_v1_360 | FLOAT64 | First derivative bqx_360 | d(bqx)/d(interval) |
| der_v1_720 | FLOAT64 | First derivative bqx_720 | d(bqx)/d(interval) |
| der_v1_1440 | FLOAT64 | First derivative bqx_1440 | d(bqx)/d(interval) |
| der_v1_2880 | FLOAT64 | First derivative bqx_2880 | d(bqx)/d(interval) |
| der_v2_45 | FLOAT64 | Second derivative (acceleration) bqx_45 | d²(bqx)/d(interval)² |
| der_v2_90 | FLOAT64 | Second derivative bqx_90 | d²(bqx)/d(interval)² |
| der_v2_180 | FLOAT64 | Second derivative bqx_180 | d²(bqx)/d(interval)² |
| der_v2_360 | FLOAT64 | Second derivative bqx_360 | d²(bqx)/d(interval)² |
| der_v2_720 | FLOAT64 | Second derivative bqx_720 | d²(bqx)/d(interval)² |
| der_v2_1440 | FLOAT64 | Second derivative bqx_1440 | d²(bqx)/d(interval)² |
| der_v2_2880 | FLOAT64 | Second derivative bqx_2880 | d²(bqx)/d(interval)² |
| der_v3_composite | FLOAT64 | Third derivative (jerk) composite | d³(bqx)/d(interval)³ |

### SQL Formulas (Interval-Centric)

```sql
-- First Derivative (Velocity): Change per interval
der_v1_{W} = bqx_{W} - LAG(bqx_{W}, 1) OVER (ORDER BY interval_id)

-- Second Derivative (Acceleration): Change of velocity per interval
der_v2_{W} = der_v1_{W} - LAG(der_v1_{W}, 1) OVER (ORDER BY interval_id)

-- Third Derivative (Jerk): Change of acceleration per interval
der_v3_composite = der_v2_composite - LAG(der_v2_composite, 1) OVER (ORDER BY interval_id)

-- Smoothed versions (optional, reduces noise)
der_v1_{W}_smooth = AVG(der_v1_{W}) OVER (ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| High positive velocity | der_v1 > 2σ | Momentum building rapidly |
| Negative acceleration at +BQX | der_v2 < 0 AND bqx > 0 | Upward momentum decelerating |
| Positive acceleration at -BQX | der_v2 > 0 AND bqx < 0 | Downward momentum decelerating |
| Large jerk | |der_v3| > 3σ | Sudden change imminent |

---

## FEATURE TYPE 3: EXTREMITY METRICS (ext_)

### Purpose
Quantify how extreme current BQX is relative to recent and historical distributions.

### Game Theory Value
- Extremes are where contrarian strategy acts (|BQX| > 1σ)
- "How extreme" directly informs position sizing
- Features that predict extremity = features that predict opportunity

### Table Structure

```
ext_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - extremity is specifically about BQX values, not price.

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| ext_zscore_45 | FLOAT64 | Z-score of bqx_45 vs rolling 720 | (bqx - mean) / std |
| ext_zscore_90 | FLOAT64 | Z-score of bqx_90 | (bqx - mean) / std |
| ext_zscore_180 | FLOAT64 | Z-score of bqx_180 | (bqx - mean) / std |
| ext_zscore_360 | FLOAT64 | Z-score of bqx_360 | (bqx - mean) / std |
| ext_zscore_720 | FLOAT64 | Z-score of bqx_720 | (bqx - mean) / std |
| ext_zscore_1440 | FLOAT64 | Z-score of bqx_1440 | (bqx - mean) / std |
| ext_zscore_2880 | FLOAT64 | Z-score of bqx_2880 | (bqx - mean) / std |
| ext_percentile_45 | FLOAT64 | Percentile rank (0-100) bqx_45 | PERCENT_RANK |
| ext_percentile_90 | FLOAT64 | Percentile rank bqx_90 | PERCENT_RANK |
| ext_percentile_composite | FLOAT64 | Composite percentile | AVG across windows |
| ext_distance_zero | FLOAT64 | Absolute distance from zero | ABS(bqx_composite) |
| ext_sigma_band | INT64 | Which sigma band (-3 to +3) | FLOOR(zscore) |
| ext_historical_rank | FLOAT64 | Rank vs all-time distribution | PERCENT_RANK vs all |

### SQL Formulas (Interval-Centric)

```sql
-- Z-Score: Rolling standardization
ext_zscore_{W} = (
  bqx_{W} - AVG(bqx_{W}) OVER (ORDER BY interval_id ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING)
) / NULLIF(STDDEV(bqx_{W}) OVER (ORDER BY interval_id ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING), 0)

-- Percentile Rank: Position in recent distribution
ext_percentile_{W} = PERCENT_RANK() OVER (
  ORDER BY bqx_{W}
  ROWS BETWEEN 2880 PRECEDING AND CURRENT ROW
) * 100

-- Sigma Band: Discrete categorization
ext_sigma_band = CASE
  WHEN ext_zscore_composite >= 3 THEN 3
  WHEN ext_zscore_composite >= 2 THEN 2
  WHEN ext_zscore_composite >= 1 THEN 1
  WHEN ext_zscore_composite >= -1 THEN 0
  WHEN ext_zscore_composite >= -2 THEN -1
  WHEN ext_zscore_composite >= -3 THEN -2
  ELSE -3
END

-- Distance from equilibrium
ext_distance_zero = ABS(AVG(bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880))
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| High z-score | |ext_zscore| > 2 | In extreme territory |
| Extreme percentile | ext_percentile < 5 OR > 95 | Rare event, high reversion prob |
| Sigma band ±2 or ±3 | ext_sigma_band IN (-3,-2,2,3) | Maximum position sizing |
| Large distance | ext_distance_zero > 2σ | Strong reversion force |

---

## FEATURE TYPE 4: CYCLE POSITION (cyc_)

### Purpose
Identify where BQX is in its oscillation cycle - timing optimization.

### Game Theory Value
- Oscillations have rhythm - knowing position is predictive
- "How long can this continue?" - cycle duration informs probability
- Mean-reversion probability increases with cycle duration

### Table Structure

```
cyc_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - cycles are in BQX oscillation, not price.

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| cyc_intervals_since_zero | INT64 | Intervals since last zero crossing | COUNT since sign change |
| cyc_intervals_since_ext | INT64 | Intervals since last |BQX| > 2σ | COUNT since extreme |
| cyc_intervals_in_positive | INT64 | Consecutive intervals BQX > 0 | Running count |
| cyc_intervals_in_negative | INT64 | Consecutive intervals BQX < 0 | Running count |
| cyc_avg_cycle_length | FLOAT64 | Rolling average full cycle length | AVG of cycle durations |
| cyc_current_cycle_progress | FLOAT64 | Estimated % through current cycle | current / avg_length |
| cyc_phase_45 | FLOAT64 | Phase angle (0-360) for bqx_45 | Hilbert transform proxy |
| cyc_phase_composite | FLOAT64 | Composite phase across windows | Weighted average |
| cyc_half_cycle_complete | BOOLEAN | Past midpoint of expected cycle | progress > 0.5 |

### SQL Formulas (Interval-Centric)

```sql
-- Intervals since zero crossing
cyc_intervals_since_zero = ROW_NUMBER() OVER (
  PARTITION BY SIGN(bqx_composite) = LAG(SIGN(bqx_composite)) OVER (ORDER BY interval_id)
  ORDER BY interval_id
)

-- Alternative: Using window functions
cyc_intervals_since_zero = interval_id - MAX(CASE WHEN SIGN(bqx_composite) != SIGN(LAG(bqx_composite)) THEN interval_id END) OVER (ORDER BY interval_id ROWS UNBOUNDED PRECEDING)

-- Intervals since extreme
cyc_intervals_since_ext = interval_id - MAX(CASE WHEN ABS(ext_zscore_composite) > 2 THEN interval_id END) OVER (ORDER BY interval_id ROWS UNBOUNDED PRECEDING)

-- Average cycle length (rolling)
cyc_avg_cycle_length = AVG(cycle_duration) OVER (ORDER BY interval_id ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING)
-- Where cycle_duration = intervals between consecutive zero crossings

-- Cycle progress
cyc_current_cycle_progress = cyc_intervals_since_zero / NULLIF(cyc_avg_cycle_length, 0)

-- Phase estimation (simplified - not true Hilbert transform)
cyc_phase_45 = ATAN2(
  bqx_45 - LAG(bqx_45, 5) OVER (ORDER BY interval_id),
  bqx_45
) * 180 / 3.14159 + 180
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| Long cycle duration | cyc_intervals_since_zero > 1.5 * avg | Extended trend, reversion imminent |
| Near cycle end | cyc_current_cycle_progress > 0.8 | High probability of reversal |
| Long time since extreme | cyc_intervals_since_ext > 500 | Extreme may be approaching |
| Phase near 180° or 360° | cyc_phase near turning points | Cycle turning |

---

## FEATURE TYPE 5: CROSS-WINDOW DIVERGENCE (div_)

### Purpose
Detect disagreement between BQX windows - early warning for reversals.

### Game Theory Value
- Short-term window reversing while long-term still extreme = leading indicator
- Alignment = trend strength; Divergence = transition coming
- Cross-window divergence often precedes direction changes by 5-15 intervals

### Table Structure

```
div_{pair}           # IDX variant (28 tables)
div_bqx_{pair}       # BQX variant (28 tables)
```

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| div_45_2880 | FLOAT64 | Divergence between shortest and longest | bqx_45 - bqx_2880 |
| div_45_720 | FLOAT64 | Short vs medium divergence | bqx_45 - bqx_720 |
| div_90_1440 | FLOAT64 | Medium divergence | bqx_90 - bqx_1440 |
| div_180_2880 | FLOAT64 | Medium-long divergence | bqx_180 - bqx_2880 |
| div_sign_alignment | INT64 | Count of windows with same sign | COUNT matching signs |
| div_alignment_score | FLOAT64 | Correlation across all windows | CORR matrix score |
| div_cascade_direction | INT64 | Are shorter windows leading? | Sign comparison |
| div_short_leading | BOOLEAN | bqx_45 reversed before bqx_2880 | Comparison |
| div_spread_zscore | FLOAT64 | Z-score of current spread | Standardized spread |

### SQL Formulas (Interval-Centric)

```sql
-- Simple divergence (same row, different windows)
div_45_2880 = bqx_45 - bqx_2880

-- Sign alignment count
div_sign_alignment = (
  CASE WHEN SIGN(bqx_45) = SIGN(bqx_90) THEN 1 ELSE 0 END +
  CASE WHEN SIGN(bqx_90) = SIGN(bqx_180) THEN 1 ELSE 0 END +
  CASE WHEN SIGN(bqx_180) = SIGN(bqx_360) THEN 1 ELSE 0 END +
  CASE WHEN SIGN(bqx_360) = SIGN(bqx_720) THEN 1 ELSE 0 END +
  CASE WHEN SIGN(bqx_720) = SIGN(bqx_1440) THEN 1 ELSE 0 END +
  CASE WHEN SIGN(bqx_1440) = SIGN(bqx_2880) THEN 1 ELSE 0 END
)
-- Range: 0 (all different) to 6 (all aligned)

-- Alignment score (simplified)
div_alignment_score = div_sign_alignment / 6.0

-- Cascade detection: Shorter windows reversing first
div_cascade_direction = CASE
  WHEN SIGN(bqx_45) != SIGN(bqx_2880) AND ABS(bqx_45) < ABS(bqx_2880) THEN SIGN(bqx_2880) * -1
  ELSE 0
END
-- Returns expected reversal direction

-- Short leading indicator
div_short_leading = (
  SIGN(bqx_45) != SIGN(LAG(bqx_45, 5) OVER (ORDER BY interval_id))
  AND SIGN(bqx_2880) = SIGN(LAG(bqx_2880, 5) OVER (ORDER BY interval_id))
)

-- Spread z-score
div_spread_zscore = (
  div_45_2880 - AVG(div_45_2880) OVER (ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING)
) / NULLIF(STDDEV(div_45_2880) OVER (ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING), 0)
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| Low alignment | div_alignment_score < 0.5 | Windows disagreeing, transition |
| Short leading | div_short_leading = TRUE | bqx_45 reversed, others will follow |
| Large spread | |div_45_2880| > 2σ | Short and long term diverged |
| Cascade signal | div_cascade_direction != 0 | Reversal direction predicted |

---

## FEATURE TYPE 6: MEAN-REVERSION TENSION (mrt_)

### Purpose
Quantify the "spring force" pulling BQX back to zero.

### Game Theory Value
- Mean-reversion is the CORE of contrarian strategy
- "Tension" increases as BQX gets more extreme
- Quantifying tension = quantifying opportunity magnitude

### Table Structure

```
mrt_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - tension is about BQX mean-reversion, not price.

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| mrt_tension_45 | FLOAT64 | Reversion tension for bqx_45 | See formula |
| mrt_tension_90 | FLOAT64 | Reversion tension for bqx_90 | See formula |
| mrt_tension_180 | FLOAT64 | Reversion tension for bqx_180 | See formula |
| mrt_tension_360 | FLOAT64 | Reversion tension for bqx_360 | See formula |
| mrt_tension_720 | FLOAT64 | Reversion tension for bqx_720 | See formula |
| mrt_tension_1440 | FLOAT64 | Reversion tension for bqx_1440 | See formula |
| mrt_tension_2880 | FLOAT64 | Reversion tension for bqx_2880 | See formula |
| mrt_tension_composite | FLOAT64 | Weighted composite tension | Weighted avg |
| mrt_half_life | FLOAT64 | Estimated half-life of deviation | Decay analysis |
| mrt_expected_reversion | FLOAT64 | Expected intervals to zero | Regression est |
| mrt_reversion_probability | FLOAT64 | Prob of reverting in H intervals | Logistic |

### SQL Formulas (Interval-Centric)

```sql
-- Tension: |BQX| × historical decay rate
-- Higher tension = larger deviation AND historically fast reversion
mrt_tension_{W} = ABS(bqx_{W}) * (
  1 - CORR(bqx_{W}, LAG(bqx_{W}, 1)) OVER (ROWS BETWEEN 720 PRECEDING AND 1 PRECEDING)
)
-- Tension high when: BQX far from zero AND autocorrelation is low (fast reversion)

-- Alternative: Ornstein-Uhlenbeck inspired
-- θ = mean-reversion speed, estimated from data
mrt_tension_{W} = (0 - bqx_{W}) * theta_{W}
-- Where theta is estimated from: d(bqx) = theta * (0 - bqx) * dt + noise

-- Half-life estimation (exponential decay)
mrt_half_life = -LN(2) / LN(autocorr_1_lag)
-- Where autocorr_1_lag = CORR(bqx, LAG(bqx, 1))

-- Expected intervals to zero (linear approximation)
mrt_expected_reversion = ABS(bqx_composite) / AVG(ABS(der_v1_composite)) OVER (ROWS BETWEEN 100 PRECEDING AND 1 PRECEDING)

-- Reversion probability (logistic based on tension)
mrt_reversion_probability = 1 / (1 + EXP(-0.5 * (mrt_tension_composite - 1)))
-- Calibrate threshold (1) based on historical data
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| High tension | mrt_tension_composite > 2 | Strong reversion force |
| Short half-life | mrt_half_life < 50 intervals | Fast mean-reversion expected |
| Near expected reversion | mrt_expected_reversion < 15 | Reversal imminent |
| High reversion prob | mrt_reversion_probability > 0.7 | 70%+ chance of reversion |

---

## FEATURE TYPE 7: TEMPORAL PATTERNS (tmp_) - TIME-CENTRIC EXCEPTION

### Purpose
Capture calendar and session effects in BQX behavior.

### Architecture Note
**This is the ONLY time-centric feature type.**

All other feature types use interval-based calculations. The tmp_ type extracts time metadata from each row but does NOT use time-based window functions.

### Game Theory Value
- BQX behavior varies by trading session (NY momentum > Asian)
- Certain hours produce more extremes
- Session transitions often trigger reversals
- Weekend positioning creates Monday patterns

### Table Structure

```
tmp_{pair}           # Per-pair (28 tables)
```

**Note**: No IDX/BQX variant - time features are universal.

### Columns

| Column | Type | Description | SQL Template |
|--------|------|-------------|--------------|
| interval_id | INT64 | Primary key | From source |
| tmp_hour_utc | INT64 | Hour of day (0-23 UTC) | EXTRACT(HOUR FROM timestamp) |
| tmp_day_of_week | INT64 | Day of week (0=Sun, 6=Sat) | EXTRACT(DAYOFWEEK FROM timestamp) |
| tmp_minute_of_hour | INT64 | Minute (0-59) | EXTRACT(MINUTE FROM timestamp) |
| tmp_is_london | BOOLEAN | London session (08:00-16:00 UTC) | Hour check |
| tmp_is_ny | BOOLEAN | New York session (13:00-21:00 UTC) | Hour check |
| tmp_is_asian | BOOLEAN | Asian session (00:00-08:00 UTC) | Hour check |
| tmp_is_overlap_london_ny | BOOLEAN | London/NY overlap (13:00-16:00) | Hour check |
| tmp_is_weekend | BOOLEAN | Saturday or Sunday | Day check |
| tmp_is_monday | BOOLEAN | Monday (gap risk) | Day check |
| tmp_is_friday | BOOLEAN | Friday (position squaring) | Day check |
| tmp_hours_to_close | INT64 | Hours until Friday 21:00 UTC | Calculation |
| tmp_session_phase | STRING | 'ASIAN', 'LONDON', 'NY', 'OVERLAP' | CASE statement |

### SQL Formulas (Time-Based Extraction)

```sql
-- Hour extraction (UTC)
tmp_hour_utc = EXTRACT(HOUR FROM timestamp)

-- Day of week (1=Sunday in BigQuery)
tmp_day_of_week = EXTRACT(DAYOFWEEK FROM timestamp) - 1  -- Convert to 0-indexed

-- Session classification
tmp_is_asian = tmp_hour_utc >= 0 AND tmp_hour_utc < 8
tmp_is_london = tmp_hour_utc >= 8 AND tmp_hour_utc < 16
tmp_is_ny = tmp_hour_utc >= 13 AND tmp_hour_utc < 21
tmp_is_overlap_london_ny = tmp_hour_utc >= 13 AND tmp_hour_utc < 16

-- Weekend detection
tmp_is_weekend = tmp_day_of_week IN (0, 6)  -- Sunday, Saturday

-- Session phase
tmp_session_phase = CASE
  WHEN tmp_hour_utc >= 13 AND tmp_hour_utc < 16 THEN 'OVERLAP'
  WHEN tmp_is_ny THEN 'NY'
  WHEN tmp_is_london THEN 'LONDON'
  WHEN tmp_is_asian THEN 'ASIAN'
  ELSE 'OFF_HOURS'
END

-- Hours to weekly close (Friday 21:00 UTC)
tmp_hours_to_close = (
  (5 - tmp_day_of_week) * 24 + (21 - tmp_hour_utc)
) MOD (7 * 24)
```

### Expected Predictive Value

| Signal | Condition | Game Theory Implication |
|--------|-----------|------------------------|
| London/NY overlap | tmp_is_overlap_london_ny = TRUE | Highest volume, fastest moves |
| Asian session | tmp_is_asian = TRUE | Lower volatility, range-bound |
| Monday open | tmp_is_monday AND hour < 8 | Gap risk, weekend news |
| Friday afternoon | tmp_is_friday AND hour > 18 | Position squaring |
| Near weekly close | tmp_hours_to_close < 5 | Low liquidity, wider spreads |

---

## IMPLEMENTATION PHASES

### Phase 1: HIGH IMPACT (Priority 1)
**Duration**: ~4 hours
**Tables**: 112

| Type | Tables | Why First |
|------|--------|-----------|
| rev_ | 56 | Directly predicts when to trade |
| der_ | 56 | Captures momentum exhaustion dynamics |

### Phase 2: EXTREMITY & CYCLE (Priority 2)
**Duration**: ~3 hours
**Tables**: 56

| Type | Tables | Why Second |
|------|--------|------------|
| ext_ | 28 | Quantifies opportunity zones |
| cyc_ | 28 | Timing optimization |

### Phase 3: DIVERGENCE & TENSION (Priority 3)
**Duration**: ~3 hours
**Tables**: 84

| Type | Tables | Why Third |
|------|--------|-----------|
| div_ | 56 | Early warning for reversals |
| mrt_ | 28 | Opportunity magnitude |

### Phase 4: TEMPORAL (Priority 4)
**Duration**: ~1 hour
**Tables**: 28

| Type | Tables | Why Last |
|------|--------|----------|
| tmp_ | 28 | Optimization layer, not core |

---

## VALIDATION REQUIREMENTS

### Per-Table Validation

| Check | Criterion | Action if Fail |
|-------|-----------|----------------|
| Row count | Matches source table | Investigate join |
| Null rate | < 5% per column | Check formula edge cases |
| Value range | Within expected bounds | Review calculation |
| Correlation sanity | Expected sign with target | Review logic |

### Cross-Type Validation

| Check | Criterion | Action if Fail |
|-------|-----------|----------------|
| IDX/BQX parity | Same row count | Align source tables |
| Feature correlation | No perfect collinearity | Remove redundant |
| Predictive power | Correlation > 0.05 with target | Evaluate utility |

---

## APPENDIX: COMPLETE TABLE LIST

### rev_ Tables (56)
```
rev_eurusd, rev_gbpusd, rev_usdjpy, rev_usdchf, rev_audusd, rev_usdcad, rev_nzdusd,
rev_eurgbp, rev_eurjpy, rev_eurchf, rev_euraud, rev_eurcad, rev_eurnzd,
rev_gbpjpy, rev_gbpchf, rev_gbpaud, rev_gbpcad, rev_gbpnzd,
rev_audjpy, rev_audchf, rev_audcad, rev_audnzd,
rev_nzdjpy, rev_nzdchf, rev_nzdcad,
rev_cadjpy, rev_cadchf, rev_chfjpy

rev_bqx_eurusd, rev_bqx_gbpusd, rev_bqx_usdjpy, rev_bqx_usdchf, rev_bqx_audusd, rev_bqx_usdcad, rev_bqx_nzdusd,
rev_bqx_eurgbp, rev_bqx_eurjpy, rev_bqx_eurchf, rev_bqx_euraud, rev_bqx_eurcad, rev_bqx_eurnzd,
rev_bqx_gbpjpy, rev_bqx_gbpchf, rev_bqx_gbpaud, rev_bqx_gbpcad, rev_bqx_gbpnzd,
rev_bqx_audjpy, rev_bqx_audchf, rev_bqx_audcad, rev_bqx_audnzd,
rev_bqx_nzdjpy, rev_bqx_nzdchf, rev_bqx_nzdcad,
rev_bqx_cadjpy, rev_bqx_cadchf, rev_bqx_chfjpy
```

### der_ Tables (56)
```
der_eurusd, der_gbpusd, der_usdjpy, der_usdchf, der_audusd, der_usdcad, der_nzdusd,
der_eurgbp, der_eurjpy, der_eurchf, der_euraud, der_eurcad, der_eurnzd,
der_gbpjpy, der_gbpchf, der_gbpaud, der_gbpcad, der_gbpnzd,
der_audjpy, der_audchf, der_audcad, der_audnzd,
der_nzdjpy, der_nzdchf, der_nzdcad,
der_cadjpy, der_cadchf, der_chfjpy

der_bqx_eurusd, der_bqx_gbpusd, der_bqx_usdjpy, der_bqx_usdchf, der_bqx_audusd, der_bqx_usdcad, der_bqx_nzdusd,
der_bqx_eurgbp, der_bqx_eurjpy, der_bqx_eurchf, der_bqx_euraud, der_bqx_eurcad, der_bqx_eurnzd,
der_bqx_gbpjpy, der_bqx_gbpchf, der_bqx_gbpaud, der_bqx_gbpcad, der_bqx_gbpnzd,
der_bqx_audjpy, der_bqx_audchf, der_bqx_audcad, der_bqx_audnzd,
der_bqx_nzdjpy, der_bqx_nzdchf, der_bqx_nzdcad,
der_bqx_cadjpy, der_bqx_cadchf, der_bqx_chfjpy
```

### ext_ Tables (28 - BQX only)
```
ext_bqx_eurusd, ext_bqx_gbpusd, ext_bqx_usdjpy, ext_bqx_usdchf, ext_bqx_audusd, ext_bqx_usdcad, ext_bqx_nzdusd,
ext_bqx_eurgbp, ext_bqx_eurjpy, ext_bqx_eurchf, ext_bqx_euraud, ext_bqx_eurcad, ext_bqx_eurnzd,
ext_bqx_gbpjpy, ext_bqx_gbpchf, ext_bqx_gbpaud, ext_bqx_gbpcad, ext_bqx_gbpnzd,
ext_bqx_audjpy, ext_bqx_audchf, ext_bqx_audcad, ext_bqx_audnzd,
ext_bqx_nzdjpy, ext_bqx_nzdchf, ext_bqx_nzdcad,
ext_bqx_cadjpy, ext_bqx_cadchf, ext_bqx_chfjpy
```

### cyc_ Tables (28 - BQX only)
```
cyc_bqx_eurusd, cyc_bqx_gbpusd, cyc_bqx_usdjpy, cyc_bqx_usdchf, cyc_bqx_audusd, cyc_bqx_usdcad, cyc_bqx_nzdusd,
cyc_bqx_eurgbp, cyc_bqx_eurjpy, cyc_bqx_eurchf, cyc_bqx_euraud, cyc_bqx_eurcad, cyc_bqx_eurnzd,
cyc_bqx_gbpjpy, cyc_bqx_gbpchf, cyc_bqx_gbpaud, cyc_bqx_gbpcad, cyc_bqx_gbpnzd,
cyc_bqx_audjpy, cyc_bqx_audchf, cyc_bqx_audcad, cyc_bqx_audnzd,
cyc_bqx_nzdjpy, cyc_bqx_nzdchf, cyc_bqx_nzdcad,
cyc_bqx_cadjpy, cyc_bqx_cadchf, cyc_bqx_chfjpy
```

### div_ Tables (56)
```
div_eurusd, div_gbpusd, div_usdjpy, div_usdchf, div_audusd, div_usdcad, div_nzdusd,
div_eurgbp, div_eurjpy, div_eurchf, div_euraud, div_eurcad, div_eurnzd,
div_gbpjpy, div_gbpchf, div_gbpaud, div_gbpcad, div_gbpnzd,
div_audjpy, div_audchf, div_audcad, div_audnzd,
div_nzdjpy, div_nzdchf, div_nzdcad,
div_cadjpy, div_cadchf, div_chfjpy

div_bqx_eurusd, div_bqx_gbpusd, div_bqx_usdjpy, div_bqx_usdchf, div_bqx_audusd, div_bqx_usdcad, div_bqx_nzdusd,
div_bqx_eurgbp, div_bqx_eurjpy, div_bqx_eurchf, div_bqx_euraud, div_bqx_eurcad, div_bqx_eurnzd,
div_bqx_gbpjpy, div_bqx_gbpchf, div_bqx_gbpaud, div_bqx_gbpcad, div_bqx_gbpnzd,
div_bqx_audjpy, div_bqx_audchf, div_bqx_audcad, div_bqx_audnzd,
div_bqx_nzdjpy, div_bqx_nzdchf, div_bqx_nzdcad,
div_bqx_cadjpy, div_bqx_cadchf, div_bqx_chfjpy
```

### mrt_ Tables (28 - BQX only)
```
mrt_bqx_eurusd, mrt_bqx_gbpusd, mrt_bqx_usdjpy, mrt_bqx_usdchf, mrt_bqx_audusd, mrt_bqx_usdcad, mrt_bqx_nzdusd,
mrt_bqx_eurgbp, mrt_bqx_eurjpy, mrt_bqx_eurchf, mrt_bqx_euraud, mrt_bqx_eurcad, mrt_bqx_eurnzd,
mrt_bqx_gbpjpy, mrt_bqx_gbpchf, mrt_bqx_gbpaud, mrt_bqx_gbpcad, mrt_bqx_gbpnzd,
mrt_bqx_audjpy, mrt_bqx_audchf, mrt_bqx_audcad, mrt_bqx_audnzd,
mrt_bqx_nzdjpy, mrt_bqx_nzdchf, mrt_bqx_nzdcad,
mrt_bqx_cadjpy, mrt_bqx_cadchf, mrt_bqx_chfjpy
```

### tmp_ Tables (28 - No variant)
```
tmp_eurusd, tmp_gbpusd, tmp_usdjpy, tmp_usdchf, tmp_audusd, tmp_usdcad, tmp_nzdusd,
tmp_eurgbp, tmp_eurjpy, tmp_eurchf, tmp_euraud, tmp_eurcad, tmp_eurnzd,
tmp_gbpjpy, tmp_gbpchf, tmp_gbpaud, tmp_gbpcad, tmp_gbpnzd,
tmp_audjpy, tmp_audchf, tmp_audcad, tmp_audnzd,
tmp_nzdjpy, tmp_nzdchf, tmp_nzdcad,
tmp_cadjpy, tmp_cadchf, tmp_chfjpy
```

---

*Document generated: 2025-11-29*
*Dataset: bqx-ml:bqx_ml_v3_features*
