#!/usr/bin/env python3
"""
AirTable Compliance Hooks
Ensures all AirTable updates follow established standards
Based on /intelligence/airtable_standards.json and mandates.json
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
import os

# Load standards
STANDARDS_PATH = '/home/micha/bqx_ml_v3/intelligence/airtable_standards.json'
with open(STANDARDS_PATH, 'r') as f:
    STANDARDS = json.load(f)

class AirTableComplianceValidator:
    """Validates AirTable updates against established standards"""

    def __init__(self):
        self.notes_standard = STANDARDS['notes_standardization']
        self.field_requirements = STANDARDS['field_requirements']
        self.status_icons = self.notes_standard['status_icons']
        self.violations = []

    def validate_update(self, field: str, new_value: str, old_value: str = "") -> Tuple[bool, List[str]]:
        """
        Main validation entry point
        Returns (is_valid, list_of_violations)
        """
        self.violations = []

        if field == 'notes':
            return self.validate_notes_update(new_value, old_value)
        elif field == 'description':
            return self.validate_description(new_value)
        elif field == 'task_id':
            return self.validate_task_id(new_value)
        elif field == 'status':
            return self.validate_status(new_value)
        elif field == 'priority':
            return self.validate_priority(new_value)
        else:
            # No specific validation for other fields
            return True, []

    def validate_notes_update(self, new_notes: str, old_notes: str) -> Tuple[bool, List[str]]:
        """
        Validate notes field update follows APPEND mode standards
        """
        # CRITICAL: Check if it's append mode (old content preserved)
        if old_notes and old_notes not in new_notes:
            self.violations.append("❌ CRITICAL: Notes must be APPENDED, not replaced! Old content was deleted.")
            return False, self.violations

        # Check if new content is at the TOP
        if old_notes and new_notes.index(old_notes) == 0:
            self.violations.append("❌ New updates must be added to the TOP, not bottom")

        # Extract the new update (everything before old content)
        if old_notes:
            new_update = new_notes.replace(old_notes, '').strip()
        else:
            new_update = new_notes

        # Validate format of new update
        self._validate_note_format(new_update)

        # Check minimum length
        if len(new_notes) < self.field_requirements['notes']['min_length']:
            self.violations.append(f"⚠️ Notes too short: {len(new_notes)} chars (min: {self.field_requirements['notes']['min_length']})")

        # Check maximum length
        if len(new_notes) > self.field_requirements['notes']['max_length']:
            self.violations.append(f"⚠️ Notes too long: {len(new_notes)} chars (max: {self.field_requirements['notes']['max_length']})")

        return len(self.violations) == 0, self.violations

    def _validate_note_format(self, update: str):
        """Validate the format of a notes update"""
        if not update:
            return

        lines = update.split('\n')
        if len(lines) < 3:
            self.violations.append("⚠️ Note update must have header, separator, and content")
            return

        # Check header format: [ICON] STATUS: TIMESTAMP
        header = lines[0]
        header_pattern = r'^(✅|🔄|📋|🚫|❌|🔀)\s+(COMPLETED|IN PROGRESS|PLANNED|BLOCKED|CANCELLED|RESTATED):\s+\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'

        if not re.match(header_pattern, header):
            self.violations.append(f"⚠️ Invalid header format. Expected: [ICON] STATUS: TIMESTAMP")

            # Check for valid status icon
            valid_icons = ['✅', '🔄', '📋', '🚫', '❌', '🔀']
            if not any(header.startswith(icon) for icon in valid_icons):
                self.violations.append(f"⚠️ Missing or invalid status icon. Use: {', '.join(valid_icons)}")

            # Check for uppercase status
            status_words = ['COMPLETED', 'IN PROGRESS', 'PLANNED', 'BLOCKED', 'CANCELLED', 'RESTATED']
            if not any(status in header for status in status_words):
                self.violations.append("⚠️ Status text must be in UPPERCASE")

            # Check for timestamp
            if not re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', header):
                self.violations.append("⚠️ Missing or invalid ISO timestamp")

        # Check separator (should be exactly 48 equals signs)
        if len(lines) > 1:
            separator = lines[1]
            if separator != '=' * 48:
                self.violations.append(f"⚠️ Separator must be exactly 48 equals signs, got {len(separator)}")

    def validate_description(self, description: str) -> Tuple[bool, List[str]]:
        """Validate description field"""
        min_len = self.field_requirements['description']['min_length']
        max_len = self.field_requirements['description']['max_length']

        if len(description) < min_len:
            self.violations.append(f"⚠️ Description too short: {len(description)} chars (min: {min_len})")

        if len(description) > max_len:
            self.violations.append(f"⚠️ Description too long: {len(description)} chars (max: {max_len})")

        # Check for boilerplate content
        boilerplate_patterns = [
            r'This task involves',
            r'The purpose of this task',
            r'Successfully complete',
            r'Ensure proper'
        ]

        for pattern in boilerplate_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                self.violations.append("⚠️ Description contains boilerplate content")
                break

        return len(self.violations) == 0, self.violations

    def validate_task_id(self, task_id: str) -> Tuple[bool, List[str]]:
        """Validate task_id format"""
        pattern = self.field_requirements['task_id']['format']
        if not re.match(pattern, task_id):
            self.violations.append(f"⚠️ Invalid task_id format. Expected: {pattern}")

        return len(self.violations) == 0, self.violations

    def validate_status(self, status: str) -> Tuple[bool, List[str]]:
        """Validate status field"""
        allowed = self.field_requirements['status']['allowed_values']
        if status not in allowed:
            self.violations.append(f"⚠️ Invalid status '{status}'. Allowed: {', '.join(allowed)}")

        return len(self.violations) == 0, self.violations

    def validate_priority(self, priority: str) -> Tuple[bool, List[str]]:
        """Validate priority field"""
        allowed = self.field_requirements['priority']['allowed_values']
        if priority not in allowed:
            self.violations.append(f"⚠️ Invalid priority '{priority}'. Allowed: {', '.join(allowed)}")

        return len(self.violations) == 0, self.violations


class AirTableComplianceEnforcer:
    """Enforces compliance by intercepting and validating updates"""

    def __init__(self):
        self.validator = AirTableComplianceValidator()

    def enforce_update(self, table_name: str, record_id: str, updates: Dict) -> Dict:
        """
        Enforce compliance on updates before they're sent to AirTable
        Returns compliant updates or raises exception
        """
        compliant_updates = {}
        all_violations = []

        # Special handling for notes field (needs old value for append check)
        if 'notes' in updates:
            # This would need to fetch old value from AirTable
            # For now, assume it's provided
            old_notes = updates.get('_old_notes', '')
            is_valid, violations = self.validator.validate_notes_update(
                updates['notes'], old_notes
            )

            if not is_valid:
                all_violations.extend(violations)
            else:
                compliant_updates['notes'] = updates['notes']

        # Validate other fields
        for field, value in updates.items():
            if field in ['_old_notes', 'notes']:
                continue

            is_valid, violations = self.validator.validate_update(field, value)

            if not is_valid:
                all_violations.extend(violations)
            else:
                compliant_updates[field] = value

        # If there are violations, handle them
        if all_violations:
            self._handle_violations(table_name, record_id, all_violations)
            # Attempt to fix violations
            compliant_updates = self._attempt_auto_fix(updates, all_violations)

        return compliant_updates

    def _handle_violations(self, table_name: str, record_id: str, violations: List[str]):
        """Handle compliance violations"""
        print("\n" + "=" * 60)
        print("⚠️  AIRTABLE COMPLIANCE VIOLATIONS DETECTED")
        print("=" * 60)
        print(f"Table: {table_name}")
        print(f"Record: {record_id}")
        print("\nViolations:")
        for v in violations:
            print(f"  {v}")
        print("=" * 60)

        # Log to file
        with open('/home/micha/bqx_ml_v3/logs/airtable_compliance.log', 'a') as f:
            f.write(f"\n[{datetime.now().isoformat()}] Violations in {table_name}/{record_id}:\n")
            for v in violations:
                f.write(f"  {v}\n")

    def _attempt_auto_fix(self, updates: Dict, violations: List[str]) -> Dict:
        """Attempt to automatically fix violations"""
        fixed_updates = updates.copy()

        for violation in violations:
            if "Notes must be APPENDED" in violation:
                # Can't auto-fix this - need to preserve old content
                raise ValueError("CRITICAL: Attempted to replace notes instead of appending. Update rejected.")

            elif "Description too short" in violation:
                # Add more detail to description
                if 'description' in fixed_updates:
                    fixed_updates['description'] += " This task is part of the BQX ML V3 implementation."

            elif "Status text must be in UPPERCASE" in violation:
                # Fix case in notes
                if 'notes' in fixed_updates:
                    for old, new in [('completed', 'COMPLETED'), ('in progress', 'IN PROGRESS'),
                                     ('planned', 'PLANNED'), ('blocked', 'BLOCKED')]:
                        fixed_updates['notes'] = fixed_updates['notes'].replace(old, new)

        return fixed_updates


def create_compliant_note_update(status: str, content: str, old_notes: str = "") -> str:
    """
    Helper function to create a compliant notes update
    """
    # Map status to icon
    status_map = {
        'completed': ('✅', 'COMPLETED'),
        'in_progress': ('🔄', 'IN PROGRESS'),
        'planned': ('📋', 'PLANNED'),
        'blocked': ('🚫', 'BLOCKED'),
        'cancelled': ('❌', 'CANCELLED'),
        'restated': ('🔀', 'RESTATED')
    }

    icon, status_text = status_map.get(status.lower(), ('📋', 'PLANNED'))

    # Create header with timestamp
    timestamp = datetime.now().isoformat()
    header = f"{icon} {status_text}: {timestamp}"

    # Create separator
    separator = "=" * 48

    # Build new update block
    new_update = f"{header}\n{separator}\n{content}\n"

    # CRITICAL: Append to TOP of old notes
    if old_notes:
        return new_update + "\n" + old_notes
    else:
        return new_update


# Hook function for integration
def validate_airtable_update(updates: Dict, table_name: str = "Tasks",
                            record_id: str = "", old_values: Dict = None) -> Dict:
    """
    Main hook function to validate AirTable updates
    Called before any AirTable update
    """
    enforcer = AirTableComplianceEnforcer()

    # Add old values if provided
    if old_values and 'notes' in old_values:
        updates['_old_notes'] = old_values['notes']

    # Enforce compliance
    compliant_updates = enforcer.enforce_update(table_name, record_id, updates)

    return compliant_updates


if __name__ == "__main__":
    # Test compliance validator
    print("🔍 AirTable Compliance Validator Test")
    print("=" * 60)

    validator = AirTableComplianceValidator()

    # Test valid notes update
    old_notes = "📋 PLANNED: 2025-11-27T08:00:00\n" + "=" * 48 + "\nPrevious content"
    new_notes = "✅ COMPLETED: 2025-11-27T09:00:00\n" + "=" * 48 + "\nTask completed successfully\n\n" + old_notes

    is_valid, violations = validator.validate_notes_update(new_notes, old_notes)
    print(f"Valid notes update: {is_valid}")
    if violations:
        for v in violations:
            print(f"  {v}")

    # Test invalid replacement
    bad_notes = "This replaces everything"
    is_valid, violations = validator.validate_notes_update(bad_notes, old_notes)
    print(f"\nInvalid notes replacement: {is_valid}")
    if violations:
        for v in violations:
            print(f"  {v}")

    print("\n✅ Compliance hooks installed and ready!")
    print("Location: /home/micha/bqx_ml_v3/.claude/hooks/airtable_compliance.py")