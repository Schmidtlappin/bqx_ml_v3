#!/usr/bin/env python3
"""
Check stages in AirTable
"""

import requests
import json

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

def check_stages():
    """Check all stages in AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'

    # Filter for S03 stages
    params = {
        'filterByFormula': 'FIND("S03", {stage_id}) > 0',
        'sort[0][field]': 'stage_id',
        'sort[0][direction]': 'asc',
        'maxRecords': 100
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])

        print("="*80)
        print("STAGES IN AIRTABLE")
        print("="*80)
        print(f"\nTotal S03 stages found: {len(records)}\n")

        if records:
            for record in records:
                fields = record.get('fields', {})
                stage_id = fields.get('stage_id', 'Unknown')
                name = fields.get('name', 'No name')
                status = fields.get('status', 'Unknown')
                score = fields.get('record_score')

                print(f"📋 {stage_id}: {name[:50]}")
                print(f"   Status: {status}")
                if score:
                    print(f"   Score: {score}")
                print()
        else:
            print("No S03 stages found in AirTable")
            print("\nTrying to get ANY stages...")

            # Try without filter
            response = requests.get(url, headers=headers, params={'maxRecords': 10})
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"\nTotal stages in table: {len(records)}")
                if records:
                    print("\nFirst few stages:")
                    for record in records[:5]:
                        fields = record.get('fields', {})
                        stage_id = fields.get('stage_id', 'Unknown')
                        print(f"  - {stage_id}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_stages()