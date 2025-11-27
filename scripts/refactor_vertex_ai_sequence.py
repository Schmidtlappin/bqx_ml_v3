#!/usr/bin/env python3
"""
Refactor Vertex AI Migration Tasks to properly queue into project work sequence.
Move from P12-P16 to earlier phases where infrastructure should be set up.
"""

import os
import subprocess
from pyairtable import Api

# Get credentials from GCP Secrets Manager
def get_secret(secret_name):
    try:
        result = subprocess.run(
            [f"gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY") or get_secret("bqx-ml-airtable-token")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID") or get_secret("bqx-ml-airtable-base-id")

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials")

api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(BASE_ID, "Tasks")

# Define the refactoring map - moving Vertex AI tasks to earlier phases
# Infrastructure should come early (P03), then containerization (P04), etc.
REFACTOR_MAP = {
    # Infrastructure Setup (was P12, now P03.S03)
    "MP03.P12.S01.T01": "MP03.P03.S03.T01",  # Enable Vertex AI APIs
    "MP03.P12.S01.T02": "MP03.P03.S03.T02",  # Create GCS buckets
    "MP03.P12.S01.T03": "MP03.P03.S03.T03",  # Configure Artifact Registry
    "MP03.P12.S01.T04": "MP03.P03.S03.T04",  # Set up service accounts

    # Containerization (was P13, now P04.S03)
    "MP03.P13.S01.T01": "MP03.P04.S03.T01",  # Create Dockerfiles
    "MP03.P13.S01.T02": "MP03.P04.S03.T02",  # Build container images
    "MP03.P13.S01.T03": "MP03.P04.S03.T03",  # Push images to Registry
    "MP03.P13.S01.T04": "MP03.P04.S03.T04",  # Validate containers

    # Pipeline Development (was P14, now P05.S03)
    "MP03.P14.S01.T01": "MP03.P05.S03.T01",  # Testing pipeline
    "MP03.P14.S01.T02": "MP03.P05.S03.T02",  # Training pipeline
    "MP03.P14.S01.T03": "MP03.P05.S03.T03",  # Prediction pipeline
    "MP03.P14.S01.T04": "MP03.P05.S03.T04",  # Pipeline orchestration

    # Model Deployment (was P15, now P08.S03)
    "MP03.P15.S01.T01": "MP03.P08.S03.T01",  # Create endpoints
    "MP03.P15.S01.T02": "MP03.P08.S03.T02",  # Deploy models
    "MP03.P15.S01.T03": "MP03.P08.S03.T03",  # Configure auto-scaling
    "MP03.P15.S01.T04": "MP03.P08.S03.T04",  # Set up load balancing

    # Operations & Monitoring (was P16, now P09.S03)
    "MP03.P16.S01.T01": "MP03.P09.S03.T01",  # Model monitoring
    "MP03.P16.S01.T02": "MP03.P09.S03.T02",  # Alerting policies
    "MP03.P16.S01.T03": "MP03.P09.S03.T03",  # Implement logging
    "MP03.P16.S01.T04": "MP03.P09.S03.T04",  # Create dashboards
}

# Phase descriptions for notes
PHASE_DESCRIPTIONS = {
    "MP03.P03.S03": "Vertex AI Infrastructure Setup (Early Phase)",
    "MP03.P04.S03": "Vertex AI Containerization",
    "MP03.P05.S03": "Vertex AI Pipeline Development",
    "MP03.P08.S03": "Vertex AI Model Deployment",
    "MP03.P09.S03": "Vertex AI Operations & Monitoring"
}

def refactor_vertex_ai_tasks():
    """Refactor all Vertex AI tasks to their new positions in the work sequence."""

    print("🔄 REFACTORING VERTEX AI TASKS TO PROPER SEQUENCE")
    print("=" * 60)
    print("\nMoving tasks from end phases (P12-P16) to integrated phases (P03-P09)")
    print("-" * 60)

    updated_count = 0
    failed_count = 0

    for old_id, new_id in REFACTOR_MAP.items():
        try:
            # Find the task with the old ID
            tasks = tasks_table.all(formula=f"{{task_id}}='{old_id}'")

            if not tasks:
                print(f"⚠️  Task {old_id} not found in AirTable")
                continue

            task = tasks[0]
            task_record_id = task['id']
            task_name = task['fields'].get('name', 'Unknown')

            # Extract new phase info
            new_phase = ".".join(new_id.split(".")[:3])
            phase_desc = PHASE_DESCRIPTIONS.get(new_phase, "Vertex AI Migration")

            # Update the task with new ID and updated notes
            current_notes = task['fields'].get('notes', '')
            updated_notes = current_notes.replace(old_id, new_id)

            # Add refactoring note
            updated_notes += f"\n\n[Refactored {old_id} → {new_id}]"

            update_fields = {
                "task_id": new_id,
                "notes": updated_notes
            }

            # Update in AirTable
            tasks_table.update(task_record_id, update_fields)
            print(f"✅ Refactored: {old_id} → {new_id} ({task_name})")
            updated_count += 1

        except Exception as e:
            print(f"❌ Failed to refactor {old_id}: {e}")
            failed_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Successfully refactored: {updated_count} tasks")
    if failed_count > 0:
        print(f"❌ Failed to refactor: {failed_count} tasks")

    print("\n📋 New Vertex AI Task Sequence:")
    print("  P03.S03: Infrastructure Setup (4 tasks)")
    print("  P04.S03: Containerization (4 tasks)")
    print("  P05.S03: Pipeline Development (4 tasks)")
    print("  P08.S03: Model Deployment (4 tasks)")
    print("  P09.S03: Operations & Monitoring (4 tasks)")
    print("\n✅ Tasks now properly integrated into main work sequence!")
    print("=" * 60)

    return updated_count

if __name__ == "__main__":
    refactored = refactor_vertex_ai_tasks()

    if refactored > 0:
        print("\n🎯 Vertex AI tasks successfully integrated into work sequence!")
        print("The migration infrastructure will now be set up at the appropriate phases.")
    else:
        print("\n⚠️ No tasks were refactored. They may already be in the correct sequence.")