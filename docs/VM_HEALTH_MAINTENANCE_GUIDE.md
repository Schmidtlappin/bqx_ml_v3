# BQX-ML-V3 VM Health Maintenance Guide

**Last Updated**: December 11, 2025
**Instance**: bqx-ml-master (GCP Compute Engine, us-east1-b)
**IP**: 34.139.203.254
**Specs**: 62GB RAM, n1-highmem-16 (16 vCPUs)

---

## Quick Health Check

```bash
ssh bqx-ml-master
cd /home/micha/bqx_ml_v3
./scripts/health-monitor.sh
```

---

## Health Metrics & Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Load Average | > 20 | > 50 | Investigate CPU-bound processes |
| Memory Usage | > 85% | > 95% | Check memory leaks, kill stuck processes |
| Swap Usage | Any usage | > 50% | Memory pressure - investigate |
| Disk Usage | > 85% | > 95% | Clean up logs, temp files, old data |
| Active rclone | > 2 | > 5 | Kill excessive sync processes |
| Stuck Processes (D state) | > 0 | > 5 | I/O wait issues - check disk |

---

## Common Health Issues

### 1. High Load Average (> 20)

**Symptoms:**
- System sluggish
- SSH connections slow
- Commands take long to execute

**Diagnosis:**
```bash
# Check load
uptime

# Top CPU consumers
ps aux --sort=-%cpu | head -10

# Check I/O wait
top -b -n 1 | grep "Cpu(s)"
```

**Resolution:**
```bash
# If rclone is the culprit
pkill -9 -f rclone

# If ML training is stuck
ps aux | grep python3 | grep -E '(training|validate|polars)'
kill -9 <PID>  # After confirming stuck
```

---

### 2. Memory Pressure (> 85% used, swap active)

**Symptoms:**
- Swap usage > 0
- OOM (Out of Memory) errors
- Processes killed by kernel

**Diagnosis:**
```bash
# Memory status
free -h

# Top memory consumers
ps aux --sort=-%mem | head -10

# Check for memory leaks
top -o %MEM
```

**Resolution:**
```bash
# Kill stuck Python processes
ps aux | grep python3 | grep -E '(polars|pandas|numpy)'

# Drop caches (safe, non-destructive)
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# If swap is heavily used, consider reboot
sudo reboot
```

---

### 3. Excessive rclone Processes (> 2)

**Symptoms:**
- High I/O wait
- Disk thrashing
- Load average climbing

**Diagnosis:**
```bash
# Count rclone processes
ps aux | grep rclone | grep -v grep | wc -l

# Show details
ps aux | grep rclone | grep -v grep
```

**Resolution:**
```bash
# Kill all rclone
pkill -9 -f rclone

# Verify cron jobs disabled
crontab -l | grep -E '(sync|rclone)'

# Should show commented-out entries
```

---

### 4. Stuck Processes (D state - uninterruptible sleep)

**Symptoms:**
- Processes that can't be killed
- High I/O wait
- Slow disk operations

**Diagnosis:**
```bash
# Find stuck processes
ps -eo pid,stat,wchan:20,cmd | grep ' D '

# Check disk I/O
cat /proc/meminfo | grep -i dirty
```

**Resolution:**
```bash
# Sync to flush dirty pages
sudo sync

# If many processes stuck, reboot required
sudo reboot

# After reboot, check disk health
sudo smartctl -a /dev/sda  # if available
```

---

## Preventive Maintenance

### Daily Checks
- Run health monitor: `./scripts/health-monitor.sh`
- Check disk space: `df -h`
- Verify no rclone running: `ps aux | grep rclone | grep -v grep`

### Weekly Checks
- Review logs: `ls -lh /home/micha/logs/*.log | tail -10`
- Clean old logs: `find /home/micha/logs -name "*.log" -mtime +30 -delete`
- Check for zombie processes: `ps -eo stat | grep '^Z'`

### Monthly Checks
- Review sync script configuration
- Verify backups in Google Drive
- Check for system updates: `sudo apt update && sudo apt list --upgradable`

---

## Emergency Procedures

### VM Unresponsive (Load > 200)

1. **DO NOT** try to SSH if load is extreme
2. Use GCP Console → Serial Console
3. Kill processes via serial console:
   ```bash
   pkill -9 -f rclone
   pkill -9 -f python3
   ```
4. If still unresponsive, hard reboot via GCP Console

### Out of Disk Space

```bash
# Find large files
du -sh /home/micha/bqx_ml_v3/* | sort -rh | head -10

# Clean common culprits
rm -rf /home/micha/bqx_ml_v3/data/temp/*
find /home/micha/logs -name "*.log" -mtime +7 -delete
docker system prune -a -f  # Clean Docker cache
```

### Memory Leak (Swap > 10GB)

```bash
# Identify leaking process
ps aux --sort=-%mem | head -5

# Kill suspect processes
kill -9 <PID>

# Drop caches
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# If swap still high, reboot
sudo reboot
```

---

## Sync Operations (Post-Refactor)

### Manual Sync (Recommended)

```bash
cd /home/micha/bqx_ml_v3

# Full project sync (first time or after conflicts)
./scripts/sync-workspace.sh --resync

# Incremental sync (normal operation)
./scripts/sync-workspace.sh

# Background sync (runs in background)
./scripts/sync-workspace.sh --background
```

### Monitoring Active Sync

```bash
# Check for running sync
ps aux | grep rclone | grep -v grep

# View sync logs
tail -f /home/micha/bqx_ml_v3/logs/sync_*.log

# Monitor bandwidth
watch -n 2 'ss -tunap | grep rclone'
```

### Sync Health Checks

- **Before sync**: Verify load < 10, memory < 80%
- **During sync**: Monitor load, should stay < 5
- **After sync**: Verify completion in log file
- **If stuck**: `pkill -f rclone`, review conflict resolution

---

## Automated Monitoring (Future Enhancement)

### Option 1: Systemd Timer (Recommended)

Create systemd service for continuous monitoring:

```bash
sudo nano /etc/systemd/system/bqx-health-monitor.service
sudo nano /etc/systemd/system/bqx-health-monitor.timer
sudo systemctl enable bqx-health-monitor.timer
sudo systemctl start bqx-health-monitor.timer
```

### Option 2: Lightweight Cron (Conservative)

```bash
# Run health check every hour, log only issues
0 * * * * /home/micha/bqx_ml_v3/scripts/health-monitor.sh >> /home/micha/logs/health.log 2>&1
```

**NOTE**: Avoid aggressive cron schedules (learned from rclone crisis)

---

## Resource Optimization Tips

### Memory Management
- Use `--lazy` flag for large Polars operations
- Stream large files instead of loading into memory
- Set `POLARS_MAX_THREADS` to limit parallelism

### Disk I/O
- Use `--transfers 2 --checkers 4` for rclone (already configured)
- Add `--bwlimit 10M` to prevent bandwidth saturation
- Avoid `--checksum` flag (extremely I/O intensive)

### CPU Management
- Use `nice` for background jobs: `nice -n 10 python3 script.py`
- Limit threads in ML libraries: `export OMP_NUM_THREADS=4`
- Use `ionice` for I/O-heavy tasks: `ionice -c3 python3 script.py`

---

## Escalation Contacts

| Issue Type | Contact | Method |
|------------|---------|--------|
| VM Performance | User (CE) | This session |
| GCP Infrastructure | GCP Support | support.google.com/cloud |
| Data Loss/Corruption | Restore from Google Drive | gdrive:bqx_ml_v3 |
| Critical Outage | Hard reboot via GCP Console | console.cloud.google.com |

---

## Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-11 | Created guide | Post-rclone crisis documentation |
| 2025-12-11 | Sync refactor to bisync | Prevent I/O overload, enable bidirectional |
| 2025-12-11 | Disabled cron jobs | Aggressive sync causing load 245+ |
| 2025-12-11 | Added health-monitor.sh | Proactive monitoring |

---

## Related Files

- [sync-workspace.sh](../scripts/sync-workspace.sh) - Bidirectional workspace sync
- [sync-bqx-project.sh](../scripts/sync-bqx-project.sh) - Full project sync
- [sync-claude-workspace.sh](../scripts/sync-claude-workspace.sh) - Claude workspace sync
- [health-monitor.sh](../scripts/health-monitor.sh) - Health monitoring script
- [20251211_1527_OPS-to-CE_BISYNC_REFACTOR_COMPLETE.md](../.claude/sandbox/communications/inboxes/CE/20251211_1527_OPS-to-CE_BISYNC_REFACTOR_COMPLETE.md) - Refactor completion report

---

**END OF GUIDE**
