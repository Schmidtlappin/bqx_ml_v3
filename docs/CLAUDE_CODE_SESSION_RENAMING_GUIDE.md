# Claude Code Session Renaming Guide

**Date:** 2025-12-11
**Purpose:** Guide for renaming sessions in VS Code Claude Code dropdown menu
**Applies To:** Claude Code VS Code Extension v2.0.46+

## Problem Overview

Sessions created programmatically (via Task tool or agent spawning) may not appear in the Claude Code "Past Conversations" dropdown, or may display incorrect names derived from the first user prompt instead of the intended agent/session name.

## How the Dropdown Works

The VS Code Claude Code extension populates the dropdown menu using:

1. **Session Location**: Only shows sessions from the current workspace's project directory
   - Path pattern: `/home/micha/.claude/projects/-home-micha-[workspace]/`
   - Example: `/home/micha/.claude/projects/-home-micha-bqx-ml-v3/`

2. **Session Name Source**: Uses the **first user message text** in the session
   - NOT the `enqueue` event (added but not used for display)
   - NOT the session ID or file name
   - Skips `<ide_opened_file>` notifications to find actual text

3. **Session File Format**: `.jsonl` files with session UUID as filename
   - Example: `b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl`

## Common Issues

### Issue 1: Session Not in Dropdown
**Symptom**: Session file exists but doesn't appear in dropdown

**Causes**:
- Session in wrong project directory (different workspace)
- Missing initial `enqueue` event
- Corrupted session file

**Solution**: Verify location and add enqueue event (see below)

### Issue 2: Wrong Session Name Displayed
**Symptom**: Dropdown shows "check messages" or other wrong text instead of agent name

**Cause**: First user message contains generic text or command

**Solution**: Update first user message (see below)

## Solution: Rename Session in Dropdown

### Prerequisites

```bash
# Verify session file exists
ls -lh /home/micha/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl

# Identify session ID from AGENT_REGISTRY.json or recent activity
cat /home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json
```

### Method 1: Add Enqueue Event (Initial Setup)

This adds a title event at the beginning of the session file. **Note:** This is supplementary; the dropdown uses the first user message.

```python
#!/usr/bin/env python3
import json
import sys

def add_enqueue_event(session_file, title, session_id):
    """Add enqueue event with title to beginning of session file."""

    # Create the enqueue event
    enqueue_event = {
        "type": "queue-operation",
        "operation": "enqueue",
        "timestamp": "2025-12-10T21:49:49.000Z",
        "content": [{"type": "text", "text": title}],
        "sessionId": session_id
    }

    # Read existing content
    with open(session_file, 'r') as f:
        lines = f.readlines()

    # Write enqueue first, then existing content
    with open(session_file, 'w') as f:
        f.write(json.dumps(enqueue_event) + '\n')
        f.writelines(lines)

    print(f"✓ Added enqueue event '{title}' to {session_file}")

# Usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 add_enqueue.py <session_file> <title> <session_id>")
        sys.exit(1)

    add_enqueue_event(sys.argv[1], sys.argv[2], sys.argv[3])
```

**Example Usage:**
```bash
python3 add_enqueue.py \
  /home/micha/.claude/projects/-home-micha-bqx-ml-v3/b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl \
  "CE - Chief Engineer" \
  "b2360551-04af-4110-9cc8-cb1dce3334cc"
```

### Method 2: Update First User Message (Dropdown Name)

This updates the actual text that appears in the dropdown menu.

```python
#!/usr/bin/env python3
import json
import sys

def update_first_user_message(session_file, new_title):
    """Update the first user message text in session file."""

    lines = []
    fixed = False

    with open(session_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                if not fixed and event.get('type') == 'user':
                    content = event.get('message', {}).get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            # Skip ide_opened_file notifications
                            if not text.startswith('<ide_opened_file>'):
                                # Found first actual user text - replace it
                                item['text'] = new_title
                                fixed = True
                                break
                    if fixed:
                        line = json.dumps(event) + '\n'
            except:
                pass
            lines.append(line)

    if fixed:
        with open(session_file, 'w') as f:
            f.writelines(lines)
        print(f"✓ Updated first user message to: {new_title}")
        return True
    else:
        print("✗ No user message found to update")
        return False

# Usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 update_first_message.py <session_file> <new_title>")
        sys.exit(1)

    update_first_user_message(sys.argv[1], sys.argv[2])
```

**Example Usage:**
```bash
python3 update_first_message.py \
  /home/micha/.claude/projects/-home-micha-bqx-ml-v3/fb3ed231-0c68-4195-a3bf-800f659121bc.jsonl \
  "QA - Quality Assurance"
```

### Method 3: Batch Rename All Agent Sessions

```bash
#!/bin/bash
# Batch rename all 4 agent sessions

PROJECT_DIR="/home/micha/.claude/projects/-home-micha-bqx-ml-v3"

# Agent sessions from AGENT_REGISTRY.json
declare -A AGENTS=(
  ["b2360551-04af-4110-9cc8-cb1dce3334cc"]="CE - Chief Engineer"
  ["df480dab-e189-46d8-be49-b60b436c2a3e"]="BA - Build Agent"
  ["fb3ed231-0c68-4195-a3bf-800f659121bc"]="QA - Quality Assurance"
  ["05c73962-b9f1-4e06-9a5a-a5ae556cae5a"]="EA - Enhancement Assistant"
)

for session_id in "${!AGENTS[@]}"; do
  title="${AGENTS[$session_id]}"
  file="$PROJECT_DIR/$session_id.jsonl"

  if [ -f "$file" ]; then
    echo "Updating $session_id → $title"
    python3 update_first_message.py "$file" "$title"
  else
    echo "⚠ File not found: $file"
  fi
done

echo ""
echo "✓ Batch rename complete. Reload VS Code window to see changes."
```

## Verification

### Check Current Session Names

```python
#!/usr/bin/env python3
import json
import os
import glob

def get_session_title(session_file):
    """Extract the first user message text from session."""
    try:
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get('type') == 'user':
                        content = event.get('message', {}).get('content', [])
                        for item in content:
                            if item.get('type') == 'text':
                                text = item.get('text', '')
                                if not text.startswith('<ide_opened_file>'):
                                    return text[:50]  # First 50 chars
                except:
                    continue
    except:
        pass
    return "No user message found"

# Check all sessions
project_dir = "/home/micha/.claude/projects/-home-micha-bqx-ml-v3"
sessions = glob.glob(f"{project_dir}/*.jsonl")

print(f"Found {len(sessions)} sessions:\n")
for session_file in sorted(sessions):
    session_id = os.path.basename(session_file).replace('.jsonl', '')
    title = get_session_title(session_file)
    size_mb = os.path.getsize(session_file) / (1024 * 1024)
    print(f"{session_id[:8]}... → {title} ({size_mb:.1f}M)")
```

### Check Agent Registry Sessions

```bash
# Extract session IDs from AGENT_REGISTRY.json
jq -r '.agent_registry | to_entries[] |
  select(.value.current_session_id != null) |
  "\(.key): \(.value.current_session_id) - \(.value.full_name)"' \
  /home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json
```

## After Renaming

1. **Reload VS Code Window**:
   - Press `Cmd/Ctrl + Shift + P`
   - Type "Developer: Reload Window"
   - Press Enter

2. **Verify Dropdown**:
   - Open Claude Code panel
   - Click conversation dropdown
   - Confirm all agents show correct names:
     - CE - Chief Engineer
     - BA - Build Agent
     - QA - Quality Assurance
     - EA - Enhancement Assistant

## Session File Structure

### Key Events in Session File

```jsonl
{"type":"queue-operation","operation":"enqueue","content":[{"type":"text","text":"CE - Chief Engineer"}],"sessionId":"..."}
{"type":"queue-operation","operation":"dequeue","timestamp":"...","sessionId":"..."}
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"CE - Chief Engineer"}]},"uuid":"..."}
{"type":"assistant","message":{"role":"assistant","content":[...]},"uuid":"..."}
...
```

**Important Fields**:
- `type: "queue-operation"` - Session lifecycle events (enqueue/dequeue)
- `type: "user"` - User messages (dropdown uses first one)
- `type: "assistant"` - Assistant responses
- `content[].text` - The actual message text
- `sessionId` - UUID for this session
- `cwd` - Working directory (determines project folder)

## Troubleshooting

### Sessions Still Not Appearing

1. **Check workspace**:
   ```bash
   # Current workspace
   pwd
   # Expected: /home/micha/bqx_ml_v3

   # Session directory should match
   ls -la /home/micha/.claude/projects/-home-micha-bqx-ml-v3/
   ```

2. **Check session cwd field**:
   ```bash
   grep -m1 '"cwd":' session.jsonl | jq -r '.cwd'
   # Should match current workspace
   ```

3. **Move session to correct directory**:
   ```bash
   # If session is in wrong workspace directory
   mv /home/micha/.claude/projects/-home-micha/session.jsonl \
      /home/micha/.claude/projects/-home-micha-bqx-ml-v3/
   ```

### Dropdown Shows Old Name

1. **Clear VS Code cache**:
   - Close VS Code completely
   - Delete: `/home/micha/.vscode-server/data/User/workspaceStorage/*/`
   - Restart VS Code

2. **Verify first user message actually changed**:
   ```bash
   grep -m1 '"type":"user"' session.jsonl | \
     jq -r '.message.content[] | select(.type=="text") | .text'
   ```

### Session File Corrupted

1. **Validate JSON**:
   ```bash
   # Check each line is valid JSON
   while IFS= read -r line; do
     echo "$line" | jq . > /dev/null || echo "Invalid JSON: $line"
   done < session.jsonl
   ```

2. **Restore from backup** (if available):
   ```bash
   # Check for backups
   ls -la /home/micha/bqx_ml_v3/archive/*session*
   ```

## Reference

### Agent Registry Location
```
/home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json
```

### Session Locations by Workspace

| Workspace | Project Directory |
|-----------|-------------------|
| `/home/micha` | `/home/micha/.claude/projects/-home-micha/` |
| `/home/micha/bqx_ml_v3` | `/home/micha/.claude/projects/-home-micha-bqx-ml-v3/` |

### Todo Files Location
```
/home/micha/.claude/todos/<session-id>-agent-<session-id>.json
```

## Scripts Storage

Save the Python scripts to:
```
/home/micha/bqx_ml_v3/scripts/claude_code_session_tools/
├── add_enqueue_event.py
├── update_first_message.py
├── verify_session_names.py
└── batch_rename_agents.sh
```

## Related Documentation

- [AGENT_ONBOARDING_PROTOCOL.md](/home/micha/bqx_ml_v3/mandate/AGENT_ONBOARDING_PROTOCOL.md)
- [AGENT_REGISTRY.json](/home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json)
- Claude Code Documentation: https://code.claude.com/docs

---

**Last Updated:** 2025-12-11
**Maintained By:** Chief Engineer
**Version:** 1.0
