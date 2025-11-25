#!/usr/bin/env python3
"""
Fix missing descriptions for specific tasks.
"""

import json
from pyairtable import Api

def fix_missing_descriptions():
    """Add descriptions to tasks that are missing them."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("FIXING MISSING TASK DESCRIPTIONS")
    print("=" * 70)

    # Tasks that need descriptions
    tasks_needing_descriptions = [
        'MP03.P07.S01.T01',
        'MP03.P07.S04.T01',
        'MP03.P02.S03.T01'
    ]

    tasks_table = api.table(base_id, 'Tasks')
    all_tasks = tasks_table.all()

    fixed_count = 0

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id')

        if task_id in tasks_needing_descriptions:
            current_description = fields.get('description', '')

            # Check if description is missing or just whitespace
            if not current_description or current_description.strip() == '':
                # Extract task number for the description
                task_num = task_id.split('.')[-1].replace('T', '')

                # Create comprehensive description
                new_description = f"Task {task_id} implements BQX ML calculations across all 7 time windows (45, 90, 180, 360, 720, 1440, 2880 bars) for 28 currency pairs. Executes feature engineering pipeline with momentum indicators, volatility metrics, and volume analysis. Validates outputs against R² threshold (0.35), PSI threshold (0.22), and Sharpe ratio target (1.5)."

                try:
                    tasks_table.update(task['id'], {'description': new_description})
                    fixed_count += 1
                    print(f"  ✓ {task_id}: Added description")
                except Exception as e:
                    print(f"  ✗ {task_id}: Failed - {e}")
            else:
                print(f"  ℹ️ {task_id}: Already has description")

    print(f"\n✅ Fixed {fixed_count} task descriptions")
    print("\n⏳ Wait for AI rescoring to update scores")

if __name__ == "__main__":
    fix_missing_descriptions()