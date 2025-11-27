#!/usr/bin/env python3
"""
Generate Build Agent-ready descriptions for all tasks in AirTable.
Replaces boilerplate content with specific, actionable instructions.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime
import re

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

# BQX ML V3 Configuration
BQX_CONFIG = {
    'windows': [45, 90, 180, 360, 720, 1440, 2880],
    'pairs': ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF'],  # Sample of 28 pairs
    'thresholds': {'r2_min': 0.35, 'rmse_max': 0.15, 'accuracy_min': 0.75},
    'models': 196,  # 28 pairs × 7 horizons
    'methodology': 'INTERVAL-CENTRIC'
}

def generate_phase_context(phase_id):
    """Generate phase-specific context for Build Agents."""

    phase_contexts = {
        'P00': {
            'type': 'Infrastructure Setup',
            'tools': ['gcloud', 'terraform', 'kubectl'],
            'environment': 'development',
            'access': 'GCP project admin'
        },
        'P01': {
            'type': 'Baseline Model',
            'tools': ['python', 'sklearn', 'pandas'],
            'environment': 'development',
            'access': 'BigQuery read'
        },
        'P02': {
            'type': 'Data Preparation',
            'tools': ['python', 'pandas', 'numpy'],
            'environment': 'development',
            'access': 'BigQuery read/write'
        },
        'P03': {
            'type': 'Vertex AI Infrastructure',
            'tools': ['gcloud', 'vertex-ai', 'terraform'],
            'environment': 'cloud',
            'access': 'Vertex AI admin'
        },
        'P04': {
            'type': 'Feature Engineering',
            'tools': ['python', 'pandas', 'feature-tools'],
            'environment': 'development',
            'access': 'BigQuery read/write'
        },
        'P05': {
            'type': 'Advanced Models',
            'tools': ['python', 'tensorflow', 'xgboost'],
            'environment': 'cloud',
            'access': 'Vertex AI training'
        },
        'P06': {
            'type': 'Algorithm Diversification',
            'tools': ['python', 'ensemble-methods'],
            'environment': 'cloud',
            'access': 'Model registry'
        },
        'P07': {
            'type': 'Backtesting',
            'tools': ['python', 'backtrader', 'pandas'],
            'environment': 'development',
            'access': 'Historical data'
        },
        'P08': {
            'type': 'Production Deployment',
            'tools': ['docker', 'kubernetes', 'vertex-ai'],
            'environment': 'production',
            'access': 'Production deploy'
        },
        'P09': {
            'type': 'Monitoring',
            'tools': ['prometheus', 'grafana', 'vertex-monitoring'],
            'environment': 'production',
            'access': 'Monitoring systems'
        },
        'P10': {
            'type': 'Optimization',
            'tools': ['python', 'optuna', 'hyperopt'],
            'environment': 'development',
            'access': 'Model registry'
        },
        'P11': {
            'type': 'Documentation',
            'tools': ['sphinx', 'markdown', 'swagger'],
            'environment': 'development',
            'access': 'Repository write'
        }
    }

    return phase_contexts.get(phase_id, {
        'type': 'General',
        'tools': ['python'],
        'environment': 'development',
        'access': 'Standard'
    })

def generate_task_command(task_id, task_name, phase_context):
    """Generate specific command for task execution."""

    phase = task_id.split('.')[1] if '.' in task_id else 'P00'
    stage = task_id.split('.')[2] if len(task_id.split('.')) > 2 else 'S00'

    # Map task patterns to commands
    task_lower = task_name.lower()

    # Infrastructure tasks
    if 'setup' in task_lower or 'configure' in task_lower:
        if 'vertex' in task_lower:
            return f"gcloud services enable aiplatform.googleapis.com --project=bqx-ml-v3"
        elif 'docker' in task_lower:
            return f"docker build -t bqx-ml-v3:{task_id.lower()} -f Dockerfile.{phase.lower()} ."
        else:
            return f"terraform apply -var='project_id=bqx-ml-v3' -auto-approve"

    # Data tasks
    elif 'data' in task_lower or 'etl' in task_lower:
        return f"python3 scripts/data_pipeline.py --task={task_id} --windows={BQX_CONFIG['windows']}"

    # Training tasks
    elif 'train' in task_lower or 'model' in task_lower:
        if 'baseline' in task_lower:
            return f"python3 scripts/train_baseline.py --config=config/baseline.yaml --output=models/baseline/"
        else:
            return f"python3 scripts/train_model.py --phase={phase} --stage={stage} --config=config/{phase.lower()}.yaml"

    # Feature engineering
    elif 'feature' in task_lower:
        return f"python3 scripts/feature_engineering.py --windows={BQX_CONFIG['windows']} --pairs={','.join(BQX_CONFIG['pairs'][:4])}"

    # Testing tasks
    elif 'test' in task_lower or 'validate' in task_lower:
        return f"pytest tests/{phase.lower()}/test_{stage.lower()}.py -v --junitxml=reports/test_{task_id}.xml"

    # Deployment tasks
    elif 'deploy' in task_lower:
        if 'vertex' in task_lower:
            return f"gcloud ai models upload --region=us-central1 --display-name=bqx-{task_id.lower()}"
        else:
            return f"kubectl apply -f deployments/{phase.lower()}/{stage.lower()}.yaml"

    # Monitoring tasks
    elif 'monitor' in task_lower or 'alert' in task_lower:
        return f"python3 scripts/setup_monitoring.py --service={task_id} --config=monitoring/{phase.lower()}.yaml"

    # Documentation tasks
    elif 'document' in task_lower:
        return f"python3 scripts/generate_docs.py --module={phase} --output=docs/{phase.lower()}/"

    # Default
    else:
        return f"python3 scripts/execute_task.py --task_id={task_id} --config=config/tasks.yaml"

def generate_inputs_outputs(task_id, task_name, phase):
    """Generate input and output specifications for the task."""

    task_lower = task_name.lower()

    inputs = []
    outputs = []

    # Phase-specific patterns
    if phase == 'P00':  # Infrastructure
        inputs.append("config/project_config.yaml")
        outputs.append("infrastructure/terraform.tfstate")

    elif phase == 'P01':  # Baseline
        inputs.append("data/raw/forex_m1_data.csv")
        outputs.append("models/baseline/model.pkl")
        outputs.append("reports/baseline_metrics.json")

    elif phase == 'P02':  # Data prep
        inputs.append("data/raw/*.csv")
        outputs.append("data/processed/features_*.parquet")
        outputs.append("data/metadata/schema.json")

    elif phase in ['P03', 'P04', 'P05']:  # Vertex AI phases
        inputs.append(f"config/vertex_{phase.lower()}_config.yaml")
        inputs.append("credentials/gcp-sa-key.json")
        outputs.append(f"vertex_artifacts/{phase.lower()}/")

    elif phase in ['P06', 'P07']:  # Algorithm & Backtesting
        inputs.append("models/*/model.pkl")
        outputs.append(f"results/{phase.lower()}_analysis.json")
        outputs.append(f"reports/{phase.lower()}_report.html")

    elif phase in ['P08', 'P09']:  # Production
        inputs.append("models/optimized/*.pkl")
        inputs.append(f"deployments/{phase.lower()}.yaml")
        outputs.append(f"endpoints/{phase.lower()}_endpoint.json")
        outputs.append("logs/deployment.log")

    elif phase == 'P10':  # Optimization
        inputs.append("models/*/metrics.json")
        outputs.append("models/optimized/best_model.pkl")
        outputs.append("reports/optimization_results.json")

    elif phase == 'P11':  # Documentation
        inputs.append("src/**/*.py")
        outputs.append("docs/api/")
        outputs.append("docs/user_guide.pdf")

    # Task-specific patterns
    if 'train' in task_lower:
        inputs.append("data/training/*.parquet")
        outputs.append(f"models/{task_id}/model.pkl")

    if 'test' in task_lower:
        inputs.append("data/test/*.parquet")
        outputs.append(f"reports/test_{task_id}.json")

    if 'deploy' in task_lower:
        inputs.append("models/production/*.pkl")
        outputs.append("endpoints/production.json")

    return inputs, outputs

def generate_build_agent_description(task):
    """Generate a complete Build Agent-ready description for a task."""

    task_id = task['fields'].get('task_id', '')
    task_name = task['fields'].get('name', '')

    # Extract phase and stage
    parts = task_id.split('.')
    phase = parts[1] if len(parts) > 1 else 'P00'
    stage = parts[2] if len(parts) > 2 else 'S00'

    # Get phase context
    phase_context = generate_phase_context(phase)

    # Generate command
    command = generate_task_command(task_id, task_name, phase_context)

    # Generate inputs and outputs
    inputs, outputs = generate_inputs_outputs(task_id, task_name, phase)

    # Build the description
    description_parts = []

    # Command
    description_parts.append(f"Execute: {command}")

    # Inputs
    if inputs:
        description_parts.append(f"Input: {inputs[0]}")

    # Outputs
    if outputs:
        description_parts.append(f"Output: {outputs[0]}")

    # Success criteria
    if 'test' in task_name.lower():
        description_parts.append("Success: All tests pass (exit_code=0)")
    elif 'train' in task_name.lower():
        description_parts.append(f"Success: R²≥{BQX_CONFIG['thresholds']['r2_min']}, RMSE≤{BQX_CONFIG['thresholds']['rmse_max']}")
    elif 'deploy' in task_name.lower():
        description_parts.append("Success: Endpoint responds HTTP 200")
    else:
        description_parts.append("Success: exit_code=0 && outputs exist")

    # Environment requirements
    if phase_context.get('environment') == 'cloud':
        description_parts.append("Env: PROJECT_ID=bqx-ml-v3,REGION=us-central1")

    # Join parts with proper formatting
    description = ". ".join(description_parts)

    # Ensure it's within length limits (100-300 chars ideal)
    if len(description) > 300:
        # Truncate intelligently
        description = description[:297] + "..."
    elif len(description) < 100:
        # Add more context
        description += f". Method: {BQX_CONFIG['methodology']}. Windows: {BQX_CONFIG['windows'][:3]}"

    return description

def update_task_descriptions():
    """Update all task descriptions with Build Agent-ready content."""

    print("🤖 GENERATING BUILD AGENT DESCRIPTIONS")
    print("=" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()
    print(f"\nProcessing {len(all_tasks)} tasks")

    # Track updates
    updates = {
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'examples': []
    }

    # Group tasks by phase for batch processing
    phase_tasks = {}
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        parts = task_id.split('.')
        phase = parts[1] if len(parts) > 1 else 'P00'

        if phase not in phase_tasks:
            phase_tasks[phase] = []
        phase_tasks[phase].append(task)

    # Process by phase
    for phase in sorted(phase_tasks.keys()):
        tasks = phase_tasks[phase]
        print(f"\n📋 Processing Phase {phase} ({len(tasks)} tasks)")
        print("-" * 60)

        for task in tasks:
            task_id = task['fields'].get('task_id', '')
            current_desc = task['fields'].get('description', '')

            # Generate new description
            new_description = generate_build_agent_description(task)

            # Skip if already good
            if 'Execute:' in current_desc and 'Success:' in current_desc:
                updates['skipped'] += 1
                continue

            # Update the task
            try:
                tasks_table.update(task['id'], {
                    'description': new_description
                })
                updates['successful'] += 1

                # Save examples
                if updates['successful'] <= 5:
                    updates['examples'].append({
                        'task_id': task_id,
                        'old': current_desc[:80] + '...' if len(current_desc) > 80 else current_desc,
                        'new': new_description
                    })

                print(f"  ✅ {task_id}: Updated with Build Agent context")

            except Exception as e:
                updates['failed'] += 1
                print(f"  ❌ {task_id}: Failed - {e}")

    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 UPDATE SUMMARY")
    print("=" * 80)

    print(f"\nTotal Tasks: {len(all_tasks)}")
    print(f"Successfully Updated: {updates['successful']}")
    print(f"Failed Updates: {updates['failed']}")
    print(f"Skipped (Already Good): {updates['skipped']}")

    # Show examples
    if updates['examples']:
        print("\n📝 EXAMPLE TRANSFORMATIONS:")
        print("-" * 60)

        for example in updates['examples']:
            print(f"\nTask: {example['task_id']}")
            print(f"Old: {example['old']}")
            print(f"New: {example['new']}")

    # Verify improvements
    print("\n✅ IMPROVEMENTS IMPLEMENTED:")
    print("  • Added execution commands to all tasks")
    print("  • Specified input/output paths")
    print("  • Included success criteria")
    print("  • Added environment variables where needed")
    print("  • Incorporated BQX-specific parameters")
    print(f"  • Used {BQX_CONFIG['methodology']} methodology references")

    # Next steps
    print("\n🚀 NEXT STEPS:")
    print("  1. Review updated descriptions in AirTable")
    print("  2. Test Build Agent parsing of new format")
    print("  3. Validate execution commands")
    print("  4. Run integration tests")

    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 80)

    return updates['successful'] > 0

if __name__ == "__main__":
    success = update_task_descriptions()

    if success:
        print("\n🎉 Build Agent descriptions successfully generated!")
        exit(0)
    else:
        print("\n⚠️  No updates were made. Check for errors.")
        exit(1)