#!/usr/bin/env python3
"""
Comprehensive Backup of Non-MP03 AirTable Records

This script creates a complete backup of all AirTable records NOT associated
with the MP03 (BQX ML V3) plan before deletion.

Backup includes:
- All Plans (except MP03)
- All Phases (except MP03.*)
- All Stages (except MP03.*)
- All Tasks (except MP03.*)

Output: JSON file with full field data, record IDs, and metadata
"""
import json
import hashlib
from datetime import datetime
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

def calculate_checksum(data: dict) -> str:
    """Calculate SHA256 checksum of data"""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

def backup_plans() -> Dict:
    """Backup all non-MP03 plans"""
    print("\n" + "="*70)
    print("BACKING UP PLANS")
    print("="*70)

    all_plans = plans_table.all()
    non_mp03_plans = []

    for record in all_plans:
        plan_id = record['fields'].get('plan_id', '')

        # Keep only non-MP03 plans
        if not plan_id.startswith('MP03'):
            non_mp03_plans.append({
                'record_id': record['id'],
                'fields': record['fields'],
                'created_time': record.get('createdTime', ''),
            })
            print(f"  ✓ Backing up: {plan_id} - {record['fields'].get('name', 'Unnamed')}")

    print(f"\n✓ Backed up {len(non_mp03_plans)} non-MP03 plans")

    return {
        'count': len(non_mp03_plans),
        'records': non_mp03_plans,
        'checksum': calculate_checksum(non_mp03_plans)
    }

def backup_phases() -> Dict:
    """Backup all non-MP03 phases"""
    print("\n" + "="*70)
    print("BACKING UP PHASES")
    print("="*70)

    all_phases = phases_table.all()
    non_mp03_phases = []
    plan_distribution = {}

    for record in all_phases:
        phase_id = record['fields'].get('phase_id', '')

        # Keep only non-MP03 phases
        if not phase_id.startswith('MP03.'):
            # Extract plan ID (e.g., MP01 from MP01.P01)
            plan_id = phase_id.split('.')[0] if '.' in phase_id else 'Unknown'

            non_mp03_phases.append({
                'record_id': record['id'],
                'fields': record['fields'],
                'created_time': record.get('createdTime', ''),
            })

            plan_distribution[plan_id] = plan_distribution.get(plan_id, 0) + 1

            if len(non_mp03_phases) <= 10:  # Show first 10
                print(f"  ✓ Backing up: {phase_id} - {record['fields'].get('name', 'Unnamed')}")

    if len(non_mp03_phases) > 10:
        print(f"  ... and {len(non_mp03_phases) - 10} more phases")

    print(f"\n✓ Backed up {len(non_mp03_phases)} non-MP03 phases")
    print(f"  Distribution by plan: {plan_distribution}")

    return {
        'count': len(non_mp03_phases),
        'records': non_mp03_phases,
        'plan_distribution': plan_distribution,
        'checksum': calculate_checksum(non_mp03_phases)
    }

def backup_stages() -> Dict:
    """Backup all non-MP03 stages"""
    print("\n" + "="*70)
    print("BACKING UP STAGES")
    print("="*70)

    all_stages = stages_table.all()
    non_mp03_stages = []
    plan_distribution = {}

    for record in all_stages:
        stage_id = record['fields'].get('stage_id', '')

        # Keep only non-MP03 stages
        if not stage_id.startswith('MP03.'):
            # Extract plan ID (e.g., MP01 from MP01.P01.S01)
            plan_id = stage_id.split('.')[0] if '.' in stage_id else 'Unknown'

            non_mp03_stages.append({
                'record_id': record['id'],
                'fields': record['fields'],
                'created_time': record.get('createdTime', ''),
            })

            plan_distribution[plan_id] = plan_distribution.get(plan_id, 0) + 1

            if len(non_mp03_stages) <= 10:  # Show first 10
                print(f"  ✓ Backing up: {stage_id} - {record['fields'].get('name', 'Unnamed')[:50]}")

    if len(non_mp03_stages) > 10:
        print(f"  ... and {len(non_mp03_stages) - 10} more stages")

    print(f"\n✓ Backed up {len(non_mp03_stages)} non-MP03 stages")
    print(f"  Distribution by plan: {plan_distribution}")

    return {
        'count': len(non_mp03_stages),
        'records': non_mp03_stages,
        'plan_distribution': plan_distribution,
        'checksum': calculate_checksum(non_mp03_stages)
    }

def backup_tasks() -> Dict:
    """Backup all non-MP03 tasks"""
    print("\n" + "="*70)
    print("BACKING UP TASKS")
    print("="*70)

    all_tasks = tasks_table.all()
    non_mp03_tasks = []
    plan_distribution = {}
    score_distribution = {'below_90': 0, 'above_90': 0, 'no_score': 0}

    for record in all_tasks:
        task_id = record['fields'].get('task_id', '')

        # Keep only non-MP03 tasks
        if not task_id.startswith('MP03.'):
            # Extract plan ID (e.g., MP01 from MP01.P01.S01.T01)
            plan_id = task_id.split('.')[0] if '.' in task_id else 'Unknown'

            # Track score distribution
            score = record['fields'].get('record_score', None)
            if score is None:
                score_distribution['no_score'] += 1
            elif score < 90:
                score_distribution['below_90'] += 1
            else:
                score_distribution['above_90'] += 1

            non_mp03_tasks.append({
                'record_id': record['id'],
                'fields': record['fields'],
                'created_time': record.get('createdTime', ''),
            })

            plan_distribution[plan_id] = plan_distribution.get(plan_id, 0) + 1

            if len(non_mp03_tasks) <= 10:  # Show first 10
                print(f"  ✓ Backing up: {task_id} - {record['fields'].get('name', 'Unnamed')[:40]}")

    if len(non_mp03_tasks) > 10:
        print(f"  ... and {len(non_mp03_tasks) - 10} more tasks")

    print(f"\n✓ Backed up {len(non_mp03_tasks)} non-MP03 tasks")
    print(f"  Distribution by plan: {plan_distribution}")
    print(f"  Score distribution: {score_distribution}")

    return {
        'count': len(non_mp03_tasks),
        'records': non_mp03_tasks,
        'plan_distribution': plan_distribution,
        'score_distribution': score_distribution,
        'checksum': calculate_checksum(non_mp03_tasks)
    }

def verify_backup(backup_data: Dict) -> bool:
    """Verify backup completeness by re-querying AirTable"""
    print("\n" + "="*70)
    print("VERIFYING BACKUP COMPLETENESS")
    print("="*70)

    all_verified = True

    # Verify Plans
    print("\n📊 Verifying Plans...")
    all_plans = plans_table.all()
    actual_non_mp03 = len([r for r in all_plans if not r['fields'].get('plan_id', '').startswith('MP03')])
    backed_up = backup_data['plans']['count']

    if actual_non_mp03 == backed_up:
        print(f"  ✅ Plans: {backed_up} backed up = {actual_non_mp03} in AirTable")
    else:
        print(f"  ❌ Plans: {backed_up} backed up ≠ {actual_non_mp03} in AirTable")
        all_verified = False

    # Verify Phases
    print("\n📊 Verifying Phases...")
    all_phases = phases_table.all()
    actual_non_mp03 = len([r for r in all_phases if not r['fields'].get('phase_id', '').startswith('MP03.')])
    backed_up = backup_data['phases']['count']

    if actual_non_mp03 == backed_up:
        print(f"  ✅ Phases: {backed_up} backed up = {actual_non_mp03} in AirTable")
    else:
        print(f"  ❌ Phases: {backed_up} backed up ≠ {actual_non_mp03} in AirTable")
        all_verified = False

    # Verify Stages
    print("\n📊 Verifying Stages...")
    all_stages = stages_table.all()
    actual_non_mp03 = len([r for r in all_stages if not r['fields'].get('stage_id', '').startswith('MP03.')])
    backed_up = backup_data['stages']['count']

    if actual_non_mp03 == backed_up:
        print(f"  ✅ Stages: {backed_up} backed up = {actual_non_mp03} in AirTable")
    else:
        print(f"  ❌ Stages: {backed_up} backed up ≠ {actual_non_mp03} in AirTable")
        all_verified = False

    # Verify Tasks
    print("\n📊 Verifying Tasks...")
    all_tasks = tasks_table.all()
    actual_non_mp03 = len([r for r in all_tasks if not r['fields'].get('task_id', '').startswith('MP03.')])
    backed_up = backup_data['tasks']['count']

    if actual_non_mp03 == backed_up:
        print(f"  ✅ Tasks: {backed_up} backed up = {actual_non_mp03} in AirTable")
    else:
        print(f"  ❌ Tasks: {backed_up} backed up ≠ {actual_non_mp03} in AirTable")
        all_verified = False

    # Overall verification
    print("\n" + "="*70)
    if all_verified:
        print("✅ BACKUP VERIFICATION: 100% COMPLETE")
        print("   All non-MP03 records successfully backed up")
    else:
        print("❌ BACKUP VERIFICATION: FAILED")
        print("   Mismatch between backup and AirTable")
    print("="*70)

    return all_verified

def main():
    print("💾 Non-MP03 AirTable Records Backup")
    print("="*70)
    print("\nThis script will backup all non-MP03 records before deletion")
    print("="*70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"airtable_non_mp03_backup_{timestamp}.json"

    # Perform backups
    plans_backup = backup_plans()
    phases_backup = backup_phases()
    stages_backup = backup_stages()
    tasks_backup = backup_tasks()

    # Assemble complete backup
    backup_data = {
        'metadata': {
            'backup_timestamp': datetime.now().isoformat(),
            'backup_version': '1.0',
            'description': 'Complete backup of non-MP03 AirTable records before deletion',
            'airtable_base_id': AIRTABLE_BASE_ID,
            'total_records': (
                plans_backup['count'] +
                phases_backup['count'] +
                stages_backup['count'] +
                tasks_backup['count']
            )
        },
        'plans': plans_backup,
        'phases': phases_backup,
        'stages': stages_backup,
        'tasks': tasks_backup,
        'restore_instructions': {
            'warning': 'This backup is for archival purposes only. Restoration should be done manually and carefully.',
            'tables': ['Plans', 'Phases', 'Stages', 'Tasks'],
            'order': 'Restore in order: Plans → Phases → Stages → Tasks',
            'note': 'Record IDs in backup may not match after restoration as AirTable generates new IDs'
        }
    }

    # Calculate overall checksum
    backup_data['metadata']['backup_checksum'] = calculate_checksum(backup_data)

    # Save backup
    print("\n" + "="*70)
    print("SAVING BACKUP")
    print("="*70)

    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Backup saved to: {backup_filename}")
    print(f"   File size: {len(json.dumps(backup_data)) / 1024:.1f} KB")

    # Verify backup
    verification_passed = verify_backup(backup_data)

    # Print summary
    print("\n" + "="*70)
    print("BACKUP SUMMARY")
    print("="*70)

    print(f"\n📊 Total Records Backed Up: {backup_data['metadata']['total_records']}")
    print(f"\n  Plans:  {plans_backup['count']}")
    print(f"  Phases: {phases_backup['count']}")
    print(f"  Stages: {stages_backup['count']}")
    print(f"  Tasks:  {tasks_backup['count']}")

    print(f"\n📝 Task Score Distribution (Non-MP03):")
    score_dist = tasks_backup['score_distribution']
    print(f"  Below 90:  {score_dist['below_90']}")
    print(f"  Above 90:  {score_dist['above_90']}")
    print(f"  No score:  {score_dist['no_score']}")

    print(f"\n🔐 Checksums:")
    print(f"  Plans:  {plans_backup['checksum'][:16]}...")
    print(f"  Phases: {phases_backup['checksum'][:16]}...")
    print(f"  Stages: {stages_backup['checksum'][:16]}...")
    print(f"  Tasks:  {tasks_backup['checksum'][:16]}...")
    print(f"  Overall: {backup_data['metadata']['backup_checksum'][:16]}...")

    print(f"\n📁 Backup File: {backup_filename}")
    print(f"   Timestamp: {backup_data['metadata']['backup_timestamp']}")

    if verification_passed:
        print("\n✅ BACKUP COMPLETE AND VERIFIED")
        print("   Ready for deletion phase")
    else:
        print("\n⚠️  BACKUP COMPLETE BUT VERIFICATION FAILED")
        print("   DO NOT PROCEED WITH DELETION")

    print("\n" + "="*70)

    return verification_passed

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
