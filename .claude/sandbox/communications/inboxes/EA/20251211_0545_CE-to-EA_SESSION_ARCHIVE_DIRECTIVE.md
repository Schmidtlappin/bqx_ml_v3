# CE Directive: Archive All Non-Active Claude Sessions

**Date**: December 11, 2025 05:45 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **P0 - IMMEDIATE**
**Type**: Session Cleanup

---

## PROBLEM

The Claude Code session dropdown shows **249 files** but only **4 sessions are active**. This clutters the UI and confuses session selection.

---

## ROOT CAUSE

All `.jsonl` files in `~/.claude/projects/-home-micha-bqx-ml-v3/` appear in the dropdown menu.

Currently:
- 232 `agent-*.jsonl` files (subagent artifacts - NOT user sessions)
- 17 main session files (UUID format)
- Only 4 are actually active

---

## ACTIVE SESSIONS (DO NOT TOUCH)

| Session ID | Agent | Size | Status |
|------------|-------|------|--------|
| `b2360551-04af-4110-9cc8-cb1dce3334cc` | CE | 5.0 MB | **ACTIVE** |
| `c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc` | EA | 2.3 MB | **ACTIVE** |

Note: BA and QA sessions are corrupted and will be recreated. New session IDs will be assigned when they start.

---

## SESSIONS TO ARCHIVE

### Category 1: Corrupted Main Sessions
```bash
# These MUST be archived (thinking block corruption)
mv ~/.claude/projects/-home-micha-bqx-ml-v3/72a1c1a7-c564-4ac8-974a-13ed0ce87dca.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
mv ~/.claude/projects/-home-micha-bqx-ml-v3/b959d344-c727-4cd9-9fe9-53d8e2dac32f.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
```

### Category 2: ALL agent-*.jsonl Files
```bash
# These are subagent artifacts, NOT user-selectable sessions
# Moving them removes them from dropdown
mkdir -p /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/agents/
mv ~/.claude/projects/-home-micha-bqx-ml-v3/agent-*.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/agents/
```

### Category 3: Empty/Stale Sessions
```bash
# 0-byte files are stale/abandoned
find ~/.claude/projects/-home-micha-bqx-ml-v3/ -name "*.jsonl" -size 0 \
  -exec mv {} /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/ \;
```

### Category 4: Old Main Sessions (before Dec 10)
```bash
# Archive any remaining old main sessions EXCEPT the two active ones
cd ~/.claude/projects/-home-micha-bqx-ml-v3/
for f in *.jsonl; do
  # Skip active sessions
  if [[ "$f" == "b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl" ]] || \
     [[ "$f" == "c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc.jsonl" ]]; then
    continue
  fi
  # Skip agent files (already moved)
  if [[ "$f" == agent-* ]]; then
    continue
  fi
  # Move if older than Dec 10
  if [[ $(stat -c %Y "$f") -lt $(date -d "2025-12-10" +%s) ]]; then
    mv "$f" /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
  fi
done
```

---

## EXPECTED RESULT

### Before
```
~/.claude/projects/-home-micha-bqx-ml-v3/
├── 249 .jsonl files
└── Dropdown shows 249 options (confusing)
```

### After
```
~/.claude/projects/-home-micha-bqx-ml-v3/
├── b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl (CE)
├── c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc.jsonl (EA)
└── (2-4 files total, dropdown shows only active sessions)

/home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
├── agents/           (232 agent-*.jsonl files)
├── corrupted/        (2 files: old QA, old BA)
└── stale/            (remaining old sessions)
```

---

## SIMPLIFIED COMMANDS (RECOMMENDED)

Run these in order:

```bash
# 1. Create archive directories
mkdir -p /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/{agents,corrupted,stale}

# 2. Archive corrupted sessions
mv ~/.claude/projects/-home-micha-bqx-ml-v3/72a1c1a7-c564-4ac8-974a-13ed0ce87dca.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/corrupted/
mv ~/.claude/projects/-home-micha-bqx-ml-v3/b959d344-c727-4cd9-9fe9-53d8e2dac32f.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/corrupted/

# 3. Archive ALL agent-*.jsonl files (removes them from dropdown)
mv ~/.claude/projects/-home-micha-bqx-ml-v3/agent-*.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/agents/

# 4. Archive 0-byte files
find ~/.claude/projects/-home-micha-bqx-ml-v3/ -name "*.jsonl" -size 0 \
  -exec mv {} /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/stale/ \;

# 5. Archive remaining old sessions (keep only CE and EA)
cd ~/.claude/projects/-home-micha-bqx-ml-v3/
for f in *.jsonl; do
  case "$f" in
    b2360551-*|c31dd28b-*) continue ;;  # Keep CE and EA
    *) mv "$f" /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/stale/ ;;
  esac
done
```

---

## VERIFICATION

After running:
```bash
# Should show only 2 files (CE and EA)
ls ~/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl

# Expected output:
# b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl
# c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc.jsonl
```

---

## WHY THIS WORKS

1. **Dropdown reads from `~/.claude/projects/{project}/`** - moving files OUT removes them from dropdown
2. **Archive location is in project workspace** - NOT in `~/.claude/`, so it won't affect Claude Code
3. **Files are preserved** - can be restored if needed
4. **New BA/QA sessions** - will create NEW .jsonl files when those agents start fresh sessions

---

## REPORT REQUIRED

After completion, report:
1. Files remaining in session directory (should be 2)
2. Files archived (count per category)
3. Dropdown verification (confirm only 2 sessions visible)

---

**Chief Engineer (CE)**
