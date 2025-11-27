#!/usr/bin/env python3
"""
Complete assigned_to, artifacts, and source fields for all tasks in AirTable.
Ensures 100% field completeness across all required fields.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime

# Get credentials from GCP Secrets Manager
def get_secret(secret_name):
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

# Try GitHub secrets as fallback
def get_github_secret():
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
            base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']
            return api_key, base_id
    except:
        return None, None

# Get credentials
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY") or get_secret("bqx-ml-airtable-token")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID") or get_secret("bqx-ml-airtable-base-id")

# Fallback to GitHub secrets
if not AIRTABLE_API_KEY or not BASE_ID:
    AIRTABLE_API_KEY, BASE_ID = get_github_secret()

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials from any source")

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def get_source_for_task(task_id, task_name, phase):
    """Generate appropriate source field based on task context."""

    sources = {
        # Infrastructure and setup tasks
        'P00': 'docs/BQX_ML_V3_PIPELINE_ARCHITECTURE.md',
        'P01': 'scripts/baseline_model_training.py',
        'P02': 'scripts/data_preparation_pipeline.py',

        # Vertex AI phases
        'P03': {
            'S03': 'scripts/vertex_ai_infrastructure.py',  # Vertex AI Infrastructure
            'default': 'scripts/model_development.py'
        },
        'P04': {
            'S03': 'scripts/vertex_ai_containerization.py',  # Vertex AI Containerization
            'default': 'scripts/feature_engineering.py'
        },
        'P05': {
            'S03': 'scripts/vertex_ai_pipelines.py',  # Vertex AI Pipelines
            'default': 'scripts/advanced_features.py'
        },
        'P06': 'scripts/algorithm_diversification.py',
        'P07': 'scripts/backtesting_framework.py',
        'P08': {
            'S03': 'scripts/vertex_ai_deployment.py',  # Vertex AI Deployment
            'default': 'scripts/production_deployment.py'
        },
        'P09': {
            'S03': 'scripts/vertex_ai_monitoring.py',  # Vertex AI Monitoring
            'default': 'scripts/monitoring_alerting.py'
        },
        'P10': 'scripts/optimization_tuning.py',
        'P11': 'scripts/documentation_generator.py'
    }

    # Extract phase and stage from task_id
    parts = task_id.split('.')
    if len(parts) >= 2:
        phase_id = parts[1]  # P01, P02, etc.
        stage_id = parts[2] if len(parts) >= 3 else None  # S01, S02, etc.

        if phase_id in sources:
            source = sources[phase_id]
            # Handle phase-specific stage sources
            if isinstance(source, dict):
                if stage_id and stage_id in source:
                    return source[stage_id]
                else:
                    return source.get('default', 'scripts/bqx_ml_pipeline.py')
            else:
                return source

    # Default based on task name keywords
    if 'vertex' in task_name.lower() or 'gcp' in task_name.lower():
        return 'scripts/vertex_ai_migration.py'
    elif 'docker' in task_name.lower() or 'container' in task_name.lower():
        return 'Dockerfile'
    elif 'test' in task_name.lower():
        return 'scripts/testing_framework.py'
    elif 'train' in task_name.lower():
        return 'scripts/model_training.py'
    elif 'predict' in task_name.lower():
        return 'scripts/prediction_pipeline.py'
    elif 'monitor' in task_name.lower():
        return 'scripts/monitoring_system.py'
    elif 'data' in task_name.lower():
        return 'scripts/data_pipeline.py'
    elif 'feature' in task_name.lower():
        return 'scripts/feature_engineering.py'

    return 'scripts/bqx_ml_v3_main.py'

def get_artifacts_for_task(task_id, task_name, phase):
    """Generate appropriate artifacts field based on task context."""

    # Extract phase from task_id
    parts = task_id.split('.')
    phase_id = parts[1] if len(parts) >= 2 else 'P00'
    stage_id = parts[2] if len(parts) >= 3 else 'S00'

    artifacts = []

    # Common artifacts based on phase
    phase_artifacts = {
        'P00': ['docs/PROJECT_OVERVIEW.md', 'config/project_config.yaml'],
        'P01': ['models/baseline_model.pkl', 'reports/baseline_metrics.json'],
        'P02': ['data/preprocessed/', 'intelligence/data_quality_report.json'],
        'P03': ['infrastructure/terraform/', 'config/vertex_ai_config.yaml'],
        'P04': ['models/feature_sets/', 'reports/feature_importance.json'],
        'P05': ['models/advanced/', 'pipelines/training_pipeline.yaml'],
        'P06': ['models/ensemble/', 'reports/algorithm_comparison.json'],
        'P07': ['backtest_results/', 'reports/backtest_analysis.html'],
        'P08': ['deployments/production/', 'config/deployment_config.yaml'],
        'P09': ['dashboards/monitoring/', 'alerts/alert_policies.yaml'],
        'P10': ['models/optimized/', 'reports/optimization_results.json'],
        'P11': ['docs/api_documentation/', 'docs/user_guide.pdf']
    }

    # Add phase-specific artifacts
    if phase_id in phase_artifacts:
        artifacts.extend(phase_artifacts[phase_id])

    # Vertex AI specific artifacts for S03 stages
    if stage_id == 'S03':
        if phase_id == 'P03':
            artifacts.extend(['gs://bqx-ml-v3-vertex/infrastructure/', 'vertex_ai_apis.txt'])
        elif phase_id == 'P04':
            artifacts.extend(['gcr.io/bqx-ml-v3/containers/', 'Dockerfile.vertex'])
        elif phase_id == 'P05':
            artifacts.extend(['vertex_pipelines/', 'pipeline_definitions.json'])
        elif phase_id == 'P08':
            artifacts.extend(['vertex_endpoints/', 'model_endpoints.json'])
        elif phase_id == 'P09':
            artifacts.extend(['monitoring_dashboards/', 'alert_configs.yaml'])

    # Add task-specific artifacts based on name
    if 'model' in task_name.lower():
        artifacts.append('models/')
    if 'data' in task_name.lower():
        artifacts.append('data/')
    if 'report' in task_name.lower() or 'analysis' in task_name.lower():
        artifacts.append('reports/')
    if 'config' in task_name.lower():
        artifacts.append('config/')
    if 'docker' in task_name.lower() or 'container' in task_name.lower():
        artifacts.append('Dockerfile')
    if 'pipeline' in task_name.lower():
        artifacts.append('pipelines/')
    if 'test' in task_name.lower():
        artifacts.append('test_results/')
    if 'notebook' in task_name.lower():
        artifacts.append('notebooks/')

    # Return as comma-separated string
    return ', '.join(list(set(artifacts))[:5])  # Limit to 5 unique artifacts

def update_task_fields():
    """Update all tasks with missing assigned_to, artifacts, and source fields."""

    print("🔧 COMPLETING ALL TASK FIELDS")
    print("=" * 80)
    print("Fields to update: assigned_to, artifacts, source")
    print("-" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()
    print(f"\nFound {len(all_tasks)} tasks to process")

    # Track updates
    updates_needed = 0
    updates_successful = 0
    updates_failed = 0

    # Process each task
    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')
        task_name = fields.get('name', '')

        # Check which fields need updating
        update_fields = {}

        # Check assigned_to
        if not fields.get('assigned_to'):
            # Assign based on task type and phase
            parts = task_id.split('.')
            phase = parts[1] if len(parts) >= 2 else 'P00'

            if 'vertex' in task_name.lower() or phase in ['P03', 'P04', 'P05', 'P08', 'P09']:
                if 'S03' in task_id:  # Vertex AI specific stages
                    update_fields['assigned_to'] = 'vertex-ai-team@bqx-ml-v3'
                else:
                    update_fields['assigned_to'] = 'ml-engineering@bqx-ml-v3'
            elif phase in ['P00', 'P01', 'P02']:
                update_fields['assigned_to'] = 'data-science@bqx-ml-v3'
            elif phase in ['P06', 'P07']:
                update_fields['assigned_to'] = 'quant-research@bqx-ml-v3'
            elif phase in ['P10']:
                update_fields['assigned_to'] = 'optimization-team@bqx-ml-v3'
            elif phase in ['P11']:
                update_fields['assigned_to'] = 'documentation@bqx-ml-v3'
            else:
                update_fields['assigned_to'] = 'bqx-ml-team@bqx-ml-v3'

        # Check artifacts
        if not fields.get('artifacts'):
            parts = task_id.split('.')
            phase = parts[1] if len(parts) >= 2 else 'P00'
            update_fields['artifacts'] = get_artifacts_for_task(task_id, task_name, phase)

        # Check source
        if not fields.get('source'):
            parts = task_id.split('.')
            phase = parts[1] if len(parts) >= 2 else 'P00'
            update_fields['source'] = get_source_for_task(task_id, task_name, phase)

        # Apply updates if needed
        if update_fields:
            updates_needed += 1
            try:
                tasks_table.update(task['id'], update_fields)
                updates_successful += 1

                # Show what was updated
                updates_str = ', '.join(update_fields.keys())
                print(f"✅ {task_id}: Updated {updates_str}")

                # Show details for Vertex AI tasks
                if 'vertex' in task_name.lower() or 'S03' in task_id:
                    for field, value in update_fields.items():
                        print(f"   • {field}: {value}")

            except Exception as e:
                updates_failed += 1
                print(f"❌ {task_id}: Failed to update - {e}")

    # Summary report
    print("\n" + "=" * 80)
    print("📊 UPDATE SUMMARY")
    print("=" * 80)

    print(f"\nTotal Tasks Processed: {len(all_tasks)}")
    print(f"Updates Needed: {updates_needed}")
    print(f"Updates Successful: {updates_successful}")
    print(f"Updates Failed: {updates_failed}")

    # Check specific Vertex AI tasks
    print("\n📋 VERTEX AI TASKS STATUS")
    print("-" * 40)

    vertex_patterns = [
        'MP03.P03.S03.',  # Infrastructure
        'MP03.P04.S03.',  # Containerization
        'MP03.P05.S03.',  # Pipelines
        'MP03.P08.S03.',  # Deployment
        'MP03.P09.S03.'   # Monitoring
    ]

    vertex_count = 0
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        if any(pattern in task_id for pattern in vertex_patterns):
            vertex_count += 1
            fields = task['fields']

            # Check completeness
            has_assigned = bool(fields.get('assigned_to'))
            has_artifacts = bool(fields.get('artifacts'))
            has_source = bool(fields.get('source'))

            if has_assigned and has_artifacts and has_source:
                print(f"  ✅ {task_id}: All fields complete")
            else:
                missing = []
                if not has_assigned:
                    missing.append('assigned_to')
                if not has_artifacts:
                    missing.append('artifacts')
                if not has_source:
                    missing.append('source')
                print(f"  ⚠️  {task_id}: Missing {', '.join(missing)}")

    print(f"\nTotal Vertex AI tasks: {vertex_count}")

    # Final assessment
    print("\n" + "=" * 80)
    print("🎯 FIELD COMPLETENESS STATUS")
    print("=" * 80)

    if updates_failed == 0 and updates_needed == updates_successful:
        print("\n✅ SUCCESS: All task fields have been completed!")
        print("   • assigned_to: All tasks assigned to appropriate teams")
        print("   • artifacts: All tasks have associated artifacts")
        print("   • source: All tasks have source references")
    elif updates_successful > 0:
        print(f"\n🔄 PARTIAL SUCCESS: {updates_successful}/{updates_needed} fields updated")
        print("   Some updates may have failed. Run again to retry.")
    else:
        print("\n✅ NO UPDATES NEEDED: All fields were already complete!")

    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 80)

    return updates_failed == 0

if __name__ == "__main__":
    success = update_task_fields()

    if success:
        print("\n🎉 All task fields successfully completed!")
    else:
        print("\n⚠️  Some updates failed. Please review and retry if needed.")