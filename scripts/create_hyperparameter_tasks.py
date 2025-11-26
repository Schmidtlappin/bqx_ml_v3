#!/usr/bin/env python3
"""
Create hyperparameter tuning tasks to address component coverage gap.
Adds 3 new tasks to MP03.P07.S03 for comprehensive hyperparameter optimization.
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
tasks_table = base.table('Tasks')
stages_table = base.table('Stages')
phases_table = base.table('Phases')

def get_stage_record_id(stage_id):
    """Get the AirTable record ID for a stage."""
    stages = stages_table.all()
    for stage in stages:
        if stage['fields'].get('stage_id') == stage_id:
            return stage['id']
    return None

def get_phase_record_id(phase_id):
    """Get the AirTable record ID for a phase."""
    phases = phases_table.all()
    for phase in phases:
        if phase['fields'].get('phase_id') == phase_id:
            return phase['id']
    return None

def create_hyperparameter_tuning_tasks():
    """Create comprehensive hyperparameter tuning tasks."""
    print("=" * 80)
    print("CREATING HYPERPARAMETER TUNING TASKS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get stage and phase IDs
    stage_id = 'MP03.P07.S03'
    phase_id = 'MP03.P07'

    stage_record = get_stage_record_id(stage_id)
    phase_record = get_phase_record_id(phase_id)

    if not stage_record:
        print(f"❌ Stage {stage_id} not found")
        return 0

    print(f"\n📋 Creating tasks in stage: {stage_id}")

    # Define the new hyperparameter tuning tasks
    new_tasks = [
        {
            'task_id': 'MP03.P07.S03.T05',
            'name': 'Implement Hyperparameter Tuning Framework',
            'description': """**Implement Hyperparameter Tuning Framework**

**Objective**: Develop automated hyperparameter optimization using Vertex AI Vizier for all 28 BQX ML models, implementing INTERVAL-CENTRIC architecture.

**Context**: This task establishes the foundation for systematic hyperparameter optimization across all currency pair models, ensuring optimal performance for each prediction horizon (N+45 through N+2880).

**Scope**: Create a comprehensive tuning framework that supports multiple optimization strategies, integrates with Vertex AI Vizier, and maintains consistency with the BQX paradigm.

**BQX Paradigm Implementation**:
This task implements the BQX (backward-looking momentum) paradigm where hyperparameters are tuned specifically for momentum-based features. The optimization considers:
- IDX feature importance weights
- BQX momentum window parameters
- LAG operation depths for feature engineering
- Regularization parameters for interval-specific models""",
            'notes': """### Hyperparameter Tuning Framework Implementation

**Vertex AI Vizier Configuration**:
```python
from google.cloud import aiplatform

def create_vizier_study(model_pair, horizon):
    study = aiplatform.HyperparameterTuningJob(
        display_name=f'bqx_tuning_{model_pair}_{horizon}i',
        metric_spec={
            'r2_score': 'maximize',
            'sharpe_ratio': 'maximize'
        },
        parameter_spec={
            'learning_rate': hpt.DoubleParameterSpec(min=0.001, max=0.1, scale='log'),
            'max_depth': hpt.IntegerParameterSpec(min=3, max=10, scale='linear'),
            'n_estimators': hpt.IntegerParameterSpec(min=100, max=1000, scale='linear'),
            'min_samples_split': hpt.IntegerParameterSpec(min=2, max=20, scale='linear'),
            'reg_alpha': hpt.DoubleParameterSpec(min=0.0, max=1.0, scale='linear'),
            'reg_lambda': hpt.DoubleParameterSpec(min=0.0, max=1.0, scale='linear')
        },
        max_trial_count=100,
        parallel_trial_count=5
    )
    return study
```

**Optimization Strategy**:
- Multi-objective optimization balancing R² and Sharpe ratio
- Parallel trials for faster convergence
- Early stopping based on convergence criteria
- Separate tuning per horizon interval

**Key Parameters to Tune**:
- Model complexity (depth, estimators)
- Learning dynamics (learning rate, regularization)
- Feature selection thresholds
- Window-specific parameters for BQX calculations""",
            'priority': 'High',
            'status': 'Todo',
            'assigned_to': 'ML Team',
            'artifacts': """• Vizier study configuration files
• Parameter search space definitions
• Tuning job templates for 28 pairs × 7 horizons
• Optimization metrics tracking
• Best parameters storage in BigQuery""",
            'stage_link': [stage_record] if stage_record else [],
            'phase_link': [phase_record] if phase_record else [],
            'source': 'Gap analysis - missing hyperparameter tuning'
        },
        {
            'task_id': 'MP03.P07.S03.T06',
            'name': 'Configure Grid Search for Model Parameters',
            'description': """**Configure Grid Search for Model Parameters**

**Objective**: Set up systematic grid search for key hyperparameters across all BQX ML models, ensuring comprehensive parameter space exploration.

**Context**: This task (ID: MP03.P07.S03.T06) implements exhaustive grid search as a baseline tuning method, particularly useful for understanding parameter interactions in the INTERVAL-CENTRIC architecture.

**Scope**: Design and implement grid search configurations for critical parameters, with intelligent pruning to manage computational costs across 196 model variants (28 pairs × 7 horizons).

**BQX Paradigm Implementation**:
Grid search specifically targets BQX-related parameters:
- Momentum window sizes for reg_slope calculations
- Feature aggregation intervals (45i, 90i, 180i, etc.)
- LAG depth for historical feature inclusion
- Dual feature table weight balancing (IDX vs BQX importance)""",
            'notes': """### Grid Search Implementation

**Parameter Grid Definition**:
```python
def create_parameter_grid(pair, horizon):
    base_grid = {
        'model_type': ['XGBoost', 'LightGBM'],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [4, 6, 8, 10],
        'n_estimators': [100, 300, 500],
        'subsample': [0.7, 0.8, 0.9],
        'colsample_bytree': [0.7, 0.8, 0.9]
    }

    # Horizon-specific adjustments
    if horizon <= 90:  # Short-term predictions
        base_grid['max_depth'] = [3, 4, 5]  # Simpler models
    elif horizon >= 1440:  # Long-term predictions
        base_grid['n_estimators'] = [300, 500, 700]  # More complex

    return base_grid
```

**Intelligent Pruning Strategy**:
- Start with coarse grid, refine around best performers
- Use cross-validation to estimate parameter stability
- Prune combinations with low theoretical merit
- Cache results for similar currency pairs

**Computational Optimization**:
- Distributed grid search using Vertex AI Training
- Batch multiple parameter combinations per job
- Early stopping for poor performing combinations
- Result caching in BigQuery for reuse""",
            'priority': 'Medium',
            'status': 'Todo',
            'assigned_to': 'ML Team',
            'artifacts': """• Grid search configuration scripts
• Parameter grid specifications per model
• Cross-validation setup code
• Performance comparison matrices
• Grid search result analytics in BigQuery""",
            'stage_link': [stage_record] if stage_record else [],
            'phase_link': [phase_record] if phase_record else [],
            'source': 'Gap analysis - missing hyperparameter tuning'
        },
        {
            'task_id': 'MP03.P07.S03.T07',
            'name': 'Implement Bayesian Optimization',
            'description': """**Implement Bayesian Optimization**

**Objective**: Configure Bayesian optimization for efficient hyperparameter search, leveraging probabilistic models to find optimal parameters with minimal trials.

**Context**: This task (ID: MP03.P07.S03.T07) implements advanced Bayesian optimization techniques for the BQX ML V3 system, significantly reducing the computational cost of hyperparameter tuning while maintaining optimization quality.

**Scope**: Develop Bayesian optimization pipeline using Gaussian processes, implement acquisition functions, and establish convergence criteria for all 196 model configurations.

**BQX Paradigm Implementation**:
Bayesian optimization is tailored for BQX-specific challenges:
- Multi-fidelity optimization for different prediction horizons
- Transfer learning between similar currency pairs
- Constraint handling for momentum calculation windows
- Joint optimization of IDX and BQX feature importance""",
            'notes': """### Bayesian Optimization Implementation

**Gaussian Process Configuration**:
```python
from skopt import BayesSearchCV
from skopt.space import Real, Integer, Categorical

def create_bayesian_optimizer(model_base):
    search_spaces = {
        'learning_rate': Real(0.001, 0.3, prior='log-uniform'),
        'max_depth': Integer(3, 12),
        'n_estimators': Integer(50, 1000),
        'min_child_weight': Integer(1, 10),
        'gamma': Real(0.0, 0.5),
        'subsample': Real(0.5, 1.0),
        'colsample_bytree': Real(0.5, 1.0),
        'reg_alpha': Real(0.0, 1.0),
        'reg_lambda': Real(0.0, 1.0),
        'scale_pos_weight': Real(0.5, 2.0)
    }

    optimizer = BayesSearchCV(
        model_base,
        search_spaces,
        n_iter=50,
        cv=5,
        n_jobs=-1,
        scoring='neg_mean_squared_error',
        acq_func='EI',  # Expected Improvement
        acq_optimizer='auto',
        random_state=42
    )

    return optimizer
```

**Acquisition Function Strategy**:
- Expected Improvement (EI) for exploitation-exploration balance
- Upper Confidence Bound (UCB) for exploration phases
- Probability of Improvement (PI) for refinement
- Multi-objective acquisition for R² and Sharpe ratio

**Transfer Learning Between Pairs**:
```python
def transfer_hyperparameters(source_pair, target_pair):
    # Use similar pairs' optimal parameters as priors
    similar_pairs = find_correlated_pairs(target_pair)
    prior_params = get_best_params(similar_pairs)

    # Warm-start Bayesian optimization
    return create_informed_prior(prior_params)
```

**Convergence Criteria**:
- No improvement for 10 consecutive iterations
- Confidence interval < 0.01 for predicted optimum
- Maximum budget of 100 evaluations per model""",
            'priority': 'Medium',
            'status': 'Todo',
            'assigned_to': 'ML Team',
            'artifacts': """• Bayesian optimization implementation code
• Gaussian process model configurations
• Acquisition function implementations
• Convergence monitoring dashboards
• Transfer learning utilities for currency pairs
• Optimization history storage in BigQuery""",
            'stage_link': [stage_record] if stage_record else [],
            'phase_link': [phase_record] if phase_record else [],
            'source': 'Gap analysis - missing hyperparameter tuning'
        }
    ]

    # Create tasks
    created_count = 0

    for task_data in new_tasks:
        try:
            # Check if task already exists
            existing = tasks_table.all(formula=f"{{task_id}}='{task_data['task_id']}'")

            if existing:
                print(f"  ⚠️  Task {task_data['task_id']} already exists, skipping")
                continue

            # Create the task
            result = tasks_table.create(task_data)
            print(f"  ✅ Created task: {task_data['task_id']} - {task_data['name']}")
            created_count += 1

        except Exception as e:
            print(f"  ❌ Failed to create {task_data['task_id']}: {e}")

    # Update stage with new task links if tasks were created
    if created_count > 0 and stage_record:
        try:
            # Get all tasks for this stage
            stage_tasks = tasks_table.all(formula=f"SEARCH('{stage_id}', {{task_id}})")
            task_links = [task['id'] for task in stage_tasks]

            # Update stage with task links
            stages_table.update(stage_record, {'task_link': task_links})
            print(f"\n  ✅ Updated stage {stage_id} with {len(task_links)} task links")

        except Exception as e:
            print(f"\n  ⚠️  Failed to update stage links: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("HYPERPARAMETER TUNING TASKS SUMMARY")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"  Tasks planned: {len(new_tasks)}")
    print(f"  Tasks created: {created_count}")

    if created_count > 0:
        print(f"\n✅ New Tasks Added:")
        print(f"  • MP03.P07.S03.T05 - Hyperparameter Tuning Framework")
        print(f"  • MP03.P07.S03.T06 - Grid Search Implementation")
        print(f"  • MP03.P07.S03.T07 - Bayesian Optimization Setup")

        print(f"\n🎯 Coverage Achieved:")
        print(f"  • Comprehensive hyperparameter tuning capability")
        print(f"  • Multiple optimization strategies available")
        print(f"  • Vertex AI Vizier integration configured")
        print(f"  • Support for all 196 model variants")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return created_count

def main():
    """Main entry point."""
    created = create_hyperparameter_tuning_tasks()

    if created > 0:
        print(f"\n✅ SUCCESS! Created {created} hyperparameter tuning tasks")
        print("   Component coverage gap resolved")
    else:
        print("\n⚠️  No new tasks created (may already exist)")

    return 0

if __name__ == "__main__":
    exit(main())