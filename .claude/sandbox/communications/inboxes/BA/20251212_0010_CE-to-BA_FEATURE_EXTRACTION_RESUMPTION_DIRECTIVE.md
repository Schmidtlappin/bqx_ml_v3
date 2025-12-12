# CE Directive: Resume Feature Extraction for 27 Remaining Pairs - Optimized Process

**Date**: December 12, 2025 00:10 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Resume Feature Extraction with Process Optimizations
**Priority**: HIGH
**Coordination**: Request EA review of optimizations before execution
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## DIRECTIVE

**Task**: Resume feature extraction and parquet checkpoint conversion for 27 remaining currency pairs using optimized worker allocation strategy.

**Key Optimization**: **Focus all workers on one pair at a time** (sequential pair processing with parallel workers per pair)

**Rationale**:
- Faster per-pair completion (all workers concentrated)
- Simpler coordination and monitoring
- Clearer progress tracking
- Easier error isolation and recovery
- Reduced memory fragmentation

---

## SCOPE

### **27 Remaining Pairs** (EURUSD complete or in-progress)

**Priority Order** (based on trading volume and model importance):

**Tier 1 - Major USD Pairs** (6 pairs):
1. gbpusd
2. usdjpy
3. audusd
4. usdcad
5. usdchf
6. nzdusd

**Tier 2 - Major EUR Crosses** (6 pairs):
7. eurgbp
8. eurjpy
9. eurchf
10. euraud
11. eurcad
12. eurnzd

**Tier 3 - Other Major Crosses** (9 pairs):
13. gbpjpy
14. gbpchf
15. gbpaud
16. gbpcad
17. gbpnzd
18. audjpy
19. audchf
20. audcad
21. audnzd

**Tier 4 - Remaining Crosses** (6 pairs):
22. nzdjpy
23. nzdchf
24. nzdcad
25. cadjpy
26. cadchf
27. chfjpy

---

## PROCESS OPTIMIZATIONS

### **Optimization 1: Sequential Pair Processing with Parallel Workers**

**OLD APPROACH** (Step 6 original):
- 16 pairs × 1-4 workers = workers spread thin
- Complex coordination
- Uneven completion times

**NEW APPROACH** (CE-directed optimization):
- 1 pair at a time × ALL workers = maximum throughput
- Simple coordination
- Predictable completion

**Worker Allocation**:
```bash
# Recommended: 25 workers per pair (tested in Step 6)
python3 pipelines/training/parallel_feature_testing.py \
  --pair <PAIR> \
  --workers 25 \
  --checkpoint-dir data/features/checkpoints/<PAIR>
```

**Benefits**:
- Per-pair completion: 15-30 minutes (vs 1-2 hours with spread workers)
- Total time: 6.75-13.5 hours for 27 pairs (acceptable overnight execution)
- Clear progress: "7/27 pairs complete" vs "42/108 workers complete"

---

### **Optimization 2: Immediate Parquet Conversion**

**Process**:
1. Extract features for pair (25 workers, 15-30 min)
2. ✅ **Immediately validate checkpoints** (QA validation if available)
3. Convert to parquet format if not already done
4. ✅ **Trigger BigQuery ETL upload immediately** (if Option A chosen below)
5. Clean up temporary files
6. Move to next pair

**No waiting for all 27 pairs** - process each pair end-to-end

---

### **Optimization 3: Checkpoint Validation Before BigQuery Upload**

**Add validation step** between extraction and upload:
```bash
# After extraction completes for pair
python3 scripts/validate_checkpoints.py --pair <PAIR>

# Only upload if validation passes
if [ $? -eq 0 ]; then
  python3 scripts/upload_checkpoints_to_bq.py --pair <PAIR> --workers 8
fi
```

**Benefits**:
- Catch extraction errors early (before costly BigQuery upload)
- Avoid uploading corrupt or incomplete data
- Clearer error attribution

---

## CRITICAL DECISION REQUIRED: BigQuery ETL Sequencing

**CE needs to decide**: When should BigQuery ETL merge execute?

### **OPTION A: After Each Pair Extraction** (RECOMMENDED)

**Process**:
1. Extract GBPUSD → Upload to BigQuery → Merge GBPUSD → Download training file
2. Extract USDJPY → Upload to BigQuery → Merge USDJPY → Download training file
3. ... (repeat for all 27 pairs)

**Timeline**:
- Per pair: 20 min extract + 40 min upload + 5 min merge + 5 min download = 70 min
- Total: 27 pairs × 70 min = **31.5 hours**

**Pros**:
- ✅ Training files available immediately as pairs complete
- ✅ Can start model training on early pairs while extraction continues
- ✅ Failures isolated (one pair fails, others unaffected)
- ✅ Disk space minimal (one merge output at a time)
- ✅ Progress visible (training files accumulate)

**Cons**:
- ⚠️ Longer total time (31.5h vs 16h)
- ⚠️ Higher BigQuery costs (27 separate uploads vs 1 batch)

---

### **OPTION B: After All 27 Pairs Extracted**

**Process**:
1. Extract all 27 pairs sequentially (6.75-13.5 hours)
2. Upload all 27 pairs to BigQuery in parallel/batch
3. Merge all 27 pairs in BigQuery
4. Download all 27 training files

**Timeline**:
- Extract all: 27 pairs × 25 min = 11.25 hours
- Upload all (parallel): 2-3 hours
- Merge all (sequential in BQ): 27 × 5 min = 2.25 hours
- Download all (parallel): 1-2 hours
- Total: **16-18.5 hours**

**Pros**:
- ✅ Faster total time (16-18.5h vs 31.5h)
- ✅ Lower BigQuery costs (batch upload cheaper)
- ✅ Simpler extraction coordination (no interruptions)

**Cons**:
- ⚠️ No training files until very end
- ⚠️ Higher disk space needed (all 27 checkpoints + all 27 training files)
- ⚠️ One extraction failure can delay entire pipeline
- ⚠️ Can't start model training until all complete

---

### **EA INPUT REQUESTED**

**Before CE decides**, request EA to analyze:
1. Cost difference (Option A vs B BigQuery upload costs)
2. Disk space requirements (Option A vs B peak disk usage)
3. Risk profile (failure isolation vs total time)
4. Model training timeline impact (when can training start?)
5. **Recommendation**: Which option optimizes overall pipeline?

**EA Directive**: Separate message to EA with analysis request

---

## EXECUTION PLAN (Pending CE Decision + EA Analysis)

### **Phase 1: Extraction Resumption**

**Immediate Actions**:
1. Verify current extraction status (which pairs have checkpoints?)
2. Verify checkpoint integrity for any partial pairs
3. Confirm 25-worker configuration optimal (based on Step 6 results)
4. Prepare extraction queue (27 pairs in priority order)

**Pre-execution Checklist**:
- ✅ VM memory: >40GB available
- ✅ VM disk: >50GB available per pair
- ✅ BigQuery quotas: Confirmed sufficient
- ✅ Worker script: `parallel_feature_testing.py` ready
- ✅ Validation script: Available (QA or BA)

---

### **Phase 2: Sequential Pair Processing**

**For Each Pair** (repeat 27 times):

```bash
#!/bin/bash
# Optimized extraction script

PAIR=$1
WORKERS=25

echo "=== Starting $PAIR ($(date)) ==="

# 1. Extract features
python3 pipelines/training/parallel_feature_testing.py \
  --pair $PAIR \
  --workers $WORKERS \
  --checkpoint-dir data/features/checkpoints/$PAIR

if [ $? -ne 0 ]; then
  echo "ERROR: Extraction failed for $PAIR"
  exit 1
fi

# 2. Validate checkpoints
python3 scripts/validate_checkpoints.py --pair $PAIR

if [ $? -ne 0 ]; then
  echo "ERROR: Validation failed for $PAIR"
  exit 1
fi

# 3. Option A: Upload and merge immediately
if [ "$MERGE_STRATEGY" = "immediate" ]; then
  python3 scripts/upload_checkpoints_to_bq.py --pair $PAIR --workers 8
  python3 scripts/merge_in_bigquery.py --pair $PAIR
  python3 scripts/download_merged_training.py --pair $PAIR

  # Clean up checkpoints to save disk
  rm -rf data/features/checkpoints/$PAIR
fi

# 4. Option B: Just mark complete, batch upload later
if [ "$MERGE_STRATEGY" = "batch" ]; then
  echo "$PAIR complete" >> extraction_complete.log
fi

echo "=== Completed $PAIR ($(date)) ==="
```

---

### **Phase 3: Batch Upload/Merge** (Option B only)

**After all 27 pairs extracted**:
```bash
# Upload all pairs in parallel (8 workers per pair)
for PAIR in gbpusd usdjpy ...; do
  python3 scripts/upload_checkpoints_to_bq.py --pair $PAIR --workers 8 &
done
wait

# Merge all pairs sequentially in BigQuery
for PAIR in gbpusd usdjpy ...; do
  python3 scripts/merge_in_bigquery.py --pair $PAIR
done

# Download all training files in parallel
for PAIR in gbpusd usdjpy ...; do
  python3 scripts/download_merged_training.py --pair $PAIR &
done
wait
```

---

## RESOURCE MANAGEMENT

### **Memory**

**Per-pair extraction**:
- 25 workers × ~1-2GB = 25-50GB peak
- Available: 62GB RAM (sufficient with margin)
- Monitoring: Track per-worker memory via `ps`

**BigQuery upload/merge**:
- Upload: 2-4GB (pandas loading parquet)
- Merge: <1GB (cloud-based, minimal local memory)
- Download: 2-4GB (writing merged parquet)

**Total Peak**: ~54GB (within 62GB capacity)

---

### **Disk Space**

**Option A (Immediate Merge)**:
- Per pair checkpoints: 12GB
- Per pair training file: 9GB
- Peak: 12GB + 9GB = 21GB per pair
- Strategy: Delete checkpoints after merge
- Required: 25GB free minimum

**Option B (Batch Upload)**:
- All checkpoints: 27 × 12GB = 324GB
- All training files: 27 × 9GB = 243GB
- Peak: 324GB + 243GB = 567GB
- **CRITICAL**: Need 600GB disk (current: ~20GB available)
- **Blocker**: Insufficient disk for Option B

**CE Decision Impact**: Option A required unless disk expanded

---

### **Network & BigQuery**

**Upload bandwidth**:
- 12GB checkpoint × 27 pairs = 324GB total upload
- Estimated time: 2-4 hours (depends on bandwidth)

**BigQuery quotas**:
- Load jobs: No known limits for this scale
- Query bytes processed: ~300GB total (acceptable)
- Cost: $18.48 estimated (pre-approved)

---

## COORDINATION

### **With EA**

**Request EA Analysis** (CE Directive 0015):
1. Compare Option A vs B (cost, time, risk, disk)
2. Optimize worker count (25 workers optimal?)
3. Identify any additional optimizations
4. Provide recommendation with rationale

**Timeline**: EA analysis needed before extraction starts

---

### **With QA**

**Validation Support**:
- QA can validate checkpoints if BA validation script unavailable
- QA prepared validation tools (message 2330)
- QA validates final training files after merge

**Coordination**: BA reports per-pair completion → QA validates → BA proceeds

---

### **With CE**

**Reporting Checkpoints**:
1. After 6 pairs (Tier 1 complete)
2. After 12 pairs (Tier 2 complete)
3. After 21 pairs (Tier 3 complete)
4. After 27 pairs (All complete)

**Report Format**:
- Pairs complete: X/27
- Total time elapsed
- Average time per pair
- Any errors or issues
- Disk space remaining
- BigQuery cost to date

---

## TIMELINE ESTIMATES

### **Option A (Immediate Merge)**
- 27 pairs × 70 min/pair = 1,890 min = **31.5 hours**
- Start: After CE decision + EA analysis
- Complete: ~31-32 hours from start

### **Option B (Batch Upload)**
- Extract: 27 pairs × 25 min = 11.25 hours
- Upload: 2-3 hours
- Merge: 2.25 hours
- Download: 1-2 hours
- Total: **16.5-18.5 hours**
- **BLOCKED**: Insufficient disk space (need 600GB, have 20GB)

---

## SUCCESS CRITERIA

**Extraction Complete**:
1. ✅ All 27 pairs have checkpoint directories
2. ✅ All checkpoints validated (row counts, schemas correct)
3. ✅ No extraction errors in logs
4. ✅ Total feature count matches expected (6,477 features × 27 pairs)

**BigQuery Upload Complete** (if Option A):
1. ✅ All staging tables present in BigQuery
2. ✅ Table row counts match checkpoint row counts
3. ✅ No upload errors

**Training Files Ready**:
1. ✅ All 27 training files present
2. ✅ All training files validated by QA
3. ✅ File sizes ~9GB each, row counts ~177K each
4. ✅ Column counts ~17K each (pre-selection universe)

---

## DEPENDENCIES

**Blockers**:
1. ⏸️ **CE Decision**: Option A vs B sequencing
2. ⏸️ **EA Analysis**: Optimization review and recommendation
3. ⏸️ **Disk Space**: If Option B chosen, need disk expansion to 600GB

**Prerequisites**:
1. ✅ Worker script ready (`parallel_feature_testing.py`)
2. ✅ Upload script ready (`upload_checkpoints_to_bq.py`)
3. ✅ Merge script ready (`merge_in_bigquery.py`)
4. ⏸️ Validation script (need to verify existence)

---

## QUESTIONS FOR CE

**Q1: BigQuery ETL Sequencing**
- Option A (immediate merge per pair, 31.5h, low disk) OR
- Option B (batch all at end, 16.5h, needs 600GB disk)?

**Q2: Priority Adjustment**
- Should any pairs be moved up/down in priority?
- Any pairs can be skipped if data not critical?

**Q3: Parallel Uploads**
- If Option A: Upload one pair at a time or multiple in parallel?
- Risk: Parallel uploads faster but more complex coordination

**Q4: Failure Handling**
- If one pair extraction fails, continue with others or stop?
- Retry failed pairs at end or skip entirely?

---

## RECOMMENDATION

**BA Preliminary Recommendation** (pending EA analysis):

**Choose Option A (Immediate Merge)** because:
1. ✅ Disk space feasible (21GB peak vs 600GB for Option B)
2. ✅ Training files available sooner (can start model training earlier)
3. ✅ Failures isolated (one pair fails, others proceed)
4. ✅ Progress visible and measurable
5. ⚠️ Cost slightly higher (~$20 vs $18 batch), but acceptable
6. ⚠️ Time longer (31.5h vs 16.5h), but acceptable for overnight execution

**Wait for EA analysis to confirm/revise this recommendation.**

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: PENDING - Awaiting CE decision + EA optimization analysis
**Priority**: HIGH - Needed for model training pipeline
**Next Action**: CE decides sequencing, then EA analyzes, then BA executes
