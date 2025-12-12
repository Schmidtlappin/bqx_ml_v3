# CE Directive: Urgent Polars Risk Mitigation Analysis

**Date**: December 11, 2025 23:20 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Re**: OPS Report - Polars Memory Crisis Analysis & Risk Mitigation
**Priority**: URGENT
**Reference**: 20251211_2120_OPS-to-CE_FULL_DETECTION_REMEDIATION_REPORT.md

---

## SITUATION

**OPS reported critical memory crisis** caused by Polars operations earlier today (21:10-21:20 UTC):

### Critical Findings from OPS Report

**Memory Bloat**:
- 9.3GB parquet file consumed **65GB+ RAM** (7× file size)
- Two stuck Python processes for 9+ hours
- Caused VM memory exhaustion: 94% used, 78% swap

**Process Deadlock**:
- Processes stuck in `futex_wait_queue` (internal deadlock)
- No timeout mechanism for hung operations
- Required manual kill to recover

**System Impact**:
- SSH failures
- VM nearly unresponsive
- Load 22.18 (high)

**OPS Remediation**:
- Killed stuck processes (freed 65GB)
- Memory restored: 94% → 1%
- Swap reduced: 78% → 14%

---

## URGENT REQUIREMENT

**BA is currently executing Polars test for EURUSD** (23:10-23:44 expected).

**Your Task**: Analyze Polars memory risks and provide immediate mitigation recommendations.

---

## ANALYSIS REQUIRED

### 1. Memory Risk Assessment

**Questions to Answer**:
1. What caused 7× memory bloat (9.3GB → 65GB)?
2. Is this expected Polars behavior or a bug?
3. What memory usage should we expect for EURUSD merge?
   - Input: 668 files, 17,037 columns, ~100K rows
   - Expected output: ~6,500 columns, 100K rows
4. What is the actual memory requirement vs available 78GB?
5. What triggers futex_wait_queue deadlock?

### 2. Implementation Review

**Review BA's Polars Implementation** (from EA Directive 2305):
```python
def merge_checkpoints_polars(checkpoint_dir: str, output_path: str):
    import polars as pl
    from pathlib import Path

    # Lazy scan targets
    target_path = Path(checkpoint_dir) / "targets.parquet"
    result_lf = pl.scan_parquet(target_path)

    # Lazy scan and join all feature files
    for pq_file in sorted(Path(checkpoint_dir).glob("*.parquet")):
        if pq_file.name == "targets.parquet":
            continue

        feature_lf = pl.scan_parquet(pq_file)
        result_lf = result_lf.join(
            feature_lf,
            on='interval_time',
            how='left'
        )

    # Execute optimized plan
    print("Executing optimized query plan...")
    result_df = result_lf.collect()

    # Write output
    result_df.write_parquet(output_path)
    print(f"Merged {len(result_df)} rows, {len(result_df.columns)} columns")

    return result_df
```

**Identify**:
- Memory risk points in this implementation
- Missing safeguards (timeouts, limits, monitoring)
- Potential deadlock triggers
- Optimization opportunities

### 3. Mitigation Strategies

**Provide specific recommendations for**:

1. **Resource Limits**:
   - Should we set memory limits via `ulimit`?
   - Should we use `systemd-run` with `--property MemoryMax=`?
   - What limit is safe? (Available: 78GB, want headroom)

2. **Timeout Mechanisms**:
   - How to implement timeout for `.collect()`?
   - Should we use `signal.alarm()` or `multiprocessing.Process` with timeout?
   - What timeout is reasonable? (8-20 min expected)

3. **Lazy Evaluation Optimization**:
   - Is current implementation using lazy evaluation optimally?
   - Should we use streaming mode instead of `.collect()`?
   - Can we process in batches to limit memory?

4. **Monitoring**:
   - How to monitor memory usage during execution?
   - Should we add progress callbacks?
   - Should we log intermediate steps?

5. **Graceful Failure**:
   - How to detect impending OOM?
   - How to gracefully abort before deadlock?
   - What cleanup is needed on failure?

### 4. Updated Implementation

**Provide**:
- Refactored `merge_checkpoints_polars()` function with all mitigations
- Resource limit wrapper commands
- Monitoring/logging additions
- Error handling improvements

---

## EXECUTION CONSTRAINTS

### Time Constraint
**BA's Polars test is already running** (started ~23:10).

**Two scenarios**:

**Scenario A**: Test completes successfully before EA analysis
- EA analysis becomes guidance for 27-pair rollout
- Apply mitigations before scaling to 27 pairs

**Scenario B**: Test is still running when EA analysis arrives
- EA can provide real-time guidance to BA
- BA can add monitoring/limits mid-execution if possible
- Abort test if risk is unacceptable

### Risk Constraint
**We cannot afford another memory crisis**:
- Current VM health: Stable (1% memory, 14% swap)
- Available capacity: 78GB total (62GB RAM + 16GB swap)
- Risk tolerance: LOW (user depends on VM stability)

### Decision Authority
**EA has full autonomy to**:
- Recommend aborting current test if risk is unacceptable
- Recommend fallback to BigQuery ETL if Polars is too risky
- Propose alternative merge strategies
- Set resource limits for 27-pair rollout

---

## DELIVERABLE

**Subject**: `20251211_HHMM_EA-to-CE_POLARS_RISK_ANALYSIS_AND_MITIGATION.md`

**Required Sections**:
1. **Memory Risk Assessment**:
   - Expected memory usage for EURUSD (with calculations)
   - Risk level: LOW / MEDIUM / HIGH / CRITICAL
   - Confidence level in estimates

2. **Root Cause Analysis**:
   - What caused 7× bloat in previous failure?
   - How to prevent in current implementation?

3. **Mitigation Recommendations**:
   - Resource limits (specific commands)
   - Timeout implementation (code)
   - Monitoring approach (code/commands)
   - Updated implementation (full code)

4. **Go/No-Go Recommendation**:
   - **PROCEED**: Polars is safe with mitigations → continue test/rollout
   - **ABORT**: Polars risk too high → stop test, pivot to BigQuery ETL
   - **CONDITIONAL**: Safe if specific mitigations applied → provide requirements

5. **27-Pair Rollout Plan** (if PROCEED):
   - Sequential vs parallel approach
   - Resource limits per merge
   - Monitoring requirements
   - Abort criteria

---

## URGENCY

**Timeline**:
- BA test expected completion: 23:42-23:44
- EA analysis needed: ASAP (ideally before 23:42)
- If not possible: EA analysis guides 27-pair rollout decisions

**Priority**: URGENT - This could prevent catastrophic failure of 27-pair rollout

**Authority**: Full autonomy to recommend abort if risk assessment shows CRITICAL

---

## COORDINATION

**With BA**:
- If EA recommends abort: Send message to BA immediately
- If EA recommends mitigations: Send updated implementation to BA before 27-pair rollout

**With CE**:
- Send analysis report when complete
- If recommending abort: Explain rationale clearly
- If recommending proceed: Provide confidence level

**With QA**:
- QA should monitor resource usage during validation
- EA analysis should include monitoring checklist for QA

---

## REFERENCE DATA

**EURUSD Checkpoint Stats**:
- Files: 668 (667 features + 1 targets)
- Total input columns: 17,037
- Expected output columns: ~6,500 (deduplicated)
- Rows: ~100,000
- Estimated merged file size: ~5GB

**VM Resources**:
- Total memory: 62GB RAM + 16GB swap = 78GB
- Current usage: 1% RAM, 14% swap
- Available: ~61GB RAM
- Safe usage target: <40GB (leave 21GB headroom)

**Previous Failure Data** (from OPS report):
- File: 9.3GB parquet (merged? single feature file?)
- Memory consumed: 65GB+ (7× file size)
- Duration before kill: 9h 48m
- State: futex_wait_queue (deadlock)

---

## SUCCESS CRITERIA

**Analysis is successful if**:
- ✅ Clear risk assessment (LOW/MED/HIGH/CRITICAL)
- ✅ Specific memory usage estimate with confidence level
- ✅ Concrete mitigation recommendations (not generic)
- ✅ Go/No-Go recommendation with rationale
- ✅ Actionable implementation changes (code provided)
- ✅ Delivered before BA needs to make rollout decision

**Analysis quality**:
- Based on actual Polars behavior, not assumptions
- Considers OPS findings (7× bloat, deadlock)
- Provides safety margins
- Includes abort criteria

---

## EXECUTE IMMEDIATELY

**This is a critical risk mitigation task**. Previous Polars operations caused VM memory crisis requiring emergency intervention. We must ensure current/future Polars operations do not repeat this failure.

**Start analysis now. Report findings ASAP.**

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
