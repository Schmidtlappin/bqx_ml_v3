# CE Directive: Step 6 Output Validation

**Date**: December 11, 2025 06:50 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P0 - CRITICAL
**Trigger**: When EURUSD parquet completes (669/669 tables)

---

## DIRECTIVE SUMMARY

Validate each Step 6 pair output parquet for completeness, data quality, and 100% feature coverage. This is a **GATE** - no pair proceeds to Step 7 without QA approval.

---

## STRATEGIC IMPORTANCE

| Layer | Impact |
|-------|--------|
| **Immediate** | Parquet files feed Step 7 (feature selection) |
| **Downstream** | Training quality depends on data quality |
| **Cost** | Bad data = wasted $30-50 per pair in compute |
| **Risk** | Gaps propagate to production models |

**Bottom Line**: This validation is the GATE between extraction and training. Catch issues NOW, not after hours of training.

---

## VALIDATION CHECKLIST (Per Pair)

### 1. File Integrity
```bash
# Check file exists and is readable
python3 -c "import pandas as pd; df = pd.read_parquet('data/features/checkpoints/eurusd/eurusd_merged_features.parquet'); print(f'Rows: {len(df)}, Cols: {len(df.columns)}')"
```

| Check | Expected | Status |
|-------|----------|--------|
| File exists | YES | [ ] |
| File readable | YES | [ ] |
| File size | >100 MB | [ ] |

### 2. Row Count
| Check | Expected | Tolerance |
|-------|----------|-----------|
| Row count | ~100,000 | ±10% |

### 3. Column Count (Feature Coverage)
| Check | Expected | Status |
|-------|----------|--------|
| Total columns | ~11,337 | [ ] |
| Unique features | ~1,064 | [ ] |

### 4. Feature Category Coverage (CRITICAL)
| Category | Pattern | Expected Tables | Status |
|----------|---------|-----------------|--------|
| Pair-specific | `*eurusd*` | 256 | [ ] |
| Triangulation | `tri_*` | 194 | [ ] |
| Market-wide | `mkt_*` | 12 | [ ] |
| Variance | `var_*` | 63 | [ ] |
| Currency Strength | `csi_*` | 144 | [ ] |
| **TOTAL** | | **669** | [ ] |

**Validation Method**:
```python
# Check column prefixes
cols = df.columns.tolist()
pair_cols = [c for c in cols if 'eurusd' in c.lower()]
tri_cols = [c for c in cols if c.startswith('tri_')]
mkt_cols = [c for c in cols if c.startswith('mkt_')]
var_cols = [c for c in cols if c.startswith('var_')]
csi_cols = [c for c in cols if c.startswith('csi_')]

print(f"Pair: {len(pair_cols)}, Tri: {len(tri_cols)}, Mkt: {len(mkt_cols)}, Var: {len(var_cols)}, CSI: {len(csi_cols)}")
```

### 5. Data Quality Checks
| Check | Column(s) | Threshold | Action if Fail |
|-------|-----------|-----------|----------------|
| NULL in interval_time | interval_time | 0% | HALT |
| NULL in targets | h15-h105 | 0% | HALT |
| NULL in features | all others | <1% | Document, continue |
| Duplicates | interval_time | 0 | Remove |
| Data types | numeric cols | float64/int64 | Cast |

**Validation Script**:
```python
import pandas as pd

df = pd.read_parquet('data/features/checkpoints/eurusd/eurusd_merged_features.parquet')

# NULL analysis
null_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
print("Top 10 NULL columns:")
print(null_pct.head(10))

# Key columns NULL check
key_cols = ['interval_time'] + [c for c in df.columns if c.startswith('h') and c[1:].isdigit()]
for col in key_cols:
    if col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f"CRITICAL: {col} has {null_count} NULLs")

# Duplicate check
dups = df.duplicated(subset=['interval_time']).sum()
print(f"Duplicates: {dups}")
```

### 6. Value Range Sanity
| Check | Expected Range | Action if Fail |
|-------|----------------|----------------|
| Features | -1e10 to 1e10 | Investigate |
| Targets (h*) | -1, 0, 1 | Investigate |
| Prices | >0 | Investigate |

---

## DATA CLEANING PROTOCOL

### When to Clean
| Issue | Severity | Action |
|-------|----------|--------|
| NULL <1% in features | LOW | Forward-fill or drop rows |
| NULL >5% in features | HIGH | **HALT - report to CE** |
| NULL in key columns | CRITICAL | **HALT - investigate source** |
| Duplicates | MEDIUM | Remove, document count |
| Type mismatch | MEDIUM | Cast, document |
| Outliers | INFO | Document only (forex can have extreme values) |

### When NOT to Clean
- Do NOT remove outliers (forex data is naturally volatile)
- Do NOT impute targets (h15-h105) - must investigate source
- Do NOT modify interval_time

---

## GAP REMEDIATION

If gaps found:

1. **Identify missing category** (pair, tri, mkt, var, csi)
2. **Check Step 6 logs** for extraction errors
3. **Report to CE** with specific gap details
4. **BA will remediate** (re-run extraction for missing tables)
5. **QA re-validates** after remediation

---

## DELIVERABLES

### Per Pair Report
File: `inboxes/CE/[timestamp]_QA-to-CE_STEP6_[PAIR]_AUDIT.md`

Include:
1. Row count
2. Column count
3. Feature category breakdown
4. NULL analysis summary
5. Duplicate count
6. Data quality issues (if any)
7. PASS/FAIL verdict
8. Remediation needed (if any)

### Summary Report (After All 28 Pairs)
File: `inboxes/CE/[timestamp]_QA-to-CE_STEP6_FINAL_AUDIT.md`

---

## SUCCESS CRITERIA

| Criterion | Threshold |
|-----------|-----------|
| File integrity | 100% |
| Row count | 90K-110K |
| Feature coverage | 100% (all 5 categories) |
| NULL in key columns | 0% |
| NULL in features | <1% |
| Duplicates | 0 |

**GATE APPROVAL**: All criteria must pass for pair to proceed to Step 7.

---

## CURRENT STATUS

| Pair | Progress | Status |
|------|----------|--------|
| EURUSD | 570/669 (85%) | EXTRACTING |
| GBPUSD-NZDJPY | 0/669 | PENDING |

**Trigger**: Begin validation when EURUSD reaches 669/669 and merged parquet is created.

---

## ESCALATION

| Issue | Escalate To | Action |
|-------|-------------|--------|
| NULL >5% | CE | Halt extraction |
| Missing category | CE + BA | Re-run extraction |
| File corruption | CE + BA | Re-run pair |
| Persistent gaps | CE | Review extraction code |

---

**Chief Engineer (CE)**
