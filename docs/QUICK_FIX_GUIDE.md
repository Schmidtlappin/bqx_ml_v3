# Quick Fix Guide: Empty Description Vulnerability

## 🎯 What to Do

Update the AirTable `record_audit` field prompt to prevent tasks with empty descriptions from scoring 100.

---

## ⚡ Quick Steps

### 1. Navigate to AirTable
```
AirTable → BQX ML V3 Base → Tasks table → record_audit field
```

### 2. Open Prompt Editor
- Click on `record_audit` field settings
- Select "Configure AI" or "Edit Prompt"

### 3. Copy New Prompt
**Location**: [docs/improved_record_audit_prompt.md](improved_record_audit_prompt.md)

Look for the section starting with:
```
You are a strict quality assessment agent for the BQX ML project Tasks table...
```

### 4. Find This Section in Current Prompt
```
### description (20 points MAX)
{description}
- Contains numbers + methods + thresholds: +20
- Has methods but vague metrics: +10
- Technical but no specifics: +5
- Generic/template: +0
```

### 5. Replace With This
```
### description (20 points MAX)
{description}

**FIRST: Check if description is empty/missing**
- If empty or <20 characters: Apply -30 penalty, award 0 points
- If present but thin (<100 chars): Award max 5 points

**THEN: Evaluate quality for non-empty descriptions:**
- Contains numbers + methods + thresholds: +20
- Has methods but vague metrics: +10
- Technical but no specifics: +5
- Generic/template: +0
```

### 6. Add Empty Field Penalties Section
Insert this BEFORE "## CRITICAL: Thin Content Detection":
```
## CRITICAL FIELD REQUIREMENTS

### EMPTY FIELD PENALTIES (Applied BEFORE any scoring)
These penalties are applied IMMEDIATELY and reduce the base score:
- **Empty/missing description field: -30 points**
- Empty/missing notes field: -40 points
- Missing task_id: -50 points (critical failure)
- Missing name: -40 points (critical failure)

### EMPTY DESCRIPTION DETECTION (NEW)
A description is considered empty if:
- Field is null, undefined, or empty string
- Field contains only whitespace
- Field is less than 20 characters
- Field contains only placeholder text ("TODO", "TBD", "N/A", "PLACEHOLDER", etc.)

When detected, IMMEDIATELY apply -30 penalty and include in Issues list:
"Empty description field (-30 points). Critical data quality failure."
```

### 7. Update Score Calculation Section
Find:
```
## FINAL SCORE CALCULATION
1. Start with base: 40
2. Add field points (max +85 possible)
3. Apply ALL applicable penalties
4. Minimum: 0, Maximum: 100
```

Replace with:
```
## FINAL SCORE CALCULATION
1. Start with base: 40
2. **APPLY ALL EMPTY FIELD PENALTIES FIRST** (description, notes, etc.)
3. Add field quality points (max +85 possible)
4. Apply content penalties (thin, generic, etc.)
5. Minimum: 0, Maximum: 100

**RESULT: Tasks with empty descriptions cannot score above 55 points**
(40 base - 30 empty desc penalty + 45 from other fields = max 55)
```

### 8. Save & Wait
- Save the updated prompt
- Wait 10-30 minutes for AI to rescore all 173 tasks
- Run validation (see below)

---

## ✅ Validation

### Run This Command
```bash
python3 scripts/fix_empty_description_scoring_vulnerability.py
```

### Expected Output
```
✅ No tasks with empty descriptions (vulnerability not currently exploited)
✅ All 173 tasks have good descriptions
```

### If Issues Found
```bash
# The script will show:
⚠️  VULNERABILITY ACTIVE: X tasks with empty descriptions

# And offer to remediate:
Remediate empty descriptions? (yes/no):
```

---

## 📊 Before vs After

### Before (Vulnerable)
```
Task with empty description:
  Base: 40
  + task_id: 5
  + name: 15
  + description: 0  ← No penalty!
  + notes: 30
  + other: 15
  ──────────────
  = 105 → capped at 100 ❌
```

### After (Fixed)
```
Task with empty description:
  Base: 40
  - description empty: -30  ← NEW PENALTY!
  + task_id: 5
  + name: 15
  + description: 0
  + notes: 30
  + other: 15
  ──────────────
  = 55 max ✅
```

---

## 🚨 What Changed

| Aspect | Before | After |
|--------|--------|-------|
| Empty description penalty | None | -30 points |
| Max score with empty desc | 100 | 55 |
| Score calculation order | Add all, then penalize | Penalize first, then add |
| Detection threshold | None | <20 characters |
| Placeholder detection | No | Yes ("TODO", "TBD", etc.) |

---

## 📁 Reference Files

All documentation in `/home/micha/bqx_ml_v3/docs/`:

1. **[improved_record_audit_prompt.md](improved_record_audit_prompt.md)**
   - Complete new prompt text (copy-paste ready)

2. **[empty_description_vulnerability_analysis.md](empty_description_vulnerability_analysis.md)**
   - Full technical analysis
   - Risk assessment
   - Testing strategy

3. **[QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md)** (this file)
   - Quick reference for implementation

Script in `/home/micha/bqx_ml_v3/scripts/`:

4. **[fix_empty_description_scoring_vulnerability.py](../scripts/fix_empty_description_scoring_vulnerability.py)**
   - Automated validation
   - Can remediate empty descriptions if found
   - Generates descriptions from task context

---

## 💡 Key Insights

### Why This Matters
- **Description** explains WHAT the task does
- **Notes** explains HOW to do it (with code)
- Both are required for complete task documentation

### The Vulnerability
Current prompt allows perfect scores without descriptions because:
- No explicit penalty for empty fields
- Only awards 0 points (vs subtracting points)
- Task can score 105 from other fields → capped at 100

### The Fix
- Explicit -30 penalty applied BEFORE scoring
- Caps empty-description tasks at 55 points
- Treats description as required field
- Prevents future data quality issues

---

## 🔄 Rollback (If Needed)

If the fix causes issues:

1. Revert prompt in AirTable
   - Use field history feature
   - Or restore from backup in `scripts/investigate_record_score_field.py`

2. Document the issue
   - What went wrong?
   - Which tasks were affected?

3. Contact development team

---

## ✨ Success Criteria

After deploying the fix:

✅ All 173 tasks maintain their current scores (all have descriptions)
✅ Any new task with empty description scores ≤55
✅ AI audit reports "Empty description field (-30 points)" for violations
✅ No false positives (valid tasks incorrectly penalized)

---

**Time to Complete**: 5-10 minutes
**Difficulty**: Easy (copy-paste prompt update)
**Risk**: Very Low (all current tasks have descriptions)
**Impact**: High (prevents future data quality issues)

---

**Last Updated**: 2025-11-25
**Version**: 1.0
