#!/bin/bash
# sync-bqx-project.sh - Sync entire BQX ML V3 project to Google Drive
# Includes all project files, Claude workspace, scripts, docs, etc.

set -e

# Configuration
PROJECT_DIR="/home/micha/bqx_ml_v3"
GDRIVE_REMOTE="gdrive:bqx_ml_v3"
LOG_DIR="/home/micha/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "[$TIMESTAMP] Starting BQX ML V3 project sync..."
echo "Project size: $(du -sh $PROJECT_DIR | cut -f1)"

# Create the remote directory if it doesn't exist
rclone mkdir "$GDRIVE_REMOTE" 2>/dev/null || true

# Sync entire project to Google Drive
rclone sync "$PROJECT_DIR" "$GDRIVE_REMOTE" \
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
  --checksum \
  --transfers 4 \
  --checkers 8 \
  --log-level INFO \
  --log-file="${LOG_DIR}/bqx-sync-${TIMESTAMP}.log" \
  --progress

echo "[$TIMESTAMP] BQX ML V3 project sync complete"
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