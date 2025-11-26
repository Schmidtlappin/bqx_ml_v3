#!/usr/bin/env python3
"""
Remove ALL fake "REAL BUILD OUTCOME" text from notes field.
Keep only original task notes.
"""

import json
import time
from pyairtable import Api

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def main():
    print("="*80)
    print("🧹 REMOVING ALL FAKE BUILD OUTCOMES FROM NOTES")
    print("="*80)

    # Get all tasks
    tasks = tasks_table.all()
    cleaned_count = 0

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        notes = task['fields'].get('notes', '')

        # Check if notes contain any fake outcome markers
        fake_markers = [
            'REAL BUILD OUTCOME',
            'REAL EXECUTION OUTCOME',
            'EXECUTION OUTCOME',
            'Status: COMPLETED',
            'Build Engineer: Claude',
            'Implementation Type: REAL'
        ]

        has_fake_content = any(marker in notes for marker in fake_markers)

        if has_fake_content:
            # Extract only original content
            original_notes = ''

            # Look for the original content markers
            if 'Previous Content:' in notes:
                parts = notes.split('Previous Content:')
                if len(parts) > 1:
                    original_notes = parts[-1].strip()
            elif '---' in notes and 'OUTCOME' in notes:
                parts = notes.split('---')
                # Get the last part that doesn't contain outcome text
                for part in reversed(parts):
                    if not any(marker in part for marker in fake_markers):
                        original_notes = part.strip()
                        break

            # If we couldn't extract original, just clear the fake parts
            if not original_notes and has_fake_content:
                # Remove everything before "Previous Content:" or after outcome markers
                lines = notes.split('\n')
                clean_lines = []
                skip_mode = False

                for line in lines:
                    if any(marker in line for marker in fake_markers):
                        skip_mode = True
                    elif '---' in line:
                        skip_mode = False
                    elif not skip_mode:
                        clean_lines.append(line)

                original_notes = '\n'.join(clean_lines).strip()

            # Update the task with cleaned notes
            try:
                tasks_table.update(task['id'], {
                    'status': 'Todo',  # Reset to Todo
                    'notes': original_notes
                })
                cleaned_count += 1
                print(f"  ✅ Cleaned {task_id}")
            except Exception as e:
                print(f"  ❌ Failed to clean {task_id}: {e}")

            time.sleep(0.2)  # Rate limiting

    print(f"\n✅ Cleaned {cleaned_count} tasks")
    print("All fake build outcomes have been removed")
    print("Tasks are now in Todo status with original notes only")

if __name__ == "__main__":
    main()