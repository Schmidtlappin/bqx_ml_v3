#!/usr/bin/env python3
"""
Get detailed audit feedback for low-scoring phases
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

PHASES_TABLE = 'tblbNORPGr9fcOnsP'

def get_phase_audit_details(phase_ids):
    """Get detailed audit feedback for specific phases"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PHASES_TABLE}'

    # Build filter for specific phase IDs
    filter_parts = [f'{{phase_id}}="{pid}"' for pid in phase_ids]
    filter_formula = f'OR({",".join(filter_parts)})'

    params = {
        'filterByFormula': filter_formula,
        'fields[]': ['phase_id', 'name', 'record_score', 'record_audit', 'description', 'notes']
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])

        print("="*80)
        print("DETAILED AUDIT FEEDBACK FOR LOW-SCORING PHASES")
        print("="*80)

        remediation_actions = {}

        for record in records:
            fields = record.get('fields', {})
            phase_id = fields.get('phase_id', 'Unknown')
            name = fields.get('name', 'No name')
            score = fields.get('record_score')
            audit = fields.get('record_audit', {})

            print(f"\n📋 Phase {phase_id}: {name}")
            print(f"Current Score: {score}")
            print("-"*60)

            # Parse audit feedback
            if isinstance(audit, dict) and 'value' in audit:
                audit_text = audit['value']
            else:
                audit_text = str(audit) if audit else 'No audit feedback'

            print("\n🔍 AUDIT FEEDBACK:")
            print(audit_text)

            # Extract remediation points
            if "Areas for Improvement" in audit_text or "Recommendations" in audit_text:
                print("\n✅ REMEDIATION ACTIONS REQUIRED:")

                actions = []

                # Parse specific recommendations from audit
                if "quantified deliverables" in audit_text.lower():
                    actions.append("Add specific numbers to deliverables")
                if "resource allocation" in audit_text.lower():
                    actions.append("Include detailed resource estimates (hours and costs)")
                if "technology stack" in audit_text.lower():
                    actions.append("Specify exact technologies and tools")
                if "timeline" in audit_text.lower():
                    actions.append("Add detailed timeline/milestones")
                if "dependencies" in audit_text.lower():
                    actions.append("Clarify dependencies on other phases")
                if "risk" in audit_text.lower():
                    actions.append("Include risk assessment and mitigation")
                if "success metrics" in audit_text.lower():
                    actions.append("Define clear success criteria")

                for i, action in enumerate(actions, 1):
                    print(f"  {i}. {action}")

                remediation_actions[phase_id] = {
                    'record_id': record['id'],
                    'current_score': score,
                    'actions': actions,
                    'current_description': fields.get('description', ''),
                    'current_notes': fields.get('notes', '')
                }

            print("-"*60)

        return remediation_actions
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return {}

def main():
    """Get audit details for low-scoring phases"""
    # Phases that scored below 90
    low_scoring_phases = ["P03.02", "P03.03"]

    print(f"Fetching audit details for phases: {', '.join(low_scoring_phases)}")
    remediation_actions = get_phase_audit_details(low_scoring_phases)

    # Save remediation plan
    if remediation_actions:
        with open('/home/micha/bqx_ml_v3/docs/phase_remediation_plan.json', 'w') as f:
            json.dump(remediation_actions, f, indent=2)
        print(f"\n\n💾 Remediation plan saved to: /home/micha/bqx_ml_v3/docs/phase_remediation_plan.json")

    return remediation_actions

if __name__ == "__main__":
    main()