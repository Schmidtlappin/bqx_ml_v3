# Feature Ledger Mandate: 100% Coverage Requirement

**Document Type**: MANDATE (Authoritative)
**Date**: December 9, 2025
**Version**: 1.0.0
**Status**: ACTIVE

---

## MANDATE STATEMENT

**Every model must account for 100% of all features in the feature universe.**

This mandate ensures complete traceability and auditability of feature selection decisions across all 784 planned models (28 pairs × 7 horizons × 4 ensemble members).

---

## FEATURE UNIVERSE DEFINITION

### Total Features Per Model: 6,477

| Category | Features | Percentage | Description |
|----------|----------|------------|-------------|
| Pair-Specific | 1,569 | 24% | Features computed for the model's target pair |
| Cross-Pair | 4,332 | 67% | cov (2,004) + corr (240) + tri (2,088) |
| Market-Wide | 576 | 9% | mkt features aggregated across all pairs |
| Currency-Level (CSI) | 0 | 0% | GAP - Implementation in progress (192 tables) |
| **TOTAL** | **6,477** | **100%** | All features must be in ledger |

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

### Per Pair-Horizon-Model Combination

| Configuration | Count |
|---------------|-------|
| Pairs | 28 |
| Horizons | 7 |
| Ensemble Members | 4 |
| Features per Model | 6,477 |
| **Total Ledger Rows** | **1,269,492** |

Formula: `28 × 7 × 4 × 6,477 = 5,077,968` (full expansion)

Note: If tracking at pair-horizon level (not per ensemble member): `28 × 7 × 6,477 = 1,269,492`

---

## VALIDATION REQUIREMENTS

### V1: Row Count Validation (CRITICAL)

```sql
-- Must equal expected count for each pair-horizon
SELECT pair, horizon,
       COUNT(*) as row_count,
       COUNT(DISTINCT feature_name) as unique_features
FROM feature_ledger
GROUP BY pair, horizon
HAVING COUNT(*) != 6477 OR COUNT(DISTINCT feature_name) != 6477
```

**Failure Mode**: Any pair-horizon with != 6,477 rows is INVALID.

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

**Expected per pair-horizon:**
- pair_specific: 1,569
- cross_pair: 4,332
- market_wide: 576
- currency_level: 0 (until CSI implemented)

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
# Every feature in catalogue must appear in ledger
catalogue_features = load_catalogue()  # 6,477 per pair
ledger_features = load_ledger(pair='EURUSD', horizon='h15')

missing = set(catalogue_features) - set(ledger_features['feature_name'])
assert len(missing) == 0, f"Missing features: {missing}"
```

---

## IMPLEMENTATION PHASES

### Phase 1: Ledger Generation Script

**File**: `scripts/generate_feature_ledger.py`

**Responsibilities**:
1. Query all 4,888 tables in bqx_ml_v3_features_v2
2. Extract all feature columns per table
3. Classify by scope (pair, cross_pair, market_wide, currency_level)
4. Generate initial ledger with final_status = 'PENDING'
5. Output: `feature_ledger_initial.parquet`

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
- With ~400 retained features, 100K samples provides ~250 samples per feature on average
- SHAP values stabilize better with larger sample sizes
- Full dataset has 2.17M rows; 100K is ~5% coverage (statistical robustness)

### Expected SHAP Calculation Volume

For EURUSD h15 with ~400 stable features retained:
- Base models: 4
- SHAP samples: **100,000+** (USER MANDATE)
- SHAP calculations: 4 × 400 × 100,000 = 160M
- Estimated time: 50-100 minutes per pair-horizon

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
  "ledger_version": "1.0.0",
  "generated": "2025-12-09T12:00:00Z",
  "pair": "EURUSD",
  "horizon": "h15",
  "feature_universe_count": 6477,
  "retained_count": 399,
  "pruned_count": 6078,
  "excluded_count": 0,
  "validation": {
    "row_count_valid": true,
    "status_coverage_valid": true,
    "scope_distribution_valid": true,
    "shap_coverage_valid": true
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

## REFERENCES

- [feature_catalogue.json](../intelligence/feature_catalogue.json) - Authoritative feature inventory
- [roadmap_v2.json](../intelligence/roadmap_v2.json) - Phase 4/5 governance gate
- [ontology.json](../intelligence/ontology.json) - Feature type taxonomy
- [BQX_TARGET_FORMULA_MANDATE.md](./BQX_TARGET_FORMULA_MANDATE.md) - Target specification

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Mandate Status**: ACTIVE AND BINDING
