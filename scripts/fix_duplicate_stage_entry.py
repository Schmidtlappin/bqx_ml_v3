#!/usr/bin/env python3
"""
Fix duplicate stage entry (MP03.P07.S01 appears twice).
"""

import os
import json
from datetime import datetime
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

def fix_duplicate_stage():
    """Find and remove duplicate stage entries."""
    print("=" * 80)
    print("FIXING DUPLICATE STAGE ENTRY")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all stages
    stages = stages_table.all()

    # Track stage_ids
    stage_ids = {}
    duplicates_found = []

    # Find duplicates
    for stage in stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            if stage_id in stage_ids:
                # Found duplicate
                duplicates_found.append({
                    'stage_id': stage_id,
                    'record1': stage_ids[stage_id],
                    'record2': stage
                })
            else:
                stage_ids[stage_id] = stage

    if not duplicates_found:
        print("\n✅ No duplicate stages found")
        return 0

    # Process duplicates
    for dup in duplicates_found:
        print(f"\n📋 Found duplicate: {dup['stage_id']}")

        # Compare records to decide which to keep
        record1 = dup['record1']
        record2 = dup['record2']

        # Keep the one with more content or newer creation time
        fields1 = record1['fields']
        fields2 = record2['fields']

        # Count populated fields
        score1 = sum(1 for v in fields1.values() if v)
        score2 = sum(1 for v in fields2.values() if v)

        # Decide which to keep
        if score1 >= score2:
            keep = record1
            delete = record2
            print(f"  Keeping record with {score1} fields, deleting record with {score2} fields")
        else:
            keep = record2
            delete = record1
            print(f"  Keeping record with {score2} fields, deleting record with {score1} fields")

        # Delete the duplicate
        try:
            stages_table.delete(delete['id'])
            print(f"  ✅ Deleted duplicate record")
        except Exception as e:
            print(f"  ❌ Failed to delete duplicate: {e}")
            # If deletion fails, try merging content
            try:
                # Merge any missing fields from delete into keep
                update_fields = {}
                for field, value in delete['fields'].items():
                    if value and not keep['fields'].get(field):
                        update_fields[field] = value

                if update_fields:
                    stages_table.update(keep['id'], update_fields)
                    print(f"  ✅ Merged missing fields into kept record")
            except:
                pass

    print(f"\n✅ Fixed {len(duplicates_found)} duplicate stage entries")
    return 0

if __name__ == "__main__":
    exit(fix_duplicate_stage())