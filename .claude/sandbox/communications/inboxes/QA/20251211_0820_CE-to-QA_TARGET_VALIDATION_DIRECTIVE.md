# CE DIRECTIVE: Target Data Validation

**Date**: December 11, 2025 08:20 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P1 - HIGH
**Category**: Data Validation

---

## DIRECTIVE SUMMARY

Validate that target data in Step 6 parquet outputs matches mandate requirements. This supplements the Step 6 validation directive.

---

## TARGET VALIDATION CHECKLIST

### Per Parquet File

| Check | Expected | Critical |
|-------|----------|----------|
| Target columns present | 49 (7 windows × 7 horizons) | YES |
| Target column naming | `target_bqx{W}_h{H}` format | YES |
| Target value range | AVG ≈ 0, STDDEV ~0.08-0.10 | YES |
| Target NULL rate | <0.1% (only at data edges) | YES |

### Target Column Names (All 49)
```
target_bqx45_h15, target_bqx45_h30, target_bqx45_h45, target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105,
target_bqx90_h15, target_bqx90_h30, ..., target_bqx90_h105,
target_bqx180_h15, ..., target_bqx180_h105,
target_bqx360_h15, ..., target_bqx360_h105,
target_bqx720_h15, ..., target_bqx720_h105,
target_bqx1440_h15, ..., target_bqx1440_h105,
target_bqx2880_h15, ..., target_bqx2880_h105
```

### Validation Script
```python
import pandas as pd

df = pd.read_parquet('data/features/checkpoints/eurusd/eurusd_merged_features.parquet')

# Check target columns exist
target_cols = [c for c in df.columns if c.startswith('target_bqx')]
print(f"Target columns: {len(target_cols)}")  # Should be 49

# Check value ranges
for col in target_cols[:7]:  # Sample first window
    avg = df[col].mean()
    std = df[col].std()
    print(f"{col}: AVG={avg:.6f}, STD={std:.4f}")
    if abs(avg) > 1:
        print(f"  WARNING: AVG too high - may be indexed prices!")
```

---

## NON-COMPLIANCE FLAGS

| Symptom | Diagnosis | Action |
|---------|-----------|--------|
| AVG ≈ 100 | Indexed prices, not BQX | HALT - Report to CE |
| Missing target columns | Incomplete extraction | HALT - Re-extract |
| Wrong column names | Formula mismatch | HALT - Investigate |
| High NULL rate | Data edge issue | Document - May be acceptable |

---

## REPORT FORMAT

Include in Step 6 validation report:
1. Target column count (expect 49)
2. Sample statistics (AVG, STD for h15 targets)
3. Compliance verdict (PASS/FAIL)

---

**Chief Engineer (CE)**
