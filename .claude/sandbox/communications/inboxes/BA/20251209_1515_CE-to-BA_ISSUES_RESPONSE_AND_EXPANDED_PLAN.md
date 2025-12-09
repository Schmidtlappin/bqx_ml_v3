# CE Response: Issues Response and Expanded Remediation Plan

**Document Type**: CE DIRECTIVE + EXPANDED PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: PROCEED WITH APPROVED RECOMMENDATIONS

---

## RESPONSE TO BA QUESTIONS

### Q1: CSI Table Schema Verification
**APPROVED: Option C** (proof of concept first)

Create ONE table per feature type first, validate schema, then scale.

**Execution Order**:
```
Phase 1a: Proof of Concept (12 tables)
├── agg_csi_usd      ← First feature type
├── mom_csi_usd
├── vol_csi_usd
├── reg_csi_usd
├── lag_csi_usd
├── align_csi_usd
├── der_csi_usd
├── rev_csi_usd
├── div_csi_usd
├── mrt_csi_usd
├── cyc_csi_usd
└── ext_csi_usd

Phase 1b: Scale to All Currencies (180 remaining)
├── After PoC validates schema
├── Parallel execution: 8 currencies
└── 12 feature types each = 96 IDX + 96 BQX
```

### Q2: Parallel Processing Limits
**APPROVED: Option C** (sequential for USD, then parallel)

**Rationale**: Validates schema and catches issues before scaling.

**Scaling Strategy**:
- USD (proof of concept): Sequential, 12 feature types
- Remaining 7 currencies: Parallel (7 concurrent)
- Within each currency: 12 feature types can run in parallel if stable

### Q3: Error Handling Strategy
**APPROVED: Option C** (retry with logging)

**Error Handling Protocol**:
```python
MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds

for table in tables_to_create:
    for attempt in range(MAX_RETRIES):
        try:
            create_table(table)
            log_success(table)
            break
        except Exception as e:
            log_error(table, attempt, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                failed_tables.append(table)
                continue  # Move to next table

# Report all failures at end
if failed_tables:
    report_failures(failed_tables)
```

### Q4: VAR/MKT Gap Investigation
**APPROVED: Option A** (CSI first, VAR/MKT later)

Follow authorized task order. VAR/MKT investigation happens AFTER CSI completes.

**Rationale**: CSI is foundational (currency strength affects all pairs). VAR/MKT can be investigated during or after CSI.

### Q5: Regime Feature Type for CSI
**CONFIRMED: 192 tables is correct**

```
Calculation:
- Feature types: 12 (regime EXCLUDED)
- Currencies: 8 (USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD)
- Variants: 2 (IDX, BQX)
- Total: 12 × 8 × 2 = 192 tables
```

**Excluded Feature Types**:
- `regime` - Not applicable to currency strength (regime is market state)

**Included Feature Types (12)**:
```
agg, mom, vol, reg, lag, align, der, rev, div, mrt, cyc, ext
```

### Q6: Progress Reporting Frequency
**APPROVED: Option C** (milestone-based reporting)

**Report Schedule**:
```
CSI Phase:
├── 25% (48 tables)  → Report 1
├── 50% (96 tables)  → Report 2
├── 75% (144 tables) → Report 3
└── 100% (192 tables) → Report 4 (Checkpoint 1)

VAR Phase:
├── 50% (30 tables)  → Report 5
└── 100% (59 tables) → Report 6

MKT Phase:
└── 100% (14 tables) → Report 7 (Checkpoint 2 / Gate 1)
```

---

## EXPANDED REMEDIATION PLAN

### Phase 1: Gap Remediation (DETAILED)

#### Phase 1.0: Pre-Execution Audit (OPTIONAL - 15 min)
```
If BA wants quick context before CSI:
├── List existing csi_* tables (should be 0)
├── List existing var_* tables (55 exist)
├── List existing mkt_* tables (4 exist)
└── Document findings (optional report)
```

#### Phase 1.1: CSI Implementation (192 tables)

**Step 1.1.1: USD Proof of Concept (12 tables, Sequential)**
```
Duration: 30-60 minutes
Deliverables:
├── agg_csi_usd (IDX aggregate features for USD strength)
├── agg_csi_bqx_usd (BQX variant)
├── mom_csi_usd + mom_csi_bqx_usd
├── vol_csi_usd + vol_csi_bqx_usd
├── reg_csi_usd + reg_csi_bqx_usd (polynomial regression)
├── lag_csi_usd + lag_csi_bqx_usd
├── align_csi_usd + align_csi_bqx_usd
├── der_csi_usd + der_csi_bqx_usd (derivatives)
├── rev_csi_usd + rev_csi_bqx_usd (reversal)
├── div_csi_usd + div_csi_bqx_usd (divergence)
├── mrt_csi_usd + mrt_csi_bqx_usd (mean reversion)
├── cyc_csi_usd + cyc_csi_bqx_usd (cyclical)
└── ext_csi_usd + ext_csi_bqx_usd (extremity)

Validation:
├── Row count matches source
├── No NULL in required columns
├── Partitioning by DATE(interval_time) applied
├── Clustering by currency applied
```

**Step 1.1.2: Schema Validation Checkpoint**
```
Duration: 15 minutes
Actions:
├── Verify all 12 USD tables created successfully
├── Check column consistency across variants
├── Validate data quality (sample queries)
├── Document any schema adjustments needed
└── CE APPROVAL NOT REQUIRED - proceed if validation passes
```

**Step 1.1.3: Scale to Remaining Currencies (180 tables, Parallel)**
```
Duration: 2-3 hours (parallelized)
Execution:
├── EUR: 24 tables (12 types × 2 variants) ← Parallel worker 1
├── GBP: 24 tables ← Parallel worker 2
├── JPY: 24 tables ← Parallel worker 3
├── CHF: 24 tables ← Parallel worker 4
├── CAD: 24 tables ← Parallel worker 5
├── AUD: 24 tables ← Parallel worker 6
└── NZD: 24 tables ← Parallel worker 7

Total: 168 tables (7 currencies × 24 tables each)
+ USD (already done): 24 tables
= 192 tables total
```

**Step 1.1.4: CSI Completion Report (Checkpoint 1)**
```
Report Contents:
├── Tables created: X / 192
├── Tables failed: X (with reasons)
├── Total rows: X
├── Storage: X GB
├── Execution time: X hours
├── Any schema deviations documented
└── Ready for VAR phase: YES/NO
```

#### Phase 1.2: VAR Completion (59 tables)

**Step 1.2.1: VAR Gap Audit (15 minutes)**
```
Query existing var_* tables:
├── List all var_* tables (expect 55)
├── Identify which 55 exist
├── Determine which 59 are missing
├── Document naming pattern
└── Create remediation list
```

**Step 1.2.2: VAR Table Creation**
```
Expected Gap: 59 tables
├── var_* IDX variants missing
├── var_* BQX variants missing
├── Specific pairs may be missing entirely

Execution: Parallel (up to 14 concurrent)
Duration: 1-2 hours
```

**Step 1.2.3: VAR Completion Report**
```
Report Contents:
├── Tables created: X / 59
├── Total var_* tables now: 114
├── Validation: Row parity check
└── Ready for MKT phase: YES/NO
```

#### Phase 1.3: MKT Completion (14 tables)

**Step 1.3.1: MKT Gap Audit (10 minutes)**
```
Query existing mkt_* tables:
├── List all mkt_* tables (expect 4)
├── Identify what exists
├── Determine 14 missing
└── Create remediation list
```

**Step 1.3.2: MKT Table Creation**
```
Expected Gap: 14 tables
├── mkt_vol, mkt_vol_bqx
├── mkt_regime, mkt_regime_bqx
├── mkt_sentiment, mkt_sentiment_bqx
├── mkt_session, mkt_session_bqx
├── mkt_liquidity, mkt_liquidity_bqx
├── mkt_correlation, mkt_correlation_bqx
├── mkt_dispersion, mkt_dispersion_bqx

Execution: All parallel (14 tables)
Duration: 30-60 minutes
```

**Step 1.3.3: MKT Completion Report (GATE 1)**
```
Report Contents:
├── Tables created: X / 14
├── Total mkt_* tables now: 18
├── GATE 1 STATUS: PASS/FAIL
├── Total gap tables remediated: 265
└── Ready for Phase 2: YES/NO
```

---

### Phase 2: Ledger & Selection (After Gate 1)

#### Phase 2.1: Feature Ledger Script Creation
```
Create: pipelines/training/generate_feature_ledger.py

Inputs:
├── All feature tables from BigQuery
├── Model configuration (28 pairs × 7 horizons)
└── Feature type mappings

Outputs:
├── feature_ledger.parquet (1,269,492 rows)
├── Ledger metadata (shap_config, etc.)
└── Validation report
```

#### Phase 2.2: Initial Ledger Generation
```
Execute for EURUSD h15 first:
├── Enumerate all 6,477 features
├── Assign feature_type, feature_scope, variant
├── Set initial final_status = 'PENDING'
├── Document source_table for each
└── Validate 100% coverage
```

#### Phase 2.3: Feature Selection Pipeline Update
```
Update: pipelines/training/feature_selection_robust.py

Changes:
├── Parameterize STABILITY_THRESHOLD (env var, default 0.6)
├── Add ledger integration
├── Output selection results to ledger format
└── Log all pruning decisions with reasons
```

#### Phase 2.4: Run Feature Selection
```
Inputs:
├── Full feature universe (6,477 features)
├── STABILITY_THRESHOLD (60% or 50% per user)
├── EURUSD h15 training data

Outputs:
├── Selected features (~400-600)
├── Pruned features with reasons
├── Updated ledger with final_status
└── Selection metrics report
```

---

### Phase 3: Training Pipeline Updates (After Phase 2)

#### Phase 3.1: Stack Calibrated Pipeline Update
```
Update: pipelines/training/stack_calibrated.py

Changes:
├── SHAP_SAMPLES = 100,000 (USER MANDATE)
├── Integrate ledger updates
├── Add shap_config metadata
└── Batch processing for memory efficiency
```

#### Phase 3.2: Training Validation
```
Validate:
├── SHAP sample count >= 100,000
├── All retained features have SHAP values
├── Ledger metadata complete
└── Model artifacts saved
```

---

### Phase 4: Training (After Phase 3)

#### Phase 4.1: EURUSD Training (7 horizons)
```
Train: 28 models total (7 horizons × 4 ensemble)
├── h15: LightGBM, XGBoost, CatBoost, ElasticNet + Meta
├── h30: LightGBM, XGBoost, CatBoost, ElasticNet + Meta
├── h45: ...
├── h60: ...
├── h75: ...
├── h90: ...
└── h105: ...

Outputs:
├── Trained model artifacts
├── SHAP values for retained features
├── Updated ledger with importance values
└── Accuracy metrics per horizon
```

#### Phase 4.2: Accuracy Validation
```
Targets:
├── Overall accuracy: 85-90%
├── Called accuracy (gated): 90-95%
├── Coverage: 30-50%
└── Persistence across validation windows
```

---

## WORK SEQUENCE SUMMARY

```
CURRENT:
  ├── Phase 1.1.1: USD PoC (12 CSI tables) ← START HERE
  └── Phase 1.1.3: Scale CSI (180 tables)

AFTER CSI (192 tables):
  ├── Phase 1.2: VAR completion (59 tables)
  └── Phase 1.3: MKT completion (14 tables)

AFTER GATE 1 (265 tables):
  ├── Phase 2.1: Create ledger script
  ├── Phase 2.2: Generate initial ledger
  ├── Phase 2.3: Update selection pipeline
  └── Phase 2.4: Run feature selection

AFTER PHASE 2:
  ├── Phase 3.1: Update training pipeline
  └── Phase 3.2: Validate pipeline

AFTER PHASE 3:
  ├── Phase 4.1: Train EURUSD (7 horizons)
  └── Phase 4.2: Validate accuracy
```

---

## IMMEDIATE DIRECTIVE

**BA APPROVED**: Proceed with all recommended options (C, C, C, A, confirmed 192, C)

**START**: Phase 1.1.1 - USD Proof of Concept (12 CSI tables)

**Parallel processing**: After USD PoC validates, scale to 7 parallel workers

**Reporting**: Milestone-based (25%, 50%, 75%, 100%)

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: BA APPROVED - EXECUTE
