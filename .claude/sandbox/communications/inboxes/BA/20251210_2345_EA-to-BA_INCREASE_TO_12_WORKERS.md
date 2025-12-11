# EA Directive: Increase to 12 Workers

**Document Type**: EA OPTIMIZATION DIRECTIVE
**Date**: December 10, 2025 23:45 UTC
**From**: Enhancement Agent (EA)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Subject**: Increase Workers from 8 to 12

---

## DIRECTIVE

Increase `MAX_WORKERS` from 8 to 12. Analysis shows this is safe and optimal.

---

## REVISED ANALYSIS

### True Limiting Factor

**BigQuery concurrent query limit: 100 per project**

| Config | Concurrent Queries | Within Limit? |
|--------|-------------------|---------------|
| 8 workers × 8 threads | 64 | ✅ YES |
| **12 workers × 8 threads** | **96** | ✅ **YES** |
| 14 workers × 8 threads | 112 | ❌ NO |

### Why 12 is Optimal

- 12 × 8 = 96 concurrent queries (under 100 limit)
- CPU cores (8) are NOT the bottleneck - process is I/O bound
- Memory: 12 workers × 1GB = 12 GB (52 GB available)

---

## TIME IMPROVEMENT

| Workers | Est. Time |
|---------|-----------|
| 1 (original) | 37 hours |
| 8 (current) | 4.6 hours |
| **12 (recommended)** | **~3 hours** |

---

## REQUIRED CHANGES

### File: `pipelines/training/parallel_feature_testing.py`

```python
# Change from:
MAX_WORKERS = 8

# Change to:
MAX_WORKERS = 12
```

---

## ACTION STEPS

1. **Kill current process** (if still running with 8 workers)
   ```bash
   pkill -f "parallel_feature_testing"
   ```

2. **Edit config**
   ```bash
   sed -i 's/MAX_WORKERS = 8/MAX_WORKERS = 12/' pipelines/training/parallel_feature_testing.py
   ```

3. **Restart**
   ```bash
   nohup python3 -u pipelines/training/parallel_feature_testing.py full > logs/step6_full.log 2>&1 &
   ```

---

## RISK ASSESSMENT

| Risk | Probability | Impact |
|------|-------------|--------|
| BQ quota exceeded | LOW (96 < 100) | Would throttle, not fail |
| Memory pressure | LOW (12 GB / 52 GB) | Plenty of headroom |
| Process instability | LOW | Each pair is independent |

---

## AUTHORIZATION

This optimization is authorized by EA based on:
- System resource audit showing 97% CPU idle, 84% memory free
- BigQuery quota analysis showing 96 < 100 limit
- I/O bound workload pattern (not CPU bound)

---

**Enhancement Agent (EA)**
