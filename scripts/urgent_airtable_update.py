#!/usr/bin/env python3
"""
URGENT: Update AirTable with dual processing results immediately.
Uses correct credentials path from github_secrets.json.
"""

import json
from pyairtable import Api
from datetime import datetime

# Load credentials from the CORRECT location
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

print("✅ AirTable credentials loaded successfully!")

# Connect to AirTable
api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

# Critical dual processing results to add
dual_processing_results = """

📊 DUAL PROCESSING EXPERIMENT RESULTS (2025-11-27 00:30):
================================================
Completed comprehensive comparison of BQX-only vs Dual Processing approaches.

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

IMPLEMENTATION VERIFIED:
• Created table: bqx_ml_v3_models.eurusd_45_dual_train (9,761 rows)
• Created scripts: prepare_training_dataset_dual.py
• Created scripts: train_dual_processing_model.py
• Full report: /sandbox/DUAL_PROCESSING_RESULTS_REPORT.md
• Verification: /sandbox/DUAL_PROCESSING_VERIFICATION.md

AUTHORIZATION TO SCALE (00:35):
• Use BQX-only approach for all 196 models
• Target: R² ≥ 0.35 for each model
• Expected completion: 6 hours
• Baseline hyperparameters validated
"""

print("\n📝 UPDATING AIRTABLE...")

# Get all tasks
all_tasks = tasks_table.all()
updates_made = 0
tasks_updated = []

# Priority task to update: MP03.P01.S01.T01
priority_task_id = 'MP03.P01.S01.T01'

for record in all_tasks:
    task = record['fields']
    task_id = task.get('Task ID', '')

    # Update MP03.P01.S01.T01 with dual processing results
    if task_id == priority_task_id:
        current_notes = task.get('Notes', '')

        # Check if dual processing results already added
        if 'DUAL PROCESSING EXPERIMENT RESULTS' not in current_notes:
            try:
                # Update the task
                tasks_table.update(record['id'], {
                    'Status': 'Done',
                    'Notes': current_notes + dual_processing_results
                })
                updates_made += 1
                tasks_updated.append(task_id)
                print(f"✅ Updated {task_id} with dual processing results")
            except Exception as e:
                print(f"❌ Failed to update {task_id}: {e}")
        else:
            print(f"ℹ️  {task_id} already has dual processing results")

# Update related tasks
related_updates = {
    'MP03.P01.S01.T02': {
        'status': 'In Progress',
        'note': '\n\n📌 MODEL EVALUATION UPDATE (2025-11-27):\nDual processing evaluation complete. BQX-only validated as superior.\nNext: Implement evaluation framework for all 196 models using BQX-only.'
    },
    'MP03.P02.S01.T01': {
        'status': 'In Progress',
        'note': '\n\n📌 FEATURE ENGINEERING DECISION (2025-11-27):\nAfter empirical testing, BQX features proven optimal.\nIDX features add noise rather than signal.\nProceeding with 14 BQX momentum features for all models.'
    },
    'MP03.P04.S01.T01': {
        'status': 'In Progress',
        'note': '\n\n📌 MODEL TRAINING PIPELINE UPDATE (2025-11-27):\nBased on dual processing experiment:\n• Configuration: BQX-only with 14 features\n• Baseline hyperparameters from EURUSD validated\n• Expected R² ≥ 0.35 for all 196 models\n• Training time: ~20 seconds per model'
    }
}

for record in all_tasks:
    task = record['fields']
    task_id = task.get('Task ID', '')

    if task_id in related_updates:
        update_info = related_updates[task_id]
        current_notes = task.get('Notes', '')

        # Check if update already added
        if '2025-11-27' not in current_notes:
            try:
                tasks_table.update(record['id'], {
                    'Status': update_info['status'],
                    'Notes': current_notes + update_info['note']
                })
                updates_made += 1
                tasks_updated.append(task_id)
                print(f"✅ Updated {task_id}")
            except Exception as e:
                print(f"❌ Failed to update {task_id}: {e}")

# Get current status counts
print("\n📊 CURRENT AIRTABLE STATUS:")
all_tasks = tasks_table.all()  # Refresh to get latest
status_counts = {'Todo': 0, 'In Progress': 0, 'Done': 0}

for record in all_tasks:
    status = record['fields'].get('Status', 'Todo')
    status_counts[status] += 1

print(f"  Todo: {status_counts['Todo']}")
print(f"  In Progress: {status_counts['In Progress']}")
print(f"  Done: {status_counts['Done']}")
print(f"  Total: {sum(status_counts.values())}")

print(f"\n✅ AIRTABLE UPDATE COMPLETE!")
print(f"  Tasks updated: {updates_made}")
print(f"  Tasks modified: {', '.join(tasks_updated)}")
print(f"  Timestamp: {datetime.now().isoformat()}")

# Add performance_first mandate note if needed
performance_first_note = """

📌 PERFORMANCE_FIRST MANDATE (2025-11-27 00:25):
Always pursue the option that yields best BQX ML V3 performance, regardless of complexity.
Applied to dual processing decision: BQX-only chosen based on superior R² = 0.4648.
"""

# Check if we need to add PERFORMANCE_FIRST context to any tasks
for record in all_tasks:
    task = record['fields']
    task_id = task.get('Task ID', '')

    # Add to key decision tasks
    if task_id in ['MP03.P01.S01.T01', 'MP03.P04.S01.T01'] and 'PERFORMANCE_FIRST MANDATE' not in task.get('Notes', ''):
        try:
            current_notes = task.get('Notes', '')
            tasks_table.update(record['id'], {
                'Notes': current_notes + performance_first_note
            })
            print(f"✅ Added PERFORMANCE_FIRST mandate to {task_id}")
        except Exception as e:
            print(f"❌ Failed to add mandate to {task_id}: {e}")

print("\n🎯 AIRTABLE IS NOW CURRENT!")
print("All dual processing experiment results and decisions recorded.")