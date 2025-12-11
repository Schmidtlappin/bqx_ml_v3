# CE Directive: System Monitoring for Step 6

**Date**: December 11, 2025 04:50 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **HIGH**

---

## DIRECTIVE: Monitor System Capacity, Usage, and Health

You are directed to monitor system resources during Step 6 execution to ensure healthy operation and identify any issues.

---

## MONITORING SCOPE

### 1. Memory Usage

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Total RAM | 64 GB available | INFO |
| Process RSS | >40 GB | WARNING |
| Process RSS | >50 GB | CRITICAL |
| Swap usage | >1 GB | WARNING |

**Commands**:
```bash
# Process memory
ps -p 1272452 -o pid,rss,vsz,%mem --no-headers

# System memory
free -h

# Memory over time
watch -n 30 'ps -p 1272452 -o pid,rss,%mem --no-headers'
```

### 2. CPU Usage

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Process CPU | >800% (8 cores) | INFO (expected) |
| Process CPU | >1100% | WARNING |
| System load | >12 | WARNING |

**Commands**:
```bash
# Process CPU
ps -p 1272452 -o pid,%cpu --no-headers

# System load
uptime

# Top processes
top -b -n 1 | head -20
```

### 3. Disk Usage

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| /home usage | >80% | WARNING |
| /home usage | >90% | CRITICAL |
| Checkpoint dir size | Growing | INFO |

**Commands**:
```bash
# Disk usage
df -h /home

# Checkpoint directory size
du -sh data/features/checkpoints/

# Features directory size
du -sh data/features/
```

### 4. BigQuery Costs

| Metric | Budget | Alert Level |
|--------|--------|-------------|
| Cost per pair | $1.06 | INFO |
| Cost per pair | >$1.50 (+42%) | WARNING |
| Total cost | $29.56 | Budget |
| Total cost | >$35 | WARNING |

**Monitor via**: Log output shows bytes scanned per table

### 5. Process Health

| Check | Expected | Alert Level |
|-------|----------|-------------|
| Process running | PID 1272452 active | CRITICAL if dead |
| Log updating | New entries | CRITICAL if stale |
| Progress | Tables incrementing | WARNING if stuck |

**Commands**:
```bash
# Process alive
ps -p 1272452 -o pid,state --no-headers

# Log activity
tail -1 logs/step6_sequential_*.log

# Tables processed
grep -c "SAVED" logs/step6_sequential_*.log
```

---

## MONITORING SCHEDULE

| Interval | Actions |
|----------|---------|
| Every 5 min | Check process alive, memory usage |
| Every 15 min | Check disk usage, progress |
| Every 30 min | Report status to CE |
| On anomaly | Immediate report |

---

## REPORTING

### Regular Status (Every 30 min)

```markdown
## EA System Status Report - {TIME}

| Metric | Value | Status |
|--------|-------|--------|
| Process | PID 1272452 | RUNNING/DEAD |
| Memory (RSS) | X GB | OK/WARNING |
| CPU | X% | OK/WARNING |
| Disk | X% | OK/WARNING |
| Tables processed | X/669 | PROGRESS |
| Current pair | {PAIR} | INFO |
```

### Alert Reports

File: `EA-to-CE_STEP6_ALERT_{TIMESTAMP}.md`

---

## CRITICAL ALERTS (Immediate)

Flag immediately if:
- Process dies
- Memory > 50 GB
- Disk > 90%
- Log stale > 5 min
- Process stuck (no progress > 10 min)

---

## PROCESS DETAILS

| Parameter | Value |
|-----------|-------|
| PID | 1272452 |
| Mode | SEQUENTIAL + CHECKPOINT |
| Log | `logs/step6_sequential_*.log` |
| VM | n2-highmem-8 (64 GB RAM, 8 vCPU) |

---

**Chief Engineer (CE)**
