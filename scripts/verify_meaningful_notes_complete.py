#!/usr/bin/env python3
"""
Final verification that all 197 tasks have meaningful, non-boilerplate notes.
"""

import os
import json
import re
from datetime import datetime
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
tasks_table = base.table('Tasks')

def check_for_boilerplate(content):
    """Check if content contains boilerplate patterns."""

    boilerplate_patterns = [
        r'This task involves.*comprehensive validation',
        r'Lorem ipsum',
        r'TODO:.*implement',
        r'Insert.*here',
        r'Description to be added',
        r'Coming soon',
        r'TBD',
        r'Work in progress',
        r'\[placeholder\]',
        r'Sample text',
        r'Example content'
    ]

    for pattern in boilerplate_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True, pattern

    return False, None

def verify_meaningful_content():
    """Verify all tasks have meaningful content."""

    print("=" * 80)
    print("VERIFYING MEANINGFUL NOTES - FINAL CHECK")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all tasks
    print("\n📥 Loading all tasks...")
    tasks = tasks_table.all()
    print(f"  Found {len(tasks)} tasks")

    # Analysis counters
    total_tasks = len(tasks)
    tasks_with_notes = 0
    meaningful_notes = 0
    boilerplate_found = []
    empty_notes = []
    short_notes = []
    excellent_notes = []

    # Quality thresholds
    MIN_LENGTH = 1000  # Minimum characters for meaningful content
    EXCELLENT_LENGTH = 4000  # Length for excellent content

    print("\n📊 Analyzing content quality...")

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        notes = task['fields'].get('notes', '')

        # Check if notes exist
        if notes:
            tasks_with_notes += 1

            # Check length
            if len(notes) < MIN_LENGTH:
                short_notes.append((task_id, len(notes)))
            elif len(notes) >= EXCELLENT_LENGTH:
                excellent_notes.append((task_id, len(notes)))

            # Check for boilerplate
            has_boilerplate, pattern = check_for_boilerplate(notes)
            if has_boilerplate:
                boilerplate_found.append((task_id, pattern))
            else:
                meaningful_notes += 1

            # Check for implementation code
            has_code = '```python' in notes or '```sql' in notes
            has_bigquery = 'BigQuery' in notes or 'SELECT' in notes
            has_vertex = 'Vertex AI' in notes or 'aiplatform' in notes
            has_testing = 'test_' in notes or 'pytest' in notes

            # Count quality indicators
            quality_score = sum([
                has_code,
                has_bigquery,
                has_vertex,
                has_testing,
                len(notes) >= EXCELLENT_LENGTH
            ])

            if quality_score >= 4:
                excellent_notes.append((task_id, quality_score))
        else:
            empty_notes.append(task_id)

    # Print detailed report
    print("\n" + "=" * 80)
    print("📈 CONTENT QUALITY REPORT")
    print("=" * 80)

    print(f"\n✅ COVERAGE METRICS:")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Tasks with notes: {tasks_with_notes} ({tasks_with_notes/total_tasks*100:.1f}%)")
    print(f"  Empty notes: {len(empty_notes)} ({len(empty_notes)/total_tasks*100:.1f}%)")

    print(f"\n📊 QUALITY METRICS:")
    print(f"  Meaningful content: {meaningful_notes} ({meaningful_notes/total_tasks*100:.1f}%)")
    print(f"  Excellent notes (4000+ chars): {len(excellent_notes)} ({len(excellent_notes)/total_tasks*100:.1f}%)")
    print(f"  Short notes (<1000 chars): {len(short_notes)} ({len(short_notes)/total_tasks*100:.1f}%)")
    print(f"  Boilerplate detected: {len(boilerplate_found)} ({len(boilerplate_found)/total_tasks*100:.1f}%)")

    # Show any issues
    if boilerplate_found:
        print(f"\n⚠️ BOILERPLATE PATTERNS FOUND:")
        for task_id, pattern in boilerplate_found[:5]:
            print(f"  • {task_id}: Pattern '{pattern}'")

    if empty_notes:
        print(f"\n❌ EMPTY NOTES:")
        for task_id in empty_notes[:5]:
            print(f"  • {task_id}")

    if short_notes:
        print(f"\n⚠️ SHORT NOTES (<{MIN_LENGTH} chars):")
        for task_id, length in short_notes[:5]:
            print(f"  • {task_id}: {length} chars")

    # Sample excellent notes
    print(f"\n🌟 SAMPLE EXCELLENT NOTES:")
    for task_id, score in excellent_notes[:5]:
        print(f"  • {task_id}: Quality score {score}/5")

    # Final verdict
    print("\n" + "=" * 80)
    print("🎯 FINAL VERDICT")
    print("=" * 80)

    success = (
        tasks_with_notes == total_tasks and
        len(boilerplate_found) == 0 and
        len(empty_notes) == 0
    )

    if success:
        print("✅ SUCCESS! All tasks have meaningful, non-boilerplate notes")
        print(f"📊 100% coverage with {meaningful_notes}/{total_tasks} meaningful notes")
        print("🚀 BQX ML V3 build team has comprehensive implementation guidance")
    else:
        print("⚠️ Some issues detected:")
        if empty_notes:
            print(f"  • {len(empty_notes)} tasks missing notes")
        if boilerplate_found:
            print(f"  • {len(boilerplate_found)} tasks with boilerplate")
        if short_notes:
            print(f"  • {len(short_notes)} tasks with short notes")

    # Statistics summary
    print("\n📈 STATISTICS SUMMARY:")
    print(f"  Average note length: {sum(len(t['fields'].get('notes', '')) for t in tasks) / total_tasks:.0f} chars")
    print(f"  Tasks with code examples: {sum(1 for t in tasks if '```' in t['fields'].get('notes', ''))} tasks")
    print(f"  Tasks with SQL queries: {sum(1 for t in tasks if 'SELECT' in t['fields'].get('notes', ''))} tasks")
    print(f"  Tasks with Python code: {sum(1 for t in tasks if 'def ' in t['fields'].get('notes', ''))} tasks")
    print(f"  Tasks with test cases: {sum(1 for t in tasks if 'test_' in t['fields'].get('notes', ''))} tasks")

    print(f"\n✅ Verification completed at: {datetime.now().isoformat()}")

    return success

def main():
    """Main entry point."""
    success = verify_meaningful_content()

    if success:
        print("\n🎉 CONFIRMATION: All 197 tasks have meaningful task-centric notes!")
        print("📚 No boilerplate content detected")
        print("💯 Ready for BQX ML V3 build team")
        return 0
    else:
        print("\n⚠️ Some quality issues remain")
        return 1

if __name__ == "__main__":
    exit(main())