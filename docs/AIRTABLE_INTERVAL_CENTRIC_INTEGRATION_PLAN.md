# AirTable Integration Plan: INTERVAL-CENTRIC Recommendations
## Achieving 100% Coverage of V2.0 Recommendations in Project Management

---

## Integration Strategy

### Phase 1: Mapping Analysis
Map each recommendation to existing AirTable records and identify gaps.

### Phase 2: Record Enhancement
Update existing records with interval-centric specifications.

### Phase 3: New Record Creation
Add new stages/tasks for uncovered recommendations.

### Phase 4: Validation Framework
Create validation tasks to ensure interval consistency.

---

## Detailed Mapping to AirTable Structure

### 🔷 PHASE MP03.04: DATA PIPELINE & FEATURE ENGINEERING
**Status**: Needs Major Updates

#### Existing Stages to Update:

##### S03.04.01: Create Secondary Feature Tables (lag_bqx_*)
**Current**: Basic lag features
**Update Required**:
- Add INTERVAL-CENTRIC BQX autoregressive features
- Specify LAG operations use intervals (1-180)
- Include bqx_mid, bqx_ask, bqx_bid lags
**New Description**:
```
Implements INTERVAL-CENTRIC lag features using ROWS BETWEEN. Creates lag_bqx_* tables with BQX autoregressive features from past intervals (1i through 180i). Critical: LAG(bqx_mid, N) represents N intervals ago, not N minutes. Includes short (1-10i), medium (15-45i), and long-term (60-180i) BQX momentum patterns.
```

##### S03.04.02: Create Tertiary Feature Tables (regime_bqx_*)
**Current**: Regime detection
**Update Required**:
- Specify INTERVAL-BASED regime calculation
- Use ROWS BETWEEN for all statistics
**New Description**:
```
Implements INTERVAL-BASED regime detection using rolling statistics over fixed row counts. Uses ROWS BETWEEN 89 PRECEDING for 90-interval volatility, ROWS BETWEEN 359 PRECEDING for 360-interval trends. Classifies market states (trending/ranging/volatile) based on interval statistics, not time-based metrics.
```

##### S03.04.03: Create Quaternary Feature Tables (agg_bqx_*)
**Current**: Aggregation features
**Update Required**:
- Multi-resolution INTERVAL aggregations
- Specify windows as row counts
**New Description**:
```
Creates multi-resolution BQX features using INTERVAL-BASED aggregations. Implements 5i, 15i, 45i, 90i, 180i, 360i averages using ROWS BETWEEN. Each aggregation uses exact row counts regardless of time gaps. Includes interval alignment signals for momentum consensus.
```

#### New Stages to Add:

##### S03.04.07: BQX Momentum Derivatives [NEW]
**Description**:
```
Calculates BQX velocity, acceleration, and jerk using INTERVAL-BASED derivatives. Velocity = change per interval (not per minute). Creates reversal signals based on interval momentum changes. Uses diff(1), diff(5), diff(15) for multi-interval derivatives.
```
**Tasks**:
- T03.04.07.01: Implement single-interval velocity (diff(1))
- T03.04.07.02: Implement multi-interval velocities (diff(5), diff(15))
- T03.04.07.03: Calculate acceleration (velocity derivatives)
- T03.04.07.04: Generate reversal signals from derivatives

##### S03.04.08: Interval Validation Framework [NEW]
**Description**:
```
Validates all features use ROWS BETWEEN exclusively. Checks for prohibited RANGE BETWEEN or time-based calculations. Ensures consistency across market gaps. Validates naming convention (_Ni suffix for intervals).
```
**Tasks**:
- T03.04.08.01: SQL validation for ROWS BETWEEN usage
- T03.04.08.02: Python validation for integer windows
- T03.04.08.03: Gap consistency validation
- T03.04.08.04: Naming convention validation

##### S03.04.09: Data Leakage Prevention [NEW]
**Description**:
```
Implements strict INTERVAL-BASED temporal isolation. Ensures features use past intervals (t-n) and targets use future intervals (t+n). Critical for preventing lookahead bias. Uses LAG for features, LEAD for targets exclusively.
```
**Tasks**:
- T03.04.09.01: Create temporal isolation validation
- T03.04.09.02: Implement safe feature extraction
- T03.04.09.03: Validate no future data in features
- T03.04.09.04: Create leakage detection tests

---

## Task-Level Updates Required

### Critical Task Updates for INTERVAL Compliance

#### Tasks in S03.04.01 (lag_bqx_* tables):
```python
# Update each task's notes field with:
"""
INTERVAL-CENTRIC Implementation:
- Use LAG(bqx_mid, N) where N = intervals, not minutes
- Include lags: 1i, 2i, 3i, 5i, 10i, 15i, 30i, 45i, 60i, 90i, 120i, 180i
- SQL must use: LAG(column, N) OVER (ORDER BY bar_start_time)
- Feature naming: bqx_mid_lag_5i (not bqx_mid_lag_5m)
- Validation: Verify consistency across weekend gaps

BQX_LAGS = [1, 2, 3, 5, 10, 15, 30, 45, 60, 90, 120, 180]
for lag in BQX_LAGS:
    features[f'bqx_mid_lag_{lag}i'] = f'LAG(bqx_mid, {lag})'
"""
```

#### Tasks in S03.04.02 (regime_bqx_* tables):
```python
# Update notes with:
"""
INTERVAL-BASED Regime Detection:
- 45-interval volatility: ROWS BETWEEN 44 PRECEDING AND CURRENT ROW
- 90-interval volatility: ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
- 360-interval trend: ROWS BETWEEN 359 PRECEDING AND CURRENT ROW
- NO time-based windows allowed
- Regime thresholds based on interval statistics

STDDEV(bqx_mid) OVER (
    ORDER BY bar_start_time
    ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
) AS bqx_90i_std
"""
```

#### Tasks in S03.04.03 (agg_bqx_* tables):
```python
# Update notes with:
"""
Multi-Resolution INTERVAL Aggregations:
RESOLUTIONS = {
    5: 'ROWS BETWEEN 4 PRECEDING AND CURRENT ROW',
    15: 'ROWS BETWEEN 14 PRECEDING AND CURRENT ROW',
    45: 'ROWS BETWEEN 44 PRECEDING AND CURRENT ROW',
    90: 'ROWS BETWEEN 89 PRECEDING AND CURRENT ROW',
    180: 'ROWS BETWEEN 179 PRECEDING AND CURRENT ROW',
    360: 'ROWS BETWEEN 359 PRECEDING AND CURRENT ROW'
}

Each window = exact row count, not time period
Alignment signals compare multiple interval resolutions
"""
```

---

## Implementation Script Structure

```python
# /home/micha/bqx_ml_v3/scripts/update_airtable_interval_centric.py

def update_airtable_for_interval_centric():
    """
    Updates all AirTable records with INTERVAL-CENTRIC specifications
    """

    # 1. Update existing stages
    stage_updates = {
        'S03.04.01': {
            'description': 'INTERVAL-CENTRIC lag features using ROWS BETWEEN...',
            'notes': add_interval_lag_details()
        },
        'S03.04.02': {
            'description': 'INTERVAL-BASED regime detection...',
            'notes': add_interval_regime_details()
        },
        'S03.04.03': {
            'description': 'Multi-resolution INTERVAL aggregations...',
            'notes': add_interval_aggregation_details()
        }
    }

    # 2. Create new stages
    new_stages = [
        {
            'stage_id': 'S03.04.07',
            'name': 'BQX Momentum Derivatives',
            'description': 'Calculates velocity/acceleration per INTERVAL...',
            'phase_link': get_phase_record('MP03.04')
        },
        {
            'stage_id': 'S03.04.08',
            'name': 'Interval Validation Framework',
            'description': 'Validates ROWS BETWEEN usage...',
            'phase_link': get_phase_record('MP03.04')
        },
        {
            'stage_id': 'S03.04.09',
            'name': 'Data Leakage Prevention',
            'description': 'INTERVAL-BASED temporal isolation...',
            'phase_link': get_phase_record('MP03.04')
        }
    ]

    # 3. Update all task notes
    task_updates = update_all_task_notes_with_interval_specs()

    # 4. Add validation tasks
    validation_tasks = create_interval_validation_tasks()

    return {
        'stages_updated': len(stage_updates),
        'stages_created': len(new_stages),
        'tasks_updated': len(task_updates),
        'tasks_created': len(validation_tasks)
    }
```

---

## Coverage Checklist

### V2.0 Recommendations Coverage:

| Recommendation | AirTable Location | Coverage Status |
|----------------|-------------------|-----------------|
| **Data Leakage Prevention** | New S03.04.09 | ✅ Full coverage |
| **BQX Autoregressive Lags** | S03.04.01 (updated) | ✅ Full coverage |
| **Multi-Resolution Features** | S03.04.03 (updated) | ✅ Full coverage |
| **BQX Momentum Derivatives** | New S03.04.07 | ✅ Full coverage |
| **Regime Detection (Interval)** | S03.04.02 (updated) | ✅ Full coverage |
| **Interval Validation** | New S03.04.08 | ✅ Full coverage |
| **ROWS BETWEEN Mandate** | All task notes | ✅ Full coverage |
| **Naming Convention (_Ni)** | Documentation tasks | ✅ Full coverage |

### Metrics for Success:
- **100%** of V2.0 recommendations mapped to AirTable records
- **All** SQL specifications include ROWS BETWEEN
- **Zero** time-based window references
- **All** feature names use _Ni suffix for intervals

---

## Update Priority Order

### Week 1 (Critical):
1. Update S03.04.01 (lag features) - Add BQX autoregressive
2. Create S03.04.09 (leakage prevention)
3. Update all task notes with ROWS BETWEEN

### Week 2 (Important):
1. Update S03.04.02, S03.04.03 with interval specs
2. Create S03.04.07 (derivatives)
3. Add validation framework (S03.04.08)

### Week 3 (Validation):
1. Run validation checks
2. Update any remaining records
3. Final QA scoring verification

---

## Expected Outcomes

After implementing this integration plan:

1. **Complete Traceability**: Every V2.0 recommendation traceable to specific AirTable records
2. **Clear Implementation Guidance**: Each task contains interval-specific code/SQL
3. **Validation Framework**: Automated checks ensure interval compliance
4. **Consistent Naming**: All features follow _Ni convention
5. **Zero Time Dependencies**: No RANGE BETWEEN or time-based calculations

---

## Success Validation

```python
def validate_airtable_interval_coverage():
    """
    Validates 100% coverage of INTERVAL-CENTRIC recommendations
    """
    checks = {
        'all_stages_have_rows_between': check_sql_specs(),
        'no_time_based_windows': check_no_range_between(),
        'naming_convention_followed': check_ni_suffix(),
        'bqx_autoregressive_present': check_lag_features(),
        'derivatives_implemented': check_momentum_derivatives(),
        'validation_tasks_exist': check_validation_framework()
    }

    coverage = sum(1 for check in checks.values() if check) / len(checks) * 100
    print(f"INTERVAL-CENTRIC Coverage: {coverage}%")
    return coverage == 100
```

---

*This plan ensures 100% coverage of V2.0 INTERVAL-CENTRIC recommendations in AirTable project management.*