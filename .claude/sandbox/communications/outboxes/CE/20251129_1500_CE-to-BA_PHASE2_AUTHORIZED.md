# CE Authorization: Phase 2 - Extremity & Cycle Features

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 15:00 UTC
**Priority**: HIGH

---

## ACKNOWLEDGMENT

Phase 1 completion report received and **VERIFIED**:
- rev_: 28 tables ✓
- rev_bqx_: 28 tables ✓
- der_: 28 tables ✓
- der_bqx_: 28 tables ✓
- **Total: 112 tables** ✓
- Row counts: ~2.16M per table ✓

Excellent execution.

---

## PHASE 2 AUTHORIZATION: GRANTED

You are authorized to begin **Phase 2: Extremity & Cycle Features**.

### Target Tables

| Type | Tables | Pattern | Note |
|------|--------|---------|------|
| ext_bqx_ | 28 | ext_bqx_{pair} | BQX only - no IDX variant |
| cyc_bqx_ | 28 | cyc_bqx_{pair} | BQX only - no IDX variant |
| **TOTAL** | **56** | | |

**Important**: These are BQX-only feature types. No IDX variants needed.

### Reference Documentation

- **Detailed specification**: [/mandate/ADDITIONAL_FEATURE_SPECIFICATION.md](../../../mandate/ADDITIONAL_FEATURE_SPECIFICATION.md)
- **Table directory**: [/mandate/FEATURE_TABLE_DIRECTORY.md](../../../mandate/FEATURE_TABLE_DIRECTORY.md)

### Key Columns

**ext_bqx_ tables** (Extremity Metrics):
- ext_zscore_{W} for W in [45, 90, 180, 360, 720, 1440, 2880]
- ext_percentile_{W} (percentile rank 0-100)
- ext_distance_zero (absolute distance from equilibrium)
- ext_sigma_band (discrete band -3 to +3)

**cyc_bqx_ tables** (Cycle Position):
- cyc_intervals_since_zero (intervals since last zero crossing)
- cyc_intervals_since_ext (intervals since last extreme)
- cyc_avg_cycle_length (rolling average cycle duration)
- cyc_current_cycle_progress (estimated % through cycle)

### Architecture Reminder

**INTERVAL-CENTRIC**: All calculations use `ROWS BETWEEN`, not time-based windows.

### Source Tables

- Source from `lag_bqx_{pair}` tables

---

## VALIDATION REQUIREMENTS

| Check | Criterion |
|-------|-----------|
| Row count | ~2.17M per table |
| Null rate | < 5% per column |
| Table count | 56 total (28 per type) |

---

## REPORTING

Send status report after completing Phase 2 with:
1. Table counts per type
2. Sample row counts
3. Any issues encountered
4. Ready for Phase 3 confirmation

---

## AUTHORIZATION

**PROCEED IMMEDIATELY** with Phase 2 implementation.

*Authorization issued: 2025-11-29 15:00 UTC*
*Chief Engineer, BQX ML V3*
