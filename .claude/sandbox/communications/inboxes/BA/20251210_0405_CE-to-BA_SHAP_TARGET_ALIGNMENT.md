# CE Directive: SHAP Target Alignment - BQX Mandate Compliance

**Document Type**: CE DIRECTIVE (Amendment)
**Date**: December 10, 2025 04:05
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**:
- 20251210_0400_CE-to-BA_SHAP_DOCUMENTATION_SPEC
- mandate/BQX_TARGET_FORMULA_MANDATE.md

---

## PURPOSE

Confirm that all SHAP feature importance calculations MUST be computed against BQX target values as defined in the BQX_TARGET_FORMULA_MANDATE.md.

---

## BQX TARGET ALIGNMENT

### Target Formula (Canonical)

```sql
target_bqx{window}_h{horizon} = LEAD(bqx_{window}, horizon)
```

### For h15 Models

```sql
target_bqx45_h15 = LEAD(bqx_45, 15) OVER (ORDER BY interval_time)
```

### What SHAP Measures

SHAP values measure: **"How much does each feature contribute to predicting the future BQX momentum value?"**

The model predicts:
- **NOT** raw price
- **NOT** binary direction
- **SPECIFICALLY** the BQX momentum indicator N intervals ahead

---

## SHAP CALCULATION REQUIREMENTS

### 1. Target Variable

```python
# CORRECT - Use BQX target
y = df['target_bqx45_h15']  # For h15 models

# The model predicts future BQX momentum
# SHAP explains feature contributions to this prediction
```

### 2. SHAP Output Interpretation

| SHAP Value | Meaning |
|------------|---------|
| Positive | Feature pushes prediction toward higher BQX (bullish momentum) |
| Negative | Feature pushes prediction toward lower BQX (bearish momentum) |
| Magnitude | Strength of feature's influence on predicted BQX value |

### 3. Validation

```python
# Verify SHAP is computed against BQX target
assert model.target_name == 'target_bqx45_h15'
assert shap_values.shape[1] == len(feature_names)

# SHAP values should sum to (prediction - expected_value)
assert np.allclose(
    shap_values.sum(axis=1),
    model.predict(X) - explainer.expected_value,
    atol=0.01
)
```

---

## LEDGER COLUMN UPDATE

Add column to `feature_shap_ledger`:

| Column | Type | Description |
|--------|------|-------------|
| `target_variable` | STRING | e.g., "target_bqx45_h15" |

This confirms which BQX target the SHAP values are computed against.

---

## MANDATE COMPLIANCE CHECKLIST

- [ ] SHAP computed against `target_bqx{window}_h{horizon}` (not raw price)
- [ ] BQX values oscillate around zero (per mandate verification)
- [ ] Target formula = `LEAD(bqx_{window}, horizon)`
- [ ] Ledger includes `target_variable` column
- [ ] SHAP interpretation aligned with BQX momentum semantics

---

## SUMMARY

| Aspect | Specification |
|--------|--------------|
| Target for h15 | `target_bqx45_h15` = `LEAD(bqx_45, 15)` |
| SHAP measures | Feature contribution to predicted BQX momentum |
| Mandate reference | `/mandate/BQX_TARGET_FORMULA_MANDATE.md` |
| Verification | 100% formula match (2,164,270 rows) |

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 04:05
**Status**: SHAP-BQX TARGET ALIGNMENT CONFIRMED
