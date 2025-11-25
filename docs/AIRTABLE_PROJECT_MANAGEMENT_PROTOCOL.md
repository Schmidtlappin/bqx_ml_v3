# AIRTABLE PROJECT MANAGEMENT PROTOCOL
## BQX ML V3 Execution Framework

### 🎯 CORE PRINCIPLE: "Plan First, Execute Via AirTable"

## 📋 AIRTABLE STRUCTURE

### Base Information
- **Base ID**: appR3PPnrNkVo48mO
- **API Key**: (in .secrets/github_secrets.json)
- **Project**: P03
- **Table**: Plans

### Task Fields
```json
{
  "Task ID": "P03.2.001",
  "Task Name": "Create BigQuery dataset bqx_ml",
  "Phase": "P03.2",
  "Status": "Not Started | In Progress | Complete | Blocked",
  "Assigned To": "BQXML CHIEF ENGINEER",
  "Started": "2024-11-24T20:00:00Z",
  "Completed": null,
  "Progress": "0%",
  "Notes": "",
  "Errors": "",
  "Resolution": ""
}
```

## 🔄 WORKFLOW PROTOCOL

### 1. BEFORE ANY WORK: Check AirTable
```python
import requests
import json

def get_next_task():
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Get tasks with "Not Started" status
    response = requests.get(
        f'https://api.airtable.com/v0/{BASE_ID}/Plans',
        headers=headers,
        params={
            'filterByFormula': 'AND({Status}="Not Started", {Phase}="P03.2")',
            'sort[0][field]': 'Task ID',
            'sort[0][direction]': 'asc'
        }
    )

    tasks = response.json()['records']
    return tasks[0] if tasks else None

# Get next task
task = get_next_task()
if not task:
    print("No tasks available. Check AirTable for new assignments.")
    exit()
```

### 2. START WORK: Update Status
```python
def start_task(record_id):
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'fields': {
            'Status': 'In Progress',
            'Started': datetime.now().isoformat(),
            'Assigned To': 'BQXML CHIEF ENGINEER'
        }
    }

    response = requests.patch(
        f'https://api.airtable.com/v0/{BASE_ID}/Plans/{record_id}',
        headers=headers,
        json=data
    )

    return response.json()

# Start the task
start_task(task['id'])
print(f"Started: {task['fields']['Task Name']}")
```

### 3. EXECUTE: With Full Automation
```python
def execute_task(task):
    task_name = task['fields']['Task Name']

    try:
        if 'BigQuery dataset' in task_name:
            # Automated execution
            result = subprocess.run(
                ['bq', 'mk', '-d', '--location=us-east1', '--project=bqx-ml', 'bqx_ml'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise Exception(result.stderr)

        elif 'lag_bqx' in task_name:
            # Execute SQL for lag tables
            pair = extract_pair_from_task(task_name)
            create_lag_table(pair)

        elif 'GitHub secrets' in task_name:
            # Run automated script
            subprocess.run(
                ['bash', '/home/micha/bqx_ml_v3/.secrets/setup_github_secrets.sh'],
                check=True
            )

        return "Success"

    except Exception as e:
        # MANDATORY: Investigate and resolve
        return investigate_and_resolve(e, task)
```

### 4. ERROR RESOLUTION: Never Skip
```python
def investigate_and_resolve(error, task):
    """
    USER MANDATE: All errors must be investigated and resolved in real-time
    Never skip, never fake completion
    """

    error_type = classify_error(str(error))

    if 'Permission denied' in str(error):
        # Fix permissions automatically
        fix_permissions()
        # Retry task
        return execute_task(task)

    elif 'already exists' in str(error):
        # Verify existence and continue
        if verify_resource_exists():
            return "Already exists - verified"

    elif 'not found' in str(error):
        # Create missing prerequisites
        create_prerequisites()
        # Retry task
        return execute_task(task)

    else:
        # Log for escalation but NEVER skip
        log_error_to_airtable(task['id'], str(error))
        # Attempt alternative solution
        return attempt_alternative_solution(task)
```

### 5. COMPLETE: Update AirTable
```python
def complete_task(record_id, result, progress_percent):
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'fields': {
            'Status': 'Complete',
            'Completed': datetime.now().isoformat(),
            'Progress': f"{progress_percent}%",
            'Notes': result
        }
    }

    response = requests.patch(
        f'https://api.airtable.com/v0/{BASE_ID}/Plans/{record_id}',
        headers=headers,
        json=data
    )

    return response.json()

# Complete the task
complete_task(task['id'], "BigQuery dataset created successfully", 100)
```

## 📊 TASK TEMPLATES FOR P03.2

### Pre-loaded Tasks for AirTable
```python
P03_2_TASKS = [
    # Infrastructure Setup
    {"id": "P03.2.001", "name": "Create BigQuery dataset bqx_ml", "priority": 1},
    {"id": "P03.2.002", "name": "Create Cloud Storage buckets", "priority": 2},
    {"id": "P03.2.003", "name": "Deploy GitHub secrets", "priority": 3},

    # Lag Tables (28 pairs × 1 type)
    {"id": "P03.2.010", "name": "Create lag_bqx_eurusd table", "priority": 10},
    {"id": "P03.2.011", "name": "Create lag_bqx_gbpusd table", "priority": 11},
    # ... continue for all 28 pairs

    # Regime Tables (28 pairs × 1 type)
    {"id": "P03.2.040", "name": "Create regime_bqx_eurusd table", "priority": 40},
    # ... continue for all 28 pairs

    # Aggregation Tables (28 pairs × 1 type)
    {"id": "P03.2.070", "name": "Create agg_bqx_eurusd table", "priority": 70},
    # ... continue for all 28 pairs

    # Alignment Tables (28 pairs × 1 type)
    {"id": "P03.2.100", "name": "Create align_bqx_eurusd table", "priority": 100},
    # ... continue for all 28 pairs
]
```

## 🚫 PROHIBITED BEHAVIORS

### Never Do This:
```python
# ❌ WRONG - Working without AirTable
create_bigquery_dataset()  # No AirTable task!

# ❌ WRONG - Skipping errors
try:
    create_table()
except:
    pass  # NEVER ignore errors!

# ❌ WRONG - Faking completion
update_airtable("Complete")  # Without actually doing the work

# ❌ WRONG - Manual TODO lists
todos = ["Create dataset", "Deploy secrets"]  # Use AirTable instead!
```

### Always Do This:
```python
# ✅ CORRECT - AirTable-driven execution
task = get_next_task_from_airtable()
start_task(task)
result = execute_with_automation(task)
investigate_all_errors(result)
complete_task_in_airtable(task)

# ✅ CORRECT - Error investigation
try:
    create_table()
except Exception as e:
    root_cause = investigate_error(e)
    solution = resolve_error(root_cause)
    retry_with_solution(solution)

# ✅ CORRECT - Automated execution
subprocess.run(['bash', 'setup_github_secrets.sh'], check=True)
```

## 📈 PROGRESS TRACKING

### Calculate Progress
```python
def calculate_phase_progress():
    """
    P03.2 has 112 tables total:
    - 28 lag tables
    - 28 regime tables
    - 28 aggregation tables
    - 28 alignment tables
    """

    completed_tables = count_completed_tables()
    total_tables = 112

    progress = (completed_tables / total_tables) * 100

    # Update phase progress
    update_phase_progress('P03.2', progress)

    return progress
```

### Milestone Updates
```python
MILESTONES = {
    25: "Lag tables complete",
    50: "Regime tables complete",
    75: "Aggregation tables complete",
    100: "All feature tables complete"
}

def check_milestone(progress):
    for threshold, description in MILESTONES.items():
        if progress >= threshold:
            update_airtable_milestone(description)
```

## 🔑 API INTEGRATION

### Full AirTable Integration Class
```python
class AirTableProjectManager:
    def __init__(self):
        self.base_id = "appR3PPnrNkVo48mO"
        self.api_key = self.load_api_key()
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def load_api_key(self):
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
            secrets = json.load(f)
            return secrets['secrets']['AIRTABLE_API_KEY']['value']

    def get_next_task(self):
        # Implementation

    def start_task(self, task_id):
        # Implementation

    def complete_task(self, task_id, result):
        # Implementation

    def report_error(self, task_id, error, resolution):
        # Implementation

    def calculate_progress(self):
        # Implementation

# Usage
pm = AirTableProjectManager()
task = pm.get_next_task()
pm.start_task(task['id'])
# ... execute work ...
pm.complete_task(task['id'], "Success")
```

## ✅ SUCCESS CRITERIA

You are successful when:
1. Every task starts with AirTable lookup
2. Every task updates AirTable on completion
3. All errors are investigated and resolved
4. No manual processes - full automation
5. Progress is tracked in real-time

---
**Remember: AirTable is your project manager, not a TODO list.**
**Plan in AirTable. Execute via AirTable. Report to AirTable.**
**Automate everything. Investigate all errors. Never skip tasks.**