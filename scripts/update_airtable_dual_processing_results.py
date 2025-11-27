#!/usr/bin/env python3
"""
Update AirTable with dual processing experiment results and decision.
This is CRITICAL for maintaining project truth per user mandate.
"""

import os
import sys
from pathlib import Path
from pyairtable import Api
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to load credentials from various locations
def load_credentials():
    env_paths = [
        Path('.env'),
        Path('../.env'),
        Path(os.path.expanduser('~/.env')),
        Path('/home/micha/bqx_ml_v3/.env'),
        Path('/home/micha/.env')
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                env_content = f.read()
                api_key = None
                base_id = None
                for line in env_content.split('\n'):
                    if 'AIRTABLE_API_KEY' in line:
                        api_key = line.split('=')[1].strip()
                    elif 'AIRTABLE_BASE_ID' in line:
                        base_id = line.split('=')[1].strip()
                if api_key and base_id:
                    return api_key, base_id

    # Try environment variables
    api_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')
    if api_key and base_id:
        return api_key, base_id

    print("⚠️  Could not find AirTable credentials")
    print("📝 CRITICAL UPDATES REQUIRED IN AIRTABLE:")
    return None, None

def print_required_updates():
    """Print the updates that need to be made to AirTable."""

    print("\n" + "="*80)
    print("AIRTABLE CRITICAL UPDATES - DUAL PROCESSING EXPERIMENT RESULTS")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Task updates
    task_updates = [
        {
            "task_id": "MP03.P01.S01.T01",
            "status": "Done",
            "notes_addition": """

📊 DUAL PROCESSING EXPERIMENT RESULTS (2025-11-27 00:30):
================================================
Completed comprehensive comparison of BQX-only vs Dual Processing approaches:

PERFORMANCE METRICS:
• BQX-only (14 features): R² = 0.4648 ✅ (132.8% of target)
• Dual Processing (28 features): R² = 0.2692 ❌ (76.9% of target)
• Performance Delta: BQX-only is 72.7% BETTER

DIRECTIONAL ACCURACY:
• BQX-only: 74.16% ✅
• Dual Processing: 68.65% ✅
• Delta: BQX-only is 7.4% better

FEATURE IMPORTANCE ANALYSIS:
• BQX features: 63.2% of model importance
• IDX features: 36.8% of model importance
• Top 10 features: 8 are BQX, only 2 are IDX

DECISION per PERFORMANCE_FIRST mandate:
✅ PROCEED WITH BQX-ONLY APPROACH for all 196 models

VERIFICATION:
• Created table: bqx_ml_v3_models.eurusd_45_dual_train (9,761 rows)
• Created scripts: prepare_training_dataset_dual.py, train_dual_processing_model.py
• Comprehensive report: /sandbox/DUAL_PROCESSING_RESULTS_REPORT.md
"""
        },
        {
            "task_id": "MP03.P01.S01.T02",
            "status": "In Progress",
            "notes_addition": """

📌 MODEL EVALUATION UPDATE (2025-11-27):
Dual processing evaluation complete. BQX-only validated as superior approach.
Next: Implement evaluation framework for all 196 models using BQX-only.
"""
        },
        {
            "task_id": "MP03.P02.S01.T01",
            "status": "In Progress",
            "notes_addition": """

📌 FEATURE ENGINEERING DECISION (2025-11-27):
After empirical testing, BQX features proven optimal.
IDX features add noise rather than signal.
Proceeding with 14 BQX momentum features for all models.
"""
        },
        {
            "task_id": "MP03.P04.S01.T01",
            "status": "In Progress",
            "notes_addition": """

📌 MODEL TRAINING PIPELINE UPDATE (2025-11-27):
Based on dual processing experiment:
• Configuration: BQX-only with 14 features
• Baseline hyperparameters from EURUSD validated
• Expected R² ≥ 0.35 for all 196 models
• Training time: ~20 seconds per model
"""
        }
    ]

    print("📋 TASKS REQUIRING IMMEDIATE UPDATE:\n")
    for i, task in enumerate(task_updates, 1):
        print(f"{i}. Task ID: {task['task_id']}")
        print(f"   Status: {task['status']}")
        print(f"   Notes to ADD (append to existing):")
        print("   " + "-"*70)
        for line in task['notes_addition'].strip().split('\n'):
            if line.strip():
                print(f"   {line}")
        print("   " + "-"*70)
        print()

    # New tasks to create
    print("\n📝 NEW TASKS TO CREATE (if not exists):\n")

    new_tasks = [
        {
            "task_id": "MP03.P01.S01.T03",
            "task_name": "Scale BQX-only pipeline to 196 models",
            "status": "In Progress",
            "phase": "P01",
            "stage": "S01",
            "notes": """Authorized 2025-11-27 00:35 to scale BQX-only approach.
Target: 196 models (28 pairs × 7 windows)
Expected completion: 6 hours
Performance target: R² ≥ 0.35 for all models"""
        },
        {
            "task_id": "MP03.P01.S01.T04",
            "task_name": "Document model performance metrics",
            "status": "Todo",
            "phase": "P01",
            "stage": "S01",
            "notes": """Track for each of 196 models:
• R² score
• Directional accuracy
• RMSE
• Training time
• Any hyperparameter adjustments needed"""
        }
    ]

    for task in new_tasks:
        print(f"Task ID: {task['task_id']}")
        print(f"Task Name: {task['task_name']}")
        print(f"Status: {task['status']}")
        print(f"Phase: {task['phase']}")
        print(f"Stage: {task['stage']}")
        print(f"Notes: {task['notes']}")
        print("-" * 70)
        print()

    # Performance tracking table
    print("\n📊 PERFORMANCE TRACKING TABLE TO CREATE:\n")
    print("Table Name: 'Model Performance Metrics'")
    print("Columns:")
    print("  - Currency Pair (e.g., EURUSD)")
    print("  - Window (45, 90, 180, 360, 720, 1440, 2880)")
    print("  - Approach (BQX-only)")
    print("  - R² Score")
    print("  - Directional Accuracy")
    print("  - RMSE")
    print("  - Training Time (seconds)")
    print("  - Quality Gate Status (Pass/Fail)")
    print("  - Timestamp")
    print()

    # Initial row for the table
    print("INITIAL ROW TO ADD:")
    print("  Currency Pair: EURUSD")
    print("  Window: 45")
    print("  Approach: BQX-only")
    print("  R² Score: 0.4648")
    print("  Directional Accuracy: 74.16%")
    print("  RMSE: 1.7172")
    print("  Training Time: 0.10")
    print("  Quality Gate Status: PASS")
    print(f"  Timestamp: 2025-11-27 00:00:00")
    print()

    print("="*80)
    print("⚠️  CRITICAL: All above updates MUST be recorded in AirTable")
    print("This maintains project TRUTH per user mandate")
    print("="*80)

def update_airtable_with_results():
    """Attempt to update AirTable with dual processing results."""

    try:
        api_key, base_id = load_credentials()

        if not api_key or not base_id:
            # Print manual update instructions
            print_required_updates()
            return False

        api = Api(api_key)
        table = api.table(base_id, 'Tasks')

        # Get all records
        records = table.all()
        updates_made = 0

        # Dual processing results note
        dual_processing_results = """

📊 DUAL PROCESSING EXPERIMENT RESULTS (2025-11-27 00:30):
================================================
Completed comprehensive comparison of BQX-only vs Dual Processing approaches:

PERFORMANCE METRICS:
• BQX-only (14 features): R² = 0.4648 ✅ (132.8% of target)
• Dual Processing (28 features): R² = 0.2692 ❌ (76.9% of target)
• Performance Delta: BQX-only is 72.7% BETTER

DIRECTIONAL ACCURACY:
• BQX-only: 74.16% ✅
• Dual Processing: 68.65% ✅
• Delta: BQX-only is 7.4% better

FEATURE IMPORTANCE ANALYSIS:
• BQX features: 63.2% of model importance
• IDX features: 36.8% of model importance
• Top 10 features: 8 are BQX, only 2 are IDX

TECHNICAL INSIGHTS:
• IDX features introduce noise that obscures momentum signals
• BQX already encodes IDX information in more predictive form
• Doubling features (14→28) increases overfitting without proportional gain
• Momentum signals (BQX) are more predictive than absolute levels (IDX)

DECISION per PERFORMANCE_FIRST mandate:
✅ PROCEED WITH BQX-ONLY APPROACH for all 196 models

IMPLEMENTATION:
• Created table: bqx_ml_v3_models.eurusd_45_dual_train (9,761 rows)
• Created scripts: prepare_training_dataset_dual.py
• Created scripts: train_dual_processing_model.py
• Full report: /sandbox/DUAL_PROCESSING_RESULTS_REPORT.md

NEXT STEPS:
• Scale BQX-only to all 196 models (28 pairs × 7 windows)
• Use EURUSD hyperparameters as baseline
• Target completion: 6 hours
"""

        # Update MP03.P01.S01.T01 with dual processing results
        for record in records:
            fields = record.get('fields', {})
            task_id = fields.get('Task ID', '')

            if task_id == 'MP03.P01.S01.T01':
                current_notes = fields.get('Notes', '')

                # Only update if dual processing results not already added
                if 'DUAL PROCESSING EXPERIMENT RESULTS' not in current_notes:
                    try:
                        table.update(record['id'], {
                            'Notes': current_notes + dual_processing_results,
                            'Status': 'Done'
                        })
                        updates_made += 1
                        print(f"✅ Updated {task_id} with dual processing results")
                    except Exception as e:
                        print(f"❌ Failed to update {task_id}: {e}")
                else:
                    print(f"ℹ️  {task_id} already has dual processing results")

        print(f"\n📊 AIRTABLE UPDATE SUMMARY:")
        print(f"  Tasks updated: {updates_made}")
        print(f"  Timestamp: {datetime.now().isoformat()}")

        return updates_made > 0

    except Exception as e:
        print(f"❌ Error updating AirTable: {e}")
        print_required_updates()
        return False

if __name__ == "__main__":
    success = update_airtable_with_results()

    if not success:
        print("\n📋 MANUAL UPDATE REQUIRED")
        print("Please update AirTable manually with the information above")

    sys.exit(0 if success else 1)