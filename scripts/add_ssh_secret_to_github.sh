#!/bin/bash
# Add SSH remote host configuration to GitHub Secrets
# Usage: bash scripts/add_ssh_secret_to_github.sh

set -e

echo "🔐 Adding SSH Remote Host Configuration to GitHub Secrets"
echo "=========================================================="

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Read SSH config JSON
CONFIG_FILE=".secrets/ssh_remote_host_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

echo "✓ Found SSH config file"

# Add JSON config to GitHub secrets
echo "📤 Adding SSH_REMOTE_HOST_CONFIG to GitHub secrets..."
gh secret set SSH_REMOTE_HOST_CONFIG < "$CONFIG_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Successfully added SSH_REMOTE_HOST_CONFIG"
else
    echo "❌ Failed to add SSH_REMOTE_HOST_CONFIG"
    exit 1
fi

# Add individual secrets for easier access
echo ""
echo "📤 Adding individual SSH secrets..."

# Extract values from JSON
HOSTNAME=$(jq -r '.hostname' "$CONFIG_FILE")
USER=$(jq -r '.user' "$CONFIG_FILE")
PORT=$(jq -r '.port' "$CONFIG_FILE")
ZONE=$(jq -r '.zone' "$CONFIG_FILE")

echo "  - SSH_HOST_IP=$HOSTNAME"
echo "$HOSTNAME" | gh secret set SSH_HOST_IP

echo "  - SSH_HOST_USER=$USER"
echo "$USER" | gh secret set SSH_HOST_USER

echo "  - SSH_HOST_PORT=$PORT"
echo "$PORT" | gh secret set SSH_HOST_PORT

echo "  - SSH_HOST_ZONE=$ZONE"
echo "$ZONE" | gh secret set SSH_HOST_ZONE

echo ""
echo "✅ All SSH secrets added successfully!"
echo ""
echo "📋 Secrets added:"
echo "   1. SSH_REMOTE_HOST_CONFIG (JSON)"
echo "   2. SSH_HOST_IP"
echo "   3. SSH_HOST_USER"
echo "   4. SSH_HOST_PORT"
echo "   5. SSH_HOST_ZONE"
echo ""
echo "🔗 View secrets at:"
echo "   https://github.com/Schmidtlappin/bqx_ml_v3/settings/secrets/actions"
echo ""
echo "⚠️  Note: Private key (SSH_PRIVATE_KEY) should be added manually for security"
echo "   Location: ~/.ssh/google_compute_engine"
