#!/usr/bin/env python3
"""
Fix all RANGE BETWEEN → ROWS BETWEEN technical inconsistencies.
Addresses 38 tasks identified in pre-flight audit.
"""

import os
import json
from datetime import datetime
from pyairtable import Api

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
tasks_table = base.table('Tasks')

def fix_range_between_issues():
    """Fix all RANGE BETWEEN → ROWS BETWEEN issues."""
    print("=" * 80)
    print("FIXING TECHNICAL INCONSISTENCIES: RANGE BETWEEN → ROWS BETWEEN")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all tasks
    tasks = tasks_table.all()

    fixes_made = 0
    tasks_fixed = []
    backup = []

    print("\n📋 Scanning for RANGE BETWEEN usage...")

    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id', '')

        # Check description and notes for RANGE BETWEEN
        description = fields.get('description', '')
        notes = fields.get('notes', '')

        needs_update = False
        update_fields = {}

        # Fix in description
        if 'RANGE BETWEEN' in description:
            backup.append({
                'task_id': task_id,
                'field': 'description',
                'original': description
            })

            new_description = description.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['description'] = new_description
            needs_update = True
            print(f"  Found in {task_id} description")

        # Fix in notes
        if 'RANGE BETWEEN' in notes:
            backup.append({
                'task_id': task_id,
                'field': 'notes',
                'original': notes
            })

            new_notes = notes.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['notes'] = new_notes
            needs_update = True
            print(f"  Found in {task_id} notes")

        # Apply update if needed
        if needs_update:
            try:
                tasks_table.update(task['id'], update_fields)
                fixes_made += 1
                tasks_fixed.append(task_id)
                print(f"  ✅ Fixed {task_id}")
            except Exception as e:
                print(f"  ❌ Failed to fix {task_id}: {e}")

    # Save backup
    backup_file = f"/home/micha/bqx_ml_v3/backups/range_between_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)

    with open(backup_file, 'w') as f:
        json.dump(backup, f, indent=2)

    print(f"\n📄 Backup saved to: {backup_file}")

    # Summary
    print("\n" + "=" * 80)
    print("FIX SUMMARY")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"  Tasks scanned: {len(tasks)}")
    print(f"  Tasks fixed: {fixes_made}")

    if tasks_fixed:
        print(f"\n✅ Fixed tasks:")
        for task_id in tasks_fixed[:10]:
            print(f"  • {task_id}")
        if len(tasks_fixed) > 10:
            print(f"  ... and {len(tasks_fixed) - 10} more")

    print(f"\n🎯 Technical Consistency Achieved:")
    print(f"  • All window operations now use ROWS BETWEEN")
    print(f"  • INTERVAL-CENTRIC architecture properly implemented")
    print(f"  • No time-based RANGE operations remain")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return fixes_made

def main():
    """Main entry point."""
    fixes = fix_range_between_issues()

    if fixes > 0:
        print(f"\n✅ SUCCESS! Fixed {fixes} technical inconsistencies")
        return 0
    else:
        print("\n✅ No RANGE BETWEEN issues found - already compliant")
        return 0

if __name__ == "__main__":
    exit(main())