#!/usr/bin/env python3
"""
AirTable Compliance Enforcer Script
Integrates compliance hooks with all AirTable operations
Ensures all updates follow established standards
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import importlib.util

# Add paths for imports
sys.path.append('/home/micha/bqx_ml_v3')
sys.path.append('/home/micha/bqx_ml_v3/.claude/hooks')

# Import the compliance validator
spec = importlib.util.spec_from_file_location(
    "airtable_compliance",
    "/home/micha/bqx_ml_v3/.claude/hooks/airtable_compliance.py"
)
compliance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compliance_module)

from pyairtable import Api

class AirTableComplianceEnforcer:
    """Main compliance enforcer that wraps all AirTable operations"""

    def __init__(self):
        """Initialize with API key and compliance validator"""
        api_key = os.environ.get('AIRTABLE_API_KEY')
        if not api_key:
            print("⚠️ WARNING: AIRTABLE_API_KEY not set. Running in validation-only mode.")
            self.api = None
        else:
            self.api = Api(api_key)

        self.base_id = 'app3tpP9F3BrP1P7j'
        self.validator = compliance_module.AirTableComplianceValidator()
        self.enforcer = compliance_module.AirTableComplianceEnforcer()
        self.log_file = '/home/micha/bqx_ml_v3/logs/airtable_compliance.log'

    def update_task(self, task_id: str, updates: Dict, table_name: str = "Tasks") -> bool:
        """
        Update a task with compliance enforcement
        """
        print(f"\n{'='*60}")
        print(f"📋 COMPLIANCE CHECK: Updating {table_name}/{task_id}")
        print(f"{'='*60}")

        # If we have API access, fetch current values for append check
        old_values = {}
        if self.api:
            try:
                table = self.api.table(self.base_id, table_name)
                record = table.get(task_id)
                old_values = record.get('fields', {})
                print(f"✅ Fetched current values for compliance check")
            except Exception as e:
                print(f"⚠️ Could not fetch current values: {e}")

        # Run compliance enforcement
        compliant_updates = self.enforcer.enforce_update(
            table_name, task_id, {**updates, '_old_notes': old_values.get('notes', '')}
        )

        # Check if updates were modified
        if compliant_updates != updates:
            print("\n🔧 Updates were modified for compliance:")
            for field, value in compliant_updates.items():
                if field not in updates or updates[field] != value:
                    print(f"  • {field}: Modified for compliance")

        # Apply the updates if we have API access
        if self.api:
            try:
                table = self.api.table(self.base_id, table_name)
                table.update(task_id, compliant_updates)
                print(f"✅ Successfully updated {task_id} with compliant data")
                self.log_update(task_id, compliant_updates, "SUCCESS")
                return True
            except Exception as e:
                print(f"❌ Failed to update AirTable: {e}")
                self.log_update(task_id, compliant_updates, f"FAILED: {e}")
                return False
        else:
            print("⚠️ Running in validation-only mode (no API key)")
            self.log_update(task_id, compliant_updates, "VALIDATION_ONLY")
            return True

    def batch_update_tasks(self, updates: List[Dict]) -> Dict:
        """
        Batch update multiple tasks with compliance
        Returns summary of results
        """
        results = {
            'total': len(updates),
            'success': 0,
            'failed': 0,
            'modified': 0,
            'violations': []
        }

        for update in updates:
            task_id = update.get('id')
            fields = update.get('fields', {})

            if self.update_task(task_id, fields):
                results['success'] += 1
            else:
                results['failed'] += 1

        return results

    def create_compliant_note(self, status: str, content: str, old_notes: str = "") -> str:
        """
        Helper to create a compliant note update
        """
        return compliance_module.create_compliant_note_update(status, content, old_notes)

    def validate_all_fields(self, fields: Dict) -> tuple:
        """
        Validate all fields against standards
        Returns (is_valid, violations)
        """
        all_violations = []

        for field, value in fields.items():
            is_valid, violations = self.validator.validate_update(field, str(value))
            if not is_valid:
                all_violations.extend(violations)

        return len(all_violations) == 0, all_violations

    def log_update(self, task_id: str, updates: Dict, status: str):
        """Log all updates for audit trail"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        with open(self.log_file, 'a') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'task_id': task_id,
                'status': status,
                'updates': updates
            }
            f.write(json.dumps(log_entry) + '\n')

    def audit_existing_tasks(self, limit: int = 10) -> Dict:
        """
        Audit existing tasks for compliance
        """
        if not self.api:
            print("⚠️ Cannot audit without API key")
            return {}

        print(f"\n{'='*60}")
        print(f"🔍 AUDITING EXISTING TASKS FOR COMPLIANCE")
        print(f"{'='*60}")

        table = self.api.table(self.base_id, "Tasks")
        records = table.all(max_records=limit)

        audit_results = {
            'total': len(records),
            'compliant': 0,
            'non_compliant': 0,
            'issues': []
        }

        for record in records:
            task_id = record['id']
            fields = record['fields']
            task_name = fields.get('name', 'Unknown')

            print(f"\nChecking task: {task_name}")

            # Check notes field specifically
            notes = fields.get('notes', '')
            if notes:
                # Check if follows append format
                lines = notes.split('\n')
                if lines and not any(icon in lines[0] for icon in ['✅', '🔄', '📋', '🚫', '❌', '🔀']):
                    print(f"  ⚠️ Notes don't follow status icon format")
                    audit_results['non_compliant'] += 1
                    audit_results['issues'].append({
                        'task_id': task_id,
                        'task_name': task_name,
                        'issue': 'Notes missing status icon format'
                    })
                else:
                    print(f"  ✅ Notes appear compliant")
                    audit_results['compliant'] += 1
            else:
                print(f"  📝 No notes present")
                audit_results['compliant'] += 1

        print(f"\n{'='*60}")
        print(f"AUDIT SUMMARY:")
        print(f"  Total: {audit_results['total']}")
        print(f"  Compliant: {audit_results['compliant']}")
        print(f"  Non-compliant: {audit_results['non_compliant']}")
        print(f"{'='*60}")

        return audit_results


def main():
    """Main entry point for compliance enforcement"""
    enforcer = AirTableComplianceEnforcer()

    # Example: Create a compliant note update
    print("\n📝 Example: Creating compliant note update")
    compliant_note = enforcer.create_compliant_note(
        'completed',
        'Successfully implemented AirTable compliance hooks.\n' +
        'All updates now validated against standards.\n' +
        'APPEND mode enforced for all notes.',
        ''  # No old notes for this example
    )
    print(f"Generated note:\n{compliant_note}")

    # Example: Validate fields
    print("\n🔍 Example: Validating fields")
    test_fields = {
        'description': 'This task implements comprehensive AirTable compliance validation to ensure all updates follow established standards including APPEND mode for notes.',
        'status': 'In Progress',
        'priority': 'High'
    }

    is_valid, violations = enforcer.validate_all_fields(test_fields)
    if is_valid:
        print("✅ All fields are compliant!")
    else:
        print("⚠️ Compliance violations found:")
        for v in violations:
            print(f"  {v}")

    # If API key is available, audit some existing tasks
    if os.environ.get('AIRTABLE_API_KEY'):
        print("\n🔍 Auditing existing tasks...")
        audit_results = enforcer.audit_existing_tasks(limit=5)

        # Save audit results
        with open('/home/micha/bqx_ml_v3/intelligence/airtable_compliance_audit.json', 'w') as f:
            json.dump(audit_results, f, indent=2)
            print(f"✅ Audit results saved to intelligence/airtable_compliance_audit.json")
    else:
        print("\n⚠️ Skipping audit (no API key set)")
        print("To enable full functionality, set AIRTABLE_API_KEY environment variable")

    print("\n✅ Compliance enforcement system ready!")
    print("Location: /home/micha/bqx_ml_v3/scripts/airtable_compliance_enforcer.py")
    print("\nUsage:")
    print("  from scripts.airtable_compliance_enforcer import AirTableComplianceEnforcer")
    print("  enforcer = AirTableComplianceEnforcer()")
    print("  enforcer.update_task(task_id, updates)")


if __name__ == "__main__":
    main()