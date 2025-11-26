#!/usr/bin/env python3
"""
Update AirTable BQX ML V3 Project Plan with INTERVAL-CENTRIC V2.0 Recommendations
Version 2: Corrected for actual AirTable structure
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

def generate_interval_centric_notes():
    """Generate comprehensive INTERVAL-CENTRIC notes."""
    return f"""
### ⚠️ CRITICAL: INTERVAL-CENTRIC MANDATE

This implementation MUST use ROWS BETWEEN for all window operations.

**FORBIDDEN:**
- RANGE BETWEEN
- Time-based windows
- INTERVAL keyword with time units
- Any reference to minutes/hours in window calculations

**REQUIRED:**
- ROWS BETWEEN N PRECEDING AND CURRENT ROW
- ROWS BETWEEN N FOLLOWING AND M FOLLOWING (for BQX)
- LAG/LEAD functions for interval offsets
- Naming: _Ni suffix for N intervals (not _Nm for minutes)

**BQX Windows (INTERVALS not minutes):**
{BQX_WINDOWS} represent row counts, NOT time periods.

**Implementation Example:**
```sql
-- CORRECT: Interval-based (uses ROWS)
AVG(bqx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 359 PRECEDING AND CURRENT ROW
) AS bqx_360i  -- 360 intervals, not minutes

-- WRONG: Time-based (NEVER use this)
AVG(bqx_mid) OVER (
    ORDER BY bar_start_time
    RANGE BETWEEN INTERVAL 360 MINUTE PRECEDING AND CURRENT ROW
) AS bqx_360m  -- FORBIDDEN
```

**Lag Features:**
```python
BQX_LAGS = {BQX_LAGS}
for lag in BQX_LAGS:
    features[f'bqx_mid_lag_{{lag}}i'] = LAG(bqx_mid, lag)
```

**Performance Targets:**
- R² > 0.35 using interval-based features
- PSI < 0.22 for interval stability
- Sharpe > 1.5 with interval returns
- 52% overall improvement expected
"""

def update_bqx_paradigm_stages():
    """Update BQX paradigm stages with INTERVAL-CENTRIC specifications."""

    updates = []
    all_stages = stages_table.all()

    # Target stages for INTERVAL-CENTRIC updates
    target_updates = {
        'MP03.P06.S02': {  # BQX paradigm transformations
            'name_suffix': ' [INTERVAL-CENTRIC]',
            'description': """
Implements BQX paradigm transformations using INTERVAL-CENTRIC calculations.
All BQX windows [45, 90, 180, 360, 720, 1440, 2880] use ROWS BETWEEN for forward-looking intervals.
Critical: idx_mid - AVG(idx_mid) OVER (ROWS BETWEEN 1 FOLLOWING AND N FOLLOWING).
Zero tolerance for time-based windows. Handles market gaps correctly through row-based windowing.
            """.strip(),
            'notes_addition': """

### INTERVAL-CENTRIC BQX Calculation
```sql
-- BQX 360-interval window (NOT 360-minute!)
idx_mid - AVG(idx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 1 FOLLOWING AND 360 FOLLOWING
) AS bqx_360w
```
All 7 BQX windows MUST use this pattern with ROWS BETWEEN.
"""
        },
        'MP03.P06.S03': {  # Lag and window features
            'name_suffix': ' [INTERVAL-BASED]',
            'description': """
Creates lag and window features using INTERVAL-BASED calculations exclusively.
LAG(column, N) where N represents intervals (rows), not time.
Includes BQX autoregressive features: LAG(bqx_mid, 1) through LAG(bqx_mid, 180).
All rolling windows use ROWS BETWEEN. Features named with _Ni suffix.
            """.strip(),
            'notes_addition': """

### BQX Autoregressive Features (CRITICAL ADDITION)
```sql
-- Past BQX values as features (paradigm shift)
LAG(bqx_mid, 1) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_1i,
LAG(bqx_mid, 5) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_5i,
LAG(bqx_mid, 15) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_15i,
-- Continue through lag_180i
```
BQX values from past INTERVALS predict future BQX.
"""
        },
        'MP03.P06.S05': {  # BQX Feature Generation
            'name_suffix': ' [ROWS BETWEEN MANDATE]',
            'description': """
Implements BQX Paradigm Feature Generation with strict INTERVAL-CENTRIC approach.
Generates multi-resolution BQX features: 5i, 15i, 45i, 90i, 180i, 360i aggregations.
All use ROWS BETWEEN for exact interval counts. Includes BQX momentum derivatives.
Zero time-based calculations allowed. Validates interval consistency across gaps.
            """.strip(),
            'notes_addition': """

### Multi-Resolution BQX Features
```sql
-- 5-interval average (5 rows, not 5 minutes)
AVG(bqx_mid) OVER (ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS bqx_5i,
-- 360-interval average (360 rows, not 6 hours)
AVG(bqx_mid) OVER (ROWS BETWEEN 359 PRECEDING AND CURRENT ROW) AS bqx_360i
```

### BQX Momentum Derivatives
```python
# Velocity per interval (not per minute)
bqx_velocity_1i = bqx_mid.diff(1)
bqx_velocity_5i = bqx_mid.diff(5) / 5  # Average per interval
bqx_acceleration_1i = bqx_velocity_1i.diff(1)
```
"""
        },
        'MP03.P07.S01': {  # Multi-timeframe correlations
            'name_suffix': ' [INTERVAL CORRELATIONS]',
            'description': """
Engineers multi-timeframe correlation features using INTERVAL-BASED windows.
Correlations calculated over fixed row counts: 45i, 90i, 180i, 360i windows.
Cross-pair BQX correlations use synchronized interval alignment.
All calculations use ROWS BETWEEN. No time-based correlation windows.
            """.strip(),
            'notes_addition': """

### Interval-Based Correlations
```sql
-- Correlation over 360 intervals (rows)
CORR(bqx_mid, close) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 359 PRECEDING AND CURRENT ROW
) AS bqx_close_corr_360i
```
Ensures consistent correlation calculation across market gaps.
"""
        }
    }

    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id', '')

        if stage_id in target_updates:
            update_info = target_updates[stage_id]
            current_name = stage['fields'].get('name', '')
            current_notes = stage['fields'].get('notes', '')

            # Only add suffix if not already present
            new_name = current_name
            if update_info['name_suffix'] not in current_name:
                new_name = current_name + update_info['name_suffix']

            # Add interval-centric notes
            updated_notes = current_notes + update_info['notes_addition'] + generate_interval_centric_notes()

            try:
                stages_table.update(stage['id'], {
                    'name': new_name,
                    'description': update_info['description'],
                    'notes': updated_notes
                })
                updates.append(stage_id)
                print(f"✓ Updated stage {stage_id}: {new_name}")
            except Exception as e:
                print(f"  Error updating {stage_id}: {e}")

    return updates

def create_new_interval_stages():
    """Create new stages for INTERVAL-CENTRIC features not yet covered."""

    # Find Phase MP03.P06 (Primary Feature Engineering)
    phases = phases_table.all()
    phase_06_id = None
    phase_07_id = None

    for phase in phases:
        if phase['fields'].get('phase_id') == 'MP03.P06':
            phase_06_id = phase['id']
        elif phase['fields'].get('phase_id') == 'MP03.P07':
            phase_07_id = phase['id']

    if not phase_06_id:
        print("Warning: Could not find Phase MP03.P06")
        return []

    new_stages = [
        {
            'stage_id': 'MP03.P06.S07',
            'name': 'BQX Momentum Derivatives [INTERVAL-BASED]',
            'status': 'Todo',
            'description': """
Calculates BQX velocity, acceleration, and jerk using INTERVAL-BASED derivatives.
Velocity = change per interval (NOT per minute).
Creates reversal signals from interval momentum patterns.
All derivatives use diff() with integer periods representing intervals.
            """.strip(),
            'notes': generate_interval_centric_notes() + """

### Implementation
```python
def calculate_bqx_derivatives(df):
    # Single interval derivatives
    df['bqx_velocity_1i'] = df['bqx_mid'].diff(1)
    df['bqx_acceleration_1i'] = df['bqx_velocity_1i'].diff(1)
    df['bqx_jerk_1i'] = df['bqx_acceleration_1i'].diff(1)

    # Multi-interval for smoothing
    df['bqx_velocity_5i'] = df['bqx_mid'].diff(5) / 5
    df['bqx_velocity_15i'] = df['bqx_mid'].diff(15) / 15

    return df
```
""",
            'phase_link': [phase_06_id],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        },
        {
            'stage_id': 'MP03.P06.S08',
            'name': 'Data Leakage Prevention [INTERVAL ISOLATION]',
            'status': 'Todo',
            'description': """
Implements strict INTERVAL-BASED temporal isolation to prevent data leakage.
Features use past intervals (LAG), targets use future intervals (LEAD).
Validates no overlap between feature and target interval ranges.
Critical for preventing lookahead bias in BQX predictions.
            """.strip(),
            'notes': generate_interval_centric_notes() + """

### Temporal Isolation
```python
def validate_temporal_isolation(features, targets):
    # Features: past intervals only
    assert all('lag' in col or 'PRECEDING' in sql for col in features)
    # Targets: future intervals only
    assert all('lead' in col or 'FOLLOWING' in sql for col in targets)
    # No overlap
    assert len(set(features) & set(targets)) == 0
```
""",
            'phase_link': [phase_06_id],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        },
        {
            'stage_id': 'MP03.P07.S05',
            'name': 'Interval Validation Framework',
            'status': 'Todo',
            'description': """
Validates all features use ROWS BETWEEN exclusively - zero tolerance for RANGE BETWEEN.
Checks for prohibited time-based calculations or INTERVAL keyword with time units.
Ensures consistency across market gaps. Validates _Ni naming convention.
Generates compliance report for interval-centric architecture.
            """.strip(),
            'notes': generate_interval_centric_notes() + """

### Validation Queries
```sql
-- Check for forbidden patterns
SELECT COUNT(*) as violations
FROM INFORMATION_SCHEMA.ROUTINES
WHERE routine_definition REGEXP 'RANGE BETWEEN|INTERVAL.*MINUTE|INTERVAL.*HOUR'
```
""",
            'phase_link': [phase_07_id] if phase_07_id else [phase_06_id],
            'source': 'docs/FINAL_RECOMMENDATIONS_INTERVAL_CENTRIC_V2.md'
        }
    ]

    created = []
    for stage_data in new_stages:
        try:
            result = stages_table.create(stage_data)
            created.append(stage_data['stage_id'])
            print(f"✓ Created new stage: {stage_data['stage_id']} - {stage_data['name']}")

            # Create tasks for the new stage
            create_tasks_for_new_stage(result['id'], stage_data['stage_id'])

        except Exception as e:
            print(f"  Error creating stage {stage_data['stage_id']}: {e}")

    return created

def create_tasks_for_new_stage(stage_record_id, stage_id):
    """Create tasks for newly created stages."""

    task_templates = {
        'MP03.P06.S07': [  # BQX Momentum Derivatives
            ('Calculate single-interval velocity', 'Implement bqx_mid.diff(1) for immediate momentum'),
            ('Calculate multi-interval velocities', 'Implement diff(5), diff(15), diff(45) for smoothed momentum'),
            ('Compute acceleration derivatives', 'Second-order derivatives showing momentum change'),
            ('Generate reversal signals', 'Detect momentum reversals from derivative patterns')
        ],
        'MP03.P06.S08': [  # Data Leakage Prevention
            ('Implement temporal isolation', 'Ensure strict past/future interval separation'),
            ('Create safe feature extraction', 'Extract features using only past intervals (LAG)'),
            ('Validate no future data', 'Check features contain zero future interval data'),
            ('Build leakage detection tests', 'Automated tests for continuous validation')
        ],
        'MP03.P07.S05': [  # Interval Validation
            ('SQL validation for ROWS BETWEEN', 'Scan all SQL for ROWS BETWEEN compliance'),
            ('Python validation for windows', 'Ensure .rolling() uses integer window parameter'),
            ('Gap consistency validation', 'Verify calculations work across market gaps'),
            ('Naming convention validation', 'Check all features use _Ni suffix')
        ]
    }

    if stage_id in task_templates:
        task_num = 1
        for task_name, task_desc in task_templates[stage_id]:
            task_data = {
                'task_id': f'{stage_id}.T{task_num:02d}',
                'name': task_name,
                'description': task_desc,
                'status': 'in_progress',
                'stage_link': [stage_record_id],
                'notes': f"""
INTERVAL-CENTRIC Implementation Required:
- Use ROWS BETWEEN exclusively
- Features named with _Ni suffix
- BQX windows = {BQX_WINDOWS} (intervals, not minutes)
- Must handle weekend/holiday gaps correctly
""",
                'source': 'scripts/interval_centric_implementation.py'
            }

            try:
                tasks_table.create(task_data)
                print(f"    ✓ Created task: {task_data['task_id']}")
                task_num += 1
            except Exception as e:
                print(f"    Error creating task: {e}")

def update_all_feature_tasks():
    """Update all feature engineering tasks with INTERVAL-CENTRIC mandate."""

    all_tasks = tasks_table.all()
    updated_count = 0

    interval_mandate = """

### ⚠️ INTERVAL-CENTRIC MANDATE
ALL window operations MUST use ROWS BETWEEN.
- FORBIDDEN: RANGE BETWEEN, time-based windows
- REQUIRED: ROWS BETWEEN N PRECEDING AND CURRENT ROW
- Naming: _Ni suffix for intervals (not _Nm for minutes)
- BQX windows [45,90,180,360,720,1440,2880] = INTERVALS
"""

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')

        # Update tasks in feature engineering phases
        if any(task_id.startswith(phase) for phase in ['MP03.P05', 'MP03.P06', 'MP03.P07']):
            current_notes = task['fields'].get('notes', '')

            # Only update if not already updated
            if 'INTERVAL-CENTRIC MANDATE' not in current_notes:
                updated_notes = current_notes + interval_mandate

                try:
                    tasks_table.update(task['id'], {'notes': updated_notes})
                    updated_count += 1

                    if updated_count % 10 == 0:
                        print(f"  Updated {updated_count} tasks...")

                except Exception as e:
                    print(f"  Error updating task {task_id}: {e}")

    print(f"✓ Updated {updated_count} tasks with INTERVAL-CENTRIC mandate")
    return updated_count

def validate_coverage():
    """Validate comprehensive coverage of INTERVAL-CENTRIC recommendations."""

    print("\n=== Coverage Validation ===")

    checks = {
        'BQX Autoregressive Lags': False,
        'Multi-Resolution Features': False,
        'BQX Momentum Derivatives': False,
        'Interval-Based Regimes': False,
        'Data Leakage Prevention': False,
        'Interval Validation Framework': False,
        'ROWS BETWEEN Mandate': False,
        'Naming Convention (_Ni)': False
    }

    # Check stages and tasks
    all_stages = stages_table.all()
    all_tasks = tasks_table.all()

    # Combine all text to search
    all_text = ""
    for stage in all_stages:
        all_text += stage['fields'].get('description', '') + " "
        all_text += stage['fields'].get('notes', '') + " "
    for task in all_tasks:
        all_text += task['fields'].get('notes', '') + " "

    # Check for specific patterns
    if 'LAG(bqx_mid' in all_text or 'bqx_mid_lag' in all_text:
        checks['BQX Autoregressive Lags'] = True
    if 'multi-resolution' in all_text.lower() or 'bqx_5i' in all_text:
        checks['Multi-Resolution Features'] = True
    if 'velocity' in all_text.lower() or 'acceleration' in all_text.lower():
        checks['BQX Momentum Derivatives'] = True
    if 'interval-based' in all_text.lower() and 'regime' in all_text.lower():
        checks['Interval-Based Regimes'] = True
    if 'leakage prevention' in all_text.lower() or 'temporal isolation' in all_text.lower():
        checks['Data Leakage Prevention'] = True
    if 'validation framework' in all_text.lower() or 'ROWS BETWEEN' in all_text:
        checks['Interval Validation Framework'] = True
    if 'ROWS BETWEEN' in all_text and 'INTERVAL-CENTRIC' in all_text:
        checks['ROWS BETWEEN Mandate'] = True
    if '_Ni' in all_text or '_ni' in all_text.lower() or 'lag_1i' in all_text:
        checks['Naming Convention (_Ni)'] = True

    # Calculate coverage
    covered = sum(1 for v in checks.values() if v)
    total = len(checks)
    coverage_pct = (covered / total) * 100

    print("\nRecommendation Coverage:")
    for recommendation, is_covered in checks.items():
        status = "✅" if is_covered else "❌"
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
    print("INTERVAL-CENTRIC AirTable Update Script V2")
    print("Incorporating V2.0 Recommendations into Project Plan")
    print("=" * 60)

    if not API_KEY or not BASE_ID:
        print("ERROR: AirTable credentials not found")
        return 1

    print("\n1. Updating BQX paradigm stages...")
    updated_stages = update_bqx_paradigm_stages()
    print(f"   Updated {len(updated_stages)} stages")

    print("\n2. Creating new INTERVAL-CENTRIC stages...")
    created_stages = create_new_interval_stages()
    print(f"   Created {len(created_stages)} new stages")

    print("\n3. Updating all feature engineering tasks...")
    updated_tasks = update_all_feature_tasks()
    print(f"   Updated {updated_tasks} tasks")

    print("\n4. Validating coverage...")
    coverage = validate_coverage()

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Stages updated: {len(updated_stages)}")
    print(f"  Stages created: {len(created_stages)}")
    print(f"  Tasks updated: {updated_tasks}")
    print(f"  Coverage achieved: {coverage:.1f}%")

    if coverage == 100:
        print("\n✅ SUCCESS: Full INTERVAL-CENTRIC integration complete!")
    else:
        print(f"\n⚠️ Partial success: {coverage:.1f}% coverage achieved")

    print("=" * 60)

    return 0 if coverage >= 90 else 1

if __name__ == "__main__":
    exit(main())