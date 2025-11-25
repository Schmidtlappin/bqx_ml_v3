#!/usr/bin/env python3
"""
Simple check of phase scores in AirTable
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

def check_phase_scores():
    """Check scores for P03 phases"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PHASES_TABLE}'

    # Filter for P03 phases
    params = {
        'filterByFormula': 'FIND("P03", {phase_id}) > 0',
        'sort[0][field]': 'phase_id',
        'sort[0][direction]': 'asc'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])

        print("="*80)
        print("P03 PHASE SCORES")
        print("="*80)
        print(f"\nTotal P03 phases found: {len(records)}\n")

        low_scoring = []
        no_score = []
        high_scoring = []

        for record in records:
            fields = record.get('fields', {})
            phase_id = fields.get('phase_id', 'Unknown')
            name = fields.get('name', 'No name')
            score = fields.get('record_score')
            status = fields.get('status', 'Unknown')

            # Get audit info
            audit = fields.get('record_audit', {})
            if isinstance(audit, dict):
                audit_text = audit.get('value', '')[:200] if audit.get('value') else 'No audit'
            else:
                audit_text = str(audit)[:200] if audit else 'No audit'

            print(f"📊 {phase_id}: {name[:40]}")
            print(f"   Status: {status}")
            print(f"   Score: {score if score is not None else 'Not scored yet'}")

            if score is None:
                no_score.append((phase_id, name))
                print(f"   ⚠️ Not yet scored by AI auditor")
            elif score < 90:
                low_scoring.append((phase_id, name, score))
                print(f"   ❌ Below 90 - needs remediation")
                print(f"   Audit: {audit_text}...")
            else:
                high_scoring.append((phase_id, name, score))
                print(f"   ✅ Good score!")

            print()

        # Summary
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✅ High scoring (90+): {len(high_scoring)} phases")
        print(f"❌ Low scoring (<90): {len(low_scoring)} phases")
        print(f"⚠️ Not scored yet: {len(no_score)} phases")

        if low_scoring:
            print("\n🔧 PHASES NEEDING REMEDIATION:")
            for phase_id, name, score in low_scoring:
                print(f"  - {phase_id} (Score: {score}): {name[:50]}")

        if no_score:
            print("\n⏳ PHASES AWAITING AI SCORING:")
            for phase_id, name in no_score:
                print(f"  - {phase_id}: {name[:50]}")

        # Check if AI auditor needs time
        if no_score:
            print("\n💡 TIP: The AI auditor may need a few moments to score newly")
            print("   created/updated records. Check again in 1-2 minutes.")

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    check_phase_scores()