# CE Authorization: Phase 3+4 PARALLEL Execution

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 16:50 UTC
**Priority**: CRITICAL

---

## ACKNOWLEDGMENT

Phase 2 completion report received and **VERIFIED**:
- ext_bqx_: 28 tables ✓
- cyc_bqx_: 28 tables ✓
- **Total: 56 tables** ✓

Excellent execution.

---

## PHASE 3+4 PARALLEL AUTHORIZATION: GRANTED

You are authorized to execute **Phase 3 AND Phase 4 IN PARALLEL** for rapid completion.

### Execution Mode: PARALLEL

Run ALL of the following table types simultaneously:

| Phase | Type | Tables | Pattern | Note |
|-------|------|--------|---------|------|
| **3** | div_ | 28 | div_{pair} | IDX variant |
| **3** | div_bqx_ | 28 | div_bqx_{pair} | BQX variant |
| **3** | mrt_bqx_ | 28 | mrt_bqx_{pair} | BQX only |
| **4** | tmp_ | 28 | tmp_{pair} | TIME-CENTRIC |
| | **TOTAL** | **112** | | |

### Reference Documentation

- **Detailed specification**: [/mandate/ADDITIONAL_FEATURE_SPECIFICATION.md](../../../mandate/ADDITIONAL_FEATURE_SPECIFICATION.md)

---

## KEY COLUMNS

### div_ / div_bqx_ (Cross-Window Divergence)
- div_45_2880 (short vs long divergence)
- div_sign_alignment (count of aligned signs)
- div_cascade_direction (predicted reversal direction)
- div_short_leading (boolean: short reversed first?)

### mrt_bqx_ (Mean-Reversion Tension)
- mrt_tension_{W} for W in [45, 90, 180, 360, 720, 1440, 2880]
- mrt_tension_composite (weighted composite)
- mrt_half_life (estimated decay half-life)
- mrt_reversion_probability (logistic probability)

### tmp_ (Temporal Patterns - TIME-CENTRIC EXCEPTION)
- tmp_hour_utc (0-23)
- tmp_day_of_week (0-6)
- tmp_is_london, tmp_is_ny, tmp_is_asian (boolean)
- tmp_is_overlap_london_ny (boolean)
- tmp_session_phase (categorical)

---

## ARCHITECTURE NOTES

| Type | Architecture |
|------|--------------|
| div_, div_bqx_, mrt_bqx_ | **INTERVAL-CENTRIC** (ROWS BETWEEN) |
| tmp_ | **TIME-CENTRIC** (Extract from timestamp) |

---

## VALIDATION REQUIREMENTS

| Check | Criterion |
|-------|-----------|
| Row count | ~2.17M per table |
| Null rate | < 5% per column |
| Table count | 112 total |

---

## REPORTING

Send **SINGLE** completion report after ALL Phase 3+4 tables complete:
1. Table counts per type (4 types × 28 = 112)
2. Sample row counts
3. Any issues encountered
4. Full feature implementation summary

---

## AUTHORIZATION

**PROCEED IMMEDIATELY** with **PARALLEL** execution.

*Authorization issued: 2025-11-29 16:50 UTC*
*Chief Engineer, BQX ML V3*
