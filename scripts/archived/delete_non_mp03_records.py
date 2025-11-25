#!/usr/bin/env python3
"""
Delete Non-MP03 AirTable Records

This script deletes all non-MP03 records from AirTable after backup.

IMPORTANT: This script requires a backup file created by backup_non_mp03_records.py
The backup file is used as the source of record IDs to delete.

Deletion order (respects relational integrity):
1. Tasks (no dependencies)
2. Stages (referenced by tasks)
3. Phases (referenced by stages)
4. Plans (referenced by phases)

Safety features:
- Requires backup file
- Dry-run mode (default)
- Detailed logging
- Verification after deletion
"""
import json
import sys
import glob
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

def find_latest_backup() -> str:
    """Find the most recent backup file"""
    backup_files = glob.glob("airtable_non_mp03_backup_*.json")

    if not backup_files:
        return None

    # Sort by filename (which includes timestamp)
    backup_files.sort(reverse=True)
    return backup_files[0]

def load_backup(filename: str) -> Dict:
    """Load backup file"""
    print(f"\n📂 Loading backup file: {filename}")

    with open(filename, 'r') as f:
        backup_data = json.load(f)

    print(f"✓ Backup loaded:")
    print(f"   Timestamp: {backup_data['metadata']['backup_timestamp']}")
    print(f"   Total records: {backup_data['metadata']['total_records']}")
    print(f"   Plans: {backup_data['plans']['count']}")
    print(f"   Phases: {backup_data['phases']['count']}")
    print(f"   Stages: {backup_data['stages']['count']}")
    print(f"   Tasks: {backup_data['tasks']['count']}")

    return backup_data

def delete_tasks(backup_data: Dict, dry_run: bool = True) -> int:
    """Delete all tasks from backup"""
    print("\n" + "="*70)
    print("DELETING TASKS")
    print("="*70)

    tasks_to_delete = backup_data['tasks']['records']
    deleted_count = 0
    failed_count = 0

    print(f"\nTotal tasks to delete: {len(tasks_to_delete)}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual deletions will occur")

    for i, task in enumerate(tasks_to_delete, 1):
        record_id = task['record_id']
        task_id = task['fields'].get('task_id', 'Unknown')

        if i <= 10 or i % 50 == 0:  # Show first 10, then every 50th
            if dry_run:
                print(f"  [{i}/{len(tasks_to_delete)}] Would delete: {task_id}")
            else:
                print(f"  [{i}/{len(tasks_to_delete)}] Deleting: {task_id}")

        if not dry_run:
            try:
                tasks_table.delete(record_id)
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ Failed to delete {task_id}: {e}")
                failed_count += 1
        else:
            deleted_count += 1

    if dry_run:
        print(f"\n✓ Would delete {deleted_count} tasks (DRY RUN)")
    else:
        print(f"\n✓ Deleted {deleted_count} tasks")
        if failed_count > 0:
            print(f"  ⚠️  Failed to delete {failed_count} tasks")

    return deleted_count

def delete_stages(backup_data: Dict, dry_run: bool = True) -> int:
    """Delete all stages from backup"""
    print("\n" + "="*70)
    print("DELETING STAGES")
    print("="*70)

    stages_to_delete = backup_data['stages']['records']
    deleted_count = 0
    failed_count = 0

    print(f"\nTotal stages to delete: {len(stages_to_delete)}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual deletions will occur")

    for i, stage in enumerate(stages_to_delete, 1):
        record_id = stage['record_id']
        stage_id = stage['fields'].get('stage_id', 'Unknown')

        if i <= 10 or i % 25 == 0:  # Show first 10, then every 25th
            if dry_run:
                print(f"  [{i}/{len(stages_to_delete)}] Would delete: {stage_id}")
            else:
                print(f"  [{i}/{len(stages_to_delete)}] Deleting: {stage_id}")

        if not dry_run:
            try:
                stages_table.delete(record_id)
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ Failed to delete {stage_id}: {e}")
                failed_count += 1
        else:
            deleted_count += 1

    if dry_run:
        print(f"\n✓ Would delete {deleted_count} stages (DRY RUN)")
    else:
        print(f"\n✓ Deleted {deleted_count} stages")
        if failed_count > 0:
            print(f"  ⚠️  Failed to delete {failed_count} stages")

    return deleted_count

def delete_phases(backup_data: Dict, dry_run: bool = True) -> int:
    """Delete all phases from backup"""
    print("\n" + "="*70)
    print("DELETING PHASES")
    print("="*70)

    phases_to_delete = backup_data['phases']['records']
    deleted_count = 0
    failed_count = 0

    print(f"\nTotal phases to delete: {len(phases_to_delete)}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual deletions will occur")

    for i, phase in enumerate(phases_to_delete, 1):
        record_id = phase['record_id']
        phase_id = phase['fields'].get('phase_id', 'Unknown')

        if dry_run:
            print(f"  [{i}/{len(phases_to_delete)}] Would delete: {phase_id}")
        else:
            print(f"  [{i}/{len(phases_to_delete)}] Deleting: {phase_id}")

        if not dry_run:
            try:
                phases_table.delete(record_id)
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ Failed to delete {phase_id}: {e}")
                failed_count += 1
        else:
            deleted_count += 1

    if dry_run:
        print(f"\n✓ Would delete {deleted_count} phases (DRY RUN)")
    else:
        print(f"\n✓ Deleted {deleted_count} phases")
        if failed_count > 0:
            print(f"  ⚠️  Failed to delete {failed_count} phases")

    return deleted_count

def delete_plans(backup_data: Dict, dry_run: bool = True) -> int:
    """Delete all plans from backup"""
    print("\n" + "="*70)
    print("DELETING PLANS")
    print("="*70)

    plans_to_delete = backup_data['plans']['records']
    deleted_count = 0
    failed_count = 0

    print(f"\nTotal plans to delete: {len(plans_to_delete)}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual deletions will occur")

    for i, plan in enumerate(plans_to_delete, 1):
        record_id = plan['record_id']
        plan_id = plan['fields'].get('plan_id', 'Unknown')
        plan_name = plan['fields'].get('name', 'Unnamed')

        if dry_run:
            print(f"  [{i}/{len(plans_to_delete)}] Would delete: {plan_id} - {plan_name}")
        else:
            print(f"  [{i}/{len(plans_to_delete)}] Deleting: {plan_id} - {plan_name}")

        if not dry_run:
            try:
                plans_table.delete(record_id)
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ Failed to delete {plan_id}: {e}")
                failed_count += 1
        else:
            deleted_count += 1

    if dry_run:
        print(f"\n✓ Would delete {deleted_count} plans (DRY RUN)")
    else:
        print(f"\n✓ Deleted {deleted_count} plans")
        if failed_count > 0:
            print(f"  ⚠️  Failed to delete {failed_count} plans")

    return deleted_count

def verify_only_mp03_remains() -> bool:
    """Verify that only MP03 records remain in AirTable"""
    print("\n" + "="*70)
    print("VERIFYING REMAINING RECORDS")
    print("="*70)

    all_clean = True

    # Check Plans
    print("\n📊 Checking Plans table...")
    all_plans = plans_table.all()
    non_mp03_plans = [r for r in all_plans if not r['fields'].get('plan_id', '').startswith('MP03')]

    if non_mp03_plans:
        print(f"  ❌ Found {len(non_mp03_plans)} non-MP03 plans still in table")
        for plan in non_mp03_plans[:5]:
            print(f"      - {plan['fields'].get('plan_id')}")
        all_clean = False
    else:
        mp03_count = len([r for r in all_plans if r['fields'].get('plan_id', '').startswith('MP03')])
        print(f"  ✅ Only MP03 plans remain ({mp03_count} records)")

    # Check Phases
    print("\n📊 Checking Phases table...")
    all_phases = phases_table.all()
    non_mp03_phases = [r for r in all_phases if not r['fields'].get('phase_id', '').startswith('MP03.')]

    if non_mp03_phases:
        print(f"  ❌ Found {len(non_mp03_phases)} non-MP03 phases still in table")
        for phase in non_mp03_phases[:5]:
            print(f"      - {phase['fields'].get('phase_id')}")
        all_clean = False
    else:
        mp03_count = len([r for r in all_phases if r['fields'].get('phase_id', '').startswith('MP03.')])
        print(f"  ✅ Only MP03 phases remain ({mp03_count} records)")

    # Check Stages
    print("\n📊 Checking Stages table...")
    all_stages = stages_table.all()
    non_mp03_stages = [r for r in all_stages if not r['fields'].get('stage_id', '').startswith('MP03.')]

    if non_mp03_stages:
        print(f"  ❌ Found {len(non_mp03_stages)} non-MP03 stages still in table")
        for stage in non_mp03_stages[:5]:
            print(f"      - {stage['fields'].get('stage_id')}")
        all_clean = False
    else:
        mp03_count = len([r for r in all_stages if r['fields'].get('stage_id', '').startswith('MP03.')])
        print(f"  ✅ Only MP03 stages remain ({mp03_count} records)")

    # Check Tasks
    print("\n📊 Checking Tasks table...")
    all_tasks = tasks_table.all()
    non_mp03_tasks = [r for r in all_tasks if not r['fields'].get('task_id', '').startswith('MP03.')]

    if non_mp03_tasks:
        print(f"  ❌ Found {len(non_mp03_tasks)} non-MP03 tasks still in table")
        for task in non_mp03_tasks[:5]:
            print(f"      - {task['fields'].get('task_id')}")
        all_clean = False
    else:
        mp03_count = len([r for r in all_tasks if r['fields'].get('task_id', '').startswith('MP03.')])
        print(f"  ✅ Only MP03 tasks remain ({mp03_count} records)")

    # Overall result
    print("\n" + "="*70)
    if all_clean:
        print("✅ VERIFICATION PASSED: Only MP03 records remain")
        print("\n📊 Final MP03 Record Count:")
        print(f"   Plans: {len([r for r in all_plans if r['fields'].get('plan_id', '').startswith('MP03')])}")
        print(f"   Phases: {len([r for r in all_phases if r['fields'].get('phase_id', '').startswith('MP03.')])}")
        print(f"   Stages: {len([r for r in all_stages if r['fields'].get('stage_id', '').startswith('MP03.')])}")
        print(f"   Tasks: {len([r for r in all_tasks if r['fields'].get('task_id', '').startswith('MP03.')])}")
    else:
        print("❌ VERIFICATION FAILED: Non-MP03 records still exist")
    print("="*70)

    return all_clean

def main():
    print("🗑️  Delete Non-MP03 AirTable Records")
    print("="*70)

    # Check for backup file
    backup_file = find_latest_backup()

    if not backup_file:
        print("\n❌ ERROR: No backup file found!")
        print("   Please run backup_non_mp03_records.py first")
        return False

    # Load backup
    backup_data = load_backup(backup_file)

    # Ask for confirmation
    print("\n" + "="*70)
    print("⚠️  WARNING: This will delete the following from AirTable:")
    print("="*70)
    print(f"\n  Plans:  {backup_data['plans']['count']} records")
    print(f"  Phases: {backup_data['phases']['count']} records")
    print(f"  Stages: {backup_data['stages']['count']} records")
    print(f"  Tasks:  {backup_data['tasks']['count']} records")
    print(f"\n  TOTAL:  {backup_data['metadata']['total_records']} records")

    print(f"\n📁 Backup file: {backup_file}")
    print(f"   Checksum: {backup_data['metadata']['backup_checksum'][:32]}...")

    print("\n" + "="*70)
    response = input("\nProceed with deletion? Type 'DELETE' to confirm: ")

    if response != 'DELETE':
        print("\n❌ Deletion cancelled")
        print("   (To proceed, you must type 'DELETE' exactly)")
        return False

    print("\n✓ Deletion confirmed")

    # Perform deletions in order
    print("\n" + "="*70)
    print("DELETION SEQUENCE")
    print("="*70)
    print("\nDeleting in order: Tasks → Stages → Phases → Plans")
    print("(This order respects relational dependencies)")

    tasks_deleted = delete_tasks(backup_data, dry_run=False)
    stages_deleted = delete_stages(backup_data, dry_run=False)
    phases_deleted = delete_phases(backup_data, dry_run=False)
    plans_deleted = delete_plans(backup_data, dry_run=False)

    # Verify results
    verification_passed = verify_only_mp03_remains()

    # Print summary
    print("\n" + "="*70)
    print("DELETION SUMMARY")
    print("="*70)

    print(f"\n📊 Records Deleted:")
    print(f"   Plans:  {plans_deleted}")
    print(f"   Phases: {phases_deleted}")
    print(f"   Stages: {stages_deleted}")
    print(f"   Tasks:  {tasks_deleted}")
    print(f"   TOTAL:  {plans_deleted + phases_deleted + stages_deleted + tasks_deleted}")

    print(f"\n📁 Backup preserved at: {backup_file}")

    if verification_passed:
        print("\n✅ DELETION COMPLETE AND VERIFIED")
        print("   Only MP03 records remain in AirTable")
    else:
        print("\n⚠️  DELETION COMPLETE BUT VERIFICATION FAILED")
        print("   Some non-MP03 records may still exist")
        print("   Please review manually")

    print("\n" + "="*70)

    return verification_passed

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
