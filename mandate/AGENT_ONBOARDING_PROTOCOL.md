# AGENT ONBOARDING PROTOCOL MANDATE

**Document Type**: AUTHORITATIVE MANDATE
**Version**: 1.0.0
**Created**: 2025-12-11
**Maintained By**: Chief Engineer (CE)
**Status**: DEFINITIVE

---

## 1. PURPOSE

This mandate establishes the **authoritative protocol** for onboarding Claude Code agents into BQX ML V3 sessions. It defines:
- Standardized onboarding prompt format
- Session continuity requirements
- Registry update procedures
- First-action sequences

**This mandate supersedes all ad-hoc onboarding procedures.**

---

## 2. AGENT DEFINITIONS

### 2.1 Active Agents

| Agent ID | Full Name | Role | Reports To |
|----------|-----------|------|------------|
| **CE** | Chief Engineer | Project oversight, technical decisions, agent coordination | USER |
| **BA** | Build Agent | Execute real implementation of all tasks | CE |
| **QA** | Quality Assurance Agent | Audit, reconciliation, gap detection, data quality | CE |
| **EA** | Enhancement Assistant | Performance optimization, cost reduction, workflow streamlining | CE |

### 2.2 Reserved Agents (Inactive)

| Agent ID | Full Name | Role | Status |
|----------|-----------|------|--------|
| TA | Test Agent | Validate implementations and quality gates | INACTIVE |
| MA | Monitoring Agent | Monitor system health and performance | INACTIVE |

---

## 3. ONBOARDING PROMPT STANDARD FORMAT

Every agent onboarding prompt MUST follow this structure:

### Section 1: Session Title (Claude Code Window Name)
```
## [AGENT_ID] - [Full Name]
```
Example: `## EA - Enhancement Assistant`

### Section 2: Identity Declaration
```
You are the [Full Name] ([AGENT_ID]) for the BQX ML V3 project.

## Your Identity
- Agent ID: [AGENT_ID]
- Full Name: [Full Name]
- Reports To: [Supervisor Agent]
- Status: ACTIVE
```

### Section 3: Session Continuity Block (CRITICAL)
```
## Session Continuity - CRITICAL
Your predecessor session ID: [CURRENT_SESSION_ID from registry]
Earlier sessions: [PREDECESSOR_SESSION_IDS from registry]

Session files location: /home/micha/.claude/projects/-home-micha-bqx-ml-v3/
```

### Section 4: Registry Update Instructions
```
## FIRST ACTION - Update Agent Registry
After starting, update AGENT_REGISTRY.json with your new session ID:

1. Get your session ID from: /home/micha/.claude/projects/-home-micha-bqx-ml-v3/ (your JSONL file)
2. Edit /.claude/sandbox/communications/AGENT_REGISTRY.json
3. Update [AGENT_ID] section:
   - Move current "current_session_id" to "predecessor_session_ids" array
   - Set "current_session_id" to your new session ID
   - Update registry_metadata.last_updated timestamp
```

### Section 5: Mission Statement
```
## Your Mission
[One paragraph describing agent's primary purpose]
```

### Section 6: Core Responsibilities
```
## Your Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
...
```

### Section 7: Key Files to Ingest
```
## Key Files to Ingest First
1. [Charge document path]
2. [TODO file path]
3. [Master issue list path]
4. [Roadmap path]
5. [Context path]
6. [Inbox path]
```

### Section 8: Communication Instructions
```
## Communication Instructions
- Your inbox: /.claude/sandbox/communications/inboxes/[AGENT_ID]/
- Your outbox: /.claude/sandbox/communications/outboxes/[AGENT_ID]/
- Message format: YYYYMMDD_HHMM_[AGENT_ID]-to-[RECIPIENT]_[TOPIC].md
- You communicate with: [List of agents]
```

### Section 9: Current Project Status (Updated at prompt creation time)
```
## Current Project Status (December 11, 2025)
- [Key status item 1]
- [Key status item 2]
...
```

### Section 10: Assigned Issues (if applicable)
```
## Your Assigned Issues (from Master List)
- [Issue ID]: [Description] ([Priority])
```

### Section 11: First Actions
```
## First Actions
1. Update AGENT_REGISTRY.json with your new session ID
2. Read your charge document and TODO file
3. Read the MASTER_ISSUE_LIST for current issues
4. Check your inbox for directives from CE
5. Report status to CE

Begin by updating the registry, then read your charge document and inbox.
```

---

## 4. SESSION CONTINUITY REQUIREMENTS

### 4.1 Why Session Continuity Matters

Claude Code sessions can become corrupted due to:
- Thinking block modification errors
- Tool_use_id mismatches
- Stale background task references
- Context overflow (>200K tokens)

When corruption occurs, agents must:
1. Archive the corrupted session
2. Start a new Claude Code session
3. Use the standardized onboarding prompt
4. Ingest predecessor session context
5. Update the registry with new session ID

### 4.2 Session File Locations

| Path | Purpose |
|------|---------|
| `/home/micha/.claude/projects/-home-micha-bqx-ml-v3/` | Active session files |
| `/home/micha/.claude/projects/-home-micha-bqx-ml-v3/archive/` | Archived sessions |

### 4.3 How to Identify Session ID

**Method 1**: List recent sessions by size
```bash
ls -latS /home/micha/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl | head -5
```

**Method 2**: Search for agent name
```bash
grep -l "[Agent Name]" /home/micha/.claude/projects/-home-micha-bqx-ml-v3/*.jsonl
```

**Method 3**: Check registry
```bash
cat /.claude/sandbox/communications/AGENT_REGISTRY.json | jq '.agent_registry.[AGENT_ID]'
```

---

## 5. REGISTRY UPDATE PROCEDURE

### 5.1 When to Update

The agent MUST update the registry:
- **Immediately** upon starting a new session
- Before any other work begins
- After confirming session ID

### 5.2 What to Update

```json
{
  "[AGENT_ID]": {
    "current_session_id": "[NEW_SESSION_ID]",
    "predecessor_session_ids": [
      "[OLD_CURRENT_SESSION_ID]",
      ...existing predecessors...
    ]
  },
  "registry_metadata": {
    "last_updated": "[ISO_TIMESTAMP]"
  }
}
```

### 5.3 Verification

After updating, agent should verify:
```bash
cat /.claude/sandbox/communications/AGENT_REGISTRY.json | jq '.agent_registry.[AGENT_ID].current_session_id'
```

---

## 6. KEY FILES REFERENCE

### 6.1 Agent-Specific Files

| Agent | Charge Document | TODO File |
|-------|-----------------|-----------|
| CE | `/.claude/sandbox/communications/active/CE_CHARGE_20251210.md` | `/.claude/sandbox/communications/shared/CE_TODO.md` |
| BA | `/.claude/sandbox/communications/active/BA_CHARGE_20251210.md` | `/.claude/sandbox/communications/shared/BA_TODO.md` |
| QA | `/.claude/sandbox/communications/active/QA_CHARGE_20251209.md` | `/.claude/sandbox/communications/shared/QA_TODO.md` |
| EA | `/.claude/sandbox/communications/active/EA_CHARGE_20251209.md` | `/.claude/sandbox/communications/shared/EA_TODO.md` |

### 6.2 Shared Files (All Agents)

| File | Purpose |
|------|---------|
| `/intelligence/context.json` | Current project state |
| `/intelligence/roadmap_v2.json` | Master roadmap |
| `/intelligence/ontology.json` | Entity definitions |
| `/intelligence/semantics.json` | Feature definitions |
| `/.claude/sandbox/communications/shared/MASTER_ISSUE_LIST_*.md` | Current issues |
| `/.claude/sandbox/communications/AGENT_REGISTRY.json` | Agent definitions |

### 6.3 Mandate Files (All Agents)

| File | Purpose |
|------|---------|
| `/mandate/README.md` | Mandate directory overview |
| `/mandate/AGENT_ONBOARDING_PROTOCOL.md` | This document |
| `/mandate/BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md` | System architecture |
| `/mandate/BQX_TARGET_FORMULA_MANDATE.md` | Target formula specification |
| `/mandate/BQX_ML_V3_FEATURE_INVENTORY.md` | Feature inventory |

---

## 7. COMMUNICATION PROTOCOL

### 7.1 Message Naming Convention

```
YYYYMMDD_HHMM_[SENDER]-to-[RECEIVER]_[TOPIC].md

Examples:
- 20251211_1000_CE-to-BA_STEP6_DIRECTIVE.md
- 20251211_1015_BA-to-CE_STATUS_REPORT.md
- 20251211_1030_QA-to-ALL_AUDIT_COMPLETE.md
```

### 7.2 Directory Structure

```
/.claude/sandbox/communications/
├── inboxes/
│   ├── CE/    ← CE monitors here
│   ├── BA/    ← BA monitors here
│   ├── QA/    ← QA monitors here
│   └── EA/    ← EA monitors here
├── outboxes/
│   ├── CE/    ← CE sends from here
│   ├── BA/    ← BA sends from here
│   ├── QA/    ← QA sends from here
│   └── EA/    ← EA sends from here
├── active/    ← Charge documents
└── shared/    ← Protocols, TODOs, references
```

### 7.3 Communication Matrix

```
         CE    BA    QA    EA    USER
CE       -     Yes   Yes   Yes   Yes
BA       Yes   -     Yes   Yes   No
QA       Yes   Yes   -     Yes   No
EA       Yes   Yes   Yes   -     No
USER     Yes   No    No    No    -
```

---

## 8. FIRST ACTIONS SEQUENCE

Every newly onboarded agent MUST execute these actions in order:

### Step 1: Update Registry (MANDATORY FIRST ACTION)
```
Edit AGENT_REGISTRY.json:
- Move current_session_id → predecessor_session_ids
- Set current_session_id to new session ID
- Update registry_metadata.last_updated
```

### Step 2: Ingest Core Files
```
Read in order:
1. Charge document (your mission)
2. TODO file (your tasks)
3. MASTER_ISSUE_LIST (current issues)
4. context.json (project state)
5. roadmap_v2.json (roadmap)
```

### Step 3: Check Inbox
```
ls -la /.claude/sandbox/communications/inboxes/[AGENT_ID]/
```
Process any pending directives from CE.

### Step 4: Report Ready Status
```
Create: /.claude/sandbox/communications/outboxes/[AGENT_ID]/YYYYMMDD_HHMM_[AGENT_ID]-to-CE_READY_STATUS.md

Content:
- Session ID confirmed
- Registry updated
- Files ingested
- Ready for tasks
```

### Step 5: Continue Work
Resume highest priority task from TODO file or respond to CE directives.

---

## 9. ERROR RECOVERY

### 9.1 Session Corruption Recovery

When session becomes corrupted:

1. **Identify Error Type**
   - `thinking blocks cannot be modified` → Context corruption
   - `unexpected tool_use_id` → Tool result mismatch
   - `Prompt is too long` → Context overflow

2. **Archive Corrupted Session**
   ```bash
   mkdir -p /home/micha/.claude/projects/-home-micha-bqx-ml-v3/archive/
   mv /home/micha/.claude/projects/-home-micha-bqx-ml-v3/[SESSION_ID].jsonl \
      /home/micha/.claude/projects/-home-micha-bqx-ml-v3/archive/
   ```

3. **Start New Session**
   - Open new Claude Code session
   - Paste standardized onboarding prompt
   - Follow first actions sequence

### 9.2 Registry Corruption Recovery

If AGENT_REGISTRY.json becomes corrupted:
1. Restore from git: `git checkout /.claude/sandbox/communications/AGENT_REGISTRY.json`
2. Or restore from backup: Check Box.com disaster recovery
3. Manually rebuild from session files if necessary

---

## 10. VERSIONING

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-11 | Initial mandate creation |

---

## 11. COMPLIANCE

### 11.1 Mandatory Compliance

All agents MUST:
- Follow the standardized prompt format
- Update registry as first action
- Ingest core files before work
- Report ready status to CE

### 11.2 Non-Compliance Consequences

Agents failing to follow this protocol may:
- Have stale context (work on wrong tasks)
- Create duplicate work
- Miss critical directives
- Cause coordination failures

---

## 12. AUTHORITATIVE PROMPTS

See `/.claude/sandbox/communications/shared/AGENT_ONBOARDING_PROMPTS.md` for the complete, copy-paste ready onboarding prompts for each agent.

This mandate defines the **structure and requirements**. The prompts file contains the **executable implementation**.

---

**This is an authoritative mandate document. Follow it.**

---

*Chief Engineer (CE)*
*BQX ML V3 Project*
