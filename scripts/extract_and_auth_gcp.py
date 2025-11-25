#!/usr/bin/env python3
"""
Extract GCP service account key from github_secrets.json and authenticate
"""

import json
import os
import subprocess

# Load the secrets file
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    data = json.load(f)

# Extract the GCP service account key
gcp_key = data['secrets']['GCP_SERVICE_ACCOUNT_KEY']['value']

# Create credentials directory if it doesn't exist
os.makedirs('/home/micha/bqx_ml_v3/credentials', exist_ok=True)

# Write the service account key to a file
key_path = '/home/micha/bqx_ml_v3/credentials/gcp-sa-key.json'
with open(key_path, 'w') as f:
    json.dump(gcp_key, f, indent=2)

print("✅ GCP service account key saved to:", key_path)

# Set the environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

# Authenticate with gcloud
project_id = data['secrets']['GCP_PROJECT_ID']['value']
print(f"\n🔐 Authenticating gcloud with project: {project_id}")

try:
    # Activate the service account
    result = subprocess.run(
        ['gcloud', 'auth', 'activate-service-account', '--key-file', key_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Service account activated successfully")

        # Set the project
        subprocess.run(['gcloud', 'config', 'set', 'project', project_id])
        print(f"✅ Project set to: {project_id}")

        # Verify authentication
        result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
        print("\nActive accounts:")
        print(result.stdout)
    else:
        print(f"❌ Failed to activate service account: {result.stderr}")

except Exception as e:
    print(f"❌ Error during authentication: {e}")

print("\n📊 Next steps:")
print("1. GitHub secrets can now be deployed using GitHub CLI")
print("2. Credentials have been extracted and are ready for use")
print("3. The workspace can be sanitized for git commits")