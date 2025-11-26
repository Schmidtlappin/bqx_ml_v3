#!/usr/bin/env python3
"""
Remediate remaining link issues after initial remediation.
Handles duplicate stage IDs and missing phase links.
"""

import os
import json
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

def analyze_plans_table():
    """Analyze the Plans table to understand its field structure."""
    print("=" * 80)
    print("ANALYZING PLANS TABLE STRUCTURE")
    print("=" * 80)

    plans = plans_table.all()
    if plans:
        plan = plans[0]
        print(f"\n📋 Plans table fields:")
        for field_name in plan['fields'].keys():
            field_value = plan['fields'][field_name]
            if isinstance(field_value, list):
                print(f"  - {field_name}: [List with {len(field_value)} items]")
            else:
                value_str = str(field_value)[:50] + "..." if len(str(field_value)) > 50 else str(field_value)
                print(f"  - {field_name}: {value_str}")

    return plans

def fix_duplicate_stage_issues():
    """Handle stages with duplicate IDs and fix their phase links."""
    print("\n" + "=" * 80)
    print("FIXING DUPLICATE STAGE ID ISSUES")
    print("=" * 80)

    stages = stages_table.all()
    phases = phases_table.all()

    # Build phase ID to record mapping
    phases_by_id = {}
    for phase in phases:
        phase_id = phase['fields'].get('phase_id', '')
        if phase_id:
            phases_by_id[phase_id] = phase

    # Find stages with missing phase_link
    stages_missing_phase = []
    stage_ids_seen = defaultdict(list)

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        stage_ids_seen[stage_id].append(stage)

        if not stage['fields'].get('phase_link'):
            stages_missing_phase.append(stage)

    print(f"\n📊 Analysis:")
    print(f"  Stages missing phase_link: {len(stages_missing_phase)}")

    # Show duplicate stage IDs
    duplicates = {sid: stages for sid, stages in stage_ids_seen.items() if len(stages) > 1}
    if duplicates:
        print(f"  Stage IDs with duplicates: {len(duplicates)}")
        for sid, dup_stages in duplicates.items():
            print(f"    {sid}: {len(dup_stages)} records")

    # Fix missing phase links
    fixed_count = 0
    for stage in stages_missing_phase:
        stage_id = stage['fields'].get('stage_id', '')

        if '.' in stage_id:
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])  # MP03.P01.S01 -> MP03.P01

                if phase_id in phases_by_id:
                    try:
                        stages_table.update(stage['id'], {
                            'phase_link': [phases_by_id[phase_id]['id']]
                        })
                        print(f"  ✅ Fixed {stage_id}: linked to phase {phase_id}")
                        fixed_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to fix {stage_id}: {e}")
                else:
                    print(f"  ⚠️ Cannot fix {stage_id}: phase {phase_id} not found")
        else:
            print(f"  ⚠️ Cannot parse stage ID: {stage_id}")

    print(f"\n✅ Fixed {fixed_count} stages with missing phase links")
    return fixed_count

def update_plans_phases_link():
    """Try to update the Plans table with correct field name."""
    print("\n" + "=" * 80)
    print("UPDATING PLANS-PHASES RELATIONSHIP")
    print("=" * 80)

    plans = plans_table.all()
    phases = phases_table.all()

    if not plans:
        print("❌ No plans found")
        return 0

    plan = plans[0]  # Should be MP03
    plan_id = plan['fields'].get('plan_id', 'MP03')

    # Get all phases for this plan
    plan_phases = []
    for phase in phases:
        phase_id = phase['fields'].get('phase_id', '')
        if phase_id and phase_id.startswith(plan_id):
            plan_phases.append(phase)

    if plan_phases:
        phase_record_ids = [p['id'] for p in plan_phases]
        print(f"\n📊 Found {len(plan_phases)} phases for plan {plan_id}")

        # Try different possible field names
        possible_fields = ['phases', 'Phases', 'phases_link', 'phase', 'Phase']

        for field_name in possible_fields:
            if field_name in plan['fields']:
                try:
                    plans_table.update(plan['id'], {
                        field_name: phase_record_ids
                    })
                    print(f"✅ Successfully updated {field_name} field with {len(phase_record_ids)} phases")
                    return 1
                except Exception as e:
                    print(f"⚠️ Failed to update {field_name}: {e}")

        # If no existing field worked, show what fields are available
        print("\n⚠️ Could not find appropriate field for phase links in Plans table")
        print("Available fields:", list(plan['fields'].keys()))
        return 0
    else:
        print(f"❌ No phases found for plan {plan_id}")
        return 0

def final_verification():
    """Final check of all link relationships."""
    print("\n" + "=" * 80)
    print("FINAL LINK VERIFICATION")
    print("=" * 80)

    # Re-fetch all records
    plans = plans_table.all()
    phases = phases_table.all()
    stages = stages_table.all()
    tasks = tasks_table.all()

    stats = {
        'plans_with_phases': 0,
        'phases_with_plan': 0,
        'phases_with_stages': 0,
        'stages_with_phase': 0,
        'stages_with_plan': 0,
        'stages_with_tasks': 0,
        'tasks_with_stage': 0,
        'tasks_with_phase': 0,
        'tasks_with_plan': 0
    }

    # Check Plans
    for plan in plans:
        # Check various possible field names for phase link
        has_phases = False
        for field in ['phases', 'Phases', 'phases_link', 'phase_link']:
            if plan['fields'].get(field):
                has_phases = True
                break
        if has_phases:
            stats['plans_with_phases'] += 1

    # Check Phases
    for phase in phases:
        if phase['fields'].get('plan_link'):
            stats['phases_with_plan'] += 1
        if phase['fields'].get('stage_link'):
            stats['phases_with_stages'] += 1

    # Check Stages
    for stage in stages:
        if stage['fields'].get('phase_link'):
            stats['stages_with_phase'] += 1
        if stage['fields'].get('plan_link'):
            stats['stages_with_plan'] += 1
        if stage['fields'].get('task_link'):
            stats['stages_with_tasks'] += 1

    # Check Tasks
    for task in tasks:
        if task['fields'].get('stage_link'):
            stats['tasks_with_stage'] += 1
        if task['fields'].get('phase_link'):
            stats['tasks_with_phase'] += 1
        if task['fields'].get('plan_link'):
            stats['tasks_with_plan'] += 1

    print("\n📊 Final Link Statistics:")
    print(f"  Plans with phase links: {stats['plans_with_phases']}/{len(plans)}")
    print(f"  Phases with plan links: {stats['phases_with_plan']}/{len(phases)}")
    print(f"  Phases with stage links: {stats['phases_with_stages']}/{len(phases)}")
    print(f"  Stages with phase links: {stats['stages_with_phase']}/{len(stages)}")
    print(f"  Stages with plan links: {stats['stages_with_plan']}/{len(stages)}")
    print(f"  Stages with task links: {stats['stages_with_tasks']}/{len(stages)}")
    print(f"  Tasks with stage links: {stats['tasks_with_stage']}/{len(tasks)}")
    print(f"  Tasks with phase links: {stats['tasks_with_phase']}/{len(tasks)}")
    print(f"  Tasks with plan links: {stats['tasks_with_plan']}/{len(tasks)}")

    # Calculate completion percentage
    total_expected = len(plans) + len(phases)*2 + len(stages)*3 + len(tasks)*3
    total_actual = sum(stats.values())
    completion = (total_actual / total_expected * 100) if total_expected > 0 else 0

    print(f"\n✅ Overall Link Completion: {completion:.1f}%")

    return stats

def main():
    """Main execution function."""
    print("=" * 80)
    print("AIRTABLE REMAINING LINKS REMEDIATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Step 1: Analyze Plans table structure
    print("\n🔍 Step 1: Analyzing Plans table structure...")
    plans = analyze_plans_table()

    # Step 2: Fix duplicate stage issues
    print("\n🔧 Step 2: Fixing stages with missing phase links...")
    stages_fixed = fix_duplicate_stage_issues()

    # Step 3: Try to update Plans-Phases relationship
    print("\n🔧 Step 3: Updating Plans-Phases relationship...")
    plans_updated = update_plans_phases_link()

    # Step 4: Final verification
    print("\n✅ Step 4: Final verification...")
    final_stats = final_verification()

    # Summary
    print("\n" + "=" * 80)
    print("REMEDIATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 Actions Taken:")
    print(f"  Stages fixed: {stages_fixed}")
    print(f"  Plans updated: {plans_updated}")

    print(f"\n✅ Remediation completed at: {datetime.now().isoformat()}")

    return 0

if __name__ == "__main__":
    exit(main())