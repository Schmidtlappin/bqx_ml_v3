#!/usr/bin/env python3
"""
Synchronize AirTable credentials across all secret storage locations:
- Local: .secrets/github_secrets.json
- GitHub: Repository secrets
- GCP: Secret Manager
"""

import json
import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """Execute a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def load_local_secrets():
    """Load secrets from local file"""
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets'].get('AIRTABLE_API_KEY', {}).get('value')
            base_id = secrets['secrets'].get('AIRTABLE_BASE_ID', {}).get('value')
            return api_key, base_id
    except Exception as e:
        print(f"❌ Error loading local secrets: {e}")
        return None, None

def check_gcp_secrets():
    """Check GCP Secret Manager for AirTable secrets"""
    print("\n🔍 Checking GCP Secret Manager...")

    # Check for API key
    success, stdout, _ = run_command("gcloud secrets list --format='value(name)' | grep -i airtable")
    gcp_secrets = stdout.strip().split('\n') if success else []

    has_api_key = any('token' in s.lower() or 'key' in s.lower() for s in gcp_secrets)
    has_base_id = any('base' in s.lower() for s in gcp_secrets)

    print(f"  API Key: {'✅ Found' if has_api_key else '❌ Missing'}")
    print(f"  Base ID: {'✅ Found' if has_base_id else '❌ Missing'}")

    return has_api_key, has_base_id

def sync_to_gcp(api_key, base_id):
    """Sync AirTable secrets to GCP Secret Manager"""
    print("\n📤 Syncing to GCP Secret Manager...")

    # Update or create API key secret
    if api_key:
        # Check if secret exists
        check_cmd = "gcloud secrets describe bqx-ml-airtable-token 2>/dev/null"
        exists, _, _ = run_command(check_cmd)

        if exists:
            # Update existing secret
            cmd = f"echo -n '{api_key}' | gcloud secrets versions add bqx-ml-airtable-token --data-file=-"
            success, _, error = run_command(cmd)
            if success:
                print("  ✅ Updated bqx-ml-airtable-token")
            else:
                print(f"  ❌ Failed to update API key: {error}")
        else:
            # Create new secret
            cmd = f"echo -n '{api_key}' | gcloud secrets create bqx-ml-airtable-token --data-file=- --replication-policy=automatic"
            success, _, error = run_command(cmd)
            if success:
                print("  ✅ Created bqx-ml-airtable-token")
            else:
                print(f"  ❌ Failed to create API key: {error}")

    # Create Base ID secret (if missing)
    if base_id:
        # Check if secret exists
        check_cmd = "gcloud secrets describe bqx-ml-airtable-base-id 2>/dev/null"
        exists, _, _ = run_command(check_cmd)

        if not exists:
            # Create new secret
            cmd = f"echo -n '{base_id}' | gcloud secrets create bqx-ml-airtable-base-id --data-file=- --replication-policy=automatic"
            success, _, error = run_command(cmd)
            if success:
                print("  ✅ Created bqx-ml-airtable-base-id")
            else:
                print(f"  ❌ Failed to create Base ID: {error}")
        else:
            print("  ℹ️  bqx-ml-airtable-base-id already exists")

def check_github_repo():
    """Check GitHub repository access"""
    print("\n🔍 Checking GitHub repository...")

    # Try to get repo info
    cmd = "gh repo view bqx-gpt/bqx_ml_v3 --json name 2>/dev/null"
    success, stdout, error = run_command(cmd)

    if not success or "Not Found" in error:
        # Try different repo names
        repos_to_try = [
            "bqx_ml_v3",
            "micha/bqx_ml_v3",
            "."  # Current repo
        ]

        for repo in repos_to_try:
            cmd = f"gh repo view {repo} --json name 2>/dev/null"
            success, stdout, _ = run_command(cmd)
            if success:
                print(f"  ✅ Found repository: {repo}")
                return repo

        print("  ❌ No GitHub repository found")
        return None

    print(f"  ✅ Repository accessible: bqx-gpt/bqx_ml_v3")
    return "bqx-gpt/bqx_ml_v3"

def sync_to_github(api_key, base_id, repo):
    """Sync AirTable secrets to GitHub"""
    if not repo:
        print("\n⚠️  Skipping GitHub sync - no repository found")
        return

    print(f"\n📤 Syncing to GitHub repository: {repo}")

    # Set API key
    if api_key:
        cmd = f"echo '{api_key}' | gh secret set AIRTABLE_API_KEY --repo={repo}"
        success, _, error = run_command(cmd)
        if success:
            print("  ✅ Set AIRTABLE_API_KEY")
        else:
            print(f"  ❌ Failed to set API key: {error}")

    # Set Base ID
    if base_id:
        cmd = f"echo '{base_id}' | gh secret set AIRTABLE_BASE_ID --repo={repo}"
        success, _, error = run_command(cmd)
        if success:
            print("  ✅ Set AIRTABLE_BASE_ID")
        else:
            print(f"  ❌ Failed to set Base ID: {error}")

def main():
    print("=" * 60)
    print("AIRTABLE SECRETS SYNCHRONIZATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Load local secrets
    print("\n📁 Loading local secrets...")
    api_key, base_id = load_local_secrets()

    if not api_key or not base_id:
        print("❌ Missing local AirTable credentials!")
        print("   Please ensure both AIRTABLE_API_KEY and AIRTABLE_BASE_ID")
        print("   are present in .secrets/github_secrets.json")
        sys.exit(1)

    print(f"  ✅ API Key: {len(api_key)} characters")
    print(f"  ✅ Base ID: {base_id}")

    # Check and sync to GCP
    has_gcp_key, has_gcp_base = check_gcp_secrets()
    if not has_gcp_key or not has_gcp_base:
        sync_to_gcp(api_key, base_id)
    else:
        print("  ℹ️  GCP secrets already present")

    # Check and sync to GitHub
    repo = check_github_repo()
    if repo:
        sync_to_github(api_key, base_id, repo)

    print("\n" + "=" * 60)
    print("SYNCHRONIZATION SUMMARY")
    print("=" * 60)

    # Final verification
    print("\n📊 Final Status:")
    print(f"  Local: ✅ Both secrets present")

    # Check GCP again
    success, stdout, _ = run_command("gcloud secrets list --format='value(name)' | grep -i airtable | wc -l")
    gcp_count = int(stdout.strip()) if success else 0
    print(f"  GCP: {gcp_count} AirTable secret(s)")

    # Check GitHub if repo exists
    if repo:
        cmd = f"gh secret list --repo={repo} 2>/dev/null | grep -i airtable | wc -l"
        success, stdout, _ = run_command(cmd)
        gh_count = int(stdout.strip()) if success else 0
        print(f"  GitHub: {gh_count} AirTable secret(s)")

    print("\n✅ Synchronization complete!")
    print("\nUsage in different contexts:")
    print("  Local: Load from .secrets/github_secrets.json")
    print("  GCP: gcloud secrets versions access latest bqx-ml-airtable-token")
    print("  GitHub Actions: Use ${{ secrets.AIRTABLE_API_KEY }}")

if __name__ == "__main__":
    main()