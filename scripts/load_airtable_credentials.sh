#!/bin/bash
# Permanent solution for loading AirTable credentials from GCP Secrets Manager

echo "Loading AirTable credentials from GCP Secrets Manager..."

export AIRTABLE_API_KEY=$(gcloud secrets versions access latest --secret="bqx-ml-airtable-token" 2>/dev/null)
export AIRTABLE_BASE_ID=$(gcloud secrets versions access latest --secret="bqx-ml-airtable-base-id" 2>/dev/null)

if [ -z "$AIRTABLE_API_KEY" ] || [ -z "$AIRTABLE_BASE_ID" ]; then
    echo "❌ Failed to load AirTable credentials from GCP Secrets Manager"
    exit 1
fi

echo "✅ AirTable credentials loaded successfully"
echo "   Base ID: $AIRTABLE_BASE_ID"