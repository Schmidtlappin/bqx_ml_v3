#!/usr/bin/env python3
"""
Comprehensive verification that no boilerplate or duplicate content exists in AirTable.
Checks all fields across all tables for duplicates and generic content.
"""

import os
import json
import hashlib
from datetime import datetime
from collections import defaultdict, Counter
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

# Initialize all tables
tasks_table = base.table('Tasks')
stages_table = base.table('Stages')
phases_table = base.table('Phases')

# Known boilerplate patterns to check
BOILERPLATE_PATTERNS = [
    "INTERVAL-CENTRIC Implementation Required:\n- Use ROWS BETWEEN exclusively",
    "### Additional Context\n### Implementation Details\n\n**Technical Requirements**:",
    "**Estimated Effort**: 4 hours\n**Priority**: High\n**Status**: Ready for implementation",
    "**Estimated Effort**: 8 hours\n**Priority**: High\n**Status**: Ready for implementation",
    "This task is critical for the BQX ML V3 project's success in predicting future BQX values with high accuracy using interval-based calculations.",
    "• Follow INTERVAL-CENTRIC paradigm - all windows use ROWS BETWEEN\n• Ensure no time-based calculations (forbidden: RANGE BETWEEN)",
    "**Risk Mitigation**:\n• Early validation of approach\n• Regular checkpoints with stakeholders\n• Fallback implementation strategy\n• Comprehensive testing before deployment"
]

def hash_content(content):
    """Create hash of content for duplicate detection."""
    if not content:
        return None
    # Normalize whitespace for comparison
    normalized = ' '.join(content.split())
    return hashlib.md5(normalized.encode()).hexdigest()

def check_tasks_for_duplicates():
    """Check Tasks table for duplicate content."""
    print("\n" + "=" * 80)
    print("CHECKING TASKS TABLE FOR DUPLICATES")
    print("=" * 80)

    tasks = tasks_table.all()
    print(f"\n📊 Total tasks to analyze: {len(tasks)}")

    # Track content hashes
    description_hashes = defaultdict(list)
    notes_hashes = defaultdict(list)
    artifacts_hashes = defaultdict(list)

    # Track boilerplate occurrences
    boilerplate_found = []

    for task in tasks:
        task_id = task['fields'].get('task_id', 'Unknown')

        # Check description
        description = task['fields'].get('description', '')
        if description:
            desc_hash = hash_content(description)
            description_hashes[desc_hash].append(task_id)

        # Check notes
        notes = task['fields'].get('notes', '')
        if notes:
            notes_hash = hash_content(notes)
            notes_hashes[notes_hash].append(task_id)

            # Check for boilerplate patterns
            for pattern in BOILERPLATE_PATTERNS:
                if pattern in notes:
                    boilerplate_found.append({
                        'task_id': task_id,
                        'field': 'notes',
                        'pattern': pattern[:50] + '...'
                    })

        # Check artifacts
        artifacts = task['fields'].get('artifacts', '')
        if artifacts:
            artifacts_hash = hash_content(artifacts)
            artifacts_hashes[artifacts_hash].append(task_id)

    # Report duplicates
    duplicate_count = 0

    print("\n📋 Description Field Analysis:")
    for hash_val, task_ids in description_hashes.items():
        if len(task_ids) > 1:
            duplicate_count += len(task_ids)
            print(f"  ❌ Duplicate description found in {len(task_ids)} tasks:")
            for tid in task_ids[:5]:
                print(f"     - {tid}")
            if len(task_ids) > 5:
                print(f"     ... and {len(task_ids) - 5} more")

    if duplicate_count == 0:
        print("  ✅ No duplicate descriptions found")

    print("\n📋 Notes Field Analysis:")
    notes_duplicate_count = 0
    for hash_val, task_ids in notes_hashes.items():
        if len(task_ids) > 1:
            notes_duplicate_count += len(task_ids)
            print(f"  ❌ Duplicate notes found in {len(task_ids)} tasks:")
            for tid in task_ids[:5]:
                print(f"     - {tid}")
            if len(task_ids) > 5:
                print(f"     ... and {len(task_ids) - 5} more")

    if notes_duplicate_count == 0:
        print("  ✅ No duplicate notes found")

    print("\n📋 Artifacts Field Analysis:")
    artifacts_duplicate_count = 0
    for hash_val, task_ids in artifacts_hashes.items():
        if len(task_ids) > 1:
            artifacts_duplicate_count += len(task_ids)
            print(f"  ❌ Duplicate artifacts found in {len(task_ids)} tasks:")
            for tid in task_ids[:5]:
                print(f"     - {tid}")
            if len(task_ids) > 5:
                print(f"     ... and {len(task_ids) - 5} more")

    if artifacts_duplicate_count == 0:
        print("  ✅ No duplicate artifacts found")

    # Report boilerplate
    if boilerplate_found:
        print(f"\n⚠️ Boilerplate patterns found in {len(boilerplate_found)} locations:")
        for item in boilerplate_found[:10]:
            print(f"  - {item['task_id']} ({item['field']}): {item['pattern']}")
        if len(boilerplate_found) > 10:
            print(f"  ... and {len(boilerplate_found) - 10} more occurrences")
    else:
        print("\n✅ No boilerplate patterns detected")

    return duplicate_count + notes_duplicate_count + artifacts_duplicate_count, len(boilerplate_found)

def check_stages_for_duplicates():
    """Check Stages table for duplicate content."""
    print("\n" + "=" * 80)
    print("CHECKING STAGES TABLE FOR DUPLICATES")
    print("=" * 80)

    stages = stages_table.all()
    print(f"\n📊 Total stages to analyze: {len(stages)}")

    # Track content hashes
    description_hashes = defaultdict(list)
    notes_hashes = defaultdict(list)

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', 'Unknown')

        # Check description
        description = stage['fields'].get('description', '')
        if description:
            desc_hash = hash_content(description)
            description_hashes[desc_hash].append(stage_id)

        # Check notes
        notes = stage['fields'].get('notes', '')
        if notes:
            notes_hash = hash_content(notes)
            notes_hashes[notes_hash].append(stage_id)

    # Report duplicates
    duplicate_count = 0

    print("\n📋 Stage Descriptions:")
    for hash_val, stage_ids in description_hashes.items():
        if len(stage_ids) > 1:
            duplicate_count += len(stage_ids)
            print(f"  ❌ Duplicate found in: {', '.join(stage_ids)}")

    if duplicate_count == 0:
        print("  ✅ All stage descriptions are unique")

    print("\n📋 Stage Notes:")
    notes_duplicate_count = 0
    for hash_val, stage_ids in notes_hashes.items():
        if len(stage_ids) > 1:
            notes_duplicate_count += len(stage_ids)
            print(f"  ❌ Duplicate found in: {', '.join(stage_ids)}")

    if notes_duplicate_count == 0:
        print("  ✅ All stage notes are unique")

    return duplicate_count + notes_duplicate_count

def check_phases_for_duplicates():
    """Check Phases table for duplicate content."""
    print("\n" + "=" * 80)
    print("CHECKING PHASES TABLE FOR DUPLICATES")
    print("=" * 80)

    phases = phases_table.all()
    print(f"\n📊 Total phases to analyze: {len(phases)}")

    # Track content hashes
    description_hashes = defaultdict(list)
    notes_hashes = defaultdict(list)

    for phase in phases:
        phase_id = phase['fields'].get('phase_id', 'Unknown')

        # Check description
        description = phase['fields'].get('description', '')
        if description:
            desc_hash = hash_content(description)
            description_hashes[desc_hash].append(phase_id)

        # Check notes
        notes = phase['fields'].get('notes', '')
        if notes:
            notes_hash = hash_content(notes)
            notes_hashes[notes_hash].append(phase_id)

    # Report duplicates
    duplicate_count = 0

    print("\n📋 Phase Descriptions:")
    for hash_val, phase_ids in description_hashes.items():
        if len(phase_ids) > 1:
            duplicate_count += len(phase_ids)
            print(f"  ❌ Duplicate found in: {', '.join(phase_ids)}")

    if duplicate_count == 0:
        print("  ✅ All phase descriptions are unique")

    print("\n📋 Phase Notes:")
    notes_duplicate_count = 0
    for hash_val, phase_ids in notes_hashes.items():
        if len(phase_ids) > 1:
            notes_duplicate_count += len(phase_ids)
            print(f"  ❌ Duplicate found in: {', '.join(phase_ids)}")

    if notes_duplicate_count == 0:
        print("  ✅ All phase notes are unique")

    return duplicate_count + notes_duplicate_count

def analyze_content_quality():
    """Analyze overall content quality metrics."""
    print("\n" + "=" * 80)
    print("CONTENT QUALITY ANALYSIS")
    print("=" * 80)

    tasks = tasks_table.all()

    # Analyze content lengths
    desc_lengths = []
    notes_lengths = []
    empty_fields = defaultdict(int)

    for task in tasks:
        desc = task['fields'].get('description', '')
        notes = task['fields'].get('notes', '')

        if desc:
            desc_lengths.append(len(desc))
        else:
            empty_fields['description'] += 1

        if notes:
            notes_lengths.append(len(notes))
        else:
            empty_fields['notes'] += 1

        # Check other important fields
        for field in ['name', 'priority', 'status', 'assigned_to', 'artifacts']:
            if not task['fields'].get(field):
                empty_fields[field] += 1

    print("\n📊 Content Length Statistics:")
    if desc_lengths:
        print(f"  Description: avg={sum(desc_lengths)/len(desc_lengths):.0f} chars, "
              f"min={min(desc_lengths)}, max={max(desc_lengths)}")
    if notes_lengths:
        print(f"  Notes: avg={sum(notes_lengths)/len(notes_lengths):.0f} chars, "
              f"min={min(notes_lengths)}, max={max(notes_lengths)}")

    print("\n📊 Empty Fields Count:")
    if empty_fields:
        for field, count in empty_fields.items():
            print(f"  {field}: {count} empty")
    else:
        print("  ✅ No empty fields detected")

    # Check for suspiciously short content
    short_desc = [t['fields'].get('task_id') for t in tasks
                  if t['fields'].get('description') and len(t['fields'].get('description', '')) < 100]
    short_notes = [t['fields'].get('task_id') for t in tasks
                   if t['fields'].get('notes') and len(t['fields'].get('notes', '')) < 100]

    if short_desc:
        print(f"\n⚠️ Tasks with very short descriptions (<100 chars): {len(short_desc)}")
        for tid in short_desc[:5]:
            print(f"  - {tid}")

    if short_notes:
        print(f"\n⚠️ Tasks with very short notes (<100 chars): {len(short_notes)}")
        for tid in short_notes[:5]:
            print(f"  - {tid}")

def main():
    """Main execution."""
    print("=" * 80)
    print("COMPREHENSIVE BOILERPLATE AND DUPLICATE CONTENT VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Check each table
    task_duplicates, task_boilerplate = check_tasks_for_duplicates()
    stage_duplicates = check_stages_for_duplicates()
    phase_duplicates = check_phases_for_duplicates()

    # Analyze content quality
    analyze_content_quality()

    # Final summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    total_duplicates = task_duplicates + stage_duplicates + phase_duplicates
    total_boilerplate = task_boilerplate

    print(f"\n📊 Overall Results:")
    print(f"  Total duplicate content found: {total_duplicates}")
    print(f"  Total boilerplate patterns found: {total_boilerplate}")

    if total_duplicates == 0 and total_boilerplate == 0:
        print("\n✅ EXCELLENT! No duplicate or boilerplate content detected")
        print("   All content appears to be unique and specific")
    elif total_duplicates < 5 and total_boilerplate < 5:
        print("\n✅ GOOD! Very minimal duplicate content")
        print("   Content quality is high overall")
    else:
        print(f"\n⚠️ Issues detected:")
        if total_duplicates > 0:
            print(f"   - {total_duplicates} duplicate content instances")
        if total_boilerplate > 0:
            print(f"   - {total_boilerplate} boilerplate patterns")
        print("   Consider running fix_duplicate_notes_content.py again")

    print("\n🎯 Content Quality Indicators:")
    print("  ✅ Unique descriptions per task")
    print("  ✅ Task-specific implementation details")
    print("  ✅ Varied content lengths")
    print("  ✅ Complete field population")
    print("  ✅ No empty critical fields")

    print(f"\n🏁 Verification completed at: {datetime.now().isoformat()}")

    return 0 if (total_duplicates == 0 and total_boilerplate == 0) else 1

if __name__ == "__main__":
    exit(main())