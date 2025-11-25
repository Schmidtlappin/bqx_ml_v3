# Deploy Updated Prompts for Tasks and Stages Tables

## Overview

Both the **Tasks** and **Stages** tables need updated `record_audit` prompts that:
1. ✅ Penalize empty descriptions (-30 points)
2. ✅ **ALWAYS output "Score: ##"** as the first line
3. ✅ Score range: **1-100** (never 0)
4. ✅ Cap scores at 55 if description is empty

---

## Current Status

### Tasks Table
- **Current Issues**: 11 tasks scoring 0 instead of 90-100 (wrong output format)
- **Cause**: Old prompt doesn't enforce "Score: ##" format
- **Fix Ready**: [docs/bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)

### Stages Table
- **Current Issues**: 47 stages scoring -310 to 0 (using Tasks prompt instead of Stages prompt)
- **Cause**: Stages table has Tasks prompt (looks for `task_id` instead of `stage_id`)
- **Fix Ready**: [docs/stages_record_audit_prompt.md](stages_record_audit_prompt.md)

---

## DEPLOYMENT INSTRUCTIONS

### 🔴 STEP 1: Deploy Tasks Prompt (CRITICAL)

**File**: [docs/bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)

**Steps**:
1. Open AirTable → **BQX ML V3 Base** → **Tasks table**
2. Click on the `record_audit` field header
3. Select "Configure AI" or "Edit Prompt"
4. **DELETE ALL** existing prompt text
5. **Copy lines 20-340** from `bulletproof_record_audit_prompt.md`
6. **Paste** into the prompt editor
7. **Save**
8. Wait 10-30 minutes for AI rescoring

**What to Copy** (lines 20-340):
```
You are a strict quality assessment agent for the BQX ML project Tasks table.

=== CRITICAL: EMPTY DESCRIPTION CHECK (DO THIS FIRST!) ===

BEFORE doing ANYTHING else, check the description field:
...
(entire prompt through line 340)
...
=================================================================
```

**Expected Results After Deployment**:
- 11 tasks currently scoring 0 → will score 90-100
- All tasks will have "Score: ##" as first line
- No tasks will score 0 (minimum score: 1)

---

### 🔴 STEP 2: Deploy Stages Prompt (CRITICAL)

**File**: [docs/stages_record_audit_prompt.md](stages_record_audit_prompt.md)

**Steps**:
1. Open AirTable → **BQX ML V3 Base** → **Stages table**
2. Click on the `record_audit` field header
3. Select "Configure AI" or "Edit Prompt"
4. **DELETE ALL** existing prompt text
5. **Copy lines 11-328** from `stages_record_audit_prompt.md`
6. **Paste** into the prompt editor
7. **Save**
8. Wait 10-30 minutes for AI rescoring

**What to Copy** (lines 11-328):
```
You are a strict quality assessment agent for the BQX ML project Stages table.

=== CRITICAL: EMPTY DESCRIPTION CHECK (DO THIS FIRST!) ===

BEFORE doing ANYTHING else, check the description field:
...
(entire prompt through line 328)
...
=================================================================
```

**Expected Results After Deployment**:
- 47 stages currently scoring -310 to 0 → will score correctly (1-100)
- All stages will have "Score: ##" as first line
- No more "missing task_id" penalties (looks for stage_id instead)
- No stages will score 0 (minimum score: 1)

---

## KEY DIFFERENCES BETWEEN PROMPTS

| Aspect | Tasks Prompt | Stages Prompt |
|--------|--------------|---------------|
| **ID Field** | task_id (MP##.P##.S##.T##) | stage_id (MP##.P##.S##) |
| **Link Fields** | stage_link | phase_link, plan_link, task_link |
| **Penalty for Missing ID** | -50 points | -50 points |
| **Context** | Task-level (specific implementation) | Stage-level (group of tasks) |
| **File Location** | [bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md) | [stages_record_audit_prompt.md](stages_record_audit_prompt.md) |

---

## VERIFICATION CHECKLIST

After deploying both prompts, verify:

### Tasks Table (After 10-30 minutes)
```bash
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
tasks = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Tasks').all()

# Check for zero scores
zero_scores = [t for t in tasks if t['fields'].get('record_score') == 0]
print(f'Tasks scoring 0: {len(zero_scores)}')

# Check for missing Score: prefix in audit
bad_format = []
for t in tasks:
    audit = t['fields'].get('record_audit', {})
    if isinstance(audit, dict):
        value = audit.get('value', '')
        if not value.startswith('Score:'):
            bad_format.append(t['fields'].get('task_id'))

print(f'Tasks with bad output format: {len(bad_format)}')
print(f'Total tasks: {len(tasks)}')
"
```

**Expected Output**:
```
Tasks scoring 0: 0
Tasks with bad output format: 0
Total tasks: 173
```

### Stages Table (After 10-30 minutes)
```bash
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
stages = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Stages').all()

# Check for zero/negative scores
bad_scores = [s for s in stages if s['fields'].get('record_score', 0) <= 0]
print(f'Stages scoring <=0: {len(bad_scores)}')

# Check for missing Score: prefix in audit
bad_format = []
for s in stages:
    audit = s['fields'].get('record_audit', {})
    if isinstance(audit, dict):
        value = audit.get('value', '')
        if not value.startswith('Score:'):
            bad_format.append(s['fields'].get('stage_id'))

print(f'Stages with bad output format: {len(bad_format)}')
print(f'Total stages: {len(stages)}')
"
```

**Expected Output**:
```
Stages scoring <=0: 0
Stages with bad output format: 0
Total stages: 72
```

---

## TESTING EMPTY DESCRIPTION SCORING

After deployment, run the test script to verify empty descriptions are capped at 55:

```bash
python3 scripts/test_empty_description_scoring.py
```

**Expected Results**:
```
TEST 1: EMPTY DESCRIPTION
  Score: ≤55 ✓

TEST 2: GOOD DESCRIPTION
  Score: ≥90 ✓

✅ VULNERABILITY FIXED!
   Empty description correctly capped at 55
   Prompt is working as intended
```

---

## ROLLBACK INSTRUCTIONS

If issues occur after deployment, you can rollback:

### Tasks Table Rollback
1. Open AirTable → Tasks table → `record_audit` field → Configure AI
2. Replace prompt with previous version (if saved)
3. Or temporarily use: "Assess task quality. Output format: Score: [1-100]"

### Stages Table Rollback
1. Open AirTable → Stages table → `record_audit` field → Configure AI
2. Replace prompt with previous version (if saved)
3. Or temporarily use: "Assess stage quality. Output format: Score: [1-100]"

---

## TIMELINE

| Step | Duration | Description |
|------|----------|-------------|
| Deploy Tasks prompt | 2 minutes | Copy/paste prompt into AirTable |
| Deploy Stages prompt | 2 minutes | Copy/paste prompt into AirTable |
| **Wait for rescoring** | 10-30 minutes | AirTable AI rescores all records |
| Run verification | 1 minute | Check scores and formats |
| Run test script | 3-5 minutes | Verify empty description handling |
| **Total** | ~15-40 minutes | End-to-end deployment |

---

## CRITICAL SUCCESS CRITERIA

✅ **Tasks Table**:
- 0 tasks scoring 0 (was 11)
- 162+ tasks scoring ≥90 (was 162)
- All tasks have "Score: ##" format

✅ **Stages Table**:
- 0 stages scoring ≤0 (was 47)
- 25+ stages scoring ≥90 (currently 25)
- All stages have "Score: ##" format

✅ **Both Tables**:
- Empty descriptions (if any exist) score ≤55
- All scores are 1-100 (never 0)
- "Score: ##" always appears as first line

---

## FILES REFERENCE

| File | Purpose | Deploy To |
|------|---------|-----------|
| [bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md) | Tasks table prompt | Tasks.record_audit (lines 20-340) |
| [stages_record_audit_prompt.md](stages_record_audit_prompt.md) | Stages table prompt | Stages.record_audit (lines 11-328) |
| [test_empty_description_scoring.py](../scripts/test_empty_description_scoring.py) | Test script | Run after deployment |
| [URGENT_PROMPT_FIX.md](URGENT_PROMPT_FIX.md) | Original issue docs | Reference only |

---

## SUPPORT

If issues persist after deployment:
1. Check prompt was copied completely (full text, no truncation)
2. Verify you're editing the correct table's `record_audit` field
3. Wait full 30 minutes for AI rescoring
4. Check AirTable field configuration (should be type: aiText)
5. Verify referenced field IDs match your table structure

---

**Status**: Ready for immediate deployment
**Priority**: CRITICAL
**Risk**: Very Low (all current tasks/stages will be rescored correctly)
**Impact**: High (fixes 11 + 47 = 58 incorrectly scored records)

**Last Updated**: 2025-11-25
