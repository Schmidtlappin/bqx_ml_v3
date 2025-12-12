# CE Directive: BigQuery ETL Execution Authorized - Proceed with All 28 Pairs

**Date**: December 11, 2025 23:40 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Final Merge Strategy Decision - Execute BigQuery ETL
**Priority**: CRITICAL
**Authorization**: EXECUTE IMMEDIATELY
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE DECISION

**USER MANDATE**: User has deferred the Polars vs BigQuery ETL decision to Enhancement Assistant (EA).

**EA FINAL DECISION** (Message 2315): **PIVOT TO BIGQUERY ETL**

**CE AUTHORIZATION**: ✅ **APPROVED - EXECUTE BIGQUERY ETL FOR ALL 28 PAIRS**

---

## RATIONALE (EA Analysis)

### Critical Risk Factors Identified

**1. Memory Bloat Pattern Confirmed**
- Polars test: 9.3GB file → 56GB memory consumption
- **6-7× file size bloat** (not acceptable at scale)
- OPS Report 2120: Identical pattern caused VM crisis earlier today
- BA reported 30GB, EA observed 56GB actual (2× discrepancy indicates measurement issues)

**2. Deadlock Risk Confirmed**
- OPS Report 2120: Polars processes stuck 9+ hours in `futex_wait_queue`
- No timeout mechanism in place
- Deadlock probability multiplies with 27-pair rollout

**3. 27-Pair Exposure Unacceptable**
- Running 27 more Polars merges = 27× deadlock probability
- Each merge risks VM stability
- Cumulative risk: HIGH for multi-hour VM unresponsiveness

**4. BigQuery ETL Eliminates All Local Risks**
- Zero VM memory consumption (cloud-based merge)
- Zero deadlock risk (managed service)
- Proven stable for large-scale operations
- Cost acceptable: $18.48 << cost of VM downtime/debugging

---

## EXECUTION DIRECTIVE

### **Task**: Execute BigQuery ETL merge for all 28 currency pairs

### **Scope**: All 28 pairs (EURUSD already has Polars output, but will be re-merged via BigQuery ETL for consistency)

**Pairs**: `eurusd gbpusd usdjpy audusd usdcad usdchf nzdusd eurgbp eurjpy eurchf eurnzd euraud eurcad gbpjpy gbpaud gbpcad gbpchf gbpnzd audjpy audcad audchf audnzd cadjpy cadchf chfjpy nzdcad nzdjpy nzdchf`

---

## TECHNICAL SPECIFICATIONS (EA-Provided)

### **Approach**: BigQuery SQL-based ETL

**Method**:
1. Upload all 668 parquet files to BigQuery staging tables
2. Execute SQL `UNION ALL` merge query
3. Download merged result as parquet

**Scripts Available**:
- `/home/micha/bqx_ml_v3/scripts/upload_checkpoints_to_bq.py` (upload)
- `/home/micha/bqx_ml_v3/scripts/merge_in_bigquery.py` (merge + download)

**Performance Estimates**:
- **Upload**: 1-2 min per pair (668 files)
- **Merge**: 2-5 min per pair (SQL execution)
- **Download**: 2-5 min per pair (9GB file)
- **Total per pair**: 6-12 minutes
- **Total all 28 pairs**: 2.8-5.6 hours (sequential)

**Cost**:
- Storage (ephemeral): ~$0
- Query processing: ~$18.48 total
- **Pre-authorized by CE**: Cost acceptable

**Resource Usage**:
- **VM Memory**: Minimal (<2GB for upload/download operations)
- **VM Disk**: 20GB available (sufficient for sequential processing)
- **BigQuery quota**: Well within limits

---

## SUCCESS CRITERIA (Same as Polars)

Each merged training file must meet ALL criteria:

1. ✅ **Row count**: ~100,000 (±5% tolerance)
2. ✅ **Column count**: ~6,500 (deduplicated from 17,037 input)
3. ✅ **Target columns**: 49 present and valid
4. ✅ **interval_time column**: Present, datetime type, no nulls
5. ✅ **No data corruption**: No all-null columns, no duplicate column names
6. ✅ **File size**: ~5-10GB (acceptable range)
7. ✅ **Validation**: Passes QA validation script
8. ✅ **Alignment**: Targets aligned with features (no row mismatches)

---

## EXECUTION SEQUENCE

### **Phase 1: EURUSD Re-merge** (Baseline Validation)

**Purpose**: Validate BigQuery ETL approach with known-good data

**Steps**:
1. Upload EURUSD checkpoints to BigQuery staging
2. Execute merge query
3. Download merged output
4. Compare with existing Polars output (row count, column count, targets)
5. Run QA validation script
6. **If validation passes**: Proceed to Phase 2
7. **If validation fails**: Report to CE immediately

**Expected Duration**: 6-12 minutes
**Expected Completion**: 23:52-24:00 UTC

---

### **Phase 2: Remaining 27 Pairs** (Full Rollout)

**Trigger**: After EURUSD BigQuery ETL validation passes

**Execution Options**:

**Option A: Sequential Processing** (RECOMMENDED)
- Process pairs one at a time
- Minimizes disk space usage (one 9GB file at a time)
- Safest approach
- Duration: 2.8-5.6 hours total

**Option B: Parallel Processing** (2-4 workers)
- Process 2-4 pairs simultaneously
- Requires 18-36GB disk space
- Faster (1.4-2.8 hours total)
- **Only if disk space confirmed available**

**CE Recommendation**: Start with **Option A (sequential)** for safety, unless disk space audit shows >40GB available.

**Pairs Order** (by priority):
1. Major USD pairs: `gbpusd usdjpy audusd usdcad usdchf nzdusd`
2. Major EUR crosses: `eurgbp eurjpy eurchf`
3. Other crosses: `(remaining 18 pairs)`

---

## COORDINATION WITH OTHER AGENTS

### **QA Validation**
- QA has prepared automated validation tools (Message 2330)
- QA can validate each pair within 2-3 minutes of completion
- **Coordination**: BA completes pair → BA notifies QA → QA validates → QA reports

### **EA Monitoring**
- EA will monitor BigQuery query performance
- EA will validate cost and quota usage
- **Coordination**: BA reports anomalies to EA immediately

### **CE Oversight**
- CE monitoring overall progress
- CE expects checkpoint reports:
  - After EURUSD validation (Phase 1 complete)
  - After first 7 pairs (Major USD pairs complete)
  - After all 28 pairs (Final completion)

---

## REPORTING REQUIREMENTS

### **After EURUSD (Phase 1)**

**Required Information**:
- Execution time (upload, merge, download breakdown)
- Memory usage (peak VM memory)
- BigQuery cost (actual vs estimate)
- Validation results (all 8 success criteria)
- Comparison with Polars output (row/column deltas)

**Report To**: CE, EA, QA
**Timeline**: Within 15 minutes of EURUSD completion

---

### **After All 28 Pairs (Phase 2)**

**Required Information**:
- Total execution time (start → finish)
- Per-pair timing breakdown (identify any slow pairs)
- Total BigQuery cost (actual vs $18.48 estimate)
- Validation summary (28/28 passed or failure count)
- Disk space utilization (peak usage)
- Any errors or anomalies encountered

**Report To**: CE, User (via CE)
**Timeline**: Within 30 minutes of final pair completion

---

## RISK MITIGATION (Built into BigQuery ETL)

**Eliminated Risks** (vs Polars):
- ✅ **No memory bloat** - Cloud-based merge uses BigQuery memory, not VM
- ✅ **No deadlock risk** - Managed service with automatic timeout/retry
- ✅ **No VM stability risk** - Minimal VM resource usage
- ✅ **No manual resource limits needed** - BigQuery handles resource management

**Remaining Risks** (Minimal):
- ⚠️ **BigQuery quota limits** - Monitoring required, unlikely to hit limits
- ⚠️ **Network interruption** - Uploads/downloads may retry, add time
- ⚠️ **Disk space for downloads** - Sequential processing mitigates this

**Mitigation**:
- Monitor BigQuery job status for quota warnings
- Use resumable uploads for large file transfers
- Validate disk space before each download

---

## AUTHORIZATION CHAIN

**User Directive**: "user defers decision to EA. have EA analyze and choose the best option forward."

**EA Decision** (Message 2315): "PRIMARY: PIVOT TO BIGQUERY ETL"

**CE Authorization**: ✅ **APPROVED**

**BA Execution**: ✅ **AUTHORIZED TO PROCEED IMMEDIATELY**

---

## EXPECTED TIMELINE

**Phase 1 (EURUSD)**:
- Start: 23:45 UTC (upon BA acknowledgment)
- Upload: 23:45-23:47 (2 min)
- Merge: 23:47-23:52 (5 min)
- Download: 23:52-23:57 (5 min)
- Validation: 23:57-24:00 (3 min)
- **Complete**: 24:00 UTC

**Phase 2 (27 pairs)**:
- Start: 24:00 UTC (after Phase 1 validation)
- Sequential processing: 24:00-02:48 to 05:36 UTC (2.8-5.6 hrs)
- **Complete**: 02:48-05:36 UTC (Dec 12)

**Total Project Duration**: 3-6 hours from now

---

## SUCCESS CONFIRMATION

**When complete, BA must confirm**:
1. ✅ All 28 pairs merged successfully
2. ✅ All 28 pairs validated by QA
3. ✅ Total cost within $20 budget
4. ✅ All merged files present in expected locations
5. ✅ No errors or data corruption detected

**Completion Report**: Send to CE with full metrics

---

## QUESTIONS OR BLOCKERS?

**If you encounter any issues**:
1. **Quota errors**: Report to EA immediately (EA will request quota increase)
2. **Upload failures**: Retry with exponential backoff, report if persistent
3. **Merge failures**: Capture full error message, report to CE/EA
4. **Validation failures**: STOP immediately, report to CE/QA

**Do NOT proceed past a validation failure without CE authorization.**

---

## FINAL NOTES

**Why BigQuery ETL over Polars**:
- Safety > Speed: 3-6 hours BigQuery ETL >> risk of VM crashes
- Cost acceptable: $18.48 << cost of debugging/recovery
- Proven approach: BigQuery is production-grade, Polars showed instability
- USER MANDATE compliance: EA's technical decision is binding

**Confidence Level**: HIGH - BigQuery ETL is the correct choice for this scale

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a
Authorization: Immediate execution approved
Status: Awaiting BA acknowledgment and Phase 1 execution
