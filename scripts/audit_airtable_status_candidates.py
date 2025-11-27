#!/usr/bin/env python3
"""
Audit AirTable records to identify candidates for Cancelled/Restated status
Based on AIRTABLE_STATUS_STANDARDIZATION_GUIDE.md
Version 1.0
"""

import json
from pyairtable import Api
from datetime import datetime
import re
import sys

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)

def analyze_task_for_cancellation(task):
    """
    Determine if a task should be cancelled based on audit criteria
    """
    name = task['fields'].get('name', '').lower()
    description = task['fields'].get('description', '').lower()
    notes = task['fields'].get('notes', '').lower()
    status = task['fields'].get('status', '').lower()
    task_id = task['fields'].get('task_id', '')

    reasons = []

    # Check for naive dual processing tasks
    if 'naive dual' in name or 'naive dual' in description:
        reasons.append("Naive dual processing - superseded by Smart Dual (R² 0.27 vs 0.94)")

    # Check for unrealistic 95% accuracy targets
    if ('95%' in name or '95%' in description) and ('accuracy' in name or 'accuracy' in description):
        reasons.append("Unrealistic 95% accuracy target - adjusted to 85-88% realistic goal")

    # Check for "implement all features" tasks
    if ('all' in name and 'features' in name) or ('implement all' in description):
        if '6000' in name or '6000' in description:
            reasons.append("'Implement all 6000 features' - changed to test all, keep what works")

    # Check for excessive complexity
    if 'every possible algorithm' in description or 'all possible' in description:
        reasons.append("Excessive complexity - selective approach preferred")

    # Check for TFT implementation if XGBoost sufficient
    if 'tft' in name.lower() or 'temporal fusion' in name:
        if 'todo' in status or 'not started' in status:
            reasons.append("TFT implementation - only needed if XGBoost < 85% (currently 94%+)")

    # Check for obsolete simulation tasks
    if 'simulation' in name and ('fake' in notes or 'synthetic' in description):
        reasons.append("Simulation violation - BUILD_DONT_SIMULATE mandate")

    return reasons

def analyze_task_for_restatement(task):
    """
    Determine if a task should be restated based on audit criteria
    """
    name = task['fields'].get('name', '').lower()
    description = task['fields'].get('description', '').lower()
    notes = task['fields'].get('notes', '').lower()
    task_id = task['fields'].get('task_id', '')

    restatements = []

    # Check for vague scope that needs clarification
    if 'improve model performance' == name.strip():
        restatements.append({
            'original': 'Improve model performance',
            'restated': 'Test 6000+ features, keep those with >1% R² improvement'
        })

    # Check for changed accuracy requirements
    if '95%' in description and 'accuracy' in description:
        if 'master' in name or 'objective' in name:
            restatements.append({
                'original': 'Achieve 95% accuracy',
                'restated': 'Achieve 85-88% realistic accuracy with Smart Dual Processing'
            })

    # Check for feature implementation scope changes
    if 'implement' in name and 'features' in name:
        if 'all' in name or '6000' in description:
            restatements.append({
                'original': 'Implement all features',
                'restated': 'Test all features, operationalize only those improving performance'
            })

    # Check for algorithm selection changes
    if 'must use' in description and ('algorithm' in name or 'model' in name):
        restatements.append({
            'original': 'Must use specific algorithm',
            'restated': 'Test algorithms in order, use if improvement > threshold'
        })

    # Check for BQX lag understanding
    if 'bqx' in name and 'feature' in name and not 'smart dual' in notes:
        if 'todo' not in task['fields'].get('status', '').lower():
            restatements.append({
                'original': 'BQX features implementation',
                'restated': 'Smart Dual with weighted BQX (90-lag aware) and IDX features'
            })

    return restatements

def audit_all_tables():
    """
    Audit Tasks, Stages, and Phases tables
    """
    results = {
        'cancellation_candidates': [],
        'restatement_candidates': [],
        'status_field_updates_needed': [],
        'timestamp': datetime.now().isoformat()
    }

    # Audit Tasks table
    print("\n📋 AUDITING TASKS TABLE...")
    tasks_table = base.table('Tasks')
    all_tasks = tasks_table.all()

    for task in all_tasks:
        task_id = task['fields'].get('task_id', 'Unknown')

        # Check for cancellation
        cancel_reasons = analyze_task_for_cancellation(task)
        if cancel_reasons:
            results['cancellation_candidates'].append({
                'table': 'Tasks',
                'record_id': task['id'],
                'task_id': task_id,
                'name': task['fields'].get('name', ''),
                'current_status': task['fields'].get('status', ''),
                'reasons': cancel_reasons
            })

        # Check for restatement
        restatements = analyze_task_for_restatement(task)
        if restatements:
            results['restatement_candidates'].append({
                'table': 'Tasks',
                'record_id': task['id'],
                'task_id': task_id,
                'name': task['fields'].get('name', ''),
                'current_status': task['fields'].get('status', ''),
                'restatements': restatements
            })

    # Check if status field needs new options
    # Get first task to check field schema
    if all_tasks:
        status_values = set()
        for task in all_tasks:
            if 'status' in task['fields']:
                status_values.add(task['fields']['status'])

        if 'Cancelled' not in status_values and 'Restated' not in status_values:
            results['status_field_updates_needed'].append({
                'table': 'Tasks',
                'current_options': list(status_values),
                'missing': ['Cancelled', 'Restated'],
                'action': 'Add Cancelled and Restated to status field options'
            })

    # Audit Stages table
    print("\n📊 AUDITING STAGES TABLE...")
    try:
        stages_table = base.table('Stages')
        all_stages = stages_table.all()

        for stage in all_stages:
            name = stage['fields'].get('name', '').lower()
            description = stage['fields'].get('description', '').lower()

            # Check for stages that might need cancellation
            if 'naive dual' in name or 'simulation' in name:
                results['cancellation_candidates'].append({
                    'table': 'Stages',
                    'record_id': stage['id'],
                    'stage_id': stage['fields'].get('stage_id', ''),
                    'name': stage['fields'].get('name', ''),
                    'current_status': stage['fields'].get('status', ''),
                    'reasons': ['Stage contains obsolete approach']
                })
    except Exception as e:
        print(f"  ⚠️ Could not audit Stages table: {e}")

    # Audit Phases table
    print("\n🎯 AUDITING PHASES TABLE...")
    try:
        phases_table = base.table('Phases')
        all_phases = phases_table.all()

        for phase in all_phases:
            name = phase['fields'].get('name', '').lower()

            # Check for phases needing restatement
            if '95%' in name and 'accuracy' in name:
                results['restatement_candidates'].append({
                    'table': 'Phases',
                    'record_id': phase['id'],
                    'phase_id': phase['fields'].get('phase_id', ''),
                    'name': phase['fields'].get('name', ''),
                    'current_status': phase['fields'].get('status', ''),
                    'restatements': [{
                        'original': 'Target 95% accuracy',
                        'restated': 'Target 85-88% realistic accuracy'
                    }]
                })
    except Exception as e:
        print(f"  ⚠️ Could not audit Phases table: {e}")

    return results

def generate_report(results):
    """
    Generate audit report
    """
    report = []
    report.append("\n" + "="*80)
    report.append("AIRTABLE STATUS AUDIT REPORT")
    report.append(f"Timestamp: {results['timestamp']}")
    report.append("="*80)

    # Status field updates needed
    if results['status_field_updates_needed']:
        report.append("\n⚙️ STATUS FIELD UPDATES REQUIRED:")
        report.append("-" * 40)
        for update in results['status_field_updates_needed']:
            report.append(f"Table: {update['table']}")
            report.append(f"  Current options: {', '.join(update['current_options'])}")
            report.append(f"  Missing options: {', '.join(update['missing'])}")
            report.append(f"  Action: {update['action']}")

    # Cancellation candidates
    report.append(f"\n❌ CANCELLATION CANDIDATES: {len(results['cancellation_candidates'])} found")
    report.append("-" * 40)

    if results['cancellation_candidates']:
        # Group by reason
        by_reason = {}
        for candidate in results['cancellation_candidates']:
            for reason in candidate['reasons']:
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append(candidate)

        for reason, tasks in by_reason.items():
            report.append(f"\n📌 {reason}")
            for task in tasks[:5]:  # Show first 5
                report.append(f"  • {task['task_id']}: {task['name'][:50]}...")
            if len(tasks) > 5:
                report.append(f"  • ... and {len(tasks)-5} more")
    else:
        report.append("  No tasks identified for cancellation")

    # Restatement candidates
    report.append(f"\n🔀 RESTATEMENT CANDIDATES: {len(results['restatement_candidates'])} found")
    report.append("-" * 40)

    if results['restatement_candidates']:
        # Group by restatement type
        by_type = {}
        for candidate in results['restatement_candidates']:
            for restatement in candidate['restatements']:
                key = restatement['original']
                if key not in by_type:
                    by_type[key] = {
                        'restated': restatement['restated'],
                        'tasks': []
                    }
                by_type[key]['tasks'].append(candidate)

        for original, info in by_type.items():
            report.append(f"\n📝 Original: {original}")
            report.append(f"   Restated: {info['restated']}")
            report.append(f"   Affected tasks:")
            for task in info['tasks'][:5]:
                report.append(f"    • {task['task_id']}: {task['name'][:40]}...")
            if len(info['tasks']) > 5:
                report.append(f"    • ... and {len(info['tasks'])-5} more")
    else:
        report.append("  No tasks identified for restatement")

    # Summary
    report.append("\n" + "="*80)
    report.append("SUMMARY")
    report.append("-" * 40)
    report.append(f"Total cancellation candidates: {len(results['cancellation_candidates'])}")
    report.append(f"Total restatement candidates: {len(results['restatement_candidates'])}")
    report.append(f"Tables needing field updates: {len(results['status_field_updates_needed'])}")

    # Recommendations
    report.append("\n📌 RECOMMENDED ACTIONS:")
    report.append("-" * 40)
    report.append("1. Update status field options to include 'Cancelled' and 'Restated'")
    report.append("2. Review and approve cancellation candidates")
    report.append("3. Review and approve restatement candidates")
    report.append("4. Apply status changes using append mode for notes")
    report.append("5. Document decisions in task notes with timestamps")

    return "\n".join(report)

def save_results(results):
    """
    Save audit results to JSON file
    """
    output_file = '/home/micha/bqx_ml_v3/intelligence/airtable_audit_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Audit results saved to: {output_file}")

# Main execution
if __name__ == "__main__":
    print("\n🔍 Starting AirTable Status Audit...")
    print("="*80)

    try:
        # Run audit
        results = audit_all_tables()

        # Generate report
        report = generate_report(results)
        print(report)

        # Save results
        save_results(results)

        # Create actionable script
        if results['cancellation_candidates'] or results['restatement_candidates']:
            print("\n✅ Audit complete. Review results and run:")
            print("  python3 /home/micha/bqx_ml_v3/scripts/apply_status_changes.py")
            print("\nThis will apply the recommended status changes.")
        else:
            print("\n✅ Audit complete. No status changes recommended.")

    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)