#!/usr/bin/env python3
"""
Reconcile all stage_link data with task_id to confirm proper attachment.
Validates that each Task's stage_link points to the correct Stage based on ID patterns.
"""

import json
from pyairtable import Api

def reconcile_stage_links():
    """Reconcile and validate all Task stage_link attachments."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("STAGE_LINK RECONCILIATION REPORT")
    print("=" * 70)

    # Get all Stages and build mappings
    stages_table = api.table(base_id, 'Stages')
    all_stages = stages_table.all()

    # Build mappings: record_id -> stage_id and stage_id -> record_id
    stage_record_to_id = {}
    stage_id_to_record = {}

    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_record_to_id[stage['id']] = stage_id
            stage_id_to_record[stage_id] = stage['id']

    print(f"\n📊 Stages Summary:")
    print(f"  Total Stages: {len(all_stages)}")
    print(f"  Stages with IDs: {len(stage_id_to_record)}")

    # Get all Tasks
    tasks_table = api.table(base_id, 'Tasks')
    all_tasks = tasks_table.all()

    print(f"\n📊 Tasks Summary:")
    print(f"  Total Tasks: {len(all_tasks)}")

    # Analyze Task-Stage relationships
    correct_links = []
    incorrect_links = []
    missing_links = []
    orphaned_tasks = []

    print("\n📋 Analyzing Task-Stage Relationships...")
    print("-" * 50)

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        stage_links = fields.get('stage_link', [])

        # Extract expected stage_id from task_id
        expected_stage_id = None
        if '.' in task_id and 'S' in task_id:
            parts = task_id.split('.')
            stage_parts = []
            for part in parts:
                stage_parts.append(part)
                if part.startswith('S'):
                    break
            if stage_parts:
                expected_stage_id = '.'.join(stage_parts)

        # Check if stage_link exists
        if not stage_links:
            missing_links.append({
                'task_id': task_id,
                'expected_stage': expected_stage_id
            })
        else:
            # Validate the link
            linked_stage_record = stage_links[0]  # Get first link
            linked_stage_id = stage_record_to_id.get(linked_stage_record, 'Unknown')

            if expected_stage_id:
                if linked_stage_id == expected_stage_id:
                    correct_links.append({
                        'task_id': task_id,
                        'stage_id': linked_stage_id,
                        'status': '✓ Correct'
                    })
                else:
                    incorrect_links.append({
                        'task_id': task_id,
                        'expected': expected_stage_id,
                        'actual': linked_stage_id,
                        'status': '✗ Mismatch'
                    })
            else:
                # Can't determine expected stage
                orphaned_tasks.append({
                    'task_id': task_id,
                    'linked_to': linked_stage_id,
                    'status': '? Cannot validate'
                })

    # Print detailed results
    print("\n✅ CORRECT LINKS:")
    print(f"  Total: {len(correct_links)}")
    if len(correct_links) <= 10:
        for item in correct_links:
            print(f"    {item['task_id']} → {item['stage_id']}")
    else:
        for item in correct_links[:5]:
            print(f"    {item['task_id']} → {item['stage_id']}")
        print(f"    ... and {len(correct_links) - 5} more correct links")

    if incorrect_links:
        print("\n❌ INCORRECT LINKS:")
        print(f"  Total: {len(incorrect_links)}")
        for item in incorrect_links[:10]:
            print(f"    {item['task_id']}: Expected {item['expected']}, Got {item['actual']}")
        if len(incorrect_links) > 10:
            print(f"    ... and {len(incorrect_links) - 10} more incorrect links")

    if missing_links:
        print("\n⚠️ MISSING LINKS:")
        print(f"  Total: {len(missing_links)}")
        for item in missing_links[:10]:
            print(f"    {item['task_id']} → No stage linked (expected {item['expected_stage']})")
        if len(missing_links) > 10:
            print(f"    ... and {len(missing_links) - 10} more missing links")

    if orphaned_tasks:
        print("\n❓ UNVALIDATABLE TASKS:")
        print(f"  Total: {len(orphaned_tasks)}")
        for item in orphaned_tasks[:5]:
            print(f"    {item['task_id']} → {item['linked_to']}")
        if len(orphaned_tasks) > 5:
            print(f"    ... and {len(orphaned_tasks) - 5} more")

    # Summary statistics
    print("\n" + "=" * 70)
    print("RECONCILIATION SUMMARY")
    print("=" * 70)
    print(f"Total Tasks analyzed: {len(all_tasks)}")
    print(f"✅ Correctly linked: {len(correct_links)} ({100*len(correct_links)/len(all_tasks):.1f}%)")
    print(f"❌ Incorrectly linked: {len(incorrect_links)} ({100*len(incorrect_links)/len(all_tasks):.1f}%)")
    print(f"⚠️ Missing links: {len(missing_links)} ({100*len(missing_links)/len(all_tasks):.1f}%)")
    print(f"❓ Cannot validate: {len(orphaned_tasks)} ({100*len(orphaned_tasks)/len(all_tasks):.1f}%)")

    # Provide recommendations
    if len(incorrect_links) > 0 or len(missing_links) > 0:
        print("\n📌 RECOMMENDATIONS:")
        if incorrect_links:
            print("  - Fix incorrect stage_link mappings")
        if missing_links:
            print("  - Add missing stage_link fields")
        print("  - Consider running fix_missing_links.py again")
    else:
        print("\n✨ VALIDATION RESULT: All stage_link fields are properly attached!")

    # Check for stages not referenced by any task
    print("\n📊 REVERSE CHECK - Stages without Tasks:")
    all_linked_stages = set()
    for task in all_tasks:
        stage_links = task['fields'].get('stage_link', [])
        for link in stage_links:
            all_linked_stages.add(link)

    unlinked_stages = []
    for stage in all_stages:
        if stage['id'] not in all_linked_stages:
            stage_id = stage['fields'].get('stage_id', 'Unknown')
            unlinked_stages.append(stage_id)

    if unlinked_stages:
        print(f"  Found {len(unlinked_stages)} stages with no tasks:")
        for stage_id in unlinked_stages[:10]:
            print(f"    - {stage_id}")
        if len(unlinked_stages) > 10:
            print(f"    ... and {len(unlinked_stages) - 10} more")
    else:
        print("  ✓ All stages have at least one task linked")

    return len(correct_links) == len(all_tasks) and len(incorrect_links) == 0

if __name__ == "__main__":
    all_valid = reconcile_stage_links()
    if all_valid:
        print("\n🎉 SUCCESS: All Task-Stage relationships are valid!")
    else:
        print("\n⚠️ Some Task-Stage relationships need attention.")
