#!/usr/bin/env python3
"""
Deploy Models to Vertex AI Endpoints
Bringing health score from 90/100 to 93/100
"""

import os
from google.cloud import aiplatform
from datetime import datetime
import json
import time

# Set credentials
credentials_path = '/home/micha/.cache/google-vscode-extension/auth/application_default_credentials.json'
if os.path.exists(credentials_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

print("="*70)
print("🚀 DEPLOYING MODELS TO VERTEX AI ENDPOINTS")
print("Target: Health Score 90 → 93/100")
print("="*70)

# Initialize Vertex AI
print("\n📍 Initializing Vertex AI in us-central1...")
aiplatform.init(
    project='bqx-ml',
    location='us-central1',
    staging_bucket='gs://bqx-ml-bqx-ml-artifacts/'
)

# Models to deploy
models_to_deploy = [
    {'name': 'EUR_USD_45', 'r2': 0.1161},
    {'name': 'EUR_USD_90', 'r2': 0.3768},
    {'name': 'GBP_USD_45', 'r2': 0.1241},
    {'name': 'GBP_USD_90', 'r2': 0.3666}
]

successful_deployments = []
failed_deployments = []

for model_info in models_to_deploy:
    model_name = model_info['name']
    print(f"\n{'='*60}")
    print(f"📦 Deploying {model_name} (R²={model_info['r2']:.4f})")
    print(f"{'='*60}")

    try:
        # Step 1: Upload model to Model Registry
        print(f"  1️⃣ Uploading model to registry...")
        model = aiplatform.Model.upload(
            display_name=f"bqx-{model_name}",
            artifact_uri=f"gs://bqx-ml-vertex-models/{model_name}/",
            serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest",
            description=f"BQX ML V3 Model - {model_name} (R²={model_info['r2']:.4f})"
        )
        print(f"     ✅ Model uploaded: {model.resource_name}")

        # Step 2: Create endpoint
        print(f"  2️⃣ Creating endpoint...")
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_name}-endpoint",
            description=f"Endpoint for {model_name} predictions"
        )
        print(f"     ✅ Endpoint created: {endpoint.resource_name}")

        # Step 3: Deploy model to endpoint
        print(f"  3️⃣ Deploying model to endpoint...")
        deployed_model = endpoint.deploy(
            model=model,
            deployed_model_display_name=f"{model_name}-deployment",
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=2,
            accelerator_type=None,
            accelerator_count=0,
            traffic_percentage=100
        )
        print(f"     ✅ Model deployed successfully!")

        successful_deployments.append({
            'model': model_name,
            'r2': model_info['r2'],
            'model_id': model.resource_name,
            'endpoint_id': endpoint.resource_name,
            'timestamp': datetime.now().isoformat()
        })

        print(f"  ✅ SUCCESS: {model_name} fully deployed and serving!")

    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        failed_deployments.append({
            'model': model_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

    # Small delay between deployments
    time.sleep(2)

# Save deployment results
results = {
    'deployment_timestamp': datetime.now().isoformat(),
    'total_attempted': len(models_to_deploy),
    'successful': len(successful_deployments),
    'failed': len(failed_deployments),
    'health_score_before': 90,
    'health_score_after': 90 + (3 if len(successful_deployments) == 4 else 0),
    'successful_deployments': successful_deployments,
    'failed_deployments': failed_deployments
}

output_file = f'/home/micha/bqx_ml_v3/endpoint_deployment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*70)
print("📊 DEPLOYMENT SUMMARY")
print("="*70)
print(f"✅ Successfully deployed: {len(successful_deployments)}/4")
print(f"❌ Failed: {len(failed_deployments)}/4")

if len(successful_deployments) > 0:
    print("\n✅ Deployed Models:")
    for dep in successful_deployments:
        print(f"  • {dep['model']} (R²={dep['r2']:.4f})")

if len(failed_deployments) > 0:
    print("\n❌ Failed Models:")
    for dep in failed_deployments:
        print(f"  • {dep['model']}: {dep['error'][:50]}...")

print(f"\n📁 Results saved to: {output_file}")

# Calculate new health score
if len(successful_deployments) == 4:
    print("\n🎯 HEALTH SCORE UPDATE:")
    print("  Previous: 90/100")
    print("  Current:  93/100 ✅ (+3 points)")
    print("\n🚀 Next step: Scale to 196 models for 96/100!")
else:
    print(f"\n⚠️ Partial success: {len(successful_deployments)}/4 models deployed")
    print("  Health score remains at 90/100")

print("="*70)