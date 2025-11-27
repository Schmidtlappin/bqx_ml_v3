#!/usr/bin/env python3
"""
VERTEX AI DEPLOYMENT - FIXED DIRECTORY STRUCTURE
Corrects the model directory issue for successful deployment
"""

import os
import sys
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
import json
from datetime import datetime

print("🚀 VERTEX AI DEPLOYMENT - FIXED VERSION")
print("=" * 80)

# Configuration
REGION = "us-central1"
PROJECT = "bqx-ml"
BUCKET_NAME = f"{PROJECT}-vertex-models"

# Set explicit credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/micha/.cache/google-vscode-extension/auth/application_default_credentials.json'

# Initialize services
print(f"\n📍 Initializing services...")
aiplatform.init(
    project=PROJECT,
    location=REGION,
    staging_bucket=f'gs://{PROJECT}-vertex-staging'
)

# Initialize storage client
storage_client = storage.Client(project=PROJECT)
bucket = storage_client.bucket(BUCKET_NAME)

def load_bqx_data(pair, window):
    """Load data with correct column names"""
    client = bigquery.Client(project=PROJECT)

    # Correct column names: bqx_45, not eurusd_bqx_45
    query = f"""
    SELECT
        interval_time,
        bqx_{window} as feature,
        target_{window} as target
    FROM `{PROJECT}.bqx_ml_v3_features.{pair.lower().replace('_', '')}_bqx`
    WHERE target_{window} IS NOT NULL
    ORDER BY interval_time DESC
    LIMIT 10000
    """

    print(f"  Loading data for {pair} window {window}...")
    df = client.query(query).to_dataframe()
    print(f"  ✅ Loaded {len(df)} rows")
    return df

def train_and_upload_model(pair, window):
    """Train model and upload with CORRECT directory structure"""

    print(f"\n🔧 Training {pair} window {window}")

    try:
        # Load data
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
        local_path = f'/tmp/model.pkl'
        joblib.dump(model, local_path)
        print(f"  💾 Model saved locally")

        # CRITICAL FIX: Upload to subdirectory as 'model.pkl'
        model_dir = f"{pair}_{window}"
        blob_path = f"{model_dir}/model.pkl"

        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_path)

        gcs_uri = f"gs://{BUCKET_NAME}/{model_dir}/"
        print(f"  ☁️  Uploaded to {gcs_uri}")

        return {
            'pair': pair,
            'window': window,
            'r2_score': score,
            'model_uri': gcs_uri,
            'model_name': f"{pair}_{window}"
        }

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def deploy_to_vertex_endpoint(model_info):
    """Deploy model to Vertex AI endpoint"""

    print(f"\n🚀 Deploying {model_info['model_name']} to endpoint")

    try:
        # Upload model to Model Registry with correct URI
        model = aiplatform.Model.upload(
            display_name=f"bqx-{model_info['model_name']}",
            artifact_uri=model_info['model_uri'],  # Points to directory containing model.pkl
            serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-23:latest"
        )
        print(f"  ✅ Model uploaded: {model.display_name}")

        # Create endpoint
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_info['model_name']}-endpoint"
        )
        print(f"  ✅ Endpoint created: {endpoint.display_name}")

        # Deploy model to endpoint
        deployment = endpoint.deploy(
            model=model,
            deployed_model_display_name=f"bqx-{model_info['model_name']}-v1",
            machine_type="n1-standard-4",
            min_replica_count=1,
            max_replica_count=3
        )
        print(f"  ✅ Model deployed to endpoint")

        # Test prediction
        test_input = [[0.5]]  # Sample input
        prediction = endpoint.predict(test_input)
        print(f"  ✅ Test prediction successful: {prediction}")

        return endpoint

    except Exception as e:
        print(f"  ❌ Deployment error: {e}")
        return None

def main():
    """Main deployment function"""

    # Start with a subset for testing
    PAIRS_TO_DEPLOY = ['EUR_USD', 'GBP_USD']
    WINDOWS_TO_DEPLOY = [45, 90]

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

            # Train model with fixed directory structure
            model_info = train_and_upload_model(pair, window)

            if model_info:
                # Deploy to endpoint
                endpoint = deploy_to_vertex_endpoint(model_info)

                if endpoint:
                    deployed_models.append({
                        'pair': pair,
                        'window': window,
                        'r2_score': model_info['r2_score'],
                        'endpoint': endpoint.resource_name,
                        'endpoint_id': endpoint.name
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
        print(f"    Endpoint: {model['endpoint_id']}")

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
    if deployed_models:
        success_rate = len(deployed_models) / (len(deployed_models) + len(failed_models)) * 100
        print(f"\n🎯 Deployment success rate: {success_rate:.1f}%")

        print("\n✅ VERTEX AI DEPLOYMENT SUCCESSFUL!")
        print(f"   {len(deployed_models)} models deployed to {REGION}")
        print("\n📈 Next steps:")
        print("   1. Scale to all 28 currency pairs")
        print("   2. Add all 7 time windows")
        print("   3. Deploy remaining 192 models")
    else:
        print("\n❌ DEPLOYMENT FAILED - Check errors above")

    return deployed_models

if __name__ == "__main__":
    print("\n⚡ STARTING FIXED DEPLOYMENT")
    print("Key fixes applied:")
    print("  1. Models stored in subdirectories as 'model.pkl'")
    print("  2. Correct artifact_uri pointing to directory")
    print("  3. Test predictions after deployment")
    print("  4. Using us-central1 region")

    deployed = main()

    if deployed:
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print(f"   {len(deployed)} models now serving predictions")
        print(f"   Access via Vertex AI console in {REGION}")

    sys.exit(0 if deployed else 1)