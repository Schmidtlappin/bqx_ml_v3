#!/bin/bash
# EA Inbox Monitor - Checks for new messages every 5 minutes
# Run in background: ./ea_inbox_monitor.sh &

EA_INBOX="/home/micha/bqx_ml_v3/.claude/sandbox/communications/inboxes/EA"
LOG_FILE="/tmp/ea_inbox_monitor.log"

echo "$(date): EA Inbox Monitor started" >> $LOG_FILE

while true; do
    # Count files in inbox
    FILE_COUNT=$(ls -1 "$EA_INBOX"/*.md 2>/dev/null | wc -l)
    LATEST=$(ls -t "$EA_INBOX"/*.md 2>/dev/null | head -1)

    if [ -n "$LATEST" ]; then
        LATEST_NAME=$(basename "$LATEST")
        echo "$(date): Files=$FILE_COUNT, Latest=$LATEST_NAME" >> $LOG_FILE
    fi

    # Sleep 5 minutes (300 seconds)
    sleep 300
done
