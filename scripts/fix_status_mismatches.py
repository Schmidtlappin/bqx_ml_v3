#!/usr/bin/env python3
"""
Fix status field mismatches where notes indicate cancelled/restated
but status field still shows old value
Version 1.0
"""

import json
from pyairtable import Api
from datetime import datetime
import re

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)

def detect_status_from_notes(notes):
    """
    Detect the most recent status from notes content
    Look for the topmost status indicator
    """
    if not notes:
        return None

    # Look for status indicators in order of priority (first one found is most recent)
    patterns = [
        (r'^❌\s*CANCELLED:', 'Cancelled'),
        (r'^🔀\s*RESTATED:', 'Restated'),
        (r'^✅\s*COMPLETED:', 'Done'),
        (r'^🔄\s*IN PROGRESS:', 'In Progress'),
        (r'^🚫\s*BLOCKED:', 'Blocked'),
        (r'^📋\s*PLANNED:', 'Todo'),
        (r'^⏸️\s*NOT STARTED:', 'Not Started')
    ]

    # Check first few lines for status indicator
    lines = notes.split('\n')[:5]
    for line in lines:
        for pattern, status in patterns:
            if re.match(pattern, line.strip()):
                return status

    return None

def find_mismatches():
    """
    Find all tasks where status field doesn't match notes content
    """
    mismatches = []
    tasks_table = base.table('Tasks')
    all_tasks = tasks_table.all()

    print(f"\n📋 Checking {len(all_tasks)} tasks for status mismatches...")

    for task in all_tasks:
        task_id = task['fields'].get('task_id', 'Unknown')
        current_status = task['fields'].get('status', '')
        notes = task['fields'].get('notes', '')

        # Detect what status should be based on notes
        detected_status = detect_status_from_notes(notes)

        if detected_status and detected_status != current_status:
            # Special handling for status values that might not exist yet
            if detected_status in ['Cancelled', 'Restated']:
                mismatches.append({
                    'record_id': task['id'],
                    'task_id': task_id,
                    'name': task['fields'].get('name', ''),
                    'current_status': current_status,
                    'should_be': detected_status,
                    'notes_preview': notes[:200] if notes else ''
                })

    return mismatches

def fix_mismatches(mismatches, dry_run=False):
    """
    Fix the mismatched status fields
    """
    tasks_table = base.table('Tasks')
    fixed_count = 0
    failed_count = 0

    print(f"\n{'🔍 DRY RUN - No changes will be made' if dry_run else '🔧 FIXING MISMATCHES'}")
    print("-" * 60)

    for mismatch in mismatches:
        task_id = mismatch['task_id']
        record_id = mismatch['record_id']
        new_status = mismatch['should_be']
        old_status = mismatch['current_status']

        try:
            if dry_run:
                print(f"  Would update {task_id}: {old_status} → {new_status}")
                print(f"    Task: {mismatch['name'][:50]}...")
                fixed_count += 1
            else:
                # Try to update the status field
                tasks_table.update(record_id, {'status': new_status})
                print(f"  ✅ {task_id}: {old_status} → {new_status}")
                print(f"    Task: {mismatch['name'][:50]}...")
                fixed_count += 1
        except Exception as e:
            if 'invalid multiple choice option' in str(e).lower() or 'insufficient permissions' in str(e).lower():
                print(f"  ⚠️ {task_id}: Can't set to '{new_status}' - option not available in field")
                print(f"    Status field needs '{new_status}' option added manually")
                failed_count += 1
            else:
                print(f"  ❌ {task_id}: Failed - {e}")
                failed_count += 1

    return fixed_count, failed_count

def generate_report(mismatches):
    """
    Generate a detailed report of mismatches
    """
    report = []
    report.append("\n" + "="*80)
    report.append("STATUS MISMATCH REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("="*80)

    if not mismatches:
        report.append("\n✅ No status mismatches found!")
        report.append("All status fields match their notes content.")
    else:
        report.append(f"\n⚠️ Found {len(mismatches)} mismatched records")
        report.append("-" * 40)

        # Group by status type
        by_status = {}
        for m in mismatches:
            status = m['should_be']
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(m)

        for status, tasks in by_status.items():
            report.append(f"\n📌 Should be '{status}': {len(tasks)} tasks")
            for task in tasks[:10]:  # Show first 10
                report.append(f"  • {task['task_id']}: {task['name'][:40]}...")
                report.append(f"    Current: '{task['current_status']}' → Should be: '{status}'")
            if len(tasks) > 10:
                report.append(f"  ... and {len(tasks)-10} more")

    report.append("\n" + "="*80)
    report.append("ACTION REQUIRED")
    report.append("-" * 40)

    if mismatches:
        # Check if we need to add field options
        needs_options = set()
        for m in mismatches:
            if m['should_be'] in ['Cancelled', 'Restated']:
                needs_options.add(m['should_be'])

        if needs_options:
            report.append("\n1. ADD STATUS OPTIONS TO AIRTABLE:")
            report.append("   Go to AirTable > Tasks table > Status field")
            report.append("   Add these options:")
            for option in sorted(needs_options):
                report.append(f"   • {option}")
            report.append("\n2. RUN THIS SCRIPT AGAIN:")
            report.append("   python3 /home/micha/bqx_ml_v3/scripts/fix_status_mismatches.py --fix")
        else:
            report.append("\nRun with --fix flag to correct these mismatches:")
            report.append("  python3 /home/micha/bqx_ml_v3/scripts/fix_status_mismatches.py --fix")
    else:
        report.append("\n✅ No actions required - all statuses are consistent!")

    return "\n".join(report)

# Main execution
if __name__ == "__main__":
    import sys

    print("\n🔍 STATUS MISMATCH DETECTOR & FIXER")
    print("="*60)

    # Find mismatches
    mismatches = find_mismatches()

    # Generate and print report
    report = generate_report(mismatches)
    print(report)

    # Check if we should fix
    if '--fix' in sys.argv and mismatches:
        print("\n" + "="*60)
        response = input("Fix these mismatches? (y/n): ")
        if response.lower() == 'y':
            fixed, failed = fix_mismatches(mismatches, dry_run=False)
            print("\n" + "="*60)
            print("RESULTS")
            print("-" * 40)
            print(f"✅ Fixed: {fixed} records")
            print(f"⚠️ Failed: {failed} records")

            if failed > 0:
                print("\nFailed records likely need status field options added.")
                print("Add 'Cancelled' and 'Restated' options to the Status field in AirTable.")
    elif '--dry-run' in sys.argv and mismatches:
        fixed, failed = fix_mismatches(mismatches, dry_run=True)
        print("\n" + "="*60)
        print("DRY RUN COMPLETE")
        print("-" * 40)
        print(f"Would fix: {fixed} records")
        print(f"Would fail: {failed} records")

    # Save mismatches to file for reference
    if mismatches:
        output_file = '/home/micha/bqx_ml_v3/intelligence/status_mismatches.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_mismatches': len(mismatches),
                'mismatches': mismatches
            }, f, indent=2, default=str)
        print(f"\n💾 Mismatch details saved to: {output_file}")

    print("\n✅ Analysis complete!")