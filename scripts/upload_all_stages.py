#!/usr/bin/env python3
"""
Upload all stages to AirTable with proper error handling
"""

import requests
import json
import time

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

STAGES_TABLE = 'tblxnuvF8O7yH1dB4'

# Import stage creation function
import sys
sys.path.append('/home/micha/bqx_ml_v3/scripts')
from airtable_stage_loader_optimized import create_optimized_stage_records

def upload_stage(stage_data):
    """Upload a single stage with error handling"""

    # Remove phase_id field - it's not a field in AirTable
    upload_data = {k: v for k, v in stage_data.items() if k != 'phase_id'}

    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'

    # Check if exists
    params = {
        'filterByFormula': f'{{stage_id}}="{stage_data["stage_id"]}"',
        'maxRecords': 1
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Error checking: {response.status_code} - {response.text}"

    records = response.json().get('records', [])

    if records:
        # Update existing
        record_id = records[0]['id']
        update_url = f'{url}/{record_id}'
        response = requests.patch(update_url, headers=headers, json={'fields': upload_data})

        if response.status_code == 200:
            return f"Updated"
        else:
            return f"Update error: {response.status_code} - {response.text}"
    else:
        # Create new
        response = requests.post(url, headers=headers, json={'fields': upload_data})

        if response.status_code == 200:
            return f"Created"
        else:
            return f"Create error: {response.status_code} - {response.text}"

def main():
    """Upload all stages"""
    stages = create_optimized_stage_records()

    print("="*60)
    print("UPLOADING STAGES TO AIRTABLE")
    print("="*60)
    print(f"Total stages to process: {len(stages)}\n")

    created_count = 0
    updated_count = 0
    error_count = 0

    for i, stage in enumerate(stages, 1):
        stage_id = stage['stage_id']
        print(f"[{i}/{len(stages)}] Processing {stage_id}...", end=" ")

        result = upload_stage(stage)

        if "Created" in result:
            print(f"✅ {result}")
            created_count += 1
        elif "Updated" in result:
            print(f"✅ {result}")
            updated_count += 1
        else:
            print(f"❌ {result}")
            error_count += 1

        time.sleep(0.2)  # Rate limiting

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Created: {created_count}")
    print(f"✅ Updated: {updated_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total: {len(stages)}")
    print("="*60)

if __name__ == "__main__":
    main()