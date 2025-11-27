#!/usr/bin/env python3
"""
AirTable Sync Service for Claude Code Integration
Provides bi-directional sync between AirTable and local project management
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

try:
    from pyairtable import Api
    PYAIRTABLE_AVAILABLE = True
except ImportError:
    PYAIRTABLE_AVAILABLE = False
    print("⚠️ pyairtable not installed. Run: pip install pyairtable")

class AirTableSync:
    """Main sync service for AirTable integration"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AirTable sync service"""
        self.api_key = api_key or os.environ.get('AIRTABLE_API_KEY')
        self.base_id = 'app3tpP9F3BrP1P7j'  # BQX ML V3 base

        if not self.api_key:
            print("❌ AIRTABLE_API_KEY not found")
            print("To set it up:")
            print("1. Get your API key from: https://airtable.com/create/tokens")
            print("2. Run: export AIRTABLE_API_KEY='your_key_here'")
            print("3. Or add to .env file")
            sys.exit(1)

        if PYAIRTABLE_AVAILABLE:
            self.api = Api(self.api_key)
            self.tasks_table = self.api.table(self.base_id, 'Tasks')
            self.phases_table = self.api.table(self.base_id, 'Phases')
            self.stages_table = self.api.table(self.base_id, 'Stages')
        else:
            print("❌ pyairtable not available")
            sys.exit(1)

    def get_next_task(self, assigned_to: str = "CE") -> Optional[Dict]:
        """Fetch highest priority pending task"""
        try:
            tasks = self.tasks_table.all(
                formula=f"AND({{status}}='Pending', {{assigned_to}}='{assigned_to}')",
                sort=['-priority', 'created_time']
            )
            return tasks[0] if tasks else None
        except Exception as e:
            print(f"❌ Error fetching task: {e}")
            return None

    def get_pending_tasks(self, limit: int = 10) -> List[Dict]:
        """Get list of pending tasks"""
        try:
            tasks = self.tasks_table.all(
                formula="{status}='Pending'",
                sort=['-priority', 'created_time'],
                max_records=limit
            )
            return tasks
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
            return []

    def update_task_status(self, task_id: str, status: str, notes: str = ""):
        """Update task status in real-time"""
        try:
            update = {
                'status': status,
                'last_updated': datetime.now().isoformat(),
            }

            if notes:
                update['execution_notes'] = notes

            if status == 'Completed':
                update['completion_time'] = datetime.now().isoformat()
                update['completion_percentage'] = 100
            elif status == 'In Progress':
                update['start_time'] = datetime.now().isoformat()

            self.tasks_table.update(task_id, update)
            print(f"✅ Updated task {task_id} to {status}")

        except Exception as e:
            print(f"❌ Error updating task: {e}")

    def log_artifact(self, task_id: str, artifact_path: str):
        """Add generated artifacts to task"""
        try:
            task = self.tasks_table.get(task_id)
            artifacts = task['fields'].get('artifacts', '')

            # Append new artifact
            if artifacts:
                new_artifacts = f"{artifacts}, {artifact_path}"
            else:
                new_artifacts = artifact_path

            self.tasks_table.update(task_id, {'artifacts': new_artifacts})
            print(f"✅ Added artifact {artifact_path} to task {task_id}")

        except Exception as e:
            print(f"❌ Error logging artifact: {e}")

    def create_task(self, name: str, description: str, phase: str = "P03",
                   stage: str = "S01", priority: str = "Medium"):
        """Create a new task in AirTable"""
        try:
            task_fields = {
                'name': name,
                'description': description,
                'status': 'Pending',
                'priority': priority,
                'assigned_to': 'CE',
                'phase_link': [f"rec{phase}Phase"],
                'stage_link': [f"rec{phase}{stage}Stage"],
                'plan_link': ['recPlanBQXMLV3'],
                'created_time': datetime.now().isoformat(),
                'score': 50
            }

            result = self.tasks_table.create(task_fields)
            print(f"✅ Created task: {name}")
            return result

        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return None

    def get_project_status(self) -> Dict[str, Any]:
        """Get overall project status from AirTable"""
        try:
            all_tasks = self.tasks_table.all()

            total = len(all_tasks)
            completed = len([t for t in all_tasks if t['fields'].get('status') == 'Completed'])
            in_progress = len([t for t in all_tasks if t['fields'].get('status') == 'In Progress'])
            pending = len([t for t in all_tasks if t['fields'].get('status') == 'Pending'])
            blocked = len([t for t in all_tasks if t['fields'].get('status') == 'Blocked'])

            return {
                'total_tasks': total,
                'completed': completed,
                'in_progress': in_progress,
                'pending': pending,
                'blocked': blocked,
                'completion_percentage': (completed / total * 100) if total > 0 else 0,
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ Error getting project status: {e}")
            return {}

    def sync_smart_vertex_tasks(self):
        """Update AirTable with Smart Vertex AI tasks"""
        smart_tasks = [
            {
                'name': 'T03.01 - Deploy 5 Critical Vertex AI Endpoints',
                'description': 'Deploy EUR_USD_90, GBP_USD_90, USD_JPY_90, EUR_GBP_90, EUR_JPY_90 using n1-standard-2. Cost: $342/month.',
                'status': 'In Progress',
                'priority': 'Critical',
                'assigned_to': 'BA'
            },
            {
                'name': 'T03.02 - Configure Vertex AI Batch Predictions',
                'description': 'Setup batch prediction jobs for 191 remaining models. Hourly refresh. Cost: $100/month.',
                'status': 'Pending',
                'priority': 'High',
                'assigned_to': 'BA'
            },
            {
                'name': 'T03.03 - Create Cloud Scheduler for Batch Jobs',
                'description': 'Configure hourly cron jobs to trigger batch predictions. Cost: $10/month.',
                'status': 'Pending',
                'priority': 'High',
                'assigned_to': 'BA'
            },
            {
                'name': 'T03.04 - Deploy Cloud Functions Unified API',
                'description': 'Create single API endpoint to serve all 196 model predictions. Cost: $20/month.',
                'status': 'Pending',
                'priority': 'High',
                'assigned_to': 'BA'
            },
            {
                'name': 'T03.05 - Implement BigQuery Prediction Cache',
                'description': 'Setup BigQuery tables to cache all predictions for fast retrieval. Cost: $20/month.',
                'status': 'Pending',
                'priority': 'Medium',
                'assigned_to': 'BA'
            },
            {
                'name': 'T03.06 - Configure Cost Monitoring',
                'description': 'Setup budget alerts to ensure staying within $442/month budget.',
                'status': 'Pending',
                'priority': 'Medium',
                'assigned_to': 'CE'
            }
        ]

        for task in smart_tasks:
            existing = self.tasks_table.all(formula=f"{{name}}='{task['name']}'")
            if not existing:
                self.create_task(**task)
            else:
                print(f"Task already exists: {task['name']}")

def main():
    """Main entry point for sync service"""
    import argparse

    parser = argparse.ArgumentParser(description='AirTable Sync Service')
    parser.add_argument('--sync', action='store_true', help='Sync Smart Vertex AI tasks')
    parser.add_argument('--status', action='store_true', help='Get project status')
    parser.add_argument('--next', action='store_true', help='Get next pending task')
    parser.add_argument('--list', action='store_true', help='List pending tasks')
    parser.add_argument('--update', help='Update task status (format: task_id:status)')

    args = parser.parse_args()

    # Initialize sync service
    sync = AirTableSync()

    if args.sync:
        sync.sync_smart_vertex_tasks()

    elif args.status:
        status = sync.get_project_status()
        print("\n📊 PROJECT STATUS")
        print(f"Total Tasks: {status.get('total_tasks', 0)}")
        print(f"Completed: {status.get('completed', 0)} ({status.get('completion_percentage', 0):.1f}%)")
        print(f"In Progress: {status.get('in_progress', 0)}")
        print(f"Pending: {status.get('pending', 0)}")
        print(f"Blocked: {status.get('blocked', 0)}")

    elif args.next:
        task = sync.get_next_task()
        if task:
            print(f"\n📋 NEXT TASK:")
            print(f"Name: {task['fields'].get('name', 'Unknown')}")
            print(f"Description: {task['fields'].get('description', 'No description')}")
            print(f"Priority: {task['fields'].get('priority', 'Medium')}")
            print(f"ID: {task['id']}")
        else:
            print("No pending tasks found")

    elif args.list:
        tasks = sync.get_pending_tasks()
        print(f"\n📋 PENDING TASKS ({len(tasks)}):")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['fields'].get('name', 'Unknown')} - {task['fields'].get('priority', 'Medium')}")

    elif args.update:
        parts = args.update.split(':')
        if len(parts) == 2:
            task_id, status = parts
            sync.update_task_status(task_id, status)
        else:
            print("Invalid format. Use: task_id:status")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()