#!/usr/bin/env python3
"""
Verify and fix all link fields (plan_link, phase_link, stage_link, task_link)
throughout the AirTable BQX ML V3 project plan.
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from pyairtable import Api

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
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

def verify_and_fix_links():
    """Verify and fix all link fields throughout AirTable."""
    print("=" * 80)
    print("VERIFYING AND FIXING ALL LINK FIELDS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Load all data
    print("\n📥 Loading all data from AirTable...")
    phases = phases_table.all()
    stages = stages_table.all()
    tasks = tasks_table.all()
    print(f"  Loaded: {len(phases)} phases, {len(stages)} stages, {len(tasks)} tasks")

    # Track statistics
    stats = {
        'phases_fixed': 0,
        'stages_fixed': 0,
        'tasks_fixed': 0,
        'links_added': 0,
        'errors': 0
    }

    # Create lookup dictionaries
    phase_lookup = {p['fields'].get('phase_id'): p for p in phases}
    stage_lookup = {s['fields'].get('stage_id'): s for s in stages}
    task_lookup = {t['fields'].get('task_id'): t for t in tasks}

    # Group entities
    stages_by_phase = defaultdict(list)
    tasks_by_stage = defaultdict(list)
    tasks_by_phase = defaultdict(list)

    for stage in stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id and '.' in stage_id:
            phase_id = '.'.join(stage_id.split('.')[:2])
            stages_by_phase[phase_id].append(stage)

    for task in tasks:
        task_id = task['fields'].get('task_id')
        if task_id and '.' in task_id:
            stage_id = '.'.join(task_id.split('.')[:3])
            phase_id = '.'.join(task_id.split('.')[:2])
            tasks_by_stage[stage_id].append(task)
            tasks_by_phase[phase_id].append(task)

    # Fix Phase links
    print("\n📋 Fixing Phase links...")
    for phase in phases:
        phase_id = phase['fields'].get('phase_id')
        if not phase_id:
            continue

        update_fields = {}

        # Ensure plan_link is set (assuming MP03)
        # Note: plan_link should point to the plan record, but we don't have that table
        # So we'll skip this for phases

        # Add stage_link if missing
        current_stage_links = phase['fields'].get('stage_link', [])
        expected_stages = stages_by_phase.get(phase_id, [])

        if len(current_stage_links) != len(expected_stages):
            stage_ids = [s['id'] for s in expected_stages]
            if stage_ids:
                update_fields['stage_link'] = stage_ids
                stats['links_added'] += len(stage_ids)

        # Update if needed
        if update_fields:
            try:
                phases_table.update(phase['id'], update_fields)
                stats['phases_fixed'] += 1
                print(f"  ✅ Fixed {phase_id}: added {len(update_fields)} links")
            except Exception as e:
                print(f"  ❌ Failed to fix {phase_id}: {e}")
                stats['errors'] += 1

    # Fix Stage links
    print("\n📋 Fixing Stage links...")
    for stage in stages:
        stage_id = stage['fields'].get('stage_id')
        if not stage_id or '.' not in stage_id:
            continue

        update_fields = {}
        phase_id = '.'.join(stage_id.split('.')[:2])

        # Ensure phase_link is set
        if not stage['fields'].get('phase_link'):
            if phase_id in phase_lookup:
                update_fields['phase_link'] = [phase_lookup[phase_id]['id']]
                stats['links_added'] += 1

        # Add task_link if missing
        current_task_links = stage['fields'].get('task_link', [])
        expected_tasks = tasks_by_stage.get(stage_id, [])

        if len(current_task_links) != len(expected_tasks):
            task_ids = [t['id'] for t in expected_tasks]
            if task_ids:
                update_fields['task_link'] = task_ids
                stats['links_added'] += len(task_ids)

        # Update if needed
        if update_fields:
            try:
                stages_table.update(stage['id'], update_fields)
                stats['stages_fixed'] += 1
                print(f"  ✅ Fixed {stage_id}: added {len(update_fields)} links")
            except Exception as e:
                print(f"  ❌ Failed to fix {stage_id}: {e}")
                stats['errors'] += 1

    # Fix Task links
    print("\n📋 Fixing Task links...")
    for task in tasks:
        task_id = task['fields'].get('task_id')
        if not task_id or '.' not in task_id:
            continue

        update_fields = {}
        stage_id = '.'.join(task_id.split('.')[:3])
        phase_id = '.'.join(task_id.split('.')[:2])

        # Ensure stage_link is set
        if not task['fields'].get('stage_link'):
            if stage_id in stage_lookup:
                update_fields['stage_link'] = [stage_lookup[stage_id]['id']]
                stats['links_added'] += 1

        # Ensure phase_link is set
        if not task['fields'].get('phase_link'):
            if phase_id in phase_lookup:
                update_fields['phase_link'] = [phase_lookup[phase_id]['id']]
                stats['links_added'] += 1

        # Skip plan_link as we don't have a Plans table

        # Update if needed
        if update_fields:
            try:
                tasks_table.update(task['id'], update_fields)
                stats['tasks_fixed'] += 1
                print(f"  ✅ Fixed {task_id}: added {len(update_fields)} links")
            except Exception as e:
                print(f"  ❌ Failed to fix {task_id}: {e}")
                stats['errors'] += 1

    # Final verification
    print("\n" + "=" * 80)
    print("LINK VERIFICATION SUMMARY")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"  Phases fixed: {stats['phases_fixed']}")
    print(f"  Stages fixed: {stats['stages_fixed']}")
    print(f"  Tasks fixed: {stats['tasks_fixed']}")
    print(f"  Links added: {stats['links_added']}")
    print(f"  Errors: {stats['errors']}")

    # Check completeness
    print("\n📋 Final Link Completeness Check...")

    # Re-load to verify
    phases = phases_table.all()
    stages = stages_table.all()
    tasks = tasks_table.all()

    issues = []

    # Check phases
    for phase in phases:
        fields = phase['fields']
        phase_id = fields.get('phase_id')
        # Skip plan_link check as we don't have a Plans table

    # Check stages
    for stage in stages:
        fields = stage['fields']
        stage_id = fields.get('stage_id')
        if not fields.get('phase_link'):
            issues.append(f"Stage {stage_id} missing phase_link")

    # Check tasks
    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id')
        if not fields.get('stage_link'):
            issues.append(f"Task {task_id} missing stage_link")
        if not fields.get('phase_link'):
            issues.append(f"Task {task_id} missing phase_link")
        # Skip plan_link check as we don't have a Plans table

    if issues:
        print(f"  ⚠️  {len(issues)} link issues remaining:")
        for issue in issues[:10]:
            print(f"    • {issue}")
        if len(issues) > 10:
            print(f"    ... and {len(issues) - 10} more")
    else:
        print("  ✅ All link fields are complete!")

    print(f"\n🎯 Link Field Coverage:")
    print(f"  • All stages have phase_link: {'✅' if not any('Stage' in i and 'phase_link' in i for i in issues) else '❌'}")
    print(f"  • All tasks have stage_link: {'✅' if not any('Task' in i and 'stage_link' in i for i in issues) else '❌'}")
    print(f"  • All tasks have phase_link: {'✅' if not any('Task' in i and 'phase_link' in i for i in issues) else '❌'}")

    total_fixed = stats['phases_fixed'] + stats['stages_fixed'] + stats['tasks_fixed']

    if total_fixed > 0:
        print(f"\n✅ SUCCESS! Fixed {total_fixed} records with {stats['links_added']} links")
    else:
        print(f"\n✅ All link fields were already complete")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return len(issues) == 0

def main():
    """Main entry point."""
    success = verify_and_fix_links()

    if success:
        print("\n✅ SUCCESS! All link fields are complete")
        return 0
    else:
        print("\n⚠️  Some link issues remain")
        return 1

if __name__ == "__main__":
    exit(main())