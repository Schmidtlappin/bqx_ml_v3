#!/usr/bin/env python3
"""
Complete all missing stage_link fields in Tasks table.
Maps task_id to stage_id and creates proper record links.
"""

import json
import time
from pyairtable import Api

def complete_stage_links():
    """Complete all missing stage_link fields in Tasks table."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("COMPLETING STAGE_LINK FIELDS IN TASKS TABLE")
    print("=" * 70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get all records from Stages table to build mapping
    print("\n📊 Building Stage mappings...")
    stages_table = api.table(base_id, 'Stages')
    all_stages = stages_table.all()

    # Create stage_id -> record_id mapping
    stage_map = {}
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_map[stage_id] = stage['id']

    print(f"  Found {len(stage_map)} stages")

    # Get all Tasks records
    print("\n📋 Checking Tasks table for missing stage_link fields...")
    tasks_table = api.table(base_id, 'Tasks')
    all_tasks = tasks_table.all()

    missing_links = []
    fixed_count = 0

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        current_stage_link = fields.get('stage_link', [])

        # Check if stage_link is empty
        if not current_stage_link:
            # Extract stage_id from task_id (e.g., MP03.P01.S07.T01 -> MP03.P01.S07)
            if '.' in task_id and 'S' in task_id:
                parts = task_id.split('.')
                # Find the stage part (everything up to and including S##)
                stage_parts = []
                for part in parts:
                    stage_parts.append(part)
                    if part.startswith('S'):
                        break

                if stage_parts:
                    stage_id = '.'.join(stage_parts)

                    # Check if we have this stage in our mapping
                    if stage_id in stage_map:
                        try:
                            # Update with the stage record link
                            updates = {'stage_link': [stage_map[stage_id]]}
                            tasks_table.update(task['id'], updates)
                            fixed_count += 1
                            print(f"  ✓ {task_id}: Linked to stage {stage_id}")
                        except Exception as e:
                            print(f"  ✗ {task_id}: Failed to link - {e}")
                    else:
                        missing_links.append((task_id, stage_id))
                        print(f"  ⚠️ {task_id}: Stage {stage_id} not found in mapping")
                else:
                    print(f"  ⚠️ {task_id}: Could not extract stage from task_id")

    print("\n" + "=" * 70)
    print("STAGE LINK COMPLETION SUMMARY")
    print("=" * 70)
    print(f"✅ Total Tasks processed: {len(all_tasks)}")
    print(f"✅ Stage links completed: {fixed_count}")

    if missing_links:
        print(f"\n⚠️ Tasks with unmapped stages: {len(missing_links)}")
        for task_id, stage_id in missing_links[:10]:
            print(f"  - {task_id} -> {stage_id} (stage not found)")
        if len(missing_links) > 10:
            print(f"  ... and {len(missing_links) - 10} more")

    print("\n✨ Stage link completion finished!")

    return fixed_count

if __name__ == "__main__":
    complete_stage_links()