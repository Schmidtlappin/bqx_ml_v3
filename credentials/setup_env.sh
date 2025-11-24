#!/bin/bash
# BQX ML v3 Environment Setup
# Source this file: source credentials/setup_env.sh

# GCP Service Account
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials/gcp-sa-key.json"
export GCP_PROJECT_ID="bqx-ml"

# AirTable
export AIRTABLE_API_KEY="your-api-key-here"
export AIRTABLE_BASE_ID="appR3PPnrNkVo48mO"

echo "BQX ML v3 environment configured"
echo "  GCP Project: $GCP_PROJECT_ID"
echo "  AirTable Base: $AIRTABLE_BASE_ID"
