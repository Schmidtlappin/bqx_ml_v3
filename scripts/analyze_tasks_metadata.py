#!/usr/bin/env python3
"""
Analyze AirTable Tasks table metadata to understand field requirements
for achieving 90+ scores on task records
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
TASKS_TABLE = 'tblQ9VXdTgZiIR6H2'

def get_tasks_schema():
    """Get the complete schema for the Tasks table"""
    url = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        schema = response.json()
        for table in schema.get('tables', []):
            if table['id'] == TASKS_TABLE:
                return table
    return None

def get_tasks_with_scores():
    """Get existing tasks to analyze patterns in high-scoring records"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TASKS_TABLE}'

    params = {
        'maxRecords': 20,
        'fields[]': ['task_id', 'name', 'description', 'notes', 'status', 'priority',
                     'estimated_hours', 'actual_hours', 'realized_cost',
                     'record_audit', 'record_score', 'artifacts', 'blockers']
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def analyze_tasks_metadata():
    """Analyze Tasks table structure and requirements"""

    print("="*80)
    print("TASKS TABLE METADATA ANALYSIS")
    print("="*80)

    # Get schema
    schema = get_tasks_schema()
    if not schema:
        print("Could not retrieve tasks schema")
        return

    print(f"\nTable Name: {schema['name']}")
    print(f"Table ID: {schema['id']}")
    if 'description' in schema:
        print(f"Table Description: {schema['description']}")

    print("\n" + "-"*80)
    print("FIELD DEFINITIONS AND REQUIREMENTS")
    print("-"*80)

    # Track critical fields for scoring
    critical_fields = []
    scoring_fields = []

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
            elif field_type == 'multipleSelects' and 'choices' in options:
                choices = [c['name'] for c in options['choices']] if options['choices'] else []
                if choices:
                    print(f"   Available tags: {', '.join(choices[:10])}...")

        # Identify critical fields
        if field_name in ['task_id', 'name', 'description', 'status', 'priority']:
            critical_fields.append(field_name)
            print(f"   📍 CRITICAL for basic completion")

        # Identify scoring impact fields
        if field_name in ['estimated_hours', 'artifacts', 'notes', 'blockers']:
            scoring_fields.append(field_name)
            print(f"   ⭐ IMPORTANT for high scores")

    # Get sample high-scoring records
    print("\n" + "-"*80)
    print("ANALYSIS OF EXISTING TASKS")
    print("-"*80)

    data = get_tasks_with_scores()
    if data:
        records = data.get('records', [])
        print(f"\nTotal existing tasks: {len(records)}")

        # Analyze patterns
        high_score_examples = []
        priority_distribution = {}
        status_distribution = {}

        for record in records:
            fields = record.get('fields', {})

            # Track priority distribution
            priority = fields.get('priority', 'Unknown')
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

            # Track status distribution
            status = fields.get('status', 'Unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1

            # Find high-scoring examples
            if 'record_score' in fields and fields['record_score'] >= 90:
                high_score_examples.append({
                    'task_id': fields.get('task_id', 'Unknown'),
                    'score': fields['record_score'],
                    'name': fields.get('name', '')[:50],
                    'has_hours': 'estimated_hours' in fields,
                    'has_artifacts': bool(fields.get('artifacts')),
                    'has_notes': bool(fields.get('notes')),
                    'desc_length': len(fields.get('description', ''))
                })

        print(f"\nPriority Distribution:")
        for priority, count in priority_distribution.items():
            print(f"  • {priority}: {count}")

        print(f"\nStatus Distribution:")
        for status, count in status_distribution.items():
            print(f"  • {status}: {count}")

        if high_score_examples:
            print(f"\n📈 High-Scoring Task Analysis (90+ scores):")
            print(f"Found {len(high_score_examples)} high-scoring tasks")

            for example in high_score_examples[:3]:
                print(f"\n  Task {example['task_id']} (Score: {example['score']})")
                print(f"    ✓ Has estimated hours: {example['has_hours']}")
                print(f"    ✓ Has artifacts: {example['has_artifacts']}")
                print(f"    ✓ Has notes: {example['has_notes']}")
                print(f"    ✓ Description length: {example['desc_length']} chars")

    # Provide comprehensive recommendations
    print("\n" + "-"*80)
    print("✅ REQUIREMENTS FOR 95+ SCORES ON TASKS")
    print("-"*80)

    print("""
CRITICAL FIELDS (Must Have):

1. **task_id** (T##.##.##)
   - Format: T03.01.01.01 (Plan.Phase.Stage.Task)
   - Must be unique and sequential

2. **name** (5-10 words)
   - Start with action verb
   - Be specific about deliverable
   - Example: "Deploy 12 GitHub secrets via automation"

3. **description** (300+ chars)
   Must include ALL:
   • **Objective**: Clear goal statement
   • **Technical Approach**: How you'll do it
   • **Deliverables**: Quantified outputs
   • **Success Criteria**: Measurable outcomes
   • **Dependencies**: What's needed first
   • **Validation**: How to verify completion

4. **status** (singleSelect)
   - Todo / In Progress / Done / Blocked

5. **priority** (singleSelect)
   - Critical / High / Medium / Low

SCORING ENHANCEMENT FIELDS (For 95+):

6. **estimated_hours** (number)
   - Realistic estimate including testing
   - Example: 4.0

7. **notes** (multilineText)
   Must include:
   • Resource breakdown (people, costs)
   • Technology specifics
   • Risk factors
   • Timeline
   • Implementation details

8. **artifacts** (multilineText)
   - List all outputs/deliverables
   - Example: "github_secrets.json, setup.sh, validation_report.md"

9. **blockers** (multilineText)
   - Current impediments if any
   - Include ticket numbers

10. **tags** (multipleSelects)
    - Add relevant tags for categorization
    - Helps with filtering and reporting
""")

    # Generate optimal task template
    print("\n" + "-"*80)
    print("📝 TASK TEMPLATE FOR 95+ SCORES")
    print("-"*80)

    task_template = {
        "task_id": "T03.01.01.01",
        "status": "Todo",
        "priority": "Critical",
        "name": "Execute GitHub secrets deployment script",
        "description": """**Objective**: Deploy all 12 GitHub secrets from .secrets/github_secrets.json to repository settings.

**Technical Approach**:
1. Load credentials from JSON file
2. Use GitHub CLI (gh) for deployment
3. Iterate through secrets with rate limiting
4. Validate each deployment via API

**Quantified Deliverables**:
• 12 secrets deployed
• Deployment log generated
• Validation report created

**Success Criteria**:
• 100% secrets accessible in Actions
• Zero deployment errors
• Validation tests pass
• <30 seconds total execution

**Dependencies**:
• GitHub CLI installed and authenticated
• .secrets/github_secrets.json exists
• Repository admin access confirmed

**Validation Method**:
• Run test workflow to verify secret access
• Check GitHub Settings UI for confirmation
• Execute API validation script""",
        "notes": """**Implementation Details**:
Script: .secrets/setup_github_secrets.sh
Language: Bash + GitHub CLI
API Calls: ~15 (with rate limiting)

**Resource Requirements**:
• Engineer: 2 hours
• GitHub API quota: 50 calls
• Cost: $10

**Risk Factors**:
• API rate limiting (mitigation: exponential backoff)
• Permission errors (mitigation: pre-validate access)
• Network failures (mitigation: retry logic)

**Timeline**:
Minute 0-15: Script preparation
Minute 15-30: Execution
Minute 30-45: Validation
Minute 45-60: Documentation

2024-11-24: Task created, ready for execution""",
        "estimated_hours": 2.0,
        "artifacts": """• setup_github_secrets.sh (execution script)
• deployment.log (execution log)
• validation_report.md (test results)
• secrets_backup.json (encrypted backup)""",
        "blockers": "",
        "assigned_to": "BQXML CHIEF ENGINEER",
        "tags": ["infrastructure", "security", "automation", "github", "critical-path"]
    }

    print(json.dumps(task_template, indent=2))

    return {
        'critical_fields': critical_fields,
        'scoring_fields': scoring_fields,
        'scoring_requirements': {
            'min_description_length': 300,
            'min_notes_length': 200,
            'requires_estimated_hours': True,
            'requires_artifacts': True,
            'elements_for_95_plus': [
                'quantified_deliverables',
                'technical_approach',
                'success_criteria',
                'dependencies',
                'validation_method',
                'resource_requirements',
                'risk_factors'
            ]
        },
        'template': task_template
    }

def main():
    """Main execution"""
    print("\nTASKS TABLE METADATA ANALYSIS")
    print("Analyzing field requirements for 95+ scores...")
    print()

    results = analyze_tasks_metadata()

    # Save results
    if results:
        output_file = '/home/micha/bqx_ml_v3/docs/tasks_metadata_requirements.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n\nRequirements saved to: {output_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("\nKey Insights for 95+ Task Scores:")
    print("1. Include estimated_hours (critical for scoring)")
    print("2. List specific artifacts/deliverables")
    print("3. Write detailed technical descriptions (300+ chars)")
    print("4. Include implementation notes with timeline")
    print("5. Specify all dependencies and validation methods")
    print("="*80)

if __name__ == "__main__":
    main()