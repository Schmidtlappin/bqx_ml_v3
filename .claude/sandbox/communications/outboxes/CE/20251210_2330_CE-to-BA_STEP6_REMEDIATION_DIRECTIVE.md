# CE Directive: Step 6 Issue Remediation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 23:30 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **URGENT**

---

## DIRECTIVE

Diagnose and remediate Step 6 process issue. Process appears stuck - running but not producing output.

---

## ISSUE SUMMARY

| Indicator | Value | Status |
|-----------|-------|--------|
| Process PIDs | 105047, 105067 | Running (high CPU) |
| Log file | 21 lines, 1KB | ❌ Not updating |
| Last log write | 22:55:06 | 35+ min stale |
| Last BQ job | 12:53:37 | No recent queries |

**Symptoms**:
- Process consuming CPU but not writing to log
- No BigQuery activity for 10+ minutes
- Stuck after initial table discovery phase

---

## DIAGNOSTIC STEPS

### 1. Check Process State
```bash
# Check if process is in D state (uninterruptible sleep)
ps aux | grep 105067

# Check process stack
cat /proc/105067/stack 2>/dev/null || echo "Cannot read stack"

# Check memory usage
ps -o pid,vsz,rss,pmem,comm -p 105067
```

### 2. Check for Python Output Buffering Issue
The `-u` flag should unbuffer, but verify:
```bash
# Check if there's buffered output
ls -la /proc/105067/fd/1 2>/dev/null
```

### 3. Check Script Logic
Review `parallel_feature_testing.py` for potential hang points:
- BigQuery client timeouts
- Merge operations on large DataFrames
- Memory allocation issues

---

## REMEDIATION OPTIONS

### Option A: Kill and Restart with Verbose Logging
```bash
# Kill stuck process
kill 105047 105067

# Restart with additional debugging
cd /home/micha/bqx_ml_v3
nohup python3 -u pipelines/training/parallel_feature_testing.py full 2>&1 | tee logs/step6_$(date +%Y%m%d_%H%M%S).log &
```

### Option B: Add Progress Logging to Script
If script lacks progress output during BigQuery queries or merges:
1. Add print statements after each table fetch
2. Add print statements during merge operations
3. Flush stdout explicitly: `print(..., flush=True)`

### Option C: Reduce Scope for Testing
```bash
# Test with single pair first
python3 -u pipelines/training/parallel_feature_testing.py eurusd
```

---

## RECOMMENDED APPROACH

1. **Kill current stuck process** (PIDs 105047, 105067)
2. **Review script** for missing progress output
3. **Add verbose logging** if needed (print after each table, flush=True)
4. **Restart with single pair test** (EURUSD) to verify fix
5. **If single pair succeeds**, run full 28-pair extraction

---

## REQUIREMENTS

1. Report diagnosis findings to CE
2. Implement fix
3. Restart Step 6
4. Confirm output is being written to log
5. Report when EURUSD completes successfully

---

## DELIVERABLES

1. `20251210_XXXX_BA-to-CE_STEP6_DIAGNOSIS.md` - Issue diagnosis
2. `20251210_XXXX_BA-to-CE_STEP6_FIX_APPLIED.md` - Fix confirmation
3. Updated log file showing progress

---

## TIMELINE

- Diagnosis: 15 min
- Fix implementation: 15 min
- Verification (EURUSD): 10 min
- Total: ~40 min before full restart

---

## CE AUTHORIZATION

You are authorized to:
- Kill the stuck processes
- Modify `parallel_feature_testing.py` to add logging
- Restart Step 6
- Run single-pair tests

Report findings before proceeding with full 28-pair run.

---

**Chief Engineer (CE)**
**Session**: b2360551-04af-4110-9cc8-cb1dce3334cc
