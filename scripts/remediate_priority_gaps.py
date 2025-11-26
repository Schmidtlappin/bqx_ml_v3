#!/usr/bin/env python3
"""
Remediate HIGH and MEDIUM priority gaps identified in gap analysis.
Adds missing tasks to AirTable for complete MLOps coverage.
"""

import os
import json
import time
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

def add_priority_gap_tasks():
    """Add all priority gap remediation tasks to AirTable."""
    print("=" * 80)
    print("REMEDIATING PRIORITY GAPS IN AIRTABLE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all stages for finding appropriate locations
    stages = stages_table.all()
    stages_by_id = {s['fields'].get('stage_id'): s for s in stages}

    # Track results
    tasks_created = []
    tasks_failed = []

    # Define all gap remediation tasks
    gap_tasks = [
        {
            'priority': 'HIGH',
            'name': 'Vertex AI Datasets',
            'stage_id': 'MP03.P05.S04',  # Data pipelines stage
            'task_suffix': 'T97',
            'description': """**Configure Vertex AI Datasets for TabularDataset Creation**

**Objective**: Create aiplatform.TabularDataset from BigQuery feature tables for streamlined model training and serving.

**Scope**: Configure Vertex AI Datasets to ingest feature data from BigQuery, enabling managed dataset versioning and lineage tracking.""",

            'notes': """### Implementation Details

**Technical Requirements**:
• Create TabularDataset from BigQuery feature tables
• Support all 28 currency pairs
• Enable dataset versioning for reproducibility
• Implement INTERVAL-CENTRIC feature extraction

**Implementation Steps**:

1. **Dataset Creation Pipeline**:
```python
from google.cloud import aiplatform

def create_vertex_dataset(pair, source_table):
    dataset = aiplatform.TabularDataset.create(
        display_name=f"bqx_features_{pair}",
        gcs_source=None,
        bq_source=f"bq://{project_id}.{dataset_id}.{source_table}",
        labels={"pair": pair, "version": "v3", "type": "interval_centric"}
    )
    return dataset
```

2. **Feature Schema Definition**:
```python
feature_schema = {
    "idx_features": ["idx_mid", "idx_close", "idx_spread"],
    "bqx_features": ["bqx_45w", "bqx_90w", "bqx_180w"],
    "lag_features": ["lag_1i", "lag_5i", "lag_45i", "lag_90i"],
    "target": "bqx_future_90i"
}
```

3. **Dataset Versioning**:
• Tag datasets with version numbers
• Maintain dataset lineage in Vertex AI
• Enable rollback to previous versions

**Success Criteria**:
• All 28 currency pairs have TabularDatasets
• Datasets auto-refresh when source tables update
• Version control and lineage tracking enabled"""
        },
        {
            'priority': 'HIGH',
            'name': 'Scheduled Model Retraining',
            'stage_id': 'MP03.P09.S04',  # Production monitoring stage
            'task_suffix': 'T96',
            'description': """**Configure Cloud Scheduler for Periodic Model Retraining**

**Objective**: Implement automated weekly/monthly model retraining jobs to maintain prediction accuracy with latest market data.

**Scope**: Set up Cloud Scheduler to trigger Vertex AI training pipelines on a regular schedule for all 28 models.""",

            'notes': """### Scheduled Retraining Implementation

**Schedule Configuration**:
• Weekly retraining for high-volume pairs (EUR/USD, GBP/USD)
• Bi-weekly for medium-volume pairs
• Monthly for low-volume pairs

**Cloud Scheduler Setup**:
```python
from google.cloud import scheduler

def create_retraining_schedule(pair, frequency):
    client = scheduler.CloudSchedulerClient()
    parent = f"projects/{project_id}/locations/{location}"

    job = {
        "name": f"{parent}/jobs/retrain_{pair}",
        "description": f"Retrain BQX ML model for {pair}",
        "schedule": frequency,  # e.g., "0 2 * * 1" for weekly
        "time_zone": "UTC",
        "http_target": {
            "uri": f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/trainingJobs",
            "http_method": "POST",
            "body": json.dumps({
                "displayName": f"retrain_{pair}_{datetime.now().strftime('%Y%m%d')}",
                "model": f"bqx_model_{pair}",
                "trainingInput": {...}
            })
        }
    }
    return client.create_job(parent=parent, job=job)
```

**Retraining Pipeline**:
1. Fetch latest feature data (last 90 days)
2. Validate data quality and completeness
3. Train model with updated data
4. Evaluate against holdout set
5. Deploy if performance improves
6. Archive previous model version

**Monitoring**:
• Track retraining success/failure rates
• Monitor performance drift between versions
• Alert on retraining failures

**INTERVAL-CENTRIC Compliance**:
• All feature windows use ROWS BETWEEN
• Consistent interval calculations across retraining"""
        },
        {
            'priority': 'HIGH',
            'name': 'Scheduled Predictions',
            'stage_id': 'MP03.P09.S01',  # Production deployment stage
            'task_suffix': 'T95',
            'description': """**Configure Scheduled Batch Prediction Jobs**

**Objective**: Implement Cloud Scheduler to trigger regular batch predictions for systematic forecast generation.

**Scope**: Schedule automated batch predictions at multiple intervals throughout the day for all currency pairs.""",

            'notes': """### Scheduled Batch Predictions

**Schedule Strategy**:
• Hourly: Short-term predictions (N+45, N+90)
• 4-hourly: Medium-term (N+180, N+360)
• Daily: Long-term (N+720, N+1440, N+2880)
• Market-aware: Increased frequency during market hours

**Implementation**:
```python
def create_prediction_schedule():
    schedules = {
        "hourly": "0 * * * *",
        "4_hourly": "0 */4 * * *",
        "daily": "0 0 * * *",
        "market_open": "0 9 * * 1-5",
        "market_close": "0 17 * * 1-5"
    }

    for schedule_name, cron in schedules.items():
        job = scheduler.Job(
            name=f"predict_{schedule_name}",
            schedule=cron,
            http_target={
                "uri": vertex_ai_batch_endpoint,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "instances": get_latest_features(),
                    "parameters": {"horizons": get_horizons(schedule_name)}
                })
            }
        )
```

**Output Management**:
• Write predictions to time-partitioned BigQuery tables
• Maintain prediction history for backtesting
• Enable real-time access via Feature Store

**Quality Checks**:
• Validate input feature completeness
• Check prediction value ranges
• Monitor prediction latency
• Alert on anomalous predictions

**INTERVAL-CENTRIC**:
• All predictions at specific future intervals (N+45, N+90, etc.)
• No time-based scheduling logic in predictions themselves"""
        },
        {
            'priority': 'MEDIUM',
            'name': 'Confusion Matrix Analysis',
            'stage_id': 'MP03.P08.S02',  # Model evaluation stage
            'task_suffix': 'T94',
            'description': """**Implement Confusion Matrix for Directional Predictions**

**Objective**: Add confusion matrix analysis to evaluate directional prediction accuracy (up/down/neutral) for BQX momentum.

**Scope**: Create classification metrics alongside regression metrics for comprehensive model evaluation.""",

            'notes': """### Confusion Matrix Implementation

**Directional Classification**:
```python
def create_directional_labels(bqx_values, thresholds=(-0.0001, 0.0001)):
    labels = []
    for val in bqx_values:
        if val < thresholds[0]:
            labels.append("DOWN")
        elif val > thresholds[1]:
            labels.append("UP")
        else:
            labels.append("NEUTRAL")
    return labels
```

**Confusion Matrix Calculation**:
```python
from sklearn.metrics import confusion_matrix, classification_report

def evaluate_directional_accuracy(y_true, y_pred):
    # Convert to directional
    true_dir = create_directional_labels(y_true)
    pred_dir = create_directional_labels(y_pred)

    # Generate confusion matrix
    cm = confusion_matrix(true_dir, pred_dir,
                         labels=["DOWN", "NEUTRAL", "UP"])

    # Calculate metrics
    report = classification_report(true_dir, pred_dir,
                                  output_dict=True)

    return {
        "confusion_matrix": cm,
        "accuracy": report["accuracy"],
        "precision_per_class": {
            "down": report["DOWN"]["precision"],
            "neutral": report["NEUTRAL"]["precision"],
            "up": report["UP"]["precision"]
        },
        "recall_per_class": {...},
        "f1_per_class": {...}
    }
```

**Visualization**:
• Heatmap visualization of confusion matrix
• Time-series of directional accuracy
• Per-horizon accuracy comparison

**Integration with MLOps**:
• Add to model evaluation pipeline
• Track in experiment runs
• Include in model cards"""
        },
        {
            'priority': 'MEDIUM',
            'name': 'Residual Analysis',
            'stage_id': 'MP03.P08.S03',  # Model diagnostics stage
            'task_suffix': 'T93',
            'description': """**Implement Residual Analysis for Model Diagnostics**

**Objective**: Add comprehensive residual analysis to validate regression assumptions and identify model improvements.

**Scope**: Implement residual plots, statistical tests, and diagnostics for all prediction horizons.""",

            'notes': """### Residual Analysis Implementation

**Residual Calculations**:
```python
def analyze_residuals(y_true, y_pred):
    residuals = y_true - y_pred

    diagnostics = {
        "mean_residual": np.mean(residuals),
        "std_residual": np.std(residuals),
        "skewness": scipy.stats.skew(residuals),
        "kurtosis": scipy.stats.kurtosis(residuals),
        "normality_test": scipy.stats.normaltest(residuals),
        "autocorrelation": calculate_acf(residuals)
    }
    return diagnostics
```

**Diagnostic Plots**:
1. **Residuals vs Fitted**: Check for homoscedasticity
2. **Q-Q Plot**: Assess normality of residuals
3. **Scale-Location**: Check variance consistency
4. **Residuals vs Leverage**: Identify influential points
5. **ACF/PACF**: Check for autocorrelation

**Statistical Tests**:
```python
def residual_tests(residuals, predictions):
    tests = {
        "breusch_pagan": het_breuschpagan(residuals, predictions),
        "durbin_watson": durbin_watson(residuals),
        "jarque_bera": jarque_bera(residuals),
        "ljung_box": acorr_ljungbox(residuals)
    }
    return tests
```

**Pattern Detection**:
• Identify systematic biases per interval horizon
• Detect heteroscedasticity patterns
• Find autocorrelation in residuals
• Identify outliers and influential observations

**Remediation Actions**:
• If heteroscedastic: Consider weighted regression
• If autocorrelated: Add lag features or AR terms
• If non-normal: Consider transformations
• If biased: Adjust model or add features

**INTERVAL-CENTRIC Context**:
• Analyze residuals by interval horizon
• Check for interval-specific patterns
• Validate across different market regimes"""
        }
    ]

    print(f"\n📋 Tasks to Create: {len(gap_tasks)}")
    print("  HIGH Priority: 3 tasks")
    print("  MEDIUM Priority: 2 tasks")

    # Create each task
    for gap in gap_tasks:
        stage_id = gap['stage_id']
        stage = stages_by_id.get(stage_id)

        if not stage:
            print(f"\n⚠️ Stage {stage_id} not found, searching alternatives...")
            # Find alternative stage
            for sid, s in stages_by_id.items():
                if stage_id[:8] in sid:  # Match phase
                    stage = s
                    stage_id = sid
                    break

        if not stage:
            print(f"❌ Could not find stage for {gap['name']}")
            tasks_failed.append(gap['name'])
            continue

        task_data = {
            'task_id': f"{stage_id}.{gap['task_suffix']}",
            'description': gap['description'],
            'notes': gap['notes'],
            'status': 'Todo',
            'priority': gap['priority'].capitalize(),
            'stage_link': [stage['id']]
        }

        try:
            print(f"\n📝 Creating {gap['priority']} priority task: {gap['name']}...")
            new_task = tasks_table.create(task_data)
            print(f"  ✅ Created: {new_task['fields']['task_id']}")
            tasks_created.append(gap['name'])

            # Update stage task_link
            current_links = stage['fields'].get('task_link', [])
            current_links.append(new_task['id'])
            stages_table.update(stage['id'], {'task_link': current_links})

            time.sleep(0.2)  # Rate limit

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            tasks_failed.append(gap['name'])

    return tasks_created, tasks_failed

def verify_gap_remediation():
    """Verify that all gaps have been addressed."""
    print("\n" + "=" * 80)
    print("VERIFYING GAP REMEDIATION")
    print("=" * 80)

    tasks = tasks_table.all()

    # Check for gap-related tasks
    gap_keywords = {
        'Vertex AI Datasets': 'tabulardataset',
        'Scheduled Model Retraining': 'retraining',
        'Scheduled Predictions': 'scheduled batch',
        'Confusion Matrix': 'confusion matrix',
        'Residual Analysis': 'residual'
    }

    gaps_found = {gap: False for gap in gap_keywords.keys()}

    for task in tasks:
        desc = task['fields'].get('description', '').lower()
        notes = (task['fields'].get('notes', '') or '').lower()
        content = f"{desc} {notes}"

        for gap, keyword in gap_keywords.items():
            if keyword in content:
                gaps_found[gap] = True

    print("\n📊 Gap Coverage Status:")
    for gap, found in gaps_found.items():
        status = "✅" if found else "❌"
        print(f"  {status} {gap}")

    all_covered = all(gaps_found.values())
    return all_covered

def main():
    """Main execution."""
    print("=" * 80)
    print("PRIORITY GAP REMEDIATION")
    print("=" * 80)

    # Create tasks for all gaps
    created, failed = add_priority_gap_tasks()

    # Verify remediation
    all_covered = verify_gap_remediation()

    # Summary
    print("\n" + "=" * 80)
    print("REMEDIATION SUMMARY")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"  Tasks created: {len(created)}")
    print(f"  Tasks failed: {len(failed)}")

    if created:
        print(f"\n✅ Successfully created tasks:")
        for task in created:
            print(f"    • {task}")

    if failed:
        print(f"\n❌ Failed to create tasks:")
        for task in failed:
            print(f"    • {task}")

    if all_covered:
        print(f"\n🎉 SUCCESS! All priority gaps have been remediated")
    else:
        print(f"\n⚠️ Some gaps may still need attention")

    print(f"\n📋 Next Steps:")
    print(f"  1. Review new tasks in AirTable")
    print(f"  2. Assign to appropriate team members")
    print(f"  3. Update priorities and timelines")
    print(f"  4. Begin implementation")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    exit(main())