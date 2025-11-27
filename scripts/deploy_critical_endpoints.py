#!/usr/bin/env python3
"""
Deploy only the 5 critical endpoints for the Smart Vertex AI Architecture.
This implements Phase 1 of the $442/month solution instead of $13,420/month.

Critical models (90-min windows only):
- EUR_USD_90: Highest volume
- GBP_USD_90: Second highest
- USD_JPY_90: Asian markets
- EUR_GBP_90: Cross-pair leader
- EUR_JPY_90: European cross

Total cost: $342/month (5 × $68.40)
"""

from google.cloud import aiplatform
import time
import os
from datetime import datetime

# Configuration
PROJECT = "bqx-ml"
REGION = "us-central1"
BUCKET_NAME = "bqx-ml-vertex-models"

# ONLY THESE 5 ENDPOINTS (90-minute windows only)
CRITICAL_MODELS = [
    "EUR_USD_90",  # Highest volume
    "GBP_USD_90",  # Second highest
    "USD_JPY_90",  # Asian markets
    "EUR_GBP_90",  # Cross-pair leader
    "EUR_JPY_90"   # European cross
]

def deploy_critical_endpoint(model_name):
    """Deploy a single critical endpoint with optimal settings for cost efficiency"""

    print(f"\n{'='*60}")
    print(f"📦 Deploying {model_name} (Critical Endpoint)")
    print(f"{'='*60}")

    try:
        # Initialize Vertex AI
        aiplatform.init(project=PROJECT, location=REGION)

        # Get model from GCS
        model_path = f"gs://{BUCKET_NAME}/{model_name}/"

        print(f"  1️⃣ Uploading model from {model_path}...")

        # Upload model to Vertex AI registry
        model = aiplatform.Model.upload(
            display_name=f"bqx-{model_name}",
            artifact_uri=model_path,
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"
        )

        print(f"     ✅ Model uploaded: {model.resource_name}")

        # Create endpoint
        print(f"  2️⃣ Creating endpoint...")
        endpoint = aiplatform.Endpoint.create(
            display_name=f"bqx-{model_name}-endpoint"
        )

        print(f"     ✅ Endpoint created: {endpoint.resource_name}")

        # Deploy with MINIMAL resources (critical for cost!)
        print(f"  3️⃣ Deploying model to endpoint (minimal resources)...")

        # IMPORTANT: Use n1-standard-2, NOT n1-standard-4
        # This saves $34.20 per endpoint per month!
        deployed_model = endpoint.deploy(
            model=model,
            deployed_model_display_name=f"bqx-{model_name}-deployed",
            machine_type="n1-standard-2",  # Smaller instance for cost savings
            min_replica_count=1,            # Minimum replicas
            max_replica_count=2,            # Allow scaling to 2 if needed
            traffic_percentage=100
        )

        print(f"     ✅ Model deployed successfully!")
        print(f"     💰 Monthly cost: $68.40")
        print(f"     🔗 Endpoint URL: {endpoint.resource_name}")

        # Test prediction
        print(f"  4️⃣ Testing prediction...")
        test_instance = [[0.5]]  # Simple test value

        try:
            prediction = endpoint.predict(instances=test_instance)
            print(f"     ✅ Test prediction successful: {prediction.predictions[0]}")
        except Exception as e:
            print(f"     ⚠️ Test prediction failed (model may need warmup): {e}")

        return {
            "model_name": model_name,
            "model_id": model.resource_name,
            "endpoint_id": endpoint.resource_name,
            "status": "deployed",
            "monthly_cost": 68.40,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"     ❌ Error deploying {model_name}: {e}")
        return {
            "model_name": model_name,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def main():
    """Deploy all 5 critical endpoints"""

    print("="*70)
    print("🚀 SMART VERTEX AI - PHASE 1: CRITICAL ENDPOINTS")
    print("="*70)
    print(f"Target: Deploy 5 critical endpoints for $342/month")
    print(f"Savings: $12,978/month (97% reduction)")
    print("="*70)

    # Track deployment results
    results = []
    successful = 0
    failed = 0
    total_cost = 0

    # Deploy each critical endpoint
    for i, model_name in enumerate(CRITICAL_MODELS, 1):
        print(f"\n[{i}/5] Processing {model_name}...")

        result = deploy_critical_endpoint(model_name)
        results.append(result)

        if result["status"] == "deployed":
            successful += 1
            total_cost += result["monthly_cost"]
        else:
            failed += 1

        # Wait between deployments to avoid rate limiting
        if i < len(CRITICAL_MODELS):
            print(f"\n⏳ Waiting 60 seconds before next deployment...")
            time.sleep(60)

    # Summary report
    print("\n" + "="*70)
    print("📊 PHASE 1 DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"✅ Successful deployments: {successful}/5")
    if failed > 0:
        print(f"❌ Failed deployments: {failed}/5")
    print(f"💰 Total monthly cost: ${total_cost:.2f}")
    print(f"💸 Monthly savings vs naive approach: ${13420 - total_cost:.2f}")
    print(f"📈 Cost reduction: {((13420 - total_cost) / 13420 * 100):.1f}%")
    print("="*70)

    # Save results
    import json
    results_file = "/home/micha/bqx_ml_v3/deployment_results/critical_endpoints.json"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump({
            "phase": "critical_endpoints",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "successful": successful,
                "failed": failed,
                "total_cost": total_cost,
                "savings": 13420 - total_cost
            },
            "deployments": results
        }, f, indent=2)

    print(f"\n📁 Results saved to: {results_file}")

    if successful == 5:
        print("\n✅ PHASE 1 COMPLETE! Ready for Phase 2 (Batch Predictions)")
    else:
        print(f"\n⚠️ PHASE 1 INCOMPLETE: Only {successful}/5 endpoints deployed")
        print("   Please review errors and retry failed deployments")

    return results

if __name__ == "__main__":
    main()