# 📋 BQX ML V3 MANDATE DOCUMENTATION

**Purpose**: This directory contains the authoritative architectural mandate documents for BQX ML V3.

**Status**: DEFINITIVE SPECIFICATIONS
**Date**: 2025-12-10 (Updated)
**Migration Status**: COMPLETE - V2 datasets active, V1 deleted

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
├── Total Tables: 4,888 in BigQuery v2 (MIGRATION COMPLETE)
├── Features per Model: 11,337 columns (1,064 unique features)
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
*Last updated: 2025-12-12*
*Total size: 58KB across 1,950+ lines*
*Status: DEFINITIVE AND AUTHORITATIVE*
