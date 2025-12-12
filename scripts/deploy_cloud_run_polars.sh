#!/bin/bash
# Deploy Updated Cloud Run with Polars Integration
# Replaces BA's original BigQuery-based deployment

set -e

PROJECT_ID="bqx-ml"
REGION="us-central1"
SERVICE_ACCOUNT="bqx-ml-pipeline@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE="gcr.io/${PROJECT_ID}/bqx-ml-polars-pipeline:latest"

echo "========================================="
echo "Cloud Run Polars Pipeline Deployment"
echo "========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE}"
echo "Service Account: ${SERVICE_ACCOUNT}"
echo "========================================="
echo ""

# Step 1: Build container image
echo "=== Step 1: Building Container Image ==="
echo "Using Cloud Build to build and push image..."
echo ""

gcloud builds submit \
    --config cloudbuild-polars.yaml \
    --project ${PROJECT_ID} || {
    echo "❌ Build failed"
    exit 1
}

echo ""
echo "✅ Container image built and pushed"
echo ""

# Step 2: Delete old job (if exists)
echo "=== Step 2: Removing Old Deployment ==="
echo ""

gcloud run jobs delete bqx-ml-pipeline \
    --region ${REGION} \
    --quiet \
    2>/dev/null && echo "✅ Old job deleted" || echo "ℹ️  No existing job to delete"

echo ""

# Step 3: Deploy new job with Polars
echo "=== Step 3: Deploying New Polars Pipeline ==="
echo ""

gcloud run jobs create bqx-ml-pipeline \
    --image ${IMAGE} \
    --region ${REGION} \
    --service-account ${SERVICE_ACCOUNT} \
    --memory 12Gi \
    --cpu 4 \
    --task-timeout 7200 \
    --max-retries 1 \
    --set-env-vars "PROJECT_ID=${PROJECT_ID}" || {
    echo "❌ Deployment failed"
    exit 1
}

echo ""
echo "✅ Cloud Run job deployed successfully"
echo ""

# Step 4: Verify deployment
echo "=== Step 4: Verification ==="
echo ""

gcloud run jobs describe bqx-ml-pipeline \
    --region ${REGION} \
    --format="table(name,spec.template.spec.containers[0].image,spec.template.spec.containers[0].resources.limits)"

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "Job Name: bqx-ml-pipeline"
echo "Image: ${IMAGE}"
echo "Memory: 12 GB"
echo "CPU: 2 cores"
echo "Timeout: 2 hours"
echo ""
echo "Pipeline Stages:"
echo "  1. BigQuery extraction (60-70 min)"
echo "  2. Polars merge (13-20 min)"
echo "  3. Validation (1-2 min)"
echo "  4. GCS backup (2-3 min)"
echo "  5. Cleanup (1 min)"
echo ""
echo "Total time per pair: ~77-96 minutes"
echo "Cost per pair: ~$0.71 (Cloud Run compute)"
echo ""
echo "To execute a single pair:"
echo "  gcloud run jobs execute bqx-ml-pipeline \\"
echo "    --region ${REGION} \\"
echo "    --set-env-vars PAIR=gbpusd"
echo ""
echo "========================================="
