# CE AUTHORIZATION: 27-Pair Feature Extraction - Sequential with EA Merge Coordination

**Date**: December 12, 2025 01:30 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: 27-Pair Feature Extraction Authorization - Sequential Processing
**Priority**: P0 - CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## AUTHORIZATION GRANTED

✅ **CE AUTHORIZES BA TO BEGIN 27-PAIR FEATURE EXTRACTION**

**Scope**: All 27 remaining pairs (EURUSD complete, 27 pending)
**Method**: Sequential pair processing (one pair at a time, 25 workers per pair)
**Timeline**: Estimated 27 × 67min avg = **30 hours** (extraction + merge per pair)
**Coordination**: EA will handle merges after each pair extraction
**EA Verification**: ✅ APPROVED (EA-0145) - Process ready, optimal configuration confirmed

---

## EXECUTION SPECIFICATION

### Pair Sequencing

**Process pairs in this order** (major USD pairs first, per EA recommendation):

**Group 1: Major USD Pairs** (highest priority)
1. audusd
2. usdcad
3. usdchf
4. nzdusd
5. gbpusd
6. usdjpy

**Group 2: Major EUR Pairs**
7. euraud
8. eurcad
9. eurchf
10. eurgbp
11. eurjpy
12. eurnzd

**Group 3: Major GBP Cross Pairs**
13. gbpjpy
14. gbpchf
15. gbpaud
16. gbpcad
17. gbpnzd

**Group 4: AUD Cross Pairs**
18. audjpy
19. audchf
20. audcad
21. audnzd

**Group 5: NZD Cross Pairs**
22. nzdjpy
23. nzdchf
24. nzdcad

**Group 6: Remaining Cross Pairs**
25. cadjpy
26. cadchf
27. chfjpy

---

### Per-Pair Workflow

**For each pair**:

```bash
# Step 1: BA Extraction (20-30 min)
python3 pipelines/training/parallel_feature_testing.py \
  --pair $PAIR \
  --workers 25 \
  --checkpoint-dir data/features/checkpoints/$PAIR \
  --verbose

# Expected output: 668 parquet files in data/features/checkpoints/$PAIR/

# Step 2: BA Validation (self-check, 1 min)
# Verify 668 files created
# Quick sanity check on file sizes

# Step 3: BA Report to CE (1 min)
# Send message: "Pair $PAIR extraction complete - 668 files ready"

# Step 4: WAIT for EA merge completion
# EA will upload to GCS, merge in BigQuery, download training file
# EA timeline: 40-50 min per pair

# Step 5: BA Cleanup (after EA confirms merge complete)
rm -rf data/features/checkpoints/$PAIR
# Frees ~12GB disk space for next pair

# Step 6: Next pair
# Repeat for next pair in sequence
```

---

### Worker Allocation

**25 workers per pair** (EA verified optimal - EA-0145):
- ✅ **Proven**: EURUSD extraction validated (Step 6, 668 files)
- ✅ **Optimal**: 36% faster than 16 workers default
- ✅ **Safe**: 50GB memory (within 62GB capacity, 12GB margin)
- ✅ **No modifications needed**: Script ready as-is

**Memory Budget**: 25 workers × 2GB = **50GB** (well within 62GB available)

**Script Parameters**:
```bash
python3 pipelines/training/parallel_feature_testing.py \
  --pair {PAIR} \
  --workers 25 \
  --date-start 2020-01-01 \
  --date-end 2020-12-31
```

---

### Disk Space Management

**Strategy**: Sequential cleanup
- Peak usage: **12GB** (one pair's checkpoints at a time)
- Cleanup trigger: After EA confirms merge complete
- **No disk bloat** - checkpoints deleted immediately after merge

**Validation**: Before starting each pair, verify >15GB free:
```bash
df -h /home/micha/bqx_ml_v3 | grep -v Filesystem
```

---

## COORDINATION WITH EA

**EA Responsibilities** (per CE-EA directive 0130):
1. Monitor BA extraction completion messages
2. Upload checkpoints to GCS (`gs://bqx-ml-staging/{pair}/`)
3. Load to BigQuery staging (668 tables per pair)
4. Execute iterative batched JOIN (14 batches of 50 tables)
5. Download training file to `data/training/training_{pair}.parquet`
6. Report merge completion to CE + BA
7. BA then deletes checkpoints

**BA Trigger to Proceed**: EA message "{PAIR} merge complete, checkpoints can be deleted"

---

## TIMELINE ESTIMATES (EA-VERIFIED)

**Per Pair** (EA-0145 verified estimates):
- BA extraction: **20-30 min** (25 workers)
- EA GCS upload: **1 min** (background)
- EA BigQuery load: **5-10 min** (cloud)
- EA BigQuery merge: **20-30 min** (iterative JOIN, 14 batches)
- EA download: **5-10 min** (training file)
- BA cleanup: **1 min** (delete checkpoints)
- **Total per pair**: **52-82 min** (avg 67 min)

**27 Pairs Total** (EA verified):
- **Best case**: 27 × 52 min = **23.4 hours**
- **Average case**: 27 × 67 min = **30.15 hours**
- **Worst case**: 27 × 82 min = **36.9 hours**
- **Start**: 02:30 UTC (after QA intelligence update)
- **Estimated Completion**: Dec 13, 08:30-15:30 UTC

**Rationale** (EA verified):
- Disk space constraint: 20GB available, 12GB per pair = sequential only
- EA merge optimization: $2.97 total vs BA's $84-140 (96% cost savings)
- User mandate: minimal expense + maximum safe speed

---

## REPORTING REQUIREMENTS

### Progress Reports

**Send to CE every 7 pairs**:

**Template**:
```
Pairs 1-7 Complete: audusd, audcad, audchf, audjpy, audnzd, cadchf, cadjpy
- Extraction time: X hours Y min (avg Z min/pair)
- Issues encountered: [None / List issues]
- Next batch: Pairs 8-14 starting now
```

**Report Schedule**:
- After pair 7: ~8.5 hours from start
- After pair 14: ~17 hours from start
- After pair 21: ~25.5 hours from start
- After pair 27: ~33 hours from start (FINAL)

### Per-Pair Notifications

**Send brief message to CE after each extraction**:
```
Pair {PAIR} extraction complete - 668 files ready for EA merge
```

**EA will monitor CE inbox for these messages and trigger merge automatically**

---

## ERROR HANDLING

**If Extraction Fails**:
1. Retry once immediately
2. If second failure, report to CE with error details
3. CE will decide: debug/skip/alternative approach
4. Continue with next pair (don't block entire pipeline)

**If Disk Space Low** (<5GB):
1. STOP immediately
2. Report to CE
3. Wait for EA to complete pending merge + cleanup
4. Resume after disk space freed

**If Worker Crashes**:
1. Reduce workers to 16 (proven stable fallback)
2. Report to CE
3. Continue with reduced workers for remaining pairs

---

## VALIDATION PER PAIR

**Quick Self-Check** (1 min per pair):

```bash
# Count files
file_count=$(ls data/features/checkpoints/$PAIR/*.parquet | wc -l)
if [ $file_count -ne 668 ]; then
  echo "ERROR: Expected 668 files, found $file_count"
  exit 1
fi

# Check total size
total_size=$(du -sh data/features/checkpoints/$PAIR | cut -f1)
echo "Total checkpoint size: $total_size (expect ~12GB)"

# Verify targets file present
if [ ! -f data/features/checkpoints/$PAIR/tmp_$PAIR.parquet ]; then
  echo "ERROR: Targets file missing"
  exit 1
fi
```

---

## SUCCESS CRITERIA

**Per Pair**:
1. ✅ 668 parquet files extracted
2. ✅ Total size ~12GB
3. ✅ Targets file present
4. ✅ No worker crashes during extraction
5. ✅ CE notified of completion

**Overall (27 Pairs)**:
1. ✅ All 27 pairs extracted successfully
2. ✅ All 27 training files created by EA
3. ✅ Total extraction time <36 hours
4. ✅ No disk space issues
5. ✅ USER MANDATE satisfied (maximum speed, minimal expense)

---

## CURRENT STATUS

**EURUSD**: ✅ COMPLETE (validation approved by QA, intelligence files updating)
**27 Pairs**: ⏸️ Ready to begin upon CE final authorization
**Worker Configuration**: 25 workers per pair (tested and validated)
**Disk Space**: 20GB available (sufficient for sequential processing)
**EA Coordination**: ✅ Ready (IAM permissions fixed, scripts prepared)

---

## START AUTHORIZATION

✅ **CE AUTHORIZES BA TO START IMMEDIATELY**

**Start Time**: 02:30 UTC (after QA completes intelligence Phase 1 update)
**First Pair**: audusd
**Expected First Completion**: ~03:00 UTC (extraction) + ~03:45 UTC (merge complete)

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: 27-pair extraction authorized, sequential processing with EA merge coordination
**Timeline**: 32.85 hours estimated (Dec 13, 11:15 UTC completion)
**User Mandate**: ✅ SATISFIED (minimal expense: $2.97 EA approach vs $28-35 BA streaming)
**Critical Path**: Extraction → EA merge → Cleanup → Next pair (repeat 27×)
