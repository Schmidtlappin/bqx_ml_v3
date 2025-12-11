# CE DIRECTIVE: Analytics Dataset Remediation

**Date**: December 11, 2025 10:05 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P1 - HIGH
**Category**: Data Cleanup

---

## EXECUTIVE SUMMARY

Two remediation tasks required:
1. **DELETE** V1 analytics dataset (`bqx_ml_v3_analytics`) - duplicate/stale
2. **AUDIT** V2 analytics for non-essential tables

---

## TASK 1: DELETE V1 ANALYTICS DATASET

### Current State
V1 analytics dataset still exists despite V2 migration being complete.

| Dataset | Tables | Status |
|---------|--------|--------|
| `bqx_ml_v3_analytics` (V1) | 50+ | **DELETE** |
| `bqx_ml_v3_analytics_v2` | 56 | **KEEP** |

### Execution
```bash
# Delete entire V1 dataset
bq rm -r -f bqx-ml:bqx_ml_v3_analytics
```

### Verification
```bash
bq ls bqx-ml:bqx_ml_v3_analytics
# Should return: "Not found" or error
```

### Expected Savings
- Storage: ~$10-20/month
- Eliminates confusion between V1/V2

---

## TASK 2: V2 ANALYTICS AUDIT

### Current V2 Tables (56 total)

#### Target Tables (29) - KEEP
```
targets_eurusd, targets_gbpusd, targets_usdjpy, targets_usdchf,
targets_audusd, targets_usdcad, targets_nzdusd, targets_eurgbp,
targets_eurjpy, targets_eurchf, targets_euraud, targets_eurcad,
targets_eurnzd, targets_gbpjpy, targets_gbpchf, targets_gbpaud,
targets_gbpcad, targets_gbpnzd, targets_audjpy, targets_audchf,
targets_audcad, targets_audnzd, targets_nzdjpy, targets_nzdchf,
targets_nzdcad, targets_cadjpy, targets_cadchf, targets_chfjpy,
targets_all_fixed  # INVESTIGATE - may be needed
```

#### Analysis Tables (27) - INVESTIGATE
```
comprehensive_catalog
extreme_vs_full_correlation_comparison
feature_catalog
feature_correlations_20pct_extreme
feature_correlations_by_horizon
feature_correlations_by_horizon_extreme
feature_correlations_extreme_7windows
feature_correlations_full_7windows
feature_correlations_full_dataset
feature_rankings_20pct_extreme
feature_rankings_full_dataset
feature_type_lift_comparison
horizon_correlation_summary
optimal_feature_slate
pair_extreme_periods_20pct
pair_extreme_thresholds_20pct
poly_feature_ranking
poly_window_horizon_analysis
residual_feature_matrix
timing_correlations
timing_correlations_comprehensive
timing_correlations_full
timing_targets
top100_per_target
top_features_by_horizon
training_eurusd_full_poly
training_eurusd_poly
```

### Action Required
1. **VERIFY** `targets_all_fixed` purpose - keep if needed, delete if not
2. **DEFER** analysis table cleanup until after Step 6 completes
3. **DOCUMENT** which analysis tables are actively used

---

## TASK 3: VERIFY EURUSD TARGETS

### Verification Query
```sql
SELECT
    COUNT(*) as row_count,
    COUNT(target_bqx45_h15) as bqx45_count,
    COUNT(target_bqx720_h15) as bqx720_count,
    COUNT(target_bqx2880_h105) as bqx2880_count
FROM `bqx-ml.bqx_ml_v3_analytics_v2.targets_eurusd`
```

### Expected Results
- All counts should be equal (~2.1M rows)
- Confirms all 49 target columns populated

---

## PRIORITY SEQUENCE

1. **IMMEDIATE**: Delete V1 analytics dataset
2. **IMMEDIATE**: Verify EURUSD targets (all 49 columns present)
3. **DEFERRED**: Audit analysis tables after Step 6

---

## REPORTING

Upon completion, report:
1. V1 deletion status
2. Storage savings realized
3. targets_all_fixed investigation result
4. EURUSD verification query results

---

**Chief Engineer (CE)**
