# CE Directive: SHAP Documentation Specification

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 04:00
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH - Required for Full Feature Testing
**Reference**: 20251210_0345_CE-to-BA_FULL_FEATURE_UNIVERSE_TESTING

---

## PURPOSE

Define the authoritative specification for documenting SHAP metrics during full 6,477 feature universe testing.

---

## STORAGE STRATEGY (Hybrid)

| Storage | Format | Purpose |
|---------|--------|---------|
| **BigQuery** | Table | Full ledger (authoritative, queryable) |
| **JSON** | File | Per pair-horizon summaries (git-tracked) |

---

## 1. BIGQUERY TABLE SCHEMA

### Table: `bqx_ml_v3_features_v2.feature_shap_ledger`

```sql
CREATE TABLE IF NOT EXISTS `bqx-ml.bqx_ml_v3_features_v2.feature_shap_ledger` (
  pair STRING NOT NULL,
  horizon INT64 NOT NULL,
  feature_name STRING NOT NULL,
  feature_type STRING,  -- reg/mom/vol/der/lag/cov/corr/tri/mkt
  tested BOOL NOT NULL DEFAULT TRUE,
  stability_score FLOAT64,  -- 0.0-1.0 (selection_frequency / total_runs)
  selection_frequency INT64,  -- 0-15 (runs where selected)
  status STRING,  -- RETAINED / EXCLUDED
  lgb_shap FLOAT64,  -- LightGBM mean |SHAP|
  xgb_shap FLOAT64,  -- XGBoost mean |SHAP|
  cb_shap FLOAT64,   -- CatBoost mean |SHAP|
  ensemble_shap FLOAT64,  -- Weighted average
  shap_rank INT64,  -- Rank among retained (NULL if excluded)
  shap_samples INT64,  -- Number of samples used (must be 100K+)
  shap_method STRING DEFAULT 'TreeSHAP',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(updated_at)
CLUSTER BY pair, horizon;
```

### Expected Row Counts

| Scope | Calculation | Rows |
|-------|-------------|------|
| Per pair-horizon | 6,477 features | 6,477 |
| Per pair (all horizons) | 6,477 × 7 | 45,339 |
| Full project | 6,477 × 7 × 28 | **1,269,492** |

---

## 2. JSON SUMMARY FORMAT

### Directory Structure

```
intelligence/shap/
├── eurusd_h15_shap.json
├── eurusd_h30_shap.json
├── ...
└── nzdjpy_h105_shap.json
```

### JSON Schema

```json
{
  "pair": "eurusd",
  "horizon": 15,
  "version": "3.0.0",
  "generated_at": "2025-12-10T04:00:00Z",

  "selection_summary": {
    "total_features_tested": 6477,
    "selection_config": {
      "folds": 5,
      "seeds": 3,
      "total_runs": 15,
      "threshold": 0.50
    },
    "retained_count": 423,
    "excluded_count": 6054
  },

  "shap_config": {
    "samples": 100000,
    "method": "TreeSHAP"
  },

  "top_features": {
    "lightgbm": [
      {"name": "reg_eurusd_close_lag_1", "mean_abs_shap": 0.0423, "rank": 1},
      {"name": "mom_eurusd_rsi_14", "mean_abs_shap": 0.0389, "rank": 2}
    ],
    "xgboost": [...],
    "catboost": [...],
    "ensemble": [...]
  },

  "model_stats": {
    "lightgbm": {"total_shap_sum": 1.0, "max_shap": 0.0423, "min_shap": 0.0001},
    "xgboost": {...},
    "catboost": {...}
  }
}
```

**Note**: JSON contains top 100 features per model. Full data in BigQuery.

---

## 3. VALIDATION REQUIREMENTS

### A. All Features Tested

```sql
-- Must return 6477 for each pair-horizon
SELECT pair, horizon, COUNT(*) as feature_count
FROM `bqx-ml.bqx_ml_v3_features_v2.feature_shap_ledger`
WHERE tested = TRUE
GROUP BY pair, horizon
HAVING feature_count != 6477;

-- Expected: 0 rows (all pair-horizons have exactly 6477)
```

### B. SHAP Completeness (Retained Features)

```sql
-- All retained features must have SHAP values for all 3 models
SELECT pair, horizon, feature_name
FROM `bqx-ml.bqx_ml_v3_features_v2.feature_shap_ledger`
WHERE status = 'RETAINED'
  AND (lgb_shap IS NULL OR xgb_shap IS NULL OR cb_shap IS NULL);

-- Expected: 0 rows
```

### C. SHAP Sample Count

```sql
-- All SHAP calculations must use 100K+ samples
SELECT pair, horizon, MIN(shap_samples) as min_samples
FROM `bqx-ml.bqx_ml_v3_features_v2.feature_shap_ledger`
WHERE status = 'RETAINED'
GROUP BY pair, horizon
HAVING min_samples < 100000;

-- Expected: 0 rows
```

---

## 4. IMPLEMENTATION STEPS

### Step 1: Create BigQuery Table

Run the CREATE TABLE statement above.

### Step 2: During Stability Selection

For each feature tested, insert a row with:
- `tested = TRUE`
- `selection_frequency` = count of runs where selected
- `stability_score` = selection_frequency / 15
- `status` = 'RETAINED' if stability_score >= 0.50, else 'EXCLUDED'

### Step 3: After Model Training (Retained Features Only)

Update rows for retained features with:
- `lgb_shap`, `xgb_shap`, `cb_shap` values
- `ensemble_shap` = weighted average
- `shap_rank` = rank by ensemble_shap
- `shap_samples` = 100000 (or actual count)
- `shap_method` = 'TreeSHAP'

### Step 4: Generate JSON Summary

Export top 100 features per model to JSON file.

---

## 5. DELIVERABLES

| Deliverable | Format | Location |
|-------------|--------|----------|
| Feature SHAP Ledger | BigQuery | `bqx_ml_v3_features_v2.feature_shap_ledger` |
| EURUSD h15 Summary | JSON | `intelligence/shap/eurusd_h15_shap.json` |
| Validation Report | Markdown | Include in completion report |

---

## 6. SUCCESS CRITERIA

- [ ] BigQuery table created with correct schema
- [ ] All 6,477 features have `tested = TRUE`
- [ ] All retained features have SHAP values for all 3 models
- [ ] All SHAP calculations use 100K+ samples
- [ ] JSON summary generated for EURUSD h15
- [ ] Validation queries return 0 rows (no gaps)

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 04:00
**Status**: SPECIFICATION ISSUED - IMPLEMENT WITH FULL FEATURE TESTING
