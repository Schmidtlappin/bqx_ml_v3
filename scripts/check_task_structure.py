#!/usr/bin/env python3
"""
Check task structure in AirTable to understand format.
"""

import os
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

# Get all tasks
tasks = tasks_table.all()

print(f"Total tasks: {len(tasks)}")
print("\nFirst 10 task IDs and names:")
print("="*80)

for i, task in enumerate(tasks[:10]):
    task_id = task['fields'].get('task_id', 'NO_ID')
    name = task['fields'].get('name', 'NO_NAME')
    status = task['fields'].get('status', 'NO_STATUS')
    print(f"{i+1:3}. ID: {task_id:15} Status: {status:10} Name: {name[:50]}")

# Check for different phase patterns
print("\n\nPhase distribution:")
print("="*80)

phase_counts = {}
for task in tasks:
    task_id = task['fields'].get('task_id', '')
    # Extract phase identifier
    if '.' in task_id:
        phase = task_id.split('.')[1]
    elif task_id.startswith('P'):
        phase = task_id.split('-')[0] if '-' in task_id else task_id[:3]
    else:
        phase = 'UNKNOWN'

    phase_counts[phase] = phase_counts.get(phase, 0) + 1

for phase, count in sorted(phase_counts.items()):
    print(f"  {phase}: {count} tasks")

# Check current status distribution
print("\n\nStatus distribution:")
print("="*80)

status_counts = {}
for task in tasks:
    status = task['fields'].get('status', 'NO_STATUS')
    status_counts[status] = status_counts.get(status, 0) + 1

for status, count in sorted(status_counts.items()):
    print(f"  {status}: {count} tasks")