#!/usr/bin/env python3
"""
Add plan_link and phase_link to all stage records in AirTable
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

# Table IDs
PLANS_TABLE = 'tblTtBE4sEa5ibCHE'
PHASES_TABLE = 'tblbNORPGr9fcOnsP'
STAGES_TABLE = 'tblxnuvF8O7yH1dB4'

def get_plan_record_id():
    """Get the P03 plan record ID"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PLANS_TABLE}'
    params = {
        'filterByFormula': '{plan_id}="P03"',
        'maxRecords': 1
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        records = response.json().get('records', [])
        if records:
            return records[0]['id']
    return None

def get_phase_mappings():
    """Get phase_id to record_id mappings"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PHASES_TABLE}'
    params = {
        'filterByFormula': 'FIND("P03", {phase_id}) > 0',
        'fields[]': ['phase_id'],
        'maxRecords': 100
    }

    phase_map = {}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        records = response.json().get('records', [])
        for record in records:
            phase_id = record['fields'].get('phase_id')
            if phase_id:
                phase_map[phase_id] = record['id']

    return phase_map

def get_stages_needing_links():
    """Get all S03 stages that need link updates"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'
    params = {
        'filterByFormula': 'FIND("S03", {stage_id}) > 0',
        'fields[]': ['stage_id', 'name', 'plan_link', 'phase_link'],
        'maxRecords': 100
    }

    stages = []
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        records = response.json().get('records', [])
        for record in records:
            stage_id = record['fields'].get('stage_id', '')
            # Check if links are missing
            if not record['fields'].get('plan_link') or not record['fields'].get('phase_link'):
                stages.append({
                    'record_id': record['id'],
                    'stage_id': stage_id,
                    'name': record['fields'].get('name', ''),
                    'has_plan_link': bool(record['fields'].get('plan_link')),
                    'has_phase_link': bool(record['fields'].get('phase_link'))
                })

    return stages

def determine_phase_for_stage(stage_id):
    """Determine which phase a stage belongs to based on stage_id"""
    # Extract phase number from stage_id (e.g., S03.01.01 -> P03.01)
    if '.' in stage_id and len(stage_id.split('.')) >= 2:
        parts = stage_id.split('.')
        if parts[0] == 'S03':
            return f"P03.{parts[1]}"

    # Fallback mappings for non-standard stage IDs
    stage_phase_map = {
        'S03.01': 'P03.08',  # Baseline Model Training
        'S03.02': 'P03.08',  # Train-Validation-Test Split
        'S03.03': 'P03.08',  # Cross-Validation Strategy
        'S03.04': 'P03.08',  # Advanced Model Architectures
        'S03.05': 'P03.08',  # Hyperparameter Optimization
        'S03.06': 'P03.08',  # Ensemble Methods
        'S03.07': 'P03.08',  # Model Interpretability
        'S03.08': 'P03.08',  # Final Model Evaluation
        'S03.09': 'P03.09',  # Model Serialization and Registry
        'S03.10': 'P03.08',  # Multi-Window Target Selection Strategy
    }

    return stage_phase_map.get(stage_id, 'P03.01')  # Default to P03.01

def update_stage_links(stage, plan_id, phase_map):
    """Update a single stage with plan and phase links"""
    stage_id = stage['stage_id']
    phase_id = determine_phase_for_stage(stage_id)
    phase_record_id = phase_map.get(phase_id)

    if not phase_record_id:
        return f"No phase record found for {phase_id}"

    # Prepare update data
    update_data = {}
    if not stage['has_plan_link'] and plan_id:
        update_data['plan_link'] = [plan_id]
    if not stage['has_phase_link'] and phase_record_id:
        update_data['phase_link'] = [phase_record_id]

    if not update_data:
        return "Already has links"

    # Update the record
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}/{stage["record_id"]}'
    response = requests.patch(url, headers=headers, json={'fields': update_data})

    if response.status_code == 200:
        links_added = []
        if 'plan_link' in update_data:
            links_added.append('plan')
        if 'phase_link' in update_data:
            links_added.append(f'phase {phase_id}')
        return f"Added {', '.join(links_added)} links"
    else:
        return f"Error: {response.status_code} - {response.text[:100]}"

def main():
    """Main execution"""
    print("="*60)
    print("ADDING LINKS TO STAGE RECORDS")
    print("="*60)

    # Get plan ID
    print("\nFetching P03 plan record...")
    plan_id = get_plan_record_id()
    if not plan_id:
        print("❌ Could not find P03 plan record")
        return
    print(f"✅ Found plan record: {plan_id}")

    # Get phase mappings
    print("\nFetching phase records...")
    phase_map = get_phase_mappings()
    print(f"✅ Found {len(phase_map)} phase records")

    # Get stages needing updates
    print("\nFetching stages needing links...")
    stages = get_stages_needing_links()
    print(f"✅ Found {len(stages)} stages needing link updates")

    if not stages:
        print("\n✨ All stages already have proper links!")
        return

    print("\n" + "-"*60)
    print("UPDATING STAGE LINKS")
    print("-"*60)

    success_count = 0
    skip_count = 0
    error_count = 0

    for stage in stages:
        stage_id = stage['stage_id']
        print(f"\n{stage_id}: {stage['name'][:40]}...")

        result = update_stage_links(stage, plan_id, phase_map)

        if "Added" in result:
            print(f"  ✅ {result}")
            success_count += 1
        elif "Already" in result:
            print(f"  ⏭️ {result}")
            skip_count += 1
        else:
            print(f"  ❌ {result}")
            error_count += 1

        time.sleep(0.2)  # Rate limiting

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Updated: {success_count} stages")
    print(f"⏭️ Skipped: {skip_count} stages (already had links)")
    print(f"❌ Errors: {error_count} stages")
    print(f"📊 Total: {len(stages)} stages")
    print("="*60)

if __name__ == "__main__":
    main()