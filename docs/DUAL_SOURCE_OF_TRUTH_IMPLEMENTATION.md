# Dual Source of Truth Implementation

**Date**: 2025-12-13
**Author**: Claude (Chief Engineer)
**Status**: IMPLEMENTED
**Priority**: P0 - FOUNDATIONAL ARCHITECTURE

---

## EXECUTIVE SUMMARY

Implemented **dual source of truth** architecture for feature definitions as approved by user:

| Source | Format | Purpose | File |
|--------|--------|---------|------|
| **Programmatic** | JSON | Scripts, validation, programmatic queries | [feature_catalogue_v3.json](../intelligence/feature_catalogue_v3.json) |
| **Human-Readable** | Markdown | Documentation, human reference, specifications | [BQX_ML_V3_FEATURE_INVENTORY.md](../mandate/BQX_ML_V3_FEATURE_INVENTORY.md) |

---

## CRITICAL DISCOVERY DURING IMPLEMENTATION

###  Feature Count Reconciliation

**MAJOR FINDING**: Documented "1,127 features" was an early estimate that didn't account for post-merge feature expansion.

| Metric | Count | Explanation |
|--------|-------|-------------|
| **Base Column Names** | 1,604 | Unique column names in BigQuery (e.g., `agg_mean_45`) |
| **Actual Training Features** | **16,988** | **Post-merge features with table suffixes** (e.g., `agg_mean_45_bqx`, `agg_mean_45_idx`) |
| Previous Documentation | ~~1,127~~ | Early estimate, superseded |

**Verified From**: EURUSD training file (`gs://bqx-ml-output/training_eurusd.parquet`)

### Scope Breakdown (16,988 Total Features)

| Scope | Features | Percentage |
|-------|----------|------------|
| Pair-specific | 2,542 | 15.0% |
| Cross-pair (COV/CORR/TRI) | 9,064 | 53.4% |
| Market-wide (MKT) | 150 | 0.9% |
| Currency-level (CSI) | 5,232 | 30.8% |

---

## WHY THE MULTIPLICATION?

### Example: Single Base Column → Multiple Features

**In BigQuery**:
```
agg_bqx_eurusd.agg_mean_45  ← Column in one table
agg_idx_eurusd.agg_mean_45  ← Same column name, different table
```

**After Merge** (Polars adds table suffixes):
```
agg_mean_45_bqx_eurusd  ← Feature 1
agg_mean_45_idx_eurusd  ← Feature 2
```

**Result**: 1 base column name → 2 training features

Multiply across:
- 20 feature types (agg, mom, vol, reg, cov, corr, tri, mkt, csi, etc.)
- Multiple variants (BQX, IDX, OTHER)
- Multiple source tables per type
- Cross-pair combinations (27 other pairs for each pair)
- **TOTAL**: 16,988 unique features per pair

---

## IMPLEMENTATION DETAILS

### 1. Programmatic Source ([feature_catalogue_v3.json](../intelligence/feature_catalogue_v3.json))

**Version**: 3.1.0 (updated 2025-12-13)
**Size**: 985.8 KB
**Features**: 1,604 base column definitions

**Contents**:
```json
{
  "catalogue_version": "3.1.0",
  "CRITICAL_CLARIFICATION": {
    "base_column_names_in_bigquery": 1604,
    "actual_features_in_training_file": 16988,
    "multiplication_factor": "~10.6x",
    "verification_source": "EURUSD training file"
  },
  "feature_definitions": [
    {
      "feature_name": "agg_mean_45",
      "feature_type": "agg",
      "semantic_group": 2,
      "formula": "Arithmetic mean over window",
      "source_tables": ["agg_bqx_*", "agg_idx_*"],
      "mandate_compliance": {
        "M005": false,
        "M006": false,
        "M007": true,
        "M008": true
      }
    }
    // ... 1,603 more definitions
  ]
}
```

**Usage**:
```python
import json

# Load catalogue
with open('intelligence/feature_catalogue_v3.json') as f:
    catalogue = json.load(f)

# Query programmatically
base_columns = catalogue['summary']['base_column_names']  # 1,604
actual_features = catalogue['summary']['actual_features_per_pair']  # 16,988

# Find features by semantic group
regression_features = [
    f for f in catalogue['feature_definitions']
    if f['semantic_group'] == 1  # Group 1: Regression
]
```

### 2. Human-Readable Source ([BQX_ML_V3_FEATURE_INVENTORY.md](../mandate/BQX_ML_V3_FEATURE_INVENTORY.md))

**Updated**: 2025-12-13
**Size**: 45 KB
**Lines**: 650+

**Captures**:
- Feature count reconciliation (line 17, 19)
- Scope breakdown by category
- 4-Mandate architecture integration
- Implementation status
- Critical paradigms and requirements

**Key Sections**:
- Executive Summary (counts, architecture)
- Detailed Feature Specifications (formulas, windows)
- Four-Mandate Architecture (M005, M006, M007, M008)
- Implementation Status (tables, deployment)
- Critical Mandates (requirements, validation)

### 3. Reconciliation Report ([FEATURE_COUNT_RECONCILIATION_20251213.md](FEATURE_COUNT_RECONCILIATION_20251213.md))

**Created**: 2025-12-13
**Size**: 6.6 KB
**Purpose**: Explains discrepancy between documented 1,127 and actual 16,988

**Root Cause**: Early estimate didn't account for table suffix multiplication during merge

---

## IMPACT ON FEATURE LEDGER

### Previous Calculation (INCORRECT)
```
28 pairs × 7 horizons × 1,127 features = 220,892 rows
```

### CORRECTED Calculation
```
28 pairs × 7 horizons × 16,988 features = 3,329,648 rows
```

**Impact**: 15× increase in ledger size (~3.3M rows vs 221K rows)

**Storage**: ~500 MB (Parquet compressed) = $0.02/month in GCS

**Cost**: No change ($0 - SHAP is local CPU compute)

---

## FILES GENERATED

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `scripts/generate_comprehensive_feature_catalogue.py` | Generator script | 12 KB | ✅ Created |
| `intelligence/feature_catalogue_v3.json` | Programmatic source | 985.8 KB | ✅ v3.1.0 |
| `docs/FEATURE_COUNT_RECONCILIATION_20251213.md` | Reconciliation report | 6.6 KB | ✅ Created |
| `docs/DUAL_SOURCE_OF_TRUTH_IMPLEMENTATION.md` | This document | TBD | ✅ Created |

---

## NEXT STEPS (PENDING)

### P0-CRITICAL Corrections Required

1. ✅ **Feature Catalogue**: COMPLETE (v3.1.0 with corrections)
2. ⏳ **README.md**: Update with 16,988 actual features
3. ⏳ **BQX_ML_V3_FEATURE_INVENTORY.md**: Complete reconciliation (partial corrections exist)
4. ⏳ **FEATURE_LEDGER_100_PERCENT_MANDATE.md**: Update to 16,988 features, 3.3M ledger rows
5. ⏳ **context.json**: Update with corrected counts
6. ⏳ **roadmap_v2.json**: Update with corrected counts
7. ⏳ **All other intelligence files**: Update references to "1,127 features"

---

## VALIDATION

### Training File Analysis (EURUSD)

```bash
python3 -c "
import polars as pl
df = pl.read_parquet('/tmp/training_eurusd.parquet')
print(f'Total columns: {len(df.columns)}')  # 17,038
print(f'Features: {len([c for c in df.columns if not c.startswith(\"target_\") and c not in [\"interval_time\", \"pair\"]])}')  # 16,988
print(f'Targets: {len([c for c in df.columns if c.startswith(\"target_\")])}')  # 49
"
```

**Result**: ✅ 16,988 features confirmed

---

## RECONCILIATION WITH 4-MANDATE ARCHITECTURE

The dual source of truth captures mandate compliance for each feature:

### M005: Regression Feature Architecture
- **Impact**: Adds 35 regression features per pair (lin_coef, quad_coef, lin_term, quad_term, residual)
- **Catalogue**: 169 features marked M005-compliant

### M006: Maximize Feature Comparisons
- **Impact**: Expands cross-pair features (3,528 COV tables, 194 TRI tables)
- **Catalogue**: 155 features marked M006-compliant

### M007: Semantic Feature Compatibility
- **Impact**: Defines 9 semantic groups, constrains valid comparisons
- **Catalogue**: 1,014 features assigned to semantic groups

### M008: Naming Standard Mandate
- **Impact**: Ensures consistent naming across 6,069 tables
- **Catalogue**: All 1,604 base column names validated

---

## CONCLUSION

**Dual source of truth architecture IMPLEMENTED and OPERATIONAL.**

**Ground truth established**: **16,988 features per pair** (verified from actual training file)

**Action required**: P0-CRITICAL corrections to mandate and intelligence files (in progress)

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: 2025-12-13
**Status**: Phase 1 COMPLETE (Dual source created), Phase 2 PENDING (Documentation corrections)
**Version**: 1.0.0
