# GATE_3 Validation Criteria

**Document Type**: QA GATE CRITERIA
**Gate**: GATE_3
**Phase**: Phase 4 - EURUSD Training Pipeline
**Created**: December 10, 2025
**Author**: Quality Assurance Agent (QA)
**Status**: PENDING (Awaiting BA completion)

---

## Gate Definition

**From roadmap_v2.json (v2.3.1)**:
- **Name**: GATE_3
- **Criteria**: EURUSD h15 training complete with target metrics achieved

---

## Validation Requirements

| # | Requirement | Threshold | Validation Method |
|---|-------------|-----------|-------------------|
| 1 | Called accuracy | ≥85% | Check model metrics |
| 2 | Coverage | 30-50% range | Check gating curves |
| 3 | SHAP values | 100K+ samples | Verify sample count (USER MANDATE) |
| 4 | Gating curves | Documented | Check artifact exists |
| 5 | Model artifacts | Saved to GCS | Verify GCS bucket |

---

## Pre-Gate Checklist

### 1. Model Training Validation
```sql
-- Verify training complete
-- Check model registry for EURUSD h15
```

- [ ] LightGBM model trained
- [ ] XGBoost model trained
- [ ] CatBoost model trained
- [ ] Meta-learner trained

### 2. Performance Metrics
```python
# Expected metrics from Phase 3 baseline
# tau_85: accuracy=0.9166, coverage=0.3827
```

| Metric | Target | Baseline | Actual |
|--------|--------|----------|--------|
| Called accuracy | ≥85% | 91.66% | TBD |
| Coverage | 30-50% | 38.27% | TBD |
| AUC | ≥0.80 | 0.8505 | TBD |

### 3. SHAP Values (USER MANDATE)
```python
# Minimum samples: 100,000 (BINDING per user mandate 2025-12-09)
```

- [ ] SHAP computed for LightGBM
- [ ] SHAP computed for XGBoost
- [ ] SHAP computed for CatBoost
- [ ] Sample count ≥ 100,000

### 4. Artifacts
- [ ] Gating curves documented
- [ ] Model files saved to GCS
- [ ] Feature importance rankings saved
- [ ] Calibration report generated

---

## Validation SQL Queries

### Check Model Registry
```sql
-- TBD: Query model_registry table when available
```

### Check SHAP Sample Count
```python
# Verify SHAP output file
import pandas as pd
shap_df = pd.read_parquet('/path/to/shap_values.parquet')
assert len(shap_df) >= 100000, "SHAP samples below USER MANDATE"
```

---

## Pass/Fail Criteria

**PASS** if ALL of the following are true:
1. Called accuracy ≥ 85% at selected threshold
2. Coverage within 30-50% range
3. SHAP values generated with 100K+ samples
4. All model artifacts present in GCS
5. Gating curves documented

**FAIL** if ANY of the following:
1. Any base model missing
2. Accuracy below 85%
3. Coverage outside 30-50% range
4. SHAP samples < 100,000
5. Missing artifacts

---

## Trigger Condition

Gate validation will be triggered when:
- BA reports Phase 4 EURUSD training complete
- Model artifacts are serialized to GCS
- SHAP generation finishes

---

## Report Template

```markdown
# GATE_3 Validation Report

**Date**: [DATE]
**Validator**: QA
**Status**: [PASS/FAIL]

## Results

| Requirement | Expected | Actual | Status |
|-------------|----------|--------|--------|
| Called accuracy | ≥85% | [VALUE] | [P/F] |
| Coverage | 30-50% | [VALUE] | [P/F] |
| SHAP samples | ≥100K | [VALUE] | [P/F] |
| Gating curves | Present | [Y/N] | [P/F] |
| GCS artifacts | Present | [Y/N] | [P/F] |

## Conclusion
[GATE_3 PASSED/FAILED]
```

---

*QA Protocol - December 10, 2025*
