# CRITICAL: Feature Count Reconciliation Report

**Date**: 2025-12-13
**Author**: Claude (Chief Engineer)
**Priority**: P0 - CRITICAL DISCREPANCY

---

## EXECUTIVE SUMMARY

A critical discrepancy has been discovered between documented feature counts and actual training file contents:

| Source | Count | Context |
|--------|-------|---------|
| **Previous Documentation** | 1,127 | Documented in mandates as "unique features per pair" |
| **Feature Catalogue v3.0.0** | 1,604 | Unique column NAMES across all BigQuery tables |
| **Actual Training File (EURUSD)** | **16,988** | **ACTUAL features in merged training file** |

**Impact**: Feature Ledger sizing, documentation accuracy, cost estimates, all affected.

---

## ROOT CAUSE ANALYSIS

### The Three Numbers Explained

1. **1,127 (INCORRECT - LEGACY)**
   - **What it represented**: Early estimate of unique features
   - **Problem**: Did not account for:
     - Column name duplicates across different table types
     - Prefixed variants in merged output
     - Cross-pair feature multiplication
   - **Status**: SUPERSEDED

2. **1,604 (PARTIAL - BASE COLUMN NAMES)**
   - **What it represents**: Unique column NAMES in BigQuery tables
   - **Example**: `agg_mean_45` appears in tables: agg_bqx_eurusd, agg_idx_eurusd
   - **After merge**: Each table's column becomes separate feature in training file
   - **Status**: CATALOGUED (base vocabulary)

3. **16,988 (CORRECT - ACTUAL FEATURES)**
   - **What it represents**: Actual merged features in training file
   - **Verified**: EURUSD training file analysis (2025-12-13)
   - **Breakdown**:
     - Pair-specific: 2,542 features
     - Cross-pair (COV/CORR/TRI): 9,064 features
     - Market-wide (MKT): 150 features
     - Currency-level (CSI): 5,232 features
     - **TOTAL**: 16,988 features
   - **Status**: VERIFIED GROUND TRUTH

---

## WHY THE MULTIPLICATION?

### Example: agg_mean_45

In BigQuery:
```
agg_bqx_eurusd.agg_mean_45
agg_idx_eurusd.agg_mean_45
```

After merge to training file:
```
agg_mean_45_bqx_eurusd  (renamed with table suffix)
agg_mean_45_idx_eurusd  (renamed with table suffix)
```

**Result**: 1 base column name → 2 features in training file

Multiply this across:
- 20 feature types (agg, mom, vol, reg, etc.)
- Multiple variants (BQX, IDX, OTHER)
- Multiple source tables per type
- Cross-pair combinations
- **TOTAL**: 16,988 unique features

---

## SCOPE BREAKDOWN (EURUSD Training File)

| Scope | Features | Percentage | Notes |
|-------|----------|------------|-------|
| Pair-Specific | 2,542 | 15.0% | Features for EURUSD only (agg, mom, vol, reg, etc.) |
| Cross-Pair | 9,064 | 53.4% | COV (pair-to-pair), CORR (ETF), TRI (triangular) |
| Market-Wide | 150 | 0.9% | MKT features (aggregated across all pairs) |
| Currency-Level | 5,232 | 30.8% | CSI features (per-currency aggregations) |
| **TOTAL** | **16,988** | **100%** | Verified from actual training file |

---

## IMPACT ASSESSMENT

### 1. Feature Ledger Mandate (CRITICAL)

**Previous Calculation**:
```
28 pairs × 7 horizons × 1,127 features = 220,892 rows
```

**CORRECTED Calculation**:
```
28 pairs × 7 horizons × 16,988 features = 3,330,928 rows
```

**Impact**: 15× increase in ledger size (3.3M rows vs 221K rows)

### 2. Documentation Updates Required

All files referencing "1,127 features":
- [x] ~~mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md~~
- [x] ~~mandate/BQX_ML_V3_FEATURE_INVENTORY.md~~
- [x] ~~mandate/README.md~~
- [ ] intelligence/feature_catalogue.json (v2.3.0)
- [ ] intelligence/roadmap_v2.json
- [ ] intelligence/context.json
- [ ] intelligence/semantics.json
- [ ] All other intelligence files

**Status**: IMMEDIATE UPDATE REQUIRED

### 3. Cost Model (NO IMPACT)

Feature selection and SHAP calculation costs are based on:
- **Selected features** (not total features)
- **Sample size** (100K+ per user mandate)
- **Compute time** (local CPU)

**Cost remains**: $0 (no cloud charges for SHAP/selection)

### 4. Storage Requirements (MINIMAL IMPACT)

**Feature Ledger Storage**:
- Rows: 3,330,928 (28 pairs × 7 horizons × 16,988)
- Columns: 17 (per mandate schema)
- Estimated size: ~500 MB (Parquet compressed)
- Cost: Negligible ($0.02/month for 500 MB in GCS)

---

## CORRECTED METRICS

### Per Pair (EURUSD Verified)

| Metric | Count |
|--------|-------|
| Total features | 16,988 |
| Pair-specific | 2,542 (15.0%) |
| Cross-pair | 9,064 (53.4%) |
| Market-wide | 150 (0.9%) |
| Currency-level | 5,232 (30.8%) |

### Per Model (28 pairs × 7 horizons × 4 ensemble = 784 models)

| Metric | Count |
|--------|-------|
| Features per model | 16,988 |
| Total feature instances | 13,317,632 (784 × 16,988) |
| Feature Ledger rows | 3,330,928 (if tracked per pair-horizon) |
| Feature Ledger rows (alt) | 13,317,632 (if tracked per model) |

### Across All Models

| Metric | Count |
|--------|-------|
| Total models | 784 |
| Total feature instances | 13,317,632 |
| Unique base column names | 1,604 |
| Actual unique features (post-merge) | 16,988 |

---

## RECOMMENDATION

1. **ACCEPT 16,988 as authoritative feature count**
   - Verified from actual training file
   - Reflects post-merge reality
   - Used for all future documentation

2. **UPDATE all documentation immediately**
   - Replace "1,127" with "16,988" throughout
   - Update Feature Ledger mandate sizing
   - Update all intelligence files

3. **CLARIFY terminology**
   - "Base column names": 1,604
   - "Unique features (training)": 16,988
   - "Feature instances (all models)": 13,317,632

4. **PRESERVE Feature Catalogue v3.0.0**
   - Contains comprehensive base column definitions
   - Still valuable as vocabulary reference
   - Add clarification note about post-merge expansion

---

## NEXT STEPS

### Immediate (Today)

1. Update Feature Ledger mandate with 16,988 count
2. Update BQX_ML_V3_FEATURE_INVENTORY.md with corrected count
3. Update README.md with corrected count
4. Update all intelligence files (5 files)

### Short-term (This Week)

1. Re-generate Feature Catalogue v3.1.0 with clarification
2. Validate GBPUSD training file has same pattern
3. Update roadmap_v2.json with corrected metrics

### Documentation

1. Add this reconciliation report to docs/
2. Reference in all mandate files
3. Update Quick Reference sections

---

## CONCLUSION

The **16,988 feature count is correct and verified**. Previous documentation citing 1,127 was based on an early estimate that did not account for post-merge feature expansion.

**Action Required**: Immediate documentation update across all mandate and intelligence files.

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: 2025-12-13
**Status**: CRITICAL - IMMEDIATE ACTION REQUIRED
