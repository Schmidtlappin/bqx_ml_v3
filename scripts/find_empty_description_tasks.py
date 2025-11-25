#!/usr/bin/env python3
"""
Find Tasks with Empty or Nearly-Empty Descriptions

Check all tasks to find those with empty or minimal descriptions
but potentially good audit scores.
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

def main():
    print("="*70)
    print("FINDING TASKS WITH EMPTY/MINIMAL DESCRIPTIONS")
    print("="*70)

    print("\nFetching all tasks...")
    all_tasks = tasks_table.all()
    print(f"✓ Found {len(all_tasks)} total tasks")

    # Categorize tasks
    empty_desc = []
    minimal_desc = []  # < 10 chars
    short_desc = []    # 10-50 chars
    normal_desc = []   # 50+ chars

    audit_mismatch = []  # Audit claims good desc but actual is bad

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        description = fields.get('description', '')

        # Get description length
        if isinstance(description, dict) and 'value' in description:
            desc_text = description['value']
        else:
            desc_text = str(description) if description else ''

        desc_len = len(desc_text.strip())

        # Get audit info
        record_audit = fields.get('record_audit', {})
        record_score = fields.get('record_score', 0)

        if isinstance(record_audit, dict):
            audit_text = record_audit.get('value', '')
        else:
            audit_text = str(record_audit) if record_audit else ''

        # Categorize
        if desc_len == 0:
            empty_desc.append({
                'task_id': task_id,
                'name': fields.get('name', 'N/A')[:50],
                'score': record_score,
                'audit': audit_text[:100]
            })
        elif desc_len < 10:
            minimal_desc.append({
                'task_id': task_id,
                'name': fields.get('name', 'N/A')[:50],
                'length': desc_len,
                'content': repr(desc_text),
                'score': record_score,
                'audit': audit_text[:100]
            })
        elif desc_len < 50:
            short_desc.append({
                'task_id': task_id,
                'name': fields.get('name', 'N/A')[:50],
                'length': desc_len,
                'score': record_score
            })
        else:
            normal_desc.append({
                'task_id': task_id,
                'length': desc_len
            })

        # Check for audit mismatch (claims good desc but actual is bad)
        if desc_len < 50:
            # Look for "Good" in audit or score > 80
            if ('Good' in audit_text or record_score >= 80) and desc_len < 50:
                # Parse the audit for character count claim
                import re
                char_match = re.search(r'(\d+)\s*chars?', audit_text)

                if char_match:
                    claimed_chars = int(char_match.group(1))

                    if claimed_chars > 50 and desc_len < 50:
                        audit_mismatch.append({
                            'task_id': task_id,
                            'name': fields.get('name', 'N/A')[:50],
                            'actual_length': desc_len,
                            'claimed_length': claimed_chars,
                            'score': record_score,
                            'audit_snippet': audit_text[:150]
                        })

    # Print results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print(f"\nCategorization:")
    print(f"  Empty descriptions (0 chars): {len(empty_desc)}")
    print(f"  Minimal descriptions (1-9 chars): {len(minimal_desc)}")
    print(f"  Short descriptions (10-49 chars): {len(short_desc)}")
    print(f"  Normal descriptions (50+ chars): {len(normal_desc)}")

    print(f"\n  Audit mismatches (claims good but actual is bad): {len(audit_mismatch)}")

    # Show empty descriptions
    if empty_desc:
        print("\n" + "-"*70)
        print(f"EMPTY DESCRIPTIONS ({len(empty_desc)} tasks)")
        print("-"*70)

        for task in empty_desc[:10]:
            print(f"\n  {task['task_id']}")
            print(f"    Name: {task['name']}")
            print(f"    Score: {task['score']}")
            print(f"    Audit: {task['audit']}")

        if len(empty_desc) > 10:
            print(f"\n  ... and {len(empty_desc) - 10} more")

    # Show minimal descriptions
    if minimal_desc:
        print("\n" + "-"*70)
        print(f"MINIMAL DESCRIPTIONS ({len(minimal_desc)} tasks)")
        print("-"*70)

        for task in minimal_desc[:10]:
            print(f"\n  {task['task_id']}")
            print(f"    Name: {task['name']}")
            print(f"    Length: {task['length']} chars")
            print(f"    Content: {task['content']}")
            print(f"    Score: {task['score']}")

        if len(minimal_desc) > 10:
            print(f"\n  ... and {len(minimal_desc) - 10} more")

    # Show audit mismatches
    if audit_mismatch:
        print("\n" + "-"*70)
        print(f"AUDIT MISMATCHES ({len(audit_mismatch)} tasks)")
        print("-"*70)
        print("\nThese tasks have audits claiming good descriptions,")
        print("but the actual description field is empty or minimal.")
        print("-"*70)

        for task in audit_mismatch[:10]:
            print(f"\n  {task['task_id']}")
            print(f"    Name: {task['name']}")
            print(f"    Claimed: {task['claimed_length']} chars")
            print(f"    Actual: {task['actual_length']} chars")
            print(f"    Score: {task['score']}")
            print(f"    Audit: {task['audit_snippet']}")

        if len(audit_mismatch) > 10:
            print(f"\n  ... and {len(audit_mismatch) - 10} more")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    total_problematic = len(empty_desc) + len(minimal_desc) + len(short_desc)

    print(f"\nTotal tasks with problematic descriptions: {total_problematic}")
    print(f"  - Empty: {len(empty_desc)}")
    print(f"  - Minimal (1-9): {len(minimal_desc)}")
    print(f"  - Short (10-49): {len(short_desc)}")

    print(f"\nTasks with audit/reality mismatch: {len(audit_mismatch)}")

    if audit_mismatch:
        print("\n⚠️  CRITICAL FINDING:")
        print(f"  {len(audit_mismatch)} tasks have audit scores claiming good descriptions")
        print(f"  but their actual description field is empty or minimal.")
        print(f"\n  This suggests:")
        print(f"  1. Descriptions were cleared/lost AFTER audit was generated")
        print(f"  2. The audit formula is reading from wrong field/cache")
        print(f"  3. A conversion process lost data")

    print("\n" + "="*70)

    # Save results
    results = {
        'total_tasks': len(all_tasks),
        'empty_descriptions': len(empty_desc),
        'minimal_descriptions': len(minimal_desc),
        'short_descriptions': len(short_desc),
        'normal_descriptions': len(normal_desc),
        'audit_mismatches': len(audit_mismatch),
        'mismatch_details': audit_mismatch
    }

    output_file = '/home/micha/bqx_ml_v3/docs/empty_description_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    main()
