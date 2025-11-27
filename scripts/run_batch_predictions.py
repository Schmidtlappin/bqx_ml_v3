#!/usr/bin/env python3
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
