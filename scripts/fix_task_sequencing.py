#!/usr/bin/env python3
"""
Fix task sequencing issues in AirTable.
Resolves duplicate task IDs and numbering gaps.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime
from collections import defaultdict

# Get credentials from GCP Secrets Manager or GitHub secrets
def get_github_secret():
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
            base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']
            return api_key, base_id
    except:
        return None, None

AIRTABLE_API_KEY, BASE_ID = get_github_secret()

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials")

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def identify_sequencing_issues():
    """Identify all sequencing issues in tasks."""

    print("🔍 IDENTIFYING TASK SEQUENCING ISSUES")
    print("=" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()

    # Group tasks by stage
    stage_tasks = defaultdict(list)
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        if task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage = '.'.join(parts[:3])  # MP03.P05.S03
                stage_tasks[stage].append({
                    'record_id': task['id'],
                    'task_id': task_id,
                    'name': task['fields'].get('name', ''),
                    'task_num': parts[3] if len(parts) > 3 else None
                })

    # Identify issues
    issues = {
        'duplicates': [],
        'gaps': [],
        'high_numbers': []
    }

    for stage, tasks in stage_tasks.items():
        # Sort by task ID
        tasks.sort(key=lambda x: x['task_id'])

        # Check for duplicates
        task_ids_seen = {}
        for task in tasks:
            if task['task_id'] in task_ids_seen:
                issues['duplicates'].append({
                    'stage': stage,
                    'task_id': task['task_id'],
                    'record1': task_ids_seen[task['task_id']],
                    'record2': task['record_id'],
                    'name1': task_ids_seen[task['task_id']]['name'],
                    'name2': task['name']
                })
            else:
                task_ids_seen[task['task_id']] = {
                    'record_id': task['record_id'],
                    'name': task['name']
                }

        # Check for gaps and high numbers
        task_numbers = []
        for task in tasks:
            if task['task_num'] and task['task_num'].startswith('T'):
                try:
                    num = int(task['task_num'][1:])
                    task_numbers.append(num)
                except:
                    pass

        if task_numbers:
            task_numbers.sort()

            # Check for gaps
            expected = list(range(1, len(set(task_numbers)) + 1))
            if task_numbers != expected:
                issues['gaps'].append({
                    'stage': stage,
                    'actual': task_numbers,
                    'expected': expected,
                    'missing': [n for n in expected if n not in task_numbers]
                })

            # Check for unusually high numbers
            for num in task_numbers:
                if num > 50:  # Tasks shouldn't normally go above 50
                    issues['high_numbers'].append({
                        'stage': stage,
                        'task_num': num,
                        'task_id': f"{stage}.T{num:02d}"
                    })

    return issues, stage_tasks

def fix_duplicate_task_ids(issues, stage_tasks):
    """Fix duplicate task IDs by renumbering."""

    print("\n🔧 FIXING DUPLICATE TASK IDS")
    print("-" * 60)

    fixed_count = 0

    for duplicate in issues['duplicates']:
        stage = duplicate['stage']

        # Get all tasks for this stage
        tasks = stage_tasks[stage]

        # Sort by name to ensure consistent ordering
        tasks.sort(key=lambda x: (x['task_id'], x['name']))

        # Find the duplicate tasks
        dup_tasks = [t for t in tasks if t['task_id'] == duplicate['task_id']]

        # Renumber duplicates
        for i, task in enumerate(dup_tasks[1:], 1):  # Skip the first one
            # Find next available number
            existing_nums = []
            for t in tasks:
                if t['task_num'] and t['task_num'].startswith('T'):
                    try:
                        existing_nums.append(int(t['task_num'][1:]))
                    except:
                        pass

            # Find next available number
            new_num = 1
            while new_num in existing_nums:
                new_num += 1

            new_task_id = f"{stage}.T{new_num:02d}"

            try:
                # Update the task ID
                tasks_table.update(task['record_id'], {
                    'task_id': new_task_id
                })

                print(f"  ✅ Fixed duplicate: {duplicate['task_id']} → {new_task_id}")
                print(f"     Task: {task['name'][:50]}")
                fixed_count += 1

                # Update our local tracking
                task['task_id'] = new_task_id
                task['task_num'] = f"T{new_num:02d}"
                existing_nums.append(new_num)

            except Exception as e:
                print(f"  ❌ Failed to fix {duplicate['task_id']}: {e}")

    return fixed_count

def fix_high_task_numbers(issues, stage_tasks):
    """Fix unusually high task numbers by renumbering sequentially."""

    print("\n🔧 FIXING HIGH TASK NUMBERS")
    print("-" * 60)

    fixed_count = 0

    # Group high numbers by stage
    stages_to_fix = set()
    for high_num in issues['high_numbers']:
        stages_to_fix.add(high_num['stage'])

    for stage in stages_to_fix:
        tasks = stage_tasks[stage]

        # Sort tasks by current number
        numbered_tasks = []
        for task in tasks:
            if task['task_num'] and task['task_num'].startswith('T'):
                try:
                    num = int(task['task_num'][1:])
                    numbered_tasks.append((num, task))
                except:
                    pass

        numbered_tasks.sort(key=lambda x: x[0])

        # Renumber sequentially
        for new_num, (old_num, task) in enumerate(numbered_tasks, 1):
            if old_num != new_num:
                new_task_id = f"{stage}.T{new_num:02d}"

                try:
                    tasks_table.update(task['record_id'], {
                        'task_id': new_task_id
                    })

                    print(f"  ✅ Renumbered: {task['task_id']} → {new_task_id}")
                    fixed_count += 1

                except Exception as e:
                    print(f"  ❌ Failed to renumber {task['task_id']}: {e}")

    return fixed_count

def fill_sequencing_gaps(issues, stage_tasks):
    """Ensure sequential task numbering without gaps."""

    print("\n🔧 FILLING SEQUENCING GAPS")
    print("-" * 60)

    fixed_count = 0

    for gap_issue in issues['gaps']:
        stage = gap_issue['stage']
        tasks = stage_tasks[stage]

        # Get all tasks with numbers
        numbered_tasks = []
        for task in tasks:
            if task['task_num'] and task['task_num'].startswith('T'):
                try:
                    num = int(task['task_num'][1:])
                    numbered_tasks.append((num, task))
                except:
                    pass

        # Sort by number
        numbered_tasks.sort(key=lambda x: x[0])

        # Renumber to be sequential
        updates_made = False
        for new_num, (old_num, task) in enumerate(numbered_tasks, 1):
            if old_num != new_num:
                new_task_id = f"{stage}.T{new_num:02d}"

                try:
                    tasks_table.update(task['record_id'], {
                        'task_id': new_task_id
                    })

                    print(f"  ✅ Resequenced: {task['task_id']} → {new_task_id}")
                    fixed_count += 1
                    updates_made = True

                except Exception as e:
                    print(f"  ❌ Failed to resequence {task['task_id']}: {e}")

        if updates_made:
            print(f"  📋 Stage {stage}: Renumbered {len(numbered_tasks)} tasks sequentially")

    return fixed_count

def verify_sequencing():
    """Verify all sequencing issues are resolved."""

    print("\n🔍 VERIFYING SEQUENCING")
    print("-" * 60)

    # Re-check for issues
    issues, stage_tasks = identify_sequencing_issues()

    remaining_issues = {
        'duplicates': len(issues['duplicates']),
        'gaps': len(issues['gaps']),
        'high_numbers': len(issues['high_numbers'])
    }

    total_remaining = sum(remaining_issues.values())

    if total_remaining == 0:
        print("  ✅ All sequencing issues resolved!")
    else:
        print(f"  ⚠️  {total_remaining} issues remain:")
        for issue_type, count in remaining_issues.items():
            if count > 0:
                print(f"    • {issue_type}: {count}")

    return total_remaining == 0

def main():
    """Main execution function."""

    print("🚀 STARTING TASK SEQUENCING FIX")
    print("=" * 80)

    try:
        # Identify issues
        issues, stage_tasks = identify_sequencing_issues()

        print(f"\n📊 ISSUES FOUND:")
        print(f"  • Duplicate task IDs: {len(issues['duplicates'])}")
        print(f"  • Stages with gaps: {len(issues['gaps'])}")
        print(f"  • High task numbers: {len(issues['high_numbers'])}")

        if not any([issues['duplicates'], issues['gaps'], issues['high_numbers']]):
            print("\n✅ No sequencing issues found!")
            return True

        # Fix issues
        total_fixed = 0

        # Fix duplicates first
        if issues['duplicates']:
            fixed = fix_duplicate_task_ids(issues, stage_tasks)
            total_fixed += fixed

        # Re-identify after fixing duplicates
        issues, stage_tasks = identify_sequencing_issues()

        # Fix high numbers
        if issues['high_numbers']:
            fixed = fix_high_task_numbers(issues, stage_tasks)
            total_fixed += fixed

        # Re-identify after fixing high numbers
        issues, stage_tasks = identify_sequencing_issues()

        # Fill gaps
        if issues['gaps']:
            fixed = fill_sequencing_gaps(issues, stage_tasks)
            total_fixed += fixed

        # Verify
        success = verify_sequencing()

        # Summary
        print("\n" + "=" * 80)
        print("📊 SEQUENCING FIX SUMMARY")
        print("=" * 80)
        print(f"\nTotal fixes applied: {total_fixed}")

        if success:
            print("\n✅ SUCCESS: All task sequencing issues resolved!")
            print("  • No duplicate task IDs")
            print("  • No numbering gaps")
            print("  • All tasks numbered sequentially")
        else:
            print("\n⚠️  Some issues remain. May need manual intervention.")

        print(f"\nCompleted: {datetime.now().isoformat()}")

        return success

    except Exception as e:
        print(f"\n❌ Error during sequencing fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()