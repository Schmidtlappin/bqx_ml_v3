# 📋 BQX ML V3 MANDATE DOCUMENTATION

**Purpose**: This directory contains the authoritative architectural mandate documents for BQX ML V3.

**Status**: DEFINITIVE SPECIFICATIONS
**Date**: 2025-12-10 (Updated)
**Migration Status**: COMPLETE - V2 datasets active, V1 deleted

---

## 📚 DOCUMENTS IN THIS DIRECTORY

### 1. [BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md](BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md)
**Size**: 22KB | **Lines**: 700+

**What it confirms:**
- ✅ 28 independent currency pair models
- ✅ 7 prediction horizons per model (15, 30, 45, 60, 75, 90, 105 intervals)
- ✅ Total: 784 models (28 pairs × 7 horizons × 4 ensemble members)
- ✅ Predicting future BQX momentum values (not raw prices)

**What it rationalizes:**
- Why 28 independent models (unique dynamics per pair, no cross-contamination)
- Why BQX targets (scale-invariant, stationary, trading-relevant)
- Why 7 horizons (different trading styles, multi-horizon consensus)
- Complete mathematical and business justification

**Use this when:** You need definitive confirmation of the overall system architecture

---

### 2. [IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md](IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md)
**Size**: 16KB | **Lines**: 600+

**What it confirms:**
- ✅ ALL features are derived from IDX and BQX only
- ✅ IDX = Indexed price data (OHLCV)
- ✅ BQX = Backward-looking momentum calculation
- ✅ NO external data sources

**What it explains:**
- What IDX is and how it's used
- What BQX is and how it's calculated
- The "dual" architecture (IDX + BQX features together)
- How technical indicators are derived FROM IDX
- Why dual outperforms single-source (32% improvement)
- Complete feature derivation pipeline

**Use this when:** You need to understand where ALL features come from and the dual processing architecture

---

### 3. [BQX_ML_V3_FEATURE_INVENTORY.md](BQX_ML_V3_FEATURE_INVENTORY.md)
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
- Test ALL 8,214+ features before selection
- NO shortcuts (90%+ requires comprehensive testing)
- Select optimal 50-100 features per model

---

## 📊 QUICK REFERENCE (UPDATED 2025-12-10)

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
├── Total Tables: 4,888 in BigQuery v2 (MIGRATION COMPLETE)
├── Features per Model: 11,337 columns (1,064 unique features)
├── Target Accuracy: 85-95% called accuracy with 30-50% coverage
├── Meta-Learner: Logistic Regression with regime features
├── Cost Estimate: ~$277/month (optimized with BigQuery ML + Spot VMs)
├── Agent Coordination: CE, BA, QA, EA (see AGENT_REGISTRY.json)
└── Pipeline Status: Step 6 feature extraction IN PROGRESS
```

### Migration Status (as of 2025-12-10)
| Dataset | Status | Tables | Size |
|---------|--------|--------|------|
| Features v2 | ✅ COMPLETE | 4,888 | 1,479 GB |
| Source v2 | ✅ COMPLETE | 2,210 | 131 GB |
| Analytics v2 | ✅ COMPLETE | 54 | 68 GB |
| V1 datasets | ❌ DELETED | - | $50/mo saved |

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
*Last updated: 2025-12-10*
*Total size: 55KB across 1,800+ lines*
*Status: DEFINITIVE AND AUTHORITATIVE*
