#!/usr/bin/env python3
"""
Apply status changes identified by the audit
Uses append mode for all notes updates
Version 1.0
"""

import json
from pyairtable import Api
from datetime import datetime
import sys

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)

def load_audit_results():
    """Load the audit results from JSON file"""
    with open('/home/micha/bqx_ml_v3/intelligence/airtable_audit_results.json', 'r') as f:
        return json.load(f)

def create_cancellation_note(reasons):
    """Create a cancellation note block"""
    timestamp = datetime.now().isoformat()
    reasons_text = '\n'.join([f"• {reason}" for reason in reasons])

    note = f"""❌ CANCELLED: {timestamp}
================================================
REASON FOR CANCELLATION
{reasons_text}

STATUS CHANGE
Task cancelled based on audit criteria.
See AIRTABLE_STATUS_STANDARDIZATION_GUIDE.md for details.
================================================"""

    return note

def create_restatement_note(restatements):
    """Create a restatement note block"""
    timestamp = datetime.now().isoformat()

    restatements_text = []
    for r in restatements:
        restatements_text.append(f"Original: {r['original']}")
        restatements_text.append(f"Restated: {r['restated']}")
        restatements_text.append("")

    restatements_formatted = '\n'.join(restatements_text)

    note = f"""🔀 RESTATED: {timestamp}
================================================
TASK REFORMULATION
{restatements_formatted}
REASON
Task scope/requirements clarified based on user feedback
and project evolution.

STATUS CHANGE
Task restated based on audit criteria.
See AIRTABLE_STATUS_STANDARDIZATION_GUIDE.md for details.
================================================"""

    return note

def update_status_field_options():
    """
    Update status field to include Cancelled and Restated options
    Note: This requires API access to field configuration which may not be available
    """
    print("\n📋 STATUS FIELD UPDATE INSTRUCTIONS:")
    print("="*60)
    print("The AirTable API doesn't support updating field options directly.")
    print("Please manually update the Status field in AirTable to include:")
    print("")
    print("Current options:")
    print("  • Todo")
    print("  • In Progress")
    print("  • Done")
    print("  • Blocked")
    print("  • Not Started")
    print("")
    print("ADD these options:")
    print("  • Cancelled")
    print("  • Restated")
    print("")
    print("This needs to be done in:")
    print("  • Tasks table")
    print("  • Stages table (if it has a status field)")
    print("  • Phases table (if it has a status field)")
    print("="*60)

    return False

def apply_cancellations(results):
    """Apply cancellation status to identified tasks"""
    tasks_table = base.table('Tasks')
    stages_table = base.table('Stages')
    phases_table = base.table('Phases')

    cancelled_count = 0

    print("\n❌ APPLYING CANCELLATIONS...")
    print("-"*40)

    for candidate in results['cancellation_candidates']:
        try:
            table_name = candidate['table']
            record_id = candidate['record_id']
            task_id = candidate.get('task_id', candidate.get('stage_id', candidate.get('phase_id', '')))
            reasons = candidate['reasons']

            # Select the appropriate table
            if table_name == 'Tasks':
                table = tasks_table
            elif table_name == 'Stages':
                table = stages_table
            elif table_name == 'Phases':
                table = phases_table
            else:
                continue

            # Get current record
            record = table.get(record_id)
            existing_notes = record['fields'].get('notes', '')

            # Create cancellation note
            cancellation_note = create_cancellation_note(reasons)

            # Append to existing notes (new on top)
            if existing_notes:
                updated_notes = f"{cancellation_note}\n\n{existing_notes}"
            else:
                updated_notes = cancellation_note

            # Update record with new status and notes
            # Note: Status update will only work if field options have been updated
            try:
                table.update(record_id, {
                    'status': 'Cancelled',
                    'notes': updated_notes
                })
                print(f"  ✅ {task_id}: Cancelled - {reasons[0][:50]}...")
                cancelled_count += 1
            except Exception as e:
                if 'invalid multiple choice option' in str(e).lower() or 'insufficient permissions' in str(e).lower():
                    # Status field doesn't have Cancelled option yet, just update notes
                    table.update(record_id, {
                        'notes': updated_notes
                    })
                    print(f"  📝 {task_id}: Cancellation note added (status field needs manual update)")
                    cancelled_count += 1
                else:
                    raise e

        except Exception as e:
            print(f"  ❌ Failed to update {task_id}: {e}")

    return cancelled_count

def apply_restatements(results):
    """Apply restatement status to identified tasks"""
    tasks_table = base.table('Tasks')
    stages_table = base.table('Stages')
    phases_table = base.table('Phases')

    restated_count = 0

    print("\n🔀 APPLYING RESTATEMENTS...")
    print("-"*40)

    for candidate in results['restatement_candidates']:
        try:
            table_name = candidate['table']
            record_id = candidate['record_id']
            task_id = candidate.get('task_id', candidate.get('stage_id', candidate.get('phase_id', '')))
            restatements = candidate['restatements']

            # Select the appropriate table
            if table_name == 'Tasks':
                table = tasks_table
            elif table_name == 'Stages':
                table = stages_table
            elif table_name == 'Phases':
                table = phases_table
            else:
                continue

            # Get current record
            record = table.get(record_id)
            existing_notes = record['fields'].get('notes', '')

            # Create restatement note
            restatement_note = create_restatement_note(restatements)

            # Append to existing notes (new on top)
            if existing_notes:
                updated_notes = f"{restatement_note}\n\n{existing_notes}"
            else:
                updated_notes = restatement_note

            # Update record with new status and notes
            # Note: Status update will only work if field options have been updated
            try:
                table.update(record_id, {
                    'status': 'Restated',
                    'notes': updated_notes
                })
                print(f"  ✅ {task_id}: Restated - {restatements[0]['original'][:30]}...")
                restated_count += 1
            except Exception as e:
                if 'invalid multiple choice option' in str(e).lower() or 'insufficient permissions' in str(e).lower():
                    # Status field doesn't have Restated option yet, just update notes
                    table.update(record_id, {
                        'notes': updated_notes
                    })
                    print(f"  📝 {task_id}: Restatement note added (status field needs manual update)")
                    restated_count += 1
                else:
                    raise e

        except Exception as e:
            print(f"  ❌ Failed to update {task_id}: {e}")

    return restated_count

# Main execution
if __name__ == "__main__":
    print("\n🔄 APPLYING STATUS CHANGES FROM AUDIT")
    print("="*80)

    try:
        # Load audit results
        results = load_audit_results()
        print(f"📊 Loaded audit results from {results['timestamp']}")

        # Update status field options (manual instructions)
        update_status_field_options()

        # Apply changes
        print("\n📝 APPLYING CHANGES...")
        print("Note: If status field options haven't been updated yet,")
        print("only notes will be updated. Run this script again after")
        print("updating field options in AirTable.")

        # Apply cancellations
        cancelled = apply_cancellations(results)

        # Apply restatements
        restated = apply_restatements(results)

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("-"*40)
        print(f"Tasks cancelled: {cancelled}")
        print(f"Tasks restated: {restated}")
        print(f"Total changes: {cancelled + restated}")

        if cancelled + restated == 0:
            print("\n⚠️ No changes applied. This may be because:")
            print("1. Status field options need to be updated first")
            print("2. Tasks have already been updated")
            print("\nPlease update status field options in AirTable and run again.")
        else:
            print("\n✅ Status changes applied successfully!")
            print("All changes used append mode to preserve history.")

        # Next steps
        print("\n📌 NEXT STEPS:")
        print("1. If not done yet, manually update status field options in AirTable")
        print("2. Review the changes in AirTable")
        print("3. Check task notes for complete audit trail")
        print("4. Update any dependent tasks as needed")

    except FileNotFoundError:
        print("\n❌ Audit results not found. Please run:")
        print("  python3 /home/micha/bqx_ml_v3/scripts/audit_airtable_status_candidates.py")
        print("\nThen run this script again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error applying changes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)