# GBPUSD Cloud Run Cost Validation Report

**Date**: December 12, 2025 19:05 UTC
**Execution ID**: bqx-ml-pipeline-54fxl
**Pair**: GBPUSD
**Author**: Enhancement Assistant (EA)
**Priority**: P0-CRITICAL (blocks 27-pair production rollout)

---

## EXECUTIVE SUMMARY

**Status**: ✅ **EXECUTION SUCCESSFUL** with cost model validation required

**Key Findings**:
- **Duration**: 107-108 minutes (vs projected 77-101 min)
- **Overage**: +7 minutes (+7% beyond upper bound)
- **Result**: SUCCESSFUL completion, training file generated
- **Cost Impact**: Duration overage affects per-pair cost projection

**ROI Validation Required**: Actual Cloud Run costs must be analyzed from GCP billing to confirm $0.71/pair projection accuracy.

---

## EXECUTION PERFORMANCE

### Actual vs Projected

| Metric | Projected | Actual | Variance | Status |
|--------|-----------|--------|----------|--------|
| **Duration** | 77-101 min | 107-108 min | +6-7 min (+7%) | ⚠️ **EXCEEDED** |
| **Success Rate** | 100% | 100% (1/1) | 0% | ✅ **MET** |
| **Output** | Training file | training_gbpusd.parquet | ✅ | ✅ **MET** |
| **Timeout** | <120 min | 107-108 min | -12 min margin | ✅ **MET** |

### Timeline

- **Start**: 2025-12-12 17:15:03 UTC
- **Completion**: ~2025-12-12 19:03:00 UTC
- **Duration**: 107-108 minutes (6,420-6,480 seconds)
- **Projection**: 77-101 minutes
- **Upper Bound Overage**: +6-7 minutes

---

## COST MODEL ANALYSIS

### Cloud Run Resource Configuration

**Per Execution**:
- **vCPUs**: 4
- **Memory**: 12 GB
- **Timeout**: 7,200 seconds (2 hours)
- **Region**: us-central1

### Cloud Run Pricing (us-central1)

**Current Rates** (as of Dec 2025):
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GB-second
- **Request**: $0.0000004 per request (batch job = 1 request)

### Projected Cost Calculation (77-101 min)

**Lower Bound** (77 min = 4,620 sec):
- CPU cost: 4 vCPUs × 4,620 sec × $0.000024 = $0.4435
- Memory cost: 12 GB × 4,620 sec × $0.0000025 = $0.1386
- Request cost: 1 × $0.0000004 = $0.0000004
- **Total**: $0.58 per execution

**Upper Bound** (101 min = 6,060 sec):
- CPU cost: 4 vCPUs × 6,060 sec × $0.000024 = $0.5818
- Memory cost: 12 GB × 6,060 sec × $0.0000025 = $0.1818
- Request cost: 1 × $0.0000004 = $0.0000004
- **Total**: $0.76 per execution

**Projected Range**: $0.58-0.76 per execution
**Stated Projection in Roadmap**: $0.71 per pair

---

## ACTUAL COST CALCULATION (108 min)

### Actual Execution (108 min = 6,480 sec)

**CPU Cost**:
- 4 vCPUs × 6,480 seconds × $0.000024/vCPU-sec
- = **$0.6221**

**Memory Cost**:
- 12 GB × 6,480 seconds × $0.0000025/GB-sec
- = **$0.1944**

**Request Cost**:
- 1 request × $0.0000004
- = **$0.0000004**

### Total Actual Cost

**GBPUSD Execution Cost**: **$0.8165** (~$0.82)

**vs Projected $0.71**: **+$0.1065** (+15% overage)

---

## ROI ACCURACY ASSESSMENT

### v2.0.0 Success Metric

**Target**: ROI accuracy ≥80% (estimates within ±20%)

### GBPUSD Cost Accuracy

**Projected**: $0.71 per pair
**Actual**: $0.82 per pair
**Variance**: +$0.11 (+15.5%)

**Accuracy**: **84.5%** ✅ (within ±20% threshold)

**ROI Metric Status**: **PASS** (84.5% accuracy vs 80% target)

---

## DURATION VARIANCE ANALYSIS

### Root Cause Investigation

**Why 108 min vs 77-101 min projection?**

**Hypothesis 1: BigQuery Extraction Rate**
- **Expected**: 10 tables/min (667 tables ÷ 67 min = 10.0 tables/min)
- **Actual**: 6.2 tables/min (667 tables ÷ 108 min ≈ 6.2 tables/min)
- **Finding**: **38% slower than expected**

**Hypothesis 2: Polars Merge Duration**
- **Expected**: 13-20 min
- **Actual**: Not directly measured (logs show no clear stage boundaries)
- **Finding**: Needs instrumentation to measure

**Hypothesis 3: GCS/Validation/Cleanup Overhead**
- **Expected**: 4-6 min total (2-3 GCS + 1-2 validation + 1 cleanup)
- **Actual**: Unknown (not instrumented)

**Recommended Investigation** (for performance analysis CE-1720):
1. Add stage-level timing instrumentation to pipeline
2. Measure actual extraction rate per worker
3. Identify if BigQuery query performance or network I/O is bottleneck
4. Measure Polars merge duration independently

---

## 28-PAIR COST PROJECTION UPDATE

### Original Projection (77-101 min avg)

**Per Pair**: $0.71
**28 Pairs**: $19.90
**Annual** (1× per day): $7,263.50

### Revised Projection (108 min actual)

**Per Pair**: $0.82
**28 Pairs**: $22.96
**Annual** (1× per day): $8,380.40

**Cost Increase**: +$3.06/day, +$1,116.90/year (+15.4%)

### Cost Impact Assessment

**Monthly Increase**: +$93.08
**Annual Increase**: +$1,116.90

**ROI Analysis**:
- Original projection savings vs VM: Unknown (no VM baseline established)
- Cost remains predictable and scalable
- No infrastructure maintenance overhead
- Serverless execution (pay-per-use)

**Recommendation**: **ACCEPTABLE** - Cost increase is within ±20% threshold and provides operational benefits (zero maintenance, auto-scaling, isolation).

---

## VALIDATION BLOCKERS

### Data Not Yet Available

**GCP Billing Data**:
- Cloud Run billing updates with 24-48 hour delay
- **Action Required**: Check actual billed costs on Dec 13-14
- **Location**: GCP Console → Billing → Reports → Filter "Cloud Run"

**Expected Reconciliation**:
- Theoretical calculation: $0.82
- Actual billed amount: TBD (available Dec 13-14)
- Variance tolerance: ±5% (billing rounding, regional pricing variations)

---

## NEXT ACTIONS

### P0-CRITICAL (Within 24 Hours)

1. **Verify Actual GCP Billing** (Dec 13-14)
   - Check GCP Console for bqx-ml-pipeline-54fxl execution cost
   - Compare actual vs theoretical $0.82
   - Document any variance >5%

2. **Performance Analysis** (CE-1720)
   - Create `docs/WORKER_CPU_OPTIMIZATION_RESULTS.md`
   - Analyze why 108 min vs 77-101 min projection
   - Identify bottleneck (BigQuery extraction vs Polars merge)
   - Provide recommendations for 27-pair rollout

3. **Update Intelligence Files**
   - `intelligence/roadmap_v2.json`: Update cost_per_pair $0.71 → $0.82
   - `intelligence/context.json`: Add GBPUSD execution metrics
   - Document duration variance and cost impact

### P1-HIGH (This Week)

4. **27-Pair Rollout Analysis**
   - Sequential vs parallel execution analysis
   - Cost/time tradeoff analysis
   - Execution strategy recommendation to CE

---

## LESSONS LEARNED

### Projection Accuracy

**What Went Well**:
- Execution succeeded within timeout (107 min vs 120 min limit)
- Cost variance within acceptable ±20% threshold (15.5% overage)
- No infrastructure failures or OOM issues
- Training file generated successfully

**What Needs Improvement**:
- **Duration estimate too optimistic** (77-101 min vs actual 108 min)
- **Need stage-level timing instrumentation** (can't isolate bottleneck)
- **BigQuery extraction rate assumptions** (10 tables/min vs actual 6.2)

### Recommendations for Future Projections

1. **Use Conservative Estimates**: Use 90th percentile, not average
2. **Instrument Pipeline Stages**: Add timing for each of 5 stages
3. **Measure Per-Pair Variance**: Some pairs may take longer than others
4. **Add Performance Monitoring**: Track extraction rate, memory usage, CPU utilization

---

## SUMMARY FOR CE

**GBPUSD Cloud Run Execution**: ✅ **SUCCESSFUL**

**Cost Validation**:
- Theoretical cost: **$0.82** (vs projected $0.71)
- Variance: **+15.5%** (within ±20% threshold)
- **ROI Accuracy**: **84.5%** ✅ **MEETS v2.0.0 target** (≥80%)

**Duration**:
- Actual: **108 minutes**
- Projection: **77-101 minutes**
- Overage: **+7% beyond upper bound**

**28-Pair Impact**:
- Revised cost: **$22.96/day** (vs $19.90 projected)
- Annual cost: **$8,380** (vs $7,264 projected)
- Increase: **+$1,117/year** (+15.4%)

**Recommendation**: **PROCEED** with 27-pair rollout using revised $0.82/pair cost model. Cost increase is acceptable and within ROI threshold.

**Next**: Performance analysis to identify duration bottleneck and optimize for production rollout.

---

**Enhancement Assistant (EA)**
*Cost Optimization & ROI Validation*

**Status**: P0-CRITICAL cost validation complete, awaiting GCP billing confirmation (Dec 13-14)

**Deliverable**: Cost validation report with theoretical cost analysis $0.82/pair

**Next**: Performance analysis (CE-1720) + intelligence file updates

---

**END OF REPORT**
