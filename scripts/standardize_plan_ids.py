#!/usr/bin/env python3
"""
Standardize Plans.plan_id to MP## format

Converts:
- Plans.plan_id: P## → MP##

Also updates all references in:
- Intelligence files
- Documentation files
- Scripts
- AirTable field metadata
"""
import json
import os
import re
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
plans_table = api.table(AIRTABLE_BASE_ID, 'Plans')

# Track ID mappings
id_mappings = {}

def convert_plan_id(old_id):
    """Convert plan ID from P## to MP##"""
    match = re.match(r'P(\d{2})', old_id)
    if match:
        plan_num = match.group(1)
        return f"MP{plan_num}"
    return None

def update_plans_table():
    """Update all plan IDs in AirTable Plans table"""
    print("\n" + "="*70)
    print("UPDATING PLANS TABLE")
    print("="*70)

    all_plans = plans_table.all()

    for record in all_plans:
        record_id = record['id']
        old_id = record['fields'].get('plan_id', '')

        if not old_id:
            print(f"⚠️  Skipping record {record_id}: No plan_id found")
            continue

        # Check if already in new format
        if old_id.startswith('MP'):
            print(f"✓ Skipping {old_id}: Already in new format")
            continue

        new_id = convert_plan_id(old_id)

        if not new_id:
            print(f"❌ Error: Could not parse plan_id: {old_id}")
            continue

        print(f"\n📝 Converting Plan: {old_id} → {new_id}")

        try:
            plans_table.update(record_id, {'plan_id': new_id})
            print(f"✅ Updated record {record_id}")
            id_mappings[old_id] = new_id
        except Exception as e:
            print(f"❌ Error updating {old_id}: {e}")

    return id_mappings

def update_intelligence_files(mappings):
    """Update plan ID references in intelligence files"""
    print("\n" + "="*70)
    print("UPDATING INTELLIGENCE FILES")
    print("="*70)

    intelligence_dir = 'intelligence'
    files_to_update = [
        'context.json',
        'metadata.json',
        'ontology.json',
        'workflows.json'
    ]

    for filename in files_to_update:
        filepath = os.path.join(intelligence_dir, filename)

        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n📝 Updating {filename}...")

        with open(filepath, 'r') as f:
            content = f.read()

        original_content = content
        changes = 0

        # Replace all occurrences of old IDs with new IDs
        for old_id, new_id in mappings.items():
            # Match variations: "P01", 'P01', P01 (without quotes)
            patterns = [
                (f'"{old_id}"', f'"{new_id}"'),
                (f"'{old_id}'", f"'{new_id}'"),
                (f' {old_id} ', f' {new_id} '),  # Standalone with spaces
                (f':{old_id},', f':{new_id},'),  # After colon
                (f'({old_id})', f'({new_id})'),  # In parentheses
            ]

            for old_pattern, new_pattern in patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += 1

        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Updated {filename} ({changes} replacements)")
        else:
            print(f"✓ No changes needed for {filename}")

def update_documentation_files(mappings):
    """Update plan ID references in documentation files"""
    print("\n" + "="*70)
    print("UPDATING DOCUMENTATION FILES")
    print("="*70)

    docs_dir = 'docs'

    if not os.path.exists(docs_dir):
        print(f"⚠️  Directory not found: {docs_dir}")
        return

    # Get all markdown files
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    total_updated = 0

    for filepath in md_files:
        with open(filepath, 'r') as f:
            content = f.read()

        original_content = content

        # Replace all occurrences
        for old_id, new_id in mappings.items():
            # Match various contexts: Plan P01, (P01), "P01", etc.
            patterns = [
                (f'Plan {old_id}', f'Plan {new_id}'),
                (f'plan {old_id}', f'plan {new_id}'),
                (f'"{old_id}"', f'"{new_id}"'),
                (f"'{old_id}'", f"'{new_id}'"),
                (f'`{old_id}`', f'`{new_id}`'),
                (f'({old_id})', f'({new_id})'),
                (f' {old_id} ', f' {new_id} '),
                (f' {old_id}.', f' {new_id}.'),
                (f' {old_id},', f' {new_id},'),
            ]

            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)

        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Updated {os.path.relpath(filepath)}")
            total_updated += 1

    print(f"\nTotal documentation files updated: {total_updated}")

def update_readme_files(mappings):
    """Update plan ID references in README files"""
    print("\n" + "="*70)
    print("UPDATING README FILES")
    print("="*70)

    readme_files = ['README.md', 'intelligence/README.md']

    for filepath in readme_files:
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue

        print(f"\n📝 Updating {filepath}...")

        with open(filepath, 'r') as f:
            content = f.read()

        original_content = content

        for old_id, new_id in mappings.items():
            patterns = [
                (f'Plan {old_id}', f'Plan {new_id}'),
                (f'plan {old_id}', f'plan {new_id}'),
                (f'**{old_id}**', f'**{new_id}**'),
                (f'`{old_id}`', f'`{new_id}`'),
                (f' {old_id} ', f' {new_id} '),
                (f' {old_id}:', f' {new_id}:'),
            ]

            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)

        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Updated {filepath}")
        else:
            print(f"✓ No changes needed for {filepath}")

def save_mappings(mappings):
    """Save ID mappings to JSON file for reference"""
    mapping_file = 'plan_id_mappings.json'

    with open(mapping_file, 'w') as f:
        json.dump({
            'plan_ids': mappings,
            'format': 'P## → MP##',
            'date': '2025-11-25'
        }, f, indent=2)

    print(f"\n💾 ID mappings saved to: {mapping_file}")

def main():
    print("🔄 Plan ID Standardization Script")
    print("="*70)
    print("\nThis script will convert all plan IDs to the standardized format:")
    print("  Plans: P## → MP##")
    print("\nAnd update all references in:")
    print("  - AirTable Plans table")
    print("  - Intelligence files (JSON)")
    print("  - Documentation files (Markdown)")
    print("  - README files")
    print("\n" + "="*70)

    # Update AirTable
    mappings = update_plans_table()

    if not mappings:
        print("\n⚠️  No plan IDs to update")
        return

    print(f"\n✓ Updated {len(mappings)} plan IDs in AirTable")
    print("\nID Mappings:")
    for old_id, new_id in mappings.items():
        print(f"  {old_id} → {new_id}")

    # Update intelligence files
    update_intelligence_files(mappings)

    # Update documentation
    update_documentation_files(mappings)

    # Update README files
    update_readme_files(mappings)

    # Save mappings
    save_mappings(mappings)

    print("\n" + "="*70)
    print("✅ Plan ID standardization complete!")
    print("="*70)
    print("\n📋 Summary:")
    print(f"   Plans updated: {len(mappings)}")
    print(f"   Format: P## → MP##")
    print("\n📝 Next Steps:")
    print("   1. Verify intelligence files are updated correctly")
    print("   2. Review documentation changes")
    print("   3. Update AirTable field metadata description for plan_id")
    print("   4. Commit changes to git")

if __name__ == '__main__':
    main()
