#!/usr/bin/env python3
"""
Add source field to all Phases records to fix emptyDependency error.
"""

import json
from pyairtable import Api

def add_source_to_phases():
    """Add source field to all Phases records."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("ADDING SOURCE FIELD TO PHASES RECORDS")
    print("=" * 70)

    phases_table = api.table(base_id, 'Phases')
    all_phases = phases_table.all()

    print(f"\n📊 Found {len(all_phases)} phases to update")
    print("-" * 50)

    updated_count = 0
    error_count = 0

    for phase in all_phases:
        record_id = phase['id']
        fields = phase['fields']
        phase_id = fields.get('phase_id', 'Unknown')
        name = fields.get('name', 'Unknown')

        # Determine appropriate source based on phase
        if 'P01' in phase_id:
            source = 'docs/setup_and_auth.md'
        elif 'P02' in phase_id:
            source = 'docs/intelligence_architecture.md'
        elif 'P03' in phase_id:
            source = 'docs/technical_architecture.md'
        elif 'P04' in phase_id:
            source = 'docs/gcp_infrastructure.md'
        elif 'P05' in phase_id:
            source = 'docs/data_pipeline.md'
        elif 'P06' in phase_id:
            source = 'docs/bqx_paradigm.md'
        elif 'P07' in phase_id:
            source = 'docs/advanced_features.md'
        elif 'P08' in phase_id:
            source = 'docs/model_development.md'
        elif 'P09' in phase_id:
            source = 'docs/production_deployment.md'
        elif 'P10' in phase_id:
            source = 'docs/validation_testing.md'
        elif 'P11' in phase_id:
            source = 'docs/security_compliance.md'
        else:
            source = 'docs/bqxml_project.md'

        try:
            # Add source field
            phases_table.update(record_id, {'source': source})
            updated_count += 1
            print(f"  ✓ {phase_id}: {name[:40]}... → source: '{source}'")
        except Exception as e:
            error_count += 1
            print(f"  ✗ {phase_id}: Failed - {e}")

    print(f"\n📈 Results:")
    print(f"  Successfully updated: {updated_count} phases")
    print(f"  Failed: {error_count} phases")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Wait 5-10 minutes for AI agent to reprocess")
    print("2. Check if record_audit state changes from 'error' to 'generated'")
    print("3. Scores should appear in record_score field")
    print("4. Run comprehensive remediation for low scores")

if __name__ == "__main__":
    add_source_to_phases()