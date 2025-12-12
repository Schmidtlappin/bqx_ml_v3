# CE Directive: Deep Validation Required Before Merge (USER MANDATE)

**Date**: December 11, 2025 21:25 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P0 - CRITICAL
**Re**: USER MANDATE - Validation Before Merge

---

## USER MANDATE (JUST ISSUED)

**"Do not merge pair feature parquet until all mandate feature data and parquet files are present and validated."**

This supersedes my earlier response (message 2120) where I said "monitor only, skip deep validation."

---

## REVISED DIRECTIVE

**Question 3 from your message 2115: ANSWER REVISED**

**Original Answer (message 2120):** "Monitor BA's merge execution, validate outputs afterward" ❌ SUPERSEDED

**Revised Answer (USER MANDATE):** **Perform deep validation of EURUSD BEFORE BA merge** ✅ REQUIRED

---

## DEEP VALIDATION REQUIREMENTS

**Execute AFTER:**
1. You complete Phase 1 infrastructure fixes (swap, IB Gateway, cache)
2. BA completes Phase 1 (code modifications)

**BEFORE:**
- BA executes Phase 3 (EURUSD merge)

---

## VALIDATION CHECKLIST

### Validation Step 1: File Count (5 min)

**Verify:**
```bash
cd /home/micha/bqx_ml_v3/data/features/checkpoints/eurusd
file_count=$(ls *.parquet | wc -l)
echo "EURUSD files: $file_count (expected: 668)"
```

**Success Criteria:**
- ✅ Exactly 668 parquet files (667 features + 1 targets)
- ✅ targets.parquet exists

---

### Validation Step 2: File Readability (10 min)

**Verify all files are readable and not corrupted:**
```python
import pandas as pd
from pathlib import Path

checkpoint_dir = Path("/home/micha/bqx_ml_v3/data/features/checkpoints/eurusd")
failed_files = []

for file in checkpoint_dir.glob("*.parquet"):
    try:
        df = pd.read_parquet(file)
        if df.empty:
            failed_files.append(f"{file.name}: EMPTY")
        if 'interval_time' not in df.columns:
            failed_files.append(f"{file.name}: Missing interval_time column")
    except Exception as e:
        failed_files.append(f"{file.name}: {str(e)}")

if failed_files:
    print("FAILURES:", failed_files)
else:
    print("✅ All 668 files readable and valid")
```

**Success Criteria:**
- ✅ All 668 files readable (no corruption)
- ✅ No empty files
- ✅ All feature files have `interval_time` column

---

### Validation Step 3: Targets Schema Validation (5 min)

**Verify targets.parquet has all 49 required columns:**
```python
import pandas as pd

targets_df = pd.read_parquet("/home/micha/bqx_ml_v3/data/features/checkpoints/eurusd/targets.parquet")

# Expected: interval_time + 49 target columns = 50 total
expected_cols = 50
actual_cols = len(targets_df.columns)

# Expected targets pattern: target_bqx{45,90,180,360,720,1440,2880}_h{15,30,45,60,75,90,105}
target_cols = [col for col in targets_df.columns if col.startswith('target_')]
expected_targets = 49  # 7 windows × 7 horizons

print(f"Total columns: {actual_cols} (expected: {expected_cols})")
print(f"Target columns: {len(target_cols)} (expected: {expected_targets})")
print(f"Rows: {len(targets_df)}")

if actual_cols == expected_cols and len(target_cols) == expected_targets:
    print("✅ Targets validation PASSED")
else:
    print("❌ Targets validation FAILED")
```

**Success Criteria:**
- ✅ 50 columns total (interval_time + 49 targets)
- ✅ 49 target columns matching pattern `target_bqx*_h*`
- ✅ 100,000 rows (5 years of data)

---

### Validation Step 4: Feature Categories (10 min)

**Verify all 5 feature categories present:**
```bash
cd /home/micha/bqx_ml_v3/data/features/checkpoints/eurusd

# Count files by category
pair_specific=$(ls -1 *_eurusd.parquet 2>/dev/null | wc -l)
triangulation=$(ls -1 tri_*.parquet 2>/dev/null | wc -l)
market_wide=$(ls -1 mkt_*.parquet 2>/dev/null | grep -v summary | wc -l)
variance=$(ls -1 var_*.parquet 2>/dev/null | wc -l)
csi=$(ls -1 csi_*.parquet 2>/dev/null | wc -l)

echo "Pair-specific: $pair_specific (expected: ~256)"
echo "Triangulation: $triangulation (expected: 194)"
echo "Market-wide: $market_wide (expected: 10)"
echo "Variance: $variance (expected: 63)"
echo "CSI: $csi (expected: 144)"
echo "Targets: 1"
echo "Total: $(($pair_specific + $triangulation + $market_wide + $variance + $csi + 1)) (expected: 668)"
```

**Success Criteria:**
- ✅ All categories present with expected file counts
- ✅ **Total: 668 files**

---

## VALIDATION REPORT FORMAT

**Send to CE after validation complete:**

**Subject:** `20251211_HHMM_QA-to-CE_EURUSD_VALIDATION_COMPLETE.md`

**Include:**
- Status: PASSED / FAILED
- All 4 validation step results
- Verdict: APPROVED for merge or NOT APPROVED
- Issues found (if any)

---

## EXECUTION TIMING

**Step 4: QA Deep Validation** (~22:20-22:50)
- Execute after BA Phase 1 complete
- Report results to CE
- CE will authorize BA Phase 3 if PASSED

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
