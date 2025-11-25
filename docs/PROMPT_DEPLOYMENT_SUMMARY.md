# Prompt Deployment - Quick Reference

## 🎯 Goal
Update both Tasks and Stages table prompts to:
- Penalize empty descriptions (-30 points)
- ALWAYS output "Score: ##" as first line
- Score range: 1-100 (never 0)

---

## 📋 QUICK DEPLOYMENT

### Tasks Table → [bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)
```bash
1. AirTable → Tasks table → record_audit field → Configure AI
2. Delete all existing text
3. Copy lines 20-340 from bulletproof_record_audit_prompt.md
4. Paste and Save
5. Wait 10-30 minutes
```

### Stages Table → [stages_record_audit_prompt.md](stages_record_audit_prompt.md)
```bash
1. AirTable → Stages table → record_audit field → Configure AI
2. Delete all existing text
3. Copy lines 11-328 from stages_record_audit_prompt.md
4. Paste and Save
5. Wait 10-30 minutes
```

---

## 🔍 VERIFICATION (After 30 minutes)

### Check Tasks Table:
```bash
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
tasks = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Tasks').all()

zero = len([t for t in tasks if t['fields'].get('record_score') == 0])
print(f'✓ Tasks scoring 0: {zero} (expected: 0)')
print(f'✓ Total tasks: {len(tasks)} (expected: 173)')
"
```

### Check Stages Table:
```bash
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
stages = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Stages').all()

bad = len([s for s in stages if s['fields'].get('record_score', 0) <= 0])
print(f'✓ Stages scoring ≤0: {bad} (expected: 0)')
print(f'✓ Total stages: {len(stages)} (expected: 72)')
"
```

---

## 📊 EXPECTED IMPACT

| Table | Issue | Before | After |
|-------|-------|--------|-------|
| Tasks | Scoring 0 | 11 tasks | 0 tasks |
| Tasks | Missing "Score:" format | 11 tasks | 0 tasks |
| Stages | Scoring ≤0 | 47 stages | 0 stages |
| Stages | Wrong prompt (task_id) | 72 stages | 0 stages |
| **TOTAL** | **Fixed records** | **58** | **0** |

---

## 📁 FILES

- **[DEPLOY_BOTH_PROMPTS.md](DEPLOY_BOTH_PROMPTS.md)** ← Full deployment guide
- **[bulletproof_record_audit_prompt.md](bulletproof_record_audit_prompt.md)** ← Tasks prompt
- **[stages_record_audit_prompt.md](stages_record_audit_prompt.md)** ← Stages prompt
- **[test_empty_description_scoring.py](../scripts/test_empty_description_scoring.py)** ← Test script

---

**Status**: ✅ Ready for deployment
**Priority**: 🔴 CRITICAL
**Time**: ~4 minutes deploy + 30 minutes AI rescoring
