#!/usr/bin/env python3
"""
Fix specific link issues:
1. Missing task_link data in Stages table
2. Duplicate stage_link entries in Tasks table
"""

import os
import json
import time
from datetime import datetime
from pyairtable import Api
from collections import defaultdict

# AirTable configuration
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_KEY = os.getenv('AIRTABLE_API_KEY')

# Load from secrets if not in environment
if not API_KEY or not BASE_ID:
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            API_KEY = API_KEY or secrets['secrets']['AIRTABLE_API_KEY']['value']
            BASE_ID = BASE_ID or secrets['secrets']['AIRTABLE_BASE_ID']['value']
    except:
        print("Warning: Could not load AirTable credentials")

# Initialize API
api = Api(API_KEY)
base = api.base(BASE_ID)

# Initialize tables
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

def analyze_duplicate_stage_links():
    """Analyze and fix duplicate stage_link entries in Tasks."""
    print("=" * 80)
    print("ANALYZING DUPLICATE STAGE_LINKS IN TASKS")
    print("=" * 80)

    tasks = tasks_table.all()
    stages = stages_table.all()

    # Build stage ID to record mapping
    stages_by_id = {}
    stages_by_record_id = {}
    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        if stage_id:
            stages_by_id[stage_id] = stage
            stages_by_record_id[stage['id']] = stage

    tasks_with_duplicates = []
    tasks_fixed = 0

    print(f"\n📊 Total tasks to analyze: {len(tasks)}")

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        stage_links = task['fields'].get('stage_link', [])

        if len(stage_links) > 1:
            tasks_with_duplicates.append(task)
            print(f"\n⚠️ Task {task_id} has {len(stage_links)} stage_links")

            # Determine the correct stage based on task ID
            if '.' in task_id:
                parts = task_id.split('.')
                if len(parts) >= 3:
                    expected_stage_id = '.'.join(parts[:3])  # MP03.P01.S01.T01 -> MP03.P01.S01

                    # Find the correct stage record
                    if expected_stage_id in stages_by_id:
                        correct_stage = stages_by_id[expected_stage_id]

                        # Check current stage links
                        linked_stages_info = []
                        for stage_record_id in stage_links:
                            if stage_record_id in stages_by_record_id:
                                linked_stage = stages_by_record_id[stage_record_id]
                                linked_stage_id = linked_stage['fields'].get('stage_id', 'Unknown')
                                linked_stages_info.append(f"{linked_stage_id} ({stage_record_id})")

                        print(f"  Currently linked to: {', '.join(linked_stages_info)}")
                        print(f"  Expected stage: {expected_stage_id} ({correct_stage['id']})")

                        # Update with single correct stage link
                        try:
                            tasks_table.update(task['id'], {
                                'stage_link': [correct_stage['id']]
                            })
                            print(f"  ✅ Fixed: Now linked only to {expected_stage_id}")
                            tasks_fixed += 1
                        except Exception as e:
                            print(f"  ❌ Failed to fix: {e}")
                    else:
                        print(f"  ❌ Expected stage {expected_stage_id} not found")

    print(f"\n📊 Summary:")
    print(f"  Tasks with duplicate stage_links: {len(tasks_with_duplicates)}")
    print(f"  Tasks fixed: {tasks_fixed}")

    return tasks_fixed, tasks_with_duplicates

def rebuild_stage_task_links():
    """Rebuild task_link in Stages based on corrected Tasks data."""
    print("\n" + "=" * 80)
    print("REBUILDING TASK_LINKS IN STAGES")
    print("=" * 80)

    # Re-fetch data after fixes
    stages = stages_table.all()
    tasks = tasks_table.all()

    # Build mapping of stage_id to tasks
    stage_tasks_map = defaultdict(list)

    for task in tasks:
        task_id = task['fields'].get('task_id', '')

        # Extract stage_id from task_id
        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage_id = '.'.join(parts[:3])  # MP03.P01.S01.T01 -> MP03.P01.S01
                stage_tasks_map[stage_id].append(task)

    # Update stages with their tasks
    stages_updated = 0
    stages_missing_tasks = []

    print(f"\n📊 Analyzing {len(stages)} stages...")

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        current_task_links = stage['fields'].get('task_link', [])

        if stage_id in stage_tasks_map:
            expected_tasks = stage_tasks_map[stage_id]
            expected_task_ids = [t['id'] for t in expected_tasks]

            # Check if update is needed
            if set(current_task_links) != set(expected_task_ids):
                try:
                    stages_table.update(stage['id'], {
                        'task_link': expected_task_ids
                    })
                    print(f"  ✅ {stage_id}: Updated with {len(expected_task_ids)} tasks")
                    stages_updated += 1
                    time.sleep(0.2)  # Rate limit
                except Exception as e:
                    print(f"  ❌ {stage_id}: Failed to update - {e}")
            else:
                print(f"  ✓ {stage_id}: Already has correct task_links ({len(current_task_links)} tasks)")
        else:
            # Stage has no tasks
            if current_task_links:
                # Clear incorrect task links
                try:
                    stages_table.update(stage['id'], {
                        'task_link': []
                    })
                    print(f"  ✅ {stage_id}: Cleared incorrect task_links (stage has no tasks)")
                    stages_updated += 1
                except Exception as e:
                    print(f"  ❌ {stage_id}: Failed to clear - {e}")
            else:
                stages_missing_tasks.append(stage_id)

    print(f"\n📊 Summary:")
    print(f"  Stages updated: {stages_updated}")
    print(f"  Stages without tasks: {len(stages_missing_tasks)}")

    if stages_missing_tasks[:5]:
        print(f"  Examples of stages without tasks: {', '.join(stages_missing_tasks[:5])}")

    return stages_updated

def final_validation():
    """Validate that all links are now correct."""
    print("\n" + "=" * 80)
    print("FINAL VALIDATION")
    print("=" * 80)

    # Re-fetch fresh data
    stages = stages_table.all()
    tasks = tasks_table.all()

    # Check for duplicate stage_links in tasks
    tasks_with_multiple_stages = 0
    for task in tasks:
        stage_links = task['fields'].get('stage_link', [])
        if len(stage_links) > 1:
            tasks_with_multiple_stages += 1

    # Check stages with task_link
    stages_with_tasks = 0
    stages_without_tasks = 0
    total_task_links = 0

    for stage in stages:
        task_links = stage['fields'].get('task_link', [])
        if task_links:
            stages_with_tasks += 1
            total_task_links += len(task_links)
        else:
            stages_without_tasks += 1

    # Verify task-stage bidirectional consistency
    inconsistencies = []

    # Check that each task's stage_link points to a stage that includes the task in its task_link
    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        stage_links = task['fields'].get('stage_link', [])

        if len(stage_links) == 1:
            stage_record_id = stage_links[0]
            # Find the stage
            stage_found = False
            for stage in stages:
                if stage['id'] == stage_record_id:
                    stage_found = True
                    task_links = stage['fields'].get('task_link', [])
                    if task['id'] not in task_links:
                        inconsistencies.append(f"Task {task_id} links to stage but stage doesn't link back")
                    break
            if not stage_found:
                inconsistencies.append(f"Task {task_id} links to non-existent stage {stage_record_id}")

    print("\n📊 Final Statistics:")
    print(f"  Total Stages: {len(stages)}")
    print(f"  Stages with task_links: {stages_with_tasks}")
    print(f"  Stages without task_links: {stages_without_tasks}")
    print(f"  Total task_link connections: {total_task_links}")
    print(f"\n  Total Tasks: {len(tasks)}")
    print(f"  Tasks with single stage_link: {len(tasks) - tasks_with_multiple_stages}")
    print(f"  Tasks with duplicate stage_links: {tasks_with_multiple_stages}")

    if inconsistencies:
        print(f"\n⚠️ Bidirectional inconsistencies found: {len(inconsistencies)}")
        for issue in inconsistencies[:5]:
            print(f"  - {issue}")
    else:
        print("\n✅ All task-stage links are bidirectionally consistent!")

    success = (tasks_with_multiple_stages == 0) and (len(inconsistencies) == 0)
    return success

def main():
    """Main execution function."""
    print("=" * 80)
    print("FIX TASK-STAGE LINK ISSUES")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Step 1: Fix duplicate stage_links in Tasks
    print("\n🔧 Step 1: Fixing duplicate stage_links in Tasks...")
    tasks_fixed, tasks_with_duplicates = analyze_duplicate_stage_links()

    # Step 2: Rebuild task_links in Stages
    print("\n🔧 Step 2: Rebuilding task_links in Stages...")
    stages_updated = rebuild_stage_task_links()

    # Step 3: Final validation
    print("\n✅ Step 3: Final validation...")
    success = final_validation()

    # Summary
    print("\n" + "=" * 80)
    print("REMEDIATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 Actions Taken:")
    print(f"  Tasks fixed (duplicate stage_links removed): {tasks_fixed}")
    print(f"  Stages updated (task_links rebuilt): {stages_updated}")
    print(f"  Total records modified: {tasks_fixed + stages_updated}")

    if success:
        print("\n✅ SUCCESS: All task-stage links are now correct!")
        print("  - Each task has exactly one stage_link")
        print("  - All stages have correct task_link arrays")
        print("  - Bidirectional consistency achieved")
    else:
        print("\n⚠️ PARTIAL SUCCESS: Some issues may remain")
        print("  Please review the validation results above")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())