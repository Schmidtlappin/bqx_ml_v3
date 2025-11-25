#!/usr/bin/env python3
"""
Refactor AirTable IDs to Standardized Format

Converts:
- Phases.phase_id: P##.## → MP##.P##
- Stages.stage_id: S##.##.## → MP##.P##.S##
- Tasks.task_id: T##.##.##.## → MP##.P##.S##.T##

This ensures hierarchical consistency and clarity in the project structure.
"""
import json
import re
import sys
from typing import Dict, List, Tuple, Optional
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
phases_table = api.table(AIRTABLE_BASE_ID, 'Phases')
stages_table = api.table(AIRTABLE_BASE_ID, 'Stages')
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

# Conversion tracking
conversion_report = {
    'phases': {'total': 0, 'converted': 0, 'skipped': 0, 'errors': []},
    'stages': {'total': 0, 'converted': 0, 'skipped': 0, 'errors': []},
    'tasks': {'total': 0, 'converted': 0, 'skipped': 0, 'errors': []}
}

# ID mappings for reference updates
id_mappings = {
    'phases': {},
    'stages': {},
    'tasks': {}
}


def parse_phase_id(old_id: str) -> Optional[Tuple[str, str]]:
    """
    Parse old phase ID format (P##.##) and extract components.

    Examples:
        P01.01 → (MP='01', P='01')
        P03.02 → (MP='03', P='02')

    Returns:
        Tuple of (master_plan, phase) or None if invalid
    """
    match = re.match(r'P(\d{2})\.(\d{2})', old_id)
    if match:
        master_plan = match.group(1)
        phase = match.group(2)
        return (master_plan, phase)
    return None


def parse_stage_id(old_id: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse old stage ID format (S##.##.##) and extract components.

    Examples:
        S03.02.07 → (MP='03', P='02', S='07')
        S03.01 → (MP='03', P='01', S='01') [assumes missing stage is 01]
        S03.02.06 → (MP='03', P='02', S='06')

    Returns:
        Tuple of (master_plan, phase, stage) or None if invalid
    """
    # Try full format first: S##.##.##
    match = re.match(r'S(\d{2})\.(\d{2})\.(\d{2})', old_id)
    if match:
        master_plan = match.group(1)
        phase = match.group(2)
        stage = match.group(3)
        return (master_plan, phase, stage)

    # Try shorter format: S##.##
    match = re.match(r'S(\d{2})\.(\d{2})$', old_id)
    if match:
        master_plan = match.group(1)
        phase = match.group(2)
        stage = '01'  # Default to 01 if stage number missing
        return (master_plan, phase, stage)

    # Try shortest format: S##
    match = re.match(r'S(\d{2})$', old_id)
    if match:
        master_plan = match.group(1)
        phase = '01'  # Default phase
        stage = '01'  # Default stage
        return (master_plan, phase, stage)

    return None


def parse_task_id(old_id: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Parse old task ID format (T##.##.##.##) and extract components.

    Examples:
        T03.01.01.04 → (MP='03', P='01', S='01', T='04')
        T04.07.03 → (MP='04', P='07', S='03', T='01') [assumes missing task is 01]

    Returns:
        Tuple of (master_plan, phase, stage, task) or None if invalid
    """
    # Try full format: T##.##.##.##
    match = re.match(r'T(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})', old_id)
    if match:
        master_plan = match.group(1)
        phase = match.group(2)
        stage = match.group(3)
        task = match.group(4)
        return (master_plan, phase, stage, task)

    # Try shorter format: T##.##.##
    match = re.match(r'T(\d{2})\.(\d{2})\.(\d{2})$', old_id)
    if match:
        master_plan = match.group(1)
        phase = match.group(2)
        stage = match.group(3)
        task = '01'  # Default to 01 if task number missing
        return (master_plan, phase, stage, task)

    return None


def convert_phase_id(old_id: str) -> Optional[str]:
    """Convert phase ID from P##.## to MP##.P##"""
    parsed = parse_phase_id(old_id)
    if parsed:
        mp, p = parsed
        return f"MP{mp}.P{p}"
    return None


def convert_stage_id(old_id: str) -> Optional[str]:
    """Convert stage ID from S##.##.## to MP##.P##.S##"""
    parsed = parse_stage_id(old_id)
    if parsed:
        mp, p, s = parsed
        return f"MP{mp}.P{p}.S{s}"
    return None


def convert_task_id(old_id: str) -> Optional[str]:
    """Convert task ID from T##.##.##.## to MP##.P##.S##.T##"""
    parsed = parse_task_id(old_id)
    if parsed:
        mp, p, s, t = parsed
        return f"MP{mp}.P{p}.S{s}.T{t}"
    return None


def update_phases():
    """Update all phase IDs in AirTable"""
    print("\n" + "="*70)
    print("UPDATING PHASES")
    print("="*70)

    all_phases = phases_table.all()
    conversion_report['phases']['total'] = len(all_phases)

    for record in all_phases:
        record_id = record['id']
        old_id = record['fields'].get('phase_id', '')

        if not old_id:
            print(f"⚠️  Skipping record {record_id}: No phase_id found")
            conversion_report['phases']['skipped'] += 1
            continue

        # Check if already in new format
        if old_id.startswith('MP'):
            print(f"✓ Skipping {old_id}: Already in new format")
            conversion_report['phases']['skipped'] += 1
            continue

        new_id = convert_phase_id(old_id)

        if not new_id:
            print(f"❌ Error: Could not parse phase_id: {old_id}")
            conversion_report['phases']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': 'Parse failed'
            })
            continue

        print(f"\n📝 Converting Phase: {old_id} → {new_id}")

        try:
            phases_table.update(record_id, {'phase_id': new_id})
            print(f"✅ Updated record {record_id}")
            conversion_report['phases']['converted'] += 1
            id_mappings['phases'][old_id] = new_id
        except Exception as e:
            print(f"❌ Error updating {old_id}: {e}")
            conversion_report['phases']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': str(e)
            })


def update_stages():
    """Update all stage IDs in AirTable"""
    print("\n" + "="*70)
    print("UPDATING STAGES")
    print("="*70)

    all_stages = stages_table.all()
    conversion_report['stages']['total'] = len(all_stages)

    for record in all_stages:
        record_id = record['id']
        old_id = record['fields'].get('stage_id', '')

        if not old_id:
            print(f"⚠️  Skipping record {record_id}: No stage_id found")
            conversion_report['stages']['skipped'] += 1
            continue

        # Check if already in new format
        if old_id.startswith('MP'):
            print(f"✓ Skipping {old_id}: Already in new format")
            conversion_report['stages']['skipped'] += 1
            continue

        new_id = convert_stage_id(old_id)

        if not new_id:
            print(f"❌ Error: Could not parse stage_id: {old_id}")
            conversion_report['stages']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': 'Parse failed'
            })
            continue

        print(f"\n📝 Converting Stage: {old_id} → {new_id}")

        try:
            stages_table.update(record_id, {'stage_id': new_id})
            print(f"✅ Updated record {record_id}")
            conversion_report['stages']['converted'] += 1
            id_mappings['stages'][old_id] = new_id
        except Exception as e:
            print(f"❌ Error updating {old_id}: {e}")
            conversion_report['stages']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': str(e)
            })


def update_tasks():
    """Update all task IDs in AirTable"""
    print("\n" + "="*70)
    print("UPDATING TASKS")
    print("="*70)

    all_tasks = tasks_table.all()
    conversion_report['tasks']['total'] = len(all_tasks)

    for record in all_tasks:
        record_id = record['id']
        old_id = record['fields'].get('task_id', '')

        if not old_id:
            print(f"⚠️  Skipping record {record_id}: No task_id found")
            conversion_report['tasks']['skipped'] += 1
            continue

        # Check if already in new format
        if old_id.startswith('MP'):
            print(f"✓ Skipping {old_id}: Already in new format")
            conversion_report['tasks']['skipped'] += 1
            continue

        new_id = convert_task_id(old_id)

        if not new_id:
            print(f"❌ Error: Could not parse task_id: {old_id}")
            conversion_report['tasks']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': 'Parse failed'
            })
            continue

        print(f"\n📝 Converting Task: {old_id} → {new_id}")

        try:
            tasks_table.update(record_id, {'task_id': new_id})
            print(f"✅ Updated record {record_id}")
            conversion_report['tasks']['converted'] += 1
            id_mappings['tasks'][old_id] = new_id
        except Exception as e:
            print(f"❌ Error updating {old_id}: {e}")
            conversion_report['tasks']['errors'].append({
                'record_id': record_id,
                'old_id': old_id,
                'error': str(e)
            })


def print_summary():
    """Print conversion summary report"""
    print("\n" + "="*70)
    print("CONVERSION SUMMARY")
    print("="*70)

    for entity_type in ['phases', 'stages', 'tasks']:
        report = conversion_report[entity_type]
        print(f"\n{entity_type.upper()}:")
        print(f"  Total: {report['total']}")
        print(f"  Converted: {report['converted']}")
        print(f"  Skipped: {report['skipped']}")
        print(f"  Errors: {len(report['errors'])}")

        if report['errors']:
            print(f"\n  Error Details:")
            for error in report['errors']:
                print(f"    - {error['old_id']}: {error['error']}")

    # Calculate totals
    total_records = sum(conversion_report[t]['total'] for t in ['phases', 'stages', 'tasks'])
    total_converted = sum(conversion_report[t]['converted'] for t in ['phases', 'stages', 'tasks'])
    total_skipped = sum(conversion_report[t]['skipped'] for t in ['phases', 'stages', 'tasks'])
    total_errors = sum(len(conversion_report[t]['errors']) for t in ['phases', 'stages', 'tasks'])

    print(f"\n{'='*70}")
    print(f"OVERALL TOTALS:")
    print(f"  Total Records: {total_records}")
    print(f"  Successfully Converted: {total_converted}")
    print(f"  Skipped (already converted): {total_skipped}")
    print(f"  Errors: {total_errors}")
    print(f"{'='*70}")


def save_mappings():
    """Save ID mappings to JSON file for reference updates"""
    mapping_file = 'airtable_id_mappings.json'

    with open(mapping_file, 'w') as f:
        json.dump(id_mappings, f, indent=2)

    print(f"\n💾 ID mappings saved to: {mapping_file}")
    print(f"   Use this file to update references in intelligence files and workspace")


def main():
    print("🔄 AirTable ID Standardization Refactoring")
    print("="*70)
    print("\nThis script will convert all IDs to the new standardized format:")
    print("  Phases: P##.## → MP##.P##")
    print("  Stages: S##.##.## → MP##.P##.S##")
    print("  Tasks: T##.##.##.## → MP##.P##.S##.T##")
    print("\n" + "="*70)

    # Confirm before proceeding
    response = input("\nProceed with conversion? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Conversion cancelled")
        sys.exit(0)

    # Update all entities
    update_phases()
    update_stages()
    update_tasks()

    # Print summary
    print_summary()

    # Save mappings
    save_mappings()

    print("\n✅ AirTable ID refactoring complete!")
    print("\n📋 Next Steps:")
    print("   1. Review airtable_id_mappings.json")
    print("   2. Update intelligence files with new IDs")
    print("   3. Update workspace references (docs, scripts)")
    print("   4. Update AirTable field metadata descriptions")


if __name__ == '__main__':
    main()
