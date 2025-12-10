# GATE_2 Validation Criteria: Feature Ledger

**Document Type**: QA VALIDATION CRITERIA
**Created**: December 9, 2025
**Author**: Quality Assurance Agent (QA)
**Phase**: 2.5 (Feature Ledger Generation)
**Status**: PENDING (awaiting Phase 2.5 completion)

---

## Executive Summary

GATE_2 validates the Feature Ledger, ensuring 100% coverage of all 6,477 features across 196 pair-horizon combinations (28 pairs × 7 horizons).

---

## Validation Checklist

### 1. Row Count Validation - CRITICAL

| Metric | Expected | Query |
|--------|----------|-------|
| Total Rows | **1,269,492** | `SELECT COUNT(*) FROM feature_ledger` |
| Features per Model | 6,477 | `SELECT COUNT(*) FROM ledger WHERE pair_horizon = 'eurusd_h15'` |
| Pair-Horizons | 196 | `SELECT COUNT(DISTINCT pair_horizon) FROM feature_ledger` |

**Calculation**: 6,477 features × 28 pairs × 7 horizons = **1,269,492 rows**

**Validation Query**:
```sql
SELECT
  COUNT(*) as total_rows,
  COUNT(DISTINCT pair || '_' || horizon) as pair_horizons,
  COUNT(DISTINCT feature_name) as unique_features
FROM feature_ledger
```

**Pass Criteria**:
- total_rows = 1,269,492
- pair_horizons = 196
- unique_features ≤ 6,477 (some features may be pair-specific)

---

### 2. NULL Validation - CRITICAL

| Column | NULL Allowed | Rationale |
|--------|--------------|-----------|
| pair | NO | Primary key component |
| horizon | NO | Primary key component |
| feature_name | NO | Primary key component |
| final_status | **NO** | Must be RETAINED or PRUNED |
| feature_group | NO | Required for analysis |
| selection_round | YES | May be NULL if PRUNED early |
| shap_importance | YES | Only required if RETAINED |

**Validation Query**:
```sql
SELECT
  SUM(CASE WHEN pair IS NULL THEN 1 ELSE 0 END) as null_pair,
  SUM(CASE WHEN horizon IS NULL THEN 1 ELSE 0 END) as null_horizon,
  SUM(CASE WHEN feature_name IS NULL THEN 1 ELSE 0 END) as null_feature,
  SUM(CASE WHEN final_status IS NULL THEN 1 ELSE 0 END) as null_status,
  COUNT(*) as total
FROM feature_ledger
```

**Pass Criteria**: All null_* columns = 0

---

### 3. Status Distribution Validation - HIGH

| Status | Expected Range | Description |
|--------|---------------|-------------|
| RETAINED | 550-650 per model | ~9-10% of features |
| PRUNED | 5,827-5,927 per model | ~90-91% of features |

**Validation Query**:
```sql
SELECT
  pair,
  horizon,
  SUM(CASE WHEN final_status = 'RETAINED' THEN 1 ELSE 0 END) as retained,
  SUM(CASE WHEN final_status = 'PRUNED' THEN 1 ELSE 0 END) as pruned,
  COUNT(*) as total
FROM feature_ledger
GROUP BY pair, horizon
ORDER BY pair, horizon
```

**Pass Criteria**:
- Each pair-horizon has exactly 6,477 rows
- retained count between 500-700 (based on 50% stability threshold)
- retained + pruned = 6,477 for each model

---

### 4. SHAP Coverage Validation - HIGH

All RETAINED features MUST have SHAP importance values.

**Validation Query**:
```sql
SELECT
  COUNT(*) as retained_without_shap
FROM feature_ledger
WHERE final_status = 'RETAINED'
  AND (shap_importance IS NULL OR shap_importance = 0)
```

**Pass Criteria**: retained_without_shap = 0

**SHAP Sample Size**: 100,000+ samples minimum (per USER MANDATE)

---

### 5. Feature Group Coverage - MEDIUM

Verify all feature groups are represented.

**Expected Groups** (from ontology):
| Group | Tables | Expected Features |
|-------|--------|-------------------|
| agg_* | 28 | ~500 |
| reg_* | 28 | ~500 |
| mom_* | 28 | ~400 |
| vol_* | 28 | ~400 |
| der_* | 28 | ~300 |
| align_* | 28 | ~300 |
| cov_* | 28 | ~800 |
| corr_* | 28 | ~800 |
| tri_* | 28 | ~600 |
| mkt_* | 12 | ~300 |
| csi_* | 144 | ~1,000 |
| var_* | 63 | ~500 |

**Validation Query**:
```sql
SELECT
  feature_group,
  COUNT(DISTINCT feature_name) as unique_features,
  SUM(CASE WHEN final_status = 'RETAINED' THEN 1 ELSE 0 END) as retained_count
FROM feature_ledger
WHERE pair = 'eurusd' AND horizon = 'h15'
GROUP BY feature_group
ORDER BY feature_group
```

**Pass Criteria**: All expected groups present

---

### 6. Schema Compliance - MEDIUM

**Required Schema**:
```
feature_ledger (
  pair STRING NOT NULL,
  horizon STRING NOT NULL,
  feature_name STRING NOT NULL,
  feature_group STRING NOT NULL,
  source_table STRING,
  final_status STRING NOT NULL,  -- RETAINED | PRUNED
  selection_round INT,           -- 1-5 if selected
  stability_score FLOAT,         -- 0.0-1.0
  shap_importance FLOAT,         -- Only if RETAINED
  prune_reason STRING,           -- Only if PRUNED
  created_at TIMESTAMP,
  PRIMARY KEY (pair, horizon, feature_name)
)
```

---

### 7. Cross-Pair Consistency - LOW

Verify that cross-pair features (cov, corr, tri) appear in all 28 pair models.

**Validation Query**:
```sql
SELECT
  feature_name,
  COUNT(DISTINCT pair) as pair_count
FROM feature_ledger
WHERE feature_group IN ('cov', 'corr', 'tri')
GROUP BY feature_name
HAVING COUNT(DISTINCT pair) < 28
```

**Pass Criteria**: No rows returned (all cross-pair features in all models)

---

## GATE_2 Summary Checklist

```
[ ] Row count = 1,269,492
[ ] No NULL in pair, horizon, feature_name, final_status
[ ] RETAINED count reasonable (500-700 per model)
[ ] All RETAINED features have SHAP values
[ ] SHAP computed with 100K+ samples
[ ] All feature groups represented
[ ] Schema compliant
[ ] Cross-pair features consistent
```

---

## Validation Report Template

Upon GATE_2 execution, QA will produce:

```markdown
# GATE_2 Validation Report

**Date**: [DATE]
**Status**: [PASS/FAIL]

## Results Summary
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Row Count | 1,269,492 | [X] | [PASS/FAIL] |
| NULL Check | 0 | [X] | [PASS/FAIL] |
| RETAINED Range | 500-700 | [X] | [PASS/FAIL] |
| SHAP Coverage | 100% | [X]% | [PASS/FAIL] |

## Recommendation
[APPROVE/REJECT] GATE_2 passage
```

---

## Dependencies

| Dependency | Status | Required For |
|------------|--------|--------------|
| GATE_1 | **PASSED** | Phase 2.5 start |
| Phase 2.5 Scripts | PENDING | Ledger generation |
| SHAP Computation | PENDING | RETAINED validation |

---

## Estimated Timeline

- **Ledger Generation**: After BA creates generate_feature_ledger.py
- **SHAP Computation**: 6-12 hours (parallelized)
- **QA Validation**: 1-2 hours after ledger complete

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Created**: December 9, 2025
**Status**: CRITERIA DEFINED - Awaiting Phase 2.5 execution
