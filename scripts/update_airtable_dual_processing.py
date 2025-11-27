#!/usr/bin/env python3
"""
Update AirTable with dual processing directive per user preference.
"""

import os
import sys
from pathlib import Path
from pyairtable import Api
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to load credentials from various locations
def load_credentials():
    env_paths = [
        Path('.env'),
        Path('../.env'),
        Path(os.path.expanduser('~/.env')),
        Path('/home/micha/bqx_ml_v3/.env'),
        Path('/home/micha/.env')
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                env_content = f.read()
                api_key = None
                base_id = None
                for line in env_content.split('\n'):
                    if 'AIRTABLE_API_KEY' in line:
                        api_key = line.split('=')[1].strip()
                    elif 'AIRTABLE_BASE_ID' in line:
                        base_id = line.split('=')[1].strip()
                if api_key and base_id:
                    return api_key, base_id

    # Try environment variables
    api_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    if api_key and base_id:
        return api_key, base_id

    raise FileNotFoundError("Could not find AirTable credentials in .env file or environment variables")

def update_airtable_with_dual_processing():
    """Update AirTable tasks with dual processing directive."""

    try:
        api_key, base_id = load_credentials()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False

    api = Api(api_key)
    table = api.table(base_id, 'Tasks')

    # Dual processing directive note
    dual_processing_note = """

📌 DUAL PROCESSING DIRECTIVE (2025-11-27 00:10):
Per USER preference, implement DUAL PROCESSING approach:
• Use BOTH IDX features (raw indexed values) AND BQX features (momentum percentages)
• Total 28 features instead of 14 (14 IDX + 14 BQX)
• Retrain EURUSD-45 with dual approach
• Compare performance: BQX-only (R²=0.4648) vs Dual (IDX+BQX)
• Apply dual processing to all 196 models

Implementation Requirements:
- Modify prepare_training_dataset.py to include IDX features
- Join idx and bqx tables to get both feature sets
- Target remains BQX (lead values for prediction window)
- Document performance difference in AirTable"""

    # Tasks that need dual processing directive
    target_tasks = [
        'MP03.P01.S01.T01',  # Prepare training dataset
        'MP03.P01.S01.T02',  # Develop model evaluation framework
        'MP03.P02.S01.T01',  # Design BQX feature engineering
        'MP03.P02.S01.T02',  # Implement BQX feature engineering
        'MP03.P03.S01.T01',  # Design feature engineering pipeline
        'MP03.P03.S01.T02',  # Implement feature engineering
        'MP03.P04.S01.T01',  # Design model training pipeline
        'MP03.P04.S01.T02',  # Implement model training
    ]

    # Get all records
    records = table.all()
    updates_made = 0
    tasks_already_updated = 0

    for record in records:
        fields = record.get('fields', {})
        task_id = fields.get('Task ID', '')

        if task_id in target_tasks:
            current_notes = fields.get('Notes', '')

            # Only update if dual processing not already mentioned
            if 'DUAL PROCESSING' not in current_notes.upper():
                try:
                    table.update(record['id'], {
                        'Notes': current_notes + dual_processing_note
                    })
                    updates_made += 1
                    print(f"✅ Updated {task_id} with dual processing directive")
                except Exception as e:
                    print(f"❌ Failed to update {task_id}: {e}")
            else:
                tasks_already_updated += 1
                print(f"ℹ️  {task_id} already has dual processing directive")

    # Summary
    print(f"\n📊 AIRTABLE UPDATE SUMMARY:")
    print(f"  Tasks updated with dual processing: {updates_made}")
    print(f"  Tasks already had dual processing: {tasks_already_updated}")
    print(f"  Timestamp: {datetime.now().isoformat()}")

    # Verify specific task
    for record in records:
        fields = record.get('fields', {})
        if fields.get('Task ID') == 'MP03.P01.S01.T01':
            notes = fields.get('Notes', '')
            status = fields.get('Status', 'Unknown')
            print(f"\n📌 MP03.P01.S01.T01 Verification:")
            print(f"  Status: {status}")
            if 'DUAL PROCESSING' in notes.upper():
                print(f"  Dual Processing: ✅ DIRECTIVE PRESENT")
            else:
                print(f"  Dual Processing: ❌ DIRECTIVE MISSING")
            break

    return updates_made > 0

if __name__ == "__main__":
    success = update_airtable_with_dual_processing()
    sys.exit(0 if success else 1)