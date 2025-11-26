#!/usr/bin/env python3
"""
List all actual stages in AirTable to understand the current structure.
"""

import os
import json
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

def list_all_stages():
    """List all stages with their IDs and names."""
    print("=" * 80)
    print("ALL STAGES IN AIRTABLE")
    print("=" * 80)

    all_stages = stages_table.all()

    # Group by phase
    phases = {}
    for stage in all_stages:
        stage_id = stage['fields'].get('Stage ID', 'Unknown')
        stage_name = stage['fields'].get('Name', 'Unknown')
        description = stage['fields'].get('Description', '')[:100]  # First 100 chars

        # Extract phase from stage ID
        if '.' in stage_id:
            phase = '.'.join(stage_id.split('.')[:2])
        else:
            phase = 'Unknown'

        if phase not in phases:
            phases[phase] = []

        phases[phase].append({
            'id': stage_id,
            'name': stage_name,
            'description': description
        })

    # Sort and display
    for phase in sorted(phases.keys()):
        print(f"\n📁 Phase {phase}:")
        print("-" * 70)
        for stage in sorted(phases[phase], key=lambda x: x['id']):
            print(f"  {stage['id']}: {stage['name']}")
            if stage['description']:
                desc_preview = stage['description'][:60] + "..." if len(stage['description']) > 60 else stage['description']
                print(f"    └─ {desc_preview}")

    # Check for INTERVAL-CENTRIC related stages
    print("\n" + "=" * 80)
    print("INTERVAL-CENTRIC RELATED STAGES")
    print("=" * 80)

    interval_keywords = ["interval", "rows between", "lag", "bqx", "momentum", "derivative", "leakage", "validation"]
    found_interval = []

    for stage in all_stages:
        stage_id = stage['fields'].get('Stage ID', '')
        stage_name = stage['fields'].get('Name', '').lower()
        description = stage['fields'].get('Description', '').lower()
        notes = stage['fields'].get('Notes', '').lower()

        content = f"{stage_name} {description} {notes}"

        for keyword in interval_keywords:
            if keyword in content:
                found_interval.append({
                    'id': stage_id,
                    'name': stage['fields'].get('Name', ''),
                    'keyword': keyword
                })
                break

    if found_interval:
        print("\nStages with INTERVAL-CENTRIC keywords:")
        for stage in sorted(found_interval, key=lambda x: x['id']):
            print(f"  {stage['id']}: {stage['name']} (keyword: {stage['keyword']})")
    else:
        print("\n❌ No stages found with INTERVAL-CENTRIC keywords")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Stages: {len(all_stages)}")
    print(f"Total Phases: {len(phases)}")
    print(f"Stages with INTERVAL keywords: {len(found_interval)}")

    # Look for P06 and P07 stages specifically
    p06_stages = [s for s in all_stages if 'P06' in s['fields'].get('Stage ID', '')]
    p07_stages = [s for s in all_stages if 'P07' in s['fields'].get('Stage ID', '')]

    print(f"\nP06 Stages (Feature Engineering): {len(p06_stages)}")
    if p06_stages:
        for stage in sorted(p06_stages, key=lambda x: x['fields'].get('Stage ID')):
            print(f"  {stage['fields'].get('Stage ID')}: {stage['fields'].get('Name')}")

    print(f"\nP07 Stages (Model Training): {len(p07_stages)}")
    if p07_stages:
        for stage in sorted(p07_stages, key=lambda x: x['fields'].get('Stage ID')):
            print(f"  {stage['fields'].get('Stage ID')}: {stage['fields'].get('Name')}")

    return all_stages

if __name__ == "__main__":
    list_all_stages()