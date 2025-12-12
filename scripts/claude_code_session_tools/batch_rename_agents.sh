#!/bin/bash
# Batch rename all agent sessions from AGENT_REGISTRY.json
#
# Usage:
#   ./batch_rename_agents.sh

set -e

PROJECT_DIR="/home/micha/.claude/projects/-home-micha-bqx-ml-v3"
REGISTRY_FILE="/home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Claude Code Agent Session Batch Rename ==="
echo ""

# Check if registry exists
if [ ! -f "$REGISTRY_FILE" ]; then
    echo "✗ AGENT_REGISTRY.json not found at: $REGISTRY_FILE"
    exit 1
fi

# Check if update script exists
if [ ! -f "$SCRIPT_DIR/update_first_message.py" ]; then
    echo "✗ update_first_message.py not found in: $SCRIPT_DIR"
    exit 1
fi

# Extract sessions from registry and rename
echo "Reading sessions from AGENT_REGISTRY.json..."
echo ""

# CE - Chief Engineer
CE_ID=$(jq -r '.agent_registry.CE.current_session_id // empty' "$REGISTRY_FILE")
if [ -n "$CE_ID" ] && [ -f "$PROJECT_DIR/$CE_ID.jsonl" ]; then
    echo "Updating CE ($CE_ID)..."
    python3 "$SCRIPT_DIR/update_first_message.py" "$PROJECT_DIR/$CE_ID.jsonl" "CE - Chief Engineer"
fi

# BA - Build Agent
BA_ID=$(jq -r '.agent_registry.BA.current_session_id // empty' "$REGISTRY_FILE")
if [ -n "$BA_ID" ] && [ -f "$PROJECT_DIR/$BA_ID.jsonl" ]; then
    echo "Updating BA ($BA_ID)..."
    python3 "$SCRIPT_DIR/update_first_message.py" "$PROJECT_DIR/$BA_ID.jsonl" "BA - Build Agent"
fi

# QA - Quality Assurance
QA_ID=$(jq -r '.agent_registry.QA.current_session_id // empty' "$REGISTRY_FILE")
if [ -n "$QA_ID" ] && [ -f "$PROJECT_DIR/$QA_ID.jsonl" ]; then
    echo "Updating QA ($QA_ID)..."
    python3 "$SCRIPT_DIR/update_first_message.py" "$PROJECT_DIR/$QA_ID.jsonl" "QA - Quality Assurance"
fi

# EA - Enhancement Assistant
EA_ID=$(jq -r '.agent_registry.EA.current_session_id // empty' "$REGISTRY_FILE")
if [ -n "$EA_ID" ] && [ -f "$PROJECT_DIR/$EA_ID.jsonl" ]; then
    echo "Updating EA ($EA_ID)..."
    python3 "$SCRIPT_DIR/update_first_message.py" "$PROJECT_DIR/$EA_ID.jsonl" "EA - Enhancement Assistant"
fi

echo ""
echo "✓ Batch rename complete!"
echo ""
echo "Next step: Reload VS Code window to see changes"
echo "  1. Press Cmd/Ctrl + Shift + P"
echo "  2. Type 'Developer: Reload Window'"
echo "  3. Press Enter"
