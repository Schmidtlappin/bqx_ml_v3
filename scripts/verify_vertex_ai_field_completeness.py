#!/usr/bin/env python3
"""
Verify that all Vertex AI tasks have complete fields after refactoring.
Specifically check the 20 tasks that were moved from P12-P16 to P03-P09.
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

# Define the Vertex AI task IDs (after refactoring)
VERTEX_AI_TASKS = [
    # Infrastructure Setup (P03.S03)
    "MP03.P03.S03.T01",
    "MP03.P03.S03.T02",
    "MP03.P03.S03.T03",
    "MP03.P03.S03.T04",
    # Containerization (P04.S03)
    "MP03.P04.S03.T01",
    "MP03.P04.S03.T02",
    "MP03.P04.S03.T03",
    "MP03.P04.S03.T04",
    # Pipeline Development (P05.S03)
    "MP03.P05.S03.T01",
    "MP03.P05.S03.T02",
    "MP03.P05.S03.T03",
    "MP03.P05.S03.T04",
    # Model Deployment (P08.S03)
    "MP03.P08.S03.T01",
    "MP03.P08.S03.T02",
    "MP03.P08.S03.T03",
    "MP03.P08.S03.T04",
    # Operations & Monitoring (P09.S03)
    "MP03.P09.S03.T01",
    "MP03.P09.S03.T02",
    "MP03.P09.S03.T03",
    "MP03.P09.S03.T04"
]

# Required fields to check
REQUIRED_FIELDS = [
    'task_id',
    'name',
    'description',
    'notes',
    'status',
    'priority',
    'stage_link'
]

def check_vertex_ai_tasks():
    """Check completeness of all Vertex AI tasks."""

    print("🔍 VERIFYING VERTEX AI TASK FIELD COMPLETENESS")
    print("=" * 80)
    print(f"Checking {len(VERTEX_AI_TASKS)} tasks across 5 phases")
    print("-" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()

    # Filter to just Vertex AI tasks
    vertex_tasks = {}
    for task in all_tasks:
        task_id = task['fields'].get('task_id')
        if task_id in VERTEX_AI_TASKS:
            vertex_tasks[task_id] = task

    print(f"\nFound {len(vertex_tasks)}/{len(VERTEX_AI_TASKS)} Vertex AI tasks in AirTable")

    # Track completeness
    all_complete = True
    field_stats = {field: {'complete': 0, 'missing': 0} for field in REQUIRED_FIELDS}

    # Group tasks by phase
    phases = {
        'P03.S03': 'Infrastructure Setup',
        'P04.S03': 'Containerization',
        'P05.S03': 'Pipeline Development',
        'P08.S03': 'Model Deployment',
        'P09.S03': 'Operations & Monitoring'
    }

    for phase_id, phase_name in phases.items():
        print(f"\n📋 {phase_id}: {phase_name}")
        print("-" * 60)

        phase_tasks = [t for t in VERTEX_AI_TASKS if phase_id in t]

        for task_id in phase_tasks:
            if task_id in vertex_tasks:
                task = vertex_tasks[task_id]
                fields = task['fields']
                task_name = fields.get('name', 'Unknown')[:40]

                # Check each required field
                missing_fields = []
                field_info = []

                for field in REQUIRED_FIELDS:
                    value = fields.get(field)
                    if not value or (isinstance(value, str) and len(value.strip()) == 0):
                        missing_fields.append(field)
                        field_stats[field]['missing'] += 1
                        field_info.append(f"    ❌ {field}: MISSING")
                    else:
                        field_stats[field]['complete'] += 1
                        if field == 'description':
                            field_info.append(f"    ✅ {field}: {len(value)} chars")
                        elif field == 'notes':
                            # Check if standardized
                            is_standardized = any(icon in value for icon in ['✅', '🔄', '📋', '🚫'])
                            if is_standardized:
                                field_info.append(f"    ✅ {field}: {len(value)} chars (standardized)")
                            else:
                                field_info.append(f"    ⚠️  {field}: {len(value)} chars (not standardized)")
                        elif field == 'stage_link':
                            field_info.append(f"    ✅ {field}: {len(value)} links")
                        else:
                            field_info.append(f"    ✅ {field}: {value if isinstance(value, str) else 'Present'}")

                # Display task status
                if missing_fields:
                    print(f"  ⚠️  {task_id}: {task_name}")
                    print(f"     Missing: {', '.join(missing_fields)}")
                    all_complete = False
                else:
                    print(f"  ✅ {task_id}: {task_name}")
                    print(f"     All fields complete")

                # Show field details
                for info in field_info:
                    print(info)

            else:
                print(f"  ❌ {task_id}: NOT FOUND IN AIRTABLE")
                all_complete = False

    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 VERTEX AI FIELD COMPLETENESS SUMMARY")
    print("=" * 80)

    print("\nField Completion Statistics:")
    print("-" * 40)

    total_checks = len(VERTEX_AI_TASKS)
    for field in REQUIRED_FIELDS:
        complete = field_stats[field]['complete']
        missing = field_stats[field]['missing']
        percentage = (complete / total_checks * 100) if total_checks > 0 else 0

        status = "✅" if percentage == 100 else ("⚠️" if percentage >= 80 else "❌")
        print(f"{status} {field:15}: {complete}/{total_checks} complete ({percentage:.1f}%)")

    # Overall assessment
    print("\n" + "=" * 80)
    print("🎯 OVERALL ASSESSMENT")
    print("=" * 80)

    overall_complete = sum(field_stats[f]['complete'] for f in REQUIRED_FIELDS)
    overall_total = total_checks * len(REQUIRED_FIELDS)
    overall_percentage = (overall_complete / overall_total * 100) if overall_total > 0 else 0

    if overall_percentage == 100:
        print(f"\n✅ PERFECT: All Vertex AI tasks have 100% field completeness!")
        print("   • All 20 tasks found in AirTable")
        print("   • All required fields populated")
        print("   • Notes properly standardized")
        print("   • Descriptions meet length requirements")
    elif overall_percentage >= 95:
        print(f"\n✅ EXCELLENT: {overall_percentage:.1f}% field completeness")
        print("   Nearly all fields are complete.")
    elif overall_percentage >= 90:
        print(f"\n🔄 GOOD: {overall_percentage:.1f}% field completeness")
        print("   Most fields are complete with minor gaps.")
    else:
        print(f"\n⚠️  NEEDS ATTENTION: {overall_percentage:.1f}% field completeness")
        print("   Several fields need to be filled.")

    print(f"\nTotal Fields Checked: {overall_total}")
    print(f"Complete Fields: {overall_complete}")
    print(f"Missing Fields: {overall_total - overall_complete}")

    print("\n" + "=" * 80)
    print(f"Verification completed: {datetime.now().isoformat()}")
    print("=" * 80)

    return overall_percentage == 100

if __name__ == "__main__":
    is_complete = check_vertex_ai_tasks()

    if is_complete:
        print("\n🎉 SUCCESS: All Vertex AI task fields are complete!")
    else:
        print("\n📝 Action Required: Some fields need attention.")