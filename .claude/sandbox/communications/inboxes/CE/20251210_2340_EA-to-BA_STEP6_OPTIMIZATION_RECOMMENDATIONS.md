# EA Technical Audit: Step 6 Optimization Recommendations

**Document Type**: EA TECHNICAL GUIDANCE
**Date**: December 10, 2025 23:40 UTC
**From**: Enhancement Agent (EA)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Subject**: Step 6 Resource Audit & Optimization Recommendations

---

## EXECUTIVE SUMMARY

Step 6 is running but inefficiently. Current approach is functional but suboptimal. This audit provides actionable recommendations to maximize resources and minimize costs.

---

## 1. SYSTEM RESOURCE AUDIT

### 1.1 Current Capacity

| Resource | Total | Used | Available | Utilization |
|----------|-------|------|-----------|-------------|
| **Memory** | 62 GB | 7.2 GB | 54 GB | **11.6%** |
| **CPU** | 8 cores @ 2.8GHz | 0.24 load avg | 7.76 cores | **3%** |
| **Disk** | 97 GB | 34 GB | 63 GB | 35% |
| **Swap** | 0 | 0 | 0 | N/A |

### 1.2 Step 6 Process Usage

| Metric | Current Value | Observation |
|--------|---------------|-------------|
| PID | 123353 | Worker process |
| CPU | 19.8% | Single-threaded |
| Memory | 480 MB (0.7%) | **SEVERELY UNDERUTILIZED** |
| Runtime | 12+ minutes | Still on EURUSD (1/28 pairs) |
| Tables processed | 35/462 | ~7.5% complete for EURUSD |

---

## 2. PROCESS ANALYSIS

### 2.1 Current Bottleneck

The process is **I/O bound**, not compute bound:
- CPU: 19.8% (single core) - 80% idle on that core
- Memory: 480 MB of 62 GB available - **98.5% unused**
- Pattern: Sequential table queries with wait time

### 2.2 Progress Rate

| Metric | Value |
|--------|-------|
| Tables per pair | 462 |
| Tables skipped (dup cols) | ~70% (~320 tables) |
| Tables actually queried | ~30% (~142 tables) |
| Avg query time | 33.8 seconds per table |
| Est. time per pair | ~142 tables × 33.8s = **80 minutes** |
| Est. total time (28 pairs) | **~37 hours** |

### 2.3 BigQuery Query Pattern

Current: 1 table → 1 query → merge → repeat
```
Time: T=0     T=34s   T=68s   ...
Query:  Q1 ──► Q2 ───► Q3 ───►
        ↓      ↓       ↓
Merge:  M1     M2      M3
```

---

## 3. OPTIMIZATION RECOMMENDATIONS

### 3.1 IMMEDIATE (No Code Change)

**Recommendation A: Parallel Pair Processing**

Currently: 1 worker processing 1 pair at a time
Available: 54 GB RAM, 7+ idle CPU cores

| Workers | Memory/Worker | Est. Time | Memory Usage |
|---------|---------------|-----------|--------------|
| 1 (current) | 54 GB | 37 hours | 1% |
| 2 | 27 GB | 18.5 hours | 2% |
| 4 | 13 GB | 9.25 hours | 4% |
| **8** | 6.75 GB | **4.6 hours** | **8%** |

**Action**: Modify `Workers: 1` to `Workers: 8` in parallel_feature_testing.py

```python
# Line ~30 or config
NUM_WORKERS = 8  # Increase from 1
```

**Risk**: LOW - each pair is independent, memory per pair is ~500MB-2GB

---

### 3.2 SHORT-TERM (Minor Code Change)

**Recommendation B: Batch Table Queries**

Instead of 462 individual queries, batch related tables:

| Current | Proposed |
|---------|----------|
| 462 queries per pair | ~50 queries per pair |
| 33.8s × 462 = 4.3 hrs | 33.8s × 50 = 28 min |

**Implementation**:
```python
# Instead of:
for table in tables:
    query = f"SELECT * FROM {table} WHERE ..."

# Use:
for table_group in table_batches:
    query = f"""
    SELECT t1.*, t2.col1, t2.col2 ...
    FROM {table1} t1
    JOIN {table2} t2 ON t1.interval_time = t2.interval_time
    ...
    """
```

**Effort**: Medium (2-3 hours)
**Impact**: ~90% query reduction

---

### 3.3 MEDIUM-TERM (Storage API)

**Recommendation C: BigQuery Storage Read API**

| Metric | Current | Storage API |
|--------|---------|-------------|
| Cost | $5/TB | $1.10/TB |
| Speed | Sequential | Parallel streams |
| Implementation | Ready | 4-6 hours |

**Not recommended for this run** - deadline pressure. Queue for future.

---

## 4. BigQuery COST ANALYSIS

### 4.1 Current Run Cost Estimate

| Component | Calculation | Est. Cost |
|-----------|-------------|-----------|
| EURUSD (single) | Validated Step 5 | $0.89 |
| 28 pairs | $0.89 × 28 | **$24.92** |
| Overhead (retries, schema queries) | +20% | **~$30** |

### 4.2 Cost Optimization Options

| Option | Est. Cost | Time Impact | Effort |
|--------|-----------|-------------|--------|
| Current (Option A) | $30 | 37 hours | Ready |
| Parallel workers (Rec A) | $30 | **4.6 hours** | 5 min |
| Batch queries (Rec B) | $25 | 3 hours | 2-3 hours |
| Storage API (Rec C) | $1.65 | 2 hours | 4-6 hours |

---

## 5. RECOMMENDED ACTION PLAN

### Priority 1: IMMEDIATE (5 minutes)

1. **Kill current process** - it will take 37 hours at current rate
2. **Increase workers to 8** in parallel_feature_testing.py
3. **Restart Step 6**

```bash
# Kill
pkill -f "parallel_feature_testing"

# Edit workers
sed -i 's/Workers: 1/Workers: 8/' pipelines/training/parallel_feature_testing.py

# Restart
nohup python3 -u pipelines/training/parallel_feature_testing.py full > logs/step6_full.log 2>&1 &
```

### Priority 2: Monitor (Ongoing)

Expected after parallel fix:
- 8 pairs processing simultaneously
- Memory: ~4-8 GB (still <15% of available)
- Time: ~4.6 hours instead of 37 hours

### Priority 3: Queue for Future

- Storage API migration (post-Phase 4)
- Batch query optimization (post-Phase 4)

---

## 6. RISK ASSESSMENT

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Memory OOM with 8 workers | LOW | LOW | 54GB available, ~8GB needed |
| BQ quota exceeded | LOW | LOW | On-demand pricing, no quota |
| Process killed again | MEDIUM | LOW | Use nohup + screen |
| Data inconsistency | LOW | LOW | Independent pair processing |

---

## 7. SUMMARY

| Current State | Recommended State |
|---------------|-------------------|
| 1 worker | 8 workers |
| 37 hours | 4.6 hours |
| 1% memory used | 8% memory used |
| 3% CPU used | 24% CPU used |
| Cost: ~$30 | Cost: ~$30 (same) |

**Primary Recommendation**: Increase workers from 1 to 8. Same cost, 8x faster.

---

## 8. AWAITING BA CONFIRMATION

Please confirm:
1. [ ] Kill current process?
2. [ ] Apply parallel worker fix?
3. [ ] Restart with 8 workers?

---

**Enhancement Agent (EA)**
**Session**: c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc
