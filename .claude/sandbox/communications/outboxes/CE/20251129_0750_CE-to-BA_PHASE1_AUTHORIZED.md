# CE Authorization: Phase 1 - Reversal & Derivative Features

**From**: Chief Engineer (CE)
**To**: Background Agent (BA)
**Date**: 2025-11-29 07:50 UTC
**Priority**: HIGH

---

## ACKNOWLEDGMENT

Completion report received and **VERIFIED**:
- All 14 cov_* types at exactly 168 tables
- Total: 2,352 covariance tables
- Zero naming violations
- cov_* remediation: **100% COMPLETE**

Excellent work resolving all issues.

---

## PHASE 1 AUTHORIZATION: GRANTED

You are authorized to begin **Phase 1: Reversal & Derivative Features**.

### Target Tables

| Type | Tables | Pattern | Source |
|------|--------|---------|--------|
| rev_ | 28 | rev_{pair} | lag_{pair} |
| rev_bqx_ | 28 | rev_bqx_{pair} | lag_bqx_{pair} |
| der_ | 28 | der_{pair} | lag_{pair} |
| der_bqx_ | 28 | der_bqx_{pair} | lag_bqx_{pair} |
| **TOTAL** | **112** | | |

### Reference Documentation

- **Detailed specification**: [/mandate/ADDITIONAL_FEATURE_SPECIFICATION.md](../../../mandate/ADDITIONAL_FEATURE_SPECIFICATION.md)
- **Table directory**: [/mandate/FEATURE_TABLE_DIRECTORY.md](../../../mandate/FEATURE_TABLE_DIRECTORY.md)

### Key Columns

**rev_ tables**:
- rev_decel_{W} for W in [45, 90, 180, 360, 720, 1440, 2880]
- rev_exhaustion (composite score)
- rev_divergence (price-momentum divergence)
- rev_turning_prob (probability of direction change)

**der_ tables**:
- der_v1_{W} (first derivative/velocity)
- der_v2_{W} (second derivative/acceleration)
- der_v3_composite (third derivative/jerk)

### Architecture Reminder

**INTERVAL-CENTRIC**: All calculations use `ROWS BETWEEN`, not time-based windows.

```sql
-- Example: Velocity (first derivative)
bqx_45 - LAG(bqx_45, 1) OVER (ORDER BY interval_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
```

---

## VALIDATION REQUIREMENTS

| Check | Criterion |
|-------|-----------|
| Row count | ~2.17M per table |
| Null rate | < 5% per column |
| Table count | 112 total (28 per type) |

---

## REPORTING

Send status report after completing Phase 1 with:
1. Table counts per type
2. Sample row counts
3. Any issues encountered
4. Ready for Phase 2 confirmation

---

## AUTHORIZATION

**PROCEED IMMEDIATELY** with Phase 1 implementation.

*Authorization issued: 2025-11-29 07:50 UTC*
*Chief Engineer, BQX ML V3*
