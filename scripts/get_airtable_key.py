#!/usr/bin/env python3
"""
Helper to retrieve AirTable API key from GCP Secrets Manager
Provides secure access to AirTable credentials
"""

import os
import json
import subprocess

def get_airtable_api_key():
    """
    Retrieve AirTable API key from GCP Secrets Manager

    Returns:
        str: The AirTable API key
    """
    # Get project ID from environment or metadata
    project_id = os.environ.get('GCP_PROJECT', 'bqx-ml-v3')

    # Secret name (adjust if different)
    secret_name = "AIRTABLE_API_KEY"

    try:
        # Use gcloud CLI to access the secret
        cmd = f"gcloud secrets versions access latest --secret={secret_name} --project={project_id}"
        result = subprocess.run(cmd.split(), capture_output=True, text=True, check=True)

        secret_value = result.stdout.strip()

        # Set as environment variable for current session
        os.environ['AIRTABLE_API_KEY'] = secret_value

        print(f"✅ Successfully retrieved AirTable API key from GCP Secrets Manager")
        return secret_value

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Could not retrieve AirTable API key from Secrets Manager: {e}")
        print("Attempting fallback methods...")

        # Fallback: Check environment variable
        if 'AIRTABLE_API_KEY' in os.environ:
            print("✅ Found AirTable API key in environment variable")
            return os.environ['AIRTABLE_API_KEY']

        # Fallback: Check local secrets file
        secrets_file = '/home/micha/bqx_ml_v3/.env'
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r') as f:
                for line in f:
                    if line.startswith('AIRTABLE_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        os.environ['AIRTABLE_API_KEY'] = key
                        print("✅ Found AirTable API key in .env file")
                        return key

        print("❌ Could not find AirTable API key in any location")
        return None

def test_airtable_connection():
    """
    Test the AirTable connection with the retrieved key
    """
    api_key = get_airtable_api_key()

    if not api_key:
        print("❌ No API key available for testing")
        return False

    try:
        from pyairtable import Api
        api = Api(api_key)
        base_id = 'app3tpP9F3BrP1P7j'

        # Try to access the Tasks table
        tasks_table = api.table(base_id, 'Tasks')

        # Test with a simple query (limit to 1 record)
        records = tasks_table.all(max_records=1)

        print(f"✅ AirTable connection successful!")
        print(f"   Base ID: {base_id}")
        print(f"   Tasks table accessible")
        return True

    except Exception as e:
        print(f"❌ Failed to connect to AirTable: {e}")
        return False

if __name__ == "__main__":
    # Test the key retrieval
    print("🔑 Retrieving AirTable API key from GCP Secrets Manager...")
    api_key = get_airtable_api_key()

    if api_key:
        print(f"✅ API key retrieved (length: {len(api_key)} chars)")

        # Test the connection
        print("\n🔗 Testing AirTable connection...")
        if test_airtable_connection():
            print("\n✅ All systems operational!")
        else:
            print("\n⚠️ Connection test failed - check credentials")
    else:
        print("\n❌ Failed to retrieve API key")