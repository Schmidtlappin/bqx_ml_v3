#!/usr/bin/env python3
"""
Add plan_link and phase_link to ALL stages in AirTable
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

def get_all_phase_mappings():
    """Get ALL phase_id to record_id mappings"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PHASES_TABLE}'

    all_phases = {}
    offset = None

    while True:
        params = {
            'filterByFormula': 'FIND("P03", {phase_id}) > 0',
            'fields[]': ['phase_id'],
            'pageSize': 100
        }

        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])

            for record in records:
                phase_id = record['fields'].get('phase_id')
                if phase_id:
                    all_phases[phase_id] = record['id']

            # Check for more pages
            offset = data.get('offset')
            if not offset:
                break
        else:
            break

    return all_phases

def get_all_stages():
    """Get ALL stages that need link updates"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'

    all_stages = []
    offset = None

    while True:
        params = {
            'filterByFormula': 'FIND("S03", {stage_id}) > 0',
            'fields[]': ['stage_id', 'name', 'plan_link', 'phase_link'],
            'pageSize': 100
        }

        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])

            for record in records:
                stage_id = record['fields'].get('stage_id', '')
                # Include all stages, even those that might already have links
                all_stages.append({
                    'record_id': record['id'],
                    'stage_id': stage_id,
                    'name': record['fields'].get('name', ''),
                    'has_plan_link': bool(record['fields'].get('plan_link')),
                    'has_phase_link': bool(record['fields'].get('phase_link'))
                })

            # Check for more pages
            offset = data.get('offset')
            if not offset:
                break
        else:
            break

    return all_stages

def determine_phase_for_stage(stage_id):
    """Determine which phase a stage belongs to based on stage_id"""
    # Extract phase number from stage_id (e.g., S03.04.01 -> P03.04)
    if '.' in stage_id:
        parts = stage_id.split('.')
        if len(parts) >= 2 and parts[0] == 'S03':
            return f"P03.{parts[1]}"

    # Legacy stage mappings
    legacy_map = {
        'S03.01': 'P03.08',
        'S03.02': 'P03.08',
        'S03.03': 'P03.08',
        'S03.04': 'P03.08',
        'S03.05': 'P03.08',
        'S03.06': 'P03.08',
        'S03.07': 'P03.08',
        'S03.08': 'P03.08',
        'S03.09': 'P03.09',
        'S03.10': 'P03.08',
    }

    return legacy_map.get(stage_id, 'P03.01')

def update_stage_links(stage, plan_id, phase_map):
    """Update a single stage with plan and phase links"""
    stage_id = stage['stage_id']
    phase_id = determine_phase_for_stage(stage_id)
    phase_record_id = phase_map.get(phase_id)

    if not phase_record_id:
        return f"No phase record for {phase_id}"

    # Prepare update data
    update_data = {}
    if not stage['has_plan_link'] and plan_id:
        update_data['plan_link'] = [plan_id]
    if not stage['has_phase_link'] and phase_record_id:
        update_data['phase_link'] = [phase_record_id]

    if not update_data:
        return "Already linked"

    # Update the record
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}/{stage["record_id"]}'
    response = requests.patch(url, headers=headers, json={'fields': update_data})

    if response.status_code == 200:
        links_added = []
        if 'plan_link' in update_data:
            links_added.append('plan')
        if 'phase_link' in update_data:
            links_added.append(f'phase {phase_id}')
        return f"Added {', '.join(links_added)}"
    else:
        # Try to parse error for more details
        try:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            return f"Error: {error_msg}"
        except:
            return f"Error: {response.status_code}"

def main():
    print("="*80)
    print("ADDING LINKS TO ALL STAGES")
    print("="*80)

    # Get plan ID
    print("\nFetching P03 plan record...")
    plan_id = get_plan_record_id()
    if not plan_id:
        print("❌ Could not find P03 plan record")
        return
    print(f"✅ Found plan record: {plan_id}")

    # Get all phase mappings
    print("\nFetching all phase records...")
    phase_map = get_all_phase_mappings()
    print(f"✅ Found {len(phase_map)} phase records")
    print("Phases found:", ', '.join(sorted(phase_map.keys())))

    # Get all stages
    print("\nFetching all stages...")
    stages = get_all_stages()
    print(f"✅ Found {len(stages)} total stages")

    # Filter stages needing updates
    stages_needing_links = [s for s in stages
                           if not s['has_plan_link'] or not s['has_phase_link']]

    print(f"\n📊 Stages needing link updates: {len(stages_needing_links)}")

    if not stages_needing_links:
        print("\n✨ All stages already have proper links!")
        return

    print("\n" + "-"*80)
    print("UPDATING STAGE LINKS")
    print("-"*80)

    success_count = 0
    skip_count = 0
    error_count = 0

    # Group by phase for better visibility
    phase_groups = {}
    for stage in stages_needing_links:
        phase_id = determine_phase_for_stage(stage['stage_id'])
        if phase_id not in phase_groups:
            phase_groups[phase_id] = []
        phase_groups[phase_id].append(stage)

    for phase_id in sorted(phase_groups.keys()):
        print(f"\n{phase_id}: {len(phase_groups[phase_id])} stages")

        for stage in phase_groups[phase_id]:
            stage_id = stage['stage_id']
            print(f"  {stage_id}: ", end="")

            result = update_stage_links(stage, plan_id, phase_map)

            if "Added" in result:
                print(f"✅ {result}")
                success_count += 1
            elif "Already" in result:
                print(f"⏭️ {result}")
                skip_count += 1
            else:
                print(f"❌ {result}")
                error_count += 1

            time.sleep(0.2)  # Rate limiting

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✅ Updated: {success_count} stages")
    print(f"⏭️ Skipped: {skip_count} stages")
    print(f"❌ Errors: {error_count} stages")
    print(f"📊 Total processed: {len(stages_needing_links)} stages")
    print("="*80)

if __name__ == "__main__":
    main()