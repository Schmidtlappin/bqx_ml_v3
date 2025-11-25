#!/usr/bin/env python3
"""
Byte-Level Analysis of Description Field

Examine the exact byte composition of the description field
to understand precisely what is stored.
"""

import json
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

def analyze_bytes(text):
    """Analyze text at byte level"""

    print(f"  String representation: {repr(text)}")
    print(f"  Length: {len(text)} characters")
    print(f"  Is empty: {len(text) == 0}")
    print(f"  Is whitespace only: {text.strip() == ''}")

    if len(text) > 0:
        print(f"\n  Byte-by-byte analysis:")
        for i, char in enumerate(text):
            print(f"    [{i}] char='{char}' | ord={ord(char)} | hex={hex(ord(char))} | name={repr(char)}")

    print(f"\n  Encoding:")
    try:
        utf8_bytes = text.encode('utf-8')
        print(f"    UTF-8 bytes: {utf8_bytes}")
        print(f"    UTF-8 hex: {utf8_bytes.hex()}")
        print(f"    Byte length: {len(utf8_bytes)}")
    except Exception as e:
        print(f"    Error encoding: {e}")

def main():
    print("="*70)
    print("BYTE-LEVEL DESCRIPTION FIELD ANALYSIS")
    print("="*70)

    # Fetch task
    formula = "{task_id}='MP03.P07.S04.T01'"
    records = tasks_table.all(formula=formula)

    if not records:
        print("\nTask not found!")
        return

    task = records[0]
    description = task['fields'].get('description', '')

    print(f"\nTask: MP03.P07.S04.T01")
    print(f"Record ID: {task['id']}")
    print(f"Name: {task['fields'].get('name', 'N/A')}")

    print("\n" + "-"*70)
    print("DESCRIPTION FIELD - RAW DATA")
    print("-"*70)

    print(f"\nPython type: {type(description).__name__}")

    if isinstance(description, dict):
        print(f"Dictionary keys: {list(description.keys())}")

        if 'value' in description:
            print(f"\nAnalyzing dict['value']:")
            analyze_bytes(description['value'])
    else:
        print(f"\nAnalyzing string value:")
        analyze_bytes(description)

    print("\n" + "-"*70)
    print("COMPARISON WITH EXPECTED")
    print("-"*70)

    print(f"\nExpected (from audit): 222 characters")
    print(f"Actual: {len(description) if isinstance(description, str) else len(description.get('value', ''))} character(s)")

    print(f"\nWhat 222 characters of description SHOULD look like:")
    sample_desc = "Apply isotonic regression calibration to model predictions to ensure monotonicity and improve probability estimates. This post-processing step adjusts raw model outputs to be properly calibrated while maintaining rank order."
    print(f"  Length: {len(sample_desc)} characters")
    print(f"  Sample: {sample_desc}")

    print("\n" + "-"*70)
    print("DIAGNOSIS")
    print("-"*70)

    actual_len = len(description) if isinstance(description, str) else len(description.get('value', ''))

    if actual_len == 0:
        print("\n✓ Field is completely empty (no characters)")
    elif actual_len == 1:
        if description == '\n' or (isinstance(description, dict) and description.get('value') == '\n'):
            print("\n✓ Field contains only a newline character")
            print("  This is effectively empty (whitespace only)")
    elif actual_len < 50:
        print(f"\n⚠️  Field is very short ({actual_len} chars)")
        print("  Expected minimum: 50+ characters for a proper description")
    else:
        print(f"\n✓ Field has content ({actual_len} chars)")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
