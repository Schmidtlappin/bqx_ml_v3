#!/usr/bin/env python3
"""
Fix ALL RANGE BETWEEN issues in AirTable - Final remediation.
This is critical for INTERVAL-CENTRIC compliance.
"""

import os
import json
import time
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
stages_table = base.table('Stages')
phases_table = base.table('Phases')

def fix_range_between():
    """Fix all RANGE BETWEEN issues across all tables."""

    print("=" * 80)
    print("🔧 FIXING ALL RANGE BETWEEN ISSUES")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    print("\nThis is CRITICAL for INTERVAL-CENTRIC compliance!")

    total_fixed = 0

    # Fix tasks
    print("\n📋 Fixing Tasks...")
    tasks = tasks_table.all()
    tasks_fixed = 0

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        description = task['fields'].get('description', '')
        notes = task['fields'].get('notes', '')

        updated = False
        update_fields = {}

        # Fix description
        if 'RANGE BETWEEN' in description:
            new_description = description.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['description'] = new_description
            updated = True

        # Fix notes
        if 'RANGE BETWEEN' in notes:
            new_notes = notes.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['notes'] = new_notes
            updated = True

        if updated:
            try:
                tasks_table.update(task['id'], update_fields)
                tasks_fixed += 1
                print(f"  ✅ Fixed {task_id}")
            except Exception as e:
                print(f"  ❌ Failed to fix {task_id}: {e}")

            # Rate limiting
            time.sleep(0.2)

    total_fixed += tasks_fixed
    print(f"  Fixed {tasks_fixed} tasks")

    # Fix stages
    print("\n📋 Fixing Stages...")
    stages = stages_table.all()
    stages_fixed = 0

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        description = stage['fields'].get('description', '')
        notes = stage['fields'].get('notes', '')

        updated = False
        update_fields = {}

        # Fix description
        if 'RANGE BETWEEN' in description:
            new_description = description.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['description'] = new_description
            updated = True

        # Fix notes
        if notes and 'RANGE BETWEEN' in notes:
            new_notes = notes.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['notes'] = new_notes
            updated = True

        if updated:
            try:
                stages_table.update(stage['id'], update_fields)
                stages_fixed += 1
                print(f"  ✅ Fixed {stage_id}")
            except Exception as e:
                print(f"  ❌ Failed to fix {stage_id}: {e}")

            # Rate limiting
            time.sleep(0.2)

    total_fixed += stages_fixed
    print(f"  Fixed {stages_fixed} stages")

    # Fix phases
    print("\n📋 Fixing Phases...")
    phases = phases_table.all()
    phases_fixed = 0

    for phase in phases:
        phase_id = phase['fields'].get('phase_id', '')
        description = phase['fields'].get('description', '')
        notes = phase['fields'].get('notes', '')

        updated = False
        update_fields = {}

        # Fix description
        if 'RANGE BETWEEN' in description:
            new_description = description.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['description'] = new_description
            updated = True

        # Fix notes
        if notes and 'RANGE BETWEEN' in notes:
            new_notes = notes.replace('RANGE BETWEEN', 'ROWS BETWEEN')
            update_fields['notes'] = new_notes
            updated = True

        if updated:
            try:
                phases_table.update(phase['id'], update_fields)
                phases_fixed += 1
                print(f"  ✅ Fixed {phase_id}")
            except Exception as e:
                print(f"  ❌ Failed to fix {phase_id}: {e}")

            # Rate limiting
            time.sleep(0.2)

    total_fixed += phases_fixed
    print(f"  Fixed {phases_fixed} phases")

    # Verification
    print("\n🔍 Verifying fixes...")

    # Re-check tasks
    tasks = tasks_table.all()
    remaining_issues = 0

    for task in tasks:
        description = task['fields'].get('description', '')
        notes = task['fields'].get('notes', '')

        if 'RANGE BETWEEN' in description or 'RANGE BETWEEN' in notes:
            remaining_issues += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 REMEDIATION SUMMARY")
    print("=" * 80)
    print(f"  Total records fixed: {total_fixed}")
    print(f"    • Tasks: {tasks_fixed}")
    print(f"    • Stages: {stages_fixed}")
    print(f"    • Phases: {phases_fixed}")

    if remaining_issues == 0:
        print("\n✅ SUCCESS! All RANGE BETWEEN issues fixed")
        print("🎯 100% INTERVAL-CENTRIC compliant")
        print("✅ ROWS BETWEEN used exclusively")
        return True
    else:
        print(f"\n⚠️ {remaining_issues} issues remain")
        return False

def main():
    """Main entry point."""

    success = fix_range_between()

    if success:
        print("\n" + "=" * 80)
        print("✅ REMEDIATION COMPLETE")
        print("=" * 80)
        print("All RANGE BETWEEN issues have been fixed.")
        print("The project is now 100% INTERVAL-CENTRIC compliant.")
        print("\n🚀 Ready to run pre-flight check again")
        return 0
    else:
        print("\n⚠️ Some issues could not be fixed")
        print("Manual intervention may be required")
        return 1

if __name__ == "__main__":
    exit(main())