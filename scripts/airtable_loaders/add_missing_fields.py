#!/usr/bin/env python3
"""
Add missing 'source' field to Phases and Tasks tables to fix emptyDependency errors.
"""

import json
from pyairtable import Api

def add_source_field():
    """Add source field with default values to fix QA agent errors."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("ADDING MISSING 'source' FIELD TO FIX QA AGENT ERRORS")
    print("=" * 70)

    # Tables that need the source field
    tables_to_fix = {
        'Phases': 'docs/bqxml_phases.json',
        'Tasks': 'scripts/generate_tasks.py'
    }

    for table_name, default_source in tables_to_fix.items():
        print(f"\n📋 Fixing {table_name} Table:")
        print("-" * 50)

        table = api.table(base_id, table_name)
        records = table.all()

        updated_count = 0
        error_count = 0

        for record in records:
            record_id = record['id']
            fields = record['fields']

            # Check if source field is missing or empty
            if 'source' not in fields or not fields.get('source'):
                identifier = fields.get(f'{table_name.lower()[:-1]}_id', 'Unknown')

                try:
                    # Add source field
                    table.update(record_id, {'source': default_source})
                    updated_count += 1
                    print(f"  ✓ Updated {identifier}: Added source = '{default_source}'")
                except Exception as e:
                    error_count += 1
                    print(f"  ✗ Failed {identifier}: {e}")

        print(f"\n  Summary for {table_name}:")
        print(f"    Updated: {updated_count} records")
        print(f"    Errors: {error_count} records")
        print(f"    Total: {len(records)} records")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Wait 2-3 minutes for changes to propagate")
    print("2. AI agent should automatically rerun")
    print("3. Check if record_audit state changes from 'error' to 'generated'")
    print("4. Scores should start appearing in record_score field")
    print()
    print("If errors persist:")
    print("- Check if 'record_score' field exists (might need to create it)")
    print("- Verify the AI prompt is properly configured")
    print("- Ensure all referenced fields in prompt exist in table")

if __name__ == "__main__":
    response = input("Add 'source' field to Phases and Tasks tables? (yes/no): ")
    if response.lower() == 'yes':
        add_source_field()
    else:
        print("Cancelled.")