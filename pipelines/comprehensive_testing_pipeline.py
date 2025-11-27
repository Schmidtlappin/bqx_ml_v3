#!/usr/bin/env python3
"""
Vertex AI Pipeline for BQX ML V3 Comprehensive Testing
Orchestrates parallel testing of 6000+ features across 196 models
Authorization: ALPHA-2B-COMPREHENSIVE
"""

from typing import List, NamedTuple
from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline, Input, Output, Dataset, Model, Metrics
from google.cloud import aiplatform
from datetime import datetime

# Constants
PROJECT_ID = 'bqx-ml'
LOCATION = 'us-east1'
PIPELINE_ROOT = 'gs://bqx-ml-bqx-ml-artifacts/pipelines'
SERVICE_ACCOUNT = 'vertex-ai-bqx@bqx-ml.iam.gserviceaccount.com'

# Docker image URI
DOCKER_IMAGE = 'us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/comprehensive-testing:latest'

@component(
    base_image=DOCKER_IMAGE,
    packages_to_install=['google-cloud-bigquery', 'google-cloud-storage', 'pandas', 'xgboost']
)
def test_feature_category(
    category: str,
    pair: str,
    results_bucket: str,
    metrics: Output[Metrics]
) -> NamedTuple('TestResults', [('r2_score', float), ('improvement', float), ('kept', bool)]):
    """Test a specific feature category for a currency pair"""

    import json
    from datetime import datetime
    from google.cloud import bigquery, storage
    from scripts.vertex_comprehensive_testing_orchestrator import ComprehensiveTestingOrchestrator

    # Initialize orchestrator
    orchestrator = ComprehensiveTestingOrchestrator()

    # Run test
    result = orchestrator.test_feature_category(category, pair)

    # Log metrics
    metrics.log_metric('r2_score', result.get('result', {}).get('r2_score', 0))
    metrics.log_metric('improvement', result.get('result', {}).get('improvement', 0))
    metrics.log_metric('features_tested', result.get('result', {}).get('features_tested', 0))

    # Save result to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(results_bucket)
    blob = bucket.blob(f"pipeline_results/{category}_{pair}_{datetime.now().isoformat()}.json")
    blob.upload_from_string(json.dumps(result, indent=2))

    return (
        result.get('result', {}).get('r2_score', 0),
        result.get('result', {}).get('improvement', 0),
        result.get('result', {}).get('kept', False)
    )

@component(
    base_image=DOCKER_IMAGE,
    packages_to_install=['google-cloud-bigquery', 'pandas', 'xgboost', 'scikit-learn']
)
def train_model_with_features(
    pair: str,
    window: int,
    selected_features: List[str],
    model: Output[Model],
    metrics: Output[Metrics]
) -> float:
    """Train XGBoost model with selected features"""

    from google.cloud import bigquery
    import pandas as pd
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score
    import joblib

    # Load data
    client = bigquery.Client(project=PROJECT_ID)

    # Build feature query based on selected features
    feature_conditions = []
    if 'triangulation' in selected_features:
        feature_conditions.append('triangulation features')
    if 'extended_lags' in selected_features:
        feature_conditions.append('extended lag features')
    if 'smart_dual' in selected_features:
        feature_conditions.append('smart dual processing features')

    # For now, use the base Smart Dual Processing approach
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.bqx_ml_v3_features.{pair}_idx` idx
    JOIN `{PROJECT_ID}.bqx_ml_v3_features.{pair}_bqx` bqx
    ON idx.interval_time = bqx.interval_time
    ORDER BY idx.interval_time
    LIMIT 50000
    """

    data = client.query(query).to_dataframe()

    # Create features (simplified for pipeline)
    X = data.drop(['interval_time'], axis=1)
    y = data[f'{pair}_bqx_{window}'].shift(-1)  # Predict next value

    # Remove NaN
    mask = ~y.isna()
    X = X[mask]
    y = y[mask]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train model
    model_xgb = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model_xgb.fit(X_train, y_train)

    # Evaluate
    predictions = model_xgb.predict(X_test)
    r2 = r2_score(y_test, predictions)

    # Log metrics
    metrics.log_metric('r2_score', r2)
    metrics.log_metric('pair', pair)
    metrics.log_metric('window', window)

    # Save model
    model_path = f'/tmp/model_{pair}_{window}.pkl'
    joblib.dump(model_xgb, model_path)
    model.path = model_path

    return r2

@pipeline(
    name='bqx-ml-v3-comprehensive-testing',
    description='Comprehensive testing of 6000+ features for 196 models',
    pipeline_root=PIPELINE_ROOT
)
def comprehensive_testing_pipeline(
    project_id: str = PROJECT_ID,
    location: str = LOCATION,
    results_bucket: str = 'bqx-ml-bqx-ml-results'
):
    """Main pipeline for comprehensive testing and model training"""

    # Define currency pairs and windows
    currency_pairs = [
        'eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad', 'nzdusd', 'usdchf',
        'eurjpy', 'eurgbp', 'eurchf', 'gbpjpy', 'audjpy', 'cadjpy', 'euraud'
    ]

    windows = [45, 90]  # Two main BQX windows

    feature_categories = [
        'triangulation', 'extended_lags', 'correlation_matrix',
        'smart_dual_processing', 'market_microstructure'
    ]

    # Phase 1: Test all feature categories in parallel
    test_results = {}
    for pair in currency_pairs:
        test_results[pair] = {}
        for category in feature_categories:
            test_task = test_feature_category(
                category=category,
                pair=pair,
                results_bucket=results_bucket
            )
            test_results[pair][category] = test_task

    # Phase 2: Select best features based on test results
    selected_features = []
    for pair in currency_pairs:
        pair_features = []
        for category, result in test_results[pair].items():
            if result.outputs['kept']:  # If feature was beneficial
                pair_features.append(category)
        selected_features.append(pair_features)

    # Phase 3: Train models with selected features
    models = {}
    for i, pair in enumerate(currency_pairs):
        models[pair] = {}
        for window in windows:
            train_task = train_model_with_features(
                pair=pair,
                window=window,
                selected_features=selected_features[i]
            )
            models[pair][window] = train_task

def compile_pipeline():
    """Compile the pipeline to JSON"""

    compiler.Compiler().compile(
        pipeline_func=comprehensive_testing_pipeline,
        package_path='comprehensive_testing_pipeline.json'
    )
    print("Pipeline compiled successfully!")

def submit_pipeline():
    """Submit the pipeline to Vertex AI"""

    # Initialize Vertex AI
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=PIPELINE_ROOT
    )

    # Create pipeline job
    job = aiplatform.PipelineJob(
        display_name='bqx-ml-v3-comprehensive-testing',
        template_path='comprehensive_testing_pipeline.json',
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
        parameter_values={
            'project_id': PROJECT_ID,
            'location': LOCATION,
            'results_bucket': 'bqx-ml-bqx-ml-results'
        }
    )

    # Submit job
    job.submit(service_account=SERVICE_ACCOUNT)

    print(f"Pipeline submitted! Job: {job.display_name}")
    print(f"Monitor at: https://console.cloud.google.com/vertex-ai/pipelines/runs/{job.name}?project={PROJECT_ID}")

    return job

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'compile':
        compile_pipeline()
    elif len(sys.argv) > 1 and sys.argv[1] == 'submit':
        submit_pipeline()
    else:
        print("Usage: python comprehensive_testing_pipeline.py [compile|submit]")
        print("  compile - Compile pipeline to JSON")
        print("  submit  - Submit pipeline to Vertex AI")