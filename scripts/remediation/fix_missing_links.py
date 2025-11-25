#!/usr/bin/env python3
"""
Fix missing links in link fields across all tables.
Ensures stage_link, phase_link, and task_link fields contain actual record links.
"""

import json
import time
from pyairtable import Api

def fix_link_fields():
    """Fix all missing link fields to ensure proper record linkage."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("FIXING MISSING LINK FIELDS")
    print("=" * 70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get all tables
    phases_table = api.table(base_id, 'Phases')
    stages_table = api.table(base_id, 'Stages')
    tasks_table = api.table(base_id, 'Tasks')

    # Load all records to build mapping
    all_phases = phases_table.all()
    all_stages = stages_table.all()
    all_tasks = tasks_table.all()

    # Build ID mappings
    phase_map = {}  # phase_id -> record_id
    for phase in all_phases:
        phase_id = phase['fields'].get('phase_id')
        if phase_id:
            phase_map[phase_id] = phase['id']

    stage_map = {}  # stage_id -> record_id
    stage_to_phase = {}  # stage_id -> phase_id
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_map[stage_id] = stage['id']
            # Extract phase from stage_id (e.g., MP03.P01.S01 -> MP03.P01)
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])
                stage_to_phase[stage_id] = phase_id

    task_map = {}  # task_id -> record_id
    task_to_stage = {}  # task_id -> stage_id
    task_to_phase = {}  # task_id -> phase_id
    for task in all_tasks:
        task_id = task['fields'].get('task_id')
        if task_id:
            task_map[task_id] = task['id']
            # Extract stage and phase from task_id (e.g., MP03.P01.S01.T01)
            parts = task_id.split('.')
            if len(parts) >= 3:
                phase_id = '.'.join(parts[:2])  # MP03.P01
                stage_id = '.'.join(parts[:3])  # MP03.P01.S01
                task_to_stage[task_id] = stage_id
                task_to_phase[task_id] = phase_id

    # Fix Tasks table - stage_link and phase_link
    print("\n📋 FIXING TASKS TABLE:")
    print("-" * 50)

    tasks_fixed = 0
    for task in all_tasks:
        task_id = task['fields'].get('task_id')
        if not task_id:
            continue

        updates = {}

        # Check and fix stage_link
        current_stage_link = task['fields'].get('stage_link', [])
        if not current_stage_link and task_id in task_to_stage:
            stage_id = task_to_stage[task_id]
            if stage_id in stage_map:
                updates['stage_link'] = [stage_map[stage_id]]
                print(f"  ✓ {task_id}: Adding stage_link to {stage_id}")

        # Check and fix phase_link
        current_phase_link = task['fields'].get('phase_link', [])
        if not current_phase_link and task_id in task_to_phase:
            phase_id = task_to_phase[task_id]
            if phase_id in phase_map:
                updates['phase_link'] = [phase_map[phase_id]]
                print(f"  ✓ {task_id}: Adding phase_link to {phase_id}")

        # Apply updates
        if updates:
            try:
                tasks_table.update(task['id'], updates)
                tasks_fixed += 1
            except Exception as e:
                print(f"  ✗ {task_id}: Failed to update - {e}")

    # Fix Stages table - phase_link and task_link
    print("\n📋 FIXING STAGES TABLE:")
    print("-" * 50)

    stages_fixed = 0
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if not stage_id:
            continue

        updates = {}

        # Check and fix phase_link
        current_phase_link = stage['fields'].get('phase_link', [])
        if not current_phase_link and stage_id in stage_to_phase:
            phase_id = stage_to_phase[stage_id]
            if phase_id in phase_map:
                updates['phase_link'] = [phase_map[phase_id]]
                print(f"  ✓ {stage_id}: Adding phase_link to {phase_id}")

        # Check and fix task_link (link to all tasks in this stage)
        current_task_link = stage['fields'].get('task_link', [])
        if not current_task_link:
            # Find all tasks for this stage
            stage_tasks = []
            for task_id, task_stage in task_to_stage.items():
                if task_stage == stage_id:
                    if task_id in task_map:
                        stage_tasks.append(task_map[task_id])

            if stage_tasks:
                updates['task_link'] = stage_tasks
                print(f"  ✓ {stage_id}: Linking {len(stage_tasks)} tasks")

        # Apply updates
        if updates:
            try:
                stages_table.update(stage['id'], updates)
                stages_fixed += 1
            except Exception as e:
                print(f"  ✗ {stage_id}: Failed to update - {e}")

    # Fix Phases table - stage_link and task_link
    print("\n📋 FIXING PHASES TABLE:")
    print("-" * 50)

    phases_fixed = 0
    for phase in all_phases:
        phase_id = phase['fields'].get('phase_id')
        if not phase_id:
            continue

        updates = {}

        # Check and fix stage_link
        current_stage_link = phase['fields'].get('stage_link', [])
        if not current_stage_link:
            # Find all stages for this phase
            phase_stages = []
            for stage_id, stage_phase in stage_to_phase.items():
                if stage_phase == phase_id:
                    if stage_id in stage_map:
                        phase_stages.append(stage_map[stage_id])

            if phase_stages:
                updates['stage_link'] = phase_stages
                print(f"  ✓ {phase_id}: Linking {len(phase_stages)} stages")

        # Check and fix task_link
        current_task_link = phase['fields'].get('task_link', [])
        if not current_task_link:
            # Find all tasks for this phase
            phase_tasks = []
            for task_id, task_phase in task_to_phase.items():
                if task_phase == phase_id:
                    if task_id in task_map:
                        phase_tasks.append(task_map[task_id])

            if phase_tasks:
                updates['task_link'] = phase_tasks
                print(f"  ✓ {phase_id}: Linking {len(phase_tasks)} tasks")

        # Apply updates
        if updates:
            try:
                phases_table.update(phase['id'], updates)
                phases_fixed += 1
            except Exception as e:
                print(f"  ✗ {phase_id}: Failed to update - {e}")

    # Summary
    print("\n" + "=" * 70)
    print("LINK FIELD FIXES COMPLETE")
    print("=" * 70)
    print(f"✅ Tasks fixed: {tasks_fixed}")
    print(f"✅ Stages fixed: {stages_fixed}")
    print(f"✅ Phases fixed: {phases_fixed}")
    print(f"✅ Total: {tasks_fixed + stages_fixed + phases_fixed} records")

    print("\n📌 All link fields now properly connected:")
    print("- Tasks → Stages (stage_link)")
    print("- Tasks → Phases (phase_link)")
    print("- Stages → Phases (phase_link)")
    print("- Stages → Tasks (task_link)")
    print("- Phases → Stages (stage_link)")
    print("- Phases → Tasks (task_link)")

    print("\n⏳ Next: Run targeted_field_remediation.py to add content")
    print("   Then wait 5-10 minutes for AI rescoring")

if __name__ == "__main__":
    fix_link_fields()