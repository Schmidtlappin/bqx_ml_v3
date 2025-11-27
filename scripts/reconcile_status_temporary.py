#!/usr/bin/env python3
"""
Temporarily reconcile status fields using existing options
until Cancelled and Restated are added to AirTable
Version 1.0
"""

import json
from pyairtable import Api
from datetime import datetime

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)

# Mapping for temporary status values
TEMPORARY_MAPPING = {
    'Cancelled': 'Done',      # Cancelled tasks are "done" (no more work needed)
    'Restated': 'Todo'         # Restated tasks need to be redone with new scope
}

def reconcile_statuses():
    """
    Update status fields to match notes content using available options
    """
    tasks_table = base.table('Tasks')

    # Load the mismatches we found
    with open('/home/micha/bqx_ml_v3/intelligence/status_mismatches.json', 'r') as f:
        data = json.load(f)
        mismatches = data['mismatches']

    print(f"\n🔧 RECONCILING {len(mismatches)} STATUS MISMATCHES")
    print("Using temporary mappings until new options are added:")
    print("  • Cancelled → Done (task complete, no more work)")
    print("  • Restated → Todo (needs work with new scope)")
    print("-" * 60)

    updated = 0
    failed = 0

    for mismatch in mismatches:
        task_id = mismatch['task_id']
        record_id = mismatch['record_id']
        should_be = mismatch['should_be']
        current = mismatch['current_status']

        # Get temporary status
        temp_status = TEMPORARY_MAPPING.get(should_be, should_be)

        try:
            # Update with temporary status
            tasks_table.update(record_id, {'status': temp_status})
            print(f"  ✅ {task_id}: {current} → {temp_status}")
            print(f"     (Notes indicate: {should_be})")
            updated += 1
        except Exception as e:
            print(f"  ❌ {task_id}: Failed to update - {e}")
            failed += 1

    print("\n" + "="*60)
    print("RECONCILIATION RESULTS")
    print("-" * 40)
    print(f"✅ Updated: {updated} records")
    print(f"❌ Failed: {failed} records")

    if updated > 0:
        print("\n📝 IMPORTANT:")
        print("These are TEMPORARY status values.")
        print("Once 'Cancelled' and 'Restated' options are added to AirTable,")
        print("run fix_status_mismatches.py to set the correct values.")

        # Create a reconciliation note
        timestamp = datetime.now().isoformat()
        reconciliation_note = f"""
🔄 TEMPORARY RECONCILIATION: {timestamp}
================================================
STATUS FIELD RECONCILED
Due to missing status options in AirTable, using:
• Cancelled tasks → 'Done' (no more work needed)
• Restated tasks → 'Todo' (needs new implementation)

TRUE STATUS: See notes field for actual status
ACTION: Add 'Cancelled' and 'Restated' to Status field
================================================"""

        # Add reconciliation note to affected tasks
        print("\n📝 Adding reconciliation notes...")
        for mismatch in mismatches[:updated]:
            record_id = mismatch['record_id']
            try:
                # Get current notes
                record = tasks_table.get(record_id)
                existing_notes = record['fields'].get('notes', '')

                # Only add if not already there
                if 'TEMPORARY RECONCILIATION' not in existing_notes:
                    updated_notes = f"{reconciliation_note}\n\n{existing_notes}"
                    tasks_table.update(record_id, {'notes': updated_notes})
                    print(f"  📝 Added note to {mismatch['task_id']}")
            except:
                pass  # Silent fail on note update

    return updated, failed

# Main execution
if __name__ == "__main__":
    print("\n🔄 TEMPORARY STATUS RECONCILIATION")
    print("="*60)

    updated, failed = reconcile_statuses()

    if updated == 0 and failed == 0:
        print("\n✅ No mismatches found - all statuses are reconciled!")

    print("\n✅ Reconciliation complete!")