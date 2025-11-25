#!/usr/bin/env python3
"""
Validate Tasks Table Field Completeness

This script verifies that all appropriate fields in the Tasks table
are 100% complete across all records.

Required Fields:
- task_id (unique identifier)
- name (task name)
- description (task description)
- status (current status)
- plan_link (link to Plans table)
- phase_link (link to Phases table)
- stage_link (link to Stages table)

Important Fields:
- notes (implementation notes)
- record_score (quality score)
- record_audit (AI quality assessment)

Optional Fields:
- source (source file)
- priority (task priority)
- estimated_hours (time estimate)
"""
import json
from pyairtable import Api
from typing import Dict, List

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')

# Field categories
REQUIRED_FIELDS = [
    'task_id',
    'name',
    'description',
    'status',
    'plan_link',
    'phase_link',
    'stage_link'
]

IMPORTANT_FIELDS = [
    'notes',
    'record_score',
    'record_audit'
]

OPTIONAL_FIELDS = [
    'source',
    'priority',
    'estimated_hours'
]

def check_field_completeness(tasks: List[Dict]) -> Dict:
    """
    Check completeness of all fields across all tasks.

    Returns statistics for each field:
    - total tasks
    - tasks with field populated
    - tasks with field missing
    - completion percentage
    """
    total_tasks = len(tasks)

    # Initialize stats
    field_stats = {}

    all_fields = REQUIRED_FIELDS + IMPORTANT_FIELDS + OPTIONAL_FIELDS

    for field_name in all_fields:
        field_stats[field_name] = {
            'total': total_tasks,
            'populated': 0,
            'missing': 0,
            'empty': 0,
            'missing_tasks': []
        }

    # Check each task
    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        for field_name in all_fields:
            value = fields.get(field_name)

            if value is None:
                field_stats[field_name]['missing'] += 1
                field_stats[field_name]['missing_tasks'].append(task_id)
            elif isinstance(value, str) and len(value.strip()) == 0:
                field_stats[field_name]['empty'] += 1
                field_stats[field_name]['missing_tasks'].append(task_id)
            elif isinstance(value, list) and len(value) == 0:
                field_stats[field_name]['empty'] += 1
                field_stats[field_name]['missing_tasks'].append(task_id)
            else:
                field_stats[field_name]['populated'] += 1

    # Calculate percentages
    for field_name in field_stats:
        stats = field_stats[field_name]
        stats['completion_pct'] = (stats['populated'] / stats['total'] * 100) if stats['total'] > 0 else 0

    return field_stats

def check_task_id_format(tasks: List[Dict]) -> Dict:
    """Check that all task_id values follow MP##.P##.S##.T## format"""
    import re

    total = len(tasks)
    valid = 0
    invalid = []

    pattern = r'^MP\d{2}\.P\d{2}\.S\d{2}\.T\d{2}$'

    for task in tasks:
        task_id = task['fields'].get('task_id', '')

        if re.match(pattern, task_id):
            valid += 1
        else:
            invalid.append(task_id)

    return {
        'total': total,
        'valid': valid,
        'invalid': len(invalid),
        'invalid_ids': invalid,
        'completion_pct': (valid / total * 100) if total > 0 else 0
    }

def check_link_field_validity(tasks: List[Dict]) -> Dict:
    """Check that link fields contain valid record IDs"""

    link_fields = ['plan_link', 'phase_link', 'stage_link']

    stats = {}

    for field_name in link_fields:
        stats[field_name] = {
            'total': len(tasks),
            'valid': 0,
            'empty': 0,
            'invalid': 0,
            'invalid_tasks': []
        }

    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        for field_name in link_fields:
            value = fields.get(field_name)

            if not value:
                stats[field_name]['empty'] += 1
                stats[field_name]['invalid_tasks'].append(task_id)
            elif not isinstance(value, list):
                stats[field_name]['invalid'] += 1
                stats[field_name]['invalid_tasks'].append(task_id)
            elif len(value) == 0:
                stats[field_name]['empty'] += 1
                stats[field_name]['invalid_tasks'].append(task_id)
            elif not all(isinstance(v, str) and v.startswith('rec') for v in value):
                stats[field_name]['invalid'] += 1
                stats[field_name]['invalid_tasks'].append(task_id)
            else:
                stats[field_name]['valid'] += 1

    # Calculate percentages
    for field_name in stats:
        total = stats[field_name]['total']
        valid = stats[field_name]['valid']
        stats[field_name]['completion_pct'] = (valid / total * 100) if total > 0 else 0

    return stats

def check_record_scores(tasks: List[Dict]) -> Dict:
    """Analyze record_score distribution"""

    scores = []
    missing = []
    negative = []
    low_scores = []  # < 90
    high_scores = []  # >= 90

    for task in tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        score = fields.get('record_score')

        if score is None:
            missing.append(task_id)
        else:
            scores.append(score)

            if score < 0:
                negative.append({'task_id': task_id, 'score': score})
            elif score < 90:
                low_scores.append({'task_id': task_id, 'score': score})
            else:
                high_scores.append({'task_id': task_id, 'score': score})

    return {
        'total': len(tasks),
        'with_score': len(scores),
        'missing': len(missing),
        'negative': len(negative),
        'low_scores': len(low_scores),
        'high_scores': len(high_scores),
        'missing_tasks': missing,
        'negative_scores': negative,
        'low_score_tasks': low_scores,
        'average': sum(scores) / len(scores) if scores else 0,
        'min': min(scores) if scores else None,
        'max': max(scores) if scores else None
    }

def print_field_report(field_stats: Dict):
    """Print detailed field completeness report"""

    print("\n" + "="*70)
    print("REQUIRED FIELDS COMPLETENESS")
    print("="*70)

    for field_name in REQUIRED_FIELDS:
        stats = field_stats[field_name]
        completion = stats['completion_pct']

        status = "✅" if completion == 100 else "⚠️"

        print(f"\n{status} {field_name}:")
        print(f"   Populated: {stats['populated']}/{stats['total']} ({completion:.1f}%)")

        if stats['missing'] > 0 or stats['empty'] > 0:
            print(f"   Missing: {stats['missing']}")
            print(f"   Empty: {stats['empty']}")

            if stats['missing_tasks']:
                print(f"   Tasks with issues:")
                for task_id in stats['missing_tasks'][:5]:
                    print(f"      - {task_id}")
                if len(stats['missing_tasks']) > 5:
                    print(f"      ... and {len(stats['missing_tasks']) - 5} more")

    print("\n" + "="*70)
    print("IMPORTANT FIELDS COMPLETENESS")
    print("="*70)

    for field_name in IMPORTANT_FIELDS:
        stats = field_stats[field_name]
        completion = stats['completion_pct']

        status = "✅" if completion >= 95 else "⚠️" if completion >= 80 else "❌"

        print(f"\n{status} {field_name}:")
        print(f"   Populated: {stats['populated']}/{stats['total']} ({completion:.1f}%)")

        if stats['missing'] > 0 or stats['empty'] > 0:
            print(f"   Missing: {stats['missing']}")
            print(f"   Empty: {stats['empty']}")

def main():
    print("🔍 Tasks Table Field Completeness Validation")
    print("="*70)
    print("\nValidating all fields in Tasks table for 100% completeness")
    print("="*70)

    # Fetch all tasks
    print("\n📥 Fetching all tasks from AirTable...")
    all_tasks = tasks_table.all()
    print(f"✓ Found {len(all_tasks)} tasks")

    # Check field completeness
    print("\n📊 Analyzing field completeness...")
    field_stats = check_field_completeness(all_tasks)

    # Check task_id format
    print("\n📊 Validating task_id format...")
    task_id_stats = check_task_id_format(all_tasks)

    # Check link field validity
    print("\n📊 Validating link fields...")
    link_stats = check_link_field_validity(all_tasks)

    # Check record scores
    print("\n📊 Analyzing record scores...")
    score_stats = check_record_scores(all_tasks)

    # Print reports
    print_field_report(field_stats)

    # Print task_id format report
    print("\n" + "="*70)
    print("TASK_ID FORMAT VALIDATION")
    print("="*70)

    status = "✅" if task_id_stats['completion_pct'] == 100 else "⚠️"
    print(f"\n{status} task_id format (MP##.P##.S##.T##):")
    print(f"   Valid: {task_id_stats['valid']}/{task_id_stats['total']} ({task_id_stats['completion_pct']:.1f}%)")

    if task_id_stats['invalid'] > 0:
        print(f"   Invalid: {task_id_stats['invalid']}")
        print(f"   Invalid IDs:")
        for task_id in task_id_stats['invalid_ids'][:5]:
            print(f"      - {task_id}")
        if len(task_id_stats['invalid_ids']) > 5:
            print(f"      ... and {len(task_id_stats['invalid_ids']) - 5} more")

    # Print link fields report
    print("\n" + "="*70)
    print("LINK FIELDS VALIDATION")
    print("="*70)

    for field_name in ['plan_link', 'phase_link', 'stage_link']:
        stats = link_stats[field_name]
        status = "✅" if stats['completion_pct'] == 100 else "⚠️"

        print(f"\n{status} {field_name}:")
        print(f"   Valid: {stats['valid']}/{stats['total']} ({stats['completion_pct']:.1f}%)")

        if stats['empty'] > 0 or stats['invalid'] > 0:
            print(f"   Empty: {stats['empty']}")
            print(f"   Invalid: {stats['invalid']}")

    # Print record score report
    print("\n" + "="*70)
    print("RECORD SCORE ANALYSIS")
    print("="*70)

    print(f"\n📊 Score Distribution:")
    print(f"   Total tasks: {score_stats['total']}")
    print(f"   With score: {score_stats['with_score']}")
    print(f"   Missing score: {score_stats['missing']}")

    if score_stats['with_score'] > 0:
        print(f"\n   Average score: {score_stats['average']:.1f}")
        print(f"   Min score: {score_stats['min']}")
        print(f"   Max score: {score_stats['max']}")

    print(f"\n📈 Score Categories:")
    print(f"   Scores >= 90: {score_stats['high_scores']} ({score_stats['high_scores']/score_stats['total']*100:.1f}%)")
    print(f"   Scores < 90: {score_stats['low_scores']} ({score_stats['low_scores']/score_stats['total']*100:.1f}%)")
    print(f"   Negative scores: {score_stats['negative']} ({score_stats['negative']/score_stats['total']*100:.1f}%)")

    if score_stats['low_scores'] > 0:
        print(f"\n⚠️  Tasks with score < 90:")
        for item in score_stats['low_score_tasks'][:5]:
            print(f"      - {item['task_id']}: {item['score']}")
        if len(score_stats['low_score_tasks']) > 5:
            print(f"      ... and {len(score_stats['low_score_tasks']) - 5} more")

    if score_stats['negative'] > 0:
        print(f"\n⚠️  Tasks with negative scores:")
        for item in score_stats['negative_scores'][:5]:
            print(f"      - {item['task_id']}: {item['score']}")
        if len(score_stats['negative_scores']) > 5:
            print(f"      ... and {len(score_stats['negative_scores']) - 5} more")

    # Overall summary
    print("\n" + "="*70)
    print("OVERALL COMPLETENESS SUMMARY")
    print("="*70)

    # Check if all required fields are 100% complete
    required_complete = all(
        field_stats[field]['completion_pct'] == 100
        for field in REQUIRED_FIELDS
    )

    # Check if all link fields are 100% complete
    links_complete = all(
        link_stats[field]['completion_pct'] == 100
        for field in ['plan_link', 'phase_link', 'stage_link']
    )

    # Check if task_id format is 100% valid
    task_id_valid = task_id_stats['completion_pct'] == 100

    print(f"\n✅ Required Fields: {'100% COMPLETE' if required_complete else 'INCOMPLETE'}")
    print(f"✅ Link Fields: {'100% COMPLETE' if links_complete else 'INCOMPLETE'}")
    print(f"✅ Task ID Format: {'100% VALID' if task_id_valid else 'INVALID IDs FOUND'}")

    if required_complete and links_complete and task_id_valid:
        print(f"\n🎉 ALL CRITICAL FIELDS ARE 100% COMPLETE!")
        print(f"   Total tasks: {len(all_tasks)}")
        print(f"   All required fields populated")
        print(f"   All link fields valid")
        print(f"   All task IDs properly formatted")
    else:
        print(f"\n⚠️  SOME FIELDS NEED ATTENTION")
        print(f"   Review output above for details")

    print("\n" + "="*70)

    return required_complete and links_complete and task_id_valid

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
