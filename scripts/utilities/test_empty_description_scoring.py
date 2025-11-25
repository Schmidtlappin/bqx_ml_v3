#!/usr/bin/env python3
"""
Test Empty Description Scoring Vulnerability

This script tests whether the record_audit prompt properly penalizes
tasks with empty descriptions by creating test records and checking scores.
"""
import json
import time
from pyairtable import Api
from typing import Dict, List

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']\

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
tasks_table = api.table(AIRTABLE_BASE_ID, 'Tasks')
stages_table = api.table(AIRTABLE_BASE_ID, 'Stages')

def get_stage_link():
    """Get a valid stage link for testing"""
    all_stages = stages_table.all()
    if all_stages:
        return [all_stages[0]['id']]
    return []

def create_test_task_with_empty_description() -> str:
    """Create a test task with empty description but otherwise perfect"""

    stage_link = get_stage_link()

    # Create a task with EMPTY description but perfect everything else
    test_task = {
        'task_id': 'MP03.P99.S99.T99',  # Test task ID
        'name': 'Test Task with Empty Description - Should Score Max 55',
        'description': '',  # EMPTY!
        'notes': """## Comprehensive Implementation Notes

This is a test task with comprehensive notes (>500 characters) and multiple code blocks to test the scoring vulnerability.

### Code Block 1
```python
def calculate_bqx_features(df, windows=[45, 90, 180, 360, 720, 1440, 2880]):
    \"\"\"Calculate BQX momentum features.\"\"\"
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2
    for window in windows:
        df[f'bqx_{window}w'] = df['idx_mid'] - df['idx_mid'].rolling(window).mean()
    return df
```

### Code Block 2
```sql
SELECT pair, timestamp, bqx_360w
FROM `bqx_ml_v3.features`
WHERE bqx_360w IS NOT NULL
ORDER BY timestamp;
```

### Technical Specifications
- BQX Windows: [45, 90, 180, 360, 720, 1440, 2880]
- Quality Thresholds: R² >= 0.35, RMSE <= 0.15
- 5-Algorithm Ensemble: RandomForest, XGBoost, LightGBM, LSTM, GRU

This task has everything EXCEPT a description. It should score max 55 points (40 base - 30 penalty + 45 other fields).
""",
        'status': 'In Progress',
        'source': 'scripts/test_scoring.py',
        'stage_link': stage_link
    }

    # Create the task
    created = tasks_table.create(test_task)
    return created['id']

def create_test_task_with_good_description() -> str:
    """Create a control task with good description"""

    stage_link = get_stage_link()

    # Create a task with GOOD description and everything else
    test_task = {
        'task_id': 'MP03.P99.S99.T98',  # Test task ID
        'name': 'Test Task with Good Description - Should Score 90+',
        'description': 'Implement BQX feature calculation using 7 standard windows [45, 90, 180, 360, 720, 1440, 2880] with quality thresholds R²>=0.35, RMSE<=0.15, and 5-algorithm ensemble validation.',
        'notes': """## Comprehensive Implementation Notes

This is a control task with comprehensive notes (>500 characters) and multiple code blocks.

### Code Block 1
```python
def calculate_bqx_features(df, windows=[45, 90, 180, 360, 720, 1440, 2880]):
    \"\"\"Calculate BQX momentum features.\"\"\"
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2
    for window in windows:
        df[f'bqx_{window}w'] = df['idx_mid'] - df['idx_mid'].rolling(window).mean()
    return df
```

### Code Block 2
```sql
SELECT pair, timestamp, bqx_360w
FROM `bqx_ml_v3.features`
WHERE bqx_360w IS NOT NULL
ORDER BY timestamp;
```

### Technical Specifications
- BQX Windows: [45, 90, 180, 360, 720, 1440, 2880]
- Quality Thresholds: R² >= 0.35, RMSE <= 0.15
- 5-Algorithm Ensemble: RandomForest, XGBoost, LightGBM, LSTM, GRU

This task has everything INCLUDING a good description. It should score 90+ points.
""",
        'status': 'In Progress',
        'source': 'scripts/test_scoring.py',
        'stage_link': stage_link
    }

    # Create the task
    created = tasks_table.create(test_task)
    return created['id']

def wait_for_ai_scoring(task_id: str, max_wait: int = 180) -> Dict:
    """Wait for AI to score the task"""
    print(f"   Waiting for AI scoring (max {max_wait}s)...")

    start_time = time.time()
    while (time.time() - start_time) < max_wait:
        task = tasks_table.get(task_id)
        score = task['fields'].get('record_score')
        record_audit = task['fields'].get('record_audit', {})

        # Check if scored
        if score is not None and record_audit:
            if isinstance(record_audit, dict):
                if record_audit.get('state') == 'generated':
                    return {
                        'score': score,
                        'audit': record_audit.get('value', '')
                    }

        time.sleep(5)

    return {'score': None, 'audit': 'Timeout waiting for AI scoring'}

def delete_test_task(task_id: str):
    """Delete the test task"""
    try:
        tasks_table.delete(task_id)
        print(f"   ✓ Deleted test task")
    except Exception as e:
        print(f"   ⚠️  Error deleting task: {e}")

def main():
    print("🧪 Testing Empty Description Scoring Vulnerability")
    print("="*70)
    print("\nThis test creates two tasks:")
    print("1. Task with EMPTY description (should score max 55)")
    print("2. Task with GOOD description (should score 90+)")
    print("="*70)

    # Test 1: Empty description
    print("\n" + "="*70)
    print("TEST 1: EMPTY DESCRIPTION")
    print("="*70)

    print("\n📝 Creating test task with empty description...")
    empty_desc_id = create_test_task_with_empty_description()
    print(f"   ✓ Created task: {empty_desc_id}")

    empty_result = wait_for_ai_scoring(empty_desc_id)

    print(f"\n📊 Results:")
    print(f"   Score: {empty_result['score']}")
    if empty_result['audit']:
        audit_lines = empty_result['audit'].split('\n')[:5]
        for line in audit_lines:
            if line.strip():
                print(f"   {line}")

    # Test 2: Good description
    print("\n" + "="*70)
    print("TEST 2: GOOD DESCRIPTION (Control)")
    print("="*70)

    print("\n📝 Creating test task with good description...")
    good_desc_id = create_test_task_with_good_description()
    print(f"   ✓ Created task: {good_desc_id}")

    good_result = wait_for_ai_scoring(good_desc_id)

    print(f"\n📊 Results:")
    print(f"   Score: {good_result['score']}")
    if good_result['audit']:
        audit_lines = good_result['audit'].split('\n')[:5]
        for line in audit_lines:
            if line.strip():
                print(f"   {line}")

    # Analysis
    print("\n" + "="*70)
    print("VULNERABILITY ANALYSIS")
    print("="*70)

    if empty_result['score'] is not None and good_result['score'] is not None:
        print(f"\n📊 Score Comparison:")
        print(f"   Empty description: {empty_result['score']}")
        print(f"   Good description: {good_result['score']}")
        print(f"   Difference: {good_result['score'] - empty_result['score']}")

        if empty_result['score'] > 55:
            print(f"\n❌ VULNERABILITY CONFIRMED!")
            print(f"   Empty description scored {empty_result['score']} (expected max 55)")
            print(f"   Prompt update REQUIRED")
        else:
            print(f"\n✅ VULNERABILITY FIXED!")
            print(f"   Empty description correctly capped at {empty_result['score']}")
            print(f"   Prompt is working as intended")
    else:
        print(f"\n⚠️  Could not complete analysis (AI scoring timeout)")

    # Cleanup
    print("\n" + "="*70)
    print("CLEANUP")
    print("="*70)

    response = input("\nDelete test tasks? (yes/no): ")

    if response.lower() == 'yes':
        print(f"\n🗑️  Deleting test tasks...")
        delete_test_task(empty_desc_id)
        delete_test_task(good_desc_id)
        print(f"\n✓ Cleanup complete")
    else:
        print(f"\n⚠️  Test tasks preserved:")
        print(f"   Empty description: {empty_desc_id}")
        print(f"   Good description: {good_desc_id}")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
