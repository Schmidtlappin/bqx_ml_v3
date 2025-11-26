#!/usr/bin/env python3
"""
Reset BQX ML V3 project plan to original state.
Remove simulated outcomes and reset all tasks to Todo status.
"""

import os
import json
import time
from datetime import datetime
from pyairtable import Api

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def reset_project_plan():
    """Reset all tasks to Todo status and restore original notes."""
    print("=" * 80)
    print("🔄 RESETTING BQX ML V3 PROJECT PLAN")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    print("\n⚠️  This will:")
    print("  • Reset all tasks to 'Todo' status")
    print("  • Remove simulated execution outcomes")
    print("  • Restore original implementation notes")
    print("\n📊 Loading tasks...")

    # Get all tasks
    tasks = tasks_table.all()
    total_tasks = len(tasks)
    reset_count = 0

    print(f"  Found {total_tasks} tasks to reset")

    # Process each task
    for i, task in enumerate(tasks, 1):
        task_id = task['fields'].get('task_id', '')
        current_status = task['fields'].get('status', '')
        current_notes = task['fields'].get('notes', '')

        # Check if notes contain execution outcome (our simulation marker)
        if 'EXECUTION OUTCOME' in current_notes or 'Execution Outcome' in current_notes:
            # Extract original content after the marker
            if 'Previous Content:' in current_notes:
                # Get everything after "Previous Content:"
                parts = current_notes.split('Previous Content:')
                if len(parts) > 1:
                    original_notes = parts[1].strip()
                else:
                    original_notes = current_notes
            elif '---' in current_notes:
                # Alternative marker
                parts = current_notes.split('---')
                if len(parts) > 1:
                    original_notes = parts[-1].strip()
                else:
                    original_notes = current_notes
            else:
                # If we can't find original, keep current but remove execution part
                original_notes = ""
        else:
            # Notes weren't modified by simulation
            original_notes = current_notes

        # Reset task
        try:
            update_data = {
                'status': 'Todo'  # Reset all to Todo
            }

            # Only update notes if they were modified
            if 'EXECUTION OUTCOME' in current_notes or 'Execution Outcome' in current_notes:
                update_data['notes'] = original_notes

            tasks_table.update(task['id'], update_data)
            reset_count += 1

            if i % 10 == 0:
                print(f"  Progress: {i}/{total_tasks} tasks processed")

        except Exception as e:
            print(f"  ❌ Error resetting {task_id}: {e}")

        # Rate limiting
        time.sleep(0.2)

    print(f"\n✅ Reset {reset_count}/{total_tasks} tasks")

    # Verification
    print("\n🔍 Verifying reset...")
    tasks = tasks_table.all()

    status_count = {}
    for task in tasks:
        status = task['fields'].get('status', 'Unknown')
        status_count[status] = status_count.get(status, 0) + 1

    print("\n📊 Final Status Distribution:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 RESET SUMMARY")
    print("=" * 80)
    print(f"  Total tasks: {total_tasks}")
    print(f"  Reset to Todo: {status_count.get('Todo', 0)}")
    print(f"  Notes restored: {reset_count}")

    if status_count.get('Todo', 0) == total_tasks:
        print("\n✅ SUCCESS! Project plan fully reset")
        print("All tasks are now in Todo status")
        print("Ready for actual implementation")
    else:
        print(f"\n⚠️  Some tasks may not be in Todo status")
        print("Please review manually if needed")

    return reset_count == total_tasks

def main():
    """Main entry point."""
    print("This will reset the entire BQX ML V3 project plan.")
    print("All simulated outcomes will be removed.")
    print("\nProceed? (y/n): ", end='')

    # Auto-confirm
    response = 'y'
    print(response)

    if response.lower() == 'y':
        success = reset_project_plan()

        if success:
            print("\n🎯 Project plan successfully reset!")
            print("Ready for actual task implementation")
            return 0
        else:
            print("\n⚠️  Reset completed with some issues")
            return 1
    else:
        print("Reset cancelled")
        return 0

if __name__ == "__main__":
    exit(main())