#!/bin/bash
# Setup script for AirTable + Claude Code Integration
# Works for CE, BA, MA, TA, and all agents

echo "🔗 Setting up AirTable Integration for All Agents"
echo "================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Install pyairtable
echo "📦 Installing pyairtable..."
pip install pyairtable --quiet

# Check for API key
if [ -z "$AIRTABLE_API_KEY" ]; then
    echo ""
    echo "⚠️  AIRTABLE_API_KEY not found in environment"
    echo ""
    echo "To get your API key:"
    echo "1. Go to: https://airtable.com/create/tokens"
    echo "2. Create a token with these scopes:"
    echo "   - data.records:read"
    echo "   - data.records:write"
    echo "   - schema.bases:read"
    echo "3. Add base: app3tpP9F3BrP1P7j (BQX ML V3)"
    echo ""
    echo "Then set it:"
    echo "   export AIRTABLE_API_KEY='your_key_here'"
    echo "   echo 'export AIRTABLE_API_KEY=\"your_key_here\"' >> ~/.bashrc"
    echo ""
else
    echo "✅ AIRTABLE_API_KEY found"
fi

# Create directories if needed
mkdir -p /home/micha/bqx_ml_v3/.claude/shared
mkdir -p /home/micha/bqx_ml_v3/.vscode

# Make scripts executable
chmod +x /home/micha/bqx_ml_v3/scripts/airtable_sync_service.py
chmod +x /home/micha/bqx_ml_v3/.claude/shared/airtable_multi_agent.py

# Test connection (if API key exists)
if [ -n "$AIRTABLE_API_KEY" ]; then
    echo ""
    echo "🔍 Testing AirTable connection..."
    python3 -c "
from pyairtable import Api
try:
    api = Api('$AIRTABLE_API_KEY')
    table = api.table('app3tpP9F3BrP1P7j', 'Tasks')
    count = len(table.all(max_records=1))
    print('✅ Connection successful!')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
fi

# Create agent-specific aliases
echo ""
echo "📝 Creating agent commands..."

cat > /tmp/airtable_aliases.sh << 'EOF'
# AirTable commands for all agents
alias at-next="python3 /home/micha/bqx_ml_v3/scripts/airtable_sync_service.py --next"
alias at-list="python3 /home/micha/bqx_ml_v3/scripts/airtable_sync_service.py --list"
alias at-status="python3 /home/micha/bqx_ml_v3/scripts/airtable_sync_service.py --status"
alias at-sync="python3 /home/micha/bqx_ml_v3/scripts/airtable_sync_service.py --sync"

# Agent-specific commands
alias ba-tasks="python3 /home/micha/bqx_ml_v3/.claude/shared/airtable_multi_agent.py BA"
alias ce-tasks="python3 /home/micha/bqx_ml_v3/.claude/shared/airtable_multi_agent.py CE"
EOF

echo "Aliases created in /tmp/airtable_aliases.sh"
echo "To use them, run: source /tmp/airtable_aliases.sh"

# Create quick test
echo ""
echo "📋 Available VSCode Tasks:"
echo "  - AirTable: Sync Tasks"
echo "  - AirTable: Get Next Task"
echo "  - AirTable: List Pending Tasks"
echo "  - AirTable: Project Status"
echo "  - AirTable: BA Tasks"
echo "  - AirTable: CE Team Status"
echo ""
echo "Run these from VSCode: Ctrl+Shift+P > Tasks: Run Task"

# Summary
echo ""
echo "✨ SETUP COMPLETE!"
echo "=================="
echo ""
echo "For ALL AGENTS (CE, BA, MA, TA):"
echo "  - Sync service: /scripts/airtable_sync_service.py"
echo "  - Multi-agent: /.claude/shared/airtable_multi_agent.py"
echo "  - VSCode tasks: /.vscode/airtable-tasks.json"
echo ""
echo "BA-specific guide: /.claude/sandbox/communications/shared/BA_airtable_integration.md"
echo ""

if [ -z "$AIRTABLE_API_KEY" ]; then
    echo "⚠️  Remember to set AIRTABLE_API_KEY before using!"
else
    echo "✅ Ready to use! Try: python3 scripts/airtable_sync_service.py --status"
fi