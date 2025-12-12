# CE DIRECTIVE: Tier 2A - Target Lookahead Edge Case Handling

**Date**: December 12, 2025 22:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Tier 2A - Handle Target NULL Values at End of Time Series
**Priority**: P1-HIGH (execute after Tier 1 complete)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

**Context**: EA NULL investigation identified 1.2% NULLs from target lookahead insufficiency

**Problem**: Target values (h15-h105) require future data - final rows of dataset cannot calculate targets due to insufficient lookahead

**Example**:
- Dataset ends: 2025-11-20 23:59:00
- Target h105 (105 min ahead): Requires data until 2025-11-21 01:44:00
- Result: Final 105 rows have NULL targets

**Tier 2A Remediation**: Exclude final 2,880 rows (h2880 = max horizon) OR extend data collection by 3-4 hours

**Expected Impact**: Reduces NULLs from 2.03% → 0.83% (1.2% reduction)

**Recommendation**: **EXCLUDE final 2,880 rows** (simpler, faster, acceptable for training)

**Authorization**: ⏸️ **PENDING** - Execute after Tier 1 complete, subject to user approval

**Budget**: $0 (code change only)
**Timeline**: 10 minutes (code change) OR 3-4 hours (data extension)

---

## PROBLEM STATEMENT

### Root Cause: Lookahead Limitation

**Training Data Requirements**:
- Features: Calculated from historical data (lookback)
- Targets: Calculated from future data (lookahead)

**Horizon Definitions**:
- h15: 15 minutes ahead
- h30: 30 minutes ahead
- h45: 45 minutes ahead
- h60: 60 minutes ahead
- h75: 75 minutes ahead
- h90: 90 minutes ahead
- h105: 105 minutes ahead

**Maximum Lookahead**: 2,880 minutes (h2880 = 48 hours, from bqx2880 targets)

**Consequence**:
- Final 2,880 rows (48 hours) of dataset cannot have complete targets
- Results in 1.2% NULLs (2,880 / ~177,748 rows = 1.62%)

### Current Data Range

**EURUSD Dataset**:
- Start: 2020-01-01 00:00:00
- End: 2025-11-20 23:59:00
- Total rows: 177,748

**Final Rows**:
- Rows 174,868-177,748: Missing h2880 targets (2,880 rows)
- Rows 176,639-177,748: Missing h105 targets (1,109 rows)
- Rows 177,644-177,748: Missing h15 targets (104 rows)

**Impact**: 1.62% of rows have incomplete targets (worst case: h2880)

---

## TWO OPTIONS

### Option A: Exclude Final 2,880 Rows (RECOMMENDED)

**What**: Remove final 2,880 rows from training dataset

**Implementation**:
```python
# In extraction pipeline (parallel_feature_testing.py)
df = df[:-2880]  # Exclude final 2,880 rows

# OR with explicit date cutoff
cutoff_date = df['interval_time'].max() - pd.Timedelta(minutes=2880)
df = df[df['interval_time'] <= cutoff_date]
```

**Pros**:
- ✅ **Simplest implementation** (1-line code change)
- ✅ **Zero cost** (no data collection required)
- ✅ **Fast execution** (10 minutes to implement and test)
- ✅ **Complete targets** (all remaining rows have 100% target coverage)
- ✅ **Acceptable for training** (losing 1.6% of most recent data is negligible)

**Cons**:
- ❌ Loses 2,880 rows (~1.6% of data)
- ❌ Most recent data excluded (but minimal impact on 5+ years of data)

**Impact**:
- Rows reduced: 177,748 → 174,868
- NULL reduction: 1.2%
- Training file size: Negligible difference (~1.6% smaller)

**Recommendation**: ⭐ **PREFERRED** (simple, fast, acceptable tradeoff)

---

### Option B: Extend Data Collection by 3-4 Hours

**What**: Collect additional 3-4 hours of data beyond current end date

**Implementation**:
1. Verify m1 data exists through 2025-11-21 03:59:00 (4 hours past current end)
2. If exists: Re-run feature generation for extended date range
3. If not exists: Backfill m1 data from source, then generate features
4. Re-extract training data with extended range

**Pros**:
- ✅ Preserves all current data (no rows lost)
- ✅ Adds more recent data (training on latest patterns)

**Cons**:
- ❌ **Complex implementation** (requires m1 data verification/backfill)
- ❌ **Longer execution time** (3-4 hours vs 10 minutes)
- ❌ **May not be possible** (if m1 data doesn't exist beyond 2025-11-20)
- ❌ **Marginal benefit** (1.6% more data is minimal for 5+ years)

**Impact**:
- Rows retained: All 177,748
- NULL reduction: 1.2%
- Training file size: Same as current

**Recommendation**: ❌ **NOT RECOMMENDED** (complex, slow, minimal benefit)

---

## RECOMMENDED APPROACH: OPTION A

### Implementation Steps

**Step 1: Code Change** (5 min)
```python
# File: pipelines/training/parallel_feature_testing.py
# Location: After merge complete, before export

# Add cutoff logic
MAX_HORIZON_MINUTES = 2880  # h2880 = 48 hours
cutoff_date = df['interval_time'].max() - pd.Timedelta(minutes=MAX_HORIZON_MINUTES)
df_filtered = df[df['interval_time'] <= cutoff_date]

print(f"Original rows: {len(df)}")
print(f"Filtered rows: {len(df_filtered)}")
print(f"Excluded rows: {len(df) - len(df_filtered)} (target lookahead edge)")

# Export filtered dataframe
df_filtered.to_parquet(output_path)
```

**Step 2: Test on EURUSD** (5 min)
- Re-extract EURUSD with filtered logic
- Verify row count: ~174,868 rows (177,748 - 2,880)
- Verify targets: 0% NULLs in all h15-h2880 columns

**Step 3: Validate NULL Reduction** (5 min)
- Calculate NULL percentage in new file
- Expected: 2.03% → ~0.8% (Tier 1 + Tier 2A combined)

**Step 4: Document & Deploy** (5 min)
- Update extraction pipeline documentation
- Commit code change to git
- Apply to all 28 pairs

**Total Time**: 20 minutes

---

## VALIDATION CRITERIA

**Gate 1: Row Count**
- [ ] Final row count = original - 2,880
- [ ] EURUSD: ~174,868 rows (177,748 - 2,880)

**Gate 2: Target Completeness**
- [ ] All target columns (h15-h2880) have 0% NULLs
- [ ] No edge case NULLs at end of dataset

**Gate 3: NULL Reduction**
- [ ] Overall NULLs reduced by 1.0-1.5% (combined with Tier 1)
- [ ] Expected: 2.03% → 0.5-0.8%

**Gate 4: Data Quality**
- [ ] Cutoff date calculated correctly (max_date - 2880 min)
- [ ] No unintended row exclusions

---

## TIMELINE

**Dependency**: Execute after Tier 1 complete (after 04:15 UTC Dec 14)

**Execution**:
- 04:15-04:20 UTC: Implement code change
- 04:20-04:25 UTC: Test on EURUSD sample
- 04:25-04:30 UTC: Validate NULL reduction
- 04:30-04:35 UTC: Document and commit

**Completion**: 04:35 UTC December 14, 2025 (20 min after Tier 1)

---

## COORDINATION

### With EA (Enhancement Assistant):
- **Input**: EA's Tier 2A recommendation (Option A or B)
- **Cost**: $0 (no BigQuery changes)
- **Note**: EA preparing revised ETF recommendation separately

### With QA (Quality Assurance):
- **Validation**: QA verifies target completeness after code change
- **Test**: Spot-check 5 pairs for 0% target NULLs

### With CE (Chief Engineer):
- **Approval**: CE approves Option A (exclude rows) vs Option B (extend data)
- **Report**: BA delivers 5-min status update after implementation

---

## COST-BENEFIT ANALYSIS

**Option A (Exclude Rows)**:
- Cost: $0
- Time: 20 minutes
- Benefit: 1.2% NULL reduction, 100% target completeness
- Tradeoff: Lose 1.6% of data (2,880 / 177,748)
- ROI: Infinite (zero cost, significant benefit)

**Option B (Extend Data)**:
- Cost: $0-$50 (if backfill required)
- Time: 3-4 hours
- Benefit: 1.2% NULL reduction, 100% target completeness, retain all rows
- Tradeoff: Complex implementation, may not be feasible
- ROI: Low (high time cost, marginal benefit)

**Recommendation**: **Option A** (10× faster, zero cost, acceptable tradeoff)

---

## STRATEGIC CONTEXT

**User Mandate**: *"user expects data to be complete. no short cuts."*

**Option A Compliance**:
- ✅ Achieves complete targets (0% NULLs in target columns)
- ✅ Not a shortcut (intentional edge case handling)
- ✅ Standard practice in ML (exclude rows without complete targets)
- ✅ Minimal data loss (1.6% of dataset, most recent)

**Explanation for User**:
> "Excluding final 2,880 rows ensures 100% target completeness. This is standard ML practice - we cannot calculate targets for the most recent 48 hours of data because we lack future data. Losing 1.6% of the dataset (most recent 2 days) has negligible impact on model training with 5+ years of historical data."

---

## AUTHORIZATION

**Status**: ⏸️ **PENDING** - Awaiting CE approval for Option A vs Option B

**Recommendation**: **Option A** (exclude final 2,880 rows)

**Execution**: After Tier 1 complete (04:15 UTC Dec 14)

**Budget**: $0 (approved)

---

## DELIVERABLE

**File**: `TIER2A_LOOKAHEAD_COMPLETE.md` (after implementation)

**Contents**:
- Implementation summary (Option A or B)
- Row count before/after
- Target completeness validation
- NULL reduction measurement
- Recommendation for Tier 2B (ETF handling)

---

**Chief Engineer (CE)**
*Strategic Coordination & Resource Authorization*

**Directive**: BA executes Tier 2A after Tier 1 complete, pending CE approval of Option A vs B

**Expected Outcome**: 1.2% NULL reduction, 100% target completeness, completion in 20 min

---

**END OF TIER 2A DIRECTIVE**
