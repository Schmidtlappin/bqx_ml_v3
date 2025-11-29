#!/bin/bash
#
# Setup Cloud Scheduler for periodic BQ-to-Box sync
#
# Usage: ./setup-scheduler.sh
#

set -e

PROJECT_ID="bqx-ml"
REGION="us-central1"
SERVICE_NAME="bq-to-box-sync"

echo "=== Setting up Cloud Scheduler for BQ-to-Box Sync ==="

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format="value(status.url)")

if [ -z "$SERVICE_URL" ]; then
    echo "ERROR: Could not get Cloud Run service URL. Deploy the service first."
    exit 1
fi

echo "Service URL: ${SERVICE_URL}"

# Create service account for scheduler
SA_NAME="scheduler-bq-box@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe ${SA_NAME} --project=${PROJECT_ID} &>/dev/null; then
    echo "Creating scheduler service account..."
    gcloud iam service-accounts create scheduler-bq-box \
        --display-name="BQ-to-Box Scheduler" \
        --project=${PROJECT_ID}

    # Grant Cloud Run invoker
    gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
        --region=${REGION} \
        --member="serviceAccount:${SA_NAME}" \
        --role="roles/run.invoker" \
        --project=${PROJECT_ID}
fi

# Create scheduled jobs for each dataset
# Different schedules based on priority

echo ""
echo "Creating scheduled jobs..."

# CRITICAL: Models - Daily at 2 AM
gcloud scheduler jobs create http sync-bq-models \
    --location=${REGION} \
    --schedule="0 2 * * *" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_models" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID} \
    --time-zone="UTC" \
    --description="Daily sync of ML models to Box.com" \
    2>/dev/null || gcloud scheduler jobs update http sync-bq-models \
    --location=${REGION} \
    --schedule="0 2 * * *" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_models" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID}

# HIGH: Features - Weekly on Sunday at 3 AM
gcloud scheduler jobs create http sync-bq-features \
    --location=${REGION} \
    --schedule="0 3 * * 0" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_features" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID} \
    --time-zone="UTC" \
    --description="Weekly sync of feature tables to Box.com" \
    2>/dev/null || gcloud scheduler jobs update http sync-bq-features \
    --location=${REGION} \
    --schedule="0 3 * * 0" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_features" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID}

# MEDIUM: Predictions - Weekly on Monday at 4 AM
gcloud scheduler jobs create http sync-bq-predictions \
    --location=${REGION} \
    --schedule="0 4 * * 1" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_predictions" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID} \
    --time-zone="UTC" \
    --description="Weekly sync of predictions to Box.com" \
    2>/dev/null || gcloud scheduler jobs update http sync-bq-predictions \
    --location=${REGION} \
    --schedule="0 4 * * 1" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_predictions" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID}

# LOW: Analytics - Monthly on 1st at 5 AM
gcloud scheduler jobs create http sync-bq-analytics \
    --location=${REGION} \
    --schedule="0 5 1 * *" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_analytics" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID} \
    --time-zone="UTC" \
    --description="Monthly sync of analytics to Box.com" \
    2>/dev/null || gcloud scheduler jobs update http sync-bq-analytics \
    --location=${REGION} \
    --schedule="0 5 1 * *" \
    --uri="${SERVICE_URL}/sync/bqx_ml_v3_analytics" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID}

# HIGH: Raw OHLCV - Quarterly on 1st of Jan, Apr, Jul, Oct at 1 AM
gcloud scheduler jobs create http sync-bq-ohlcv \
    --location=${REGION} \
    --schedule="0 1 1 1,4,7,10 *" \
    --uri="${SERVICE_URL}/sync/bqx_bq_uscen1" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID} \
    --time-zone="UTC" \
    --description="Quarterly sync of raw OHLCV data to Box.com" \
    2>/dev/null || gcloud scheduler jobs update http sync-bq-ohlcv \
    --location=${REGION} \
    --schedule="0 1 1 1,4,7,10 *" \
    --uri="${SERVICE_URL}/sync/bqx_bq_uscen1" \
    --http-method=POST \
    --oidc-service-account-email=${SA_NAME} \
    --project=${PROJECT_ID}

echo ""
echo "=== Scheduler Setup Complete ==="
echo ""
echo "Scheduled jobs:"
gcloud scheduler jobs list --location=${REGION} --project=${PROJECT_ID}
echo ""
echo "To trigger a job manually:"
echo "  gcloud scheduler jobs run sync-bq-models --location=${REGION}"
