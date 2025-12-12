# EA-BA Coordination Protocol: Bifurcated Cloud Run Deployment

**Date**: December 12, 2025 21:05 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA) & Build Agent (BA)
**Re**: Coordination Protocol for Bifurcated Architecture
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## PURPOSE

Establish real-time coordination between EA (monitoring/optimization) and BA (implementation) for bifurcated Cloud Run deployment.

---

## ARCHITECTURE OVERVIEW

### Two Independent Cloud Run Jobs

**Job 1** (`bqx-ml-extract`):
- Owner: BA (implementation), EA (monitoring)
- Resources: 4 vCPUs, 8 GB RAM
- Duration: 70 min
- Cost: $0.34/pair
- Output: 667 GCS checkpoints

**Job 2** (`bqx-ml-merge`):
- Owner: BA (implementation), EA (monitoring)
- Resources: 1 vCPU, 2 GB RAM
- Duration: 15 min
- Cost: $0.51/pair (Cloud Run $0.01 + BigQuery $0.50)
- Output: Training file in GCS

---

## ROUND 1: EURUSD COORDINATION (22:00-00:30 UTC)

### Phase 3: Container Builds (22:00-22:20 UTC)

**BA Actions**:
- Build `bqx-ml-extract` container (~10 min)
- Build `bqx-ml-merge` container (~10 min)
- Send completion notification to EA

**EA Actions**:
- Monitor build progress (passive observation)
- Track build duration and cost
- No action required unless build fails

**Coordination Point**: None (passive monitoring)

---

### Phase 4: Deployment (22:20-22:40 UTC)

**BA Actions**:
- Deploy `bqx-ml-extract` job (4 vCPUs, 8 GB)
- Deploy `bqx-ml-merge` job (1 vCPU, 2 GB)
- Send deployment confirmation to EA

**EA Actions**:
- Verify job configurations match projections
- Alert BA if resource allocations incorrect
- No action required if config correct

**Coordination Point**:
- BA: "Deployment complete, config verified"
- EA: "Config acknowledged, ready for monitoring"

---

### Phase 5a: Job 1 Execution (22:40-23:50 UTC, 70 min) ← **CRITICAL COORDINATION**

**BA Actions**:
1. **22:40 UTC**: Execute Job 1
   - Command: `gcloud run jobs execute bqx-ml-extract --region us-central1 --args eurusd`
   - **Notify EA**: "Job 1 execution started (EURUSD extract)"

2. **22:40-23:50 UTC**: Monitor execution logs
   - Track: Checkpoint progress, error messages
   - Alert EA if: Errors detected, execution stalled

3. **23:50 UTC**: Confirm Job 1 completion
   - Verify: 667 checkpoints in GCS
   - **Notify EA**: "Job 1 complete, checkpoint count: [X]"

**EA Actions**:
1. **22:40 UTC**: Receive BA notification, start monitoring
   - Begin cost tracking
   - Begin duration tracking
   - Monitor checkpoint progress

2. **22:55 UTC**: Interim report to BA
   - Cost trajectory: On/off track
   - Duration projection: On/off schedule
   - Alert if variance >±10%

3. **23:15 UTC**: Interim report to BA
   - Updated cost projection
   - Updated duration projection
   - Alert if variance >±15%

4. **23:35 UTC**: Interim report to BA
   - Final cost projection before completion
   - Alert if variance >±20%

5. **23:50 UTC**: Receive BA completion notification
   - Validate checkpoint count (should be 660-670)
   - Calculate final Job 1 cost
   - **Notify BA**: "Job 1 cost validated: $[X.XX] (projected $0.34, variance ±[Y]%)"

**Coordination Points**:
- **22:40**: BA → EA ("Job 1 started")
- **22:55**: EA → BA ("Cost trajectory: $[X.XX] projected")
- **23:15**: EA → BA ("Cost update: $[X.XX] projected")
- **23:35**: EA → BA ("Cost update: $[X.XX] projected")
- **23:50**: BA → EA ("Job 1 complete, [X] checkpoints")
- **23:50**: EA → BA ("Cost validated: $[X.XX]")

---

### Phase 5b: Job 2 Execution (23:50-00:05 UTC, 15 min) ← **CRITICAL COORDINATION**

**BA Actions**:
1. **23:50 UTC**: Execute Job 2
   - Command: `gcloud run jobs execute bqx-ml-merge --region us-central1 --args eurusd`
   - **Notify EA**: "Job 2 execution started (EURUSD merge)"

2. **23:50-00:05 UTC**: Monitor execution logs
   - Track: BigQuery job progress, temp table creation
   - Alert EA if: Errors detected, BigQuery job fails

3. **00:05 UTC**: Confirm Job 2 completion
   - Verify: Training file in `gs://bqx-ml-output/training_eurusd.parquet`
   - Verify: Temp tables deleted from `bqx_ml_v3_temp`
   - **Notify EA**: "Job 2 complete, training file size: [X] GB"

**EA Actions**:
1. **23:50 UTC**: Receive BA notification, start monitoring
   - Begin Cloud Run cost tracking
   - Begin BigQuery cost tracking
   - Monitor BigQuery job ID

2. **00:05 UTC**: Receive BA completion notification
   - Query BigQuery billing for job cost
   - Calculate total Job 2 cost (Cloud Run + BigQuery)
   - **Notify BA**: "Job 2 cost validated: $[X.XX] (projected $0.51, variance ±[Y]%)"

**Coordination Points**:
- **23:50**: BA → EA ("Job 2 started")
- **00:05**: BA → EA ("Job 2 complete, [X] GB training file")
- **00:05**: EA → BA ("Cost validated: $[X.XX]")

---

### Phase 6: Validation (00:05-00:20 UTC, 15 min)

**BA Actions**:
- Wait for QA validation completion
- No active monitoring required

**EA Actions**:
1. **00:05-00:20 UTC**: Finalize cost validation report
   - Job 1 cost: $[X.XX]
   - Job 2 cost: $[X.XX]
   - Total cost: $[X.XX]
   - Variance: ±[Y]% (vs $0.85 projected)

2. **00:20 UTC**: Deliver report to CE
   - **File**: `20251212_0020_EA-to-CE_ROUND1_COST_VALIDATION.md`
   - **CC**: BA (for awareness)

**Coordination Point**:
- **00:20**: EA → CE + BA ("Round 1 cost validation complete")

---

## ROUND 2: OPTIMIZATION COORDINATION (00:20-00:30 UTC)

### EA Optimization Analysis (00:20-00:30 UTC)

**EA Actions**:
1. Analyze Round 1 performance data
2. Identify optimization opportunities:
   - Job 1 resource tuning (vCPUs, memory)
   - Job 2 BigQuery cost reduction
   - Parallelization strategies
3. Draft optimization recommendations
4. **00:30 UTC**: Deliver to CE and BA
   - **File**: `20251212_0030_EA-to-CE_ROUND2_OPTIMIZATION_RECOMMENDATIONS.md`
   - **CC**: BA (for implementation)

**BA Actions**:
1. **00:30 UTC**: Receive EA optimization recommendations
2. **00:30-01:00 UTC**: Review and acknowledge
3. **01:00 UTC**: Send response to EA:
   - Accepted recommendations: [List]
   - Rejected recommendations: [List with rationale]
   - Implementation timeline for Round 2

**Coordination Point**:
- **00:30**: EA → BA ("Optimization recommendations delivered")
- **01:00**: BA → EA ("Recommendations acknowledged, [X]% accepted")

---

## ESCALATION PROTOCOL

### When EA Should Alert BA Immediately

1. **Cost Variance >±20%**: Actual cost exceeds acceptable range
2. **Duration Variance >+25%**: Execution significantly delayed
3. **Resource Exhaustion**: CPU >98% or Memory >95% sustained
4. **BigQuery Failure**: 667-table JOIN fails or times out
5. **Checkpoint Count Mismatch**: Job 1 produces <660 or >670 files

### When BA Should Alert EA Immediately

1. **Execution Failure**: Job 1 or Job 2 exits with non-zero code
2. **GCS Permission Error**: Cannot write checkpoints or training file
3. **BigQuery Permission Error**: Cannot create temp tables or run queries
4. **Timeout Risk**: Job approaching timeout limit (>90% of max duration)

### Alert Format

**Subject**: `[ALERT] [Job 1/Job 2] [Issue Description]`

**Body**:
```
Issue: [Brief description]
Severity: [HIGH / MEDIUM / LOW]
Impact: [Cost / Timeline / Quality]
Recommendation: [Immediate action needed]
```

**Example**:
```
[ALERT] [Job 1] Cost Variance Exceeds +20%

Issue: Job 1 actual cost $0.42 vs $0.34 projected (+24% variance)
Severity: HIGH
Impact: $2.24 additional cost for 28 pairs
Recommendation: Review resource allocation before Round 2
```

---

## COMMUNICATION CHANNELS

### Real-Time Updates (During Execution)

**Channel**: Agent communication files
**Format**: `YYYYMMDD_HHMM_[EA/BA]-to-[BA/EA]_[SUBJECT].md`

**Example**:
- `20251212_2255_EA-to-BA_JOB1_COST_TRAJECTORY.md`
- `20251212_2350_BA-to-EA_JOB1_COMPLETION.md`

### Post-Execution Reports

**Channel**: Agent outboxes → CE inbox (CC to other agent)
**Format**: Comprehensive reports for CE decision-making

**Example**:
- `20251212_0020_EA-to-CE_ROUND1_COST_VALIDATION.md` (CC: BA)
- `20251212_0030_EA-to-CE_ROUND2_OPTIMIZATION_RECOMMENDATIONS.md` (CC: BA)

---

## SUCCESS CRITERIA

### Coordination Quality Metrics

✅ **Timely Notifications**: All coordination points met within ±2 min
✅ **Information Accuracy**: Cost/duration projections within ±20%
✅ **Proactive Alerting**: Issues escalated before >±20% variance
✅ **Mutual Understanding**: No misalignment on Round 2 implementation

### EA-BA Collaboration (v2.0.0)

✅ **EA provides actionable insights**: ≥70% of recommendations implemented by BA
✅ **BA provides timely data**: All notifications within ±5 min of milestone
✅ **Zero surprises**: All variances >±10% communicated in advance
✅ **Round 2 readiness**: Optimizations approved and implemented before execution

---

## TIMELINE SUMMARY

| Time | BA Action | EA Action | Coordination |
|------|-----------|-----------|--------------|
| **22:00** | Start container builds | Monitor builds | None |
| **22:20** | Deploy jobs | Verify config | "Deployment complete" |
| **22:40** | Execute Job 1 | Start monitoring | "Job 1 started" |
| **22:55** | Monitor logs | Interim report | Cost trajectory |
| **23:15** | Monitor logs | Interim report | Cost update |
| **23:35** | Monitor logs | Interim report | Cost update |
| **23:50** | Job 1 complete, execute Job 2 | Switch monitoring | "Job 1 complete" |
| **00:05** | Job 2 complete | Calculate cost | "Job 2 complete" |
| **00:20** | Wait for validation | Deliver report | Cost validation |
| **00:30** | Review recommendations | Deliver optimization | Recommendations |
| **01:00** | Acknowledge EA report | Wait for response | Implementation plan |

---

## AUTHORIZATION

**CE Directive**: EA and BA MUST coordinate on bifurcated deployment
**EA Authority**: Monitor, analyze, recommend (no implementation)
**BA Authority**: Implement, execute, deploy (no cost analysis)
**Shared Responsibility**: Round 1 success, Round 2 optimization

---

**Chief Engineer (CE)**

**Purpose**: Ensure seamless EA-BA coordination for bifurcated Cloud Run deployment

**Success**: Round 1 executed flawlessly, Round 2 optimized based on data

---

**END OF COORDINATION PROTOCOL**
