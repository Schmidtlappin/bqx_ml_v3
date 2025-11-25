#!/bin/bash

# BQX ML V3 - GitHub Secrets Setup Script
# This script deploys all required secrets to GitHub repository

echo "=========================================================================="
echo "BQX ML V3 - GITHUB SECRETS SETUP"
echo "=========================================================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Please install it first: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Please run: gh auth login"
    exit 1
fi

# Set repository (you may need to adjust this)
REPO="Schmidtlappin/bqx_ml_v3"
echo "📍 Repository: $REPO"

# Load existing secrets from local file
SECRETS_FILE="/home/micha/bqx_ml_v3/.secrets/github_secrets.json"

if [ ! -f "$SECRETS_FILE" ]; then
    echo "❌ Secrets file not found: $SECRETS_FILE"
    exit 1
fi

echo ""
echo "🔐 Setting up GitHub Secrets..."
echo "--------------------------------------------------------------------------"

# Function to set a secret
set_secret() {
    local key=$1
    local value=$2

    echo -n "  Setting $key... "
    echo "$value" | gh secret set "$key" --repo="$REPO" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "❌ Failed"
        return 1
    fi
}

# Extract and set secrets using Python to parse JSON
python3 << 'PYTHON_SCRIPT'
import json
import subprocess
import sys

# Load the secrets file
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    data = json.load(f)

secrets = data.get('secrets', {})
repo = "Schmidtlappin/bqx_ml_v3"

# Core secrets to set
required_secrets = [
    'AIRTABLE_API_KEY',
    'AIRTABLE_BASE_ID',
    'GOOGLE_APPLICATION_CREDENTIALS',
    'GCP_PROJECT_ID',
    'GCP_SA_KEY',
    'DOCKER_REGISTRY_TOKEN',
    'SLACK_WEBHOOK_URL',
    'MONITORING_API_KEY',
    'ENCRYPTION_KEY',
    'JWT_SECRET_KEY'
]

# Additional BQX ML V3 specific secrets
bqx_secrets = [
    'MARKET_DATA_API_KEY',
    'MARKET_DATA_API_SECRET',
    'REUTERS_API_KEY',
    'BLOOMBERG_API_TOKEN',
    'ALPHA_VANTAGE_KEY',
    'IEX_CLOUD_TOKEN',
    'POLYGON_API_KEY',
    'QUANDL_API_KEY',
    'FRED_API_KEY',
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'REDIS_PASSWORD',
    'POSTGRES_PASSWORD',
    'KAFKA_SASL_PASSWORD',
    'GRAFANA_API_KEY',
    'PAGERDUTY_API_KEY',
    'SENTRY_DSN',
    'DATADOG_API_KEY',
    'NEWRELIC_LICENSE_KEY',
    'FIREBASE_API_KEY',
    'STRIPE_API_KEY',
    'SENDGRID_API_KEY',
    'TWILIO_AUTH_TOKEN',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY'
]

all_secrets = required_secrets + bqx_secrets
success_count = 0
fail_count = 0
skip_count = 0

for secret_name in all_secrets:
    # Check if secret exists in our file
    secret_data = secrets.get(secret_name)

    if secret_data and isinstance(secret_data, dict):
        value = secret_data.get('value', '')
    elif secret_data and isinstance(secret_data, str):
        value = secret_data
    else:
        # Try to find it in environment or generate placeholder
        value = None

    if value:
        # Set the secret in GitHub
        try:
            result = subprocess.run(
                ['gh', 'secret', 'set', secret_name, '--repo', repo],
                input=value.encode(),
                capture_output=True,
                text=False
            )

            if result.returncode == 0:
                print(f"  ✅ {secret_name}")
                success_count += 1
            else:
                print(f"  ❌ {secret_name} - Failed to set")
                fail_count += 1
        except Exception as e:
            print(f"  ❌ {secret_name} - Error: {e}")
            fail_count += 1
    else:
        print(f"  ⏭️  {secret_name} - Not found in local secrets")
        skip_count += 1

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"✅ Successfully set: {success_count} secrets")
print(f"⏭️  Skipped: {skip_count} secrets")
print(f"❌ Failed: {fail_count} secrets")
PYTHON_SCRIPT

echo ""
echo "=========================================================================="
echo "ADDITIONAL SETUP STEPS"
echo "=========================================================================="

echo ""
echo "📋 Next Steps:"
echo "1. Verify secrets in GitHub: https://github.com/$REPO/settings/secrets/actions"
echo "2. Create service account key for GCP if not done"
echo "3. Set up workload identity federation for GCP"
echo "4. Configure branch protection rules"
echo "5. Enable required GitHub Actions"

echo ""
echo "🔒 Security Best Practices:"
echo "• Rotate secrets every 90 days"
echo "• Use environment-specific secrets"
echo "• Implement secret scanning"
echo "• Enable audit logging"
echo "• Use least privilege principle"

echo ""
echo "📦 Required GitHub Actions to Enable:"
echo "• CI/CD Pipeline"
echo "• Security Scanning"
echo "• Dependency Updates"
echo "• Code Quality Checks"
echo "• Automated Testing"

echo ""
echo "=========================================================================="
echo "✅ GitHub Secrets Setup Complete!"
echo "=========================================================================="