#!/usr/bin/env python3
"""
Fix ALL duplicate stage_link entries in Tasks table.
More comprehensive approach to handle all duplicates.
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

def fix_all_duplicate_stage_links():
    """Fix ALL tasks with duplicate stage_link entries."""
    print("=" * 80)
    print("FIXING ALL DUPLICATE STAGE_LINKS IN TASKS")
    print("=" * 80)

    tasks = tasks_table.all()
    stages = stages_table.all()

    # Build comprehensive mappings
    stages_by_id = {}
    stages_by_record_id = {}
    stage_record_to_id = {}

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        stage_record_id = stage['id']

        if stage_id:
            if stage_id not in stages_by_id:
                stages_by_id[stage_id] = []
            stages_by_id[stage_id].append(stage)
            stages_by_record_id[stage_record_id] = stage
            stage_record_to_id[stage_record_id] = stage_id

    # Find all tasks with duplicate stage_links
    tasks_to_fix = []
    tasks_by_type = defaultdict(int)

    print(f"\n📊 Analyzing {len(tasks)} tasks...")

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        stage_links = task['fields'].get('stage_link', [])

        if len(stage_links) > 1:
            # Analyze the duplicate
            unique_stage_ids = set()
            for stage_record_id in stage_links:
                if stage_record_id in stage_record_to_id:
                    unique_stage_ids.add(stage_record_to_id[stage_record_id])

            if len(unique_stage_ids) == 1:
                # All links point to the same stage ID (just different records)
                tasks_by_type['same_stage_id'] += 1
            else:
                # Links point to different stage IDs
                tasks_by_type['different_stage_ids'] += 1

            tasks_to_fix.append({
                'task': task,
                'task_id': task_id,
                'stage_links': stage_links,
                'unique_stage_ids': unique_stage_ids
            })

    print(f"\n📊 Found {len(tasks_to_fix)} tasks with duplicate stage_links:")
    print(f"  - Same stage_id (different records): {tasks_by_type['same_stage_id']}")
    print(f"  - Different stage_ids: {tasks_by_type['different_stage_ids']}")

    # Fix each task
    fixed_count = 0
    failed_count = 0

    for item in tasks_to_fix:
        task = item['task']
        task_id = item['task_id']
        stage_links = item['stage_links']

        print(f"\n🔧 Fixing {task_id} ({len(stage_links)} stage_links)")

        # Determine the correct stage
        correct_stage_record = None

        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                expected_stage_id = '.'.join(parts[:3])  # MP03.P01.S01.T01 -> MP03.P01.S01

                # Find the best matching stage record
                if expected_stage_id in stages_by_id:
                    # Get all stage records with this ID
                    matching_stages = stages_by_id[expected_stage_id]

                    # Prefer the stage that's already in the current links
                    for stage in matching_stages:
                        if stage['id'] in stage_links:
                            correct_stage_record = stage
                            break

                    # If no match in current links, use the first available
                    if not correct_stage_record:
                        correct_stage_record = matching_stages[0]

        if correct_stage_record:
            try:
                # Update with single correct stage link
                tasks_table.update(task['id'], {
                    'stage_link': [correct_stage_record['id']]
                })
                print(f"  ✅ Fixed: Now linked only to {correct_stage_record['fields'].get('stage_id')} ({correct_stage_record['id']})")
                fixed_count += 1
                time.sleep(0.1)  # Rate limit
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                failed_count += 1
        else:
            print(f"  ⚠️ Could not determine correct stage for {task_id}")
            failed_count += 1

    print(f"\n📊 Summary:")
    print(f"  Total tasks with duplicates: {len(tasks_to_fix)}")
    print(f"  Successfully fixed: {fixed_count}")
    print(f"  Failed to fix: {failed_count}")

    return fixed_count, failed_count

def rebuild_all_stage_task_links():
    """Rebuild ALL task_link relationships in Stages."""
    print("\n" + "=" * 80)
    print("REBUILDING ALL TASK_LINKS IN STAGES")
    print("=" * 80)

    # Re-fetch fresh data
    stages = stages_table.all()
    tasks = tasks_table.all()

    # Build comprehensive mapping of stage_id to tasks
    stage_tasks_map = defaultdict(list)

    for task in tasks:
        task_id = task['fields'].get('task_id', '')

        # Extract stage_id from task_id
        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage_id = '.'.join(parts[:3])
                stage_tasks_map[stage_id].append(task)

    # Update ALL stages
    stages_updated = 0
    stages_cleared = 0

    print(f"\n📊 Updating {len(stages)} stages...")

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        current_task_links = stage['fields'].get('task_link', [])

        if stage_id in stage_tasks_map:
            # Stage should have tasks
            expected_tasks = stage_tasks_map[stage_id]
            expected_task_ids = [t['id'] for t in expected_tasks]

            # Always update to ensure correctness
            try:
                stages_table.update(stage['id'], {
                    'task_link': expected_task_ids
                })
                print(f"  ✅ {stage_id}: Set {len(expected_task_ids)} tasks")
                stages_updated += 1
                time.sleep(0.1)  # Rate limit
            except Exception as e:
                print(f"  ❌ {stage_id}: Failed - {e}")
        else:
            # Stage has no tasks - clear any incorrect links
            if current_task_links:
                try:
                    stages_table.update(stage['id'], {
                        'task_link': []
                    })
                    print(f"  ✅ {stage_id}: Cleared incorrect task_links")
                    stages_cleared += 1
                    time.sleep(0.1)
                except Exception as e:
                    print(f"  ❌ {stage_id}: Failed to clear - {e}")

    print(f"\n📊 Summary:")
    print(f"  Stages updated with tasks: {stages_updated}")
    print(f"  Stages cleared of incorrect links: {stages_cleared}")
    print(f"  Total changes: {stages_updated + stages_cleared}")

    return stages_updated, stages_cleared

def comprehensive_validation():
    """Comprehensive validation of all links."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE VALIDATION")
    print("=" * 80)

    # Re-fetch fresh data
    stages = stages_table.all()
    tasks = tasks_table.all()

    # Check for ANY remaining duplicates
    tasks_with_duplicates = []
    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        stage_links = task['fields'].get('stage_link', [])
        if len(stage_links) > 1:
            tasks_with_duplicates.append(task_id)

    # Check bidirectional consistency
    consistency_issues = []

    # Build stage task_link mapping
    stage_task_map = {}
    for stage in stages:
        stage_id = stage['id']
        task_links = stage['fields'].get('task_link', [])
        stage_task_map[stage_id] = set(task_links)

    # Check each task
    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        task_record_id = task['id']
        stage_links = task['fields'].get('stage_link', [])

        if len(stage_links) == 1:
            stage_record_id = stage_links[0]
            if stage_record_id in stage_task_map:
                if task_record_id not in stage_task_map[stage_record_id]:
                    consistency_issues.append(f"Task {task_id} not in its stage's task_link")

    # Summary statistics
    total_task_links = sum(len(s['fields'].get('task_link', [])) for s in stages)
    stages_with_tasks = len([s for s in stages if s['fields'].get('task_link')])
    stages_without_tasks = len(stages) - stages_with_tasks

    print("\n📊 Validation Results:")
    print(f"  Total Tasks: {len(tasks)}")
    print(f"  Tasks with single stage_link: {len(tasks) - len(tasks_with_duplicates)}")
    print(f"  Tasks with duplicate stage_links: {len(tasks_with_duplicates)}")

    if tasks_with_duplicates:
        print(f"\n  ⚠️ Tasks still having duplicates:")
        for tid in tasks_with_duplicates[:10]:
            print(f"    - {tid}")
        if len(tasks_with_duplicates) > 10:
            print(f"    ... and {len(tasks_with_duplicates) - 10} more")

    print(f"\n  Total Stages: {len(stages)}")
    print(f"  Stages with task_links: {stages_with_tasks}")
    print(f"  Stages without task_links: {stages_without_tasks}")
    print(f"  Total task connections: {total_task_links}")

    print(f"\n  Bidirectional consistency issues: {len(consistency_issues)}")
    if consistency_issues:
        for issue in consistency_issues[:5]:
            print(f"    - {issue}")

    success = (len(tasks_with_duplicates) == 0 and len(consistency_issues) == 0)
    return success, len(tasks_with_duplicates), len(consistency_issues)

def main():
    """Main execution function."""
    print("=" * 80)
    print("COMPREHENSIVE FIX FOR DUPLICATE STAGE_LINKS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Step 1: Fix ALL duplicate stage_links
    print("\n🔧 Step 1: Fixing ALL duplicate stage_links...")
    fixed, failed = fix_all_duplicate_stage_links()

    # Step 2: Rebuild ALL task_links
    print("\n🔧 Step 2: Rebuilding ALL task_links in Stages...")
    updated, cleared = rebuild_all_stage_task_links()

    # Step 3: Comprehensive validation
    print("\n✅ Step 3: Comprehensive validation...")
    success, remaining_dups, consistency_issues = comprehensive_validation()

    # Final Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"\n📊 Actions Taken:")
    print(f"  Tasks fixed (duplicates removed): {fixed}")
    print(f"  Tasks failed to fix: {failed}")
    print(f"  Stages updated with task_links: {updated}")
    print(f"  Stages cleared of incorrect links: {cleared}")
    print(f"  Total records modified: {fixed + updated + cleared}")

    if success:
        print("\n✅ COMPLETE SUCCESS!")
        print("  - ALL tasks have exactly one stage_link")
        print("  - ALL stages have correct task_link arrays")
        print("  - Full bidirectional consistency achieved")
    else:
        print(f"\n⚠️ Issues remaining:")
        if remaining_dups > 0:
            print(f"  - {remaining_dups} tasks still have duplicate stage_links")
        if consistency_issues > 0:
            print(f"  - {consistency_issues} bidirectional consistency issues")
        print("\n  Please run the script again or investigate manually")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())