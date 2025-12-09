# BA Response: Feature Ledger Mandate Alignment

**Document Type**: Mandate Alignment Response
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Re**: Feature Ledger 100% Coverage Mandate

---

## MANDATE ACKNOWLEDGMENT

**Mandate Received**: 2025-12-09T12:00:00Z
**Understood**: YES
**Compliance**: MANDATORY

I acknowledge the binding user mandate requiring 100% feature coverage in the Feature Ledger for all 784 models.

---

## CLARIFICATION RESPONSES

### Q1: Ledger Generation

**Question from CE**: How should the initial ledger be populated? Script to enumerate all features? Before or during feature selection?

**BA Understanding**:
- Create `scripts/generate_feature_ledger.py` to query all 4,888+ tables
- Extract column names from INFORMATION_SCHEMA.COLUMNS
- Classify by scope based on table prefix

**Clarification Needed**:

1. **Timing**: Should ledger generation happen:
   - A) BEFORE CSI/VAR/MKT gap remediation (baseline of 6,477 features)
   - B) AFTER gap remediation (includes new CSI features)
   - C) TWO-PASS: Generate baseline now, regenerate after CSI complete

   **BA Recommendation**: Option C - establishes baseline immediately, then adds CSI features.

2. **Column Filtering**: Should the ledger include ALL columns from feature tables, or exclude metadata columns?
   - Exclude: `interval_time`, `pair`, `currency`, `direction`
   - Include: All numeric feature columns

   **BA Recommendation**: Exclude metadata columns, include only feature columns.

### Q2: CSI Integration

**Question from CE**: Separate ledger generation for CSI? Add to existing or regenerate?

**BA Understanding**:
- CSI tables (192) will add new currency_level features
- Each CSI table has ~50-100 aggregated columns per feature type
- Total new features: ~192 tables × ~75 avg columns = ~14,400 new features

**Clarification Needed**:

1. **Scope Assignment**: CSI features are per-currency, not per-pair. How should they map to pair models?
   - Option A: Include ALL 8 currency CSI features for all pairs
   - Option B: Include only RELEVANT currency CSI features (e.g., EURUSD gets EUR + USD CSI only)

   **BA Recommendation**: Option B - more meaningful signal, smaller feature set.

2. **Integration Method**:
   - Option A: Regenerate full ledger after CSI complete
   - Option B: Incremental append of CSI features to existing ledger

   **BA Recommendation**: Option A - cleaner, ensures consistency.

### Q3: Cross-Pair Feature Handling

**BA Understanding**: Clear from mandate.

For EURUSD model:
- `cov_eurusd_*` features → RETAINED/PRUNED
- `cov_gbpusd_*` features → EXCLUDED (not applicable)
- `tri_eur_*`, `tri_usd_*` → RETAINED/PRUNED
- `tri_gbp_*` → EXCLUDED (not applicable)

**Confirmation Requested**: Is this interpretation correct?

### Q4: SHAP Requirements

**BA Understanding**:
- All RETAINED features need SHAP values
- ~10,000 samples for SHAP calculation
- Store `importance_mean`, `importance_std` per feature

**Clarification Needed**:

1. **SHAP Method**: Which explainer should be used?
   - A) TreeExplainer (fast, for tree-based models)
   - B) KernelSHAP (model-agnostic, slower)
   - C) DeepSHAP (if neural nets added later)

   **BA Recommendation**: Option A (TreeExplainer) for LightGBM/XGBoost/CatBoost, KernelSHAP for ElasticNet.

2. **SHAP Per Model vs Ensemble**: Calculate SHAP for:
   - A) Each of 4 base models separately
   - B) Only the stacked ensemble
   - C) Both

   **BA Recommendation**: Option A - base model SHAP is more interpretable, ensemble SHAP is complex.

3. **Sample Selection**: For 10,000 SHAP samples:
   - A) Random sample from validation set
   - B) Stratified sample by target class
   - C) Stratified by regime (trending/ranging/volatile)

   **BA Recommendation**: Option B - ensures class balance in importance estimates.

### Q5: Validation Pipeline

**Question from CE**: Automatic after each run, batch at end, or CI/CD integrated?

**BA Recommendation**: HYBRID APPROACH

| Gate | Validation Type | Timing |
|------|-----------------|--------|
| Pre-Training | V1-V4 (row count, status, scope, prune audit) | Before each pair-horizon training |
| Post-Training | V5 (SHAP coverage) | After each pair-horizon training |
| Aggregate | Full validation | After all 784 models trained |

**Rationale**: Catch issues early (per-model validation) while maintaining efficiency.

### Q6: Other Concerns

**Task Sequencing Concern**:

Current task queue:
1. Phase R2: CSI Implementation (192 tables) - IN PROGRESS
2. Phase R3: VAR Completion (59 tables)
3. Phase R4: MKT Completion (14 tables)
4. Phase R5: Update feature catalogue

New mandate adds:
5. Generate initial feature ledger
6. Integrate ledger into feature selection
7. Add SHAP to training pipeline

**Question**: Should BA:
- A) Complete gap remediation first (CSI/VAR/MKT), THEN generate ledger
- B) Pause gap remediation, generate baseline ledger NOW, then resume
- C) Parallel track: Generate ledger while continuing gap remediation

**BA Recommendation**: Option A - Gap remediation is infrastructure, ledger depends on complete feature universe.

---

## PROPOSED APPROACH

### Phase L1: Initial Ledger (After Gap Remediation)

```
Timeline: After CSI/VAR/MKT complete
Script: scripts/generate_feature_ledger.py
Output: feature_ledger_initial.parquet
```

Steps:
1. Query INFORMATION_SCHEMA.COLUMNS for all 5,000+ tables
2. Filter to feature columns only
3. Classify by scope (pair_specific, cross_pair, market_wide, currency_level)
4. Generate initial ledger with final_status = 'PENDING'
5. Validate row count = feature_universe_count

### Phase L2: Selection Integration

```
Timeline: During Phase 4 training (EURUSD horizons)
Script: Modify feature_selection_robust.py
Output: feature_ledger_{pair}_{horizon}.parquet
```

Steps:
1. Load initial ledger
2. Track pruning at each stage (constant, duplicate, correlated, unstable)
3. Update final_status → RETAINED/PRUNED/EXCLUDED
4. Record stability_freq for retained features

### Phase L3: SHAP Integration

```
Timeline: During Phase 4 training
Script: Modify stack_calibrated.py
Output: feature_ledger_{pair}_{horizon}_shap.parquet
```

Steps:
1. After base model training, run TreeExplainer
2. Store importance_mean, importance_std
3. Validate SHAP coverage for all RETAINED

### Phase L4: Aggregation

```
Timeline: After Phase 5 (all 784 models)
Script: scripts/aggregate_feature_ledger.py
Output: feature_ledger.parquet (master)
```

---

## TIMELINE ESTIMATE

| Phase | Task | Duration |
|-------|------|----------|
| Current | Gap Remediation (CSI/VAR/MKT) | 4-6 hours |
| L1 | Initial Ledger Generation | 1 hour |
| L2 | Selection Integration | 2 hours (code changes) |
| L3 | SHAP Integration | 2 hours (code changes) |
| L4 | Aggregation | 30 minutes |

**Total Additional Work**: ~5.5 hours of development
**Note**: L2-L3 run DURING training, not separate time blocks

---

## CONFIRMATION REQUESTED

1. Task sequencing (Option A/B/C)
2. CSI scope assignment (Option A/B)
3. SHAP method and scope (Options above)
4. Cross-pair interpretation (confirmation)

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 9, 2025
**Status**: AWAITING CE GUIDANCE ON CLARIFICATIONS
