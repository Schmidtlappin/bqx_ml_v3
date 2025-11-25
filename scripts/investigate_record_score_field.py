#!/usr/bin/env python3
"""
Investigate Tasks.record_score Field Metadata and Scoring Agent

This script investigates:
1. The record_score field metadata (including "prompt")
2. The record_audit field structure and content
3. How the embedded field agent should extract scores
4. Why it might not be working correctly
"""
import json
from pyairtable import Api
from pyairtable.api.types import Fields

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

# Get base schema to inspect field metadata
base = api.base(AIRTABLE_BASE_ID)

def get_table_schema():
    """Get the schema for the Tasks table including field metadata"""
    print("\n" + "="*70)
    print("FETCHING TASKS TABLE SCHEMA")
    print("="*70)

    try:
        # Get base schema
        schema = base.schema()

        # Find Tasks table
        tasks_schema = None
        for table in schema.tables:
            if table.name == 'Tasks':
                tasks_schema = table
                break

        if not tasks_schema:
            print("  ❌ Tasks table not found in schema")
            return None

        print(f"\n✓ Tasks table found")
        print(f"   Table ID: {tasks_schema.id}")
        print(f"   Table Name: {tasks_schema.name}")
        print(f"   Total Fields: {len(tasks_schema.fields)}")

        # Find record_score and record_audit fields
        record_score_field = None
        record_audit_field = None

        for field in tasks_schema.fields:
            if field.name == 'record_score':
                record_score_field = field
            elif field.name == 'record_audit':
                record_audit_field = field

        return {
            'record_score_field': record_score_field,
            'record_audit_field': record_audit_field,
            'all_fields': tasks_schema.fields
        }

    except Exception as e:
        print(f"  ❌ Error fetching schema: {e}")
        return None

def analyze_record_score_field(field):
    """Analyze the record_score field metadata"""
    print("\n" + "="*70)
    print("RECORD_SCORE FIELD ANALYSIS")
    print("="*70)

    if not field:
        print("  ❌ record_score field not found")
        return

    print(f"\n📊 Field Metadata:")
    print(f"   Field ID: {field.id}")
    print(f"   Field Name: {field.name}")
    print(f"   Field Type: {field.type}")

    # Check for options (if it's a field with options)
    if hasattr(field, 'options') and field.options:
        print(f"\n📝 Field Options:")
        try:
            # Try to convert to dict
            options_dict = field.options.__dict__ if hasattr(field.options, '__dict__') else {}
            print(f"   {json.dumps(options_dict, indent=4, default=str)}")
        except:
            print(f"   {field.options}")

    # Check for description
    if hasattr(field, 'description') and field.description:
        print(f"\n📖 Field Description:")
        print(f"   {field.description}")

    # Print raw field data
    print(f"\n🔍 Raw Field Data:")
    field_dict = field.__dict__ if hasattr(field, '__dict__') else {}
    for key, value in field_dict.items():
        if not key.startswith('_'):
            print(f"   {key}: {value}")

def analyze_record_audit_field(field):
    """Analyze the record_audit field metadata"""
    print("\n" + "="*70)
    print("RECORD_AUDIT FIELD ANALYSIS")
    print("="*70)

    if not field:
        print("  ❌ record_audit field not found")
        return

    print(f"\n📊 Field Metadata:")
    print(f"   Field ID: {field.id}")
    print(f"   Field Name: {field.name}")
    print(f"   Field Type: {field.type}")

    # Check for options
    if hasattr(field, 'options') and field.options:
        print(f"\n📝 Field Options:")
        try:
            # Try to convert to dict
            options_dict = field.options.__dict__ if hasattr(field.options, '__dict__') else {}
            print(f"   {json.dumps(options_dict, indent=4, default=str)}")
        except:
            print(f"   {field.options}")

    # Check for description
    if hasattr(field, 'description') and field.description:
        print(f"\n📖 Field Description:")
        print(f"   {field.description}")

    # Check if it's an AI field
    if field.type == 'aiText':
        print(f"\n🤖 AI Field Detected!")
        if hasattr(field, 'options') and field.options:
            options = field.options
            if isinstance(options, dict):
                if 'prompt' in options:
                    print(f"\n📋 AI Field Prompt:")
                    print(f"   {options['prompt']}")
                if 'referencedFieldIds' in options:
                    print(f"\n🔗 Referenced Fields:")
                    for field_id in options['referencedFieldIds']:
                        print(f"   - {field_id}")

    # Print raw field data
    print(f"\n🔍 Raw Field Data:")
    field_dict = field.__dict__ if hasattr(field, '__dict__') else {}
    for key, value in field_dict.items():
        if not key.startswith('_'):
            print(f"   {key}: {value}")

def sample_tasks_with_record_audit():
    """Sample tasks that have record_audit content"""
    print("\n" + "="*70)
    print("SAMPLING TASKS WITH RECORD_AUDIT")
    print("="*70)

    all_tasks = tasks_table.all()

    tasks_with_audit = []
    tasks_without_audit = []

    for task in all_tasks:
        fields = task['fields']
        if 'record_audit' in fields and fields['record_audit']:
            tasks_with_audit.append(task)
        else:
            tasks_without_audit.append(task)

    print(f"\n📊 Task Distribution:")
    print(f"   Total tasks: {len(all_tasks)}")
    print(f"   Tasks with record_audit: {len(tasks_with_audit)}")
    print(f"   Tasks without record_audit: {len(tasks_without_audit)}")

    # Sample a few tasks with record_audit
    if tasks_with_audit:
        print(f"\n📝 Sample Tasks with record_audit (showing first 3):")

        for i, task in enumerate(tasks_with_audit[:3], 1):
            fields = task['fields']
            print(f"\n  Task {i}: {fields.get('task_id', 'Unknown')}")
            print(f"  Name: {fields.get('name', 'Unnamed')}")
            print(f"  record_score: {fields.get('record_score', 'N/A')}")
            print(f"  record_audit type: {type(fields.get('record_audit'))}")

            # Print record_audit content
            audit = fields.get('record_audit', '')
            if isinstance(audit, dict):
                print(f"  record_audit (dict):")
                print(f"    {json.dumps(audit, indent=4)}")
            elif isinstance(audit, str):
                print(f"  record_audit (string, first 500 chars):")
                print(f"    {audit[:500]}...")
            else:
                print(f"  record_audit: {audit}")

    return tasks_with_audit

def check_for_ai_field_issues(schema_data):
    """Check for potential issues with AI field configuration"""
    print("\n" + "="*70)
    print("AI FIELD CONFIGURATION ANALYSIS")
    print("="*70)

    record_score = schema_data.get('record_score_field')
    record_audit = schema_data.get('record_audit_field')

    issues = []

    # Check if record_score is an AI field
    if record_score:
        if record_score.type == 'aiText':
            print(f"\n✓ record_score is an AI field (aiText)")

            # Check for prompt
            if hasattr(record_score, 'options') and record_score.options:
                options = record_score.options
                if isinstance(options, dict) and 'prompt' in options:
                    print(f"\n✓ record_score has a prompt defined")
                    print(f"   Prompt: {options['prompt'][:200]}...")
                else:
                    print(f"\n⚠️  record_score AI field has no prompt defined")
                    issues.append("record_score AI field missing prompt")
        else:
            print(f"\n⚠️  record_score is NOT an AI field (type: {record_score.type})")
            issues.append(f"record_score is type '{record_score.type}', not 'aiText'")

    # Check if record_audit exists
    if record_audit:
        print(f"\n✓ record_audit field exists")
        print(f"   Type: {record_audit.type}")
    else:
        print(f"\n⚠️  record_audit field not found")
        issues.append("record_audit field not found")

    # Summary
    print("\n" + "="*70)
    if issues:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No configuration issues detected")
    print("="*70)

    return issues

def main():
    print("🔍 Tasks.record_score Field Investigation")
    print("="*70)
    print("\nInvestigating record_score field metadata and scoring agent")
    print("="*70)

    # Get table schema
    schema_data = get_table_schema()

    if not schema_data:
        print("\n❌ Failed to fetch schema")
        return

    # Analyze record_score field
    analyze_record_score_field(schema_data.get('record_score_field'))

    # Analyze record_audit field
    analyze_record_audit_field(schema_data.get('record_audit_field'))

    # Sample tasks with record_audit
    tasks_with_audit = sample_tasks_with_record_audit()

    # Check for AI field issues
    issues = check_for_ai_field_issues(schema_data)

    # Final summary
    print("\n" + "="*70)
    print("INVESTIGATION SUMMARY")
    print("="*70)

    print(f"\n📊 Key Findings:")
    print(f"   record_score field type: {schema_data.get('record_score_field').type if schema_data.get('record_score_field') else 'Not found'}")
    print(f"   record_audit field type: {schema_data.get('record_audit_field').type if schema_data.get('record_audit_field') else 'Not found'}")
    print(f"   Tasks with record_audit: {len(tasks_with_audit) if tasks_with_audit else 0}")

    if issues:
        print(f"\n⚠️  {len(issues)} configuration issues detected")
        print("\n📋 Recommended Actions:")
        print("   1. Verify record_score is configured as an AI field (aiText)")
        print("   2. Ensure record_score has a prompt that references record_audit")
        print("   3. Check that record_audit contains the quality criteria")
        print("   4. Verify the AI field is properly linked to record_audit field")
    else:
        print(f"\n✅ No configuration issues detected")
        print("\n💡 Next Steps:")
        print("   1. Review sample record_audit content")
        print("   2. Verify AI field prompt matches expected format")
        print("   3. Test manual score extraction from record_audit")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
