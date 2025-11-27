#!/usr/bin/env python3
"""
Refactor BQX ML V3 Project Plan in AirTable for Smart Dual Processing
Based on the critical lag insight discovered 2025-11-27
"""

import json
from pyairtable import Api
from datetime import datetime

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

print("✅ AirTable credentials loaded!")

# Connect to AirTable
api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

print("\n🔄 REFACTORING PROJECT PLAN FOR SMART DUAL PROCESSING...")

# Get all tasks
all_tasks = tasks_table.all()
refactored = 0

# Core architectural update message
architecture_update = """

🏗️ ARCHITECTURAL UPDATE (2025-11-27):
================================================
SMART DUAL PROCESSING APPROACH

Critical Insight: BQX values are LAGGED indicators
- BQX_90 includes data from 90 intervals ago (smoothed/averaged)
- IDX provides CURRENT market state (leading indicators)
- Must use BOTH for optimal predictions

Previous Results:
- BQX-only: R² = 0.4648 (missing leading signals)
- Naive Dual (28 features): R² = 0.2692 (feature redundancy)
- Smart Dual (12-15 features): R² > 0.50 TARGET

Implementation:
- High priority: IDX lags 1-5 (weight 2.0-1.2)
- Medium priority: Selected BQX lags (weight 1.0)
- Low priority: Derived features (weight 0.8)
================================================
"""

# Task-specific updates based on smart dual processing
task_updates = {
    'MP03.P01.S01.T01': {
        'name': 'Prepare training dataset',
        'status': 'Done',
        'notes': f"""COMPLETED - Multiple iterations tested:{architecture_update}

✅ Iteration 1: BQX-only (R² = 0.4648)
✅ Iteration 2: Naive Dual (R² = 0.2692)
🔄 Iteration 3: Smart Dual Processing (IN PROGRESS)

Key Learning: IDX detects market changes BEFORE they appear in smoothed BQX values.
This is why smart dual processing is essential."""
    },
    'MP03.P02.S01.T01': {
        'name': 'Design BQX feature engineering',
        'status': 'In Progress',
        'notes': f"""REDESIGNED for Smart Dual Processing:{architecture_update}

Feature Engineering Strategy:
1. Leading Indicators (IDX recent lags)
2. Momentum Context (selected BQX lags)
3. Derived Features (ratios, volatility)

Total: 12-15 features (not 28)"""
    },
    'MP03.P02.S01.T02': {
        'name': 'Implement BQX feature engineering',
        'status': 'In Progress',
        'notes': """Smart Dual Implementation:
- create_smart_dual_features() function
- get_feature_weights() for importance
- Feature count: 12-15 optimized features
Script: smart_dual_processing_template.py"""
    },
    'MP03.P03.S01.T01': {
        'name': 'Design feature engineering pipeline',
        'status': 'In Progress',
        'notes': """Pipeline Architecture:
1. Load IDX data (current market state)
2. Load BQX data (momentum context)
3. Create smart features (12-15 total)
4. Apply feature weights
5. Train with regularization"""
    },
    'MP03.P04.S01.T01': {
        'name': 'Design model training pipeline',
        'status': 'In Progress',
        'notes': """XGBoost Configuration for Smart Dual:
- n_estimators: 200 (more trees)
- max_depth: 8 (capture interactions)
- learning_rate: 0.05 (slower, stable)
- L1/L2 regularization added
- Feature sampling: 0.7"""
    },
    'MP03.P04.S02.T01': {
        'name': 'Configure XGBoost hyperparameter search space',
        'status': 'Todo',
        'notes': """Hyperparameter Space for Smart Dual:
- Focus on regularization params
- Test different feature sampling rates
- Optimize for IDX/BQX balance
- Target: R² > 0.50"""
    },
    'MP03.P05.S01.T01': {
        'name': 'Design model evaluation framework',
        'status': 'Todo',
        'notes': """Evaluation Metrics:
Primary: R² Score (target > 0.50)
Secondary: Directional Accuracy (> 75%)
Tertiary: Feature Importance Analysis
- IDX importance (should be 40-50%)
- BQX importance (should be 30-40%)
- Derived importance (should be 10-20%)"""
    }
}

# Update existing tasks
for record in all_tasks:
    task = record['fields']
    task_id = task.get('Task ID', '')

    if task_id in task_updates:
        update = task_updates[task_id]
        print(f"\n📝 Updating {task_id}: {update['name']}")

        try:
            tasks_table.update(record['id'], {
                'Status': update['status'],
                'Notes': update['notes']
            })
            refactored += 1
            print(f"   ✅ Updated to {update['status']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

# Create new critical tasks for smart dual processing
new_tasks = [
    {
        'Task ID': 'MP03.P01.S01.T05',
        'Task Name': 'Implement Smart Dual Processing',
        'Status': 'In Progress',
        'Phase': 'P01',
        'Stage': 'S01',
        'Priority': 'Critical',
        'Notes': """Implement Smart Dual Processing based on lag insight:
- Use smart_dual_processing_template.py
- 12-15 carefully selected features
- Weight recent IDX heavily (2.0-1.2)
- Target R² > 0.50 for EURUSD-45"""
    },
    {
        'Task ID': 'MP03.P01.S01.T06',
        'Task Name': 'Validate Smart Dual Performance',
        'Status': 'Todo',
        'Phase': 'P01',
        'Stage': 'S01',
        'Priority': 'Critical',
        'Notes': """Compare three approaches:
1. BQX-only: R² = 0.4648
2. Naive Dual: R² = 0.2692
3. Smart Dual: R² > 0.50 (target)

Document why smart dual succeeds."""
    },
    {
        'Task ID': 'MP03.P01.S01.T07',
        'Task Name': 'Scale Smart Dual to 196 Models',
        'Status': 'Todo',
        'Phase': 'P01',
        'Stage': 'S01',
        'Priority': 'High',
        'Notes': """After validation on EURUSD-45:
- Apply smart dual to all 28 currency pairs
- Train all 7 prediction windows per pair
- Total: 196 models
- Expected timeline: 8-10 hours
- Update AirTable for each model"""
    },
    {
        'Task ID': 'MP03.P02.S01.T03',
        'Task Name': 'Create Feature Importance Monitor',
        'Status': 'Todo',
        'Phase': 'P02',
        'Stage': 'S01',
        'Priority': 'Medium',
        'Notes': """Monitor feature importance across models:
- Track IDX vs BQX importance ratio
- Identify which features drive predictions
- Validate lag insight hypothesis
- Create importance heatmap"""
    }
]

print("\n📋 CREATING NEW SMART DUAL TASKS...")
for task_data in new_tasks:
    # Check if task already exists
    exists = False
    for record in all_tasks:
        if record['fields'].get('Task ID') == task_data['Task ID']:
            exists = True
            break

    if not exists:
        try:
            tasks_table.create(task_data)
            print(f"✅ Created: {task_data['Task ID']} - {task_data['Task Name']}")
            refactored += 1
        except Exception as e:
            print(f"❌ Failed to create {task_data['Task ID']}: {e}")
    else:
        print(f"ℹ️  {task_data['Task ID']} already exists")

# Add project-wide note about architectural change
print("\n📊 UPDATING PROJECT STATUS...")
project_status_note = f"""

{'='*60}
PROJECT ARCHITECTURAL PIVOT - SMART DUAL PROCESSING
{'='*60}
Date: 2025-11-27
Decision: Use Smart Dual Processing (IDX + BQX)
Rationale: User identified critical lag problem in BQX values

THE LAG INSIGHT:
BQX_90[t] includes price data from 90 intervals ago.
This creates inherent lag in detecting market changes.
IDX provides current market state (leading indicators).

IMPLEMENTATION:
- 12-15 carefully selected features (not 28)
- High weight on recent IDX (2.0-1.2)
- Selected BQX for trend context (1.0)
- Derived features for relationships (0.8)

EXPECTED OUTCOME:
- R² > 0.50 (vs 0.4648 BQX-only)
- Better prediction of future BQX values
- Captures both leading and lagging signals

STATUS: Implementing smart dual processing now
{'='*60}
"""

# Update a high-level task with project status
for record in all_tasks:
    task = record['fields']
    if task.get('Task ID') == 'MP03.P01.S01.T01':
        current_notes = task.get('Notes', '')
        if 'PROJECT ARCHITECTURAL PIVOT' not in current_notes:
            try:
                tasks_table.update(record['id'], {
                    'Notes': current_notes + project_status_note
                })
                print("✅ Added project architectural pivot note")
            except Exception as e:
                print(f"❌ Failed to add project note: {e}")
        break

# Get final status
print("\n📊 VERIFYING REFACTORED AIRTABLE...")
all_tasks = tasks_table.all()  # Refresh
status_counts = {'Todo': 0, 'In Progress': 0, 'Done': 0}

for record in all_tasks:
    status = record['fields'].get('Status', 'Todo')
    status_counts[status] += 1

print(f"\nCurrent Status:")
print(f"  Todo: {status_counts['Todo']}")
print(f"  In Progress: {status_counts['In Progress']}")
print(f"  Done: {status_counts['Done']}")
print(f"  Total: {sum(status_counts.values())}")

print(f"\n✅ REFACTORING COMPLETE!")
print(f"  Tasks refactored: {refactored}")
print(f"  Architecture: Smart Dual Processing")
print(f"  Target R²: > 0.50")
print(f"  Timestamp: {datetime.now().isoformat()}")

# Create summary for user
print("\n" + "="*60)
print("REFACTORING SUMMARY")
print("="*60)
print("1. Updated existing tasks with smart dual context")
print("2. Created new tasks for smart implementation")
print("3. Documented lag insight throughout project")
print("4. Set clear performance targets (R² > 0.50)")
print("5. Established feature weighting strategy")
print("\nThe project plan now reflects the critical insight that")
print("IDX provides leading indicators while BQX provides lagging")
print("momentum context. Together they enable optimal predictions.")
print("="*60)