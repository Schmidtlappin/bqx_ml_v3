#!/usr/bin/env python3
"""
Remediate and reconcile empty link fields throughout AirTable tables.
Establishes proper relationships between Plans, Phases, Stages, and Tasks.
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
plans_table = base.table('Plans')
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

def analyze_missing_links():
    """Analyze and report on missing link fields."""
    print("=" * 80)
    print("ANALYZING MISSING LINK FIELDS")
    print("=" * 80)

    # Get all records
    plans = plans_table.all()
    phases = phases_table.all()
    stages = stages_table.all()
    tasks = tasks_table.all()

    print(f"\n📊 Record Counts:")
    print(f"  Plans: {len(plans)}")
    print(f"  Phases: {len(phases)}")
    print(f"  Stages: {len(stages)}")
    print(f"  Tasks: {len(tasks)}")

    # Analyze Plans
    print("\n📋 Plans Table:")
    plans_missing_phase = 0
    for plan in plans:
        if not plan['fields'].get('phase_link'):
            plans_missing_phase += 1
    print(f"  Plans missing phase_link: {plans_missing_phase}/{len(plans)}")

    # Analyze Phases
    print("\n📋 Phases Table:")
    phases_missing_plan = 0
    phases_missing_stage = 0
    for phase in phases:
        if not phase['fields'].get('plan_link'):
            phases_missing_plan += 1
        if not phase['fields'].get('stage_link'):
            phases_missing_stage += 1
    print(f"  Phases missing plan_link: {phases_missing_plan}/{len(phases)}")
    print(f"  Phases missing stage_link: {phases_missing_stage}/{len(phases)}")

    # Analyze Stages
    print("\n📋 Stages Table:")
    stages_missing_phase = 0
    stages_missing_plan = 0
    stages_missing_task = 0
    for stage in stages:
        if not stage['fields'].get('phase_link'):
            stages_missing_phase += 1
        if not stage['fields'].get('plan_link'):
            stages_missing_plan += 1
        if not stage['fields'].get('task_link'):
            stages_missing_task += 1
    print(f"  Stages missing phase_link: {stages_missing_phase}/{len(stages)}")
    print(f"  Stages missing plan_link: {stages_missing_plan}/{len(stages)}")
    print(f"  Stages missing task_link: {stages_missing_task}/{len(stages)}")

    # Analyze Tasks
    print("\n📋 Tasks Table:")
    tasks_missing_stage = 0
    tasks_missing_phase = 0
    tasks_missing_plan = 0
    for task in tasks:
        if not task['fields'].get('stage_link'):
            tasks_missing_stage += 1
        if not task['fields'].get('phase_link'):
            tasks_missing_phase += 1
        if not task['fields'].get('plan_link'):
            tasks_missing_plan += 1
    print(f"  Tasks missing stage_link: {tasks_missing_stage}/{len(tasks)}")
    print(f"  Tasks missing phase_link: {tasks_missing_phase}/{len(tasks)}")
    print(f"  Tasks missing plan_link: {tasks_missing_plan}/{len(tasks)}")

    return {
        'plans': plans,
        'phases': phases,
        'stages': stages,
        'tasks': tasks
    }

def build_relationship_maps(records):
    """Build maps of relationships based on IDs."""
    print("\n" + "=" * 80)
    print("BUILDING RELATIONSHIP MAPS")
    print("=" * 80)

    # Create ID to record maps
    plans_by_id = {}
    phases_by_id = {}
    stages_by_id = {}
    tasks_by_id = {}

    # Map Plans (usually just one - MP03)
    for plan in records['plans']:
        plan_id = plan['fields'].get('plan_id', '')
        if plan_id:
            plans_by_id[plan_id] = plan

    # Map Phases by phase_id
    for phase in records['phases']:
        phase_id = phase['fields'].get('phase_id', '')
        if phase_id:
            phases_by_id[phase_id] = phase

    # Map Stages by stage_id
    for stage in records['stages']:
        stage_id = stage['fields'].get('stage_id', '')
        if stage_id:
            stages_by_id[stage_id] = stage

    # Map Tasks by task_id
    for task in records['tasks']:
        task_id = task['fields'].get('task_id', '')
        if task_id:
            tasks_by_id[task_id] = task

    print(f"\n✅ Mapped Records:")
    print(f"  Plans: {len(plans_by_id)} unique IDs")
    print(f"  Phases: {len(phases_by_id)} unique IDs")
    print(f"  Stages: {len(stages_by_id)} unique IDs")
    print(f"  Tasks: {len(tasks_by_id)} unique IDs")

    # Build parent-child relationships
    relationships = {
        'plan_phases': defaultdict(list),  # plan_id -> [phase records]
        'phase_stages': defaultdict(list),  # phase_id -> [stage records]
        'stage_tasks': defaultdict(list),   # stage_id -> [task records]
    }

    # Extract plan ID from phase IDs (MP03.P01 -> MP03)
    for phase_id, phase in phases_by_id.items():
        if '.' in phase_id:
            plan_id = phase_id.split('.')[0]  # MP03.P01 -> MP03
            relationships['plan_phases'][plan_id].append(phase)

    # Extract phase ID from stage IDs (MP03.P01.S01 -> MP03.P01)
    for stage_id, stage in stages_by_id.items():
        if '.' in stage_id:
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])  # MP03.P01.S01 -> MP03.P01
                relationships['phase_stages'][phase_id].append(stage)

    # Extract stage ID from task IDs (MP03.P01.S01.T01 -> MP03.P01.S01)
    for task_id, task in tasks_by_id.items():
        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage_id = '.'.join(parts[:3])  # MP03.P01.S01.T01 -> MP03.P01.S01
                relationships['stage_tasks'][stage_id].append(task)

    print(f"\n📊 Relationship Counts:")
    print(f"  Plans with phases: {len(relationships['plan_phases'])}")
    print(f"  Phases with stages: {len(relationships['phase_stages'])}")
    print(f"  Stages with tasks: {len(relationships['stage_tasks'])}")

    return plans_by_id, phases_by_id, stages_by_id, tasks_by_id, relationships

def remediate_links(records, plans_by_id, phases_by_id, stages_by_id, tasks_by_id, relationships):
    """Fix missing link fields."""
    print("\n" + "=" * 80)
    print("REMEDIATING MISSING LINKS")
    print("=" * 80)

    updates_made = {
        'plans': 0,
        'phases': 0,
        'stages': 0,
        'tasks': 0
    }

    # Fix Plan -> Phase links
    print("\n🔧 Fixing Plan -> Phase links...")
    for plan_id, plan in plans_by_id.items():
        phases_for_plan = relationships['plan_phases'][plan_id]
        if phases_for_plan:
            phase_record_ids = [p['id'] for p in phases_for_plan]
            current_links = plan['fields'].get('phase_link', [])

            if not current_links or len(current_links) != len(phase_record_ids):
                try:
                    plans_table.update(plan['id'], {'phase_link': phase_record_ids})
                    print(f"  ✅ Updated {plan_id}: linked {len(phase_record_ids)} phases")
                    updates_made['plans'] += 1
                except Exception as e:
                    print(f"  ❌ Failed to update {plan_id}: {e}")

    # Fix Phase -> Plan and Phase -> Stage links
    print("\n🔧 Fixing Phase links...")
    for phase_id, phase in phases_by_id.items():
        updates = {}

        # Link to plan
        if '.' in phase_id:
            plan_id = phase_id.split('.')[0]
            if plan_id in plans_by_id:
                current_plan_link = phase['fields'].get('plan_link', [])
                if not current_plan_link:
                    updates['plan_link'] = [plans_by_id[plan_id]['id']]

        # Link to stages
        stages_for_phase = relationships['phase_stages'][phase_id]
        if stages_for_phase:
            current_stage_links = phase['fields'].get('stage_link', [])
            stage_record_ids = [s['id'] for s in stages_for_phase]
            if not current_stage_links or len(current_stage_links) != len(stage_record_ids):
                updates['stage_link'] = stage_record_ids

        if updates:
            try:
                phases_table.update(phase['id'], updates)
                print(f"  ✅ Updated {phase_id}: {', '.join(updates.keys())}")
                updates_made['phases'] += 1
            except Exception as e:
                print(f"  ❌ Failed to update {phase_id}: {e}")

    # Fix Stage -> Phase, Plan, and Task links
    print("\n🔧 Fixing Stage links...")
    for stage_id, stage in stages_by_id.items():
        updates = {}

        # Link to phase
        if '.' in stage_id:
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])
                if phase_id in phases_by_id:
                    current_phase_link = stage['fields'].get('phase_link', [])
                    if not current_phase_link:
                        updates['phase_link'] = [phases_by_id[phase_id]['id']]

                # Link to plan
                plan_id = parts[0]
                if plan_id in plans_by_id:
                    current_plan_link = stage['fields'].get('plan_link', [])
                    if not current_plan_link:
                        updates['plan_link'] = [plans_by_id[plan_id]['id']]

        # Link to tasks
        tasks_for_stage = relationships['stage_tasks'][stage_id]
        if tasks_for_stage:
            current_task_links = stage['fields'].get('task_link', [])
            task_record_ids = [t['id'] for t in tasks_for_stage]
            if not current_task_links or len(current_task_links) != len(task_record_ids):
                updates['task_link'] = task_record_ids

        if updates:
            try:
                stages_table.update(stage['id'], updates)
                print(f"  ✅ Updated {stage_id}: {', '.join(updates.keys())}")
                updates_made['stages'] += 1
                time.sleep(0.2)  # Rate limit
            except Exception as e:
                print(f"  ❌ Failed to update {stage_id}: {e}")

    # Fix Task -> Stage, Phase, and Plan links
    print("\n🔧 Fixing Task links...")
    for task_id, task in tasks_by_id.items():
        updates = {}

        # Link to stage, phase, and plan
        if '.' in task_id:
            parts = task_id.split('.')
            if len(parts) >= 3:
                # Link to stage
                stage_id = '.'.join(parts[:3])
                if stage_id in stages_by_id:
                    current_stage_link = task['fields'].get('stage_link', [])
                    if not current_stage_link:
                        updates['stage_link'] = [stages_by_id[stage_id]['id']]

                # Link to phase
                phase_id = '.'.join(parts[:2])
                if phase_id in phases_by_id:
                    current_phase_link = task['fields'].get('phase_link', [])
                    if not current_phase_link:
                        updates['phase_link'] = [phases_by_id[phase_id]['id']]

                # Link to plan
                plan_id = parts[0]
                if plan_id in plans_by_id:
                    current_plan_link = task['fields'].get('plan_link', [])
                    if not current_plan_link:
                        updates['plan_link'] = [plans_by_id[plan_id]['id']]

        if updates:
            try:
                tasks_table.update(task['id'], updates)
                print(f"  ✅ Updated {task_id}: {', '.join(updates.keys())}")
                updates_made['tasks'] += 1
                time.sleep(0.2)  # Rate limit
            except Exception as e:
                print(f"  ❌ Failed to update {task_id}: {e}")

    return updates_made

def verify_links():
    """Verify that all links have been properly established."""
    print("\n" + "=" * 80)
    print("VERIFYING LINK INTEGRITY")
    print("=" * 80)

    # Re-fetch all records to check current state
    plans = plans_table.all()
    phases = phases_table.all()
    stages = stages_table.all()
    tasks = tasks_table.all()

    issues = []

    # Check Plans
    for plan in plans:
        if not plan['fields'].get('phase_link'):
            issues.append(f"Plan {plan['fields'].get('plan_id')} missing phase_link")

    # Check Phases
    for phase in phases:
        if not phase['fields'].get('plan_link'):
            issues.append(f"Phase {phase['fields'].get('phase_id')} missing plan_link")

    # Check Stages
    stages_without_tasks = 0
    for stage in stages:
        if not stage['fields'].get('phase_link'):
            issues.append(f"Stage {stage['fields'].get('stage_id')} missing phase_link")
        if not stage['fields'].get('plan_link'):
            issues.append(f"Stage {stage['fields'].get('stage_id')} missing plan_link")
        # Task links are optional (not all stages have tasks)
        if not stage['fields'].get('task_link'):
            stages_without_tasks += 1

    # Check Tasks
    for task in tasks:
        if not task['fields'].get('stage_link'):
            issues.append(f"Task {task['fields'].get('task_id')} missing stage_link")

    print(f"\n📊 Link Verification Results:")
    print(f"  Total Plans with phase_links: {len([p for p in plans if p['fields'].get('phase_link')])}/{len(plans)}")
    print(f"  Total Phases with plan_links: {len([p for p in phases if p['fields'].get('plan_link')])}/{len(phases)}")
    print(f"  Total Stages with phase_links: {len([s for s in stages if s['fields'].get('phase_link')])}/{len(stages)}")
    print(f"  Total Stages with plan_links: {len([s for s in stages if s['fields'].get('plan_link')])}/{len(stages)}")
    print(f"  Total Stages with task_links: {len(stages) - stages_without_tasks}/{len(stages)}")
    print(f"  Total Tasks with stage_links: {len([t for t in tasks if t['fields'].get('stage_link')])}/{len(tasks)}")

    if issues:
        print(f"\n⚠️ Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("\n✅ All links properly established!")

    return len(issues) == 0

def main():
    """Main execution function."""
    print("=" * 80)
    print("AIRTABLE LINK REMEDIATION SCRIPT")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Step 1: Analyze current state
    print("\n🔍 Step 1: Analyzing current state...")
    records = analyze_missing_links()

    # Step 2: Build relationship maps
    print("\n🗺️ Step 2: Building relationship maps...")
    plans_by_id, phases_by_id, stages_by_id, tasks_by_id, relationships = build_relationship_maps(records)

    # Step 3: Remediate missing links
    print("\n🔧 Step 3: Remediating missing links...")
    updates_made = remediate_links(records, plans_by_id, phases_by_id, stages_by_id, tasks_by_id, relationships)

    # Step 4: Verify results
    print("\n✅ Step 4: Verifying results...")
    success = verify_links()

    # Final Report
    print("\n" + "=" * 80)
    print("REMEDIATION SUMMARY")
    print("=" * 80)
    print(f"\n📊 Updates Made:")
    print(f"  Plans updated: {updates_made['plans']}")
    print(f"  Phases updated: {updates_made['phases']}")
    print(f"  Stages updated: {updates_made['stages']}")
    print(f"  Tasks updated: {updates_made['tasks']}")
    print(f"  TOTAL: {sum(updates_made.values())} records updated")

    if success:
        print("\n✅ SUCCESS: All link fields have been properly remediated!")
    else:
        print("\n⚠️ PARTIAL SUCCESS: Some links may still need attention")
        print("Please review the verification results above")

    print(f"\n🏁 Remediation completed at: {datetime.now().isoformat()}")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())