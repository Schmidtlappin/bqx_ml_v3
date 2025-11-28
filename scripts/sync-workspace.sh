#!/bin/bash
#
# BQX-ML-V3 Unified Workspace Sync
# Syncs to BOTH Google Drive AND Box.com for disaster recovery
#
# Usage:
#   ./sync-workspace.sh [--gdrive-only] [--box-only] [--background]
#
# Options:
#   --gdrive-only    Only sync to Google Drive
#   --box-only       Only sync to Box.com
#   --background     Run sync in background (nohup)
#

set -e

PROJECT_ROOT="/home/micha/bqx_ml_v3"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/sync_$TIMESTAMP.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Parse arguments
GDRIVE_ONLY=false
BOX_ONLY=false
BACKGROUND=false

for arg in "$@"; do
    case $arg in
        --gdrive-only)
            GDRIVE_ONLY=true
            shift
            ;;
        --box-only)
            BOX_ONLY=true
            shift
            ;;
        --background)
            BACKGROUND=true
            shift
            ;;
    esac
done

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

sync_gdrive() {
    log "=== Google Drive Sync Starting ==="

    if command -v rclone &> /dev/null; then
        log "Syncing to gdrive:bqx_ml_v3..."
        rclone sync "$PROJECT_ROOT" gdrive:bqx_ml_v3 \
            --exclude ".git/**" \
            --exclude ".secrets/**" \
            --exclude "__pycache__/**" \
            --exclude "*.pyc" \
            --exclude ".env" \
            --exclude "venv/**" \
            --exclude "node_modules/**" \
            --exclude "*.pkl" \
            --exclude "*.model" \
            --exclude "logs/**" \
            --progress \
            2>&1 | tee -a "$LOG_FILE"

        log "Google Drive sync completed"
    else
        log "ERROR: rclone not found. Cannot sync to Google Drive."
        return 1
    fi
}

sync_box() {
    log "=== Box.com Sync Starting ==="

    if python3 -c "import box_sdk_gen" 2>/dev/null; then
        log "Syncing to Box.com (bqx-ml-v3 folder)..."
        python3 "$PROJECT_ROOT/scripts/sync-box-backup.py" --files-only 2>&1 | tee -a "$LOG_FILE"
        log "Box.com sync completed"
    else
        log "ERROR: box_sdk_gen not found. Cannot sync to Box.com."
        return 1
    fi
}

main() {
    log "=============================================="
    log "BQX-ML-V3 Workspace Sync"
    log "Timestamp: $TIMESTAMP"
    log "=============================================="

    GDRIVE_STATUS="SKIPPED"
    BOX_STATUS="SKIPPED"

    # Sync to Google Drive
    if [ "$BOX_ONLY" = false ]; then
        if sync_gdrive; then
            GDRIVE_STATUS="SUCCESS"
        else
            GDRIVE_STATUS="FAILED"
        fi
    fi

    # Sync to Box.com
    if [ "$GDRIVE_ONLY" = false ]; then
        if sync_box; then
            BOX_STATUS="SUCCESS"
        else
            BOX_STATUS="FAILED"
        fi
    fi

    log "=============================================="
    log "Sync Summary:"
    log "  Google Drive: $GDRIVE_STATUS"
    log "  Box.com:      $BOX_STATUS"
    log "  Log file:     $LOG_FILE"
    log "=============================================="
}

# Run in background if requested
if [ "$BACKGROUND" = true ]; then
    nohup bash -c "$(declare -f log sync_gdrive sync_box main); main" > "$LOG_FILE" 2>&1 &
    echo "Sync started in background. PID: $!"
    echo "Log file: $LOG_FILE"
else
    main
fi
