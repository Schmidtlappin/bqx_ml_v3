#!/usr/bin/env python3
"""
Debug AirTable field names to understand the structure.
"""

import os
import json
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
stages_table = base.table('Stages')

def debug_fields():
    """Debug field names in the stages table."""
    print("=" * 80)
    print("DEBUG: AIRTABLE STAGES TABLE STRUCTURE")
    print("=" * 80)

    all_stages = stages_table.all()

    if not all_stages:
        print("❌ No stages found in table")
        return

    # Get first few records to examine fields
    print(f"\nTotal records: {len(all_stages)}")
    print("\nExamining first 3 records to understand field structure:")
    print("-" * 70)

    for i, stage in enumerate(all_stages[:3]):
        print(f"\n📋 Record {i+1}:")
        print(f"  Record ID: {stage.get('id', 'N/A')}")
        print(f"  Fields available: {list(stage.get('fields', {}).keys())}")

        fields = stage.get('fields', {})
        for field_name, field_value in fields.items():
            # Print field name and value (truncated if long)
            if isinstance(field_value, str):
                value_display = field_value[:50] + "..." if len(field_value) > 50 else field_value
            elif isinstance(field_value, list):
                value_display = f"[List with {len(field_value)} items]"
            else:
                value_display = str(field_value)[:50]

            print(f"    {field_name}: {value_display}")

    # Look for common field name patterns
    print("\n" + "=" * 80)
    print("FIELD NAME ANALYSIS")
    print("=" * 80)

    all_field_names = set()
    for stage in all_stages:
        all_field_names.update(stage.get('fields', {}).keys())

    print(f"\nAll unique field names found:")
    for field in sorted(all_field_names):
        print(f"  - {field}")

    # Look for ID-like fields
    print("\nPotential ID fields:")
    id_fields = [f for f in all_field_names if 'id' in f.lower() or 'ID' in f]
    for field in id_fields:
        print(f"  - {field}")

    # Look for name/title fields
    print("\nPotential name/title fields:")
    name_fields = [f for f in all_field_names if 'name' in f.lower() or 'title' in f.lower() or 'Name' in f]
    for field in name_fields:
        print(f"  - {field}")

    # Check for stages with "P06" or "P07" in any field
    print("\n" + "=" * 80)
    print("SEARCHING FOR P06/P07 STAGES")
    print("=" * 80)

    p06_found = []
    p07_found = []

    for stage in all_stages:
        fields = stage.get('fields', {})
        record_str = json.dumps(fields).lower()

        if 'p06' in record_str:
            # Find which field contains P06
            for field_name, field_value in fields.items():
                if isinstance(field_value, str) and 'P06' in field_value.upper():
                    p06_found.append({
                        'field': field_name,
                        'value': field_value,
                        'record_id': stage.get('id')
                    })
                    break

        if 'p07' in record_str:
            # Find which field contains P07
            for field_name, field_value in fields.items():
                if isinstance(field_value, str) and 'P07' in field_value.upper():
                    p07_found.append({
                        'field': field_name,
                        'value': field_value,
                        'record_id': stage.get('id')
                    })
                    break

    if p06_found:
        print(f"\n✅ Found {len(p06_found)} stages with P06:")
        for item in p06_found[:3]:  # Show first 3
            print(f"  Field: {item['field']}, Value: {item['value']}")
    else:
        print("\n❌ No stages found with P06")

    if p07_found:
        print(f"\n✅ Found {len(p07_found)} stages with P07:")
        for item in p07_found[:3]:  # Show first 3
            print(f"  Field: {item['field']}, Value: {item['value']}")
    else:
        print("\n❌ No stages found with P07")

if __name__ == "__main__":
    debug_fields()