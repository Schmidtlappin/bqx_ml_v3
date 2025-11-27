#!/bin/bash
# sync-claude-workspace.sh - Sync Claude workspace to Google Drive
# This syncs the .claude directory which contains agent communications,
# settings, and workspace files (NOT the actual conversation)

set -e

# Configuration
CLAUDE_DIR="/home/micha/bqx_ml_v3/.claude"
GDRIVE_REMOTE="gdrive:claude-workspace"
LOG_DIR="/home/micha/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "[$TIMESTAMP] Starting Claude workspace sync..."
echo "Note: This syncs workspace files, NOT the conversation history"

# Check if Claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ Claude directory not found at $CLAUDE_DIR"
    exit 1
fi

# Create the remote directory if it doesn't exist
rclone mkdir "$GDRIVE_REMOTE" 2>/dev/null || true

# Sync Claude workspace to Google Drive
rclone sync "$CLAUDE_DIR" "$GDRIVE_REMOTE" \
  --exclude "temp/**" \
  --exclude "*.log" \
  --exclude "checkpoints/**" \
  --exclude ".git/**" \
  --checksum \
  --transfers 4 \
  --checkers 8 \
  --log-level INFO \
  --log-file="${LOG_DIR}/claude-sync-${TIMESTAMP}.log" \
  --progress

echo "[$TIMESTAMP] Claude workspace sync complete"
echo "📁 Synced to: $GDRIVE_REMOTE"
echo "📝 Log file: ${LOG_DIR}/claude-sync-${TIMESTAMP}.log"

# Show what was synced
echo ""
echo "Files synced include:"
echo "  • Agent communications (BA, CE, etc.)"
echo "  • Settings and configurations"
echo "  • Sandbox workspace files"
echo ""
echo "NOT included:"
echo "  • Current conversation with Claude"
echo "  • VS Code extension chat history"