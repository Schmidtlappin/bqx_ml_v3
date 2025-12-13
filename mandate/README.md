# 📋 BQX ML V3 MANDATE DOCUMENTATION

**Purpose**: This directory contains the authoritative architectural mandate documents for BQX ML V3.

**Status**: DEFINITIVE SPECIFICATIONS
**Date**: 2025-12-13 (Updated - Post-Audit Reconciliation)
**Migration Status**: COMPLETE - V2 datasets active, V1 deleted
**Audit Status**: 3-Mandate Architecture Reconciliation Complete

---

## 📚 DOCUMENTS IN THIS DIRECTORY

### 1. [AGENT_ONBOARDING_PROTOCOL.md](AGENT_ONBOARDING_PROTOCOL.md) (NEW)
**Size**: 12KB | **Lines**: 350+

**What it mandates:**
- Standardized onboarding prompt format for all agents (CE, BA, QA, EA)
- Session continuity requirements
- Registry update procedures
- First-action sequences

**What it defines:**
- Agent definitions and roles
- Communication protocol
- Key file references
- Error recovery procedures

**Use this when:** Onboarding a new agent session or recovering from session corruption

---

### 2. [BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md](BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md)
**Size**: 22KB | **Lines**: 700+

**What it confirms:**
- 28 independent currency pair models
- 7 prediction horizons per model (15, 30, 45, 60, 75, 90, 105 intervals)
- Total: 588 models (28 pairs × 7 horizons × 3 ensemble members)
- Predicting future BQX momentum values (not raw prices)

**What it rationalizes:**
- Why 28 independent models (unique dynamics per pair, no cross-contamination)
- Why BQX targets (scale-invariant, stationary, trading-relevant)
- Why 7 horizons (different trading styles, multi-horizon consensus)
- Complete mathematical and business justification

**Use this when:** You need definitive confirmation of the overall system architecture

---

### 3. [IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md](IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md)
**Size**: 16KB | **Lines**: 600+

**What it confirms:**
- ALL features are derived from IDX and BQX only
- IDX = Indexed price data (OHLCV)
- BQX = Backward-looking momentum calculation
- NO external data sources

**What it explains:**
- What IDX is and how it's used
- What BQX is and how it's calculated
- The "dual" architecture (IDX + BQX features together)
- How technical indicators are derived FROM IDX
- Why dual outperforms single-source (32% improvement)
- Complete feature derivation pipeline

**Use this when:** You need to understand where ALL features come from and the dual processing architecture

---

### 4. [BQX_ML_V3_FEATURE_INVENTORY.md](BQX_ML_V3_FEATURE_INVENTORY.md)
**Size**: 17KB | **Lines**: 500+

**What it inventories:**
- ✅ 1,736 planned BigQuery tables
- ✅ 8,214+ features per pair (before selection)
- ✅ Feature matrix: 8 types × 6 centrics × 2 variants = 96 cell types
- ✅ 11-phase implementation plan (75 days)

**What it specifies:**
- Complete 3D feature matrix architecture
- All 8 feature types (regression, lag, regime, aggregation, alignment, correlation, momentum, volatility)
- All 6 centric perspectives (primary, variant, covariant, triangulation, secondary, tertiary)
- Expected features per model and across all pairs
- The 90%+ accuracy mandate (requires testing ALL features)

**Use this when:** You need to know what features exist, how many tables, and the implementation roadmap

---

### 5. [REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md](REGRESSION_FEATURE_ARCHITECTURE_MANDATE.md) ⚠️ CRITICAL
**Size**: 45KB | **Lines**: 750+
**Mandate ID**: **BQX-ML-M005** | **Priority**: P0-CRITICAL

**What it mandates:**
- ✅ REG tables must have lin_coef, quad_coef, constant, lin_term, quad_term, residual per window
- ✅ TRI tables MUST INCLUDE regression features from all 3 triangle legs (+63 columns)
- ✅ COV tables MUST INCLUDE regression features from both pairs (+42 columns)
- ✅ VAR tables MUST INCLUDE aggregated regression features (+21 columns)
- ⚠️ CRITICAL: Current Tier 1 scripts are NON-COMPLIANT (missing regression features)

**What it defines:**
- Multi-level feature hierarchy (Raw State → Relationship Metrics → Regression Features)
- Polynomial regression formula: `y = quad_coef × x² + lin_coef × x + constant`
- Residual calculation: `residual = y - (quad_term + lin_term + constant)`
- Complete SQL templates for TRI/COV/VAR with regression JOINs

**Impact on Tier 1:**
- TRI: 15 → 78 columns (+63 regression features)
- COV: 14 → 56 columns (+42 regression features)
- VAR: 14 → 35 columns (+21 regression features)
- Cost: +$50-60 (additional JOINs), Timeline: +14-19 hours (refactoring + testing)

**Related Mandates:**
- FEATURE_LEDGER_100_PERCENT_MANDATE.md (ledger row count updates)
- BQX_ML_V3_FEATURE_INVENTORY.md (feature count implications)

**Use this when:** Generating or refactoring TRI/COV/VAR tables - MUST be compliant before Tier 1 launch

---

### 6. [MAXIMIZE_FEATURE_COMPARISONS_MANDATE.md](MAXIMIZE_FEATURE_COMPARISONS_MANDATE.md) ⚠️ CRITICAL
**Size**: 45KB | **Lines**: 783
**Mandate ID**: **BQX-ML-M006** | **Priority**: P0-CRITICAL

**What it mandates:**
- ✅ Maximize comparisons across ALL pairs, windows, and feature types
- ✅ Perfect variant separation (BQX and IDX never intermix)
- ✅ Multi-level feature hierarchy (pair → pair-to-pair → triangle → currency family)
- ✅ 5-phase implementation plan for complete comparison coverage

**What it defines:**
- COV tables schema evolution (14 → 56+ columns with regression features)
- TRI tables schema evolution (15 → 78+ columns with regression features)
- VAR tables schema evolution (129 → 150+ columns with regression features)
- Complete SQL templates for Phase 1-5 implementations

**Impact on Implementation:**
- COV: Add 42 regression feature columns (pair1 + pair2 × 21 features)
- TRI: Add 63 regression feature columns (3 pairs × 21 features)
- VAR: Add 21 aggregated regression feature columns
- Timeline: Phase 1 (18-24 hours), Phases 2-5 (deferred)

**Use this when:** Planning or implementing COV/TRI/VAR table generation with regression features

---

### 7. [SEMANTIC_FEATURE_COMPATIBILITY_MANDATE.md](SEMANTIC_FEATURE_COMPATIBILITY_MANDATE.md) ⚠️ CRITICAL
**Size**: 30KB | **Lines**: 554
**Mandate ID**: **BQX-ML-M007** | **Priority**: P0-CRITICAL

**What it mandates:**
- ✅ Define 9 semantic compatibility groups for valid feature comparisons
- ✅ Prohibit invalid cross-group comparisons (e.g., close_idx vs bqx_45)
- ✅ Establish 266 comparable features per pair across semantic groups
- ✅ Enforce semantic validation in all comparison table generation

**What it defines:**
- Group 1: Regression Features (35 features: lin_term, quad_term, residual)
- Group 2: Statistical Aggregates (63 features: mean, std, min, max, range)
- Group 3: Normalized Metrics (28 features: zscore, position, cv, deviation)
- Group 4: Directional Indicators (21 features: dir, direction, slope)
- Group 5: Momentum Oscillators (14 features: bqx, mom)
- Group 6: Volatility Measures (21 features: atr, volatility, vol_ratio)
- Group 7-9: Derivatives, Mean Reversion, Correlations

**Prohibited Comparisons:**
- ❌ Raw prices (close_idx, open, high, low) - different scales
- ❌ Categorical features (regime, session, pair) - non-numerical
- ❌ Cross-group comparisons (regression vs aggregation)

**Use this when:** Designing feature comparison logic or validating comparison table schemas

---

### 8. [FEATURE_LEDGER_100_PERCENT_MANDATE.md](FEATURE_LEDGER_100_PERCENT_MANDATE.md)
**Size**: 15KB | **Lines**: 400+
**Mandate ID**: BQX-ML-M001 | **Priority**: P0-CRITICAL

**What it mandates:**
- 100% of all features must be in feature ledger (6,477 features per pair)
- Every RETAINED feature must have SHAP values (100,000+ samples minimum)
- Complete traceability from selection to deployment

**Updated Requirements (Post REG Mandate)**:
- Expected features per pair: 6,477 → 6,540 (+63 from TRI/COV regression features)
- Total ledger rows: 1,269,492 → 1,282,044 (+12,552 rows)
- Calculation: 28 pairs × 7 horizons × 6,540 features

**Use this when:** Planning feature selection or validating feature ledger completeness

---

## 🎯 WHY THESE ARE "MANDATE" DOCUMENTS

These documents represent **NON-NEGOTIABLE architectural decisions** that:

1. **Define the system structure** (28 models × 7 horizons)
2. **Establish data sources** (IDX and BQX only)
3. **Specify feature requirements** (1,736 tables, 8,214+ features)
4. **Set performance targets** (90%+ directional accuracy)
5. **Rationalize design decisions** (why not alternatives)

---

## 🔒 CRITICAL PRINCIPLES

### Independence
- 28 completely isolated currency pair models
- NO cross-contamination between pairs
- Each pair's unique dynamics captured

### Dual Architecture
- IDX (position) + BQX (momentum) together
- Complementary information sources
- 32% performance improvement over single-source

### Multi-Horizon
- 7 prediction horizons per pair
- Serves scalpers, day traders, swing traders
- Consensus signals from multiple horizons

### Comprehensive Features
- Test ALL features before selection (1,127 unique features)
- NO shortcuts (90%+ requires comprehensive testing)
- Select optimal 50-100 features per model

---

## 🏛️ THREE-MANDATE ARCHITECTURE (2025-12-13)

The BQX ML V3 system is governed by **three interrelated architectural mandates** that work together to create mathematically sound, maximally informative features:

### Core Mandate Chain

```
┌──────────────────────────────────────────────────────────┐
│ M005: REGRESSION FEATURE ARCHITECTURE                   │
│ "WHAT features to add"                                  │
├──────────────────────────────────────────────────────────┤
│ • Add coefficient columns to REG tables (lin_coef,     │
│   quad_coef, lin_term, quad_term, residual)            │
│ • Propagate regression features to comparison tables    │
│ • REG: 234→248 cols, COV: 14→56 cols, TRI: 15→78 cols │
└────────────┬─────────────────────────────────────────────┘
             │ PROVIDES
             │ 35 regression features per pair
             ▼
┌──────────────────────────────────────────────────────────┐
│ M006: MAXIMIZE FEATURE COMPARISONS                      │
│ "HOW MUCH to compare"                                   │
├──────────────────────────────────────────────────────────┤
│ • Compare across ALL pairs (378 COV combinations)       │
│ • Compare across ALL windows (7 temporal scales)        │
│ • Compare across ALL feature types (5-7 variants)       │
│ • Perfect variant separation (BQX ≠ IDX)                │
└────────────┬─────────────────────────────────────────────┘
             │ MAXIMIZES
             │ Feature interaction coverage
             │ CONSTRAINED BY
             ▼
┌──────────────────────────────────────────────────────────┐
│ M007: SEMANTIC FEATURE COMPATIBILITY                    │
│ "WHICH comparisons are valid"                           │
├──────────────────────────────────────────────────────────┤
│ • Define 9 semantic compatibility groups                │
│ • Only allow comparisons WITHIN groups                  │
│ • Prohibit invalid comparisons (close_idx vs bqx_45)   │
│ • 266 comparable features per pair                      │
└──────────────────────────────────────────────────────────┘
```

### Mandate Interaction Summary

| Mandate | Scope | Status | Impact |
|---------|-------|--------|--------|
| **M005** | REG, COV, TRI, VAR schemas | Phase 0C: 17% (14/84 REG tables) | +133 cols/REG, +42 cols/COV, +63 cols/TRI |
| **M006** | Comparison table generation | Phase 3: 71% (undocumented) | COV 2,507→3,528 tables (+41%) |
| **M007** | Feature comparison validation | 100% (semantic groups defined) | 266 comparable features/pair (9 groups) |

### Implementation Dependencies

1. **M005 Gates M006**: Cannot maximize comparisons until regression features exist
2. **M007 Constrains M006**: Can only maximize *valid* comparisons within semantic groups
3. **All Three Enable M001**: Feature ledger requires complete feature universe (M005), maximum coverage (M006), and valid comparisons (M007)

### Current Compliance Status

- ✅ **M007**: Fully compliant (semantic groups defined, documented in catalogue v2.3.0)
- ⏳ **M005**: 17% compliant (Phase 0C regenerating REG tables: 14/84 complete)
- ⚠️ **M006**: Partially compliant (Phase 3 exists but undocumented)

---

## 📊 QUICK REFERENCE (UPDATED 2025-12-12)

```
BQX ML V3 Architecture:
├── Models: 28 independent currency pair systems
├── Horizons: 7 per system (h15, h30, h45, h60, h75, h90, h105)
├── Total Models: 588 (28 pairs × 7 horizons × 3 ensemble members)
├── Ensemble: LightGBM + XGBoost + CatBoost (ElasticNet removed 2025-12-09)
├── Data Sources: IDX (price) + BQX (momentum) ONLY
├── Datasets: bqx_ml_v3_features_v2, bqx_bq_uscen1_v2 (partitioned)
├── Feature Types: 8 (regression, lag, regime, agg, align, corr, mom, vol)
├── Feature Perspectives: 6 (primary, variant, covariant, tri, secondary, tertiary)
├── Total Tables: 6,069 in BigQuery v2 (MIGRATION COMPLETE, AUDITED 2025-12-13)
├── Features per Model: 11,337 total columns (1,127 unique features)
├── Target Accuracy: 85-95% called accuracy with 30-50% coverage
├── Meta-Learner: Logistic Regression with regime features
├── Deployment: Cloud Run serverless with Polars merge (user-mandated)
├── Pipeline Status: OPERATIONAL (2/28 complete, 1 testing, 25 pending)
├── Cost Estimate: $19.90 one-time + $1.03/month (Cloud Run + GCS storage)
├── Agent Coordination: CE, BA, QA, EA (see AGENT_REGISTRY.json)
└── Deployment Job: bqx-ml-pipeline (Cloud Run, us-central1)
```

## 🚀 DEPLOYMENT ARCHITECTURE (NEW - 2025-12-12)

### Cloud Run Serverless Pipeline

**Status**: OPERATIONAL
**Job**: `bqx-ml-pipeline`
**Image**: `gcr.io/bqx-ml/bqx-ml-polars-pipeline:latest`
**Region**: us-central1

**Resources**:
- CPUs: 4 cores
- Memory: 12 GB
- Timeout: 2 hours (7200s)

**Pipeline Stages** (5-stage execution):
1. **BigQuery Extraction** (60-70 min)
   - Script: `parallel_feature_testing.py`
   - Workers: 25 parallel
   - Output: 668 Parquet checkpoint files per pair
2. **Polars Merge** (13-20 min)
   - Script: `merge_with_polars_safe.py`
   - Memory monitoring: Soft (no hard limits, Polars manages efficiently)
   - Output: Single training file (~9 GB, ~177K rows, ~17K columns)
3. **Validation** (1-2 min)
   - Script: `validate_training_file.py`
   - Checks: Dimensions, targets, features, nulls
4. **GCS Backup** (2-3 min)
   - Destination: `gs://bqx-ml-output/`
5. **Cleanup** (1 min)
   - Actions: Remove checkpoints, remove local training file

**Cost**: $0.71 per pair (Cloud Run compute)
**Total**: $19.90 (28 pairs) + $1.03/month (GCS storage)

**Completed Pairs**: EURUSD (local Polars, validated QA-0120), AUDUSD (local Polars, 13 min)
**In Progress**: GBPUSD (Cloud Run test)
**Pending**: 25 pairs (Cloud Run production run after GBPUSD success)

**User Mandate**: Polars merge protocol mandated for maximum speed (4.6× faster than BigQuery alternative)
```

### Migration Status (as of 2025-12-13 - POST-AUDIT)
| Dataset | Status | Tables | Size |
|---------|--------|--------|------|
| Features v2 | ✅ COMPLETE | 6,069 | 1,479 GB |
| Source v2 | ✅ COMPLETE | 2,210 | 131 GB |
| Analytics v2 | ✅ COMPLETE | 54 | 68 GB |
| V1 datasets | ❌ DELETED | - | $50/mo saved |

**Table Breakdown (Features v2):**
- COV tables: 3,528 (pair-to-pair comparisons, 7 feature type variants)
- CORR tables: 896 (correlation matrices: 448 ETF, 224 BQX, 224 IBKR)
- TRI tables: 194 (triangular arbitrage, 5 feature type variants)
- REG tables: 84 (polynomial regression, Phase 0C: 17% complete)
- Base tables: 588 (agg, align, mom, vol, lag, regime, der, rev, etc.)
- Other families: 779 (csi, div, cyc, ext, mrt, tmp, mkt, var)

**V2 Catalog**: See `/intelligence/bigquery_v2_catalog.json` for full details
**Agent Registry**: See `/.claude/sandbox/communications/AGENT_REGISTRY.json`

---

## 🚀 WHEN TO READ THESE

**Starting the project?**
→ Read [BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md](BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md) first

**Confused about features?**
→ Read [IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md](IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md)

**Planning implementation?**
→ Read [BQX_ML_V3_FEATURE_INVENTORY.md](BQX_ML_V3_FEATURE_INVENTORY.md)

**Making architectural decisions?**
→ Read ALL THREE - they represent non-negotiable mandates

---

## ⚠️ IMPORTANT NOTES

### These documents are AUTHORITATIVE

- Supersede conflicting information in other docs
- Represent final architectural decisions
- Must be consulted before major changes

### Updates require justification

- Cannot change architecture without strong rationale
- Performance data must support alternatives
- User approval required for deviations

### Implementation must align

- Scripts must follow these specifications
- Tables must match the inventory
- Models must use the dual architecture

---

## 📅 DOCUMENT HISTORY

- **2025-12-13**: Three-mandate architecture reconciliation and audit
  - Comprehensive mandate directory audit (16 files analyzed)
  - Table count corrections: 4,888 → 6,069 (+24% discovered through BigQuery audit)
  - Feature count update: 1,064 → 1,127 unique features (+63)
  - Added M005, M006, M007 mandate documentation sections
  - Added CORR family breakdown (896 tables: 448 ETF, 224 BQX, 224 IBKR)
  - Added COV table breakdown (3,528 tables, 7 feature type variants)
  - Created mandate reconciliation report (/tmp/mandate_audit_reconciliation_20251213.md)
  - Status: 3/16 files fully compliant, 8/16 require updates
- **2025-12-12**: Cloud Run deployment operational
  - Cloud Run serverless pipeline DEPLOYED (bqx-ml-pipeline)
  - Polars merge protocol (user-mandated for maximum speed)
  - 5-stage pipeline: Extract → Merge → Validate → Backup → Cleanup
  - Cost: $19.90 one-time + $1.03/month (vs $277/month VM estimate)
  - EURUSD, AUDUSD complete (2/28), GBPUSD testing, 25 pending
  - Deployment job: 4 CPUs, 12 GB memory, 2-hour timeout
- **2025-12-10**: Agent coordination and V2 completion update
  - V2 migration COMPLETE (4,888 feature tables, 1,479 GB)
  - V1 datasets DELETED ($50/month savings realized)
  - ElasticNet removed from ensemble (588 models, not 784)
  - Multi-agent coordination: CE, BA, QA, EA (see AGENT_REGISTRY.json)
  - Step 6 feature extraction in progress (28 pairs × 11,337 columns)
  - Session continuity protocol established for all agents
- **2025-12-08**: Major architecture update
  - Migration to v2 datasets (partitioned by DATE(interval_time), clustered by pair)
  - Updated to 7 horizons (h15-h105), 784 total models
  - 95%+ accuracy target with multi-horizon prediction strategy
  - Cost optimization: ~$277/month (BigQuery ML + Spot VMs)
  - Post-migration plan: gentle-skipping-wirth.md
- **2025-11-27**: All three documents created and moved to mandate directory
  - Architecture confirmation (22KB)
  - Dual feature deep dive (16KB)
  - Feature inventory (17KB)

---

**These are the laws of BQX ML V3. Follow them.**

---

*Mandate documentation established: 2025-11-27*
*Last updated: 2025-12-13 (Post-Audit Reconciliation)*
*Total size: 75KB across 2,100+ lines*
*Status: DEFINITIVE AND AUTHORITATIVE*
*Audit Status: 3-Mandate Architecture Compliance Verified*
