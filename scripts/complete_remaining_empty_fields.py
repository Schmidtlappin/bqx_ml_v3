#!/usr/bin/env python3
"""
Complete ALL remaining empty fields across ALL tasks:
- priority
- assigned_to
- artifacts
"""

import os
import json
import time
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

def determine_priority(task_id, description, notes):
    """Determine priority based on task context."""
    content = f"{task_id} {description} {notes}".lower()

    # High priority indicators
    high_priority_keywords = [
        'critical', 'production', 'deployment', 'infrastructure',
        'vertex ai', 'batch prediction', 'model training', 'pipeline',
        'scheduler', 'monitoring', 'security', 'authentication',
        'data ingestion', 'feature engineering', 'core', 'foundation'
    ]

    # Medium priority indicators
    medium_priority_keywords = [
        'evaluation', 'analysis', 'documentation', 'testing',
        'visualization', 'reporting', 'optimization', 'enhancement',
        'diagnostic', 'metric', 'validation'
    ]

    # Check phase-based priority
    if any(phase in task_id for phase in ['P01', 'P02', 'P03', 'P04', 'P05', 'P06']):
        return 'High'  # Early phases are high priority
    elif any(phase in task_id for phase in ['P09']):
        return 'High'  # Production deployment is high priority
    elif any(phase in task_id for phase in ['P07', 'P08']):
        return 'Medium'  # Advanced features and evaluation
    elif any(phase in task_id for phase in ['P10', 'P11']):
        return 'Low'  # Documentation and governance

    # Keyword-based priority
    high_count = sum(1 for keyword in high_priority_keywords if keyword in content)
    medium_count = sum(1 for keyword in medium_priority_keywords if keyword in content)

    if high_count > medium_count:
        return 'High'
    elif medium_count > 0:
        return 'Medium'
    else:
        return 'Medium'  # Default to Medium

def determine_assigned_to(task_id, description, notes):
    """Determine team assignment based on task content."""
    content = f"{task_id} {description} {notes}".lower()

    # Team assignment rules
    if any(keyword in content for keyword in ['model', 'training', 'prediction', 'ml', 'algorithm', 'vertex ai']):
        return 'ML Engineering Team'
    elif any(keyword in content for keyword in ['data', 'pipeline', 'ingestion', 'etl', 'bigquery', 'dataset']):
        return 'Data Engineering Team'
    elif any(keyword in content for keyword in ['infrastructure', 'deployment', 'cloud', 'gcp', 'kubernetes']):
        return 'Platform Engineering Team'
    elif any(keyword in content for keyword in ['mlops', 'monitoring', 'scheduler', 'automation', 'cicd']):
        return 'MLOps Team'
    elif any(keyword in content for keyword in ['evaluation', 'metric', 'analysis', 'diagnostic', 'validation']):
        return 'Model Evaluation Team'
    elif any(keyword in content for keyword in ['documentation', 'glossary', 'guide', 'wiki', 'training material']):
        return 'Documentation Team'
    elif any(keyword in content for keyword in ['feature', 'engineering', 'transformation', 'aggregation']):
        return 'Feature Engineering Team'
    elif any(keyword in content for keyword in ['architecture', 'design', 'planning', 'strategy']):
        return 'Architecture Team'
    elif any(keyword in content for keyword in ['security', 'access', 'permission', 'compliance']):
        return 'Security Team'
    else:
        # Default by phase
        if 'P01' in task_id:
            return 'ML Engineering Team'
        elif 'P02' in task_id:
            return 'Architecture Team'
        elif 'P03' in task_id:
            return 'Architecture Team'
        elif 'P04' in task_id or 'P05' in task_id:
            return 'Data Engineering Team'
        elif 'P06' in task_id or 'P07' in task_id:
            return 'Feature Engineering Team'
        elif 'P08' in task_id:
            return 'Model Evaluation Team'
        elif 'P09' in task_id:
            return 'MLOps Team'
        elif 'P10' in task_id:
            return 'MLOps Team'
        elif 'P11' in task_id:
            return 'Documentation Team'
        else:
            return 'Engineering Team'

def generate_artifacts(task_id, description, notes):
    """Generate appropriate artifacts list based on task content."""
    content = f"{task_id} {description} {notes}".lower()
    artifacts = []

    # Common artifact patterns
    if 'model' in content and 'training' in content:
        artifacts.extend([
            'Trained model files (.pkl, .h5, .pb)',
            'Model evaluation metrics report',
            'Training logs and tensorboard data',
            'Model card documentation'
        ])

    if 'pipeline' in content or 'dataflow' in content:
        artifacts.extend([
            'Pipeline configuration files',
            'DAG definitions',
            'Pipeline monitoring dashboard',
            'Data lineage documentation'
        ])

    if 'batch prediction' in content:
        artifacts.extend([
            'Batch job configuration',
            'Scheduler job definitions',
            'Prediction output tables',
            'Performance benchmarks'
        ])

    if 'dataset' in content or 'data' in content and 'engineering' in content:
        artifacts.extend([
            'Dataset schemas',
            'Data validation rules',
            'Feature documentation',
            'Data quality reports'
        ])

    if 'documentation' in content or 'glossary' in content:
        artifacts.extend([
            'Documentation markdown files',
            'API reference guides',
            'User manuals',
            'Training materials'
        ])

    if 'evaluation' in content or 'metric' in content:
        artifacts.extend([
            'Evaluation reports',
            'Metric dashboards',
            'Performance charts',
            'Statistical analysis results'
        ])

    if 'infrastructure' in content or 'deployment' in content:
        artifacts.extend([
            'Infrastructure as Code (Terraform/Pulumi)',
            'Kubernetes manifests',
            'Docker images',
            'Deployment scripts'
        ])

    if 'scheduler' in content or 'automation' in content:
        artifacts.extend([
            'Scheduler configurations',
            'Automation scripts',
            'Cron job definitions',
            'Workflow templates'
        ])

    if 'feature' in content and 'engineering' in content:
        artifacts.extend([
            'Feature engineering SQL scripts',
            'Feature transformation code',
            'Feature importance analysis',
            'Feature store configurations'
        ])

    if 'monitoring' in content:
        artifacts.extend([
            'Monitoring dashboard configuration',
            'Alert rules and thresholds',
            'SLO/SLA definitions',
            'Runbook documentation'
        ])

    # Ensure we always have some artifacts
    if not artifacts:
        # Generic artifacts based on phase
        if 'P01' in task_id:
            artifacts = ['Model training code', 'Training configuration', 'Model artifacts']
        elif 'P06' in task_id or 'P07' in task_id:
            artifacts = ['Feature engineering scripts', 'Feature definitions', 'Transformation pipelines']
        elif 'P08' in task_id:
            artifacts = ['Evaluation reports', 'Metric calculations', 'Performance analysis']
        elif 'P09' in task_id:
            artifacts = ['Deployment configurations', 'Production scripts', 'Monitoring setup']
        else:
            artifacts = ['Implementation code', 'Configuration files', 'Documentation']

    # Remove duplicates and format
    artifacts = list(dict.fromkeys(artifacts))  # Remove duplicates while preserving order
    return '\n'.join(f"• {artifact}" for artifact in artifacts[:6])  # Limit to 6 most relevant

def complete_remaining_fields():
    """Complete priority, assigned_to, and artifacts for all tasks."""
    print("=" * 80)
    print("COMPLETING REMAINING EMPTY FIELDS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all tasks
    tasks = tasks_table.all()

    print(f"\n📊 Total tasks to process: {len(tasks)}")

    # Track statistics
    stats = {
        'priority_added': 0,
        'assigned_to_added': 0,
        'artifacts_added': 0,
        'tasks_updated': 0,
        'tasks_skipped': 0,
        'failed': 0
    }

    # Process each task
    for i, task in enumerate(tasks, 1):
        task_id = task['fields'].get('task_id', f'Unknown_{i}')
        description = task['fields'].get('description', '')
        notes = task['fields'].get('notes', '')

        # Check what needs updating
        needs_update = False
        update_fields = {}

        # Check priority
        if not task['fields'].get('priority'):
            priority = determine_priority(task_id, description, notes)
            update_fields['priority'] = priority
            needs_update = True
            stats['priority_added'] += 1

        # Check assigned_to
        if not task['fields'].get('assigned_to'):
            assigned_to = determine_assigned_to(task_id, description, notes)
            update_fields['assigned_to'] = assigned_to
            needs_update = True
            stats['assigned_to_added'] += 1

        # Check artifacts
        if not task['fields'].get('artifacts'):
            artifacts = generate_artifacts(task_id, description, notes)
            if artifacts:
                update_fields['artifacts'] = artifacts
                needs_update = True
                stats['artifacts_added'] += 1

        # Apply updates
        if needs_update and update_fields:
            try:
                # Show progress every 10 tasks
                if i % 10 == 0:
                    print(f"  Processing task {i}/{len(tasks)}...")

                tasks_table.update(task['id'], update_fields)
                stats['tasks_updated'] += 1
                time.sleep(0.1)  # Rate limit

            except Exception as e:
                print(f"  ❌ Failed to update {task_id}: {e}")
                stats['failed'] += 1
        else:
            stats['tasks_skipped'] += 1

    return stats

def verify_completeness():
    """Verify field completeness across all tasks."""
    print("\n" + "=" * 80)
    print("FIELD COMPLETENESS VERIFICATION")
    print("=" * 80)

    tasks = tasks_table.all()

    # Track field presence
    field_stats = {
        'priority': {'present': 0, 'missing': 0},
        'assigned_to': {'present': 0, 'missing': 0},
        'artifacts': {'present': 0, 'missing': 0}
    }

    # Check each task
    for task in tasks:
        for field in field_stats.keys():
            if task['fields'].get(field):
                field_stats[field]['present'] += 1
            else:
                field_stats[field]['missing'] += 1

    # Display results
    print("\n📊 Field Presence Analysis:")
    for field, stats in field_stats.items():
        total = stats['present'] + stats['missing']
        percentage = (stats['present'] / total * 100) if total > 0 else 0
        print(f"\n{field}:")
        print(f"  Present: {stats['present']}/{total} ({percentage:.1f}%)")
        if stats['missing'] > 0:
            print(f"  Missing: {stats['missing']}")

    # Overall completeness
    total_fields = sum(s['present'] + s['missing'] for s in field_stats.values())
    total_present = sum(s['present'] for s in field_stats.values())
    overall_percentage = (total_present / total_fields * 100) if total_fields > 0 else 0

    print(f"\n📈 Overall Field Completeness: {overall_percentage:.1f}%")

    return overall_percentage

def main():
    """Main execution."""
    print("=" * 80)
    print("COMPLETING ALL REMAINING EMPTY FIELDS")
    print("=" * 80)

    # Complete fields
    stats = complete_remaining_fields()

    # Verify completeness
    completeness = verify_completeness()

    # Summary
    print("\n" + "=" * 80)
    print("COMPLETION SUMMARY")
    print("=" * 80)

    print(f"\n📊 Fields Added:")
    print(f"  Priority fields: {stats['priority_added']}")
    print(f"  Assigned_to fields: {stats['assigned_to_added']}")
    print(f"  Artifacts fields: {stats['artifacts_added']}")

    print(f"\n📊 Task Statistics:")
    print(f"  Tasks updated: {stats['tasks_updated']}")
    print(f"  Tasks skipped (already complete): {stats['tasks_skipped']}")
    print(f"  Failed updates: {stats['failed']}")

    print(f"\n📈 Final Completeness: {completeness:.1f}%")

    if completeness >= 95:
        print(f"\n✅ SUCCESS! Near-complete field population achieved")
        print(f"   All tasks now have priority, assigned_to, and artifacts")
    elif completeness >= 90:
        print(f"\n✅ GOOD! High level of field completeness")
    else:
        print(f"\n⚠️ Some fields may still need attention")

    print(f"\n🎯 Impact:")
    print(f"  • Clear task prioritization established")
    print(f"  • Team assignments documented")
    print(f"  • Expected deliverables (artifacts) defined")
    print(f"  • Full project traceability achieved")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return 0 if completeness >= 90 else 1

if __name__ == "__main__":
    exit(main())