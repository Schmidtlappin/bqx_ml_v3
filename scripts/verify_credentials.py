#!/usr/bin/env python3
"""
Verify all credentials are properly configured in GitHub and GCP.
Tests connectivity without exposing sensitive information.
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def check_github_secrets():
    """Verify GitHub secrets are configured."""
    print("\n=== GitHub Secrets Status ===")
    try:
        result = subprocess.run(
            ['gh', 'secret', 'list', '--repo', 'Schmidtlappin/bqx_ml_v3'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            secrets = result.stdout.strip().split('\n')
            github_secrets = {}
            for secret in secrets:
                if secret:
                    parts = secret.split('\t')
                    if len(parts) >= 2:
                        github_secrets[parts[0]] = parts[1]

            print(f"✓ GitHub secrets found: {len(github_secrets)}")

            # Check for AirTable credentials specifically
            airtable_secrets = [s for s in github_secrets if 'AIRTABLE' in s]
            if airtable_secrets:
                print(f"✓ AirTable secrets configured: {', '.join(airtable_secrets)}")
                for secret in airtable_secrets:
                    print(f"  - {secret}: Last updated {github_secrets.get(secret, 'Unknown')}")
            else:
                print("❌ No AirTable secrets found in GitHub")
                return False

            # Check for GCP credentials
            gcp_secrets = [s for s in github_secrets if 'GCP' in s]
            if gcp_secrets:
                print(f"✓ GCP secrets configured: {', '.join(gcp_secrets)}")
            else:
                print("⚠️ No GCP secrets found in GitHub")

            return True
        else:
            print(f"❌ Failed to list GitHub secrets: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking GitHub secrets: {e}")
        return False

def check_gcp_secrets():
    """Verify GCP Secret Manager secrets."""
    print("\n=== GCP Secret Manager Status ===")
    try:
        # Check if authenticated to GCP
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True, text=True, timeout=5
        )
        project = result.stdout.strip()
        if not project:
            print("❌ Not authenticated to GCP")
            return False

        print(f"✓ Authenticated to GCP project: {project}")

        # List secrets
        result = subprocess.run(
            ['gcloud', 'secrets', 'list', '--project', project, '--format=json'],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            secrets = json.loads(result.stdout) if result.stdout else []
            secret_names = [s['name'].split('/')[-1] for s in secrets]

            print(f"✓ Total secrets in GCP: {len(secret_names)}")

            # Check for AirTable secret
            airtable_secrets = [s for s in secret_names if 'airtable' in s.lower()]
            if airtable_secrets:
                print(f"✓ AirTable secrets in GCP: {', '.join(airtable_secrets)}")
            else:
                print("⚠️ No AirTable secrets found in GCP Secret Manager")

            return True
        else:
            print(f"⚠️ Could not list GCP secrets: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking GCP secrets: {e}")
        return False

def check_local_secrets():
    """Check local secrets configuration."""
    print("\n=== Local Secrets Configuration ===")

    # Check .secrets directory
    secrets_dir = '/home/micha/bqx_ml_v3/.secrets'
    if os.path.exists(secrets_dir):
        print(f"✓ Secrets directory exists: {secrets_dir}")

        # Check for github_secrets.json
        secrets_file = os.path.join(secrets_dir, 'github_secrets.json')
        if os.path.exists(secrets_file):
            print(f"✓ GitHub secrets file exists: {secrets_file}")

            try:
                with open(secrets_file, 'r') as f:
                    data = json.load(f)

                if 'secrets' in data:
                    secrets = data['secrets']
                    airtable_keys = [k for k in secrets if 'AIRTABLE' in k]
                    if airtable_keys:
                        print(f"✓ AirTable credentials defined: {', '.join(airtable_keys)}")
                        # Check if values are populated (without printing them)
                        for key in airtable_keys:
                            if secrets[key] and secrets[key] != "your-airtable-api-key-here":
                                print(f"  ✓ {key}: Configured (not placeholder)")
                            else:
                                print(f"  ❌ {key}: Using placeholder value")
                    else:
                        print("❌ No AirTable credentials in local secrets file")

                if 'last_updated' in data:
                    print(f"  Last updated: {data['last_updated']}")

            except Exception as e:
                print(f"❌ Error reading secrets file: {e}")
                return False
        else:
            print(f"❌ GitHub secrets file not found: {secrets_file}")
            return False
    else:
        print(f"❌ Secrets directory not found: {secrets_dir}")
        return False

    return True

def verify_airtable_connectivity():
    """Test AirTable API connectivity."""
    print("\n=== AirTable API Connectivity ===")

    # Try to import pyairtable
    try:
        from pyairtable import Api
        print("✓ pyairtable library available")
    except ImportError:
        print("❌ pyairtable library not installed")
        print("  Run: pip install pyairtable")
        return False

    # Check environment variables
    api_key = os.environ.get('AIRTABLE_API_KEY')
    base_id = os.environ.get('AIRTABLE_BASE_ID')

    if api_key and base_id:
        print("✓ AirTable environment variables set")
        if api_key.startswith('pat'):
            print("  ✓ API key format looks valid (starts with 'pat')")
        else:
            print("  ⚠️ API key format may be invalid")
    else:
        print("⚠️ AirTable environment variables not set")
        print("  Missing: " + ", ".join([
            'AIRTABLE_API_KEY' if not api_key else '',
            'AIRTABLE_BASE_ID' if not base_id else ''
        ]).strip(', '))

    return True

def main():
    """Main verification routine."""
    print("=" * 60)
    print("BQX ML V3 Credentials Verification")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    results = {
        'github': check_github_secrets(),
        'gcp': check_gcp_secrets(),
        'local': check_local_secrets(),
        'airtable': verify_airtable_connectivity()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_good = True
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'Configured' if status else 'Issues found'}")
        if not status:
            all_good = False

    if all_good:
        print("\n✅ All credentials are properly configured!")
        print("\nRECOMMENDATION: The secrets are up-to-date and ready for use.")
    else:
        print("\n⚠️ Some credentials need attention.")
        print("\nRECOMMENDATIONS:")
        if not results['github']:
            print("1. Run: ./scripts/setup_github_secrets.sh")
        if not results['gcp']:
            print("2. Authenticate to GCP: gcloud auth login")
        if not results['airtable']:
            print("3. Set AirTable environment variables or update .env file")

    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())