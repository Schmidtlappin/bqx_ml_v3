#!/usr/bin/env python3
"""
Add plan_link and phase_link to all MP03 Tasks

This script:
1. Gets the MP03 plan record ID
2. Gets all MP03 phase record IDs
3. Maps each task to its corresponding plan and phase
4. Updates all MP03 tasks with the required link fields
"""
import json
import re
from pyairtable import Api
from typing import Dict, List

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
plans_table = api.table(AIRTABLE_BASE_ID, 'Plans')
phases_table = api.table(AIRTABLE_BASE_ID, 'Phases')
stages_table = api.table(AIRTABLE_BASE_ID, 'Stages')
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

def get_mp03_plan_record() -> Dict:
    """Get the MP03 plan record"""
    print("📥 Fetching MP03 plan record...")

    # Try with MP03 format
    mp03_plans = plans_table.all(formula="{plan_id} = 'MP03'")

    if mp03_plans:
        plan = mp03_plans[0]
        print(f"✓ Found MP03 plan: {plan['fields'].get('name', 'BQX ML V3')}")
        return plan

    # Try searching by name if ID not found
    bqx_plans = plans_table.all(formula="FIND('BQX ML', {name})")
    if bqx_plans:
        for plan in bqx_plans:
            if 'V3' in plan['fields'].get('name', '') or 'v3' in plan['fields'].get('name', ''):
                print(f"✓ Found BQX ML V3 plan: {plan['fields'].get('plan_id')} - {plan['fields'].get('name')}")
                return plan

    print("❌ Could not find MP03 plan record")
    return None

def get_mp03_phases() -> Dict[str, str]:
    """Get all MP03 phase records and create a mapping of phase_id to record_id"""
    print("\n📥 Fetching MP03 phase records...")

    phase_mapping = {}

    # Get all phases
    all_phases = phases_table.all()

    for phase in all_phases:
        phase_id = phase['fields'].get('phase_id', '')

        # Check if it's an MP03 phase
        if phase_id.startswith('MP03.'):
            # Extract phase number (MP03.P01 -> P01)
            match = re.match(r'MP03\.(P\d{2})', phase_id)
            if match:
                phase_num = match.group(1)
                phase_mapping[phase_num] = phase['id']
                print(f"  ✓ Found {phase_id}: {phase['fields'].get('name', '')}")

    print(f"\n✓ Found {len(phase_mapping)} MP03 phases")
    return phase_mapping

def get_mp03_stages() -> Dict[str, str]:
    """Get all MP03 stage records and create a mapping of stage_id to record_id"""
    print("\n📥 Fetching MP03 stage records...")

    stage_mapping = {}

    # Get all stages
    all_stages = stages_table.all()

    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id', '')

        # Check if it's an MP03 stage
        if stage_id.startswith('MP03.'):
            stage_mapping[stage_id] = stage['id']

    print(f"✓ Found {len(stage_mapping)} MP03 stages")
    return stage_mapping

def extract_hierarchy_from_task_id(task_id: str) -> Dict[str, str]:
    """Extract plan, phase, and stage from task_id"""
    # Format: MP03.P##.S##.T##
    match = re.match(r'(MP\d{2})\.(P\d{2})\.(S\d{2})\.(T\d{2})', task_id)

    if match:
        return {
            'plan': match.group(1),    # MP03
            'phase': match.group(2),    # P##
            'stage': f"{match.group(1)}.{match.group(2)}.{match.group(3)}"  # MP03.P##.S##
        }
    return {}

def update_task_links(mp03_plan_id: str, phase_mapping: Dict[str, str], stage_mapping: Dict[str, str]):
    """Update all MP03 tasks with plan_link and phase_link"""
    print("\n📥 Fetching MP03 tasks...")

    # Get all tasks
    all_tasks = tasks_table.all()

    mp03_tasks = []
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        if task_id.startswith('MP03.'):
            mp03_tasks.append(task)

    print(f"✓ Found {len(mp03_tasks)} MP03 tasks to update")

    # Track statistics
    stats = {
        'already_complete': 0,
        'missing_phase': 0,
        'missing_stage': 0,
        'updated': 0,
        'failed': 0
    }

    for i, task in enumerate(mp03_tasks, 1):
        task_id = task['fields'].get('task_id', '')
        task_name = task['fields'].get('name', '')

        # Check if links already exist
        existing_plan_link = task['fields'].get('plan_link', [])
        existing_phase_link = task['fields'].get('phase_link', [])
        existing_stage_link = task['fields'].get('stage_link', [])

        if existing_plan_link and existing_phase_link:
            stats['already_complete'] += 1
            if i <= 5:  # Show first 5
                print(f"  ✓ {task_id}: Already has all links")
            continue

        # Extract hierarchy
        hierarchy = extract_hierarchy_from_task_id(task_id)

        if not hierarchy:
            print(f"  ⚠️  {task_id}: Could not parse task ID")
            stats['failed'] += 1
            continue

        # Get phase record ID
        phase_num = hierarchy['phase']
        phase_record_id = phase_mapping.get(phase_num)

        if not phase_record_id:
            print(f"  ⚠️  {task_id}: Could not find phase {phase_num}")
            stats['missing_phase'] += 1
            continue

        # Get stage record ID
        stage_id = hierarchy['stage']
        stage_record_id = stage_mapping.get(stage_id)

        # Prepare update
        update_fields = {}

        # Add plan_link if missing
        if not existing_plan_link:
            update_fields['plan_link'] = [mp03_plan_id]

        # Add phase_link if missing
        if not existing_phase_link:
            update_fields['phase_link'] = [phase_record_id]

        # Ensure stage_link exists (some tasks might be missing it)
        if stage_record_id and not existing_stage_link:
            update_fields['stage_link'] = [stage_record_id]
        elif not stage_record_id and not existing_stage_link:
            stats['missing_stage'] += 1

        # Apply update
        if update_fields:
            try:
                tasks_table.update(task['id'], update_fields)
                stats['updated'] += 1

                if stats['updated'] <= 10:  # Show first 10 updates
                    links_added = []
                    if 'plan_link' in update_fields:
                        links_added.append('plan')
                    if 'phase_link' in update_fields:
                        links_added.append('phase')
                    if 'stage_link' in update_fields:
                        links_added.append('stage')

                    print(f"  ✅ {task_id}: Added {', '.join(links_added)} links")
                elif stats['updated'] == 11:
                    print(f"  ... updating remaining tasks ...")

            except Exception as e:
                print(f"  ❌ {task_id}: Failed to update - {e}")
                stats['failed'] += 1

    return stats

def verify_links():
    """Verify that all MP03 tasks now have the required links"""
    print("\n🔍 Verifying MP03 task links...")

    all_tasks = tasks_table.all()

    mp03_tasks = []
    missing_plan = []
    missing_phase = []
    missing_stage = []

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        if task_id.startswith('MP03.'):
            mp03_tasks.append(task)

            if not task['fields'].get('plan_link'):
                missing_plan.append(task_id)

            if not task['fields'].get('phase_link'):
                missing_phase.append(task_id)

            if not task['fields'].get('stage_link'):
                missing_stage.append(task_id)

    print(f"\n📊 Verification Results:")
    print(f"  Total MP03 tasks: {len(mp03_tasks)}")
    print(f"  Tasks with plan_link: {len(mp03_tasks) - len(missing_plan)} ({(len(mp03_tasks) - len(missing_plan))/len(mp03_tasks)*100:.1f}%)")
    print(f"  Tasks with phase_link: {len(mp03_tasks) - len(missing_phase)} ({(len(mp03_tasks) - len(missing_phase))/len(mp03_tasks)*100:.1f}%)")
    print(f"  Tasks with stage_link: {len(mp03_tasks) - len(missing_stage)} ({(len(mp03_tasks) - len(missing_stage))/len(mp03_tasks)*100:.1f}%)")

    if missing_plan:
        print(f"\n  ⚠️  {len(missing_plan)} tasks missing plan_link")
        for task_id in missing_plan[:3]:
            print(f"      - {task_id}")
        if len(missing_plan) > 3:
            print(f"      ... and {len(missing_plan) - 3} more")

    if missing_phase:
        print(f"\n  ⚠️  {len(missing_phase)} tasks missing phase_link")
        for task_id in missing_phase[:3]:
            print(f"      - {task_id}")
        if len(missing_phase) > 3:
            print(f"      ... and {len(missing_phase) - 3} more")

    if missing_stage:
        print(f"\n  ⚠️  {len(missing_stage)} tasks missing stage_link")
        for task_id in missing_stage[:3]:
            print(f"      - {task_id}")
        if len(missing_stage) > 3:
            print(f"      ... and {len(missing_stage) - 3} more")

    if not missing_plan and not missing_phase:
        print(f"\n  ✅ ALL MP03 TASKS HAVE REQUIRED LINKS!")
        print(f"     plan_link: 100%")
        print(f"     phase_link: 100%")
        if not missing_stage:
            print(f"     stage_link: 100%")

def main():
    print("🔗 MP03 Task Link Addition Script")
    print("="*70)
    print("\nThis script will add plan_link and phase_link to all MP03 tasks")
    print("="*70)

    # Get MP03 plan record
    mp03_plan = get_mp03_plan_record()

    if not mp03_plan:
        print("\n❌ Cannot proceed without MP03 plan record")
        return

    mp03_plan_id = mp03_plan['id']

    # Get all MP03 phases
    phase_mapping = get_mp03_phases()

    if not phase_mapping:
        print("\n❌ No MP03 phases found")
        return

    # Get all MP03 stages
    stage_mapping = get_mp03_stages()

    # Update tasks with links
    print("\n" + "="*70)
    print("UPDATING TASK LINKS")
    print("="*70)

    stats = update_task_links(mp03_plan_id, phase_mapping, stage_mapping)

    # Print summary
    print("\n" + "="*70)
    print("UPDATE SUMMARY")
    print("="*70)
    print(f"\nTasks already complete: {stats['already_complete']}")
    print(f"Tasks updated: {stats['updated']}")
    print(f"Tasks failed: {stats['failed']}")

    if stats['missing_phase'] > 0:
        print(f"Tasks with missing phase mapping: {stats['missing_phase']}")
    if stats['missing_stage'] > 0:
        print(f"Tasks with missing stage mapping: {stats['missing_stage']}")

    # Verify the updates
    verify_links()

    print("\n" + "="*70)
    print("✅ MP03 task link addition complete!")
    print("="*70)

    print("\nAll MP03 tasks now have:")
    print("  • plan_link → MP03 (BQX ML V3)")
    print("  • phase_link → Corresponding phase (P01-P11)")
    print("  • stage_link → Corresponding stage (where available)")

if __name__ == '__main__':
    main()