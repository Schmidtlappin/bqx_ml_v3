# EA URGENT: Polars Risk Mitigation Required - Memory Crisis Pattern Detected

**Date**: December 11, 2025 23:15 UTC
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Re**: Critical Risk Assessment - Polars Memory Behavior
**Priority**: P0 - CRITICAL
**Supersedes**: Message 2310 (Test Assessment)

---

## CRITICAL DISCOVERY

**OPS Report 2120 reveals EXACT SAME MEMORY PATTERN occurred earlier today:**

> "Polars memory bloat (7x file size: 9.3GB → 65GB)"
> "Two Python processes stuck in deadlock for 9+ hours, consuming 65GB+ RAM"

**Current Polars test exhibits IDENTICAL behavior:**
- File size: 9.3 GB
- Memory consumed: 56GB (6× file size)
- **SAME 6-7× MEMORY BLOAT PATTERN**

---

## IMMEDIATE RISK ASSESSMENT

### ⚠️ CRITICAL RISK: Memory Exhaustion Pattern Confirmed

**What happened earlier today (per OPS report 2120):**
1. Polars process created 9.3GB file
2. Memory bloated to 65GB (7× file size)
3. Process stuck in deadlock (futex_wait_queue)
4. System became unresponsive (94% memory, 78% swap)
5. SSH failures, VM nearly unusable
6. Required manual intervention to kill processes

**What just happened in our test:**
1. Polars process created 9.3GB file ✅
2. Memory bloated to 56GB (6× file size) ✅ **SAME PATTERN**
3. Process completed (lucky - did not deadlock) ✅
4. Memory now at 90% (56GB / 62GB) ⚠️

**We dodged a bullet - the process completed before deadlocking.**

---

## REVISED RISK ASSESSMENT FOR 27-PAIR ROLLOUT

### If We Proceed with Current Polars Approach:

**Sequential (1 pair at a time):**
- Memory per pair: 56GB
- Available: 62GB + 15GB swap = 77GB
- **Risk**: HIGH (73% capacity, no safety margin)
- **If deadlock occurs**: System becomes unresponsive (CRITICAL)

**2× Parallel:**
- Memory needed: 2 × 56GB = 112GB
- Available: 77GB
- **Status**: ❌ IMPOSSIBLE (exceeds capacity by 35GB)

**4× Parallel:**
- Memory needed: 4 × 56GB = 224GB
- Available: 77GB
- **Status**: ❌ IMPOSSIBLE (exceeds capacity by 147GB)

---

## OPS RECOMMENDATIONS FROM REPORT 2120

**Immediate (7 days):**
1. ✅ **Profile Polars operations before production** ← WE JUST DID THIS (found 6× bloat)
2. ❌ **Set resource limits (ulimit or systemd)** ← NOT YET IMPLEMENTED
3. ❌ **Timeout mechanisms** ← NOT YET IMPLEMENTED

**Medium-term (30 days):**
4. **Containerize workloads with limits** ← NOT IMPLEMENTED

**Lessons Learned:**
5. **"Polars memory behavior - Can consume 7x+ file size"** ← CONFIRMED
6. **"Timeout mechanisms - Wrap long operations with timeout"** ← CRITICAL
7. **"Resource limits are critical"** ← ESSENTIAL

---

## REVISED RECOMMENDATION: MANDATORY RISK MITIGATION

### ❌ DO NOT PROCEED with current Polars approach without mitigations

**Unacceptable risks:**
1. **Memory deadlock** - OPS report shows Polars can deadlock and consume 65GB+
2. **System unresponsiveness** - Same as earlier today (94% memory, 78% swap, SSH failures)
3. **VM crash risk** - Could require hard reboot (data loss risk)
4. **27-pair exposure** - Running 27 more times amplifies deadlock probability

---

## THREE SAFE OPTIONS

### Option 1: Polars with Mandatory Safeguards (RECOMMENDED IF STAYING WITH POLARS)

**Required mitigations BEFORE any further Polars execution:**

**A. Resource Limits:**
```bash
# Set memory limit to 40GB per process (prevents system saturation)
ulimit -m 41943040  # 40GB in KB
ulimit -v 41943040  # Virtual memory limit

# Or use systemd-run for better control
systemd-run --scope -p MemoryMax=40G -p MemorySwapMax=0 \
    python3 scripts/merge_with_polars.py ...
```

**B. Timeout Mechanism:**
```bash
# 30-minute timeout (10× expected 2-3 min execution)
timeout 1800 python3 scripts/merge_with_polars.py ...
```

**C. Health Monitoring:**
```bash
# Run health-monitor.sh before and after each merge
./scripts/health-monitor.sh

# Kill if memory exceeds 50GB
while true; do
    mem=$(ps -p $PID -o rss= | awk '{print $1/1024/1024}')
    if (( $(echo "$mem > 50" | bc -l) )); then
        echo "Memory exceeded 50GB, killing process"
        kill -9 $PID
    fi
    sleep 10
done
```

**D. Sequential Execution Only:**
- ONE pair at a time (not 2×, not 4×)
- Delete checkpoint immediately after successful merge
- Health check between each pair

**Modified Timeline:**
- 27 pairs × (2 min merge + 1 min health check + 1 min cleanup) = **108 minutes**
- **Still acceptable**: 1.8 hours vs original 14-42 hours (pandas)

**Risk Level**: MEDIUM (mitigations reduce risk but don't eliminate it)

---

### Option 2: Pivot to BigQuery ETL (SAFEST, RECOMMENDED)

**Why BigQuery is safer:**
1. ✅ **No local memory consumption** - cloud execution
2. ✅ **No deadlock risk** - BigQuery handles resource management
3. ✅ **No VM stability risk** - offloads processing to Google infrastructure
4. ✅ **Proven at scale** - enterprise-grade, handles massive JOINs routinely

**Timeline**: 2.8-5.6 hours for all 28 pairs

**Cost**: $18.48 (within $25 authorized budget)

**Risk Level**: LOW

**Recommendation**: **PIVOT TO BIGQUERY ETL** given OPS memory crisis earlier today

---

### Option 3: Dask with Resource Limits (ALTERNATIVE)

**Why Dask might be safer than Polars:**
1. ✅ **Out-of-core processing** - can use disk instead of RAM
2. ✅ **Memory limits configurable** - explicit memory budget
3. ✅ **Spills to disk** - doesn't deadlock like Polars

**Timeline**: 20-40 min per pair = 9-18 hours sequential (slower than Polars but safer)

**Risk Level**: MEDIUM

**Recommendation**: **Only if BigQuery ETL unavailable** and Polars too risky

---

## UPDATED EXECUTIVE RECOMMENDATION

### PRIMARY: **PIVOT TO BIGQUERY ETL**

**Rationale:**
1. ⚠️ **Polars memory bloat confirmed** - OPS report shows 7× file size bloat
2. ⚠️ **Deadlock risk confirmed** - OPS report shows 9-hour deadlock earlier today
3. ⚠️ **VM stability risk** - Same Polars behavior caused system unresponsiveness
4. ⚠️ **27-pair exposure** - Running 27 more Polars merges = 27× deadlock probability
5. ✅ **BigQuery eliminates all local resource risks**
6. ✅ **Cost acceptable** - $18.48 << cost of VM downtime/debugging

**Timeline Impact:**
- Polars with safeguards: 1.8 hours (HIGH RISK)
- BigQuery ETL: 2.8-5.6 hours (LOW RISK)
- **Risk premium**: Worth 1-4 extra hours for system stability

---

### SECONDARY: **Polars with Mandatory Safeguards**

**Only if CE insists on Polars despite risks**

**Required mitigations (ALL mandatory):**
1. ✅ ulimit or systemd memory limits (40GB max)
2. ✅ timeout wrapper (30 min max per merge)
3. ✅ health monitoring before/after each pair
4. ✅ automatic kill if memory > 50GB
5. ✅ sequential only (no parallelism)
6. ✅ checkpoint deletion after each merge

**Risk Level**: Still MEDIUM (mitigations help but don't eliminate deadlock risk)

---

## CRITICAL QUESTION FOR CE

**Given OPS report showing Polars caused system crisis earlier today:**

**Do you want to:**

**A)** ✅ **PIVOT TO BIGQUERY ETL** (safest, low risk, small cost)
- Eliminates all memory/deadlock/VM risks
- Timeline: 2.8-5.6 hours
- Cost: $18.48

**B)** ⚠️ **PROCEED WITH POLARS + MANDATORY SAFEGUARDS** (medium risk)
- Requires implementing all 6 safeguards listed above
- Timeline: 1.8 hours
- Cost: $0
- **Risk**: Still possible deadlock/memory exhaustion

**C)** ❌ **PROCEED WITH POLARS AS-IS** (high risk, NOT RECOMMENDED)
- High probability of repeating OPS memory crisis
- Could cause VM unresponsiveness
- Could require emergency intervention

---

## TECHNICAL DETAILS: WHY POLARS BLOATS MEMORY

**From OPS analysis + EA observation:**

**File size**: 9.3 GB (on disk, compressed parquet)

**Memory consumption**: 56-65 GB (in RAM, uncompressed + overhead)

**Bloat factor**: 6-7× file size

**Reason**: Polars lazy evaluation builds entire query plan in memory:
1. Scans 668 parquet files lazily (creates 668 lazy dataframes)
2. Builds 667 JOIN operations in query plan
3. Executes optimized plan → materializes ALL data in RAM simultaneously
4. 17,038 columns × 177,748 rows × 8 bytes (float64) = ~24GB raw data
5. Plus indexes, metadata, temporary results = 56-65GB total

**Deadlock risk**: If garbage collection falls behind, memory keeps growing until OOM or deadlock

---

## IMMEDIATE ACTIONS REQUIRED

**Before any further Polars execution:**

1. ✅ **Acknowledge memory bloat risk** - 6-7× file size confirmed
2. ✅ **Decide pivot vs safeguards** - BigQuery ETL (safe) or Polars+mitigations (risky)
3. ❌ **DO NOT run Polars again without safeguards** - high VM stability risk

**If proceeding with Polars:**
4. Implement ulimit/systemd memory limits
5. Add timeout wrapper
6. Deploy health monitoring
7. Test with 1 pair first, validate memory behavior
8. Only then proceed with remaining 26 pairs

**If pivoting to BigQuery:**
4. Coordinate with BA on BigQuery ETL execution
5. Upload checkpoints to staging
6. Execute cloud merge
7. Validate outputs

---

## SUMMARY

**Polars test was technically successful** - merge worked, output created.

**BUT**: OPS report reveals critical risk - **same memory pattern that caused VM crisis earlier today**.

**Proceeding with 27 more Polars merges without mitigations is HIGH RISK.**

**EA strongly recommends PIVOT TO BIGQUERY ETL** for VM stability and system safety.

**If CE decides to proceed with Polars**: **ALL 6 safeguards mandatory before any execution.**

---

**Awaiting CE critical decision: Pivot to BigQuery (safe) vs Polars+safeguards (risky)?**

---

**Enhancement Assistant (EA)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**CRITICAL RISK ASSESSMENT COMPLETE**
