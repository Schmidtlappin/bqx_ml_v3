#!/usr/bin/env python3
"""
Test uploading a single stage to AirTable
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

def upload_test_stage():
    """Upload a single test stage"""

    # Test stage data
    stage_data = {
        "stage_id": "S03.01.01",
        "status": "Todo",
        "name": "Deploy GitHub secrets and configure repository",
        "description": """**Objective**: Deploy 12 GitHub secrets and configure repository authentication for all GCP services.

**Technical Approach**:
• Execute setup_github_secrets.sh deployment script
• Validate secret deployment via GitHub API
• Configure service account authentication
• Test API access for BigQuery, Vertex AI, Storage

**Quantified Deliverables**:
• 12 secrets deployed to GitHub repository
• 3 service accounts configured
• 7 API authentications verified
• 100% test coverage achieved

**Success Criteria**:
• All secrets accessible in GitHub Actions
• Zero authentication failures
• <5 second API response time""",
        "notes": """**Resource Allocation**:
• Engineering Hours: 4 hours
• Total Cost: $400

**Technology Stack**:
• GitHub CLI (gh)
• Python 3.10 requests
• GCP SDK (gcloud, gsutil, bq)
• Bash scripting

**Dependencies**:
• Requires: GitHub repository access
• Blocks: All subsequent API operations

**Risk Mitigation**:
• API rate limiting → Implement exponential backoff
• Permission errors → Validate IAM roles first

**Timeline**:
Hour 1-2: Deploy secrets
Hour 3: Configure authentication
Hour 4: Validation testing"""
    }

    print("="*60)
    print("UPLOADING TEST STAGE")
    print("="*60)
    print(f"Stage ID: {stage_data['stage_id']}")
    print(f"Stage Name: {stage_data['name']}")
    print("-"*60)

    # First check if it exists
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'
    check_params = {
        'filterByFormula': f'{{stage_id}}="{stage_data["stage_id"]}"',
        'maxRecords': 1
    }

    print("Checking if stage exists...")
    response = requests.get(url, headers=headers, params=check_params)

    if response.status_code == 200:
        records = response.json().get('records', [])
        if records:
            # Update existing
            print("Stage exists, updating...")
            record_id = records[0]['id']
            update_url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}/{record_id}'
            response = requests.patch(update_url, headers=headers, json={'fields': stage_data})

            if response.status_code == 200:
                print("✅ Successfully UPDATED stage")
                print(f"Record ID: {response.json()['id']}")
            else:
                print(f"❌ Failed to update: {response.status_code}")
                print(response.text)
        else:
            # Create new
            print("Stage doesn't exist, creating new...")
            response = requests.post(url, headers=headers, json={'fields': stage_data})

            if response.status_code == 200:
                print("✅ Successfully CREATED stage")
                print(f"Record ID: {response.json()['id']}")
            else:
                print(f"❌ Failed to create: {response.status_code}")
                print(response.text)
    else:
        print(f"❌ Failed to check: {response.status_code}")
        print(response.text)

    print("-"*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    upload_test_stage()