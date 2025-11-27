# MANDATORY: AirTable Real-Time Update Requirements

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: Builder Agent (BQX ML V3 Implementation)
**Date**: 2025-11-27 01:35:00
**Priority**: CRITICAL
**Type**: COMPLIANCE DIRECTIVE

---

## 🔴 MANDATORY REQUIREMENT

Per user mandate: **"Keep AirTable current at ALL times"**

This is NOT optional. You MUST update AirTable directly after each significant event.

## 🔑 AIRTABLE CREDENTIALS LOCATION

```python
CREDENTIALS_PATH = '/home/micha/bqx_ml_v3/.secrets/github_secrets.json'

# Load credentials
import json
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']
```

## 📝 UPDATE REQUIREMENTS

### When to Update AirTable

**IMMEDIATE UPDATES REQUIRED**:
1. ✅ After EACH model trains → Update specific task
2. ✅ After EACH currency pair completes (7 models) → Update phase status
3. ✅ After fixing data infrastructure → Update resolution status
4. ✅ After implementing Smart Dual → Update architecture status
5. ✅ After any failure/error → Update with issue details
6. ✅ At start of major operation → Mark as "In Progress"
7. ✅ At completion of operation → Mark as "Done"

### What to Include in Updates

```python
def update_airtable_model_training(pair, window, metrics):
    """
    MANDATORY: Call after EVERY model training
    """
    update_fields = {
        'status': 'Done',  # or 'In Progress', 'Todo'
        'notes': f"""
Model Training Update - {datetime.now().isoformat()}
================================================
Pair: {pair}
Window: {window}
R² Score: {metrics['r2']:.4f}
Directional Accuracy: {metrics['dir_acc']:.2%}
RMSE: {metrics['rmse']:.4f}
Training Time: {metrics['time']:.2f}s
Quality Gates: {'PASSED' if metrics['r2'] >= 0.35 else 'FAILED'}
Feature Set: {'Smart Dual' if using_dual else 'BQX-only'}
================================================
        """
    }

    # Find and update the relevant task
    tasks_table.update(record_id, update_fields)
    print(f"✅ AirTable updated for {pair}-{window}")
```

## 📋 FIELD NAMES IN AIRTABLE

**Correct field names (lowercase)**:
- `task_id` - Task identifier (e.g., "MP03.P01.S01.T01")
- `status` - Must be: "Todo", "In Progress", or "Done"
- `notes` - Detailed progress updates
- `priority` - Must be: "Critical", "High", "Medium", or "Low"
- `name` - Task name/description

## 🎯 EXPECTED UPDATE FREQUENCY

### During 196 Model Training:
- **Minimum**: Update after each model (196 updates)
- **Preferred**: Update with batch progress every 10 models
- **Critical**: Update if any failures occur

### Example Update Schedule:
```
Hour 0: "Starting data generation for 28 pairs"
Hour 1: "Generated 25% of synthetic data (7 pairs complete)"
Hour 2: "Generated 50% of synthetic data (14 pairs complete)"
Hour 3: "Data generation complete. Starting validation"
Hour 4: "Starting model training - EURUSD"
Hour 5: "EURUSD complete (7/196 models). R² avg: 0.52"
...continues for each pair...
Hour 14: "All 196 models complete. Generating report"
```

## ⚠️ CRITICAL IMPLEMENTATION

### Add to Your Training Script:

```python
from pyairtable import Api
import json
from datetime import datetime

class AirTableUpdater:
    def __init__(self):
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            self.api = Api(secrets['secrets']['AIRTABLE_API_KEY']['value'])
            self.base = self.api.base(secrets['secrets']['AIRTABLE_BASE_ID']['value'])
            self.tasks = self.base.table('Tasks')

    def update_task(self, task_id, status, notes_append):
        """Update a specific task in AirTable"""
        all_tasks = self.tasks.all()
        for record in all_tasks:
            if record['fields'].get('task_id') == task_id:
                current_notes = record['fields'].get('notes', '')
                new_notes = f"{current_notes}\n\n{notes_append}"
                self.tasks.update(record['id'], {
                    'status': status,
                    'notes': new_notes
                })
                return True
        return False

    def log_model_result(self, pair, window, metrics):
        """Log model training results"""
        task_id = f"MP03.P04.S01.T{window}"  # Adjust as needed
        notes = f"""
[{datetime.now().isoformat()}] Model Result:
• {pair}-{window}: R²={metrics['r2']:.4f}
• Quality: {'✅ PASS' if metrics['r2'] >= 0.35 else '❌ FAIL'}
"""
        self.update_task(task_id, 'In Progress', notes)

# MANDATORY: Initialize at script start
airtable = AirTableUpdater()

# MANDATORY: Update after each model
airtable.log_model_result(pair, window, {
    'r2': r2_score,
    'dir_acc': directional_accuracy,
    'rmse': rmse,
    'time': training_time
})
```

## 🚨 COMPLIANCE CHECK

I will verify AirTable updates by:
1. Monitoring update frequency
2. Checking timestamp gaps
3. Validating status progression
4. Reviewing notes completeness

**Non-compliance will require explanation to user.**

## 📞 CONFIRMATION REQUIRED

**IMMEDIATELY CONFIRM**:
1. ✅ You have located the credentials file
2. ✅ You can successfully connect to AirTable
3. ✅ You understand the update requirements
4. ✅ You have integrated AirTable updates into your scripts

Reply with confirmation and show a test update to verify connectivity.

## ⚡ REMEMBER

This is a **USER MANDATE**:
> "Keep AirTable current at ALL times"

Failure to maintain real-time AirTable updates violates core project requirements.

---

**Message ID**: 20251127_0135_CE_BA
**Thread ID**: THREAD_AIRTABLE_COMPLIANCE
**Status**: MANDATORY IMPLEMENTATION
**Compliance**: REQUIRED