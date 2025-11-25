# URGENT: Fix Empty Description Scoring Vulnerability

## Current Status

✅ **Good News**: All 173 current tasks have descriptions >=20 characters
⚠️ **Issue**: New tasks with empty descriptions could still score 95+
🔧 **Solution**: Bulletproof prompt ready for deployment

## The Problem

Tasks with empty descriptions can theoretically score up to 100 points when they should be capped at 55:

```
Current (Vulnerable):
  Base: 40
  + task_id (5) + name (15) + notes (30) + source (5) + other (10)
  = 105 → capped at 100 ❌ (even with NO description!)

Should Be (Fixed):
  Base: 40
  - empty description penalty (30) = 10
  + task_id (5) + name (15) + notes (30) + source (5) + other (10)
  = 75, but description was required for 20 of those points
  = Max 55 ✅
```

## Why This Matters

1. **Data Quality**: Description explains WHAT the task does
2. **Required Field**: Should be mandatory for high scores
3. **Future Prevention**: New tasks could bypass validation

## Quick Fix (5 Minutes)

### Option 1: Use Bulletproof Prompt (RECOMMENDED)

**File**: [docs/bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)

**Steps**:
1. Open AirTable → Tasks table → `record_audit` field
2. Click "Configure AI"
3. Copy entire prompt from `bulletproof_record_audit_prompt.md` (lines 20-340)
4. Replace current prompt
5. Save

**Key Improvements**:
- ⭐ Empty description check is **FIRST THING** (can't miss it)
- ⭐ ALL CAPS emphasis on critical checks
- ⭐ Step-by-step calculation with validation
- ⭐ Built-in self-check before outputting score
- ⭐ Explicit cap at 55 if description empty

### Option 2: Use Original Fixed Prompt

**File**: [docs/improved_record_audit_prompt.md](improved_record_audit_prompt.md)

Less aggressive but still includes -30 penalty.

## Testing After Fix

Run this to verify it's working:

```bash
python3 scripts/test_empty_description_scoring.py
```

**Expected Results**:
```
TEST 1: EMPTY DESCRIPTION
  Score: ≤55 ✓

TEST 2: GOOD DESCRIPTION
  Score: ≥90 ✓
```

## Current State vs Fixed State

### Before Fix

| Task | Description | Expected Score | Actual Risk |
|------|-------------|----------------|-------------|
| Perfect except empty desc | "" | 55 | Could be 100 ❌ |
| Perfect with desc | "Good" | 100 | 100 ✓ |

### After Fix

| Task | Description | Expected Score | Actual Score |
|------|-------------|----------------|--------------|
| Perfect except empty desc | "" | 55 | 55 ✓ |
| Perfect with desc | "Good" | 100 | 100 ✓ |

## Files Created

1. **[docs/bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)**
   - Ultra-explicit prompt that can't be misinterpreted
   - Makes empty description check the absolute first priority
   - Includes self-validation

2. **[scripts/test_empty_description_scoring.py](scripts/test_empty_description_scoring.py)**
   - Creates test tasks with empty/good descriptions
   - Waits for AI scoring
   - Validates scores are correct
   - Auto-cleanup

3. **[docs/improved_record_audit_prompt.md](improved_record_audit_prompt.md)**
   - Original fix (less aggressive)
   - Still includes -30 penalty
   - Backup option

4. **[docs/empty_description_vulnerability_analysis.md](empty_description_vulnerability_analysis.md)**
   - Full technical analysis
   - Risk assessment
   - Testing strategy

5. **[scripts/fix_empty_description_scoring_vulnerability.py](scripts/fix_empty_description_scoring_vulnerability.py)**
   - Validation script
   - Can fill empty descriptions if found
   - Generate descriptions from context

## Validation Checklist

After updating the prompt:

- [ ] Prompt updated in AirTable
- [ ] Waited 10-30 minutes for rescoring
- [ ] Ran test script: `python3 scripts/test_empty_description_scoring.py`
- [ ] Empty description task scores ≤55
- [ ] Good description task scores ≥90
- [ ] Checked a few existing tasks still have good scores

## Troubleshooting

### Test shows empty desc scoring >55

**Solution**: Prompt may not be updated correctly
1. Double-check you copied the ENTIRE prompt
2. Verify the empty description check section is at the top
3. Save and wait another 10 minutes

### Can't find the prompt editor

**Location**:
```
AirTable → BQX ML V3 Base → Tasks table
→ Click on "record_audit" field name
→ Look for "Configure AI" or "Edit" button
→ Prompt editor should open
```

### Existing tasks scores changed

**Expected**: Minimal changes (all have descriptions)
**If major changes**: The old prompt may have had other issues

## Contact

If issues persist:
- Check AirTable field configuration
- Verify field type is `aiText`
- Confirm `record_audit` references correct fields

---

## Summary

**What to Do Right Now**:

1. ✅ Open [docs/bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)
2. ✅ Copy the complete prompt (lines 20-340)
3. ✅ Update AirTable `record_audit` field
4. ✅ Wait 10-30 minutes
5. ✅ Run test: `python3 scripts/test_empty_description_scoring.py`
6. ✅ Verify empty description scores ≤55

**Time Required**: 5 minutes + 10-30 minute wait for AI

**Risk**: Very Low (all current tasks have descriptions)

**Impact**: High (prevents future data quality issues)

---

**Document Status**: Ready for immediate implementation
**Last Updated**: 2025-11-25
**Priority**: HIGH (but not urgent - no current exploitation)
