# QA Session Handoff (Context Recovery)

**Date**: December 11, 2025 05:35 UTC
**Purpose**: Resume QA session after context limit corruption

---

## ONBOARDING SEQUENCE (REQUIRED)

**You are QA - Quality Assurance Agent for BQX ML V3 project.**

### Step 1: Ingest Intelligence Files (READ ALL)
```
/intelligence/context.json        # Project context and current state
/intelligence/ontology.json       # Data model and entity definitions
/intelligence/roadmap_v2.json     # Current roadmap and milestones
/intelligence/semantics.json      # Feature semantics and naming
/intelligence/feature_catalogue.json  # Feature inventory
```

### Step 2: Ingest Mandate Files (READ ALL)
```
/mandate/README.md                # Project mandate overview
/mandate/BQX_ML_V3_FEATURE_INVENTORY.md  # Feature coverage requirements
/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md  # Feature tracking mandate
```

### Step 3: Ingest Agent-Specific Files (READ ALL)
```
/.claude/sandbox/communications/shared/QA_TODO.md           # Your current tasks
/.claude/sandbox/communications/shared/AGENT_ONBOARDING_PROMPTS.md  # Role definition
/.claude/sandbox/communications/inboxes/QA/                 # Your inbox (recent .md files)
```

### Step 4: Read This Handoff Context Below

---

## CURRENT TASKS

### P1: Claude Session File Inventory & Archive (NEW - PRIORITY)

**CE DIRECTIVE**: `inboxes/QA/20251211_0530_CE-to-QA_SESSION_FILE_INVENTORY.md`

| Task | Status |
|------|--------|
| Inventory all session files | PENDING |
| Identify active vs deprecated | PENDING |
| Archive deprecated sessions | PENDING |
| Create archive manifest | PENDING |
| Verify dropdown still works | PENDING |

**Session Directory**: `~/.claude/projects/-home-micha-bqx-ml-v3/`
- Total files: 249
- Agent sessions: 232 (`agent-*.jsonl`)
- Total size: 187 MB

**CRITICAL**: Archive to `/home/micha/bqx_ml_v3/archive/claude_sessions_20251211/` NOT `~/.claude/`

**CORRUPTED SESSIONS (MUST ARCHIVE)**:
| Session ID | Agent | Size | Status |
|------------|-------|------|--------|
| `72a1c1a7-c564-4ac8-974a-13ed0ce87dca` | QA (OLD) | 8.1 MB | **CORRUPTED** |
| `b959d344-c727-4cd9-9fe9-53d8e2dac32f` | BA (OLD) | 3.3 MB | **CORRUPTED** |

**Active Sessions (DO NOT ARCHIVE)**:
| Session ID | Agent | Size |
|------------|-------|------|
| `b2360551-04af-4110-9cc8-cb1dce3334cc` | CE | 5.0 MB |
| `c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc` | EA | 2.3 MB |

**Archive Criteria**:
- Archive: `agent-*.jsonl` modified before Dec 10
- Archive: Any 0-byte sessions
- KEEP: Sessions modified Dec 10-11
- KEEP: Sessions > 1 MB

### P0: Step 6 Monitoring & Audit

**CE DIRECTIVE**: `inboxes/QA/20251211_0450_CE-to-QA_STEP6_AUDIT_DIRECTIVE.md`

| Task | Status |
|------|--------|
| Monitor Step 6 process | ACTIVE |
| Audit EURUSD data | PENDING (when complete) |
| Verify feature coverage | PENDING (per pair) |

**Current Process**:
- PID: 1312752
- Mode: SEQUENTIAL + CHECKPOINT (16 workers)
- Log: `logs/step6_sequential_*.log`

### P2: Documentation Review (After EA Cleanup)

**CE DIRECTIVE**: `inboxes/QA/20251211_0525_CE-to-QA_DOCUMENTATION_REVIEW.md`

Validate intelligence and mandate files after EA workspace cleanup.

---

## USER MANDATES (BINDING)

1. **Sequential pairs**: All workers on ONE pair at a time
2. **Checkpoint/resume**: Parquet files per table
3. **16 workers per pair**: Approved optimization

---

## COMMANDS

```bash
# Check Step 6 progress
tail -20 /home/micha/bqx_ml_v3/logs/step6_sequential_*.log

# Check process status
ps -p 1312752 -o pid,rss,%mem,%cpu --no-headers

# List session files
ls -lhS ~/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl | head -20

# Archive deprecated sessions
mkdir -p /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/
find ~/.claude/projects/-home-micha-bqx-ml-v3/ -name "agent-*.jsonl" -mtime +1 \
  -exec mv {} /home/micha/bqx_ml_v3/archive/claude_sessions_20251211/ \;
```

---

## REPORT TO CE

After completing tasks, send report to:
`/.claude/sandbox/communications/inboxes/CE/[timestamp]_QA-to-CE_[TOPIC].md`

---

**To resume**: Start new session, paste onboarding prompt, read this file, continue tasks.
