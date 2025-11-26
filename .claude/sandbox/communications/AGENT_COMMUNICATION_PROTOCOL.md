# AGENT-TO-AGENT COMMUNICATION PROTOCOL

**Document Type**: Communication Standards & Guidelines
**Date**: November 26, 2025
**Version**: 1.0
**Location**: `/home/micha/bqx_ml_v3/.claude/sandbox/communications/`

---

## 📝 NAMING CONVENTION

All agent communications must follow this standardized naming format:

### File Naming Pattern
```
YYYYMMDD_HHMM_[SENDER]-to-[RECEIVER]_[subject_brief].md
```

### Components:
- **YYYYMMDD**: Date (e.g., 20251126)
- **HHMM**: 24-hour time (e.g., 1430 for 2:30 PM)
- **SENDER**: Agent code (see Agent Codes below)
- **RECEIVER**: Agent code or "ALL" for broadcast
- **subject_brief**: Lowercase with underscores (max 5 words)

### Agent Codes:
- **CE**: Chief Engineer
- **BA**: Builder Agent
- **TA**: Test Agent (future)
- **MA**: Monitoring Agent (future)
- **USER**: Human user
- **ALL**: All agents (broadcast)

### Examples:
```
20251126_2203_CE-to-BA_critical_questions_response.md
20251126_1530_BA-to-CE_escalation_quota_limit.md
20251127_0900_CE-to-ALL_daily_standup_briefing.md
20251127_1045_BA-to-CE_task_completion_report.md
```

---

## 📂 DIRECTORY STRUCTURE

```
/home/micha/bqx_ml_v3/.claude/sandbox/communications/
├── AGENT_COMMUNICATION_PROTOCOL.md     # This document
├── active/                              # Current ongoing conversations
│   └── [timestamped messages]
├── archive/                            # Completed conversations
│   └── [YYYYMM]/                      # Monthly folders
│       └── [timestamped messages]
├── escalations/                        # Priority escalations
│   └── [timestamped urgent messages]
└── broadcasts/                         # All-agent announcements
    └── [timestamped broadcasts]
```

---

## 📋 MESSAGE TEMPLATE

Every agent communication must follow this structure:

```markdown
# [SUBJECT LINE - CLEAR AND ACTIONABLE]

**From**: [Sender Agent Name and Role]
**To**: [Receiver Agent Name and Role]
**Date**: [YYYY-MM-DD HH:MM:SS]
**Priority**: [URGENT | HIGH | NORMAL | LOW]
**Type**: [REQUEST | RESPONSE | UPDATE | ESCALATION | BROADCAST]

---

## 📌 SUMMARY
[1-2 sentence overview of the communication purpose]

## 📝 CONTENT

### Context
[Background information if needed]

### Main Message
[Core content of the communication]

### Action Items
- [ ] [Specific action required]
- [ ] [Another action if applicable]
- [ ] [Timeline for completion]

## 📊 RELEVANT DATA
[Any data, metrics, or evidence]

## 🔗 REFERENCES
- [Link to related tasks/documents]
- [AirTable task IDs if applicable]

## ⏰ RESPONSE REQUIRED BY
[Specific date/time if time-sensitive]

---

**Message ID**: [YYYYMMDD_HHMM_SENDER_RECEIVER]
**Thread ID**: [If part of ongoing conversation]
```

---

## 🔄 COMMUNICATION FLOW

### 1. Initiating Communication
```bash
# Create new message file
touch /home/micha/bqx_ml_v3/.claude/sandbox/communications/active/[filename].md

# Write content following template
# Update sender's tracking log
```

### 2. Responding to Communication
```bash
# Read original message
# Create response with matching Thread ID
# Reference original Message ID
# Move to archive when thread complete
```

### 3. Escalations
```bash
# For urgent issues requiring immediate attention
# Copy to escalations/ directory
# Update AirTable with escalation flag
# Monitor for response within SLA
```

---

## ⚡ PRIORITY LEVELS & RESPONSE SLAs

| Priority | Response Time | Use Case |
|----------|--------------|----------|
| URGENT | < 1 hour | System down, blocking issues |
| HIGH | < 4 hours | Quality gate failures, resource limits |
| NORMAL | < 24 hours | Standard updates, questions |
| LOW | < 48 hours | FYI, documentation updates |

---

## 📜 COMMUNICATION TYPES

### REQUEST
- Asking for action, information, or decision
- Must include clear action items
- Specify response deadline

### RESPONSE
- Answering a previous request
- Reference original Message ID
- Address all action items

### UPDATE
- Progress reports
- Status changes
- Milestone completions

### ESCALATION
- Issues requiring higher authority
- Blockers that cannot be resolved
- Resource or permission requests

### BROADCAST
- All-agent announcements
- Policy changes
- System-wide updates

---

## ✅ BEST PRACTICES

### DO:
- ✅ Use clear, actionable subject lines
- ✅ Include all relevant context
- ✅ Specify exact action items
- ✅ Set clear deadlines
- ✅ Reference AirTable task IDs
- ✅ Use structured format consistently
- ✅ Archive completed threads promptly
- ✅ Update tracking logs

### DON'T:
- ❌ Use vague subjects like "Question" or "Update"
- ❌ Send incomplete information requiring follow-up
- ❌ Mix multiple unrelated topics in one message
- ❌ Skip the template structure
- ❌ Leave threads open indefinitely
- ❌ Ignore response SLAs

---

## 🔍 TRACKING & AUDIT

### Message Log
Each agent maintains a log:
```
/sandbox/communications/[AGENT_CODE]_message_log.json
```

### Log Entry Format:
```json
{
  "message_id": "20251126_2203_CE_BA",
  "subject": "critical_questions_response",
  "type": "RESPONSE",
  "priority": "HIGH",
  "sent_time": "2025-11-26T22:03:00Z",
  "thread_id": "THREAD_001",
  "status": "DELIVERED",
  "response_received": null
}
```

---

## 📊 WEEKLY SUMMARY

Every Friday, compile weekly communication summary:

```markdown
## Week of [DATE]

### Messages Sent: [COUNT]
- Requests: [N]
- Responses: [N]
- Updates: [N]
- Escalations: [N]

### Average Response Time: [HOURS]
### Open Threads: [COUNT]
### Escalations Resolved: [N/TOTAL]

### Key Decisions Made:
1. [Decision and thread reference]
2. [Decision and thread reference]

### Action Items for Next Week:
- [ ] [Carry-over item]
- [ ] [New item]
```

---

## 🆘 EMERGENCY PROTOCOL

For CRITICAL issues (system failure, data loss risk):

1. Create message with prefix `CRITICAL_`
2. Copy to `/escalations/` AND `/active/`
3. Update AirTable with CRITICAL flag
4. If no response in 30 minutes, re-escalate

---

## 🔄 ARCHIVAL POLICY

- Active threads: Keep in `/active/` until resolved
- Completed threads: Move to `/archive/YYYYMM/` within 24 hours
- Archive retention: 6 months minimum
- Escalations: Never delete, permanent record

---

## 📈 CONTINUOUS IMPROVEMENT

This protocol is version controlled. Suggested improvements should be:
1. Documented as a REQUEST message
2. Discussed in thread
3. Implemented with version increment
4. Broadcast to all agents

---

**Protocol Effective Date**: November 26, 2025
**Next Review Date**: December 26, 2025
**Owner**: Chief Engineer

---

## 🚀 QUICK START CHECKLIST

For new agents starting communication:

- [ ] Read this protocol completely
- [ ] Create your message log file
- [ ] Review existing messages in `/active/`
- [ ] Use template for first message
- [ ] Set up response monitoring
- [ ] Update AirTable with communication references

**Remember**: Clear communication prevents issues, saves time, and ensures project success!