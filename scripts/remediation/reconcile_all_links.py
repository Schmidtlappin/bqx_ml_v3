#!/usr/bin/env python3
"""
Comprehensive reconciliation of ALL link fields across ALL tables.
Ensures phase_link, stage_link, and task_link fields are properly set.
"""

import json
import time
from pyairtable import Api

def reconcile_all_links():
    """Reconcile all link fields across all tables."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("COMPREHENSIVE LINK FIELD RECONCILIATION")
    print("=" * 70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get all records and build ID mappings
    print("\n📊 Building ID mappings...")

    # Phases mapping
    phases_table = api.table(base_id, 'Phases')
    all_phases = phases_table.all()
    phase_id_to_record = {}
    for phase in all_phases:
        phase_id = phase['fields'].get('phase_id')
        if phase_id:
            phase_id_to_record[phase_id] = phase['id']
    print(f"  Found {len(phase_id_to_record)} phases")

    # Stages mapping
    stages_table = api.table(base_id, 'Stages')
    all_stages = stages_table.all()
    stage_id_to_record = {}
    stage_record_to_id = {}
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_id_to_record[stage_id] = stage['id']
            stage_record_to_id[stage['id']] = stage_id
    print(f"  Found {len(stage_id_to_record)} stages")

    # Tasks mapping
    tasks_table = api.table(base_id, 'Tasks')
    all_tasks = tasks_table.all()
    task_id_to_record = {}
    for task in all_tasks:
        task_id = task['fields'].get('task_id')
        if task_id:
            task_id_to_record[task_id] = task['id']
    print(f"  Found {len(task_id_to_record)} tasks")

    # =============================
    # RECONCILE STAGES
    # =============================
    print("\n📋 RECONCILING STAGES:")
    print("-" * 50)

    stages_fixed = 0
    for stage in all_stages:
        fields = stage['fields']
        stage_id = fields.get('stage_id', 'Unknown')
        updates = {}

        # Check phase_link
        current_phase_link = fields.get('phase_link', [])

        # Extract expected phase_id from stage_id (e.g., MP03.P01.S01 -> MP03.P01)
        if '.' in stage_id and 'P' in stage_id:
            parts = stage_id.split('.')
            phase_parts = []
            for part in parts:
                phase_parts.append(part)
                if part.startswith('P'):
                    break
            expected_phase_id = '.'.join(phase_parts)

            # Check if phase_link is missing or incorrect
            if not current_phase_link:
                if expected_phase_id in phase_id_to_record:
                    updates['phase_link'] = [phase_id_to_record[expected_phase_id]]
                    print(f"  🔧 {stage_id}: Adding phase_link → {expected_phase_id}")
            else:
                # Verify the link is correct
                linked_phase = None
                for phase in all_phases:
                    if phase['id'] in current_phase_link:
                        linked_phase = phase['fields'].get('phase_id')
                        break

                if linked_phase != expected_phase_id and expected_phase_id in phase_id_to_record:
                    updates['phase_link'] = [phase_id_to_record[expected_phase_id]]
                    print(f"  🔧 {stage_id}: Fixing phase_link → {expected_phase_id} (was {linked_phase})")

        # Check task_link (stages should link to their tasks)
        current_task_link = fields.get('task_link', [])
        expected_task_ids = []

        # Find all tasks that belong to this stage
        for task in all_tasks:
            task_id = task['fields'].get('task_id', '')
            if task_id.startswith(stage_id + '.'):
                expected_task_ids.append(task['id'])

        if expected_task_ids and not current_task_link:
            updates['task_link'] = expected_task_ids
            print(f"  🔧 {stage_id}: Adding task_link → {len(expected_task_ids)} tasks")
        elif expected_task_ids and set(current_task_link) != set(expected_task_ids):
            updates['task_link'] = expected_task_ids
            print(f"  🔧 {stage_id}: Updating task_link → {len(expected_task_ids)} tasks")

        # Apply updates
        if updates:
            try:
                stages_table.update(stage['id'], updates)
                stages_fixed += 1
            except Exception as e:
                print(f"  ✗ {stage_id}: Failed - {e}")

    print(f"\n  Total Stages reconciled: {stages_fixed}")

    # =============================
    # RECONCILE TASKS
    # =============================
    print("\n📋 RECONCILING TASKS:")
    print("-" * 50)

    tasks_fixed = 0
    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        updates = {}

        # Check stage_link
        current_stage_link = fields.get('stage_link', [])

        # Extract expected stage_id from task_id (e.g., MP03.P01.S01.T01 -> MP03.P01.S01)
        if '.' in task_id and 'S' in task_id:
            parts = task_id.split('.')
            stage_parts = []
            for part in parts:
                stage_parts.append(part)
                if part.startswith('S'):
                    break
            expected_stage_id = '.'.join(stage_parts)

            # Check if stage_link is missing or incorrect
            if not current_stage_link:
                if expected_stage_id in stage_id_to_record:
                    updates['stage_link'] = [stage_id_to_record[expected_stage_id]]
                    print(f"  🔧 {task_id}: Adding stage_link → {expected_stage_id}")
                else:
                    print(f"  ⚠️ {task_id}: Stage {expected_stage_id} not found")
            else:
                # Verify the link is correct
                linked_stage_id = stage_record_to_id.get(current_stage_link[0], 'Unknown')
                if linked_stage_id != expected_stage_id and expected_stage_id in stage_id_to_record:
                    updates['stage_link'] = [stage_id_to_record[expected_stage_id]]
                    print(f"  🔧 {task_id}: Fixing stage_link → {expected_stage_id} (was {linked_stage_id})")

        # Check phase_link
        current_phase_link = fields.get('phase_link', [])

        # Extract expected phase_id from task_id (e.g., MP03.P01.S01.T01 -> MP03.P01)
        if '.' in task_id and 'P' in task_id:
            parts = task_id.split('.')
            phase_parts = []
            for part in parts:
                phase_parts.append(part)
                if part.startswith('P'):
                    break
            expected_phase_id = '.'.join(phase_parts)

            # Check if phase_link is missing or incorrect
            if not current_phase_link:
                if expected_phase_id in phase_id_to_record:
                    updates['phase_link'] = [phase_id_to_record[expected_phase_id]]
                    print(f"  🔧 {task_id}: Adding phase_link → {expected_phase_id}")

        # Apply updates
        if updates:
            try:
                tasks_table.update(task['id'], updates)
                tasks_fixed += 1
            except Exception as e:
                print(f"  ✗ {task_id}: Failed - {e}")

    print(f"\n  Total Tasks reconciled: {tasks_fixed}")

    # =============================
    # RECONCILE PHASES
    # =============================
    print("\n📋 RECONCILING PHASES:")
    print("-" * 50)

    phases_fixed = 0
    for phase in all_phases:
        fields = phase['fields']
        phase_id = fields.get('phase_id', 'Unknown')
        updates = {}

        # Check stage_link (phases should link to their stages)
        current_stage_link = fields.get('stage_link', [])
        expected_stage_ids = []

        # Find all stages that belong to this phase
        for stage in all_stages:
            stage_id = stage['fields'].get('stage_id', '')
            if stage_id.startswith(phase_id + '.'):
                expected_stage_ids.append(stage['id'])

        if expected_stage_ids and not current_stage_link:
            updates['stage_link'] = expected_stage_ids
            print(f"  🔧 {phase_id}: Adding stage_link → {len(expected_stage_ids)} stages")
        elif expected_stage_ids and set(current_stage_link) != set(expected_stage_ids):
            updates['stage_link'] = expected_stage_ids
            print(f"  🔧 {phase_id}: Updating stage_link → {len(expected_stage_ids)} stages")

        # Check task_link (phases should link to their tasks)
        current_task_link = fields.get('task_link', [])
        expected_task_ids = []

        # Find all tasks that belong to this phase
        for task in all_tasks:
            task_id = task['fields'].get('task_id', '')
            if task_id.startswith(phase_id + '.'):
                expected_task_ids.append(task['id'])

        if expected_task_ids and not current_task_link:
            updates['task_link'] = expected_task_ids
            print(f"  🔧 {phase_id}: Adding task_link → {len(expected_task_ids)} tasks")
        elif expected_task_ids and set(current_task_link) != set(expected_task_ids):
            updates['task_link'] = expected_task_ids
            print(f"  🔧 {phase_id}: Updating task_link → {len(expected_task_ids)} tasks")

        # Apply updates
        if updates:
            try:
                phases_table.update(phase['id'], updates)
                phases_fixed += 1
            except Exception as e:
                print(f"  ✗ {phase_id}: Failed - {e}")

    print(f"\n  Total Phases reconciled: {phases_fixed}")

    # =============================
    # VALIDATION
    # =============================
    print("\n" + "=" * 70)
    print("RECONCILIATION SUMMARY")
    print("=" * 70)
    print(f"✅ Phases reconciled: {phases_fixed}")
    print(f"✅ Stages reconciled: {stages_fixed}")
    print(f"✅ Tasks reconciled: {tasks_fixed}")
    print(f"✅ Total updates: {phases_fixed + stages_fixed + tasks_fixed}")

    # Verify all links
    print("\n📊 LINK VERIFICATION:")

    # Check Tasks
    tasks_missing_stage = 0
    tasks_missing_phase = 0
    for task in all_tasks:
        if not task['fields'].get('stage_link', []):
            tasks_missing_stage += 1
        if not task['fields'].get('phase_link', []):
            tasks_missing_phase += 1

    print(f"  Tasks: {len(all_tasks) - tasks_missing_stage}/{len(all_tasks)} have stage_link")
    print(f"  Tasks: {len(all_tasks) - tasks_missing_phase}/{len(all_tasks)} have phase_link")

    # Check Stages
    stages_missing_phase = 0
    stages_missing_task = 0
    for stage in all_stages:
        if not stage['fields'].get('phase_link', []):
            stages_missing_phase += 1
        if not stage['fields'].get('task_link', []):
            stages_missing_task += 1

    print(f"  Stages: {len(all_stages) - stages_missing_phase}/{len(all_stages)} have phase_link")
    print(f"  Stages: {len(all_stages) - stages_missing_task}/{len(all_stages)} have task_link")

    # Check Phases
    phases_missing_stage = 0
    phases_missing_task = 0
    for phase in all_phases:
        if not phase['fields'].get('stage_link', []):
            phases_missing_stage += 1
        if not phase['fields'].get('task_link', []):
            phases_missing_task += 1

    print(f"  Phases: {len(all_phases) - phases_missing_stage}/{len(all_phases)} have stage_link")
    print(f"  Phases: {len(all_phases) - phases_missing_task}/{len(all_phases)} have task_link")

    if (tasks_missing_stage == 0 and tasks_missing_phase == 0 and
        stages_missing_phase == 0 and phases_missing_stage == 0):
        print("\n✨ SUCCESS: All link fields are fully reconciled!")
    else:
        print("\n⚠️ Some link fields may still need attention")

if __name__ == "__main__":
    reconcile_all_links()