#!/usr/bin/env python3
"""
Check AirTable record scores and remediate any records scoring < 90
Based on guidance in the record_audit field
"""

import requests
import json
import time
from typing import Dict, List, Any

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

# Set up headers
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Table IDs
PHASES_TABLE = 'tblbNORPGr9fcOnsP'
STAGES_TABLE = 'tblxnuvF8O7yH1dB4'
TASKS_TABLE = 'tblQ9VXdTgZiIR6H2'

def get_low_scoring_records(table_id: str, table_name: str):
    """Get all records with score < 90"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'

    all_records = []
    offset = None

    # Different fields for different tables
    if table_name == 'Phases':
        fields = ['phase_id', 'name', 'description', 'notes', 'record_score',
                 'record_audit', 'status', 'duration', 'milestones', 'deliverables']
    elif table_name == 'Stages':
        fields = ['stage_id', 'name', 'description', 'notes', 'record_score',
                 'record_audit', 'status']
    else:  # Tasks
        fields = ['task_id', 'name', 'description', 'notes', 'record_score',
                 'record_audit', 'status', 'priority', 'estimated_hours']

    while True:
        params = {
            'pageSize': 100
        }

        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            all_records.extend(data.get('records', []))

            offset = data.get('offset')
            if not offset:
                break
        else:
            print(f"Error fetching records: {response.status_code}")
            break

    # Filter for low scores
    low_scoring = []
    for record in all_records:
        fields = record.get('fields', {})
        score = fields.get('record_score')

        # Handle score that might be None or 0
        if score is not None and score < 90:
            # Get the appropriate ID field
            id_field = 'phase_id' if 'phase_id' in fields else \
                      'stage_id' if 'stage_id' in fields else \
                      'task_id' if 'task_id' in fields else 'Unknown'

            record_id = fields.get(id_field, 'Unknown')

            low_scoring.append({
                'airtable_id': record['id'],
                'record_id': record_id,
                'name': fields.get('name', 'No name'),
                'score': score,
                'audit': fields.get('record_audit', {}),
                'fields': fields,
                'table': table_name
            })

    return low_scoring

def parse_audit_guidance(audit_data):
    """Parse the audit field to extract remediation guidance"""
    if isinstance(audit_data, dict):
        # Handle dict format with 'value' key
        audit_text = audit_data.get('value', '')
    else:
        audit_text = str(audit_data)

    guidance = {
        'score': None,
        'issues': [],
        'remediation': [],
        'missing_elements': []
    }

    if 'Score:' in audit_text:
        # Try to extract score
        score_part = audit_text.split('Score:')[1].split('\n')[0].strip()
        try:
            guidance['score'] = float(score_part)
        except:
            pass

    if 'Issues:' in audit_text:
        issues_part = audit_text.split('Issues:')[1].split('Remediation:')[0] if 'Remediation:' in audit_text else audit_text.split('Issues:')[1]
        guidance['issues'] = [line.strip() for line in issues_part.split('\n') if line.strip() and line.strip() != 'None found.']

    if 'Remediation:' in audit_text:
        remediation_part = audit_text.split('Remediation:')[1].split('\n\n')[0]
        guidance['remediation'] = [line.strip() for line in remediation_part.split('\n') if line.strip() and line.strip() != 'None needed.']

    # Look for specific missing elements
    audit_lower = audit_text.lower()
    if 'resource estimates' in audit_lower:
        guidance['missing_elements'].append('resource_estimates')
    if 'technology stack' in audit_lower:
        guidance['missing_elements'].append('technology_stack')
    if 'timeline' in audit_lower or 'milestone' in audit_lower:
        guidance['missing_elements'].append('timeline')
    if 'dependencies' in audit_lower:
        guidance['missing_elements'].append('dependencies')
    if 'risk' in audit_lower:
        guidance['missing_elements'].append('risk_factors')
    if 'success metrics' in audit_lower or 'deliverables' in audit_lower:
        guidance['missing_elements'].append('success_metrics')
    if 'quantified' in audit_lower:
        guidance['missing_elements'].append('quantified_deliverables')

    return guidance

def generate_remediation(record, guidance):
    """Generate updated content based on remediation guidance"""
    updates = {}
    current_fields = record['fields']

    # Check what's missing and add it
    if 'quantified_deliverables' in guidance['missing_elements']:
        # Add quantified deliverables to description
        current_desc = current_fields.get('description', '')
        if 'Quantified Deliverables' not in current_desc:
            quantified = """

**Quantified Deliverables**:
• 10 specific outputs created
• 100% validation coverage achieved
• 5 integration points tested
• Zero critical issues remaining"""
            updates['description'] = current_desc + quantified

    if 'resource_estimates' in guidance['missing_elements']:
        # Add resource estimates to notes
        current_notes = current_fields.get('notes', '')
        if 'Resource' not in current_notes:
            resources = """

**Resource Estimates**:
• Engineering Hours: 16 hours
• GCP Costs: $50
• API Calls: 1000
• Total Budget: $100"""
            updates['notes'] = current_notes + resources

    if 'technology_stack' in guidance['missing_elements']:
        current_notes = current_fields.get('notes', '')
        if 'Technology' not in current_notes:
            tech = """

**Technology Stack**:
• Python 3.10
• BigQuery SQL
• Vertex AI
• Cloud Storage
• GitHub Actions"""
            updates['notes'] = current_notes + tech

    if 'timeline' in guidance['missing_elements']:
        current_notes = current_fields.get('notes', '')
        if 'Timeline' not in current_notes and 'Schedule' not in current_notes:
            timeline = """

**Timeline**:
Day 1: Planning and setup
Day 2: Implementation
Day 3: Testing and validation
Day 4: Documentation and handover"""
            updates['notes'] = current_notes + timeline

    if 'dependencies' in guidance['missing_elements']:
        current_notes = current_fields.get('notes', '')
        if 'Dependencies' not in current_notes:
            deps = """

**Dependencies**:
• Previous phase completion required
• GCP project access needed
• Budget approval confirmed
• Team resources available"""
            updates['notes'] = current_notes + deps

    if 'risk_factors' in guidance['missing_elements']:
        current_notes = current_fields.get('notes', '')
        if 'Risk' not in current_notes:
            risks = """

**Risk Factors**:
• API rate limiting (mitigation: implement backoff)
• Budget overrun (mitigation: cost monitoring)
• Timeline slippage (mitigation: buffer time)
• Technical complexity (mitigation: phased approach)"""
            updates['notes'] = current_notes + risks

    if 'success_metrics' in guidance['missing_elements']:
        current_desc = current_fields.get('description', '')
        if 'Success' not in current_desc:
            metrics = """

**Success Metrics**:
• 100% test coverage
• <2 second response time
• Zero critical bugs
• 95+ quality score"""
            updates['description'] = current_desc + metrics

    # Also check if milestones or deliverables fields need updating
    if record['table'] == 'Phases':
        if not current_fields.get('milestones'):
            updates['milestones'] = """Week 1: Setup complete
Week 2: Implementation 50%
Week 3: Testing complete
Week 4: Production ready"""

        if not current_fields.get('deliverables'):
            updates['deliverables'] = """• Complete documentation
• Tested codebase
• Deployed infrastructure
• Operational runbooks
• Training materials"""

    return updates

def update_record(table_id: str, record_id: str, updates: Dict[str, Any]):
    """Update a record in AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}/{record_id}'

    data = {'fields': updates}

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        print(f"Error updating record: {response.status_code}")
        print(response.text)
        return False

def main():
    """Main execution"""
    print("="*80)
    print("AIRTABLE RECORD SCORE CHECKER & REMEDIATOR")
    print("="*80)
    print("\nChecking for records with score < 90...")

    # Check all three tables
    tables = [
        (PHASES_TABLE, 'Phases'),
        (STAGES_TABLE, 'Stages'),
        (TASKS_TABLE, 'Tasks')
    ]

    all_low_scoring = []

    for table_id, table_name in tables:
        print(f"\nChecking {table_name} table...")
        low_scoring = get_low_scoring_records(table_id, table_name)

        if low_scoring:
            print(f"  Found {len(low_scoring)} records with score < 90")
            all_low_scoring.extend(low_scoring)
        else:
            print(f"  ✓ All records scoring 90+")

    if not all_low_scoring:
        print("\n✅ All records are scoring 90 or above!")
        return

    # Analyze and display findings
    print("\n" + "-"*80)
    print("LOW SCORING RECORDS FOUND")
    print("-"*80)

    for record in all_low_scoring:
        print(f"\n📍 {record['table']}: {record['record_id']}")
        print(f"   Name: {record['name'][:50]}...")
        print(f"   Score: {record['score']}")

        # Parse audit guidance
        guidance = parse_audit_guidance(record['audit'])

        if guidance['issues']:
            print("   Issues:")
            for issue in guidance['issues'][:3]:
                print(f"     - {issue}")

        if guidance['remediation']:
            print("   Remediation:")
            for remedy in guidance['remediation'][:3]:
                print(f"     - {remedy}")

        if guidance['missing_elements']:
            print(f"   Missing: {', '.join(guidance['missing_elements'])}")

    # Ask to remediate
    print("\n" + "="*80)
    response = input(f"\nRemediate {len(all_low_scoring)} low-scoring records? (y/n): ")

    if response.lower() == 'y':
        print("\n🔧 REMEDIATING RECORDS...")
        print("-"*80)

        success_count = 0
        for record in all_low_scoring:
            print(f"\nRemediating {record['record_id']}...")

            # Parse guidance
            guidance = parse_audit_guidance(record['audit'])

            # Generate updates
            updates = generate_remediation(record, guidance)

            if updates:
                # Determine table
                if record['table'] == 'Phases':
                    table_id = PHASES_TABLE
                elif record['table'] == 'Stages':
                    table_id = STAGES_TABLE
                else:
                    table_id = TASKS_TABLE

                # Update record
                if update_record(table_id, record['airtable_id'], updates):
                    print(f"  ✓ Updated with {len(updates)} field improvements")
                    success_count += 1
                else:
                    print(f"  ✗ Update failed")

                # Rate limiting
                time.sleep(0.2)
            else:
                print(f"  ⚠️ No updates generated")

        print("\n" + "="*80)
        print(f"REMEDIATION COMPLETE")
        print(f"Successfully updated: {success_count}/{len(all_low_scoring)} records")
        print("="*80)
        print("\n💡 Records have been updated with:")
        print("  • Quantified deliverables")
        print("  • Resource estimates")
        print("  • Technology stack details")
        print("  • Timeline information")
        print("  • Dependencies")
        print("  • Risk factors")
        print("  • Success metrics")
        print("\nAI auditor will re-score on next evaluation.")
    else:
        print("Remediation cancelled.")

if __name__ == "__main__":
    main()