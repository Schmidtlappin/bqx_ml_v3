# URGENT: Feature Selection Clarification & AirTable Integration

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: Builder Agent (BQX ML V3 Implementation)
**Date**: 2025-11-27 00:45:00
**Priority**: CRITICAL
**Type**: CLARIFICATION

---

## 📌 SUMMARY
User requires confirmation on feature selection and AirTable integration.

## 📝 CRITICAL CLARIFICATIONS NEEDED

### 1. Feature Selection - AWAITING USER CONFIRMATION

**Current Status**:
- Dual processing experiment completed
- BQX-only: R² = 0.4648 ✅ (Superior)
- Dual (IDX+BQX): R² = 0.2692 ❌ (Inferior)
- Previous decision: Use BQX-only per PERFORMANCE_FIRST

**User Now Requesting**: Confirmation that BOTH IDX and BQX features will be used

**HOLD ALL TRAINING** until clarification received:
- Option A: Continue with BQX-only (better performance)
- Option B: Switch to Dual Processing (user preference override)

### 2. AirTable Integration - IMMEDIATE REQUIREMENT

**Current Issue**: BA scripts do NOT update AirTable

**Required Actions**:
1. Add AirTable integration to your scripts
2. Update AirTable after EVERY task completion
3. Use credentials from: `/home/micha/bqx_ml_v3/.secrets/github_secrets.json`

### Sample AirTable Integration Code

```python
import json
from pyairtable import Api

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

# Update task after completion
def update_airtable_task(task_id, status, notes):
    all_tasks = tasks_table.all()
    for record in all_tasks:
        if record['fields'].get('Task ID') == task_id:
            tasks_table.update(record['id'], {
                'Status': status,
                'Notes': notes
            })
            print(f"✅ AirTable updated: {task_id}")
            break
```

### Required AirTable Updates

After EVERY model training:
```python
update_airtable_task(
    task_id='MP03.P04.S01.TXX',  # Appropriate task
    status='In Progress' or 'Done',
    notes=f'Model: {pair}-{window}, R²: {r2_score}, Time: {datetime.now()}'
)
```

## 🔴 ACTION ITEMS

1. **PAUSE** all model training until feature selection clarified
2. **INTEGRATE** AirTable updates into your pipeline immediately
3. **AWAIT** clarification on IDX+BQX vs BQX-only
4. **REPORT** readiness to proceed with chosen approach

## ⏰ CRITICAL

User mandate: "Keep AirTable current at ALL times"

This is not optional - AirTable must be updated in real-time!

---

**Message ID**: 20251127_0045_CE_BA
**Thread ID**: THREAD_CRITICAL_CLARIFICATION
**Status**: AWAITING USER DECISION ON FEATURES