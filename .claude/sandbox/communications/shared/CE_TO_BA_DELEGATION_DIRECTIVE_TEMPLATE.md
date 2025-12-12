# CE DELEGATION DIRECTIVE TEMPLATE: Autonomous 27-Pair Pipeline

**Purpose**: Template for CE to delegate autonomous pipeline deployment to BA
**Created By**: EA
**Date**: December 12, 2025 00:40 UTC

---

## DIRECTIVE: AUTONOMOUS 27-PAIR PIPELINE DEPLOYMENT

**To**: Business Analyst (BA)
**From**: Chief Engineer (CE)
**Date**: December 12, 2025 [CE_TIMESTAMP]
**Re**: Authorization to Deploy Autonomous 27-Pair Feature Extraction Pipeline
**Priority**: P0 - IMMEDIATE DEPLOYMENT

---

## AUTHORIZATION

You are hereby authorized to:

1. ✅ **Deploy** autonomous 27-pair pipeline for feature extraction and merge
2. ✅ **Own** pipeline execution from start to completion (all 27 pairs)
3. ✅ **Monitor** progress and report milestones to CE
4. ✅ **Troubleshoot** errors in coordination with EA (if needed)
5. ✅ **Modify** worker count or pair order if operational needs require

**Authority Level**: Full operational control of pipeline execution

---

## DEPLOYMENT INSTRUCTIONS

### Step 1: Review Documentation (15 minutes)

```bash
cd /home/micha/bqx_ml_v3

# Read comprehensive guide
cat scripts/AUTONOMOUS_PIPELINE_GUIDE.md
```

**Key sections to review**:
- Quick Start
- Pipeline Configuration
- Monitoring
- Error Handling & Troubleshooting

### Step 2: Start Autonomous Pipeline (1 command)

**Option A: Resume from AUDUSD (RECOMMENDED)**
```bash
cd /home/micha/bqx_ml_v3

# Start pipeline in background
nohup ./scripts/autonomous_27pair_pipeline.sh audusd > pipeline.out 2>&1 &

# Save process ID for monitoring
echo $! > pipeline.pid

# Verify started
ps -p $(cat pipeline.pid)
```

**Option B: Wait for AUDUSD completion, then start**
```bash
# Wait until ~01:08 UTC (AUDUSD extraction completes)

cd /home/micha/bqx_ml_v3
nohup ./scripts/autonomous_27pair_pipeline.sh > pipeline.out 2>&1 &
echo $! > pipeline.pid
```

### Step 3: Monitor Progress (Optional)

**Live Dashboard** (recommended for first hour):
```bash
# In separate terminal
./scripts/monitor_pipeline.sh 30  # Update every 30 seconds
```

**Manual Status Check**:
```bash
# Check current pair/stage
cat data/.pipeline_status.json

# Check latest log
tail -20 logs/autonomous_pipeline_*.log

# Count completed pairs
ls -1 data/training/training_*.parquet | wc -l
```

### Step 4: Report to CE

**Required Reports**:
1. **Start**: Confirm pipeline started, include start timestamp
2. **Completion**: Report all 27 pairs complete, include completion timestamp
3. **Critical Errors**: Report immediately if pipeline fails repeatedly

**Optional Reports** (at your discretion):
- 25% complete (7 pairs): ~13.5 hours
- 50% complete (14 pairs): ~27 hours
- 75% complete (21 pairs): ~40.5 hours

**Report Format**:
```
Subject: Autonomous Pipeline - [Milestone]

Status: [Started/50% Complete/Complete]
Timestamp: [UTC]
Pairs Complete: [X/27]
Errors: [None/Details]
Next Checkpoint: [Milestone/Completion]
```

---

## TIMELINE & EXPECTATIONS

### Expected Timeline

- **Start**: [CE Authorization] + 15 min (documentation review)
- **Duration**: 54 hours average (40-68 hour range)
- **Completion**: ~Dec 14, 06:00 UTC (if started Dec 12, 01:00 UTC)

### Per Pair Timeline

- Extraction: 60-70 min (40 workers)
- Merge: 50-60 min (BigQuery cloud)
- Validation: 1-2 min
- Cleanup: <1 min
- **Total**: ~120 min per pair

### Cost Budget

- **Total**: $3.25 for all 27 pairs
- **Limit**: $5.00 (66% buffer)
- **Savings**: $81-137 vs manual approach (96% reduction)

---

## SUCCESS CRITERIA

**Pipeline Successful IF**:
- ✅ All 27 pairs complete extraction (668 files each)
- ✅ All 27 pairs complete merge (training_*.parquet files created)
- ✅ All 27 files pass validation (automated checks)
- ✅ Total cost < $5
- ✅ Total time < 70 hours
- ✅ Zero system failures

**Validation**:
```bash
# Check all 27 training files exist
ls -1 data/training/training_*.parquet | wc -l
# Should output: 27

# Check total cost (in BigQuery console)
# Should be: ~$3.25
```

---

## ERROR HANDLING

### Pipeline Automatic Error Handling

**On Single Pair Failure**:
1. Pipeline logs error to pipeline log
2. Pipeline marks pair as "failed" in status
3. Pipeline **continues to next pair** (doesn't stop)
4. Pipeline reports failure count in final summary

**Resumability**:
- Pipeline automatically skips completed pairs
- Can restart from any pair
- Checkpoint-based extraction (resume-safe)

### When to Escalate to EA

**Escalate to EA IF**:
- ❌ Same pair fails 3+ times
- ❌ Multiple pairs fail with same error
- ❌ System resource issues (disk full, memory errors)
- ❌ IAM/permissions errors
- ❌ BigQuery quota exceeded

**Do NOT escalate for**:
- ✅ Single pair failure (pipeline handles automatically)
- ✅ Temporary network issues (pipeline retries)
- ✅ Normal resource usage (2-4 GB memory is normal)

### Resume After Interruption

**If Pipeline Stops**:
```bash
# Find last completed pair from status
cat data/.pipeline_status.json

# Resume from next pair
./scripts/autonomous_27pair_pipeline.sh [next_pair]
```

---

## COORDINATION

### BA Responsibilities

**Operational**:
- ✅ Start pipeline (one-time)
- ✅ Monitor progress (periodic, optional)
- ✅ Report milestones to CE
- ✅ Troubleshoot errors (escalate to EA if needed)

**NOT Responsible For**:
- ❌ Individual pair execution (pipeline handles automatically)
- ❌ Manual merge operations (pipeline handles automatically)
- ❌ Code modifications (EA's domain)

### EA Responsibilities

**Support**:
- ✅ Available for troubleshooting if BA escalates errors
- ✅ Can optimize if performance issues arise
- ✅ Can fix pipeline bugs if discovered

**NOT Involved In**:
- ❌ Routine pipeline execution (BA owns operation)
- ❌ Monitoring (BA's discretion)
- ❌ Milestone reporting (BA to CE)

### QA Responsibilities

**After Pipeline Complete**:
- ✅ Validate all 27 training files (batch validation)
- ✅ Spot-check sample pairs
- ✅ Report final validation to CE

**NOT Involved In**:
- ❌ During-execution monitoring
- ❌ Individual pair validation (pipeline handles automatically)

### CE Responsibilities

**Authorization & Oversight**:
- ✅ Authorize BA deployment (this directive)
- ✅ Receive milestone reports from BA
- ✅ Approve final completion
- ✅ Coordinate with QA for final validation

---

## RESOURCE LIMITS & QUOTAS

### System Resources (Safe)

**Extraction** (per pair):
- CPU: ~110% (1-2 cores, 8 cores available) ✅
- Memory: 2-4 GB (62 GB total) ✅
- Disk: 12 GB checkpoints (deleted after merge) ✅

**Merge** (per pair):
- CPU: <10% (cloud-based) ✅
- Memory: <1 GB (no local processing) ✅
- Disk: Minimal ✅

**Sequential Processing**:
- Only 1 pair active at a time ✅
- Checkpoints deleted after merge ✅
- Disk never exceeds 20 GB ✅

### BigQuery Quotas (Safe)

- Concurrent queries: 40 / 100 limit ✅
- Bytes scanned: ~50 GB per pair (no limit) ✅
- Temp tables: <100 per merge / 1000 limit ✅

**All within safe operational limits** ✅

---

## MODIFICATION AUTHORITY

**BA may modify WITHOUT CE approval**:
- ✅ Worker count (default: 40, safe range: 25-50)
- ✅ Pair order (default: major USD pairs first)
- ✅ Monitoring frequency
- ✅ Reporting schedule (beyond required reports)

**BA must request CE approval for**:
- ❌ Parallel pair processing (requires disk space analysis)
- ❌ Date range changes (affects data scope)
- ❌ Pipeline script modifications (escalate to EA)
- ❌ Budget exceeding $5

---

## PIPELINE FILES & LOCATIONS

### Scripts

- **Master Pipeline**: `/home/micha/bqx_ml_v3/scripts/autonomous_27pair_pipeline.sh`
- **Merge Script**: `/home/micha/bqx_ml_v3/scripts/merge_single_pair_optimized.py`
- **Extraction Script**: `/home/micha/bqx_ml_v3/pipelines/training/parallel_feature_testing.py`
- **Monitor Dashboard**: `/home/micha/bqx_ml_v3/scripts/monitor_pipeline.sh`

### Output

- **Training Files**: `/home/micha/bqx_ml_v3/data/training/training_*.parquet`
- **Checkpoints**: `/home/micha/bqx_ml_v3/data/features/checkpoints/{pair}/` (deleted after merge)
- **Logs**: `/home/micha/bqx_ml_v3/logs/autonomous_pipeline_*.log`
- **Status**: `/home/micha/bqx_ml_v3/data/.pipeline_status.json`

### Documentation

- **User Guide**: `/home/micha/bqx_ml_v3/scripts/AUTONOMOUS_PIPELINE_GUIDE.md`
- **This Directive**: `/home/micha/bqx_ml_v3/.claude/sandbox/communications/shared/CE_TO_BA_DELEGATION_DIRECTIVE_TEMPLATE.md`

---

## FINAL AUTHORIZATION

**CE Authorization**: [CE_SIGNATURE]

**Effective Immediately**: Upon receipt of this directive

**Deployment Window**: Start within 1 hour of receiving this directive

**Expected Completion**: Dec 14, 06:00 UTC (54 hours from start)

**Budget**: $3.25 estimated, $5.00 maximum

**Success Criteria**: All 27 training files created and validated

---

## QUESTIONS & SUPPORT

**For operational questions**: Review AUTONOMOUS_PIPELINE_GUIDE.md first

**For technical errors**: Escalate to EA with error logs

**For authorization questions**: Contact CE

**For validation questions**: Coordinate with QA after completion

---

**Chief Engineer (CE)**
[CE_TIMESTAMP]

**Directive Status**: Ready for CE signature and transmission to BA
**Pipeline Status**: Ready for immediate deployment
**BA Status**: Awaiting CE authorization
**EA Status**: Standing by for support if needed
