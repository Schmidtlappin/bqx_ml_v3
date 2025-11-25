#!/usr/bin/env python3
"""
Test Phases table field names to ensure prompt compatibility.
"""

import json
from pyairtable import Api

def test_phases_fields():
    """Check what fields exist in the Phases table."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    phases_table = api.table(secrets['AIRTABLE_BASE_ID']['value'], 'Phases')

    print("=" * 70)
    print("PHASES TABLE FIELD ANALYSIS")
    print("=" * 70)

    # Get first phase as sample
    phases = phases_table.all()
    if not phases:
        print("No phases found!")
        return

    sample = phases[0]
    fields = sample['fields']

    print("\n📋 Available Fields in Phases Table:")
    print("-" * 50)

    # Expected fields for the prompt
    expected_fields = [
        'phase_id',
        'name',
        'description',
        'notes',
        'source',
        'status',
        'record_audit',
        'record_score'
    ]

    # Check each expected field
    for field_name in sorted(fields.keys()):
        value = fields[field_name]
        value_type = type(value).__name__

        if isinstance(value, str):
            preview = f"'{value[:50]}...'" if len(value) > 50 else f"'{value}'"
        elif isinstance(value, dict):
            preview = f"dict with keys: {list(value.keys())}"
        elif isinstance(value, list):
            preview = f"list with {len(value)} items"
        else:
            preview = str(value)

        status = "✓" if field_name in expected_fields else "?"
        print(f"  {status} {field_name:<20} ({value_type}): {preview}")

    print("\n🔍 Missing Expected Fields:")
    print("-" * 50)
    missing = [f for f in expected_fields if f not in fields]
    if missing:
        for field in missing:
            print(f"  ❌ {field}")
        print("\n⚠️ These missing fields might cause prompt errors!")
    else:
        print("  ✅ All expected fields present")

    print("\n📝 Prompt Field References:")
    print("-" * 50)
    print("The RATIONALIZED_phases_prompt.md references these fields:")
    print("  - {phase_id}")
    print("  - {name}")
    print("  - {description}")
    print("  - {notes}")
    print("  - {source}")
    print("  - {status}")
    print("\nMake sure all these fields exist in your Phases table.")

    print("\n💡 SOLUTION:")
    print("-" * 50)
    print("1. Go to AirTable → Phases table → record_audit field")
    print("2. Click 'Configure AI'")
    print("3. Copy lines 5-120 from docs/RATIONALIZED_phases_prompt.md")
    print("4. Paste into the prompt editor")
    print("5. Save and wait 10-30 minutes for AI rescoring")

if __name__ == "__main__":
    test_phases_fields()