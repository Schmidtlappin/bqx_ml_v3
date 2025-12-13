# Feature Ledger Mandate: 100% Coverage Requirement

**Document Type**: MANDATE (Authoritative)
**Date**: December 13, 2025 (Updated - Post-Audit Reconciliation)
**Version**: 1.2.0
**Status**: ACTIVE
**Deployment**: Cloud Run serverless with Polars merge
**Mandate Compliance**: M005, M006, M007, M008 integrated

---

## MANDATE STATEMENT

**Every model must account for 100% of all features (columns) in the feature universe.**

This mandate ensures complete traceability and auditability of feature selection decisions across all **784 models** (28 pairs × 7 horizons × 4 ensemble members).

**CLARIFICATION** (2025-12-13 Audit):
- **Total columns per model**: ~11,337 (for cost estimation, includes duplicates across tables)
- **Unique features per model**: 1,127 (after merge/dedup, for ML training, M005/M006/M007 compliant)
- **Ledger tracks**: ALL columns that contribute to the 1,127 unique features

**Pipeline Architecture** (Updated 2025-12-12):
- **Extraction**: Cloud Run serverless (BigQuery → Parquet checkpoints, 60-70 min)
- **Merge**: Polars (user-mandated, soft memory monitoring, 13-20 min)
- **Validation**: Comprehensive (dimensions, targets, features, nulls, 1-2 min)
- **Storage**: GCS (`gs://bqx-ml-output/`)

---

## FEATURE UNIVERSE DEFINITION

### Total Unique Features Per Model: 1,127 (POST-AUDIT 2025-12-13)

**IMPORTANT CLARIFICATION**:
- **11,337 total columns** across all BigQuery tables (includes duplicates, used for cost estimation)
- **1,127 unique features** after merge/dedup (actual ML training features, M005/M006/M007 compliant)
- **Ledger requirement**: Track ALL columns, deduplicate to unique features for validation

| Category | Unique Features | Percentage | Description |
|----------|-----------------|------------|-------------|
| Pair-Specific | ~590 | 52% | Features computed for the model's target pair (agg, mom, vol, reg, etc.) |
| Cross-Pair (TRI) | ~132 | 12% | Triangular arbitrage features (tri_*) |
| Market-Wide | ~346 | 31% | mkt features aggregated across all pairs |
| Other (CSI, etc.) | ~59 | 5% | Currency strength indices and other specialized features |
| **TOTAL** | **1,127** | **100%** | All unique features must be in ledger (M005/M006/M007 compliant) |

**Note**: Previous estimates cited "6,477 features" which was the total column count before deduplication. Corrected after 2025-12-13 audit.

### Feature Type Breakdown (20 Types)

**Pair-Level (16 types):**
- agg, mom, vol, reg, regime, lag, align, der, rev, div, mrt, cyc, ext, tmp, base, var

**Cross-Pair (3 types):**
- cov, corr, tri

**Market-Wide (1 type):**
- mkt

**Currency-Level (1 type, GAP):**
- csi (192 tables pending)

---

## LEDGER SCHEMA SPECIFICATION

### File: `feature_ledger.parquet`

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `feature_name` | STRING | YES | Full feature column name |
| `source_table` | STRING | YES | BigQuery table containing this feature |
| `feature_type` | STRING | YES | One of 20 type prefixes (agg, mom, etc.) |
| `feature_scope` | STRING | YES | pair_specific, cross_pair, market_wide, currency_level |
| `variant` | STRING | YES | IDX, BQX, or OTHER |
| `pair` | STRING | YES | Target pair this ledger row applies to |
| `horizon` | STRING | YES | Prediction horizon (h15-h105) |
| `model_type` | STRING | YES | lightgbm, xgboost, catboost, elasticnet |
| `cluster_id` | STRING | NO | Correlation cluster assignment |
| `group_id` | STRING | NO | Feature group assignment |
| `pruned_stage` | INT | NO | Stage at which feature was pruned (0-6, NULL if retained) |
| `prune_reason` | STRING | NO | constant, duplicate, missing, correlated, unstable, etc. |
| `screen_score` | FLOAT | NO | Group-first screening AUC |
| `stability_freq` | FLOAT | NO | Selection frequency across folds/seeds |
| `importance_mean` | FLOAT | NO | Mean SHAP importance |
| `importance_std` | FLOAT | NO | Std dev of SHAP importance |
| `ablation_delta` | FLOAT | NO | Performance delta when feature group removed |
| `final_status` | STRING | YES | RETAINED, PRUNED, EXCLUDED |

### Required Values for `final_status`

- **RETAINED**: Feature passed all selection stages, included in model
- **PRUNED**: Feature removed during selection (must have pruned_stage + prune_reason)
- **EXCLUDED**: Feature exists but not applicable to this model (e.g., wrong pair's cross-pair features)

---

## EXPECTED LEDGER SIZE

### Per Pair-Horizon-Model Combination (UPDATED 2025-12-13)

| Configuration | Count | Notes |
|---------------|-------|-------|
| Pairs | 28 | All forex pairs |
| Horizons | 7 | h15, h30, h45, h60, h75, h90, h105 |
| Ensemble Members | 4 | LightGBM, XGBoost, CatBoost, Meta-learner |
| **Total Models** | **784** | 28 × 7 × 4 |
| **Unique Features per Model** | **1,127** | POST-AUDIT (M005/M006/M007 compliant) |
| **Total Ledger Rows** | **883,568** | 784 × 1,127 (if tracked per model) |

Formula Options:
- **Per-model tracking**: `28 × 7 × 4 × 1,127 = 883,568 rows` (tracks each ensemble member separately)
- **Per-pair-horizon tracking**: `28 × 7 × 1,127 = 220,892 rows` (shared across ensemble members)

**Recommended**: Per-pair-horizon tracking (220,892 rows) - ensemble members share feature selection within each pair-horizon.

---

## VALIDATION REQUIREMENTS

### V1: Row Count Validation (CRITICAL)

```sql
-- Must equal expected count for each pair-horizon (POST-AUDIT: 1,127 unique features)
SELECT pair, horizon,
       COUNT(*) as row_count,
       COUNT(DISTINCT feature_name) as unique_features
FROM feature_ledger
GROUP BY pair, horizon
HAVING COUNT(*) != 1127 OR COUNT(DISTINCT feature_name) != 1127
```

**Failure Mode**: Any pair-horizon with != 1,127 rows is INVALID (updated from 6,477 after 2025-12-13 audit).

### V2: Status Coverage Validation (CRITICAL)

```sql
-- Every feature must have a final_status
SELECT pair, horizon,
       COUNT(*) as total,
       SUM(CASE WHEN final_status IS NULL THEN 1 ELSE 0 END) as missing_status
FROM feature_ledger
GROUP BY pair, horizon
HAVING SUM(CASE WHEN final_status IS NULL THEN 1 ELSE 0 END) > 0
```

**Failure Mode**: Any NULL final_status is INVALID.

### V3: Scope Distribution Validation (AUDIT)

```sql
-- Verify expected scope distribution
SELECT pair, horizon, feature_scope,
       COUNT(*) as count
FROM feature_ledger
GROUP BY pair, horizon, feature_scope
ORDER BY pair, horizon, feature_scope
```

**Expected per pair-horizon** (POST-AUDIT 2025-12-13):
- pair_specific: ~590 (52%)
- cross_pair: ~132 (12% - TRI features)
- market_wide: ~346 (31%)
- other (CSI, etc.): ~59 (5%)
- **TOTAL**: 1,127 unique features (M005/M006/M007 compliant)

### V4: Pruned Feature Audit (AUDIT)

```sql
-- All PRUNED features must have reason
SELECT pair, horizon,
       COUNT(*) as pruned_without_reason
FROM feature_ledger
WHERE final_status = 'PRUNED'
  AND (pruned_stage IS NULL OR prune_reason IS NULL)
GROUP BY pair, horizon
```

**Failure Mode**: Any PRUNED without stage+reason is INVALID.

### V5: Cross-Reference with Feature Catalogue (CRITICAL)

```python
# Every feature in catalogue must appear in ledger (POST-AUDIT: 1,127 unique features)
catalogue_features = load_catalogue()  # 1,127 unique features per pair (M005/M006/M007 compliant)
ledger_features = load_ledger(pair='EURUSD', horizon='h15')

missing = set(catalogue_features) - set(ledger_features['feature_name'])
assert len(missing) == 0, f"Missing features: {missing}"
assert len(catalogue_features) == 1127, f"Expected 1,127 features, got {len(catalogue_features)}"
```

---

## IMPLEMENTATION PHASES

### Phase 1: Ledger Generation Script

**File**: `scripts/generate_feature_ledger.py`

**Responsibilities**:
1. Query all 6,069 tables in bqx_ml_v3_features_v2 (AUDITED 2025-12-13)
2. Extract all feature columns per table
3. Classify by scope (pair, cross_pair, market_wide, currency_level)
4. Deduplicate to 1,127 unique features per pair (M005/M006/M007 compliant)
5. Generate initial ledger with final_status = 'PENDING'
6. Validate M008 naming standard compliance for all feature columns
7. Output: `feature_ledger_initial.parquet`

### Phase 2: Feature Selection Integration

**During robust feature selection (`feature_selection_robust.py`):**
1. Load initial ledger
2. For each pruning stage, update:
   - `pruned_stage`
   - `prune_reason`
   - `final_status` → 'PRUNED'
3. For retained features:
   - `stability_freq`
   - `screen_score`
   - `final_status` → 'RETAINED'
4. Output: `feature_ledger_{pair}_{horizon}.parquet`

### Phase 3: SHAP Integration

**During model training (`stack_calibrated.py`):**
1. For each base model trained:
   - Calculate SHAP values for all RETAINED features
   - Update `importance_mean`, `importance_std`
2. For ablation testing:
   - Update `ablation_delta` per feature group
3. Output: Final `feature_ledger_{pair}_{horizon}_shap.parquet`

### Phase 4: Ledger Aggregation

**Final aggregation (`aggregate_feature_ledger.py`):**
1. Combine all pair-horizon ledgers
2. Validate 100% coverage
3. Output: `feature_ledger.parquet` (master file)

---

## SHAP TESTING REQUIREMENT

### All Features Must Have SHAP Values

Per the user mandate, 100% of RETAINED features must have SHAP importance calculated:

```python
# Post-training validation
def validate_shap_coverage(ledger_df):
    retained = ledger_df[ledger_df['final_status'] == 'RETAINED']
    missing_shap = retained[retained['importance_mean'].isna()]

    if len(missing_shap) > 0:
        raise ValueError(
            f"MANDATE VIOLATION: {len(missing_shap)} retained features "
            f"missing SHAP values"
        )

    # Validate sample size
    shap_samples = ledger_df.attrs.get('shap_sample_size', 0)
    if shap_samples < 100_000:
        raise ValueError(
            f"MANDATE VIOLATION: SHAP samples {shap_samples} < 100,000 minimum"
        )
```

### SHAP Sample Size: 100,000+ (USER MANDATE)

**Minimum sample size: 100,000** - This is a USER MANDATE and is binding.

Rationale:
- With ~607 retained features (50% threshold), 100K samples provides ~165 samples per feature on average
- SHAP values stabilize better with larger sample sizes
- Full dataset has 2.17M rows; 100K is ~5% coverage (statistical robustness)

### Stability Threshold: 50% (USER MANDATE)

**Threshold: 50%** - USER APPROVED 2025-12-09

This lowers the threshold from 60% to 50%, recovering 208 high-importance features.

| Threshold | Features Retained | Impact |
|-----------|-------------------|--------|
| 60% (old) | 399 | Lost regime-specific signals |
| **50% (approved)** | **607** | **+208 high-importance features** |

### Expected SHAP Calculation Volume

For EURUSD h15 with ~607 stable features retained (50% threshold):
- Base models: 4
- SHAP samples: **100,000+** (USER MANDATE)
- SHAP calculations: 4 × 607 × 100,000 = **243M**
- Estimated time: 75-150 minutes per pair-horizon

### Cost Impact

| Resource | Cost |
|----------|------|
| BigQuery | $0 - Data already loaded |
| Compute | Local CPU - No cloud charges |
| Storage | Negligible (~KB per model) |

**Net additional cost: $0** (time cost only)

---

## NON-PAIR-SPECIFIC FEATURE HANDLING

### Cross-Pair Features (4,332 per model)

Each model receives a DIFFERENT subset of cross-pair features:

| Model Pair | cov Features | corr Features | tri Features |
|------------|--------------|---------------|--------------|
| EURUSD | cov_EURUSD_* | corr_EURUSD_* | tri_EUR_*, tri_USD_* |
| GBPUSD | cov_GBPUSD_* | corr_GBPUSD_* | tri_GBP_*, tri_USD_* |
| ... | ... | ... | ... |

**Ledger Requirement**: Cross-pair features must specify which pair they apply to.

### Market-Wide Features (576 shared)

Same 576 mkt features used by ALL models:
- mkt_mean_*, mkt_std_*, mkt_sum_*, etc.

**Ledger Requirement**: market_wide features appear in every pair-horizon ledger.

---

## AUDIT TRAIL

### Required Documentation

Each feature ledger must include metadata:

```json
{
  "ledger_version": "1.2.0",
  "generated": "2025-12-13T12:00:00Z",
  "pair": "EURUSD",
  "horizon": "h15",
  "feature_universe_count": 1127,
  "retained_count": 399,
  "pruned_count": 728,
  "excluded_count": 0,
  "mandate_compliance": {
    "M005_regression_features": true,
    "M006_maximize_comparisons": true,
    "M007_semantic_compatibility": true,
    "M008_naming_standard": true
  },
  "validation": {
    "row_count_valid": true,
    "status_coverage_valid": true,
    "scope_distribution_valid": true,
    "shap_coverage_valid": true,
    "mandate_compliance_valid": true
  }
}
```

---

## MANDATE ENFORCEMENT

### Pre-Training Gate

No model training may proceed until:
1. Initial ledger generated with 100% coverage
2. V1-V5 validations pass
3. Ledger metadata documented

### Post-Training Gate

No model deployment until:
1. SHAP values calculated for all RETAINED features
2. Final ledger aggregated
3. Audit trail complete

---

## FOUR-MANDATE INTEGRATION (2025-12-13)

This Feature Ledger Mandate integrates with and depends on four architectural mandates:

### M005: Regression Feature Architecture
**Impact on Ledger**: Adds 35 regression features per pair (lin_coef, quad_coef, lin_term, quad_term, residual)
- **Ledger requirement**: Track all regression feature columns across REG, COV, TRI tables
- **Validation**: Verify presence of all 5 regression metrics × 7 windows × relevant tables

### M006: Maximize Feature Comparisons
**Impact on Ledger**: Expands cross-pair features through comprehensive COV/TRI coverage
- **Ledger requirement**: Track 3,528 COV tables (all 378 pair combinations)
- **Validation**: Ensure each pair-horizon receives appropriate cross-pair features

### M007: Semantic Feature Compatibility
**Impact on Ledger**: Defines 9 semantic groups, constrains valid feature comparisons
- **Ledger requirement**: Tag features with semantic group (1-9)
- **Validation**: Verify only semantically compatible features are compared in COV/TRI

### M008: Naming Standard Mandate
**Impact on Ledger**: Ensures consistent naming across all 6,069 tables and 1,127 features
- **Ledger requirement**: Validate all feature_name entries comply with M008 patterns
- **Validation**: Reject any non-compliant feature names (95.6% currently compliant)

**Combined Impact**: The 1,127 unique features per model result from M005 (WHAT to add), M006 (HOW MUCH to compare), M007 (WHICH are valid), and M008 (HOW to name).

---

## REFERENCES

### Intelligence Files
- [feature_catalogue.json](../intelligence/feature_catalogue.json) - Authoritative feature inventory (1,127 features)
- [roadmap_v2.json](../intelligence/roadmap_v2.json) - Phase 4/5 governance gate
- [ontology.json](../intelligence/ontology.json) - Feature type taxonomy
- [context.json](../intelligence/context.json) - Project context (6,069 tables, 784 models)

### Mandate Files
- [REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md](./REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md) - M005 (WHAT to add)
- [MAXIMIZE_FEATURE_COMPARISONS_MANDATE.md](./MAXIMIZE_FEATURE_COMPARISONS_MANDATE.md) - M006 (HOW MUCH to compare)
- [SEMANTIC_FEATURE_COMPATIBILITY_MANDATE.md](./SEMANTIC_FEATURE_COMPATIBILITY_MANDATE.md) - M007 (WHICH are valid)
- [NAMING_STANDARD_MANDATE.md](./NAMING_STANDARD_MANDATE.md) - M008 (HOW to name)
- [BQX_TARGET_FORMULA_MANDATE.md](./BQX_TARGET_FORMULA_MANDATE.md) - Target specification

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 13, 2025 (Updated - Post-Audit Reconciliation)
**Mandate Status**: ACTIVE AND BINDING
**Version**: 1.2.0 (M005/M006/M007/M008 integrated)
