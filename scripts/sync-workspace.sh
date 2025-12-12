#!/bin/bash
#
# BQX-ML-V3 Unified Workspace Sync
# UPDATED 2025-12-11: Bidirectional sync with reduced aggression
# Changes in Google Drive sync back to VM, and vice versa.
# Default: Google Drive only. Box.com sync disabled by default.
#
# Usage:
#   ./sync-workspace.sh [--gdrive-only] [--box-only] [--background] [--enable-box] [--resync]
#
# Options:
#   --gdrive-only    Only sync to Google Drive
#   --box-only       Only sync to Box.com
#   --enable-box     Enable Box.com sync (disabled by default)
#   --background     Run sync in background (nohup)
#   --resync         Force resync (required for first run or after conflicts)
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
ENABLE_BOX=false  # Box.com disabled by default (2025-12-11)
RESYNC=false      # Force resync flag

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
        --enable-box)
            ENABLE_BOX=true
            shift
            ;;
        --background)
            BACKGROUND=true
            shift
            ;;
        --resync)
            RESYNC=true
            shift
            ;;
    esac
done

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

sync_gdrive() {
    log "=== Google Drive Bidirectional Sync Starting (Reduced Aggression Mode) ==="
    log "NOTE: Changes in BOTH directions will be synced (VM ↔ Google Drive)"

    if command -v rclone &> /dev/null; then
        # Check if this is first run or resync requested
        BISYNC_OPTS=""
        if [ "$RESYNC" = true ]; then
            log "RESYNC mode: Establishing new baseline..."
            BISYNC_OPTS="--resync"
        fi

        log "Syncing with gdrive:bqx_ml_v3 (bidirectional)..."
        log "Settings: --transfers 2, --checkers 4, --bwlimit 10M"
        log "Conflict resolution: newer file wins"

        rclone bisync "$PROJECT_ROOT" gdrive:bqx_ml_v3 \
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
            --transfers 2 \
            --checkers 4 \
            --bwlimit 10M \
            --conflict-resolve newer \
            --conflict-loser num \
            --conflict-suffix conflict \
            --create-empty-src-dirs \
            --verbose \
            $BISYNC_OPTS \
            2>&1 | tee -a "$LOG_FILE"

        if [ $? -eq 0 ]; then
            log "Google Drive bidirectional sync completed successfully"
        else
            log "ERROR: Bidirectional sync failed. You may need to run with --resync"
            return 1
        fi
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

    # Sync to Box.com (disabled by default unless --enable-box or --box-only)
    if [ "$GDRIVE_ONLY" = false ] && { [ "$ENABLE_BOX" = true ] || [ "$BOX_ONLY" = true ]; }; then
        if sync_box; then
            BOX_STATUS="SUCCESS"
        else
            BOX_STATUS="FAILED"
        fi
    else
        BOX_STATUS="DISABLED"
        log "Box.com sync DISABLED (use --enable-box to enable)"
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
