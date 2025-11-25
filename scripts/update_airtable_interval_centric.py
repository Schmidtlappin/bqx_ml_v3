#!/usr/bin/env python3
"""
Update AirTable BQX ML V3 Project Plan with INTERVAL-CENTRIC V2.0 Recommendations
Ensures 100% coverage of all interval-based specifications
"""

import os
import json
from datetime import datetime
from pyairtable import Api

# AirTable configuration
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_KEY = os.getenv('AIRTABLE_API_KEY')

# Load from secrets if not in environment
if not API_KEY or not BASE_ID:
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            API_KEY = API_KEY or secrets['secrets']['AIRTABLE_API_KEY']['value']
            BASE_ID = BASE_ID or secrets['secrets']['AIRTABLE_BASE_ID']['value']
    except:
        print("Warning: Could not load AirTable credentials")

# Initialize API
api = Api(API_KEY)
base = api.base(BASE_ID)
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

# BQX windows and lag intervals
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
BQX_LAGS = [1, 2, 3, 5, 10, 15, 30, 45, 60, 90, 120, 180]

def generate_interval_centric_description(stage_type):
    """Generate INTERVAL-CENTRIC descriptions for different stage types."""

    descriptions = {
        'lag': """
Implements INTERVAL-CENTRIC lag features using ROWS BETWEEN exclusively.
Creates lag_bqx_* tables with BQX autoregressive features from past intervals (1i through 180i).
Critical: LAG(bqx_mid, N) represents N intervals ago, NOT N minutes.
Includes short-term (1-10i), medium-term (15-45i), and long-term (60-180i) BQX momentum patterns.
All operations use row positions, ensuring consistency across market gaps.
""",
        'regime': """
Implements INTERVAL-BASED regime detection using rolling statistics over fixed row counts.
Uses ROWS BETWEEN 89 PRECEDING for 90-interval volatility calculations.
Uses ROWS BETWEEN 359 PRECEDING for 360-interval trend detection.
Classifies market states (trending/ranging/volatile) based on interval statistics, NOT time-based metrics.
Handles weekend/holiday gaps gracefully through row-based windowing.
""",
        'aggregation': """
Creates multi-resolution BQX features using INTERVAL-BASED aggregations.
Implements 5i, 15i, 45i, 90i, 180i, 360i averages using ROWS BETWEEN.
Each aggregation uses exact row counts regardless of time gaps in data.
Includes interval alignment signals for momentum consensus across resolutions.
Never uses RANGE BETWEEN or time-based windows.
""",
        'derivatives': """
Calculates BQX velocity, acceleration, and jerk using INTERVAL-BASED derivatives.
Velocity = change per interval (NOT per minute).
Acceleration = change in velocity per interval.
Creates reversal signals based on interval momentum changes.
Uses diff(1), diff(5), diff(15) for multi-interval derivative calculations.
All derivatives measure change across fixed row counts.
""",
        'validation': """
Validates all features use ROWS BETWEEN exclusively - zero tolerance for RANGE BETWEEN.
Checks for prohibited time-based calculations or INTERVAL keyword usage.
Ensures consistency across market gaps (weekends, holidays, technical outages).
Validates naming convention: _Ni suffix for N intervals (not _Nm for minutes).
Generates compliance report for interval-centric architecture.
""",
        'leakage': """
Implements strict INTERVAL-BASED temporal isolation for zero data leakage.
Ensures features use past intervals (t-n) and targets use future intervals (t+n).
Critical for preventing lookahead bias in BQX predictions.
Uses LAG for features (past intervals), LEAD for targets (future intervals).
Validates no overlap between feature and target interval ranges.
"""
    }

    return descriptions.get(stage_type, "INTERVAL-CENTRIC implementation")

def generate_interval_notes():
    """Generate detailed notes with INTERVAL-CENTRIC specifications."""

    return f"""
## INTERVAL-CENTRIC Implementation Requirements

### Core Principle
All window calculations MUST use ROWS BETWEEN, never RANGE BETWEEN or time-based windows.

### BQX Windows (INTERVALS not minutes)
{BQX_WINDOWS} represent row counts in the data, NOT time periods.

### Lag Features (Past INTERVALS)
```python
BQX_LAGS = {BQX_LAGS}
for lag in BQX_LAGS:
    features[f'bqx_mid_lag_{{lag}}i'] = LAG(bqx_mid, lag) OVER (ORDER BY bar_start_time)
```

### Multi-Resolution Aggregations
```sql
-- 5-interval average (NOT 5-minute!)
AVG(bqx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
) AS bqx_5i

-- 360-interval average (NOT 360-minute!)
AVG(bqx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 359 PRECEDING AND CURRENT ROW
) AS bqx_360i
```

### Validation Requirements
- R² > 0.35 across all interval-based predictions
- PSI < 0.22 for interval-to-interval stability
- Sharpe > 1.5 using interval returns
- Zero RANGE BETWEEN usage
- 100% ROWS BETWEEN compliance

### Performance Metrics
Week 1: +20% R² improvement from interval-based BQX lags
Week 2: +15% from multi-resolution interval features
Week 3: +10% from interval-based ensemble
Week 4: +7% from validation and optimization
Total: 52% improvement using INTERVAL-CENTRIC approach
"""

def update_existing_stages():
    """Update existing stages with INTERVAL-CENTRIC specifications."""

    updates = []

    # Define stages that need updates
    stages_to_update = {
        'S03.04.01': {
            'description': generate_interval_centric_description('lag'),
            'notes_addition': """
### CRITICAL UPDATE: BQX Autoregressive Features
- Include BQX values from past INTERVALS as features
- LAG(bqx_mid, 1) through LAG(bqx_mid, 180)
- LAG(bqx_ask, 1) through LAG(bqx_ask, 60)
- LAG(bqx_bid, 1) through LAG(bqx_bid, 60)
- All lags use INTERVALS (rows), not time
"""
        },
        'S03.04.02': {
            'description': generate_interval_centric_description('regime'),
            'notes_addition': """
### CRITICAL UPDATE: Interval-Based Statistics
- STDDEV over ROWS BETWEEN 89 PRECEDING (90 intervals)
- AVG over ROWS BETWEEN 359 PRECEDING (360 intervals)
- No time-based regime detection allowed
"""
        },
        'S03.04.03': {
            'description': generate_interval_centric_description('aggregation'),
            'notes_addition': """
### CRITICAL UPDATE: Multi-Resolution Intervals
- 5i: ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
- 15i: ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
- 45i: ROWS BETWEEN 44 PRECEDING AND CURRENT ROW
- 90i: ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
- 180i: ROWS BETWEEN 179 PRECEDING AND CURRENT ROW
- 360i: ROWS BETWEEN 359 PRECEDING AND CURRENT ROW
"""
        }
    }

    # Search and update stages
    all_stages = stages_table.all()

    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id', '')
        if stage_id in stages_to_update:
            update_data = stages_to_update[stage_id]

            # Get current notes and append interval specs
            current_notes = stage['fields'].get('notes', '')
            updated_notes = current_notes + "\n\n" + update_data['notes_addition'] + generate_interval_notes()

            # Update the stage
            stages_table.update(stage['id'], {
                'description': update_data['description'],
                'notes': updated_notes
            })

            updates.append(stage_id)
            print(f"✓ Updated stage {stage_id} with INTERVAL-CENTRIC specifications")

    return updates

def create_new_stages():
    """Create new stages for uncovered INTERVAL-CENTRIC recommendations."""

    # Get Phase MP03.04 record
    phases = phases_table.all()
    phase_04 = None
    for phase in phases:
        if phase['fields'].get('phase_id') == 'MP03.04':
            phase_04 = phase['id']
            break

    if not phase_04:
        print("Warning: Could not find Phase MP03.04")
        return []

    new_stages = [
        {
            'stage_id': 'S03.04.07',
            'name': 'BQX Momentum Derivatives (Interval-Based)',
            'status': 'Todo',
            'description': generate_interval_centric_description('derivatives'),
            'notes': generate_interval_notes(),
            'phase_link': [phase_04],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        },
        {
            'stage_id': 'S03.04.08',
            'name': 'Interval Validation Framework',
            'status': 'Todo',
            'description': generate_interval_centric_description('validation'),
            'notes': generate_interval_notes(),
            'phase_link': [phase_04],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        },
        {
            'stage_id': 'S03.04.09',
            'name': 'Data Leakage Prevention (Interval-Based)',
            'status': 'Todo',
            'description': generate_interval_centric_description('leakage'),
            'notes': generate_interval_notes(),
            'phase_link': [phase_04],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        }
    ]

    created = []
    for stage_data in new_stages:
        try:
            result = stages_table.create(stage_data)
            created.append(stage_data['stage_id'])
            print(f"✓ Created new stage: {stage_data['stage_id']} - {stage_data['name']}")

            # Create associated tasks
            create_tasks_for_stage(result['id'], stage_data['stage_id'])

        except Exception as e:
            print(f"Error creating stage {stage_data['stage_id']}: {e}")

    return created

def create_tasks_for_stage(stage_record_id, stage_id):
    """Create tasks for a new stage."""

    task_sets = {
        'S03.04.07': [  # BQX Momentum Derivatives
            {
                'task_id': 'T03.04.07.01',
                'name': 'Implement single-interval velocity',
                'description': 'Calculate BQX change per interval using diff(1)'
            },
            {
                'task_id': 'T03.04.07.02',
                'name': 'Implement multi-interval velocities',
                'description': 'Calculate BQX velocities using diff(5), diff(15), diff(45)'
            },
            {
                'task_id': 'T03.04.07.03',
                'name': 'Calculate acceleration derivatives',
                'description': 'Compute second-order derivatives (velocity changes)'
            },
            {
                'task_id': 'T03.04.07.04',
                'name': 'Generate reversal signals',
                'description': 'Detect momentum reversals from derivative patterns'
            }
        ],
        'S03.04.08': [  # Interval Validation
            {
                'task_id': 'T03.04.08.01',
                'name': 'SQL validation for ROWS BETWEEN',
                'description': 'Verify all SQL uses ROWS BETWEEN, not RANGE'
            },
            {
                'task_id': 'T03.04.08.02',
                'name': 'Python validation for integer windows',
                'description': 'Ensure .rolling() uses integer window parameter'
            },
            {
                'task_id': 'T03.04.08.03',
                'name': 'Gap consistency validation',
                'description': 'Verify consistency across market gaps'
            },
            {
                'task_id': 'T03.04.08.04',
                'name': 'Naming convention validation',
                'description': 'Check _Ni suffix usage for interval features'
            }
        ],
        'S03.04.09': [  # Data Leakage Prevention
            {
                'task_id': 'T03.04.09.01',
                'name': 'Create temporal isolation validation',
                'description': 'Ensure strict past/future interval separation'
            },
            {
                'task_id': 'T03.04.09.02',
                'name': 'Implement safe feature extraction',
                'description': 'Extract features using only past intervals'
            },
            {
                'task_id': 'T03.04.09.03',
                'name': 'Validate no future data in features',
                'description': 'Check features contain no future interval data'
            },
            {
                'task_id': 'T03.04.09.04',
                'name': 'Create leakage detection tests',
                'description': 'Build automated tests for data leakage'
            }
        ]
    }

    if stage_id in task_sets:
        for task_data in task_sets[stage_id]:
            task_data.update({
                'status': 'in_progress',
                'stage_link': [stage_record_id],
                'notes': f"""
INTERVAL-CENTRIC Implementation:
- All operations use INTERVALS (rows), not time
- Window functions use ROWS BETWEEN
- Features named with _Ni suffix
- Validation: Must handle market gaps correctly
- Performance target: Contributes to 52% R² improvement

BQX_WINDOWS = {BQX_WINDOWS}
All windows represent INTERVALS, not minutes!
""",
                'source': 'scripts/interval_centric_implementation.py'
            })

            try:
                tasks_table.create(task_data)
                print(f"  ✓ Created task: {task_data['task_id']}")
            except Exception as e:
                print(f"  Error creating task {task_data['task_id']}: {e}")

def update_existing_tasks():
    """Update all existing tasks with INTERVAL-CENTRIC specifications."""

    all_tasks = tasks_table.all()
    updated_count = 0

    interval_spec = """

### ⚠️ INTERVAL-CENTRIC MANDATE
This task MUST use ROWS BETWEEN for all window operations.
- FORBIDDEN: RANGE BETWEEN, time-based windows, INTERVAL keyword
- REQUIRED: ROWS BETWEEN N PRECEDING AND CURRENT ROW
- Naming: Use _Ni suffix (N intervals), not _Nm (minutes)
- Validation: Must work correctly across weekend/holiday gaps
"""

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')

        # Only update tasks in relevant stages
        if task_id.startswith('T03.04'):
            current_notes = task['fields'].get('notes', '')

            # Check if already updated
            if 'INTERVAL-CENTRIC' not in current_notes:
                updated_notes = current_notes + interval_spec

                tasks_table.update(task['id'], {
                    'notes': updated_notes
                })

                updated_count += 1

                if updated_count % 10 == 0:
                    print(f"  Updated {updated_count} tasks...")

    print(f"✓ Updated {updated_count} tasks with INTERVAL-CENTRIC specifications")
    return updated_count

def validate_coverage():
    """Validate that all INTERVAL-CENTRIC recommendations are covered."""

    print("\n=== Coverage Validation ===")

    checks = {
        'BQX Autoregressive Lags': False,
        'Multi-Resolution Features': False,
        'BQX Momentum Derivatives': False,
        'Regime Detection (Interval)': False,
        'Data Leakage Prevention': False,
        'Interval Validation Framework': False,
        'ROWS BETWEEN Mandate': False,
        'Naming Convention (_Ni)': False
    }

    # Check stages
    all_stages = stages_table.all()
    for stage in all_stages:
        description = stage['fields'].get('description', '')
        notes = stage['fields'].get('notes', '')
        combined = description + notes

        if 'INTERVAL-CENTRIC lag features' in combined:
            checks['BQX Autoregressive Lags'] = True
        if 'multi-resolution' in combined.lower():
            checks['Multi-Resolution Features'] = True
        if 'momentum derivatives' in combined.lower() or 'velocity' in combined.lower():
            checks['BQX Momentum Derivatives'] = True
        if 'regime detection' in combined.lower():
            checks['Regime Detection (Interval)'] = True
        if 'leakage prevention' in combined.lower():
            checks['Data Leakage Prevention'] = True
        if 'validation framework' in combined.lower():
            checks['Interval Validation Framework'] = True
        if 'ROWS BETWEEN' in combined:
            checks['ROWS BETWEEN Mandate'] = True
        if '_Ni' in combined or '_ni' in combined.lower():
            checks['Naming Convention (_Ni)'] = True

    # Calculate coverage
    covered = sum(1 for v in checks.values() if v)
    total = len(checks)
    coverage_pct = (covered / total) * 100

    print("\nRecommendation Coverage:")
    for recommendation, covered in checks.items():
        status = "✅" if covered else "❌"
        print(f"  {status} {recommendation}")

    print(f"\nOverall Coverage: {coverage_pct:.1f}%")

    if coverage_pct == 100:
        print("🎉 SUCCESS: 100% coverage of INTERVAL-CENTRIC recommendations achieved!")
    else:
        print(f"⚠️  Coverage incomplete: {100 - coverage_pct:.1f}% remaining")

    return coverage_pct

def main():
    """Main execution function."""

    print("=" * 60)
    print("INTERVAL-CENTRIC AirTable Update Script")
    print("Incorporating V2.0 Recommendations into Project Plan")
    print("=" * 60)

    if not API_KEY or not BASE_ID:
        print("ERROR: AirTable credentials not found")
        print("Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID environment variables")
        return 1

    print("\n1. Updating existing stages...")
    updated_stages = update_existing_stages()
    print(f"   Updated {len(updated_stages)} stages")

    print("\n2. Creating new stages...")
    created_stages = create_new_stages()
    print(f"   Created {len(created_stages)} new stages")

    print("\n3. Updating existing tasks...")
    updated_tasks = update_existing_tasks()
    print(f"   Updated {updated_tasks} tasks")

    print("\n4. Validating coverage...")
    coverage = validate_coverage()

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Stages updated: {len(updated_stages)}")
    print(f"  Stages created: {len(created_stages)}")
    print(f"  Tasks updated: {updated_tasks}")
    print(f"  Coverage achieved: {coverage:.1f}%")
    print("=" * 60)

    return 0 if coverage == 100 else 1

if __name__ == "__main__":
    exit(main())