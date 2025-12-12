# Claude Code Session Tools

**Purpose:** Utilities for managing Claude Code session names in VS Code dropdown menu

## Quick Start

### Rename All Agent Sessions
```bash
./batch_rename_agents.sh
```

### Verify Current Session Names
```bash
python3 verify_session_names.py
```

### Update Single Session
```bash
python3 update_first_message.py \
  /home/micha/.claude/projects/-home-micha-bqx-ml-v3/SESSION_ID.jsonl \
  "New Session Name"
```

## Scripts

### 1. batch_rename_agents.sh
**Purpose:** Automatically rename all agent sessions from AGENT_REGISTRY.json

**Usage:**
```bash
./batch_rename_agents.sh
```

**What it does:**
- Reads current session IDs from AGENT_REGISTRY.json
- Updates first user message in each session file
- Sets proper names: "CE - Chief Engineer", "BA - Build Agent", etc.

**Requirements:**
- jq (JSON processor)
- Python 3
- update_first_message.py in same directory

---

### 2. update_first_message.py
**Purpose:** Update the first user message in a session (sets dropdown name)

**Usage:**
```bash
python3 update_first_message.py <session_file> <new_title>
```

**Example:**
```bash
python3 update_first_message.py \
  /home/micha/.claude/projects/-home-micha-bqx-ml-v3/fb3ed231-0c68-4195-a3bf-800f659121bc.jsonl \
  "QA - Quality Assurance"
```

**Returns:**
- Exit code 0 on success
- Exit code 1 if no user message found

---

### 3. add_enqueue_event.py
**Purpose:** Add enqueue event to beginning of session file

**Usage:**
```bash
python3 add_enqueue_event.py <session_file> <title> <session_id>
```

**Example:**
```bash
python3 add_enqueue_event.py \
  /home/micha/.claude/projects/-home-micha-bqx-ml-v3/b2360551.jsonl \
  "CE - Chief Engineer" \
  "b2360551-04af-4110-9cc8-cb1dce3334cc"
```

**Note:** This is supplementary; the dropdown primarily uses the first user message.

---

### 4. verify_session_names.py
**Purpose:** Check what names appear in dropdown for all sessions

**Usage:**
```bash
# Default directory (bqx_ml_v3 project)
python3 verify_session_names.py

# Custom directory
python3 verify_session_names.py /home/micha/.claude/projects/-home-micha-bqx-ml-v3
```

**Output:**
```
Found 4 main session(s) in -home-micha-bqx-ml-v3:

Session ID                               Name                                               Size
----------------------------------------------------------------------------------------------------
b2360551-04af-4110-9cc8-cb1dce3334cc     CE - Chief Engineer                                 8.3M
df480dab-e189-46d8-be49-b60b436c2a3e     BA - Build Agent                                    2.3M
fb3ed231-0c68-4195-a3bf-800f659121bc     QA - Quality Assurance                              1.9M
05c73962-b9f1-4e06-9a5a-a5ae556cae5a     EA - Enhancement Assistant                          0.4M
```

## Common Tasks

### Fix Wrong Session Name in Dropdown
```bash
# 1. Find session file
ls -lh /home/micha/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl

# 2. Update first message
python3 update_first_message.py /path/to/session.jsonl "Correct Name"

# 3. Reload VS Code window (Cmd/Ctrl + Shift + P → "Reload Window")
```

### Rename All Agents at Once
```bash
# Updates CE, BA, QA, EA sessions automatically
./batch_rename_agents.sh

# Then reload VS Code
```

### Check Session Names Before/After Changes
```bash
# Before
python3 verify_session_names.py

# Make changes...

# After
python3 verify_session_names.py
```

## File Locations

### Session Files
```
/home/micha/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl
```

### Agent Registry
```
/home/micha/bqx_ml_v3/.claude/sandbox/communications/AGENT_REGISTRY.json
```

### Todo Files
```
/home/micha/.claude/todos/<session-id>-agent-<session-id>.json
```

## Troubleshooting

### Sessions Not Appearing in Dropdown

**Problem:** Session file exists but doesn't show in dropdown

**Solutions:**
1. Check if session is in correct workspace directory
2. Verify first user message exists (use verify_session_names.py)
3. Reload VS Code window

### Dropdown Shows Wrong Name

**Problem:** Dropdown shows "check messages" or generic text

**Solution:**
```bash
python3 update_first_message.py session.jsonl "Correct Name"
```

### Script Can't Find Session

**Problem:** "File not found" error

**Check:**
1. Session ID is correct (check AGENT_REGISTRY.json)
2. Session file exists in project directory
3. Using absolute path to session file

## Documentation

Full documentation: [/docs/CLAUDE_CODE_SESSION_RENAMING_GUIDE.md](../../docs/CLAUDE_CODE_SESSION_RENAMING_GUIDE.md)

## Version
- **Created:** 2025-12-11
- **Version:** 1.0
- **Maintained By:** Chief Engineer
