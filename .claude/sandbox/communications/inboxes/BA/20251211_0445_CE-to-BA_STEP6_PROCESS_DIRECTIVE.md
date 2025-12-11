# CE Directive: Step 6 Process Management

**Date**: December 11, 2025 04:45 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL**

---

## DIRECTIVE: Manage Step 6 Processes

### 1. STOP Old Processes

Terminate any old Step 6 processes that are NOT the current sequential run:

```bash
# Kill old processes (if any remain)
pkill -f "parallel_feature_testing.py"
```

### 2. START New Process (If Not Running)

The new sequential process should already be running. If not:

```bash
nohup python3 pipelines/training/parallel_feature_testing.py full > logs/step6_sequential_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

### 3. VERIFY Correct Process

Confirm the running process shows:
- **SEQUENTIAL PAIR PROCESSING** in log
- **CHECKPOINT MODE** active
- Processing ONE pair at a time

### 4. MONITOR Progress

```bash
# Watch live progress
tail -f logs/step6_sequential_*.log

# Check process status
ps aux | grep parallel_feature_testing
```

---

## CURRENT PROCESS (CE Started)

| Parameter | Value |
|-----------|-------|
| PID | 1272452 |
| Mode | SEQUENTIAL + CHECKPOINT |
| Log | `logs/step6_sequential_*.log` |
| Start time | 04:40 UTC |

---

## USER MANDATES (Verify Active)

| Mandate | Expected in Log |
|---------|-----------------|
| Single pair focus | "PAIR X/28: {PAIR}" |
| 12 workers per pair | "12 parallel workers" |
| Checkpoint mode | "CHECKPOINT MODE" |
| Resume capability | "X cached, Y pending" |

---

## REPORTING

1. Confirm old processes stopped
2. Confirm new process running with correct mode
3. Report first pair (EURUSD) completion
4. Report any errors immediately

---

**Chief Engineer (CE)**
