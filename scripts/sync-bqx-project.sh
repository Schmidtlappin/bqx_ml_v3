#!/bin/bash
# sync-bqx-project.sh - Bidirectional sync of BQX ML V3 project with Google Drive
# Changes in Google Drive sync back to VM, and vice versa.
# Includes all project files, Claude workspace, scripts, docs, etc.
# UPDATED 2025-12-11: Bidirectional sync with reduced aggression
#
# Usage:
#   ./sync-bqx-project.sh [--resync]
#
# Options:
#   --resync    Force resync (required for first run or after conflicts)

set -e

# Configuration
PROJECT_DIR="/home/micha/bqx_ml_v3"
GDRIVE_REMOTE="gdrive:bqx_ml_v3"
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

echo "[$TIMESTAMP] Starting BQX ML V3 project bidirectional sync..."
echo "NOTE: Changes in BOTH directions will be synced (VM ↔ Google Drive)"
echo "Project size: $(du -sh $PROJECT_DIR | cut -f1)"

# Create the remote directory if it doesn't exist
rclone mkdir "$GDRIVE_REMOTE" 2>/dev/null || true

# Check if this is first run or resync requested
BISYNC_OPTS=""
if [ "$RESYNC" = true ]; then
    echo "RESYNC mode: Establishing new baseline..."
    BISYNC_OPTS="--resync"
fi

# Bidirectional sync with Google Drive (REDUCED AGGRESSION MODE)
# Settings: --transfers 2, --checkers 4, --bwlimit 10M
# Conflict resolution: newer file wins
echo "Settings: --transfers 2, --checkers 4, --bwlimit 10M"
echo "Conflict resolution: newer file wins"

rclone bisync "$PROJECT_DIR" "$GDRIVE_REMOTE" \
  --exclude ".git/**" \
  --exclude ".secrets/**" \
  --exclude "baseline_model.pkl" \
  --exclude "*.pyc" \
  --exclude "__pycache__/**" \
  --exclude ".venv/**" \
  --exclude "venv/**" \
  --exclude "*.log" \
  --exclude ".pytest_cache/**" \
  --exclude "temp/**" \
  --transfers 2 \
  --checkers 4 \
  --bwlimit 10M \
  --conflict-resolve newer \
  --conflict-loser num \
  --conflict-suffix conflict \
  --create-empty-src-dirs \
  --verbose \
  --log-file="${LOG_DIR}/bqx-sync-${TIMESTAMP}.log" \
  $BISYNC_OPTS

if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] BQX ML V3 project bidirectional sync completed successfully"
else
    echo "[$TIMESTAMP] ERROR: Bidirectional sync failed. You may need to run with --resync"
    exit 1
fi
echo "📁 Synced to: $GDRIVE_REMOTE"
echo "📝 Log file: ${LOG_DIR}/bqx-sync-${TIMESTAMP}.log"

# Summary of what was synced
echo ""
echo "✅ Synced:"
echo "  • Python scripts and source code"
echo "  • Documentation (docs/)"
echo "  • Intelligence files (intelligence/)"
echo "  • Claude workspace (.claude/)"
echo "  • Configuration files"
echo ""
echo "❌ Excluded:"
echo "  • Git repository (.git/)"
echo "  • Secrets (.secrets/)"
echo "  • Large model files (*.pkl)"
echo "  • Python cache files"
echo "  • Virtual environments"