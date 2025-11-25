#!/usr/bin/env python3
"""
Fix empty source fields in Tasks table to resolve emptyDependency errors.
"""

import json
from pyairtable import Api

def fix_tasks_source_fields():
    """Populate empty source fields in Tasks table."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("FIXING EMPTY SOURCE FIELDS IN TASKS TABLE")
    print("=" * 70)

    table = api.table(base_id, 'Tasks')
    all_tasks = table.all()

    # Count and fix empty source fields
    empty_source_tasks = []
    for task in all_tasks:
        source = task['fields'].get('source')
        if not source:  # Empty, None, or missing
            empty_source_tasks.append(task)

    print(f"\n📊 Status:")
    print(f"  Total tasks: {len(all_tasks)}")
    print(f"  Tasks with empty source: {len(empty_source_tasks)}")

    if empty_source_tasks:
        print(f"\n🔧 Fixing {len(empty_source_tasks)} tasks...")
        print("-" * 50)

        updated_count = 0
        error_count = 0

        for task in empty_source_tasks:
            record_id = task['id']
            task_id = task['fields'].get('task_id', 'Unknown')

            # Determine appropriate source based on task_id pattern
            if task_id.startswith('MP03.P01'):
                default_source = 'scripts/setup_environment.py'
            elif task_id.startswith('MP03.P02'):
                default_source = 'scripts/create_intelligence_files.py'
            elif task_id.startswith('MP03.P03'):
                default_source = 'docs/technical_architecture.md'
            elif task_id.startswith('MP03.P04'):
                default_source = 'scripts/setup_gcp_infrastructure.py'
            elif task_id.startswith('MP03.P05'):
                default_source = 'scripts/data_pipeline.py'
            elif task_id.startswith('MP03.P06'):
                default_source = 'scripts/feature_engineering.py'
            elif task_id.startswith('MP03.P07'):
                default_source = 'scripts/advanced_features.py'
            elif task_id.startswith('MP03.P08'):
                default_source = 'scripts/model_training.py'
            elif task_id.startswith('MP03.P09'):
                default_source = 'scripts/deploy_production.py'
            elif task_id.startswith('MP03.P10'):
                default_source = 'scripts/validation_testing.py'
            elif task_id.startswith('MP03.P11'):
                default_source = 'scripts/security_compliance.py'
            else:
                default_source = 'scripts/bqxml_implementation.py'

            try:
                # Update source field
                table.update(record_id, {'source': default_source})
                updated_count += 1
                print(f"  ✓ {task_id}: source = '{default_source}'")
            except Exception as e:
                error_count += 1
                print(f"  ✗ {task_id}: Failed - {e}")

        print(f"\n📈 Results:")
        print(f"  Successfully updated: {updated_count} tasks")
        print(f"  Failed: {error_count} tasks")

    else:
        print("\n✅ All tasks already have source field populated!")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Wait 5-10 minutes for AI agent to reprocess")
    print("2. Check if record_audit state changes from 'error' to 'generated'")
    print("3. Scores should appear in record_score field")
    print()
    print("For Phases table:")
    print("- Deploy CORRECTED_phases_prompt.md (doesn't reference source)")
    print("- OR add source field to Phases table schema")

if __name__ == "__main__":
    fix_tasks_source_fields()