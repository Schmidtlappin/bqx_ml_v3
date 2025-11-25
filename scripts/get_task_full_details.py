#!/usr/bin/env python3
"""
Get Full Task Details

Fetch all fields for task MP03.P07.S04.T01 to understand complete state.
"""

import json
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

def main():
    print("="*70)
    print("FULL TASK DETAILS: MP03.P07.S04.T01")
    print("="*70)

    # Fetch task
    formula = "{task_id}='MP03.P07.S04.T01'"
    records = tasks_table.all(formula=formula)

    if not records:
        print("\n❌ Task not found!")
        return

    task = records[0]

    print(f"\nRecord ID: {task['id']}")
    print(f"Created Time: {task.get('createdTime', 'N/A')}")

    print("\n" + "-"*70)
    print("ALL FIELDS:")
    print("-"*70)

    fields = task['fields']

    for field_name in sorted(fields.keys()):
        value = fields[field_name]

        print(f"\n{field_name}:")
        print(f"  Type: {type(value).__name__}")

        if isinstance(value, str):
            print(f"  Length: {len(value)} chars")
            if len(value) < 200:
                print(f"  Value: {repr(value)}")
            else:
                print(f"  Value (first 200): {repr(value[:200])}")
                print(f"  Value (last 100): {repr(value[-100:])}")
        elif isinstance(value, (int, float)):
            print(f"  Value: {value}")
        elif isinstance(value, list):
            print(f"  Length: {len(value)} items")
            print(f"  Value: {value}")
        elif isinstance(value, dict):
            print(f"  Keys: {list(value.keys())}")
            print(f"  Value: {json.dumps(value, indent=4)}")
        else:
            print(f"  Value: {value}")

    # Check notes field specifically
    print("\n" + "="*70)
    print("NOTES FIELD DETAILED ANALYSIS:")
    print("="*70)

    notes = fields.get('notes', '')
    if notes:
        print(f"\nLength: {len(notes)} characters")
        print(f"\nFull Content:")
        print("-"*70)
        print(notes)
        print("-"*70)
    else:
        print("\nNo notes available")

    # Check description
    print("\n" + "="*70)
    print("DESCRIPTION FIELD DETAILED ANALYSIS:")
    print("="*70)

    description = fields.get('description', '')
    if description:
        print(f"\nLength: {len(description)} characters")
        print(f"Content: {repr(description)}")

        if len(description) > 1:
            print(f"\nFull Content:")
            print("-"*70)
            print(description)
            print("-"*70)
        else:
            print("\n⚠️  Description is essentially empty (only whitespace)")
    else:
        print("\nNo description available")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
