# BA Response: Feature Ledger Mandate Alignment

**Document Type**: Response to USER MANDATE
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**RE**: Feature Ledger 100% Coverage Mandate
**Status**: ACKNOWLEDGED - Full Compliance Committed

---

## MANDATE ACKNOWLEDGMENT

I acknowledge receipt and understanding of the **FEATURE LEDGER 100% COVERAGE MANDATE** as specified in:

1. `/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md`
2. User directive: "100% coverage of features including pair and non-pair specific features per model"

**BINDING STATUS**: Confirmed. This is a USER MANDATE requiring full compliance.

**SCOPE UNDERSTANDING**:
- 6,477 features per model (current)
- 1,269,492 total ledger rows (28 pairs × 7 horizons × 6,477 features)
- 100% coverage requirement: Every feature must have `final_status` (RETAINED, PRUNED, or EXCLUDED)
- All RETAINED features require SHAP values
- Ledger must be auditable, validated, and complete

I confirm full alignment with this requirement and commit to implementing the complete Feature Ledger system.

---

## RESPONSES TO CLARIFYING QUESTIONS

### Q1: Ledger Generation Approach

**Answer**: Two-phase approach with initial enumeration followed by selection integration.

#### Phase 1: Initial Ledger Generation (Pre-Selection)

**Script**: `/scripts/generate_feature_ledger_initial.py`

**Approach**:
1. Query BigQuery `INFORMATION_SCHEMA.COLUMNS` for all tables in `bqx_ml_v3_features_v2`
2. Extract all feature columns (exclude metadata: `interval_time`, `pair`, `pair1`, `pair2`)
3. Classify each feature by:
   - `feature_type`: Extract from column prefix (agg_, mom_, cov_, etc.)
   - `feature_scope`: Determine from table naming pattern
     - **pair_specific**: Tables named `{type}_{pair}` or `{type}_{variant}_{pair}`
     - **cross_pair**: Tables named `cov_*`, `corr_*`, `tri_*`
     - **market_wide**: Tables named `mkt_*`
     - **currency_level**: Tables named `csi_*` (currently 0, will be 192 after CSI implementation)
   - `variant`: Extract IDX/BQX/OTHER from table name
   - `source_table`: Full BigQuery table path
4. Generate initial ledger template with:
   - All feature metadata populated
   - `final_status` = NULL (to be filled during selection)
   - All selection metrics = NULL
5. Cross-multiply by all pair-horizon combinations
6. Apply EXCLUDED logic for non-applicable features:
   - Cross-pair features only apply to their specific pair (e.g., cov_EURUSD_* → EXCLUDED for GBPUSD)
   - Market-wide features apply to ALL pairs → never EXCLUDED

**Output**: `intelligence/feature_ledger_initial.parquet` (~1.27M rows, 17 columns)

**Timing**: Before any feature selection runs (one-time generation, refresh when tables change)

#### Phase 2: Selection Integration (Per Training Run)

**Integration Point**: `/pipelines/training/feature_selection_robust.py`

**Approach**:
1. Load initial ledger filtered for target pair + horizon
2. During each selection stage, update ledger rows:
   - **Stage 1 (Safe Pruning)**: Update pruned features with:
     - `pruned_stage` = 1
     - `prune_reason` = 'constant', 'missing', 'near_constant'
     - `final_status` = 'PRUNED'
   - **Stage 2 (Clustering)**: Update non-representatives with:
     - `pruned_stage` = 2
     - `prune_reason` = 'correlated'
     - `cluster_id` = cluster representative feature
     - `final_status` = 'PRUNED'
   - **Stage 3 (Group Screening)**: Record `screen_score` for all features
   - **Stage 4 (Stability Selection)**: Update stable features with:
     - `stability_freq` = selection frequency across folds
     - `final_status` = 'RETAINED' (if stable) or 'PRUNED' (if unstable, stage=4, reason='unstable')
3. Validate 100% coverage: `SUM(final_status IS NOT NULL) = 6,477`
4. Save pair-horizon ledger: `intelligence/feature_ledger_{pair}_h{horizon}.parquet`

**Output**: Per-model ledgers with complete selection audit trail

---

### Q2: CSI Integration Approach

**Answer**: Regenerate initial ledger from scratch after CSI implementation.

#### Rationale
- CSI adds 192 new tables with unknown column counts
- Feature universe size changes from 6,477 to ~6,669+ per model
- Safer to regenerate complete ledger than patch incrementally

#### Proposed CSI Integration Workflow

1. **CSI Implementation** (BA current task):
   - Create 192 tables: `csi_{feature}_{currency}` for 8 currencies × 13 types × 2 variants
   - Populate with aggregated currency-level features

2. **Ledger Regeneration**:
   - Run `generate_feature_ledger_initial.py` again
   - Script will automatically discover CSI tables
   - Classify CSI features as `feature_scope='currency_level'`
   - Generate new initial ledger with updated feature count

3. **Validation Updates**:
   - Update expected feature count in validation queries (6,477 → ~6,669)
   - Update scope distribution expectations to include currency_level

4. **Migration**:
   - Archive old initial ledger as `feature_ledger_initial_v1_pre_csi.parquet`
   - Deploy new initial ledger as `feature_ledger_initial_v2_with_csi.parquet`

**Timing**: After CSI tables are created and populated (estimated: within 2-3 days)

**No Incremental Patching**: Too error-prone. Full regeneration ensures consistency and catches any other table changes.

---

### Q3: Cross-Pair Feature Handling Clarity

**Answer**: Mapping is clear. EXCLUDED status prevents inappropriate usage.

#### Cross-Pair Feature → Pair Mapping

**Type: Covariance (cov_)**
- Naming: `cov_{pair1}_{pair2}_{variant}_{metric}_{window}`
- Example: `cov_EURUSD_GBPUSD_bqx_corr_45`
- **Applies to**: BOTH pair1 AND pair2 models
- **EXCLUDED for**: All other 26 pairs

**Type: Correlation (corr_)**
- Naming: `corr_{pair1}_{pair2}_{variant}_{metric}_{window}`
- Example: `corr_EURUSD_JPYUSD_idx_pearson_90`
- **Applies to**: BOTH pair1 AND pair2 models
- **EXCLUDED for**: All other pairs

**Type: Triangulation (tri_)**
- Naming: `tri_{currency}_{metric}_{window}`
- Example: `tri_EUR_bqx_arbitrage_45`, `tri_USD_idx_strength_90`
- **Applies to**: Any pair containing that currency
  - `tri_EUR_*` → EURUSD, EURGBP, EURJPY, EURCHF, EURCAD, EURAUD, EURNZD (7 pairs)
  - `tri_USD_*` → EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD (7 pairs)
  - Other currencies similarly
- **EXCLUDED for**: Pairs not containing that currency

#### Ledger Implementation

For EURUSD h15 ledger:
- `cov_EURUSD_*` features: `final_status` = RETAINED/PRUNED (eligible)
- `cov_GBPUSD_*` features: `final_status` = EXCLUDED (not applicable)
- `tri_EUR_*` features: `final_status` = RETAINED/PRUNED (eligible, EUR in pair)
- `tri_GBP_*` features: `final_status` = EXCLUDED (not applicable, GBP not in EURUSD)

#### Validation Query

```sql
-- Verify EXCLUDED features are correctly identified
SELECT pair, feature_scope,
       COUNT(*) as excluded_count
FROM feature_ledger
WHERE final_status = 'EXCLUDED'
GROUP BY pair, feature_scope
```

**Expected for EURUSD**:
- cross_pair EXCLUDED: ~90% of cross-pair features (other pairs' cov/corr, non-EUR/USD tri)
- market_wide EXCLUDED: 0 (mkt applies to all)
- pair_specific EXCLUDED: ~93% (other 27 pairs' features)

**Clarity Confirmed**: The mapping logic is deterministic and can be implemented via table name parsing.

---

### Q4: SHAP Requirements Clarity

**Answer**: Approach is clear. Computational strategy defined to handle scale.

#### SHAP Calculation Scope

**Who**: All base models (LightGBM, XGBoost, CatBoost, ElasticNet)
**What**: All features with `final_status = 'RETAINED'`
**When**: During model training in `stack_calibrated.py`, after base models are trained
**How Many**: ~400 stable features per model (based on EURUSD h15 test)

#### Computational Strategy

**Sample Size**:
- Use validation fold data (~10,000-15,000 samples per fold)
- For walk-forward CV with 5 folds, calculate SHAP on each fold's validation set
- Aggregate mean/std across folds

**SHAP Method**:
- **Tree models (LGB/XGB/CB)**: Use TreeExplainer (fast, exact)
- **Linear models (ElasticNet)**: Use LinearExplainer (instant)
- **Avoid KernelExplainer**: Too slow for 400 features × 10K samples

**Parallelization**:
- Calculate SHAP per base model in parallel (4 models)
- Each base model processes its features independently
- Combine results into single ledger update

#### Implementation in stack_calibrated.py

```python
# After training base models
for model_name, model_data in base_models.items():
    model = model_data['model']
    X_val = validation_data[retained_features]

    # Calculate SHAP
    if model_name in ['lightgbm', 'xgboost', 'catboost']:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_val)
    else:  # elasticnet
        explainer = shap.LinearExplainer(model, X_val)
        shap_values = explainer.shap_values(X_val)

    # Aggregate per feature
    shap_importance = np.abs(shap_values).mean(axis=0)

    # Update ledger
    for i, feat in enumerate(retained_features):
        ledger.loc[ledger['feature_name'] == feat,
                   f'importance_mean_{model_name}'] = shap_importance[i]
```

**Post-Processing**:
- Average `importance_mean` across all base models → single `importance_mean` column
- Calculate `importance_std` across base models to measure consistency
- Validate: `SUM(final_status='RETAINED' AND importance_mean IS NULL) = 0`

#### Computational Budget

Per pair-horizon:
- SHAP samples: 10,000
- Retained features: ~400
- Base models: 4
- **Total SHAP calculations**: 4 × 400 × 10,000 = 16M
- **Estimated time**: ~5-10 minutes per pair-horizon on TreeExplainer

For 784 models (28 pairs × 7 horizons × 4 ensemble members):
- **Total time**: ~65-130 hours if sequential
- **Parallelizable**: Run 7 horizons × 4 models in parallel → ~2-4 hours on multi-core

**Clarity Confirmed**: SHAP calculation is feasible and strategy is defined.

---

### Q5: Validation Pipeline Approach

**Answer**: Hybrid approach with immediate validation + batch audit.

#### Immediate Validation (Per Training Run)

**Integration Point**: End of `feature_selection_robust.py` and `stack_calibrated.py`

**Validations**:
1. **V1 (Row Count)**: Assert ledger has exactly 6,477 rows
2. **V2 (Status Coverage)**: Assert all rows have non-NULL `final_status`
3. **V4 (Pruned Audit)**: Assert all PRUNED have `pruned_stage` + `prune_reason`
4. **SHAP Coverage**: Assert all RETAINED have `importance_mean`

**Failure Behavior**:
- STOP training if validation fails
- Log detailed error with missing/invalid rows
- Do NOT proceed to model deployment

**Code Example**:
```python
def validate_feature_ledger(ledger_df, pair, horizon):
    """Run critical validations before saving ledger."""
    n_rows = len(ledger_df)
    assert n_rows == 6477, f"Expected 6,477 rows, got {n_rows}"

    missing_status = ledger_df['final_status'].isna().sum()
    assert missing_status == 0, f"{missing_status} rows missing final_status"

    pruned = ledger_df[ledger_df['final_status'] == 'PRUNED']
    invalid_pruned = pruned[
        pruned['pruned_stage'].isna() | pruned['prune_reason'].isna()
    ]
    assert len(invalid_pruned) == 0, f"{len(invalid_pruned)} PRUNED without stage/reason"

    retained = ledger_df[ledger_df['final_status'] == 'RETAINED']
    missing_shap = retained[retained['importance_mean'].isna()]
    assert len(missing_shap) == 0, f"{len(missing_shap)} RETAINED missing SHAP"

    print(f"✓ Ledger validation passed for {pair} h{horizon}")
```

#### Batch Audit (Post-Training)

**Script**: `/scripts/audit_feature_ledger.py`

**When**: After completing a batch of training runs (e.g., all 7 horizons for a pair)

**Audits**:
- **V3 (Scope Distribution)**: Verify pair_specific/cross_pair/market_wide counts match expected
- **V5 (Catalogue Cross-Reference)**: Verify all catalogue features appear in ledger
- **Aggregate Statistics**:
  - Prune rate by stage
  - Stability frequency distribution
  - SHAP importance distribution
  - Feature type representation

**Output**: `intelligence/audit_report_{pair}_{timestamp}.json`

#### CI/CD Integration (Future)

**Phase 2 Enhancement** (after initial implementation stabilizes):
- Add ledger validation to pre-commit hooks
- Integrate ledger generation into model training Airflow DAG
- Add ledger quality metrics to monitoring dashboard

**Current Recommendation**: Start with immediate validation only. Add batch audit after first successful training runs.

---

### Q6: Additional Concerns or Blockers

#### Concern 1: Feature Universe Growth Over Time

**Issue**: As we add new feature types or tables, the feature universe changes (6,477 → 6,669 → ???)

**Mitigation**:
- Version the initial ledger: `feature_ledger_initial_v1.parquet`, `v2`, etc.
- Store expected feature count in ledger metadata
- Validation queries reference metadata, not hardcoded counts
- Re-run `generate_feature_ledger_initial.py` whenever schema changes

**Proposed Metadata**:
```json
{
  "ledger_version": "2.0.0",
  "feature_universe_version": "v2_with_csi",
  "expected_feature_count": 6669,
  "table_count": 5080,
  "scope_distribution": {
    "pair_specific": 1569,
    "cross_pair": 4332,
    "market_wide": 576,
    "currency_level": 192
  },
  "last_regenerated": "2025-12-11T10:00:00Z"
}
```

#### Concern 2: Storage and Query Performance

**Issue**: 1.27M rows × 17 columns = large parquet file, slow to query repeatedly

**Mitigation**:
- **Partitioning**: Store ledger partitioned by pair and horizon
  - `intelligence/feature_ledger/pair=EURUSD/horizon=h15/ledger.parquet`
  - Each partition = 6,477 rows (manageable)
- **Lazy Loading**: Only load relevant partition during training
- **Compression**: Parquet with snappy compression (~5-10x reduction)
- **Indexing**: Keep in-memory dict mapping feature_name → row during selection

**Storage Estimate**:
- Uncompressed: ~200 MB (17 cols × 1.27M rows × ~10 bytes/cell)
- Compressed: ~20-40 MB (parquet compression)
- Per-partition: ~15 KB each (6,477 rows)

**Performance**: Non-issue. Parquet read of 6,477 rows is <100ms.

#### Concern 3: Model-Specific vs Pair-Horizon Ledgers

**Question**: Should we track ledgers per ensemble member (784 total) or per pair-horizon (196 total)?

**Recommendation**: **Per pair-horizon** (196 ledgers, not 784)

**Rationale**:
- All 4 ensemble members (LGB/XGB/CB/EN) use the SAME feature selection
- SHAP values differ per model, but can be stored as separate columns:
  - `importance_mean_lightgbm`
  - `importance_mean_xgboost`
  - `importance_mean_catboost`
  - `importance_mean_elasticnet`
  - `importance_mean` (average across models)
- Reduces ledger count by 4× (easier to manage)
- Still provides full SHAP traceability per base model

**Updated Row Count**: `28 pairs × 7 horizons × 6,477 features = 1,269,492` (not 5M+)

#### Concern 4: EXCLUDED Feature Proportion

**Issue**: For each pair, ~90%+ of cross-pair features are EXCLUDED. Is this correct?

**Analysis**:
- Total cross-pair features: 4,332
- Applicable to EURUSD:
  - `cov_EURUSD_*`: ~72 features (27 other pairs × ~2.7 cov features per pair-pair)
  - `corr_EURUSD_*`: ~8 features (27 other pairs × ~0.3 corr features)
  - `tri_EUR_*` + `tri_USD_*`: ~2,088 features (matches catalogue)
  - **Total applicable**: ~2,168 features
- **EXCLUDED**: 4,332 - 2,168 = 2,164 features (~50% of cross-pair)

**Revised Understanding**: Not 90%, closer to 50% of cross-pair features are EXCLUDED per model.

**Validation Impact**: Update V3 scope distribution to expect ~2,200 cross-pair, not 4,332, per model.

#### Concern 5: Initial Ledger Generation Time

**Issue**: Querying 4,888 tables to extract columns might be slow

**Mitigation**:
- Use `INFORMATION_SCHEMA.COLUMNS` batch query (single query for all tables)
- Cache table schemas in `intelligence/table_schemas_v2.json`
- Re-use cache unless tables change (detect via `__TABLES__.last_modified_time`)

**Estimated Time**:
- First run: ~5-10 minutes (query all schemas)
- Subsequent runs: ~30 seconds (use cache)

#### No Critical Blockers

All concerns have clear mitigations. Implementation can proceed immediately.

---

## PROPOSED IMPLEMENTATION PLAN

### Phase 1: Ledger Generation Script (2-3 days)

**Deliverable**: `/scripts/generate_feature_ledger_initial.py`

**Tasks**:
1. Query BigQuery schema for all tables in `bqx_ml_v3_features_v2`
2. Extract feature columns with metadata (type, scope, variant, source)
3. Generate initial ledger template (6,477 features × 28 pairs × 7 horizons)
4. Apply EXCLUDED logic for non-applicable features
5. Save partitioned parquet: `intelligence/feature_ledger/pair={pair}/horizon={horizon}/ledger_initial.parquet`
6. Generate metadata JSON with feature counts and validation expectations

**Validation**:
- Row count = 1,269,492
- All features from `feature_catalogue.json` present
- EXCLUDED features correctly identified

### Phase 2: Feature Selection Integration (3-4 days)

**Deliverable**: Updated `/pipelines/training/feature_selection_robust.py`

**Tasks**:
1. Load initial ledger at start of selection
2. Update ledger during each pruning stage:
   - Safe pruning → stage 1
   - Clustering → stage 2
   - Stability selection → stage 4
3. Add validation function called after selection completes
4. Save updated ledger: `intelligence/feature_ledger/pair={pair}/horizon={horizon}/ledger_selected.parquet`

**Validation**:
- All PRUNED have stage + reason
- All RETAINED/EXCLUDED have NULL pruned_stage
- 100% status coverage

### Phase 3: SHAP Integration (2-3 days)

**Deliverable**: Updated `/pipelines/training/stack_calibrated.py`

**Tasks**:
1. Load selected ledger after feature selection completes
2. Calculate SHAP for all RETAINED features per base model
3. Update ledger with importance_mean, importance_std per model
4. Add SHAP coverage validation
5. Save final ledger: `intelligence/feature_ledger/pair={pair}/horizon={horizon}/ledger_final.parquet`

**Validation**:
- All RETAINED features have SHAP values
- SHAP values are non-negative
- At least one feature has importance > 0

### Phase 4: Audit and Aggregation (1-2 days)

**Deliverable**: `/scripts/audit_feature_ledger.py`

**Tasks**:
1. Combine all pair-horizon ledgers into master ledger
2. Run comprehensive audits (V1-V5)
3. Generate summary statistics report
4. Create visualization of prune rates, SHAP distributions

**Output**:
- `intelligence/feature_ledger_master.parquet` (all 1.27M rows)
- `intelligence/feature_ledger_audit_report.json`

### Phase 5: CSI Integration (After CSI Implementation)

**Tasks**:
1. Wait for CSI tables to be created (192 tables)
2. Re-run `generate_feature_ledger_initial.py`
3. Update validation expected counts (6,477 → ~6,669)
4. Archive v1 ledger, deploy v2 ledger

---

## TIMELINE ESTIMATE

**Current Status**: CSI implementation in progress (expected completion: 2-3 days)

**Ledger Implementation**:
- Phase 1 (Initial Generation): 2-3 days
- Phase 2 (Selection Integration): 3-4 days
- Phase 3 (SHAP Integration): 2-3 days
- Phase 4 (Audit): 1-2 days
- **Total**: 8-12 days

**Integration with CSI Task**:
- Option A: Implement ledger in parallel with CSI → Complete both by Dec 21
- Option B: Wait for CSI completion, then implement ledger → Complete by Dec 23

**Recommendation**: **Option A** - Start Phase 1 immediately using current 6,477 feature universe. Re-run Phase 1 after CSI completes.

**Rationale**:
- Gets ledger framework in place sooner
- Tests validation logic on current data
- Only requires re-running Phase 1 (2-3 days) after CSI, not full re-implementation

---

## COMMITMENT SUMMARY

I, Build Agent (BA), commit to:

1. **100% Feature Coverage**: Every feature in the universe will appear in the ledger with a final_status
2. **Complete Audit Trail**: All pruning decisions will be documented with stage + reason
3. **SHAP Coverage**: All RETAINED features will have importance values
4. **Validation Gates**: No training will proceed without passing V1-V5 validations
5. **CSI Integration**: Ledger will be regenerated after CSI implementation to include currency-level features
6. **Timeline Adherence**: Ledger system will be operational within 8-12 days

This mandate is binding and will be implemented with full fidelity to the specification.

---

**BA Signature**: Claude (Build Agent, BQX ML V3)
**Date**: December 9, 2025
**Status**: ALIGNED AND COMMITTED
