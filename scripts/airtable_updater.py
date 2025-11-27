#!/usr/bin/env python3
"""
MANDATORY AirTable Real-Time Updater
Per CE directive 20251127_0135 - CRITICAL COMPLIANCE
User Mandate: "Keep AirTable current at ALL times"
"""

from pyairtable import Api
import json
from datetime import datetime
import os

class AirTableUpdater:
    """
    MANDATORY: Real-time AirTable updates for BQX ML V3 project
    """

    def __init__(self):
        """Initialize AirTable connection with credentials"""
        secrets_path = '/home/micha/bqx_ml_v3/.secrets/github_secrets.json'

        if not os.path.exists(secrets_path):
            raise FileNotFoundError(f"Credentials file not found: {secrets_path}")

        with open(secrets_path, 'r') as f:
            secrets = json.load(f)

        self.api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
        self.base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']

        # Initialize API connection
        self.api = Api(self.api_key)
        self.base = self.api.base(self.base_id)

        # Get all tables
        self.tasks_table = self.base.table('Tasks')

        print("✅ AirTable connection initialized")

    def update_task(self, task_id, status, notes_append, priority=None):
        """
        Update a specific task in AirTable

        Args:
            task_id: Task identifier (e.g., "MP03.P01.S01.T01")
            status: "Todo", "In Progress", or "Done"
            notes_append: Text to append to notes
            priority: Optional - "Critical", "High", "Medium", or "Low"
        """
        try:
            all_tasks = self.tasks_table.all()

            for record in all_tasks:
                if record['fields'].get('task_id') == task_id:
                    # Get current notes
                    current_notes = record['fields'].get('notes', '')

                    # Append new notes with timestamp
                    timestamp = datetime.now().isoformat()
                    new_notes = f"{current_notes}\n\n[{timestamp}]\n{notes_append}"

                    # Prepare update
                    update_fields = {
                        'status': status,
                        'notes': new_notes
                    }

                    if priority:
                        update_fields['priority'] = priority

                    # Update record
                    self.tasks_table.update(record['id'], update_fields)
                    print(f"✅ AirTable updated: {task_id} -> {status}")
                    return True

            print(f"⚠️ Task {task_id} not found in AirTable")
            return False

        except Exception as e:
            print(f"❌ AirTable update error: {e}")
            return False

    def log_model_result(self, pair, window, metrics, approach='BQX-only'):
        """
        Log model training results to AirTable

        Args:
            pair: Currency pair (e.g., 'EURUSD')
            window: Prediction window (45, 90, etc.)
            metrics: Dictionary with r2, dir_acc, rmse, time
            approach: 'BQX-only', 'Smart Dual', etc.
        """
        # Map to appropriate task (adjust mapping as needed)
        task_mapping = {
            45: 'MP03.P04.S01.T01',
            90: 'MP03.P04.S01.T02',
            180: 'MP03.P04.S01.T03',
            360: 'MP03.P04.S01.T04',
            720: 'MP03.P04.S01.T05',
            1440: 'MP03.P04.S01.T06',
            2880: 'MP03.P04.S01.T07'
        }

        task_id = task_mapping.get(window, 'MP03.P04.S01.T01')

        # Determine quality gate status
        quality_gates = 'PASSED' if metrics.get('r2', 0) >= 0.35 else 'FAILED'

        # Create detailed notes
        notes = f"""Model Training Result - {pair}-{window}
================================================
Approach: {approach}
R² Score: {metrics.get('r2', 0):.4f}
Directional Accuracy: {metrics.get('dir_acc', 0):.2%}
RMSE: {metrics.get('rmse', 0):.4f}
Training Time: {metrics.get('time', 0):.2f}s
Quality Gates: {quality_gates}
================================================"""

        # Determine status based on completion
        status = 'Done' if quality_gates == 'PASSED' else 'In Progress'

        self.update_task(task_id, status, notes)

    def log_progress(self, operation, message, task_id='MP03.P01.S01.T01'):
        """
        Log general progress updates

        Args:
            operation: Name of operation (e.g., 'Data Generation')
            message: Progress message
            task_id: Relevant task ID
        """
        notes = f"{operation}: {message}"
        self.update_task(task_id, 'In Progress', notes)

    def test_connection(self):
        """Test AirTable connection and update capability"""
        try:
            # Try to fetch tasks
            tasks = self.tasks_table.all()
            print(f"✅ Connection test successful!")
            print(f"   Found {len(tasks)} tasks in AirTable")

            # Show first few tasks
            if tasks:
                print("\n   Sample tasks:")
                for task in tasks[:3]:
                    fields = task['fields']
                    print(f"   - {fields.get('task_id', 'N/A')}: {fields.get('name', 'N/A')[:50]}")

            # Test update with timestamp
            test_task_id = 'MP03.P01.S01.T01'
            test_note = f"Connection test from Builder Agent - {datetime.now().isoformat()}"

            if self.update_task(test_task_id, 'In Progress', test_note):
                print(f"\n✅ Update test successful!")
                print(f"   Updated task {test_task_id} with test note")
                return True

            return False

        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def batch_update_models(self, results_list):
        """
        Batch update multiple model results

        Args:
            results_list: List of dicts with pair, window, metrics
        """
        for result in results_list:
            self.log_model_result(
                result['pair'],
                result['window'],
                result['metrics'],
                result.get('approach', 'BQX-only')
            )

    def mark_phase_complete(self, phase_name, summary):
        """
        Mark an entire phase as complete with summary

        Args:
            phase_name: Name of phase
            summary: Summary of results
        """
        # Find relevant phase task
        notes = f"""Phase Complete: {phase_name}
================================================
{summary}
================================================"""

        # Update main phase task
        self.update_task('MP03.P01.S01.T01', 'Done', notes)


# Main execution for testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("AIRTABLE UPDATER - CONNECTION TEST")
    print("Per CE directive 20251127_0135 - MANDATORY")
    print("="*60)

    try:
        # Initialize updater
        updater = AirTableUpdater()

        # Test connection
        if updater.test_connection():
            print("\n✅ AIRTABLE UPDATER READY FOR USE")
            print("   All model training will now update AirTable in real-time")

            # Log current operation
            updater.log_progress(
                'System Initialization',
                'AirTable updater configured and tested successfully',
                'MP03.P01.S01.T01'
            )

            # Save instance for import
            print("\n📌 Usage in other scripts:")
            print("   from airtable_updater import AirTableUpdater")
            print("   airtable = AirTableUpdater()")
            print("   airtable.log_model_result(pair, window, metrics)")
        else:
            print("\n⚠️ Connection test had issues")

    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()