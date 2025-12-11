# CE Directive: Lead Step 6 Execution

**Date**: December 11, 2025 04:55 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL**

---

## DIRECTIVE: Lead & Monitor Step 6 Until Complete

You are designated as **LEAD** for Step 6 execution. Monitor processes, remediate issues and errors in real-time until Step 6 is complete.

---

## YOUR RESPONSIBILITIES

### 1. Process Ownership

| Responsibility | Description |
|----------------|-------------|
| **Lead** | Primary owner of Step 6 execution |
| **Monitor** | Continuous process monitoring |
| **Remediate** | Fix issues in real-time |
| **Report** | Status updates to CE |

### 2. Active Monitoring

```bash
# Live log monitoring
tail -f logs/step6_sequential_*.log

# Process status
watch -n 60 'ps -p 1272452 -o pid,rss,%mem,%cpu --no-headers'

# Progress tracking
watch -n 60 'grep -c "SAVED" logs/step6_sequential_*.log'
```

### 3. Real-Time Remediation

| Issue | Action |
|-------|--------|
| Process crash | Restart immediately (checkpoints preserved) |
| Memory spike | Monitor, restart if OOM |
| Query timeout | Log and continue (checkpoint handles) |
| Table error | Log, continue to next table |
| Pair failure | Log, continue to next pair |

**Restart Command** (if needed):
```bash
nohup python3 pipelines/training/parallel_feature_testing.py full > logs/step6_sequential_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

---

## CURRENT PROCESS

| Parameter | Value |
|-----------|-------|
| PID | 1272452 |
| Mode | SEQUENTIAL + CHECKPOINT |
| Log | `logs/step6_sequential_*.log` |
| Status | RUNNING |

---

## MILESTONE REPORTING

| Milestone | Report To | Content |
|-----------|-----------|---------|
| EURUSD complete | CE | First pair audit |
| 25% (7 pairs) | CE | Progress update |
| 50% (14 pairs) | CE | Mid-point status |
| 75% (21 pairs) | CE | Progress update |
| 100% (28 pairs) | CE | Final completion report |
| Any error | CE | Immediate alert |

---

## ERROR HANDLING PROTOCOL

### Level 1: Table Error
- Log the error
- Continue to next table
- Checkpoint preserves good data

### Level 2: Pair Error
- Log the error
- Continue to next pair
- Report to CE

### Level 3: Process Crash
- Restart immediately
- Checkpoint enables resume
- Report to CE

### Level 4: System Issue
- Escalate to CE immediately
- Coordinate with EA (system monitoring)

---

## COORDINATION

| Agent | Role |
|-------|------|
| **BA (You)** | LEAD - Process execution |
| **QA** | Data audit & validation |
| **EA** | System health monitoring |

---

## SUCCESS CRITERIA

| Criterion | Target |
|-----------|--------|
| Pairs completed | 28/28 |
| Parquet files | 28 files in `data/features/` |
| Row count | ~100K per file |
| Feature coverage | 669 tables/pair (100%) |
| No critical errors | 0 |

---

## AUTHORITY

You are authorized to:
- Restart processes without CE approval
- Modify extraction parameters for recovery
- Skip problematic tables (log for later)
- Coordinate with QA/EA as needed

You must escalate to CE:
- System-level issues
- Data integrity concerns
- Budget overruns (>$35 total)

---

**You own Step 6 until completion. Lead effectively.**

---

**Chief Engineer (CE)**
