#!/usr/bin/env python3
"""
Explore AirTable BQX-ML base structure
"""

import requests
import json
from typing import Dict, List, Any

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

# Set up headers
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def get_base_schema():
    """Get the schema of the base including all tables and fields"""
    url = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_table_records(table_id: str, max_records: int = 5):
    """Get sample records from a table"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'
    params = {'maxRecords': max_records}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting records from {table_id}: {response.status_code}")
        return None

def print_base_structure():
    """Print the complete structure of the AirTable base"""
    schema = get_base_schema()

    if not schema:
        print("Could not retrieve base schema")
        return

    print("=" * 80)
    print(f"AIRTABLE BASE: {BASE_ID}")
    print("=" * 80)

    tables = schema.get('tables', [])
    print(f"\nTotal Tables: {len(tables)}")
    print("-" * 80)

    for table in tables:
        print(f"\n📊 TABLE: {table['name']}")
        print(f"   ID: {table['id']}")
        if 'description' in table:
            print(f"   Description: {table['description']}")

        print(f"\n   Fields ({len(table.get('fields', []))}):")
        print("   " + "-" * 70)

        for field in table.get('fields', []):
            field_info = f"   • {field['name']}"
            field_info += f" ({field['type']})"

            if 'description' in field:
                field_info += f"\n     Description: {field['description']}"

            # Add field options if available
            if 'options' in field:
                options = field['options']
                if field['type'] == 'singleSelect' and 'choices' in options:
                    choices = [c['name'] for c in options['choices']]
                    field_info += f"\n     Choices: {', '.join(choices)}"
                elif field['type'] == 'multipleSelects' and 'choices' in options:
                    choices = [c['name'] for c in options['choices']]
                    field_info += f"\n     Choices: {', '.join(choices)}"
                elif field['type'] == 'number' and 'precision' in options:
                    field_info += f"\n     Precision: {options['precision']}"
                elif field['type'] == 'percent' and 'precision' in options:
                    field_info += f"\n     Precision: {options['precision']}"
                elif field['type'] == 'formula' and 'formula' in options:
                    field_info += f"\n     Formula: {options['formula']}"
                elif field['type'] == 'rollup':
                    field_info += f"\n     Rollup Function: {options.get('rollupFunction', 'N/A')}"

            print(field_info)

        # Get sample records
        print(f"\n   Sample Records:")
        records = get_table_records(table['id'], max_records=3)
        if records and 'records' in records:
            for i, record in enumerate(records['records'], 1):
                print(f"   Record {i}: {json.dumps(record.get('fields', {}), indent=6)[:200]}...")

        print("\n" + "=" * 80)

def save_schema_to_file():
    """Save the complete schema to a JSON file for reference"""
    schema = get_base_schema()

    if schema:
        output_file = '/home/micha/bqx_ml_v3/docs/airtable_schema.json'
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"\nSchema saved to: {output_file}")

        # Also save a formatted summary
        summary_file = '/home/micha/bqx_ml_v3/docs/airtable_structure_summary.md'
        with open(summary_file, 'w') as f:
            f.write("# AirTable BQX-ML Base Structure\n\n")
            f.write(f"**Base ID**: {BASE_ID}\n\n")

            for table in schema.get('tables', []):
                f.write(f"## Table: {table['name']}\n")
                f.write(f"**ID**: {table['id']}\n\n")

                if 'description' in table:
                    f.write(f"**Description**: {table['description']}\n\n")

                f.write("### Fields\n\n")
                f.write("| Field Name | Type | Description |\n")
                f.write("|------------|------|-------------|\n")

                for field in table.get('fields', []):
                    desc = field.get('description', '').replace('\n', ' ')
                    f.write(f"| {field['name']} | {field['type']} | {desc} |\n")

                f.write("\n---\n\n")

        print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    print_base_structure()
    save_schema_to_file()