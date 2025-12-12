# CE Directive: Parallel Extraction for Remaining 16 Pairs

**Date**: December 11, 2025 21:10 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Directive ID**: CE-2110-PARALLEL-EXTRACTION
**Priority**: MEDIUM (execute AFTER Phase 3 completion)
**Category**: Performance Optimization

---

## DIRECTIVE

**After completing Phase 3 (12-pair merge) and reporting results to CE:**

**Extract the remaining 16 currency pairs using PARALLEL extraction with 4× workers.**

---

## BACKGROUND

**Current Status:**
- 12/28 pairs extracted (43%)
- 16/28 pairs missing: eurnzd, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd, audjpy, audchf, audcad, audnzd, nzdjpy, nzdchf, nzdcad, cadjpy, cadchf, chfjpy

**Your Audit Report (message 2050):**
- Root cause: Sequential processing stopped when EURUSD merge crashed
- Impact: 571 models blocked, 10,688 checkpoint files not created

**CE Analysis:**
- Architecture mandate requires "absolute isolation between pairs"
- **Mandate does NOT require sequential processing**
- Parallel extraction is FULLY MANDATE-COMPLIANT
- Parallel maintains isolation: separate processes, directories, no data sharing

---

## AUTHORIZATION

**APPROVED: Extract remaining 16 pairs with 4× parallel workers**

**Rationale:**
- System: 16 cores @ 6% utilization (severely underutilized)
- Available resources: 58GB RAM + 16GB swap = 74GB total
- 4 parallel processes: ~8-16GB memory usage (well within capacity)
- Time savings: 5.3-6.7 hours (sequential) → 1.3-1.7 hours (parallel 4×)
- **Saves 4-5 hours on critical path**

---

## IMPLEMENTATION APPROACH

### Option 1: Modify Existing Script (Recommended)

**File:** `pipelines/training/parallel_feature_testing.py`

**Modification:**
```python
def extract_all_remaining_pairs_parallel():
    """Extract remaining 16 pairs with 4× parallel workers."""

    remaining_pairs = [
        'eurnzd', 'gbpjpy', 'gbpchf', 'gbpaud',
        'gbpcad', 'gbpnzd', 'audjpy', 'audchf',
        'audcad', 'audnzd', 'nzdjpy', 'nzdchf',
        'nzdcad', 'cadjpy', 'cadchf', 'chfjpy'
    ]

    # Process 4 pairs at a time
    from multiprocessing import Pool

    with Pool(processes=4) as pool:
        results = pool.map(extract_pair_checkpoints, remaining_pairs)

    return results

def extract_pair_checkpoints(pair):
    """Extract all 667 tables for a single pair."""
    # This is your existing extraction logic
    # Each worker gets one pair to process independently
    # ... existing code ...
```

**Key Points:**
- Each worker extracts 1 full pair (667 tables)
- 4 workers run simultaneously
- Workers are completely isolated (no shared memory)
- Each writes to separate checkpoint directory

---

### Option 2: Manual Batch Execution (Alternative)

**Run 4 separate terminal sessions:**

**Terminal 1:**
```bash
python3 pipelines/training/parallel_feature_testing.py --pairs eurnzd,gbpjpy,gbpchf,gbpaud
```

**Terminal 2:**
```bash
python3 pipelines/training/parallel_feature_testing.py --pairs gbpcad,gbpnzd,audjpy,audchf
```

**Terminal 3:**
```bash
python3 pipelines/training/parallel_feature_testing.py --pairs audcad,audnzd,nzdjpy,nzdchf
```

**Terminal 4:**
```bash
python3 pipelines/training/parallel_feature_testing.py --pairs nzdcad,cadjpy,cadchf,chfjpy
```

**Advantage:** Simpler, no code changes
**Disadvantage:** Manual coordination, harder to monitor

---

## EXECUTION SEQUENCE

**CRITICAL: Do NOT execute this directive until:**
1. ✅ Phase 3 (12-pair merge) is COMPLETE
2. ✅ All 12 merged outputs validated
3. ✅ Results reported to CE
4. ✅ CE acknowledges Phase 3 completion

**Then:**

### Step 1: Verify Prerequisites (5 min)
```bash
# Check available resources
free -h  # Should show 16G swap active
df -h    # Should show 45GB+ available

# Verify existing checkpoints intact
ls -d checkpoints/*/  # Should show 12 directories

# Check BigQuery connectivity
bq ls bqx_ml_v3_features_v2 | head
```

### Step 2: Execute Parallel Extraction (1.3-1.7 hours)
```bash
# Option 1 (if script modified):
python3 pipelines/training/parallel_feature_testing.py --mode parallel --workers 4 --pairs remaining

# Option 2 (manual batches - see above)
```

### Step 3: Monitor Progress (ongoing)
```bash
# Watch checkpoint creation
watch -n 60 'ls -d checkpoints/*/ | wc -l'  # Should grow from 12 to 28

# Monitor memory usage
watch -n 30 'free -h'

# Check for errors
tail -f logs/step6_parallel_extraction.log
```

### Step 4: Validate Completion (15 min)
```bash
# Verify all 28 pairs present
ls -d checkpoints/*/ | wc -l  # Should show 28

# Verify file counts
for pair in eurnzd gbpjpy gbpchf gbpaud gbpcad gbpnzd audjpy audchf audcad audnzd nzdjpy nzdchf nzdcad cadjpy cadchf chfjpy; do
    count=$(ls checkpoints/$pair/*.parquet 2>/dev/null | wc -l)
    echo "$pair: $count files (expected 668)"
done

# Validate targets present
for pair in eurnzd gbpjpy gbpchf gbpaud gbpcad gbpnzd audjpy audchf audcad audnzd nzdjpy nzdchf nzdcad cadjpy cadchf chfjpy; do
    if [ -f "checkpoints/$pair/targets.parquet" ]; then
        echo "$pair: ✓ targets.parquet exists"
    else
        echo "$pair: ✗ MISSING targets.parquet"
    fi
done
```

---

## RESOURCE ALLOCATION

**Parallel 4× Configuration:**

| Resource | Per Worker | Total (4×) | Available | Utilization |
|----------|------------|------------|-----------|-------------|
| CPU cores | 4 cores | 16 cores | 16 cores | 100% |
| Memory | 2-4 GB | 8-16 GB | 74 GB | 11-22% |
| Disk I/O | Parallel | 4 streams | SSD | Moderate |
| BigQuery | 667 queries | 2,668 concurrent | No limit | Low cost |

**Safety Margins:**
- Memory: 58GB headroom (16GB used, 74GB total)
- Swap: 16GB safety net (prevents OOM)
- Disk: 45GB available for 10,688 parquet files (~2-3GB per pair)

---

## ERROR HANDLING

**If any pair fails during extraction:**

1. **Continue processing other pairs** (don't stop all workers)
2. **Log the failure** with full error trace
3. **After 4× batch completes**, retry failed pairs individually
4. **Report partial completion** to CE with failure details

**Retry Strategy:**
```bash
# If pair 'gbpjpy' fails, retry individually:
python3 pipelines/training/parallel_feature_testing.py --pairs gbpjpy --retry
```

**Validation:**
- Each pair must have 668 files (667 features + 1 targets)
- Targets.parquet must exist for each pair
- All files must be readable (not corrupted)

---

## SUCCESS CRITERIA

**Extraction Complete:**
- ✅ 28/28 pairs have checkpoint directories
- ✅ Each pair has 668 parquet files (667 features + 1 targets)
- ✅ All targets.parquet files readable with 49 target columns
- ✅ Total checkpoint files: ~18,704 (28 × 668)
- ✅ Elapsed time: 1.3-1.7 hours
- ✅ Memory peak: <32GB
- ✅ No OOM crashes

**Merge Ready:**
- ✅ All 16 new pairs validated
- ✅ Ready for DuckDB merge (same approach as 12 existing pairs)
- ✅ Expected merge time: 30-90 minutes for 16 pairs

---

## REPORTING CHECKPOINTS

**Report after each major milestone:**

### Report 1: Extraction Started
**File:** `20251211_HHMM_BA-to-CE_PARALLEL_EXTRACTION_STARTED.md`
```
Status: STARTED
Workers: 4× parallel
Pairs: 16 remaining
Expected completion: [timestamp + 1.5 hours]
```

### Report 2: Extraction Progress (every 30 min)
**File:** `20251211_HHMM_BA-to-CE_PARALLEL_EXTRACTION_PROGRESS.md`
```
Status: IN PROGRESS
Pairs completed: X/16
Pairs in progress: [list]
Memory usage: X GB
Elapsed: X minutes
ETA: X minutes remaining
```

### Report 3: Extraction Complete
**File:** `20251211_HHMM_BA-to-CE_PARALLEL_EXTRACTION_COMPLETE.md`
```
Status: SUCCESS/PARTIAL
Pairs completed: X/16
Pairs failed: [list if any]
Total files created: X
Elapsed time: X minutes
Memory peak: X GB
Next: Merge 16 new pairs with DuckDB
```

---

## MANDATE COMPLIANCE

**Architecture Mandate Analysis:**

✅ **"Absolute isolation between pairs"**
- Each worker process is isolated (separate memory space)
- No inter-process communication
- No shared data structures

✅ **"Each pair's model operates independently"**
- Each pair extracted to separate directory: checkpoints/{pair}/
- No cross-pair dependencies
- Independent BigQuery queries

✅ **"No cross-contamination"**
- Separate parquet files per pair
- No data mixing or sharing
- Independent column namespaces

**Parallel extraction maintains ALL mandate requirements.**

Sequential processing was an IMPLEMENTATION CHOICE, not a mandate requirement.

---

## TIMELINE ESTIMATES

**Sequential (Current Approach):**
- 16 pairs × 20-25 min/pair = **5.3-6.7 hours**

**Parallel 4× (This Directive):**
- 16 pairs ÷ 4 workers = 4 batches
- 4 batches × 20-25 min/batch = **1.3-1.7 hours**
- **Savings: 4-5 hours (75% reduction)**

**Parallel 8× (Higher Risk):**
- 16 pairs ÷ 8 workers = 2 batches
- 2 batches × 20-25 min/batch = 0.7-0.9 hours
- Risk: Higher memory usage, disk I/O contention
- **Not approved** - 4× provides best time/risk balance

---

## SCOPE LIMITATIONS

**This directive covers EXTRACTION ONLY.**

**After extraction completes:**
1. Report to CE
2. Await CE approval for merge phase
3. Then merge 16 new pairs using same DuckDB approach (Phases 0-3)
4. Merge expected time: 30-90 minutes (16 pairs × 2-6 min/pair)

**Total time to 100% complete:** ~2-3 hours (1.5 hrs extraction + 0.5-1.5 hrs merge)

---

## COORDINATION

**Dependencies:**
- **QA Phase 1 fixes**: 16GB swap must be active (prevents OOM)
- **DuckDB Phase 3 complete**: 12-pair merge must be validated first
- **CE approval checkpoint**: Wait for CE to review Phase 3 results

**After this directive completes:**
- All 28 pairs extracted and merged
- All 1,120 models ready for training (588 base + 196×7 meta)
- Step 6 100% complete
- Ready to proceed to Step 7 (model training)

---

## RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OOM crash | LOW | HIGH | 16GB swap active, 74GB total capacity |
| Disk I/O bottleneck | LOW | MEDIUM | SSD handles 4× parallel writes |
| BigQuery query failure | LOW | MEDIUM | Retry logic in existing code |
| Partial failure (1 pair) | MEDIUM | LOW | Continue others, retry individually |
| Checkpoint corruption | LOW | HIGH | Validation after extraction |

**Overall Risk:** LOW - System well-provisioned, 4× proven safe

---

## AUTHORIZATION

**Authority**: Chief Engineer (CE)
**Directive**: CE-2110-PARALLEL-EXTRACTION
**Scope**: Extract 16 remaining pairs with 4× parallel workers
**Timing**: Execute AFTER Phase 3 complete and CE approval
**Expected Duration**: 1.3-1.7 hours
**Expected Savings**: 4-5 hours vs sequential

**You are authorized to proceed after Phase 3 completion and CE checkpoint approval.**

---

## NEXT STEPS AFTER COMPLETION

1. **Report extraction results** to CE
2. **Await CE approval** for 16-pair merge phase
3. **Execute DuckDB merge** for 16 new pairs (30-90 min)
4. **Validate all 28 pairs** (QA will assist)
5. **Update intelligence files** with 100% completion status
6. **Proceed to Step 7** (model training)

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
