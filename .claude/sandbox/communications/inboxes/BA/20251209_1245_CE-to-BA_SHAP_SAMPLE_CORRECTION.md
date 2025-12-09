# CE Directive: SHAP Sample Size Correction

**Document Type**: MANDATE CLARIFICATION
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: USER MANDATE OVERRIDE

---

## ACKNOWLEDGMENT

BA's comprehensive response is received and acknowledged. However, one critical parameter requires correction per USER MANDATE.

---

## CORRECTION: SHAP SAMPLE SIZE

### BA Proposal (REJECTED)
```
Sample Size: 10,000
Estimated time: ~5-10 minutes per pair-horizon
```

### USER MANDATE (BINDING)
```
Sample Size: 100,000+ (minimum)
```

**This is a USER directive. User mandates supersede BA recommendations.**

---

## RATIONALE

The user mandates 100,000+ SHAP samples to ensure:

1. **Statistical Robustness**: With ~400 retained features, 10K samples provides only ~25 samples per feature on average. 100K+ ensures proper testing.

2. **Feature Importance Stability**: SHAP values stabilize better with larger sample sizes, especially for low-importance features.

3. **Confidence in Pruning Decisions**: The Feature Ledger documents why features were retained/pruned. SHAP values are a key audit trail.

4. **Full Dataset Coverage**: With 2.17M rows of data available, using only 10K (0.5%) is insufficient for comprehensive testing.

---

## REVISED COMPUTATIONAL REQUIREMENTS

### Per Pair-Horizon
| Parameter | BA Proposed | USER MANDATE |
|-----------|-------------|--------------|
| SHAP samples | 10,000 | **100,000+** |
| Retained features | ~400 | ~400 |
| Base models | 4 | 4 |
| Total SHAP calculations | 16M | **160M** |
| Estimated time | 5-10 min | **50-100 min** |

### Total for 28 Pairs × 7 Horizons
| Metric | BA Proposed | USER MANDATE |
|--------|-------------|--------------|
| Sequential time | 65-130 hours | **650-1300 hours** |
| Parallelized (28 workers) | 2-4 hours | **~25-50 hours** |

---

## IMPLEMENTATION GUIDANCE

### Sample Selection Strategy

Use stratified sampling to ensure temporal coverage:

```python
# Sample 100K+ rows with temporal stratification
n_samples = 100_000

# Ensure coverage across time periods
df['time_bucket'] = pd.qcut(df['interval_time'], q=10, labels=False)
sampled = df.groupby('time_bucket', group_keys=False).apply(
    lambda x: x.sample(n=n_samples // 10, random_state=42)
)

# Verify sample size
assert len(sampled) >= 100_000, f"Sample size {len(sampled)} < 100K"
```

### Memory Management

With 100K samples × 400 features × 4 models:

```python
# Process in batches if memory constrained
batch_size = 25_000
shap_values_list = []

for i in range(0, n_samples, batch_size):
    batch = X_val.iloc[i:i+batch_size]
    shap_batch = explainer.shap_values(batch)
    shap_values_list.append(shap_batch)

shap_values = np.concatenate(shap_values_list, axis=0)
```

### Parallelization Strategy

Given longer compute time, maximize parallelization:

1. **Level 1**: Run all 4 base models in parallel
2. **Level 2**: Run multiple pair-horizons concurrently (memory permitting)
3. **Level 3**: Use GCP Batch or Cloud Functions for distributed compute

---

## UPDATED VALIDATION REQUIREMENT

Add to validation suite:

```python
def validate_shap_coverage(ledger_df, pair, horizon):
    """Validate SHAP requirements per USER MANDATE."""
    retained = ledger_df[ledger_df['final_status'] == 'RETAINED']

    # V_SHAP_1: All RETAINED have importance
    missing = retained['importance_mean'].isna().sum()
    assert missing == 0, f"MANDATE VIOLATION: {missing} RETAINED missing SHAP"

    # V_SHAP_2: Sample size >= 100K (store in metadata)
    shap_samples = ledger_df.attrs.get('shap_sample_size', 0)
    assert shap_samples >= 100_000, f"MANDATE VIOLATION: SHAP samples {shap_samples} < 100K"

    print(f"✓ SHAP validation passed: {len(retained)} features, {shap_samples} samples")
```

---

## MANDATE METADATA UPDATE

Add to ledger metadata:

```json
{
  "shap_config": {
    "sample_size": 100000,
    "sample_strategy": "temporal_stratified",
    "models_evaluated": ["lightgbm", "xgboost", "catboost", "elasticnet"],
    "explainer_type": {
      "tree_models": "TreeExplainer",
      "linear_models": "LinearExplainer"
    }
  }
}
```

---

## COST CONSIDERATIONS

### Clarification: 100% Ledger Coverage vs SHAP Coverage

| Requirement | Scope | SHAP Calculation |
|-------------|-------|------------------|
| **100% Ledger Coverage** | ALL 6,477 features per model | Each has `final_status` |
| **SHAP Coverage** | Only RETAINED features (~400) | 100K+ samples each |

**SHAP is calculated only for RETAINED features, not all 6,477.** Pruned and excluded features have NULL SHAP values in the ledger.

### SHAP Cost Estimate Per Model (Pair-Horizon)

| Parameter | Value |
|-----------|-------|
| Retained features | ~400 (6.2% of 6,477) |
| SHAP samples | 100,000 |
| Base models | 4 |
| SHAP calculations | 400 × 100K × 4 = **160M** |

### Total SHAP Cost (All 196 Pair-Horizons)

| Metric | Calculation | Value |
|--------|-------------|-------|
| Pair-horizons | 28 pairs × 7 horizons | 196 |
| SHAP calculations per | 160M | 160M |
| **Total SHAP calculations** | 196 × 160M | **31.4 billion** |

### Compute Time Estimate

| Scenario | Time per Pair-Horizon | Total (196) |
|----------|----------------------|-------------|
| Sequential | 50-100 min | 163-327 hours |
| Parallel (4 workers) | - | 41-82 hours |
| Parallel (28 workers) | - | 6-12 hours |

### Cloud Cost Analysis

| Resource | Cost |
|----------|------|
| **BigQuery** | $0 - Data already loaded, no queries |
| **Local Compute** | $0 - Uses existing machine |
| **GCP Compute (if used)** | ~$5-10 (n2-standard-8 × 10 hours) |
| **Storage** | ~$0.01 (ledger parquet files) |
| **TOTAL** | **$0 - $10** |

### Memory Requirements

| Component | Size |
|-----------|------|
| Data sample (100K × 400 features) | ~300 MB |
| SHAP values (100K × 400) | ~300 MB |
| Model in memory | ~100 MB |
| **Total per model** | ~700 MB |
| **Peak (4 parallel models)** | ~2.8 GB |

### Cost-Optimized Strategy

1. **Batch Processing**: Process 25K samples at a time to limit memory
2. **Parallelization**: Run 4 base models concurrently (same data)
3. **Caching**: Store SHAP results, skip recalculation unless model changes
4. **Off-peak hours**: Run during nights/weekends if using cloud

### Summary

**100% Feature Coverage Cost:**
- **Ledger generation**: $0 (local processing)
- **SHAP testing (400 retained × 100K samples × 4 models)**: $0-10
- **Time cost**: 6-12 hours (parallelized) to 327 hours (sequential)

**Recommendation**: Use 28-worker parallelization to complete in ~6-12 hours at near-zero cloud cost.

---

## SUMMARY

| Item | BA Proposed | USER MANDATE (BINDING) |
|------|-------------|------------------------|
| SHAP sample size | 10,000 | **100,000+** |
| Validation | Coverage only | **Coverage + sample size check** |
| Metadata | Basic | **Include shap_config** |
| Cloud cost | - | **$0 additional** |

**All other aspects of BA's response are APPROVED.**

---

## EXPECTED ACKNOWLEDGMENT

Confirm understanding of:
1. SHAP sample size = 100,000+ (minimum)
2. User mandates supersede BA recommendations
3. Updated computational budget (~50-100 min per pair-horizon)

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Mandate Authority**: USER DIRECTIVE (highest priority)
