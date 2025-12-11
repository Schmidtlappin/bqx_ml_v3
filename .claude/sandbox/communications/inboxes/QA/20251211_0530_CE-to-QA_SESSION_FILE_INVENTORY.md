# CE Directive: Claude Code Session File Inventory & Archive

**Date**: December 11, 2025 05:30 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: **P1**
**Type**: Inventory & Cleanup

---

## DIRECTIVE SUMMARY

Inventory all Claude Code session files, identify active vs deprecated sessions, and archive old/unused sessions to a location OUTSIDE the Claude session directory.

---

## CURRENT STATE

| Metric | Value |
|--------|-------|
| Session directory | `~/.claude/projects/-home-micha-bqx-ml-v3/` |
| Total files | 249 |
| Agent sessions | 232 (`agent-*.jsonl`) |
| Main sessions | 17 (UUID format `.jsonl`) |
| Total size | 187 MB |

---

## TASK 1: INVENTORY

### Create Session Inventory

```bash
# List all sessions with size and date
ls -lhS ~/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl > /tmp/session_inventory.txt
```

### Categorize Sessions

| Category | Pattern | Criteria |
|----------|---------|----------|
| **ACTIVE** | Main sessions | Modified today (Dec 11) |
| **RECENT** | Any | Modified Dec 10-11 |
| **DEPRECATED** | `agent-*.jsonl` | Modified before Dec 10 |
| **STALE** | Any | Size = 0 bytes |

### CORRUPTED SESSIONS (MUST ARCHIVE)

These sessions have "thinking block" corruption and CANNOT be recovered:

| Session ID | Agent | Size | Status |
|------------|-------|------|--------|
| `72a1c1a7-c564-4ac8-974a-13ed0ce87dca` | QA (OLD) | 8.1 MB | **CORRUPTED - ARCHIVE** |
| `b959d344-c727-4cd9-9fe9-53d8e2dac32f` | BA (OLD) | 3.3 MB | **CORRUPTED - ARCHIVE** |

```bash
# Archive corrupted sessions
mv ~/.claude/projects/-home-micha-bqx-ml-v3/72a1c1a7-c564-4ac8-974a-13ed0ce87dca.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
mv ~/.claude/projects/-home-micha-bqx-ml-v3/b959d344-c727-4cd9-9fe9-53d8e2dac32f.jsonl \
   /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
```

### Active Sessions (DO NOT ARCHIVE)

| Session ID | Agent | Size |
|------------|-------|------|
| `b2360551-04af-4110-9cc8-cb1dce3334cc` | CE | 5.0 MB |
| `c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc` | EA | 2.3 MB |
| (NEW QA session) | QA | TBD |
| (NEW BA session) | BA | TBD |

---

## TASK 2: ARCHIVE DEPRECATED SESSIONS

### Archive Location (IMPORTANT)

**DO NOT archive to**: `~/.claude/` (affects dropdown menu)

**Archive TO**: `/home/micha/bqx_ml_v3/archive/claude_sessions_20251211/`

This location is:
- Inside the project workspace
- NOT read by Claude Code dropdown
- Part of regular backup scope

### Archive Commands

```bash
# Create archive directory
mkdir -p /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/

# Move deprecated agent sessions (before Dec 10)
find ~/.claude/projects/-home-micha-bqx-ml-v3/ -name "agent-*.jsonl" -mtime +1 \
  -exec mv {} /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/ \;

# Move empty sessions (0 bytes)
find ~/.claude/projects/-home-micha-bqx-ml-v3/ -name "*.jsonl" -size 0 \
  -exec mv {} /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/ \;
```

### Preserve Active Sessions

**DO NOT MOVE**:
- Any session modified today (Dec 11)
- Any session > 1 MB (likely active main session)
- Sessions in the "Known Active" table above

---

## TASK 3: CREATE MANIFEST

Create `/home/micha/bqx_ml_v3/archive/claude_sessions_20251211/MANIFEST.md`:

```markdown
# Archived Claude Code Sessions

**Archive Date**: December 11, 2025
**Archived By**: QA Agent
**Source**: ~/.claude/projects/-home-micha-bqx-ml-v3/

## Summary
- Total archived: X files
- Total size: X MB
- Criteria: Agent sessions before Dec 10, empty sessions

## Files Archived
[list of files with original timestamps]

## Active Sessions Preserved
[list of sessions NOT archived]
```

---

## TASK 4: VERIFY

After archive:

```bash
# Verify remaining sessions
ls -lh ~/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl | wc -l

# Verify archive
ls -lh /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/ | wc -l
```

Expected:
- Remaining: ~20-30 sessions (active + recent)
- Archived: ~220+ sessions

---

## CONSTRAINTS

| DO | DO NOT |
|----|--------|
| Archive `agent-*.jsonl` older than Dec 10 | Delete any session files |
| Archive 0-byte sessions | Archive sessions > 1 MB |
| Create manifest | Archive today's sessions |
| Move to project archive | Archive to `~/.claude/` subdirectory |

---

## DELIVERABLES

1. **Session inventory** - Complete list with categorization
2. **Archive manifest** - `archive/claude_sessions_20251211/MANIFEST.md`
3. **Cleanup report** - Before/after counts and sizes
4. **Verification** - Confirm dropdown still works

---

## REPORT FORMAT

```markdown
## QA Session Cleanup Report

**Date**: [timestamp]

### Before
- Total sessions: 249
- Total size: 187 MB

### After
- Remaining sessions: X
- Remaining size: X MB
- Archived sessions: X
- Archived size: X MB

### Active Sessions Preserved
| Session ID | Agent | Size | Modified |
|------------|-------|------|----------|
| ... | ... | ... | ... |

### Verification
- [ ] Dropdown menu functional
- [ ] Active sessions accessible
- [ ] Archive manifest created
```

---

**Chief Engineer (CE)**
