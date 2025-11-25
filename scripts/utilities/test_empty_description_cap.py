#!/usr/bin/env python3
"""
Test if empty descriptions are correctly capped at 55 points.
This verifies the Tasks.record_audit prompt is working correctly.
"""

import json
from pyairtable import Api
from datetime import datetime

def test_empty_description_scoring():
    """Check if tasks with empty descriptions score ≤55."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    tasks_table = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Tasks')

    print("=" * 70)
    print("EMPTY DESCRIPTION CAP TEST")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Get all tasks
    all_tasks = tasks_table.all()

    # Find tasks with empty or very short descriptions
    empty_desc_tasks = []
    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        description = fields.get('description', '')

        # Check if description is effectively empty
        if len(str(description).strip()) < 20:
            record_score = fields.get('record_score', 0)
            record_audit = fields.get('record_audit', {})
            audit_text = record_audit.get('value', '') if isinstance(record_audit, dict) else str(record_audit)

            empty_desc_tasks.append({
                'task_id': task_id,
                'desc_length': len(str(description).strip()),
                'score': record_score,
                'audit_starts_with_score': audit_text.startswith('Score:') if audit_text else False
            })

    # Report findings
    print(f"Total tasks checked: {len(all_tasks)}")
    print(f"Tasks with empty descriptions (<20 chars): {len(empty_desc_tasks)}")
    print()

    if empty_desc_tasks:
        print("TASKS WITH EMPTY DESCRIPTIONS:")
        print("-" * 70)
        print(f"{'Task ID':<20} {'Desc Len':<10} {'Score':<10} {'Status':<30}")
        print("-" * 70)

        failures = []
        for task in empty_desc_tasks:
            status = "✓ PASS" if task['score'] <= 55 else "✗ FAIL (Should be ≤55)"
            if task['score'] > 55:
                failures.append(task)

            print(f"{task['task_id']:<20} {task['desc_length']:<10} {task['score']:<10} {status:<30}")

        print()
        print("=" * 70)
        print("TEST RESULTS:")
        print("=" * 70)

        if failures:
            print(f"❌ FAILED: {len(failures)} tasks with empty descriptions scored >55")
            print()
            print("FAILED TASKS:")
            for fail in failures:
                print(f"  - {fail['task_id']}: Score {fail['score']} (should be ≤55)")
            print()
            print("ACTION REQUIRED:")
            print("1. Deploy FOOLPROOF_tasks_prompt.md to Tasks.record_audit")
            print("2. Wait 10-30 minutes for AI rescoring")
            print("3. Run this test again")
        else:
            print(f"✅ SUCCESS: All {len(empty_desc_tasks)} tasks with empty descriptions scored ≤55")
            print("The prompt is working correctly!")
    else:
        print("ℹ️ No tasks found with empty descriptions (<20 chars)")
        print("This could mean:")
        print("1. All tasks have proper descriptions (good!)")
        print("2. Empty descriptions were already remediated")

        # Special check for MP03.P07.S04.T01
        test_task = [t for t in all_tasks if t['fields'].get('task_id') == 'MP03.P07.S04.T01']
        if test_task:
            fields = test_task[0]['fields']
            print()
            print(f"Special check - MP03.P07.S04.T01:")
            print(f"  Description length: {len(str(fields.get('description', '')).strip())}")
            print(f"  Score: {fields.get('record_score', 0)}")

    print()
    print("=" * 70)

if __name__ == "__main__":
    test_empty_description_scoring()