#!/usr/bin/env python3
"""
Setup batch predictions for the Smart Vertex AI Architecture.
This implements Phase 2 of the $442/month solution.

Batch predictions for 191 models (all except the 5 critical endpoints).
Total cost: $100/month for batch predictions.
"""

import json
import os
from datetime import datetime

# Configuration
PROJECT = "bqx-ml"
BUCKET_NAME = "bqx-ml-vertex-models"

# ALL currency pairs and time windows
CURRENCY_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "EUR_GBP", "EUR_JPY", "USD_CHF",
    "AUD_USD", "NZD_USD", "USD_CAD", "EUR_CHF", "GBP_CHF", "AUD_JPY",
    "CAD_JPY", "CHF_JPY"
]

TIME_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]

# The 5 critical models that have dedicated endpoints
CRITICAL_MODELS = [
    "EUR_USD_90", "GBP_USD_90", "USD_JPY_90", "EUR_GBP_90", "EUR_JPY_90"
]

def generate_batch_model_list():
    """Generate list of all models that need batch prediction (not endpoints)"""
    batch_models = []

    for pair in CURRENCY_PAIRS:
        for window in TIME_WINDOWS:
            model_name = f"{pair}_{window}"

            # Skip the critical models that have endpoints
            if model_name not in CRITICAL_MODELS:
                batch_models.append(model_name)

    return batch_models

def create_batch_job_config(model_name):
    """Create configuration for a batch prediction job"""

    pair, window = model_name.rsplit('_', 1)

    # Construct table names
    # Input: Latest features from BigQuery
    input_table = f"{PROJECT}.bqx_ml_v3_features.{pair.lower().replace('_', '')}_bqx"

    # Output: Predictions stored in BigQuery
    output_table = f"{PROJECT}.predictions.batch_{model_name.lower()}"

    config = {
        "display_name": f"batch-{model_name}",
        "model_name": model_name,
        "model_path": f"gs://{BUCKET_NAME}/{model_name}/",
        "input_config": {
            "instances_format": "bigquery",
            "bigquery_source": {
                "input_uri": f"bq://{input_table}"
            }
        },
        "output_config": {
            "predictions_format": "bigquery",
            "bigquery_destination": {
                "output_uri": f"bq://{output_table}"
            }
        },
        "machine_spec": {
            "machine_type": "n1-standard-2",  # Minimal resources for batch
            "starting_replica_count": 1,
            "max_replica_count": 1
        },
        "schedule": "0 * * * *",  # Hourly refresh
        "estimated_monthly_cost": 0.52  # ~$0.52 per model per month for batch
    }

    return config

def create_cloud_scheduler_config(batch_configs):
    """Create Cloud Scheduler configuration for triggering batch jobs"""

    scheduler_config = {
        "name": "bqx-hourly-batch-predictions",
        "description": "Trigger hourly batch predictions for all non-critical models",
        "schedule": "0 * * * *",  # Every hour at minute 0
        "time_zone": "UTC",
        "pubsub_target": {
            "topic_name": f"projects/{PROJECT}/topics/trigger-batch-predictions",
            "attributes": {
                "action": "run_batch_predictions",
                "model_count": str(len(batch_configs))
            }
        },
        "retry_config": {
            "retry_count": 3,
            "max_retry_duration": "600s",
            "min_backoff_duration": "5s",
            "max_backoff_duration": "60s"
        }
    }

    return scheduler_config

def generate_batch_runner_script():
    """Generate the script that will actually run batch predictions"""

    script = '''#!/usr/bin/env python3
"""
Batch prediction runner - triggered hourly by Cloud Scheduler.
Processes all 191 non-critical models via batch predictions.
"""

from google.cloud import aiplatform
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load batch configurations
with open('/home/micha/bqx_ml_v3/configs/batch_predictions.json', 'r') as f:
    BATCH_CONFIGS = json.load(f)

def run_batch_prediction(config):
    """Run a single batch prediction job"""
    try:
        aiplatform.init(project="bqx-ml", location="us-central1")

        # Create batch prediction job
        job = aiplatform.BatchPredictionJob.create(
            job_display_name=config["display_name"],
            model_name=config["model_path"],
            instances_format=config["input_config"]["instances_format"],
            predictions_format=config["output_config"]["predictions_format"],
            gcs_source=config["input_config"].get("gcs_source"),
            bigquery_source=config["input_config"].get("bigquery_source"),
            gcs_destination_prefix=config["output_config"].get("gcs_destination"),
            bigquery_destination_prefix=config["output_config"].get("bigquery_destination"),
            machine_type=config["machine_spec"]["machine_type"],
            starting_replica_count=config["machine_spec"]["starting_replica_count"],
            max_replica_count=config["machine_spec"]["max_replica_count"]
        )

        logger.info(f"✅ Started batch job for {config['model_name']}: {job.resource_name}")
        return {"model": config["model_name"], "status": "started", "job_id": job.resource_name}

    except Exception as e:
        logger.error(f"❌ Failed to start batch job for {config['model_name']}: {e}")
        return {"model": config["model_name"], "status": "failed", "error": str(e)}

def main():
    """Run all batch predictions in parallel"""
    logger.info(f"Starting batch predictions for {len(BATCH_CONFIGS)} models...")

    results = []

    # Run batch jobs in parallel (max 10 at a time)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(run_batch_prediction, config): config
                   for config in BATCH_CONFIGS.values()}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Summary
    successful = [r for r in results if r["status"] == "started"]
    failed = [r for r in results if r["status"] == "failed"]

    logger.info(f"Batch predictions complete: {len(successful)} started, {len(failed)} failed")

    return results

if __name__ == "__main__":
    main()
'''

    return script

def main():
    """Setup all batch prediction configurations"""

    print("="*70)
    print("🚀 SMART VERTEX AI - PHASE 2: BATCH PREDICTIONS SETUP")
    print("="*70)
    print("Setting up batch predictions for 191 models")
    print("Estimated cost: $100/month (vs $13,078/month for endpoints)")
    print("="*70)

    # Generate list of batch models
    batch_models = generate_batch_model_list()
    print(f"\n📊 Models for batch prediction: {len(batch_models)}")
    print(f"   (Excluding 5 critical endpoints: {', '.join(CRITICAL_MODELS)})")

    # Create configurations for each model
    print("\n📝 Generating batch job configurations...")
    batch_configs = {}
    total_cost = 0

    for model_name in batch_models:
        config = create_batch_job_config(model_name)
        batch_configs[model_name] = config
        total_cost += config["estimated_monthly_cost"]

    print(f"   ✅ Generated {len(batch_configs)} configurations")
    print(f"   💰 Total estimated cost: ${total_cost:.2f}/month")

    # Save configurations
    config_dir = "/home/micha/bqx_ml_v3/configs"
    os.makedirs(config_dir, exist_ok=True)

    config_file = f"{config_dir}/batch_predictions.json"
    with open(config_file, 'w') as f:
        json.dump(batch_configs, f, indent=2)

    print(f"\n📁 Saved configurations to: {config_file}")

    # Create Cloud Scheduler configuration
    print("\n⏰ Creating Cloud Scheduler configuration...")
    scheduler_config = create_cloud_scheduler_config(batch_configs)

    scheduler_file = f"{config_dir}/scheduler_config.json"
    with open(scheduler_file, 'w') as f:
        json.dump(scheduler_config, f, indent=2)

    print(f"   ✅ Saved scheduler config to: {scheduler_file}")

    # Generate batch runner script
    print("\n🔧 Generating batch runner script...")
    runner_script = generate_batch_runner_script()

    runner_file = "/home/micha/bqx_ml_v3/scripts/run_batch_predictions.py"
    with open(runner_file, 'w') as f:
        f.write(runner_script)

    os.chmod(runner_file, 0o755)
    print(f"   ✅ Created runner script: {runner_file}")

    # Summary
    print("\n" + "="*70)
    print("📊 BATCH PREDICTION SETUP SUMMARY")
    print("="*70)
    print(f"✅ Batch models configured: {len(batch_configs)}")
    print(f"💰 Monthly cost: ${total_cost:.2f}")
    print(f"💸 Savings vs endpoints: ${len(batch_configs) * 68.40 - total_cost:.2f}/month")
    print(f"📈 Cost reduction: {((len(batch_configs) * 68.40 - total_cost) / (len(batch_configs) * 68.40) * 100):.1f}%")
    print("="*70)

    # Next steps
    print("\n📋 NEXT STEPS:")
    print("1. Deploy Cloud Scheduler job:")
    print("   gcloud scheduler jobs create pubsub bqx-hourly-batch \\")
    print(f"     --schedule='0 * * * *' \\")
    print(f"     --topic=trigger-batch-predictions \\")
    print(f"     --message-body='{{\"action\":\"run_batch\"}}' \\")
    print(f"     --time-zone=UTC")
    print("\n2. Create Pub/Sub topic:")
    print(f"   gcloud pubsub topics create trigger-batch-predictions")
    print("\n3. Deploy Cloud Function to handle batch triggers")
    print("   (See Phase 3)")

    print("\n✅ PHASE 2 SETUP COMPLETE!")

    return batch_configs

if __name__ == "__main__":
    main()