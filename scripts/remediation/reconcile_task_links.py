#!/usr/bin/env python3
"""
Reconcile Task Links with task_id Hierarchy

This script ensures 100% completion and accuracy of link fields by:
1. Parsing task_id to extract plan, phase, and stage IDs
2. Looking up correct record IDs for each entity
3. Verifying existing links match the task_id hierarchy
4. Fixing any mismatches or missing links
5. Reporting on completion status

Format: MP##.P##.S##.T## → plan_link, phase_link, stage_link must match
"""
import json
import re
from pyairtable import Api
from typing import Dict, List, Tuple, Optional

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

def parse_task_id(task_id: str) -> Optional[Dict[str, str]]:
    """
    Parse task_id to extract plan, phase, and stage IDs.

    Format: MP##.P##.S##.T##
    Example: MP03.P02.S07.T01 → {plan: 'MP03', phase: 'MP03.P02', stage: 'MP03.P02.S07'}
    """
    match = re.match(r'(MP\d{2})\.(P\d{2})\.(S\d{2})\.(T\d{2})', task_id)

    if match:
        plan_id = match.group(1)
        phase_id = f"{plan_id}.{match.group(2)}"
        stage_id = f"{phase_id}.{match.group(3)}"

        return {
            'plan_id': plan_id,
            'phase_id': phase_id,
            'stage_id': stage_id
        }

    return None

def build_record_id_maps() -> Dict[str, Dict[str, str]]:
    """
    Build mappings from entity IDs to AirTable record IDs.

    Returns:
        {
            'plans': {plan_id: record_id},
            'phases': {phase_id: record_id},
            'stages': {stage_id: record_id}
        }
    """
    print("\n" + "="*70)
    print("BUILDING RECORD ID MAPS")
    print("="*70)

    maps = {
        'plans': {},
        'phases': {},
        'stages': {}
    }

    # Build plans map
    print("\n📊 Mapping Plans...")
    all_plans = plans_table.all()
    for record in all_plans:
        plan_id = record['fields'].get('plan_id')
        if plan_id:
            maps['plans'][plan_id] = record['id']
    print(f"   ✓ Mapped {len(maps['plans'])} plans")

    # Build phases map
    print("\n📊 Mapping Phases...")
    all_phases = phases_table.all()
    for record in all_phases:
        phase_id = record['fields'].get('phase_id')
        if phase_id:
            maps['phases'][phase_id] = record['id']
    print(f"   ✓ Mapped {len(maps['phases'])} phases")

    # Build stages map
    print("\n📊 Mapping Stages...")
    all_stages = stages_table.all()
    for record in all_stages:
        stage_id = record['fields'].get('stage_id')
        if stage_id:
            maps['stages'][stage_id] = record['id']
    print(f"   ✓ Mapped {len(maps['stages'])} stages")

    return maps

def check_task_links(task_record: Dict, record_maps: Dict) -> Dict:
    """
    Check if a task's links match its task_id hierarchy.

    Returns dict with:
        - task_id
        - expected links
        - actual links
        - mismatches
        - missing
    """
    fields = task_record['fields']
    task_id = fields.get('task_id', '')

    # Parse task_id
    parsed = parse_task_id(task_id)
    if not parsed:
        return {
            'task_id': task_id,
            'error': 'Invalid task_id format',
            'needs_fix': False
        }

    # Get expected record IDs
    expected = {
        'plan_link': record_maps['plans'].get(parsed['plan_id']),
        'phase_link': record_maps['phases'].get(parsed['phase_id']),
        'stage_link': record_maps['stages'].get(parsed['stage_id'])
    }

    # Get actual links
    actual = {
        'plan_link': fields.get('plan_link', []),
        'phase_link': fields.get('phase_link', []),
        'stage_link': fields.get('stage_link', [])
    }

    # Check for mismatches
    mismatches = []
    missing = []

    for field_name in ['plan_link', 'phase_link', 'stage_link']:
        expected_id = expected[field_name]
        actual_ids = actual[field_name]

        if not expected_id:
            mismatches.append(f"{field_name}: No matching record found for {parsed.get(field_name.replace('_link', '_id'))}")
        elif not actual_ids:
            missing.append(field_name)
        elif expected_id not in actual_ids:
            mismatches.append(f"{field_name}: Expected {expected_id}, got {actual_ids}")

    needs_fix = bool(mismatches or missing)

    return {
        'task_id': task_id,
        'record_id': task_record['id'],
        'parsed_ids': parsed,
        'expected': expected,
        'actual': actual,
        'mismatches': mismatches,
        'missing': missing,
        'needs_fix': needs_fix
    }

def fix_task_links(task_check: Dict) -> bool:
    """Fix task links to match task_id hierarchy"""

    if not task_check['needs_fix']:
        return True

    task_id = task_check['task_id']
    record_id = task_check['record_id']
    expected = task_check['expected']

    # Build update dict
    updates = {}

    for field_name, expected_id in expected.items():
        if expected_id:
            updates[field_name] = [expected_id]

    try:
        tasks_table.update(record_id, updates)
        return True
    except Exception as e:
        print(f"  ❌ Error fixing {task_id}: {e}")
        return False

def reconcile_all_tasks(record_maps: Dict):
    """Reconcile all tasks with their link fields"""
    print("\n" + "="*70)
    print("RECONCILING TASK LINKS")
    print("="*70)

    all_tasks = tasks_table.all()

    print(f"\n📋 Processing {len(all_tasks)} tasks...")

    stats = {
        'total': len(all_tasks),
        'valid': 0,
        'fixed': 0,
        'errors': 0,
        'missing_plan': 0,
        'missing_phase': 0,
        'missing_stage': 0,
        'mismatch_plan': 0,
        'mismatch_phase': 0,
        'mismatch_stage': 0
    }

    issues = []

    for task in all_tasks:
        check = check_task_links(task, record_maps)

        if 'error' in check:
            stats['errors'] += 1
            issues.append(check)
            continue

        # Count specific issues
        if 'plan_link' in check['missing']:
            stats['missing_plan'] += 1
        if 'phase_link' in check['missing']:
            stats['missing_phase'] += 1
        if 'stage_link' in check['missing']:
            stats['missing_stage'] += 1

        for mismatch in check['mismatches']:
            if 'plan_link' in mismatch:
                stats['mismatch_plan'] += 1
            elif 'phase_link' in mismatch:
                stats['mismatch_phase'] += 1
            elif 'stage_link' in mismatch:
                stats['mismatch_stage'] += 1

        if check['needs_fix']:
            # Show first 10 fixes
            if stats['fixed'] < 10:
                print(f"\n  🔧 Fixing: {check['task_id']}")
                if check['missing']:
                    print(f"     Missing: {', '.join(check['missing'])}")
                if check['mismatches']:
                    for mismatch in check['mismatches']:
                        print(f"     {mismatch}")

            success = fix_task_links(check)
            if success:
                stats['fixed'] += 1
            else:
                stats['errors'] += 1
                issues.append(check)
        else:
            stats['valid'] += 1

    if stats['fixed'] > 10:
        print(f"\n  ... fixed {stats['fixed'] - 10} more tasks")

    return stats, issues

def verify_completion(record_maps: Dict):
    """Verify 100% completion of all link fields"""
    print("\n" + "="*70)
    print("VERIFYING 100% COMPLETION")
    print("="*70)

    all_tasks = tasks_table.all()

    incomplete = {
        'plan_link': [],
        'phase_link': [],
        'stage_link': [],
        'any_missing': []
    }

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        has_issue = False

        if not fields.get('plan_link'):
            incomplete['plan_link'].append(task_id)
            has_issue = True

        if not fields.get('phase_link'):
            incomplete['phase_link'].append(task_id)
            has_issue = True

        if not fields.get('stage_link'):
            incomplete['stage_link'].append(task_id)
            has_issue = True

        if has_issue:
            incomplete['any_missing'].append(task_id)

    # Print results
    print(f"\n📊 Completion Status:")
    print(f"   Total tasks: {len(all_tasks)}")
    print(f"   Tasks with all links: {len(all_tasks) - len(incomplete['any_missing'])}")
    print(f"   Tasks missing links: {len(incomplete['any_missing'])}")

    if incomplete['plan_link']:
        print(f"\n⚠️  Tasks missing plan_link: {len(incomplete['plan_link'])}")
        for task_id in incomplete['plan_link'][:5]:
            print(f"      - {task_id}")
        if len(incomplete['plan_link']) > 5:
            print(f"      ... and {len(incomplete['plan_link']) - 5} more")

    if incomplete['phase_link']:
        print(f"\n⚠️  Tasks missing phase_link: {len(incomplete['phase_link'])}")
        for task_id in incomplete['phase_link'][:5]:
            print(f"      - {task_id}")
        if len(incomplete['phase_link']) > 5:
            print(f"      ... and {len(incomplete['phase_link']) - 5} more")

    if incomplete['stage_link']:
        print(f"\n⚠️  Tasks missing stage_link: {len(incomplete['stage_link'])}")
        for task_id in incomplete['stage_link'][:5]:
            print(f"      - {task_id}")
        if len(incomplete['stage_link']) > 5:
            print(f"      ... and {len(incomplete['stage_link']) - 5} more")

    if not incomplete['any_missing']:
        print(f"\n✅ 100% COMPLETION ACHIEVED!")
        print(f"   All {len(all_tasks)} tasks have:")
        print(f"   • plan_link")
        print(f"   • phase_link")
        print(f"   • stage_link")

    return incomplete

def main():
    print("🔗 Task Links Reconciliation")
    print("="*70)
    print("\nThis script will:")
    print("1. Parse task_id to extract hierarchy")
    print("2. Verify links match task_id structure")
    print("3. Fix any mismatches or missing links")
    print("4. Ensure 100% completion")
    print("="*70)

    # Build record ID maps
    record_maps = build_record_id_maps()

    # Reconcile all tasks
    stats, issues = reconcile_all_tasks(record_maps)

    # Verify completion
    incomplete = verify_completion(record_maps)

    # Print summary
    print("\n" + "="*70)
    print("RECONCILIATION SUMMARY")
    print("="*70)

    print(f"\n📊 Task Statistics:")
    print(f"   Total tasks: {stats['total']}")
    print(f"   Already valid: {stats['valid']}")
    print(f"   Fixed: {stats['fixed']}")
    print(f"   Errors: {stats['errors']}")

    print(f"\n🔧 Issues Fixed:")
    print(f"   Missing plan_link: {stats['missing_plan']}")
    print(f"   Missing phase_link: {stats['missing_phase']}")
    print(f"   Missing stage_link: {stats['missing_stage']}")
    print(f"   Mismatched plan_link: {stats['mismatch_plan']}")
    print(f"   Mismatched phase_link: {stats['mismatch_phase']}")
    print(f"   Mismatched stage_link: {stats['mismatch_stage']}")

    if not incomplete['any_missing']:
        print(f"\n✅ SUCCESS: 100% LINK COMPLETION ACHIEVED")
        print(f"   All task_id hierarchies reconciled with link fields")
    else:
        print(f"\n⚠️  WARNING: {len(incomplete['any_missing'])} tasks still have missing links")
        print(f"   Review output above for details")

    print("\n" + "="*70)

    return not bool(incomplete['any_missing'])

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
