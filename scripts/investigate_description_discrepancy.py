#!/usr/bin/env python3
"""
Investigate Description Field Discrepancy

The record_audit says "Description Status: Good (222 chars)" but the actual
description field only contains 1 character (newline).

This script:
1. Checks if this is a display issue vs actual data issue
2. Examines the raw API response
3. Checks if there's a different description field
4. Looks for description content in other fields
"""

import json
import requests
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']
TASKS_TABLE_ID = 'tblQ9VXdTgZiIR6H2'

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

def get_task_via_direct_api(record_id: str):
    """Get task using direct API call to see raw response"""

    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TASKS_TABLE_ID}/{record_id}'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def analyze_all_text_fields(fields: dict):
    """Check all fields for description-like content"""

    text_fields = {}

    for field_name, value in fields.items():
        if isinstance(value, str):
            length = len(value)

            # Look for fields with description-like content
            if 200 <= length <= 300:
                text_fields[field_name] = {
                    'length': length,
                    'sample': value[:100]
                }

    return text_fields

def main():
    print("="*70)
    print("INVESTIGATING DESCRIPTION FIELD DISCREPANCY")
    print("="*70)

    # Get task via pyairtable
    print("\n[1] Fetching via pyairtable API...")
    formula = "{task_id}='MP03.P07.S04.T01'"
    records = tasks_table.all(formula=formula)

    if not records:
        print("  ❌ Task not found!")
        return

    task = records[0]
    record_id = task['id']

    print(f"  ✓ Found: {record_id}")

    # Get via direct API
    print("\n[2] Fetching via direct REST API...")
    direct_response = get_task_via_direct_api(record_id)

    if direct_response:
        print("  ✓ Direct API response received")

        # Compare description fields
        pyairtable_desc = task['fields'].get('description', '')
        direct_desc = direct_response.get('fields', {}).get('description', '')

        print("\n" + "="*70)
        print("DESCRIPTION FIELD COMPARISON")
        print("="*70)

        print(f"\nPyAirtable API:")
        print(f"  Type: {type(pyairtable_desc).__name__}")
        print(f"  Length: {len(pyairtable_desc)} chars")
        print(f"  Value: {repr(pyairtable_desc)}")

        print(f"\nDirect REST API:")
        print(f"  Type: {type(direct_desc).__name__}")
        print(f"  Length: {len(direct_desc)} chars")
        print(f"  Value: {repr(direct_desc)}")

        if pyairtable_desc == direct_desc:
            print(f"\n  ✓ Both APIs return the same value")
            print(f"  → This confirms the description field truly contains only: {repr(pyairtable_desc)}")
        else:
            print(f"\n  ⚠️  APIs return different values!")
            print(f"  → This suggests an API inconsistency")

    # Check record_audit
    print("\n" + "="*70)
    print("RECORD_AUDIT ANALYSIS")
    print("="*70)

    record_audit = task['fields'].get('record_audit', {})

    if isinstance(record_audit, dict):
        audit_value = record_audit.get('value', '')
        audit_state = record_audit.get('state', '')
        is_stale = record_audit.get('isStale', False)

        print(f"\nAudit State: {audit_state}")
        print(f"Is Stale: {is_stale}")
        print(f"\nAudit Content:")
        print(audit_value)

        # Parse the audit
        if "222 chars" in audit_value:
            print(f"\n⚠️  DISCREPANCY FOUND:")
            print(f"  Audit claims: 222 characters")
            print(f"  Actual description: {len(task['fields'].get('description', ''))} character")
            print(f"\n  POSSIBLE EXPLANATIONS:")
            print(f"  1. The description was cleared AFTER the audit was generated")
            print(f"  2. The audit is reading from a different field")
            print(f"  3. The audit is stale/cached (but isStale={is_stale})")
            print(f"  4. The description was converted from richText and content was lost")

    # Check all fields for 222-char content
    print("\n" + "="*70)
    print("SEARCHING FOR 222-CHARACTER CONTENT")
    print("="*70)

    text_fields = analyze_all_text_fields(task['fields'])

    if text_fields:
        print(f"\nFound {len(text_fields)} fields with 200-300 characters:")
        for field_name, info in text_fields.items():
            print(f"\n  {field_name}:")
            print(f"    Length: {info['length']} chars")
            print(f"    Sample: {info['sample']}...")
    else:
        print("\n  No fields found with content around 222 characters")

    # Check raw JSON
    print("\n" + "="*70)
    print("RAW FIELD DATA")
    print("="*70)

    print("\nDirect API Response (description field only):")
    print(json.dumps(direct_response.get('fields', {}).get('description'), indent=2))

    # Check if there's a version history
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    print("""
Based on the analysis:

1. CONFIRMED: The description field contains only '\\n' (1 character)

2. ISSUE: record_audit claims "Description Status: Good (222 chars)"
   - This is incorrect/stale

3. FIELD TYPE: The schema shows the field is 'richText' type
   - Content is stored as plain string
   - This is normal for richText fields in Airtable

4. POSSIBLE CAUSES:
   a) Description was cleared after audit was run
   b) Conversion from richText to plain text lost content
   c) An update script may have overwritten the description
   d) The audit formula is reading a different/cached value

5. NEXT STEPS:
   a) Check if there's a backup of the original description
   b) Re-generate the description if needed
   c) Force re-run the record_audit to update it
   d) Check Airtable revision history if available
    """)

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
