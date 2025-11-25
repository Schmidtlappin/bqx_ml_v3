#!/usr/bin/env python3
"""
Analyze AirTable Phases table fields, especially record_audit and record_score
to understand content requirements before uploading
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

# Table IDs from schema
PHASES_TABLE = 'tblbNORPGr9fcOnsP'

def get_phases_with_audit_data():
    """Get existing phases to analyze record_audit and record_score patterns"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{PHASES_TABLE}'

    # Get all phases to see patterns
    params = {
        'maxRecords': 100,
        'fields[]': ['phase_id', 'name', 'record_audit', 'record_score', 'status', 'description']
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def analyze_field_patterns():
    """Analyze patterns in record_audit and record_score fields"""

    data = get_phases_with_audit_data()

    if not data:
        print("Could not retrieve phases data")
        return

    records = data.get('records', [])

    print("="*80)
    print("ANALYZING PHASES TABLE FIELDS")
    print("="*80)
    print(f"\nTotal existing phases: {len(records)}")
    print("-"*80)

    # Analyze record_audit field
    print("\n📝 RECORD_AUDIT FIELD ANALYSIS:")
    print("-"*40)

    audit_examples = []
    for record in records:
        fields = record.get('fields', {})
        if 'record_audit' in fields:
            audit_text = fields['record_audit']
            phase_id = fields.get('phase_id', 'Unknown')

            print(f"\nPhase {phase_id}:")
            # Handle different data types
            if isinstance(audit_text, dict):
                print(f"Audit is a dict: {list(audit_text.keys())}")
                audit_text = str(audit_text)
            elif isinstance(audit_text, (list, tuple)):
                print(f"Audit is a {type(audit_text).__name__}: {len(audit_text)} items")
                audit_text = str(audit_text)

            if isinstance(audit_text, str):
                print(f"Audit Text Length: {len(audit_text)} characters")
                print(f"First 500 chars: {audit_text[:500]}...")
            else:
                print(f"Audit type: {type(audit_text)}")

            if audit_text:
                audit_examples.append({
                    'phase_id': phase_id,
                    'text': audit_text,
                    'length': len(audit_text)
                })

    if audit_examples:
        print(f"\n📊 Audit Field Statistics:")
        lengths = [e['length'] for e in audit_examples]
        print(f"  • Min length: {min(lengths)}")
        print(f"  • Max length: {max(lengths)}")
        print(f"  • Avg length: {sum(lengths)/len(lengths):.0f}")

        # Look for common patterns
        print(f"\n  Common patterns in audit text:")
        for example in audit_examples[:3]:
            # Check for structure
            if '**' in example['text']:
                print(f"    - Contains markdown formatting")
            if '\n' in example['text']:
                print(f"    - Multi-line content")
            if 'Score:' in example['text'] or 'Rating:' in example['text']:
                print(f"    - Contains scoring/rating information")
            if 'Completeness:' in example['text']:
                print(f"    - Contains completeness metrics")

    # Analyze record_score field
    print("\n\n📊 RECORD_SCORE FIELD ANALYSIS:")
    print("-"*40)

    score_examples = []
    for record in records:
        fields = record.get('fields', {})
        if 'record_score' in fields:
            score = fields['record_score']
            phase_id = fields.get('phase_id', 'Unknown')

            print(f"\nPhase {phase_id}:")
            print(f"  Score: {score}")

            if score is not None:
                score_examples.append({
                    'phase_id': phase_id,
                    'score': score
                })

    if score_examples:
        print(f"\n📈 Score Field Statistics:")
        scores = [e['score'] for e in score_examples]
        print(f"  • Min score: {min(scores)}")
        print(f"  • Max score: {max(scores)}")
        print(f"  • Avg score: {sum(scores)/len(scores):.1f}")
        print(f"  • Score range appears to be: 0-10 or 0-100")

    # Check field types from schema
    print("\n\n🔍 FIELD TYPE INFORMATION:")
    print("-"*40)

    schema_url = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'
    schema_response = requests.get(schema_url, headers=headers)

    if schema_response.status_code == 200:
        schema = schema_response.json()
        for table in schema.get('tables', []):
            if table['id'] == PHASES_TABLE:
                for field in table.get('fields', []):
                    if field['name'] in ['record_audit', 'record_score']:
                        print(f"\n{field['name']}:")
                        print(f"  Type: {field['type']}")
                        if 'description' in field:
                            print(f"  Description: {field['description']}")
                        if 'options' in field:
                            print(f"  Options: {json.dumps(field['options'], indent=4)}")

    # Provide recommendations
    print("\n\n✅ RECOMMENDATIONS FOR FIELD CONTENT:")
    print("-"*40)

    print("\nrecord_audit field (aiText type):")
    print("  • This appears to be an AI-generated audit/review field")
    print("  • It likely contains automated assessment of the phase record")
    print("  • May include completeness checks, quality scoring, and recommendations")
    print("  • Can be left empty for new records (will be populated by AI)")
    print("  • If provided, should be comprehensive markdown-formatted review")

    print("\nrecord_score field (number, precision 1):")
    print("  • Numeric score with 1 decimal precision")
    print("  • Range appears to be 0.0 to 10.0")
    print("  • Likely represents quality/completeness score")
    print("  • Can be left empty initially")
    print("  • If provided, use 8.0+ for well-defined phases")

    # Generate example content
    print("\n\n📝 EXAMPLE CONTENT FOR NEW PHASES:")
    print("-"*40)

    example_audit = """**Phase Assessment for P03.02: Intelligence Architecture & Discovery**

**Completeness Score: 9/10**

**Strengths:**
• Clear objectives with specific deliverables
• Well-defined intelligence architecture components
• Appropriate duration estimate (4 days)
• Critical priority correctly assigned
• Strong foundation for subsequent phases

**Areas for Enhancement:**
• Consider adding specific validation criteria for JSON files
• Include rollback procedures if intelligence system fails
• Define integration tests for IntelligenceManager class

**Dependencies:**
• Correctly depends on P03.01 (Work Environment Setup)
• No circular dependencies detected

**Risk Assessment:**
• Low risk with proper JSON schema validation
• Medium complexity requiring specialized knowledge

**Recommendations:**
• Implement JSON schema validation
• Create unit tests for IntelligenceManager
• Document intelligence layer interactions

**Overall Rating: Excellent**
Phase is well-structured and ready for execution."""

    print("\nExample record_audit content:")
    print(example_audit)

    print("\n\nExample record_score: 9.0")

    return {
        'audit_pattern': example_audit,
        'score_range': [0.0, 10.0],
        'score_recommended': 8.0
    }

def main():
    """Main execution"""
    print("AIRTABLE FIELD ANALYSIS")
    print("Analyzing Phases table fields to understand requirements...")
    print()

    patterns = analyze_field_patterns()

    # Save patterns for use in loader
    output_file = '/home/micha/bqx_ml_v3/docs/airtable_field_patterns.json'
    if patterns:
        with open(output_file, 'w') as f:
            json.dump(patterns, f, indent=2)
        print(f"\n\nPatterns saved to: {output_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("Use these patterns when creating new phase records")
    print("="*80)

if __name__ == "__main__":
    main()