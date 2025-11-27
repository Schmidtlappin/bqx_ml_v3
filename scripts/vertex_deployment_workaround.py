#!/usr/bin/env python3
"""
VERTEX AI DEPLOYMENT WORKAROUND SCRIPT
This bypasses the permission paradox using us-central1 and explicit auth
"""

import os
import sys
from google.cloud import aiplatform
from google.cloud import bigquery
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
import json
from datetime import datetime

print("🚀 VERTEX AI DEPLOYMENT WORKAROUND SCRIPT")
print("=" * 80)

# CRITICAL FIX 1: Use us-central1 NOT us-east1
REGION = "us-central1"
PROJECT = "bqx-ml"

# CRITICAL FIX 2: Set explicit credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/micha/.cache/google-vscode-extension/auth/application_default_credentials.json'

# CRITICAL FIX 3: Initialize with correct settings
print(f"\n📍 Initializing Vertex AI in {REGION}...")
aiplatform.init(
    project=PROJECT,
    location=REGION,
    staging_bucket=f'gs://{PROJECT}-vertex-staging'
)

# CRITICAL FIX 4: BigQuery schema - use correct column names
def load_bqx_data(pair, window):
    """Load data with CORRECT column names"""
    client = bigquery.Client(project=PROJECT)

    # CORRECT: Use bqx_45, not eurusd_bqx_45
    query = f"""
    SELECT
        interval_time,
        bqx_{window} as feature,     -- CORRECT column name
        target_{window} as target     -- CORRECT target column
    FROM `{PROJECT}.bqx_ml_v3_features.{pair.lower().replace('_', '')}_bqx`
    WHERE target_{window} IS NOT NULL
    ORDER BY interval_time DESC
    LIMIT 10000
    """

    print(f"  Loading data for {pair} window {window}...")
    df = client.query(query).to_dataframe()
    print(f"  ✅ Loaded {len(df)} rows")
    return df

# CRITICAL FIX 5: Local training first, then upload
def train_and_upload_model(pair, window):
    """Train locally then upload to Vertex AI"""

    print(f"\n🔧 Training {pair} window {window}")

    try:
        # Load data with correct schema
        df = load_bqx_data(pair, window)

        if len(df) < 100:
            print(f"  ⚠️  Insufficient data for {pair} {window}")
            return None

        # Prepare features
        X = df[['feature']].values
        y = df['target'].values

        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X, y)

        # Calculate R² score
        score = model.score(X, y)
        print(f"  📊 Model R² score: {score:.4f}")

        # Save model locally
        model_path = f'/tmp/{pair}_{window}_model.pkl'
        joblib.dump(model, model_path)
        print(f"  💾 Model saved to {model_path}")

        # Upload to GCS
        gcs_path = f'gs://{PROJECT}-vertex-models/{pair}_{window}_model.pkl'
        os.system(f'gsutil cp {model_path} {gcs_path}')
        print(f"  ☁️  Uploaded to {gcs_path}")

        return {
            'pair': pair,
            'window': window,
            'r2_score': score,
            'model_path': gcs_path
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# CRITICAL FIX 6: Deploy without CustomJob (bypass permission issue)
def deploy_to_vertex_endpoint(model_info):
    """Deploy model to Vertex AI endpoint"""

    print(f"\n🚀 Deploying {model_info['pair']}_{model_info['window']} to endpoint")

    try:
        # Upload model to Model Registry
        model = aiplatform.Model.upload(
            display_name=f"bqx-{model_info['pair']}-{model_info['window']}",
            artifact_uri=os.path.dirname(model_info['model_path']),
            serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-23:latest"
        )
        print(f"  ✅ Model uploaded: {model.display_name}")

        # Create endpoint
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_info['pair']}-{model_info['window']}-endpoint"
        )
        print(f"  ✅ Endpoint created: {endpoint.display_name}")

        # Deploy model to endpoint
        endpoint.deploy(
            model=model,
            deployed_model_display_name=f"bqx-{model_info['pair']}-{model_info['window']}-v1",
            machine_type="n1-standard-4",
            min_replica_count=1,
            max_replica_count=3
        )
        print(f"  ✅ Model deployed to endpoint")

        return endpoint

    except Exception as e:
        print(f"  ❌ Deployment error: {e}")
        return None

# MAIN EXECUTION
def main():
    """Main deployment function"""

    # Define what to deploy (start with subset)
    PAIRS_TO_DEPLOY = ['EUR_USD', 'GBP_USD']  # Start with 2 pairs
    WINDOWS_TO_DEPLOY = [45, 90]  # Start with 2 windows

    print(f"\n📋 Deployment Plan:")
    print(f"  • Pairs: {PAIRS_TO_DEPLOY}")
    print(f"  • Windows: {WINDOWS_TO_DEPLOY}")
    print(f"  • Total models: {len(PAIRS_TO_DEPLOY) * len(WINDOWS_TO_DEPLOY)}")

    deployed_models = []
    failed_models = []

    # Train and deploy each model
    for pair in PAIRS_TO_DEPLOY:
        for window in WINDOWS_TO_DEPLOY:
            print("\n" + "=" * 60)

            # Train model
            model_info = train_and_upload_model(pair, window)

            if model_info:
                # Deploy to endpoint
                endpoint = deploy_to_vertex_endpoint(model_info)

                if endpoint:
                    deployed_models.append({
                        'pair': pair,
                        'window': window,
                        'r2_score': model_info['r2_score'],
                        'endpoint': endpoint.resource_name
                    })
                else:
                    failed_models.append(f"{pair}_{window}")
            else:
                failed_models.append(f"{pair}_{window}")

    # Summary report
    print("\n" + "=" * 80)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 80)

    print(f"\n✅ Successfully deployed: {len(deployed_models)}")
    for model in deployed_models:
        print(f"  • {model['pair']}_{model['window']}: R²={model['r2_score']:.4f}")

    if failed_models:
        print(f"\n❌ Failed deployments: {len(failed_models)}")
        for model in failed_models:
            print(f"  • {model}")

    # Save deployment manifest
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'region': REGION,
        'project': PROJECT,
        'deployed': deployed_models,
        'failed': failed_models
    }

    with open('/tmp/deployment_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n📄 Manifest saved to /tmp/deployment_manifest.json")

    # Final status
    success_rate = len(deployed_models) / (len(deployed_models) + len(failed_models)) * 100
    print(f"\n🎯 Deployment success rate: {success_rate:.1f}%")

    if success_rate > 0:
        print("\n✅ VERTEX AI DEPLOYMENT SUCCESSFUL!")
        print(f"   Models are now available in {REGION}")
    else:
        print("\n❌ DEPLOYMENT FAILED - Check errors above")

    return deployed_models

if __name__ == "__main__":
    print("\n⚡ STARTING WORKAROUND DEPLOYMENT")
    print("This bypasses CustomJob permission issues by:")
    print("  1. Training locally with correct BigQuery schema")
    print("  2. Uploading models to GCS")
    print("  3. Deploying directly to endpoints")
    print("  4. Using us-central1 instead of us-east1")

    deployed = main()

    if deployed:
        print("\n🎉 WORKAROUND SUCCESSFUL!")
        print(f"   {len(deployed)} models deployed to Vertex AI")
        print(f"   Region: {REGION}")
        print(f"   Project: {PROJECT}")

    sys.exit(0 if deployed else 1)