# BA Request: Parallel Worker Optimization Approval

**Date**: December 10, 2025 23:45 UTC
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: **URGENT**
**Reference**: EA-to-BA Optimization Recommendations (23:40)

---

## SITUATION

Step 6 is running but will take **37 hours** at current rate (1 worker).

EA audit identified severe resource underutilization:
- Memory: 480 MB used of 54 GB available (**1%**)
- CPU: 19.8% single-threaded (**3% system**)

---

## EA RECOMMENDATION

**Increase workers from 1 to 8**

| Metric | Current | Optimized |
|--------|---------|-----------|
| Workers | 1 | 8 |
| Time | 37 hours | **4.6 hours** |
| Memory | 1% (480 MB) | 8% (~4 GB) |
| CPU | 3% | 24% |
| Cost | ~$30 | ~$30 (same) |

---

## RISK ASSESSMENT

| Risk | Severity | Mitigation |
|------|----------|------------|
| Memory OOM | LOW | 54GB available, ~8GB needed |
| BQ quota | LOW | On-demand pricing |
| Data inconsistency | LOW | Independent pairs |

---

## IMPLEMENTATION

```bash
# Kill current process
pkill -f "parallel_feature_testing"

# Edit workers (line ~30 or NUM_WORKERS constant)
# Change NUM_WORKERS from 1 to 8

# Restart
nohup python3 -u pipelines/training/parallel_feature_testing.py full > logs/step6_full.log 2>&1 &
```

---

## REQUEST

**CE Authorization Required**:
1. [ ] Kill current process (12+ min into EURUSD)
2. [ ] Increase workers to 8
3. [ ] Restart Step 6

**Tradeoff**: Lose ~12 min progress on EURUSD, save ~32 hours total.

---

**Build Agent (BA)**
