# EA Recommendation: Resource Optimization for Step 6

**Date**: December 11, 2025 05:00 UTC
**From**: Enhancement Agent (EA)
**To**: Chief Engineer (CE)
**Priority**: **MEDIUM**
**Type**: Optimization Recommendation

---

## EXECUTIVE SUMMARY

Current Step 6 execution is **highly conservative** with significant unused capacity. Resources can be safely increased to reduce runtime by 50-75%.

---

## CURRENT RESOURCE UTILIZATION

| Resource | Available | Used | Utilization |
|----------|-----------|------|-------------|
| RAM | 62 GB | 7.3 GB | **12%** |
| Process RSS | - | 2.0 GB | **3%** of total |
| vCPUs | 8 | Load 1.32 | **16%** |
| Threads | - | 37 | - |
| Disk | 62 GB free | 2.3 GB checkpoints | **4%** |

**Conclusion**: System is severely underutilized.

---

## CURRENT STEP 6 CONFIGURATION

| Parameter | Current Value |
|-----------|---------------|
| Mode | SEQUENTIAL (1 pair at a time) |
| Workers per pair | 12 |
| Pairs processed | 1 |
| Total concurrent queries | ~12 |

### Current Performance

| Metric | Value |
|--------|-------|
| Progress | 168/669 tables (25%) |
| Rate | ~17 tables/min |
| ETA EURUSD | ~30 min remaining |
| ETA All 28 pairs | ~14 hours |

---

## OPTIMIZATION OPTIONS

### Option 1: SAFE - Increase Workers (RECOMMENDED)

**Change**: Increase `max_workers` from 12 to 16-20

| Parameter | Current | Proposed |
|-----------|---------|----------|
| Workers per pair | 12 | 16 |
| Memory impact | 2.0 GB | ~2.5 GB |
| Risk | - | **LOW** |

**Expected Improvement**:
- Speedup: **30-40%**
- ETA reduction: 14h → ~10h

**Implementation**:
```python
# In process_pair_all_horizons() call:
query_pair_with_checkpoints(pair, date_start, date_end, max_workers=16)
```

---

### Option 2: MODERATE - 2 Parallel Pairs

**Change**: Process 2 pairs simultaneously with 8 workers each

| Parameter | Current | Proposed |
|-----------|---------|----------|
| Parallel pairs | 1 | 2 |
| Workers per pair | 12 | 8 |
| Total workers | 12 | 16 |
| Memory (peak) | 2 GB | ~4 GB |
| Risk | - | **MEDIUM** |

**Expected Improvement**:
- Speedup: **50%**
- ETA reduction: 14h → ~7h

**Constraints**:
- Requires code modification to run pairs in parallel
- Checkpoint directories already isolated (safe)
- BigQuery handles concurrent queries well

---

### Option 3: AGGRESSIVE - 4 Parallel Pairs

**Change**: Process 4 pairs simultaneously with 6 workers each

| Parameter | Current | Proposed |
|-----------|---------|----------|
| Parallel pairs | 1 | 4 |
| Workers per pair | 12 | 6 |
| Total workers | 12 | 24 |
| Memory (peak) | 2 GB | ~8 GB (13%) |
| Risk | - | **HIGH** |

**Expected Improvement**:
- Speedup: **75%**
- ETA reduction: 14h → ~3.5h

**Risks**:
- BigQuery quota pressure (100 concurrent query limit)
- Network bandwidth saturation
- Merge phase memory spikes

---

## KNOWN LIMITATIONS

| Constraint | Limit | Current | Headroom |
|------------|-------|---------|----------|
| BigQuery concurrent queries | 100 | ~12 | **88** |
| RAM | 62 GB | 7.3 GB | **54 GB** |
| vCPUs | 8 | 1.3 load | **6.7** |
| Network | ~1 Gbps | ~100 Mbps | **~900 Mbps** |
| Disk I/O | SSD | Minimal | **Abundant** |

---

## RECOMMENDATION

### For Current Run (No Restart)
**Option 1**: Safe to implement via code edit if process can be stopped/resumed.

### For Next Run
**Option 2**: Process 2 pairs in parallel - best balance of speed and safety.

### NOT Recommended
**Option 3**: Too aggressive without testing. Risk of quota issues.

---

## IMPLEMENTATION PRIORITY

| Priority | Action | Risk | Gain |
|----------|--------|------|------|
| 1 | Increase workers to 16 | LOW | 30-40% |
| 2 | Test 2 parallel pairs | MEDIUM | 50% |
| 3 | 4 parallel pairs | HIGH | 75% |

---

## CAUTION: DO NOT EXCEED

| Limit | Reason |
|-------|--------|
| 20 workers per pair | Diminishing returns, connection overhead |
| 4 parallel pairs | Memory spikes during merge |
| 50 GB memory | Leave buffer for OS and merge operations |
| 80% disk | Checkpoint growth during full run |

---

## DECISION REQUIRED

CE to determine:
1. Accept current configuration (conservative, safe)
2. Stop and restart with Option 1 (16 workers)
3. Plan Option 2 for next pipeline run

---

**Enhancement Agent (EA)**
