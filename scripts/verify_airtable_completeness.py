#!/usr/bin/env python3
"""
Verify AirTable completeness and generate comprehensive report
Version 1.0
"""

import json
from pyairtable import Api
from datetime import datetime, timedelta
import re
from collections import defaultdict

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)

def analyze_tasks_table():
    """Comprehensive analysis of Tasks table"""
    tasks_table = base.table('Tasks')
    all_tasks = tasks_table.all()

    analysis = {
        'total_tasks': len(all_tasks),
        'status_distribution': defaultdict(int),
        'priority_distribution': defaultdict(int),
        'missing_fields': defaultdict(list),
        'notes_compliance': {
            'compliant': 0,
            'non_compliant': 0,
            'empty': 0
        },
        'recent_updates': [],
        'issues': []
    }

    # Expected fields
    required_fields = ['task_id', 'name', 'description', 'status', 'priority', 'notes']

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'UNKNOWN')

        # Check status
        status = fields.get('status', 'MISSING')
        analysis['status_distribution'][status] += 1

        # Check priority
        priority = fields.get('priority', 'MISSING')
        analysis['priority_distribution'][priority] += 1

        # Check for missing fields
        for field in required_fields:
            if field not in fields or not fields[field]:
                analysis['missing_fields'][field].append(task_id)

        # Check notes standardization
        notes = fields.get('notes', '')
        if not notes:
            analysis['notes_compliance']['empty'] += 1
        elif any(pattern in notes for pattern in ['✅ COMPLETED:', '🔄 IN PROGRESS:', '📋 PLANNED:', '🚫 BLOCKED:', '❌ CANCELLED:', '🔀 RESTATED:']):
            analysis['notes_compliance']['compliant'] += 1
        else:
            analysis['notes_compliance']['non_compliant'] += 1

        # Check for recent updates (last 24 hours)
        if notes and '2025-11-27' in notes:
            analysis['recent_updates'].append({
                'task_id': task_id,
                'name': fields.get('name', '')[:50],
                'status': status
            })

        # Identify potential issues
        if status == 'In Progress' and '❌ CANCELLED:' in notes:
            analysis['issues'].append(f"{task_id}: Status mismatch (In Progress but notes say Cancelled)")

        if status == 'Todo' and '✅ COMPLETED:' in notes:
            analysis['issues'].append(f"{task_id}: Status mismatch (Todo but notes say Completed)")

    return analysis

def analyze_completion_metrics(analysis):
    """Calculate completion metrics"""
    total = analysis['total_tasks']

    metrics = {
        'completion_rate': 0,
        'in_progress_rate': 0,
        'blocked_rate': 0,
        'todo_rate': 0,
        'cancelled_rate': 0,
        'restated_rate': 0,
        'notes_compliance_rate': 0,
        'field_completeness_rate': 0
    }

    if total > 0:
        # Status metrics
        done_count = analysis['status_distribution'].get('Done', 0)
        in_progress = analysis['status_distribution'].get('In Progress', 0)
        blocked = analysis['status_distribution'].get('Blocked', 0)
        todo = analysis['status_distribution'].get('Todo', 0)
        cancelled = analysis['status_distribution'].get('Cancelled', 0)
        restated = analysis['status_distribution'].get('Restated', 0)

        metrics['completion_rate'] = (done_count / total) * 100
        metrics['in_progress_rate'] = (in_progress / total) * 100
        metrics['blocked_rate'] = (blocked / total) * 100
        metrics['todo_rate'] = (todo / total) * 100
        metrics['cancelled_rate'] = (cancelled / total) * 100
        metrics['restated_rate'] = (restated / total) * 100

        # Notes compliance
        compliant = analysis['notes_compliance']['compliant']
        metrics['notes_compliance_rate'] = (compliant / total) * 100

        # Field completeness
        total_fields = total * 6  # 6 required fields per task
        missing_count = sum(len(tasks) for tasks in analysis['missing_fields'].values())
        metrics['field_completeness_rate'] = ((total_fields - missing_count) / total_fields) * 100

    return metrics

def check_phase_status():
    """Check status by phase"""
    tasks_table = base.table('Tasks')
    all_tasks = tasks_table.all()

    phases = defaultdict(lambda: {'total': 0, 'done': 0, 'in_progress': 0, 'todo': 0})

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        status = task['fields'].get('status', '')

        # Extract phase from task_id (e.g., MP03.P01.S01.T01 -> P01)
        if task_id and 'P' in task_id:
            phase = task_id.split('.')[1] if '.' in task_id else 'Unknown'
            phases[phase]['total'] += 1

            if status == 'Done':
                phases[phase]['done'] += 1
            elif status == 'In Progress':
                phases[phase]['in_progress'] += 1
            elif status == 'Todo':
                phases[phase]['todo'] += 1

    return dict(phases)

def generate_report(analysis, metrics, phases):
    """Generate comprehensive report"""
    report = []
    report.append("\n" + "="*80)
    report.append("AIRTABLE COMPLETENESS VERIFICATION REPORT")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("="*80)

    # Overall Statistics
    report.append("\n📊 OVERALL STATISTICS")
    report.append("-" * 40)
    report.append(f"Total Tasks: {analysis['total_tasks']}")
    report.append(f"Field Completeness: {metrics['field_completeness_rate']:.1f}%")
    report.append(f"Notes Compliance: {metrics['notes_compliance_rate']:.1f}%")

    # Status Distribution
    report.append("\n📈 STATUS DISTRIBUTION")
    report.append("-" * 40)
    for status, count in sorted(analysis['status_distribution'].items()):
        percentage = (count / analysis['total_tasks']) * 100 if analysis['total_tasks'] > 0 else 0
        report.append(f"  {status:15} : {count:3} tasks ({percentage:5.1f}%)")

    # Priority Distribution
    report.append("\n🎯 PRIORITY DISTRIBUTION")
    report.append("-" * 40)
    for priority, count in sorted(analysis['priority_distribution'].items()):
        percentage = (count / analysis['total_tasks']) * 100 if analysis['total_tasks'] > 0 else 0
        report.append(f"  {priority:10} : {count:3} tasks ({percentage:5.1f}%)")

    # Phase Progress
    report.append("\n🚀 PHASE PROGRESS")
    report.append("-" * 40)
    for phase in sorted(phases.keys()):
        data = phases[phase]
        if data['total'] > 0:
            completion = (data['done'] / data['total']) * 100
            report.append(f"  {phase}: {data['done']}/{data['total']} done ({completion:.1f}%)")
            if data['in_progress'] > 0:
                report.append(f"       {data['in_progress']} in progress")

    # Recent Updates (Last 24 Hours)
    if analysis['recent_updates']:
        report.append(f"\n🔄 RECENT UPDATES ({len(analysis['recent_updates'])} tasks)")
        report.append("-" * 40)
        for update in analysis['recent_updates'][:10]:  # Show first 10
            report.append(f"  {update['task_id']}: {update['name']}")
        if len(analysis['recent_updates']) > 10:
            report.append(f"  ... and {len(analysis['recent_updates'])-10} more")

    # Missing Fields
    if analysis['missing_fields']:
        report.append("\n⚠️ MISSING FIELDS")
        report.append("-" * 40)
        for field, tasks in analysis['missing_fields'].items():
            if tasks:
                report.append(f"  {field}: {len(tasks)} tasks missing this field")
                if len(tasks) <= 5:
                    report.append(f"    Tasks: {', '.join(tasks)}")

    # Issues Identified
    if analysis['issues']:
        report.append("\n🚨 ISSUES IDENTIFIED")
        report.append("-" * 40)
        for issue in analysis['issues'][:10]:
            report.append(f"  • {issue}")
        if len(analysis['issues']) > 10:
            report.append(f"  ... and {len(analysis['issues'])-10} more issues")

    # Completion Summary
    report.append("\n✅ COMPLETION SUMMARY")
    report.append("-" * 40)
    report.append(f"  Tasks Completed: {metrics['completion_rate']:.1f}%")
    report.append(f"  Tasks In Progress: {metrics['in_progress_rate']:.1f}%")
    report.append(f"  Tasks Todo: {metrics['todo_rate']:.1f}%")
    report.append(f"  Tasks Blocked: {metrics['blocked_rate']:.1f}%")

    # Recommendations
    report.append("\n📋 RECOMMENDATIONS")
    report.append("-" * 40)

    if metrics['completion_rate'] < 50:
        report.append("  • Focus on completing more tasks (currently <50% done)")

    if metrics['notes_compliance_rate'] < 90:
        report.append("  • Standardize notes format for better tracking")

    if analysis['missing_fields']:
        report.append("  • Fill in missing required fields")

    if analysis['issues']:
        report.append("  • Resolve status/notes mismatches")

    if metrics['todo_rate'] > 30:
        report.append("  • High number of Todo tasks - prioritize and start execution")

    # Overall Status
    report.append("\n" + "="*80)
    report.append("OVERALL AIRTABLE STATUS")
    report.append("-" * 40)

    completeness_score = (
        metrics['field_completeness_rate'] * 0.3 +
        metrics['notes_compliance_rate'] * 0.2 +
        metrics['completion_rate'] * 0.5
    )

    if completeness_score >= 90:
        report.append("✅ EXCELLENT - AirTable is well-maintained and complete")
    elif completeness_score >= 70:
        report.append("🔄 GOOD - AirTable is mostly complete with minor gaps")
    elif completeness_score >= 50:
        report.append("⚠️ FAIR - AirTable needs attention in several areas")
    else:
        report.append("🚨 NEEDS WORK - AirTable has significant gaps")

    report.append(f"\nCompleteness Score: {completeness_score:.1f}/100")

    return "\n".join(report)

def save_analysis(analysis, metrics, phases):
    """Save analysis to JSON for tracking"""
    output = {
        'timestamp': datetime.now().isoformat(),
        'analysis': analysis,
        'metrics': metrics,
        'phases': phases
    }

    # Convert defaultdicts to regular dicts for JSON serialization
    output['analysis']['status_distribution'] = dict(output['analysis']['status_distribution'])
    output['analysis']['priority_distribution'] = dict(output['analysis']['priority_distribution'])
    output['analysis']['missing_fields'] = dict(output['analysis']['missing_fields'])

    with open('/home/micha/bqx_ml_v3/intelligence/airtable_completeness.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("💾 Analysis saved to: /home/micha/bqx_ml_v3/intelligence/airtable_completeness.json")

# Main execution
if __name__ == "__main__":
    print("\n🔍 VERIFYING AIRTABLE COMPLETENESS...")
    print("="*60)

    try:
        # Analyze tasks
        print("📊 Analyzing Tasks table...")
        analysis = analyze_tasks_table()

        # Calculate metrics
        print("📈 Calculating metrics...")
        metrics = analyze_completion_metrics(analysis)

        # Check phases
        print("🚀 Checking phase progress...")
        phases = check_phase_status()

        # Generate report
        print("📝 Generating report...")
        report = generate_report(analysis, metrics, phases)
        print(report)

        # Save analysis
        save_analysis(analysis, metrics, phases)

        print("\n✅ Verification complete!")

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()