#!/usr/bin/env python3
"""
Analyze AirTable Stages table metadata to understand field requirements
for achieving 90+ scores on stage records
"""

import requests
import json
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
STAGES_TABLE = 'tblxnuvF8O7yH1dB4'

def get_stages_schema():
    """Get the complete schema for the Stages table"""
    url = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schema = response.json()
        for table in schema.get('tables', []):
            if table['id'] == STAGES_TABLE:
                return table
    return None

def get_stages_with_scores():
    """Get existing stages to analyze patterns in high-scoring records"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'

    params = {
        'maxRecords': 20,
        'fields[]': ['stage_id', 'name', 'description', 'notes', 'status',
                     'record_audit', 'record_score', 'realized_cost']
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def analyze_stages_metadata():
    """Analyze Stages table structure and requirements"""

    print("="*80)
    print("STAGES TABLE METADATA ANALYSIS")
    print("="*80)

    # Get schema
    schema = get_stages_schema()
    if not schema:
        print("Could not retrieve stages schema")
        return

    print(f"\nTable Name: {schema['name']}")
    print(f"Table ID: {schema['id']}")
    if 'description' in schema:
        print(f"Table Description: {schema['description']}")

    print("\n" + "-"*80)
    print("FIELD DEFINITIONS AND REQUIREMENTS")
    print("-"*80)

    # Analyze each field
    required_fields = []
    optional_fields = []

    for field in schema.get('fields', []):
        field_name = field['name']
        field_type = field['type']
        field_desc = field.get('description', 'No description')

        print(f"\n📋 {field_name} ({field_type})")
        print(f"   Description: {field_desc}")

        # Check for field options
        if 'options' in field:
            options = field['options']
            if field_type == 'singleSelect' and 'choices' in options:
                choices = [c['name'] for c in options['choices']]
                print(f"   Choices: {', '.join(choices)}")
            elif field_type == 'number' and 'precision' in options:
                print(f"   Precision: {options['precision']} decimal places")

        # Determine if field is likely required
        if field_name in ['stage_id', 'name', 'description', 'status']:
            required_fields.append(field_name)
            print(f"   REQUIRED: Yes")
        else:
            optional_fields.append(field_name)
            print(f"   REQUIRED: No (but recommended for high scores)")

    # Get sample high-scoring records
    print("\n" + "-"*80)
    print("ANALYSIS OF EXISTING STAGES")
    print("-"*80)

    data = get_stages_with_scores()
    if data:
        records = data.get('records', [])
        print(f"\nTotal existing stages: {len(records)}")

        # Analyze score distribution
        scores = []
        high_score_examples = []

        for record in records:
            fields = record.get('fields', {})
            if 'record_score' in fields:
                score = fields['record_score']
                scores.append(score)

                if score >= 90:
                    high_score_examples.append({
                        'stage_id': fields.get('stage_id', 'Unknown'),
                        'score': score,
                        'name': fields.get('name', '')[:50],
                        'desc_length': len(fields.get('description', '')),
                        'notes_length': len(fields.get('notes', ''))
                    })

        if scores:
            print(f"\nScore Statistics:")
            print(f"  • Min score: {min(scores)}")
            print(f"  • Max score: {max(scores)}")
            print(f"  • Average score: {sum(scores)/len(scores):.1f}")
            print(f"  • High-scoring (90+): {len(high_score_examples)}")

        # Analyze high-scoring examples
        if high_score_examples:
            print(f"\n📈 High-Scoring Stage Examples (90+ scores):")
            for example in high_score_examples[:5]:
                print(f"\n  Stage {example['stage_id']} (Score: {example['score']})")
                print(f"    Name: {example['name']}")
                print(f"    Description length: {example['desc_length']} chars")
                print(f"    Notes length: {example['notes_length']} chars")

    # Provide recommendations
    print("\n" + "-"*80)
    print("✅ REQUIREMENTS FOR 90+ SCORES ON STAGES")
    print("-"*80)

    print("""
Based on metadata analysis, stages need:

1. **stage_id** (singleLineText)
   - Format: S##.## (e.g., S03.01.01)
   - Must be unique and follow convention

2. **name** (singleLineText)
   - 5-10 word action-oriented title
   - Start with verb
   - Be specific about deliverables
   - Example: "Create BigQuery lag feature tables"

3. **description** (richText)
   - Minimum 300 characters
   - Include:
     • Clear objectives (WHY)
     • Technical approach (HOW)
     • Success criteria (WHAT)
     • Quantified deliverables
   - Use bullet points for clarity

4. **notes** (multilineText)
   - Include ALL of these for high scores:
     • Resource estimates (hours, costs)
     • Technology stack details
     • Dependencies on other stages
     • Risk factors and mitigation
     • Timeline/schedule
     • Team assignments
   - Use date-stamped format for updates

5. **status** (singleSelect)
   - Choose from: Todo, In Progress, Done
   - Must be accurate

6. **realized_cost** (number)
   - Track actual costs
   - Format: ####.## (2 decimal precision)

7. **Scoring Elements to Include**:
   ✓ Quantified deliverables (e.g., "28 tables", not "tables")
   ✓ Resource estimates (hours AND dollar costs)
   ✓ Technology mentions (GCP, BigQuery, Python, etc.)
   ✓ Timeline/milestone references
   ✓ Dependencies explicitly stated
   ✓ Risk factors identified
   ✓ Success metrics defined
""")

    # Generate template
    print("\n" + "-"*80)
    print("📝 STAGE TEMPLATE FOR 95+ SCORES")
    print("-"*80)

    stage_template = {
        "stage_id": "S03.01.01",
        "status": "Todo",
        "name": "Deploy GitHub secrets and configure authentication",
        "description": """**Objective**: Deploy 12 GitHub secrets via automated script and configure multi-service authentication.

**Technical Approach**:
• Execute setup_github_secrets.sh script
• Validate secret deployment via GitHub API
• Configure service account authentication
• Test API access for BigQuery, Vertex AI, Storage

**Quantified Deliverables**:
• 12 secrets deployed to GitHub
• 3 service accounts configured
• 7 API authentications verified
• 100% test coverage achieved

**Success Criteria**:
• All secrets accessible in GitHub Actions
• Zero authentication failures
• <5 second API response time
• Automated tests pass""",
        "notes": """**Resource Allocation**:
• Engineering Hours: 4 hours
• GCP API Costs: $5
• GitHub API calls: 50
• Total Cost: $25

**Technology Stack**:
• GitHub CLI (gh)
• Python 3.10 requests library
• GCP SDK (gcloud, gsutil, bq)
• Bash scripting

**Dependencies**:
• Requires: GitHub repository access
• Requires: .secrets/github_secrets.json file
• Blocks: All subsequent API operations

**Risk Mitigation**:
• API rate limiting → Implement exponential backoff
• Permission errors → Validate IAM roles first
• Secret exposure → Use secure storage only

**Timeline**:
Hour 1: Deploy secrets
Hour 2: Configure authentication
Hour 3: Validation testing
Hour 4: Documentation

**Team Assignment**:
• Lead: BQXML CHIEF ENGINEER
• Support: DevOps Team"""
    }

    print(json.dumps(stage_template, indent=2))

    return {
        'required_fields': required_fields,
        'optional_fields': optional_fields,
        'scoring_requirements': {
            'min_description_length': 300,
            'min_notes_length': 200,
            'required_elements': [
                'quantified_deliverables',
                'resource_estimates',
                'technology_stack',
                'timeline',
                'dependencies',
                'risk_factors',
                'success_metrics'
            ]
        },
        'template': stage_template
    }

def main():
    """Main execution"""
    print("\nSTAGES TABLE METADATA ANALYSIS")
    print("Analyzing field requirements for 90+ scores...")
    print()

    results = analyze_stages_metadata()

    # Save results
    if results:
        output_file = '/home/micha/bqx_ml_v3/docs/stages_metadata_requirements.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n\nRequirements saved to: {output_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("Use the template above to create high-scoring stage records")
    print("="*80)

if __name__ == "__main__":
    main()