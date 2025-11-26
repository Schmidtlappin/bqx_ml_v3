#!/usr/bin/env python3
"""
Inspect Phase P01 tasks in detail to understand baseline model development requirements
"""

import requests
import json
from typing import Dict, List, Any

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']
TASKS_TABLE = 'tblQ9VXdTgZiIR6H2'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def get_phase_tasks(phase_prefix: str = "MP03.P01"):
    """Get all tasks for a specific phase"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TASKS_TABLE}'

    all_records = []
    offset = None

    while True:
        params = {
            'filterByFormula': f'FIND("{phase_prefix}", {{task_id}})',
            'sort[0][field]': 'task_id',
            'sort[0][direction]': 'asc'
        }

        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            all_records.extend(data['records'])

            if 'offset' in data:
                offset = data['offset']
            else:
                break
        else:
            print(f"Error: {response.status_code}")
            break

    return all_records

def display_task_details(tasks: List[Dict]):
    """Display task details in a structured format"""

    print("=" * 100)
    print("PHASE P01: BASELINE MODEL DEVELOPMENT - DETAILED TASK BREAKDOWN")
    print("=" * 100)
    print(f"\nTotal tasks in Phase P01: {len(tasks)}\n")

    # Group by stage
    stages = {}
    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id', '')

        # Extract stage from task_id (e.g., MP03.P01.S01.T01 -> S01)
        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage = parts[2]  # Get S01, S02, etc.
                if stage not in stages:
                    stages[stage] = []
                stages[stage].append(task)

    # Display by stage
    for stage_id in sorted(stages.keys()):
        stage_tasks = stages[stage_id]
        print(f"\n{'='*100}")
        print(f"STAGE {stage_id}: {len(stage_tasks)} tasks")
        print(f"{'='*100}")

        for task in stage_tasks:
            fields = task['fields']
            print(f"\n{'─'*80}")
            print(f"📌 Task ID: {fields.get('task_id', 'N/A')}")
            print(f"📋 Name: {fields.get('name', 'N/A')}")
            print(f"🎯 Priority: {fields.get('priority', 'N/A')}")
            print(f"📊 Status: {fields.get('status', 'N/A')}")

            # Clean up description
            description = fields.get('description', 'No description')
            if description:
                # Remove excessive newlines and format
                description = description.replace('\n\n\n', '\n\n')
                print(f"\n📝 Description:")
                print("─" * 40)
                # Show first 500 chars if too long
                if len(description) > 500:
                    print(description[:500] + "...")
                else:
                    print(description)

            # Show notes if present
            notes = fields.get('notes', '')
            if notes and notes.strip():
                print(f"\n📓 Notes:")
                print("─" * 40)
                if len(notes) > 300:
                    print(notes[:300] + "...")
                else:
                    print(notes)

            # Show estimated hours
            est_hours = fields.get('estimated_hours', 0)
            if est_hours:
                print(f"\n⏱️  Estimated Hours: {est_hours}")

def main():
    # Get Phase P01 tasks
    print("\nFetching Phase P01 tasks from AirTable...")
    tasks = get_phase_tasks("MP03.P01")

    if tasks:
        display_task_details(tasks)

        # Summary statistics
        print(f"\n{'='*100}")
        print("SUMMARY STATISTICS")
        print(f"{'='*100}")

        # Count by priority
        priorities = {}
        total_hours = 0
        for task in tasks:
            fields = task['fields']
            priority = fields.get('priority', 'Not Set')
            priorities[priority] = priorities.get(priority, 0) + 1
            total_hours += fields.get('estimated_hours', 0)

        print("\n📊 Tasks by Priority:")
        for priority in ['Critical', 'High', 'Medium', 'Low', 'Not Set']:
            if priority in priorities:
                print(f"  {priority}: {priorities[priority]} tasks")

        print(f"\n⏱️  Total Estimated Hours: {total_hours}")

        # List task IDs for easy reference
        print(f"\n📝 Quick Reference - All P01 Task IDs:")
        print("─" * 40)
        for task in sorted(tasks, key=lambda x: x['fields'].get('task_id', '')):
            task_id = task['fields'].get('task_id', '')
            name = task['fields'].get('name', '')
            if len(name) > 50:
                name = name[:47] + "..."
            print(f"  {task_id}: {name}")
    else:
        print("No tasks found for Phase P01")

if __name__ == "__main__":
    main()