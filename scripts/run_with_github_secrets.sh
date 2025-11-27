#!/bin/bash

# Run script with GitHub secrets exported
echo "Setting up environment from GitHub secrets..."

# Create temporary env file with GitHub secrets
cat > /tmp/github_secrets.env << 'EOF'
# These values will be retrieved from GitHub secrets
# For now, we'll note that they're configured in GitHub
EOF

# Get the AirTable secrets from .secrets directory if available
if [ -f ".secrets/airtable_key.txt" ]; then
    export AIRTABLE_API_KEY=$(cat .secrets/airtable_key.txt)
    echo "✅ Loaded AIRTABLE_API_KEY from .secrets"
fi

if [ -f ".secrets/airtable_base_id.txt" ]; then
    export AIRTABLE_BASE_ID=$(cat .secrets/airtable_base_id.txt)
    echo "✅ Loaded AIRTABLE_BASE_ID from .secrets"
fi

# Alternative: Use the values from credentials/setup_env.sh
source credentials/setup_env.sh

# Note: Since GitHub secrets are not directly accessible via CLI
# we need to use GitHub Actions or the repository settings

echo "Environment configured. Check GitHub repository settings for secret values."
echo ""
echo "GitHub Secrets are configured at:"
echo "https://github.com/Schmidtlappin/bqx_ml_v3/settings/secrets/actions"
echo ""
echo "To use these secrets:"
echo "1. They are automatically available in GitHub Actions workflows"
echo "2. For local development, download them securely and add to .secrets/"
echo ""

# For now, document the tasks that would be added to AirTable
echo "Creating documentation for Vertex AI tasks to be added to AirTable..."

# Run the Python script if argument provided
if [ "$1" == "python" ]; then
    python3 "$2"
fi