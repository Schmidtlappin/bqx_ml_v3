# BQX ML V3 COMPREHENSIVE FEATURE INVENTORY
**Date**: 2025-12-08 (Updated)
**Status**: V2 Migration In Progress
**Source**: Documentation, Intelligence Files, Migration Scripts

---

## 📊 EXECUTIVE SUMMARY

### System Overview (UPDATED 2025-12-08)
- **Total Models**: 784 (28 pairs × 7 horizons × 4 ensemble members)
- **Currency Pairs**: 28 independent models
- **Horizons**: h15, h30, h45, h60, h75, h90, h105 (deploy farthest achieving ≥95%)
- **Algorithms**: LightGBM, XGBoost, CatBoost → Meta-learner (LSTM/LogReg)
- **Total Tables**: 4,218+ (v2 datasets, partitioned)
- **Total Features**: 6,477 per pair (verified 2025-12-09) → 399-608 selected via stability selection
  - Pair-specific: 3,813 | Cross-pair (tri): 2,088 | Market-wide (mkt): 576
- **Target Accuracy**: 95%+ directional accuracy
- **Platform**: 100% Google Cloud Platform
- **Monthly Cost**: ~$277 (optimized)

### Critical Paradigms
1. **BQX Paradigm Shift** (2024-11-24): BQX values as BOTH features AND targets
2. **Interval-Centric**: All calculations use ROWS BETWEEN (not time-based)
3. **Model Isolation**: Complete independence between 28 pair models
4. **Comprehensive Testing**: ALL features must be tested before selection

---

## 🏗️ FEATURE ARCHITECTURE: THE FEATURE MATRIX

### 3-Dimensional Feature Space
```
Feature × Centric × Variant = 8 Features × 6 Centrics × 2 Variants = 96 cell types
```

### Dimensions Explained

#### **FEATURES (8 Types)**
1. **Regression** - Polynomial trend fitting
2. **Lag** - Historical value patterns
3. **Regime** - Market state detection
4. **Aggregation** - Statistical summaries
5. **Alignment** - Cross-timeframe coherence
6. **Correlation** - Relationship measurement
7. **Momentum** - Rate of change
8. **Volatility** - Dispersion measurement

#### **CENTRICS (6 Perspectives)**
1. **Primary** (Pair-Centric) - 28 pairs
2. **Variant** (Family-Centric) - 7 currency families
3. **Covariant** (Cross-Pair) - ~50 relationships
4. **Triangulation** (Arbitrage) - 18 triangles
5. **Secondary** (Currency-Centric) - 8 currencies
6. **Tertiary** (Market-Centric) - 1 global market

#### **VARIANTS (2 Data Sources)**
1. **IDX** - Raw indexed OHLCM values
2. **BQX** - Momentum-transformed values

### Table Count Matrix

| Feature | Primary | Variant | Covariant | Triangulation | Secondary | Tertiary | **Total** |
|---------|:-------:|:-------:|:---------:|:-------------:|:---------:|:--------:|:---------:|
| | 28×2 | 7×2 | 50×2 | 18×2 | 8×2 | 1×2 | |
| Regression | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Lag | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Regime | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Aggregation | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Alignment | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Correlation | 0 | 14 | 100 | 36 | 16 | 2 | **168** |
| Momentum | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| Volatility | 56 | 14 | 100 | 36 | 16 | 2 | **224** |
| **TOTAL** | **392** | **112** | **800** | **288** | **128** | **16** | **1,736** |

---

## 📋 DETAILED FEATURE SPECIFICATIONS

### 1. PRIMARY FEATURES (Pair-Centric)

#### 1.1 Regression Features (98 fields per pair)
**Table Pattern**: `reg_{pair}` (IDX), `reg_bqx_{pair}` (BQX)
**Windows**: [45, 90, 180, 360, 720, 1440, 2880]

**Per Window**:
- Quadratic coefficient
- Linear coefficient
- Constant term
- R² score
- Residual standard deviation
- Residual min/max
- Prediction error
- Slope direction
- Curvature sign
- Trend strength
- Acceleration
- Forecast next 5 intervals
- Confidence interval bounds
- Residual distribution metrics

**Example Tables**:
- `reg_eurusd` (56 tables for 28 pairs × 2 variants)
- `reg_bqx_gbpusd`

#### 1.2 Lag Features (60+ fields per pair)
**Table Pattern**: `lag_{pair}` (IDX), `lag_bqx_{pair}` (BQX)

**Critical Paradigm Shift - BQX as Features**:
```sql
-- NEW: BQX values included as features
LAG(bqx_mid, 1) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_1,
LAG(bqx_mid, 2) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_2,
...
LAG(bqx_mid, 60) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_60
```

**Lag Periods**: [1, 2, 3, 4, 5, 10, 15, 20, 30, 45, 60]

**Per Variable**:
- Price lags (open, high, low, close)
- BQX lags (ask, bid, mid) - **NEW!**
- Volume lags
- Spread lags
- Returns lags
- Volatility lags

**Example Tables**:
- `lag_eurusd` (56 tables)
- `lag_bqx_usdjpy` - **Contains BQX features!**

#### 1.3 Regime Features (35 fields per pair)
**Table Pattern**: `regime_{pair}` (IDX), `regime_bqx_{pair}` (BQX)

**Regime Types**:
- Trending Up/Down
- Ranging
- High/Low Volatility
- Calm/Chaotic
- Breakout/Breakdown

**Per Window** [45, 90, 180, 360, 720]:
- Current regime classification
- Regime probability scores
- Regime duration
- Regime transitions count
- Regime stability index
- Regime strength
- Volatility regime indicators

**Example Tables**:
- `regime_eurusd` (56 tables)
- `regime_bqx_audusd`

#### 1.4 Aggregation Features (56 fields per pair)
**Table Pattern**: `agg_{pair}` (IDX), `agg_bqx_{pair}` (BQX)
**Windows**: [45, 90, 180, 360, 720, 1440, 2880]

**Per Window**:
- Mean, median, mode
- Standard deviation
- Min, max, range
- Percentiles (5, 25, 50, 75, 95)
- Skewness, kurtosis
- Coefficient of variation
- Autocorrelation

**Example Tables**:
- `agg_eurusd` (56 tables)
- `agg_bqx_nzdusd`

#### 1.5 Alignment Features (28 fields per pair)
**Table Pattern**: `align_{pair}` (IDX), `align_bqx_{pair}` (BQX)

**Cross-Window Alignment**:
- Multi-window agreement scores
- Trend alignment across timeframes
- Momentum coherence
- Volatility alignment
- BQX alignment metrics

**Example Tables**:
- `align_eurusd` (56 tables)
- `align_bqx_eurgbp`

#### 1.6 Momentum Features (42 fields per pair)
**Table Pattern**: `mom_{pair}` (IDX), `mom_bqx_{pair}` (BQX)
**Windows**: [45, 90, 180, 360, 720, 1440]

**Per Window**:
- Rate of change (ROC)
- Acceleration
- Momentum persistence
- Momentum reversals
- Momentum divergence
- Relative strength

**Example Tables**:
- `mom_eurusd` (56 tables)
- `mom_bqx_gbpjpy`

#### 1.7 Volatility Features (35 fields per pair)
**Table Pattern**: `vol_{pair}` (IDX), `vol_bqx_{pair}` (BQX)
**Windows**: [45, 90, 180, 360, 720]

**Per Window**:
- ATR (Average True Range)
- Realized volatility
- Volatility of volatility
- Volatility percentiles
- Volatility regimes
- Bollinger Band width
- Keltner Channel width

**Example Tables**:
- `vol_eurusd` (56 tables)
- `vol_bqx_usdcad`

---

### 2. VARIANT FEATURES (Currency Family-Centric)

**Families** (7 total):
- EUR Family: 7 pairs
- GBP Family: 6 pairs
- AUD Family: 5 pairs
- NZD Family: 4 pairs
- USD Family: 3 pairs
- CAD Family: 2 pairs
- CHF Family: 1 pair

**Table Pattern**: `var_{feature}_{currency}` (IDX), `var_{feature}_bqx_{currency}` (BQX)

**Features Per Family**:
- Family agreement score (directional consensus)
- Family dispersion (spread between strongest/weakest)
- Family momentum consensus
- Family BQX alignment
- Family volatility coherence
- Family correlation matrix
- Family leadership indicators

**Example Tables** (112 total):
- `var_reg_eur`, `var_reg_bqx_eur`
- `var_lag_gbp`, `var_lag_bqx_gbp`
- `var_regime_aud`, `var_regime_bqx_aud`

**Expected Features**: ~30 features per family × 7 families = 210 features

---

### 3. COVARIANT FEATURES (Cross-Pair Relationships)

**Relationship Types**:
- **Positive Covariants** (move together): EURUSD ↔ GBPUSD, AUDUSD ↔ NZDUSD
- **Negative Covariants** (move opposite): EURUSD ↔ USDCHF, EURUSD ↔ USDJPY

**Table Pattern**: `cov_{feature}_{pair1}_{pair2}` (IDX), `cov_{feature}_bqx_{pair1}_{pair2}` (BQX)

**Features Per Relationship** (~30 fields):
- Rolling correlation (multiple windows: 45, 90, 180, 360, 720)
- Correlation deviation from historical norm
- Correlation regime (normal, divergent, convergent)
- Cross-pair spread z-score
- Cointegration residuals
- Cointegration regime
- Lead-lag relationships
- Spread mean reversion signals
- Correlation momentum

**Example Tables** (800 total):
- `cov_reg_eurusd_gbpusd`, `cov_reg_bqx_eurusd_gbpusd`
- `cov_lag_audusd_nzdusd`, `cov_lag_bqx_audusd_nzdusd`

**Expected Features**: ~30 fields × ~50 relationships = 1,500 features

---

### 4. TRIANGULATION FEATURES (Arbitrage Relationships)

**Triangles** (18 total):
- EUR-USD-JPY: EURUSD × USDJPY = EURJPY
- EUR-USD-CHF: EURUSD × USDCHF = EURCHF
- GBP-USD-JPY: GBPUSD × USDJPY = GBPJPY
- [... 15 more triangles]

**Table Pattern**: `tri_{feature}_{curr1}_{curr2}_{curr3}` (IDX), `tri_{feature}_bqx_{curr1}_{curr2}_{curr3}` (BQX)

**Features Per Triangle** (~30 fields):
- Triangulation error (actual - synthetic)
- Error z-score
- Error mean reversion signal
- Error volatility
- Error regime (expanding/contracting)
- BQX triangulation alignment
- Arbitrage opportunity indicator
- Liquidity imbalance signals
- Market stress indicators

**Example Tables** (288 total):
- `tri_reg_eur_usd_jpy`, `tri_reg_bqx_eur_usd_jpy`
- `tri_lag_gbp_usd_chf`, `tri_lag_bqx_gbp_usd_chf`

**Expected Features**: ~30 fields × 18 triangles = 540 features

---

### 5. SECONDARY FEATURES (Currency Strength Indices)

**Currencies** (8 total):
USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD

**Table Pattern**: `csi_{feature}_{currency}` (IDX), `csi_{feature}_bqx_{currency}` (BQX)

**Features Per Currency** (~30 fields):
- Absolute strength level
- Strength momentum (rate of change)
- Strength regime (trending up/down/ranging)
- Strength percentile (relative to history)
- Strength volatility
- Strength divergence from others
- Strength leadership/laggard indicator

**Differential Features**:
- For EURUSD model: EUR strength - USD strength = fundamental fair value signal

**Example Tables** (128 total):
- `csi_reg_usd`, `csi_reg_bqx_usd`
- `csi_lag_eur`, `csi_lag_bqx_eur`
- `csd_reg_eur_usd` (differential)

**Expected Features**: ~30 fields × 8 currencies = 240 features

---

### 6. TERTIARY FEATURES (Market-Wide Global Conditions)

**Scope**: Entire FX market (1 entity)

**Table Pattern**: `mkt_{feature}` (IDX), `mkt_{feature}_bqx` (BQX)

**Feature Categories**:

#### 6.1 Session Features
- Current session (Asian, European, American)
- Session overlap indicator
- Hours until session change
- Session-specific volatility ratio
- Volume by session

#### 6.2 Volatility Regime
- Market-wide ATR (average across all pairs)
- Volatility percentile
- Volatility regime (low, normal, high, extreme)
- Cross-pair volatility dispersion
- Volatility clustering indicator

#### 6.3 Risk Sentiment
- Risk-on indicator (AUD, NZD strength; JPY, CHF weakness)
- Risk-off indicator (opposite)
- Risk sentiment score (-1 to +1)
- Risk momentum
- Safe haven flows

#### 6.4 Market Microstructure
- Average spread across pairs
- Liquidity score
- Market efficiency ratio
- Order flow imbalance
- Transaction cost index

#### 6.5 Correlation Regime
- Market-wide correlation level
- Correlation clustering
- Correlation regime changes
- Diversification opportunity index

**Example Tables** (16 total):
- `mkt_vol`, `mkt_vol_bqx`
- `mkt_regime`, `mkt_regime_bqx`
- `mkt_sentiment`, `mkt_sentiment_bqx`

**Expected Features**: ~20 fields × 8 feature types = 160 features

---

## 🎯 FEATURE COUNT SUMMARY PER MODEL

### Expected Features Per Pair Model

| Feature Source | Tables | Fields/Table | Est. Features |
|----------------|--------|--------------|---------------|
| **Primary** | 14 | ~50 | **700** |
| **Variant** | 16 | ~30 | **480** |
| **Covariant** | ~20 | ~30 | **600** |
| **Triangulation** | ~10 | ~30 | **300** |
| **Secondary** | 12 | ~30 | **360** |
| **Tertiary** | 16 | ~20 | **320** |
| **TOTAL** | ~88 | - | **~2,760** |

### Comprehensive Feature Generation (For 90%+ Accuracy)

Per the **Feature Selection Requirements Analysis**, to achieve 90%+ directional accuracy, we must generate and test ALL possible features:

#### BQX Features (Per Pair):
- Base values: 7 windows × [ask, bid, mid] = 21 values
- All lags: 21 × 11 lag periods = 231 features
- All MAs: 21 × 6 moving averages = 126 features
- All stats: 21 × 8 statistics = 168 features
- Differences: 21 × 3 = 63 features
- Ratios: 21 × 2 = 42 features
- Rate of change: 21 × 3 = 63 features
**Subtotal: ~714 BQX features**

#### IDX Features (Per Pair):
- 50+ indicators × 7 timeframes × 5 lags × 4 transforms = **7,000 IDX features**

#### Interaction Features:
- Products, ratios, differences between key features = **~500 interaction features**

**TOTAL PER PAIR: 6,477 features (verified 2025-12-09)**
- Pair-specific: 3,813 | Cross-pair (tri): 2,088 | Market-wide (mkt): 576

#### After Feature Selection:
- Test all 6,477 features via Robust Group-First Stability Selection
- Select optimal 399-608 features per model
- Achieve target 95%+ called signal accuracy
- Note: Original 8,214 was an estimate; corrected to 6,477 (3,813 pair + 2,088 tri + 576 mkt)

---

## 🔧 IMPLEMENTATION STATUS

### Current State (as of 2025-12-08)
- **V2 Migration**: IN PROGRESS (~62% complete)
- **Features v2**: ~2,609 / 4,218 tables (62%)
- **Source v2**: 2,209 / 2,200 tables (100% complete)
- **Covariance**: 1,299 / 2,352 tables (55%)
- **Regime**: 354 tables (100%+ complete)
- **Partitioning**: ALL v2 tables partitioned by DATE(interval_time)
- **Clustering**: ALL v2 tables clustered by pair

### V2 Dataset Names
| V1 (Deprecated) | V2 (Current) | Status |
|-----------------|--------------|--------|
| bqx_ml_v3_features | bqx_ml_v3_features_v2 | 62% migrated |
| bqx_bq_uscen1 | bqx_bq_uscen1_v2 | 100% migrated |

### Multi-Horizon Architecture (UPDATED QA 2025-12-09)
| Component | Count | Details |
|-----------|-------|---------|
| Pairs | 28 | All forex pairs |
| Horizons | 7 | h15, h30, h45, h60, h75, h90, h105 |
| Ensemble | 4 | LightGBM, XGBoost, CatBoost, Meta-learner |
| **Total Models** | **784** | 28 × 7 × 4 |

### Required State (95%+ Accuracy Mandate)
- **BigQuery Tables**: 4,888+ tables in v2 datasets
- **Features Generated**: All 6,477 per pair (verified 2025-12-09)
- **Features Selected**: Top 399-608 per model (via stability selection)
- **Models Trained**: 784 (28 pairs × 7 horizons × 4 ensemble)
- **Directional Accuracy**: 95%+ (deploy farthest horizon achieving this)
- **Cost**: ~$277/month (optimized)

---

## 📊 PLANNED PHASES (11 Phases Total)

### Phase Summary

| Phase | Focus | Duration | Tables | Features |
|-------|-------|----------|--------|----------|
| MP03.01 | Work Environment Setup | 2 days | 0 | 0 |
| MP03.02 | Intelligence Architecture | 4 days | 0 | 0 |
| MP03.03 | Planning & Architecture | 3 days | 0 | 0 |
| MP03.04 | Infrastructure Setup | 3 days | 0 | 0 |
| MP03.05 | Data Pipeline & Validation | 9 days | 28 | 0 |
| MP03.06 | Primary Feature Engineering | 10 days | 392 | ~700/pair |
| MP03.07 | Advanced Feature Engineering | 12 days | 1,344 | ~2,060/pair |
| MP03.08 | Model Development & Testing | 16 days | 0 | Test all |
| MP03.09 | Deployment & Monitoring | 8 days | 0 | 0 |
| MP03.10 | Validation & DR | 7 days | 0 | 0 |
| MP03.11 | Security Hardening | 3 days | 0 | 0 |
| **TOTAL** | **Complete System** | **75 days** | **1,736** | **6,477** |

---

## 🎯 CRITICAL SUCCESS METRICS

### Technical Targets
- ✅ **Directional Accuracy**: 90%+ (MANDATORY)
- ✅ **R² Score**: > 0.75
- ✅ **Sharpe Ratio**: > 1.5
- ✅ **Max Drawdown**: < 10%
- ✅ **Win Rate**: > 55%
- ✅ **Inference Latency**: < 100ms
- ✅ **Query Performance**: < 2 seconds

### Process Requirements
- ✅ **Feature Testing**: 100% (all 6,477 features)
- ✅ **Feature Selection**: Data-driven (6 methods)
- ✅ **Model Isolation**: Complete (no cross-contamination)
- ✅ **BQX Paradigm**: Implemented (BQX as features AND targets)
- ✅ **Interval-Centric**: Enforced (ROWS BETWEEN only)

---

## 🚨 CRITICAL MANDATES

### Non-Negotiable Requirements

1. **90%+ Directional Accuracy**
   - Current: 82.52% called accuracy (pilot, τ=0.70)
   - Required: 95%+ called accuracy (NO EXCEPTIONS)
   - Path: Test ALL 6,477 features, select optimal subset via stability selection

2. **Comprehensive Feature Testing**
   - Test: 100% of features (NO shortcuts)
   - Methods: 6 selection techniques (variance, F-stat, MI, RF importance, RFE, L1)
   - Per-Model: Unique optimal feature set for each of 28 models

3. **BQX Paradigm Shift**
   - BQX values MUST be included as features (lags 1-60)
   - BQX values remain as targets (leads 1-N)
   - Enables autoregressive momentum prediction

4. **Interval-Centric Architecture**
   - ALL calculations: ROWS BETWEEN N PRECEDING
   - FORBIDDEN: Any time-based windows (INTERVAL, RANGE)
   - Ensures consistent sample sizes regardless of gaps

5. **Model Independence**
   - 28 completely isolated models
   - NO feature sharing between pairs
   - Each pair's unique dynamics captured

---

## 📁 FILE REFERENCES

### Key Documentation Files
- [BQX_ML_FEATURE_MATRIX.md](BQX_ML_FEATURE_MATRIX.md) - Complete feature matrix specification
- [BQX_ML_V3_PIPELINE.md](BQX_ML_V3_PIPELINE.md) - Pipeline architecture
- [FEATURE_SELECTION_REQUIREMENTS_ANALYSIS.md](FEATURE_SELECTION_REQUIREMENTS_ANALYSIS.md) - 90%+ accuracy mandate
- [BQX_ML_V3_FINAL_PHASE_PLAN.md](BQX_ML_V3_FINAL_PHASE_PLAN.md) - 11-phase implementation plan
- [BQX_ML_V3_CLEAN_ARCHITECTURE.md](BQX_ML_V3_CLEAN_ARCHITECTURE.md) - Clean architecture guide

### Intelligence Files
- `intelligence/semantics.json` - Terminology and concepts
- `intelligence/ontology.json` - Entity relationships
- `intelligence/mandates.json` - Critical requirements
- `intelligence/context.json` - Project context
- `intelligence/workflows.json` - Process workflows

### Scripts (151 Python files)
- Feature generation scripts
- Model training scripts
- Deployment scripts
- Testing and validation scripts

---

## ✅ CONCLUSION

BQX ML V3 is designed as a comprehensive, production-grade machine learning system with:

1. **4,888 BigQuery tables** (verified 2025-12-09) across feature types
2. **6,477 features per pair** for comprehensive market coverage (verified from BQ)
3. **784 models** (28 pairs × 7 horizons × 4 ensemble members)
4. **95%+ called signal accuracy target** with 30-50% coverage
5. **100% GCP infrastructure** for scalability and reliability

**Critical Path**: Generate ALL features → Test ALL features → Select optimal subset → Achieve 95%+ called accuracy

**NO EXCEPTIONS. NO SHORTCUTS. NO EXCUSES.**

---

## 📊 AUDIT NOTE (2025-12-09)

The original "8,214+ features" was an estimate. Actual BQ audit shows:
- **6,477 features per pair** (EURUSD verified)
  - Pair-specific: 3,813
  - Cross-pair (tri): 2,088
  - Market-wide (mkt): 576
- **86,190 total feature columns** across all tables
- **4,888 total tables** in bqx_ml_v3_features_v2

See `/intelligence/feature_catalogue.json` for complete inventory.

---

*This inventory documents all planned features for BQX ML V3 as of 2025-11-27. All features must be implemented, tested, and validated before production deployment.*
