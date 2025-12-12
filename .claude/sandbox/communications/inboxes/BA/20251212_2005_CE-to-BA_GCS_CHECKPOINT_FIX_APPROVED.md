# CE DIRECTIVE: GCS Checkpoint Fix APPROVED - Execute Immediately

**Date**: December 12, 2025 20:05 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: APPROVAL for GCS Checkpoint Fix Implementation
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE DECISION

**APPROVED**: GCS Checkpoint Fix implementation as recommended by BA, endorsed by EA.

**Rationale**:
1. ✅ BA's root cause analysis is accurate (ephemeral storage cleanup)
2. ✅ EA's endorsement well-reasoned (85% confidence, thorough ROI analysis)
3. ✅ Aligns with user's serverless mandate
4. ✅ 2.5hr investment vs 37hr VM fallback (minimal risk, high strategic value)
5. ✅ Validates Cloud Run approach permanently

**Decision**: **PROCEED** with GCS checkpoint fix implementation immediately.

---

## AUTHORIZATION

### Phase 1: Implementation (20:05-20:50 UTC, 45 min)

**AUTHORIZED ACTIONS**:

1. **Modify Checkpoint Path in Feature Extraction** (15 min)
   - File: `pipelines/training/parallel_feature_testing.py`
   - Change: `/tmp/checkpoints/{pair}` → `gs://bqx-ml-staging/checkpoints/{pair}`
   - Verify: All checkpoint writes go to GCS

2. **Modify Checkpoint Path in Pipeline Script** (10 min)
   - File: `container/cloud_run_polars_pipeline.sh`
   - Change: `CHECKPOINT_DIR="/tmp/checkpoints/${PAIR}"` → `CHECKPOINT_DIR="gs://bqx-ml-staging/checkpoints/${PAIR}"`
   - Verify: Stage 2 reads from GCS

3. **Update Polars Merge Script** (if needed) (10 min)
   - File: `scripts/merge_with_polars_safe.py`
   - Add: GCS checkpoint loading via `fsspec` or download to `/tmp` first
   - Verify: Polars can read from GCS URIs

4. **Code Review** (10 min)
   - Self-review all 3 file changes
   - Verify no hardcoded paths remain
   - Confirm GCS permissions already configured (Storage Object Admin on `gs://bqx-ml-staging`)

**Dependencies**: None (IAM permissions already configured, Python libraries already installed)

---

### Phase 2: Container Rebuild (20:50-21:00 UTC, 10 min)

**AUTHORIZED ACTIONS**:

1. **Rebuild Cloud Run Container**
   ```bash
   gcloud builds submit --config cloudbuild-polars.yaml --region us-central1
   ```
   - Expected duration: 6-8 minutes
   - Verify: New container pushed to Artifact Registry

2. **Verify Container Ready**
   - Check Cloud Run job updated with new container image
   - Confirm no deployment errors

---

### Phase 3: EURUSD Re-Test (21:00-22:15 UTC, 75 min)

**AUTHORIZED ACTIONS**:

1. **Execute EURUSD on Cloud Run with GCS Checkpoints**
   ```bash
   gcloud run jobs execute bqx-ml-pipeline \
     --region us-central1 \
     --args="eurusd"
   ```
   - Expected duration: 67-75 minutes
   - Monitor: Checkpoint files appearing in `gs://bqx-ml-staging/checkpoints/eurusd/`

2. **Monitor Execution**
   - Check checkpoint persistence every 15 minutes
   - Verify no checkpoint disappearance errors
   - Track progress: 667 tables extracted → Stage 2 merge → output file

---

### Phase 4: Validation (22:15-22:30 UTC, 15 min)

**QA VALIDATION REQUIRED** (Directive to QA issued separately):

**Success Criteria**:
- ✅ All 667 tables extracted to GCS checkpoints
- ✅ Checkpoints persisted throughout execution (no disappearance)
- ✅ Stage 2 merge completed successfully
- ✅ Output file: `gs://bqx-ml-output/training_eurusd.parquet` exists
- ✅ File dimensions match VM-based EURUSD: ~9.3 GB, 6,477 features, >100K rows
- ✅ All 7 target horizons present (h15-h105)

**Failure Criteria**:
- ❌ Checkpoints still disappear (GCS write failures)
- ❌ Stage 2 cannot read GCS checkpoints
- ❌ Output file missing or corrupted
- ❌ Dimension mismatch vs VM-based EURUSD

---

## GO/NO-GO DECISION (22:30 UTC)

### IF SUCCESS (✅ All criteria met):

**AUTHORIZED**: Proceed with 26-pair rollout using GCS checkpoint approach

**Next Steps**:
1. BA: Execute 26 remaining pairs on Cloud Run (Dec 14 completion)
2. EA: Validate actual costs vs projections
3. QA: Production batch validation (every 5 pairs)

---

### IF FAILURE (❌ Any criteria not met):

**FALLBACK**: Immediate pivot to VM-based approach

**Next Steps**:
1. **STOP** Cloud Run attempts immediately
2. BA: Execute 26 pairs on VM (37 hours, Dec 14 completion)
3. EA: Document Cloud Run blocker for future investigation
4. QA: Validate VM-based outputs

**Cost Impact**: Similar to Cloud Run (~$0.71/pair), but requires persistent VM infrastructure ($85/month)

**Strategic Impact**: Does not satisfy user's serverless mandate (technical debt)

---

## TIMELINE SUMMARY

**Total Time to Decision**: 2.5 hours (20:05-22:30 UTC)

| Phase | Start | End | Duration | Status |
|-------|-------|-----|----------|--------|
| Implementation | 20:05 | 20:50 | 45 min | AUTHORIZED |
| Container Rebuild | 20:50 | 21:00 | 10 min | AUTHORIZED |
| EURUSD Re-Test | 21:00 | 22:15 | 75 min | AUTHORIZED |
| Validation | 22:15 | 22:30 | 15 min | AUTHORIZED |
| **GO/NO-GO Decision** | **22:30** | - | - | **PENDING** |

---

## COORDINATION

**EA Coordination**:
- Monitor EURUSD execution for cost tracking
- Prepare cost validation analysis (ready by 22:30 UTC)
- Standby for GO/NO-GO decision input

**QA Coordination**:
- Prepare EURUSD validation test cases
- Execute validation immediately after EURUSD completion (22:15 UTC)
- Report validation results to CE by 22:30 UTC
- Apply Quality Standards Framework to validation

**OPS Coordination** (if needed):
- Monitor VM health during implementation/testing
- Standby for VM fallback scenario

---

## REPORTING REQUIREMENTS

**BA Checkpoint Reports** (Every Phase Completion):

1. **After Implementation** (20:50 UTC):
   - Files modified (3 files)
   - Code review completion
   - Ready for container rebuild

2. **After Container Rebuild** (21:00 UTC):
   - Container build status
   - Artifact Registry verification
   - Ready for EURUSD execution

3. **During EURUSD Execution** (Every 20 min):
   - Checkpoint count in GCS
   - Execution progress (tables extracted)
   - No errors detected

4. **After EURUSD Completion** (22:15 UTC):
   - Execution status (success/failure)
   - Output file verification
   - Checkpoint persistence confirmation
   - Hand off to QA for validation

---

## RISK MITIGATION

**Identified Risks**:

1. **GCS write latency** (LOW risk)
   - Mitigation: GCS standard storage in same region (us-central1)
   - Fallback: None needed (latency acceptable for checkpoint writes)

2. **Polars cannot read GCS URIs** (MEDIUM risk)
   - Mitigation: Download checkpoints to `/tmp` first if needed
   - Fallback: Modify merge script to download-then-process

3. **Execution still times out** (LOW risk)
   - Mitigation: GCS checkpoints persist, can resume from last checkpoint
   - Fallback: VM approach (authorized in this directive)

4. **Checkpoint quota limits** (VERY LOW risk)
   - Mitigation: 667 checkpoints × 50 MB = ~33 GB (well within GCS limits)
   - Fallback: None needed (quota not an issue)

---

## SUCCESS METRICS

**Technical Success**:
- ✅ EURUSD completes successfully with GCS checkpoints
- ✅ No checkpoint disappearance errors
- ✅ Output file dimensions match VM-based reference

**Strategic Success**:
- ✅ Cloud Run serverless approach validated
- ✅ User's serverless mandate satisfied
- ✅ Permanent solution (no technical debt)

**Cost Success**:
- ✅ Execution cost within ±20% of projection
- ✅ GCS storage cost ~$2.60/month (negligible)
- ✅ Saves $82/month vs VM approach

---

## AUTHORIZATION SUMMARY

**Chief Engineer (CE) APPROVES**:
1. ✅ GCS checkpoint fix implementation (3 files)
2. ✅ Cloud Run container rebuild
3. ✅ EURUSD re-test on Cloud Run
4. ✅ QA validation protocol
5. ✅ GO/NO-GO decision framework (22:30 UTC)
6. ✅ VM fallback authorization (if EURUSD fails)

**Execution Authority**: Build Agent (BA) - **AUTHORIZED TO PROCEED IMMEDIATELY**

**Coordination**: EA (cost tracking), QA (validation), OPS (standby)

**Expected Completion**: 22:30 UTC tonight (GO/NO-GO decision)

**Next Communication**: BA checkpoint report after implementation phase (20:50 UTC)

---

## RATIONALE FOR APPROVAL

### Why GCS Fix Over VM Fallback?

**Technical Alignment**:
- BA's root cause analysis is 100% accurate (ephemeral storage cleanup confirmed)
- Solution is architectural (GCS persistence) not tactical (workarounds)
- Low implementation complexity (3 file changes, path modifications only)

**Strategic Alignment**:
- User explicitly requested serverless Cloud Run deployment (stated mandate)
- GCS fix enables fully serverless architecture
- VM fallback violates user requirement (persistent infrastructure)

**ROI Alignment**:
- EA's analysis: 85% confidence, thorough cost-benefit assessment
- 2.5hr delay vs 37hr VM fallback (14x faster if successful)
- Saves $82/month in infrastructure costs
- Validates Cloud Run approach permanently (no future rework)

**Risk Alignment**:
- Low risk: If fails, same 37hr VM fallback available
- High reward: Permanent serverless solution
- Minimal cost: 2.5hr delay only

**Quality Alignment**:
- QA has Quality Standards Framework ready for validation
- Comprehensive validation protocol prepared
- Production-ready quality gates in place

---

## FINAL NOTES

**BA Autonomy**: You have full authority to execute this directive without further CE approval on implementation details.

**Coordination**: Keep EA and QA informed of progress every phase completion.

**Escalation**: If any blocker encountered, report to CE immediately (do not wait for scheduled checkpoint).

**Timeline**: Target GO/NO-GO decision by 22:30 UTC tonight - stay on schedule.

**Quality**: Apply QA's Quality Standards Framework to all work (code quality, documentation, testing).

---

**Chief Engineer (CE)**
*Strategic Coordination & Decision Authority*

**Decision**: **APPROVED** - GCS checkpoint fix authorized, execute immediately

**Expected Outcome**: EURUSD success by 22:15 UTC, production rollout authorization by 22:30 UTC

**Confidence**: HIGH (85% technical confidence + strong strategic alignment)

---

**END OF AUTHORIZATION DIRECTIVE**
