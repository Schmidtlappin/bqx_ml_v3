#!/bin/bash
set -e

# If PORT is set, start HTTP server for Cloud Run health checks
if [ -n "$PORT" ]; then
    # Start simple HTTP server in background for health checks
    python3 -m http.server $PORT &
    HTTP_PID=$!
fi

# Determine pair to process from environment variable or argument
PAIR="${TARGET_PAIR:-${1:-}}"

if [ -z "$PAIR" ]; then
    echo "ERROR: No pair specified. Set TARGET_PAIR environment variable or pass as argument."
    exit 1
fi

echo "========================================="
echo "Cloud Run Pipeline Execution"
echo "Pair: $PAIR"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================="

# Execute single pair pipeline
/workspace/scripts/cloud_run_single_pair.sh "$PAIR"

EXIT_CODE=$?

echo "========================================="
echo "Execution Complete"
echo "Pair: $PAIR"
echo "Exit Code: $EXIT_CODE"
echo "Completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================="

# Kill HTTP server if running
if [ -n "$HTTP_PID" ]; then
    kill $HTTP_PID 2>/dev/null || true
fi

exit $EXIT_CODE
