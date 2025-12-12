#!/bin/bash
# sync-claude-workspace.sh - Bidirectional sync of Claude workspace with Google Drive
# Changes in Google Drive sync back to VM, and vice versa.
# This syncs the .claude directory which contains agent communications,
# settings, and workspace files (NOT the actual conversation)
# UPDATED 2025-12-11: Bidirectional sync with reduced aggression
#
# Usage:
#   ./sync-claude-workspace.sh [--resync]
#
# Options:
#   --resync    Force resync (required for first run or after conflicts)

set -e

# Configuration
CLAUDE_DIR="/home/micha/bqx_ml_v3/.claude"
GDRIVE_REMOTE="gdrive:claude-workspace"
LOG_DIR="/home/micha/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESYNC=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --resync)
            RESYNC=true
            shift
            ;;
    esac
done

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "[$TIMESTAMP] Starting Claude workspace bidirectional sync..."
echo "NOTE: Changes in BOTH directions will be synced (VM ↔ Google Drive)"
echo "Note: This syncs workspace files, NOT the conversation history"

# Check if Claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ Claude directory not found at $CLAUDE_DIR"
    exit 1
fi

# Create the remote directory if it doesn't exist
rclone mkdir "$GDRIVE_REMOTE" 2>/dev/null || true

# Check if this is first run or resync requested
BISYNC_OPTS=""
if [ "$RESYNC" = true ]; then
    echo "RESYNC mode: Establishing new baseline..."
    BISYNC_OPTS="--resync"
fi

# Bidirectional sync Claude workspace with Google Drive (REDUCED AGGRESSION MODE)
# Settings: --transfers 2, --checkers 4, --bwlimit 10M
# Conflict resolution: newer file wins
echo "Settings: --transfers 2, --checkers 4, --bwlimit 10M"
echo "Conflict resolution: newer file wins"

rclone bisync "$CLAUDE_DIR" "$GDRIVE_REMOTE" \
  --exclude "temp/**" \
  --exclude "*.log" \
  --exclude "checkpoints/**" \
  --exclude ".git/**" \
  --transfers 2 \
  --checkers 4 \
  --bwlimit 10M \
  --conflict-resolve newer \
  --conflict-loser num \
  --conflict-suffix conflict \
  --create-empty-src-dirs \
  --verbose \
  --log-file="${LOG_DIR}/claude-sync-${TIMESTAMP}.log" \
  $BISYNC_OPTS

if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Claude workspace bidirectional sync completed successfully"
else
    echo "[$TIMESTAMP] ERROR: Bidirectional sync failed. You may need to run with --resync"
    exit 1
fi
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