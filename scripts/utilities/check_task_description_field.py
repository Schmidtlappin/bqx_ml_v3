#!/usr/bin/env python3
"""
Check Task Description Field Type and Content

This script fetches a specific task (MP03.P07.S04.T01) from AirTable
and examines its description field in detail:
1. Current content
2. Field type (richText vs plain text)
3. Special characters or formatting issues
4. Compare with other tasks for similar issues
"""

import json
import requests
from typing import Dict, Any, List
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

# Also use direct API for metadata
headers = {
    'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    'Content-Type': 'application/json'
}

def get_table_schema():
    """Get the schema to check field types"""
    url = f'https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schema = response.json()
        for table in schema.get('tables', []):
            if table['name'] == 'Tasks':
                return table
    return None

def analyze_description_field_schema(schema: Dict) -> Dict:
    """Extract description field details from schema"""

    if not schema or 'fields' not in schema:
        return None

    for field in schema['fields']:
        if field['name'] == 'description':
            return {
                'name': field['name'],
                'type': field['type'],
                'id': field.get('id'),
                'description': field.get('description', 'No description'),
                'options': field.get('options', {})
            }

    return None

def get_task_by_id(task_id: str) -> Dict:
    """Fetch a specific task by task_id"""

    # Use formula to filter by task_id
    formula = f"{{task_id}}='{task_id}'"

    records = tasks_table.all(formula=formula)

    if records:
        return records[0]
    return None

def analyze_description_content(description: Any) -> Dict:
    """Analyze the description field content in detail"""

    analysis = {
        'type': type(description).__name__,
        'is_none': description is None,
        'is_empty': False,
        'length': 0,
        'has_special_chars': False,
        'has_newlines': False,
        'has_markdown': False,
        'has_html': False,
        'sample': '',
        'special_chars': [],
        'encoding_issues': []
    }

    if description is None:
        return analysis

    # Handle dict with 'value' key (richText format)
    if isinstance(description, dict):
        analysis['is_dict'] = True
        analysis['dict_keys'] = list(description.keys())

        if 'value' in description:
            description_text = description['value']
            analysis['extracted_from'] = 'dict.value'
        else:
            description_text = str(description)
            analysis['extracted_from'] = 'dict_string'
    else:
        analysis['is_dict'] = False
        description_text = str(description)
        analysis['extracted_from'] = 'direct_string'

    # Analyze the text content
    if description_text:
        analysis['is_empty'] = len(description_text.strip()) == 0
        analysis['length'] = len(description_text)
        analysis['has_newlines'] = '\n' in description_text or '\r' in description_text

        # Check for markdown
        markdown_patterns = ['**', '##', '* ', '- ', '`', '[', ']', '```']
        analysis['has_markdown'] = any(p in description_text for p in markdown_patterns)

        # Check for HTML
        html_patterns = ['<p>', '<div>', '<br>', '<span>', '&nbsp;', '&lt;', '&gt;']
        analysis['has_html'] = any(p in description_text for p in html_patterns)

        # Check for special characters
        special_chars = []
        for char in description_text:
            if ord(char) > 127 or ord(char) < 32:
                if char not in ['\n', '\r', '\t']:
                    special_chars.append({
                        'char': char,
                        'ord': ord(char),
                        'hex': hex(ord(char))
                    })

        analysis['has_special_chars'] = len(special_chars) > 0
        analysis['special_chars'] = special_chars[:20]  # First 20

        # Get sample
        analysis['sample'] = description_text[:200] if len(description_text) > 200 else description_text
        analysis['sample_end'] = description_text[-100:] if len(description_text) > 100 else ''

        # Check for encoding issues
        try:
            description_text.encode('utf-8')
        except UnicodeEncodeError as e:
            analysis['encoding_issues'].append(str(e))

    return analysis

def find_similar_description_issues(all_tasks: List[Dict], target_length: int) -> Dict:
    """Find other tasks with similar description characteristics"""

    similar = {
        'same_length': [],
        'rich_text_format': [],
        'special_chars': [],
        'long_descriptions': []
    }

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        description = fields.get('description')

        if not description:
            continue

        # Check if dict (richText format)
        if isinstance(description, dict):
            similar['rich_text_format'].append({
                'task_id': task_id,
                'keys': list(description.keys())
            })

        # Get text content
        if isinstance(description, dict) and 'value' in description:
            desc_text = description['value']
        else:
            desc_text = str(description) if description else ''

        # Check length
        if desc_text:
            desc_len = len(desc_text)

            if abs(desc_len - target_length) <= 10:  # Within 10 chars
                similar['same_length'].append({
                    'task_id': task_id,
                    'length': desc_len
                })

            if desc_len > 250:
                similar['long_descriptions'].append({
                    'task_id': task_id,
                    'length': desc_len
                })

            # Check for special chars
            has_special = any(ord(c) > 127 or ord(c) < 32 for c in desc_text if c not in ['\n', '\r', '\t'])
            if has_special:
                similar['special_chars'].append({
                    'task_id': task_id,
                    'length': desc_len
                })

    return similar

def main():
    print("="*70)
    print("TASK DESCRIPTION FIELD ANALYSIS")
    print("="*70)
    print("\nTarget Task: MP03.P07.S04.T01")
    print("Expected: 286 character plain text description")
    print("="*70)

    # 1. Get table schema
    print("\n[1/4] Fetching table schema...")
    schema = get_table_schema()

    if schema:
        description_field = analyze_description_field_schema(schema)

        if description_field:
            print(f"\n✓ Description Field Metadata:")
            print(f"  Field Name: {description_field['name']}")
            print(f"  Field Type: {description_field['type']}")
            print(f"  Field ID: {description_field.get('id', 'N/A')}")
            print(f"  Description: {description_field.get('description', 'N/A')}")

            if description_field.get('options'):
                print(f"  Options: {json.dumps(description_field['options'], indent=4)}")
            else:
                print(f"  Options: None (plain text field)")
        else:
            print("  ⚠️  Could not find description field in schema")
    else:
        print("  ❌ Could not retrieve schema")

    # 2. Get the specific task
    print("\n[2/4] Fetching task MP03.P07.S04.T01...")
    task = get_task_by_id('MP03.P07.S04.T01')

    if not task:
        print("  ❌ Task not found!")
        return

    print(f"  ✓ Task found: {task['id']}")

    fields = task['fields']
    print(f"\n  Task Details:")
    print(f"    Name: {fields.get('name', 'N/A')}")
    print(f"    Status: {fields.get('status', 'N/A')}")
    print(f"    Record Score: {fields.get('record_score', 'N/A')}")

    # 3. Analyze description field
    print("\n[3/4] Analyzing description field content...")
    description = fields.get('description')

    analysis = analyze_description_content(description)

    print(f"\n  Description Content Analysis:")
    print(f"    Python Type: {analysis['type']}")
    print(f"    Is None: {analysis['is_none']}")
    print(f"    Is Empty: {analysis['is_empty']}")
    print(f"    Is Dict: {analysis.get('is_dict', False)}")

    if analysis.get('is_dict'):
        print(f"    Dict Keys: {analysis.get('dict_keys', [])}")
        print(f"    Extracted From: {analysis.get('extracted_from')}")

    print(f"    Length: {analysis['length']} characters")
    print(f"    Has Newlines: {analysis['has_newlines']}")
    print(f"    Has Markdown: {analysis['has_markdown']}")
    print(f"    Has HTML: {analysis['has_html']}")
    print(f"    Has Special Chars: {analysis['has_special_chars']}")

    if analysis['special_chars']:
        print(f"\n  Special Characters Found:")
        for sc in analysis['special_chars'][:10]:
            print(f"    - '{sc['char']}' (ord={sc['ord']}, hex={sc['hex']})")

        if len(analysis['special_chars']) > 10:
            print(f"    ... and {len(analysis['special_chars']) - 10} more")

    if analysis['encoding_issues']:
        print(f"\n  ⚠️  Encoding Issues:")
        for issue in analysis['encoding_issues']:
            print(f"    - {issue}")

    print(f"\n  Content Sample (first 200 chars):")
    print(f"    {repr(analysis['sample'])}")

    if analysis['sample_end']:
        print(f"\n  Content Sample (last 100 chars):")
        print(f"    {repr(analysis['sample_end'])}")

    print(f"\n  Full Description Content:")
    print("  " + "-"*66)
    if isinstance(description, dict):
        print(f"  {json.dumps(description, indent=4)}")
    else:
        print(f"  {description}")
    print("  " + "-"*66)

    # 4. Check for similar issues in other tasks
    print("\n[4/4] Checking for similar issues in other tasks...")

    all_tasks = tasks_table.all()
    print(f"  ✓ Fetched {len(all_tasks)} total tasks")

    similar = find_similar_description_issues(all_tasks, analysis['length'])

    print(f"\n  Similar Description Patterns:")
    print(f"    Tasks with richText format (dict): {len(similar['rich_text_format'])}")
    print(f"    Tasks with similar length (~{analysis['length']} chars): {len(similar['same_length'])}")
    print(f"    Tasks with special characters: {len(similar['special_chars'])}")
    print(f"    Tasks with long descriptions (>250 chars): {len(similar['long_descriptions'])}")

    if similar['rich_text_format']:
        print(f"\n  Tasks still using richText format:")
        for t in similar['rich_text_format'][:5]:
            print(f"    - {t['task_id']} (keys: {t['keys']})")
        if len(similar['rich_text_format']) > 5:
            print(f"    ... and {len(similar['rich_text_format']) - 5} more")

    if similar['same_length']:
        print(f"\n  Tasks with similar length:")
        for t in similar['same_length'][:5]:
            print(f"    - {t['task_id']} ({t['length']} chars)")
        if len(similar['same_length']) > 5:
            print(f"    ... and {len(similar['same_length']) - 5} more")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"\n✓ Task MP03.P07.S04.T01 Analysis Complete")
    print(f"\n  Description Field Type: {description_field['type'] if description_field else 'Unknown'}")
    print(f"  Content Type: {analysis['type']}")
    print(f"  Content Length: {analysis['length']} characters")

    if analysis.get('is_dict'):
        print(f"\n  ⚠️  ISSUE: Description is still in richText format (dict)")
        print(f"      Expected: Plain text string")
        print(f"      Actual: Dictionary with keys: {analysis.get('dict_keys', [])}")
    else:
        print(f"\n  ✓ Description is plain text (string)")

    if analysis['has_special_chars']:
        print(f"\n  ⚠️  WARNING: {len(analysis['special_chars'])} special characters found")
        print(f"      This may cause UI rendering issues")

    if similar['rich_text_format']:
        print(f"\n  ⚠️  INFO: {len(similar['rich_text_format'])} other tasks also have richText format")
        print(f"      These may need conversion as well")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
