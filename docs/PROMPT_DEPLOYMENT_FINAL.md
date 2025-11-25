# Final Prompt Deployment Guide

## 🔴 CRITICAL ISSUE
Empty descriptions in Tasks table are scoring 100 instead of being capped at 55.
AirTable's AI agent cannot handle complex prompts - they must be SIMPLE.

## 📊 Prompt Comparison

| Prompt File | Complexity | Lines | Recommendation |
|-------------|------------|-------|----------------|
| [FOOLPROOF_tasks_prompt.md](FOOLPROOF_tasks_prompt.md) | ⭐ BEST | 95 | **USE THIS - Step-by-step instructions** |
| [MINIMAL_tasks_prompt.md](MINIMAL_tasks_prompt.md) | Good | 75 | Second choice - very simple |
| [SIMPLE_tasks_prompt.md](SIMPLE_tasks_prompt.md) | OK | 150 | Has remediation but still complex |
| ~~bulletproof_record_audit_prompt.md~~ | Too Complex | 340 | ❌ AI can't follow |
| ~~FINAL_tasks_prompt.md~~ | Too Complex | 298 | ❌ Output format issues |
| ~~ULTRA_STRICT_tasks_prompt.md~~ | Too Complex | 220 | ❌ Too many warnings |

## 🚀 RECOMMENDED DEPLOYMENT

### Use FOOLPROOF_tasks_prompt.md

**File**: [docs/FOOLPROOF_tasks_prompt.md](FOOLPROOF_tasks_prompt.md)

**Why**:
- Numbered steps (1-7) that AI must follow sequentially
- Explicit "If description < 20 chars AND total > 55: Final = 55"
- Simple output format
- Only 95 lines

**Deploy**:
```bash
1. Open AirTable → BQX ML V3 Base → Tasks table
2. Click on `record_audit` field header
3. Select "Configure AI"
4. DELETE all existing text
5. Copy lines 5-95 from FOOLPROOF_tasks_prompt.md
6. Paste and Save
7. Wait 10-30 minutes for rescoring
```

## 📋 What Each Prompt Does

### FOOLPROOF (Recommended)
```
Step 1: Count description length
Step 2: If < 20, set MAX = 55
Step 3-5: Calculate score
Step 6: Apply cap if needed
Step 7: Output Score: [number]
```
**Strength**: Impossible to miss the cap logic

### MINIMAL (Backup Option)
```
Check description first
If < 20: max = 55
Calculate score
Output Score: [number]
```
**Strength**: Very short (75 lines)

### SIMPLE (If you need remediation)
```
Basic scoring with remediation guidance
Includes specific fix instructions
```
**Strength**: Helpful remediation text

## ✅ Verification After Deployment

```python
# Test script to verify empty descriptions cap at 55
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
tasks = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Tasks').all()

# Find task MP03.P07.S04.T01 (known empty description)
test_task = [t for t in tasks if t['fields'].get('task_id') == 'MP03.P07.S04.T01']
if test_task:
    score = test_task[0]['fields'].get('record_score', 0)
    print(f'Task with empty description scored: {score}')
    print(f'Expected: ≤55')
    print(f'Success: {"YES" if score <= 55 else "NO - PROMPT FAILED"}')
"
```

## 🎯 Success Criteria

After deployment, ALL tasks with empty descriptions should:
1. Score ≤55 (not 100)
2. Have "Score: [number]" as first line of record_audit
3. Show "Capped: Yes" in audit output

## 📝 Quick Reference

**Problem**: Empty descriptions scoring 100
**Root Cause**: AI agent can't handle complex prompts
**Solution**: FOOLPROOF_tasks_prompt.md with step-by-step instructions
**Deploy Time**: 2 minutes
**Wait Time**: 10-30 minutes for rescoring
**Test**: Check MP03.P07.S04.T01 scores ≤55

## 🔗 All Prompt Files

Tasks prompts created (in order of recommendation):
1. [FOOLPROOF_tasks_prompt.md](FOOLPROOF_tasks_prompt.md) ⭐ **DEPLOY THIS**
2. [MINIMAL_tasks_prompt.md](MINIMAL_tasks_prompt.md)
3. [SIMPLE_tasks_prompt.md](SIMPLE_tasks_prompt.md)
4. [bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md) ❌
5. [FINAL_tasks_prompt.md](FINAL_tasks_prompt.md) ❌
6. [ULTRA_STRICT_tasks_prompt.md](ULTRA_STRICT_tasks_prompt.md) ❌

Stages prompts:
1. [SIMPLE_stages_prompt.md](SIMPLE_stages_prompt.md) - For Stages table
2. [FINAL_stages_prompt.md](FINAL_stages_prompt.md) - For Stages table

## ⚠️ Important Notes

1. **AI Agent Limitations**: AirTable's AI cannot handle prompts >150 lines well
2. **Simplicity Wins**: Step-by-step numbered instructions work best
3. **Output Format**: MUST start with "Score: [number]" for record_score extraction
4. **Test First**: Always test with empty description tasks after deployment

---

**Status**: Ready for deployment
**Recommended Action**: Deploy FOOLPROOF_tasks_prompt.md NOW
**Expected Result**: Empty descriptions will score ≤55 instead of 100