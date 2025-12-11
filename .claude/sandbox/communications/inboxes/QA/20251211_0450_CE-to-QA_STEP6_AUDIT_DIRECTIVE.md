# CE Directive: Step 6 Monitoring & Data Audit

**Date**: December 11, 2025 04:50 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**

---

## DIRECTIVE: Monitor & Audit Step 6

You are directed to monitor Step 6 processes and audit output data to confirm correctness, completeness, and full feature coverage.

---

## PART 1: PROCESS MONITORING

### Active Process

| Parameter | Value |
|-----------|-------|
| PID | 1272452 |
| Mode | SEQUENTIAL + CHECKPOINT |
| Log | `logs/step6_sequential_*.log` |

### Monitor Commands

```bash
# Live progress
tail -f logs/step6_sequential_*.log

# Process status
ps aux | grep parallel_feature_testing

# Memory usage
ps -p 1272452 -o pid,rss,vsz,%mem,%cpu
```

### User Mandates (Verify Active)

| Mandate | Expected in Log |
|---------|-----------------|
| Sequential pairs | "PAIR X/28: {PAIR}" |
| 12 workers per pair | "12 parallel workers" |
| Checkpoint mode | "CHECKPOINT MODE" |
| Resume capability | "X cached, Y pending" |

---

## PART 2: DATA AUDIT

### Per-Pair Validation

For each completed pair, verify:

| Check | Expected | Command |
|-------|----------|---------|
| Parquet exists | `{pair}_merged_features.parquet` | `ls data/features/*.parquet` |
| Row count | ~100,000 | `python3 -c "import pandas as pd; print(len(pd.read_parquet('data/features/{pair}_merged_features.parquet')))"` |
| Column count | >10,000 | Check merged file |
| No NULL interval_time | 0 NULLs | Validate column |
| Target columns present | h15-h105 targets | Check columns |

### Feature Coverage Audit

| Category | Tables | Verify Present |
|----------|--------|----------------|
| pair_specific (%pair%) | 256 | Columns with pair name |
| triangulation (tri_*) | 194 | tri_* prefixed columns |
| market_wide (mkt_*) | 12 | mkt_* prefixed columns |
| variance (var_*) | 63 | var_* prefixed columns |
| currency_strength (csi_*) | 144 | csi_* prefixed columns |
| **TOTAL** | **669** | All categories present |

### Checkpoint Audit

```bash
# Count checkpoint files per pair
ls data/features/checkpoints/eurusd/*.parquet | wc -l
# Expected: 669 per pair
```

---

## PART 3: COMPLETENESS VERIFICATION

After Step 6 completes:

1. **28 parquet files** in `data/features/`
2. **Each file** has ~100K rows
3. **Each file** has columns from all 5 categories
4. **No gaps** in feature coverage

---

## REPORTING SCHEDULE

| Milestone | Report |
|-----------|--------|
| EURUSD complete | `QA-to-CE_STEP6_EURUSD_AUDIT.md` |
| 50% (14 pairs) | `QA-to-CE_STEP6_PROGRESS_50PCT.md` |
| 100% complete | `QA-to-CE_STEP6_FINAL_AUDIT.md` |
| Any anomaly | `QA-to-CE_STEP6_ISSUE_*.md` |

---

## AUDIT CHECKLIST TEMPLATE

```markdown
## Pair: {PAIR}

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Parquet exists | Yes | | |
| Row count | ~100K | | |
| Column count | >10K | | |
| pair_specific cols | Yes | | |
| tri_* cols | Yes | | |
| mkt_* cols | Yes | | |
| var_* cols | Yes | | |
| csi_* cols | Yes | | |
| NULL interval_time | 0 | | |
| Target columns | 7 (h15-h105) | | |
```

---

## CRITICAL: Flag Immediately

- Missing feature categories
- Row count < 90K or > 110K
- Missing target columns
- Process errors/crashes
- Memory issues (>50GB)

---

**Chief Engineer (CE)**
