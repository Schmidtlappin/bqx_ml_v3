#!/bin/bash
# Enable Required APIs for BQX ML V3
# Note: Requires appropriate permissions (Owner or Editor role)

PROJECT_ID="bqx-ml"

echo "Enabling required APIs for BQX ML V3 project: $PROJECT_ID"
echo "Note: This script requires Owner or Editor permissions."
echo ""

# Core APIs required for BQX ML V3
APIS=(
    "bigquery.googleapis.com"           # BigQuery for data storage and processing
    "aiplatform.googleapis.com"         # Vertex AI for ML training/deployment
    "storage.googleapis.com"             # Cloud Storage for model artifacts
    "compute.googleapis.com"             # Compute Engine for Vertex AI
    "iam.googleapis.com"                 # IAM for service accounts
    "cloudresourcemanager.googleapis.com" # Resource Manager
    "logging.googleapis.com"             # Cloud Logging
    "monitoring.googleapis.com"          # Cloud Monitoring
)

# APIs that are NOT required (explicitly excluded)
# - dataproc.googleapis.com (Not used in BQX ML V3)
# - dataflow.googleapis.com (Not used in BQX ML V3)

for API in "${APIS[@]}"; do
    echo "Enabling $API..."
    gcloud services enable $API --project=$PROJECT_ID
    if [ $? -eq 0 ]; then
        echo "✓ $API enabled successfully"
    else
        echo "✗ Failed to enable $API (may require manual enablement)"
    fi
    echo ""
done

echo "Checking enabled APIs..."
gcloud services list --enabled --project=$PROJECT_ID --format="table(config.name,config.title)"