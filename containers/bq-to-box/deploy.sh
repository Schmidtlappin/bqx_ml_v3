#!/bin/bash
#
# Deploy BQ-to-Box Sync Service to Cloud Run
#
# Usage: ./deploy.sh
#

set -e

PROJECT_ID="bqx-ml"
REGION="us-central1"
SERVICE_NAME="bq-to-box-sync"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=== BQ-to-Box Sync Service Deployment ==="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo ""

# Step 1: Create service account if it doesn't exist
echo "Step 1: Checking service account..."
SA_NAME="${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe ${SA_NAME} --project=${PROJECT_ID} &>/dev/null; then
    echo "Creating service account..."
    gcloud iam service-accounts create ${SERVICE_NAME} \
        --display-name="BQ-to-Box Sync Service" \
        --project=${PROJECT_ID}

    # Grant BigQuery Data Viewer
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_NAME}" \
        --role="roles/bigquery.dataViewer"

    # Grant BigQuery Job User
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_NAME}" \
        --role="roles/bigquery.jobUser"

    # Grant Storage Admin for GCS exports
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_NAME}" \
        --role="roles/storage.admin"

    # Grant Secret Manager access
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_NAME}" \
        --role="roles/secretmanager.secretAccessor"
else
    echo "Service account exists."
fi

# Step 2: Create GCS bucket for exports if it doesn't exist
echo ""
echo "Step 2: Checking GCS bucket..."
BUCKET_NAME="gs://${PROJECT_ID}-exports"
if ! gsutil ls ${BUCKET_NAME} &>/dev/null; then
    echo "Creating GCS bucket for exports..."
    gsutil mb -l ${REGION} ${BUCKET_NAME}
    gsutil lifecycle set - ${BUCKET_NAME} <<EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 7}
    }
  ]
}
EOF
else
    echo "GCS bucket exists."
fi

# Step 3: Store Box JWT config in Secret Manager
echo ""
echo "Step 3: Checking Box JWT secret..."
SECRET_NAME="box-jwt-config"
if ! gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} &>/dev/null; then
    echo "Creating secret for Box JWT config..."
    gcloud secrets create ${SECRET_NAME} \
        --project=${PROJECT_ID} \
        --replication-policy="automatic"

    echo "Please add the Box JWT config:"
    echo "  gcloud secrets versions add ${SECRET_NAME} --data-file=/path/to/box_jwt_config.json"
    echo ""
    read -p "Press Enter after adding the secret..."
else
    echo "Secret exists."
fi

# Step 4: Build container
echo ""
echo "Step 4: Building container..."
cd "$(dirname "$0")"
docker build -t ${IMAGE_NAME}:latest .

# Step 5: Push to Container Registry
echo ""
echo "Step 5: Pushing to Container Registry..."
docker push ${IMAGE_NAME}:latest

# Step 6: Deploy to Cloud Run
echo ""
echo "Step 6: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME}:latest \
    --region=${REGION} \
    --platform=managed \
    --memory=2Gi \
    --timeout=3600 \
    --no-allow-unauthenticated \
    --service-account=${SA_NAME} \
    --set-env-vars="GCP_PROJECT=${PROJECT_ID},GCS_BUCKET=${BUCKET_NAME}" \
    --project=${PROJECT_ID}

# Step 7: Get service URL
echo ""
echo "Step 7: Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format="value(status.url)")

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "To trigger a sync:"
echo "  curl -X POST ${SERVICE_URL}/sync/bqx_ml_v3_features \\"
echo "    -H 'Authorization: Bearer \$(gcloud auth print-identity-token)'"
echo ""
echo "To setup scheduled sync, run:"
echo "  ./setup-scheduler.sh"
