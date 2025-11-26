#!/usr/bin/env python3
"""
Check current status of all tasks in AirTable.
"""

import json
from collections import defaultdict
from pyairtable import Api

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

# Get all tasks
all_tasks = tasks_table.all()

print("="*80)
print("📊 AIRTABLE TASKS STATUS CHECK")
print("="*80)
print(f"\nTotal tasks: {len(all_tasks)}")

# Count by status
status_counts = defaultdict(int)
phase_status = defaultdict(lambda: defaultdict(int))

for task in all_tasks:
    status = task['fields'].get('status', 'Unknown')
    task_id = task['fields'].get('task_id', '')

    # Extract phase
    if '.' in task_id:
        parts = task_id.split('.')
        if len(parts) >= 2:
            phase = parts[1]  # e.g., P01, P02, etc.
            phase_status[phase][status] += 1

    status_counts[status] += 1

# Overall status
print("\n📈 OVERALL STATUS DISTRIBUTION:")
print("-"*40)
for status, count in sorted(status_counts.items()):
    percentage = (count / len(all_tasks)) * 100
    print(f"  {status:15} {count:3} tasks ({percentage:5.1f}%)")

# Phase-by-phase breakdown
print("\n📊 STATUS BY PHASE:")
print("-"*40)
for phase in sorted(phase_status.keys()):
    phase_tasks = sum(phase_status[phase].values())
    print(f"\n{phase}:")
    for status, count in sorted(phase_status[phase].items()):
        percentage = (count / phase_tasks) * 100
        print(f"  {status:15} {count:3} tasks ({percentage:5.1f}%)")

# Check for tasks with real build outcomes
print("\n🔍 CHECKING FOR REAL BUILD OUTCOMES:")
print("-"*40)

real_build_count = 0
simulated_count = 0
no_outcome_count = 0

for task in all_tasks:
    notes = task['fields'].get('notes', '')
    if 'REAL BUILD OUTCOME' in notes or 'REAL EXECUTION OUTCOME' in notes:
        real_build_count += 1
    elif 'EXECUTION OUTCOME' in notes or 'Execution Outcome' in notes:
        simulated_count += 1
    else:
        no_outcome_count += 1

print(f"  Tasks with REAL build outcomes:     {real_build_count}")
print(f"  Tasks with simulated outcomes:      {simulated_count}")
print(f"  Tasks without execution outcomes:   {no_outcome_count}")

# Sample some Done tasks to check their notes
print("\n📝 SAMPLE OF 'DONE' TASKS:")
print("-"*40)
done_tasks = [t for t in all_tasks if t['fields'].get('status') == 'Done'][:5]
for i, task in enumerate(done_tasks, 1):
    task_id = task['fields'].get('task_id', 'NO_ID')
    notes = task['fields'].get('notes', '')

    # Check what type of outcome it has
    if 'REAL BUILD OUTCOME' in notes or 'REAL EXECUTION OUTCOME' in notes:
        outcome_type = "REAL"
    elif 'EXECUTION OUTCOME' in notes:
        outcome_type = "SIMULATED"
    else:
        outcome_type = "UNKNOWN"

    print(f"{i}. {task_id}: Outcome type = {outcome_type}")

print("\n" + "="*80)
print("✅ STATUS CHECK COMPLETE")
print("="*80)