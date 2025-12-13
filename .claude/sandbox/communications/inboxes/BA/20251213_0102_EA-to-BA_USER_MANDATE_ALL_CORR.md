# EA DIRECTIVE: User Mandates ALL CORR Data - Both Variants Required

**Date**: December 13, 2025 01:02 UTC
**From**: Enhancement Assistant (EA)
**To**: Build Agent (BA)
**Re**: USER MANDATE - CORR-BQX only is NOT acceptable, must include IDX variant
**Priority**: P0-CRITICAL (USER DIRECTIVE)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## USER DIRECTIVE RECEIVED

**User mandate**: "all corr data must be present. corr-bqx only is not acceptable."

**Interpretation**: OPTION 3 is required - TRI + COV + CORR (Both IDX + BQX variants)

**Previous EA Recommendation**: Option 2 (CORR-BQX only) → **OVERRULED by user**

---

## REVISED TIER 1 SCOPE (USER MANDATE)

### Tier 1: TRI + COV + CORR (Both Variants)

**Tables**: 3,149 total
- TRI: 194 tables
- COV: 2,507 tables
- CORR-IDX: 224 tables (28 pairs × 8 ETFs)
- CORR-BQX: 224 tables (28 pairs × 8 ETFs)

**Timeline**: 20 hours (Dec 13, 21:00 UTC completion)

**Cost**: $160-211

**NULL Reduction**: 12.43% → ~0.9%

**Feature Coverage**: 240 CORR columns (100% of ETF correlation features)

---

## BA EXECUTION PLAN

### Step 1: Validate CORR (Both Variants) - 10 minutes

```bash
# Test 3 IDX tables
python3 scripts/generate_corr_tables_fixed.py --validate-only --test-only --workers 1

# Or validate BQX + IDX separately
python3 scripts/generate_corr_tables_fixed.py --validate-only --test-only --bqx-only --workers 1
```

**Expected**: Both variants should show +X% row increases (like TRI + COV did)

### Step 2: Launch Tier 1 (All 3 Scripts in Parallel)

```bash
python3 scripts/generate_tri_tables.py --workers 16 &
python3 scripts/generate_cov_tables.py --workers 16 &
python3 scripts/generate_corr_tables_fixed.py --workers 16 &
```

**Note**: Do NOT use `--bqx-only` flag → generates both IDX + BQX variants

---

## CORR-IDX CONSIDERATION

**Previous EA finding**: ETF IDX source tables have timestamp corruption (1970-01-01 instead of 2020-2025)

**Impact on CORR regeneration**: **NONE**

**Why**: The fixed script does NOT query ETF source tables. It:
1. Uses pair's `base_idx_{pair}` for intervals (these exist and are correct)
2. Preserves existing correlation values from current `corr_etf_idx_*` tables
3. Only adds missing interval rows (values will be NULL for new rows)

**Result**: CORR-IDX tables can be regenerated successfully even with corrupted ETF source data

---

## REVISED TIMELINE (USER MANDATE)

**01:02 UTC**: User directive received - ALL CORR required
**01:02-01:15 UTC**: BA validates CORR (both variants)
**01:15 UTC**: BA launches Tier 1 (TRI + COV + CORR-BOTH)
**21:00 UTC** (Dec 13): Tier 1 complete

**Total execution time**: ~20 hours

---

## SUMMARY

**Previous EA Recommendation**: Option 2 (CORR-BQX only, 2,925 tables, 18h, $130-170)

**User Mandate**: Option 3 (CORR-BOTH, 3,149 tables, 20h, $160-211)

**BA Action**:
- ✅ Validate CORR (both variants)
- ✅ Launch all 3 scripts WITHOUT `--bqx-only` flag
- ✅ Expected completion: Dec 13, 21:00 UTC

**Confidence**: HIGH - Fixed script tested, same pattern as TRI + COV (which passed)

---

**Enhancement Assistant (EA)**
*User Mandate Acknowledged - All CORR Required*

**Status**: ✅ User directive communicated to BA

**Next**: BA validates CORR-BOTH → launches Tier 1 with all 448 CORR tables

---

**END OF USER MANDATE NOTIFICATION**
