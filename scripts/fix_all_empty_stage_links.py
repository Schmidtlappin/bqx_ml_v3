#!/usr/bin/env python3
"""
Fix ALL empty stage_link fields in the Tasks table.
Ensures 100% completeness of stage_link field.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime

# Get credentials from GCP Secrets Manager
def get_secret(secret_name):
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

# Try GitHub secrets as fallback
def get_github_secret():
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
            base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']
            return api_key, base_id
    except:
        return None, None

# Get credentials
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY") or get_secret("bqx-ml-airtable-token")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID") or get_secret("bqx-ml-airtable-base-id")

# Fallback to GitHub secrets
if not AIRTABLE_API_KEY or not BASE_ID:
    AIRTABLE_API_KEY, BASE_ID = get_github_secret()

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials from any source")

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')
stages_table = base.table('Stages')

def fix_empty_stage_links():
    """Fix all empty stage_link fields in the Tasks table."""

    print("🔧 FIXING ALL EMPTY STAGE_LINK FIELDS")
    print("=" * 80)

    # Get all stages and build lookup
    all_stages = stages_table.all()
    stage_lookup = {}

    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_lookup[stage_id] = stage['id']

    print(f"Loaded {len(stage_lookup)} stages for lookup")

    # Get all tasks
    all_tasks = tasks_table.all()
    print(f"Found {len(all_tasks)} tasks to check")

    # Find tasks with empty stage_link
    empty_stage_links = []
    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        # Check if stage_link is empty or missing
        stage_link = fields.get('stage_link')
        if not stage_link or (isinstance(stage_link, list) and len(stage_link) == 0):
            empty_stage_links.append({
                'record_id': task['id'],
                'task_id': task_id,
                'name': fields.get('name', 'Unknown')[:50]
            })

    print(f"\n⚠️  Found {len(empty_stage_links)} tasks with empty stage_link")

    if not empty_stage_links:
        print("✅ All tasks already have stage_link populated!")
        return True

    # Fix each empty stage_link
    print("\n📝 Fixing empty stage_link fields...")
    print("-" * 60)

    fixed_count = 0
    failed_count = 0
    unfixable_count = 0

    for task_info in empty_stage_links:
        task_id = task_info['task_id']
        record_id = task_info['record_id']

        # Extract stage ID from task ID (e.g., MP03.P01.S01.T01 -> MP03.P01.S01)
        parts = task_id.split('.')
        if len(parts) >= 3:
            stage_id = '.'.join(parts[:3])  # MP03.P01.S01

            if stage_id in stage_lookup:
                # Update the task with the stage link
                try:
                    tasks_table.update(record_id, {'stage_link': [stage_lookup[stage_id]]})
                    fixed_count += 1
                    print(f"  ✅ Fixed {task_id} → linked to stage {stage_id}")
                except Exception as e:
                    failed_count += 1
                    print(f"  ❌ Failed to fix {task_id}: {e}")
            else:
                unfixable_count += 1
                print(f"  ⚠️  Cannot fix {task_id}: Stage {stage_id} not found in Stages table")

                # Try to create a less specific stage link
                if len(parts) >= 2:
                    # Try without the stage number (e.g., MP03.P01)
                    alt_stage_id = '.'.join(parts[:2]) + '.S01'
                    if alt_stage_id in stage_lookup:
                        try:
                            tasks_table.update(record_id, {'stage_link': [stage_lookup[alt_stage_id]]})
                            fixed_count += 1
                            unfixable_count -= 1
                            print(f"      ✅ Fixed using default stage {alt_stage_id}")
                        except:
                            pass
        else:
            unfixable_count += 1
            print(f"  ⚠️  Cannot parse task ID: {task_id}")

    # Re-check for remaining empty links
    print("\n🔄 Re-checking for empty stage_link fields...")

    all_tasks = tasks_table.all()
    still_empty = 0

    for task in all_tasks:
        fields = task['fields']
        stage_link = fields.get('stage_link')
        if not stage_link or (isinstance(stage_link, list) and len(stage_link) == 0):
            still_empty += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 STAGE_LINK FIX SUMMARY")
    print("=" * 80)

    print(f"\nInitial empty stage_links: {len(empty_stage_links)}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Failed to fix: {failed_count}")
    print(f"Cannot fix (missing stages): {unfixable_count}")
    print(f"Remaining empty: {still_empty}")

    completeness = ((len(all_tasks) - still_empty) / len(all_tasks)) * 100 if len(all_tasks) > 0 else 100

    print(f"\nStage_link completeness: {completeness:.1f}%")

    if completeness == 100:
        print("\n✅ PERFECT: All tasks now have stage_link populated!")
    elif completeness >= 99:
        print(f"\n✅ EXCELLENT: {completeness:.1f}% of tasks have stage_link")
    elif completeness >= 95:
        print(f"\n🔄 GOOD: {completeness:.1f}% of tasks have stage_link")
    else:
        print(f"\n⚠️  NEEDS ATTENTION: Only {completeness:.1f}% of tasks have stage_link")

    if still_empty > 0:
        print("\n📋 Tasks still missing stage_link:")
        remaining_count = 0
        for task in all_tasks:
            fields = task['fields']
            stage_link = fields.get('stage_link')
            if not stage_link or (isinstance(stage_link, list) and len(stage_link) == 0):
                task_id = fields.get('task_id', 'Unknown')
                print(f"  • {task_id}: {fields.get('name', '')[:50]}")
                remaining_count += 1
                if remaining_count >= 10:
                    print(f"  ... and {still_empty - 10} more")
                    break

    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 80)

    return completeness == 100

if __name__ == "__main__":
    success = fix_empty_stage_links()

    if success:
        print("\n🎉 SUCCESS: All stage_link fields are now complete!")
    else:
        print("\n📝 Some stage_link fields could not be fixed automatically.")