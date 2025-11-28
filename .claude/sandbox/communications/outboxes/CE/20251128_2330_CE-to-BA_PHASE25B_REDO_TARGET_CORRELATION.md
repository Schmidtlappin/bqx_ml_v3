# CE Directive: Phase 2.5B REDO - Target-Based Feature Correlation
**Timestamp:** 2025-11-28T23:30:00Z
**From:** Chief Engineer (CE)
**To:** Build Agent (BA)
**Priority:** CRITICAL
**Type:** PHASE 2.5B REDO - CORRECTED METHODOLOGY

---

## ISSUE WITH PREVIOUS PHASE 2.5B

Your Phase 2.5B correlation analysis **correlated features WITH EACH OTHER** (redundancy detection).

This is NOT what is needed for feature selection.

**REQUIRED:** Correlate features against **PREDICTION TARGETS** (future BQX values).

---

## RATIONALE: WHY TARGET-BASED CORRELATION?

### The Goal
We are building 196 prediction models (28 pairs × 7 horizons). Each model predicts FUTURE bqx_* values. To select the best features for each model, we need to know which features are most correlated with the prediction target.

### Feature-Feature vs Feature-Target Correlation

| Approach | What It Measures | Use Case |
|----------|------------------|----------|
| Feature-Feature (WRONG) | Redundancy between features | Dimensionality reduction |
| **Feature-Target (CORRECT)** | Predictive power of each feature | **Feature selection for ML models** |

### Example
- Feature-Feature: "reg_mean_45 and agg_mean_45 are 0.95 correlated" → They're redundant
- **Feature-Target**: "reg_slope_45 has 0.42 correlation with target_bqx45_h15" → **This feature predicts the target**

We need the SECOND type to select which features to include in our prediction models.

### Data Leakage Prevention
- **Features**: Current interval values (LAG perspective - what we KNOW now)
- **Targets**: LEAD values (what we're trying to PREDICT in the future)
- This ensures no future information leaks into training features

---

## CORRECTED SCOPE

### Target Combinations: 1,372 Total
- 28 pairs × 7 BQX components × 7 horizons = 1,372 targets

### BQX Components (What We Predict)
These are the 7 BQX momentum values calculated at different lookback windows:
```
[bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880]
```
Each represents momentum calculated over a different historical window.

### Prediction Horizons (How Far Ahead We Predict)
```
[15, 30, 45, 60, 75, 90, 105] intervals FORWARD
```
| Horizon | Intervals Forward | Meaning |
|---------|-------------------|---------|
| H15 | 15 intervals | Predict bqx value 15 intervals into future |
| H30 | 30 intervals | Predict bqx value 30 intervals into future |
| H45 | 45 intervals | Predict bqx value 45 intervals into future |
| H60 | 60 intervals | Predict bqx value 60 intervals into future |
| H75 | 75 intervals | Predict bqx value 75 intervals into future |
| H90 | 90 intervals | Predict bqx value 90 intervals into future |
| H105 | 105 intervals | Predict bqx value 105 intervals into future |

**INTERVAL-CENTRIC**: Do NOT reference time (minutes/hours). Always use interval counts.
**NOT the BQX lookback windows** - those are for calculating bqx_* values, NOT prediction horizons.

### Target Definition
```sql
-- For each pair, each BQX component, each horizon:
target = LEAD(bqx_X, H) OVER (PARTITION BY pair ORDER BY interval_time)

-- Example: LEAD(bqx_45, 15) = bqx_45 value 15 intervals into the FUTURE
-- At interval 100, this gives us the bqx_45 value from interval 115
```

---

## EXECUTION PLAN

### Phase 1: EURUSD Pilot (49 targets)
Execute on EURUSD first to validate methodology before scaling.

- 7 BQX components × 7 horizons = 49 target combinations
- Correlate ALL features from ALL 6 centrics (BOTH IDX and BQX variants)
- Validate results before proceeding

**Success Criteria for Pilot:**
- 49 correlation tables created
- Each table contains correlations for all features from all 6 centrics
- Features are ranked by absolute correlation
- No NULL or invalid correlation values
- Summary report generated

### Phase 2: Scale to All 28 Pairs
After EURUSD validation, scale to remaining 27 pairs.

---

## FEATURE ARCHITECTURE

### 2 Variants (BOTH must be correlated)
| Variant | Suffix | Description | Source Data |
|---------|--------|-------------|-------------|
| IDX | (none) | Price-based features | Derived from idx_* price data |
| BQX | _bqx_ | Momentum-based features | Derived from bqx_* momentum data |

**CRITICAL**: Correlate features from BOTH IDX and BQX tables for each feature type.

**Rationale**: IDX features capture price dynamics while BQX features capture momentum dynamics. Both may have predictive power for different targets. We don't know a priori which will be more predictive, so we test BOTH.

### 8 Feature Types (ALL must be correlated)
| Type | Prefix | IDX Example | BQX Example | Description |
|------|--------|-------------|-------------|-------------|
| Regression | reg_ | reg_eurusd | reg_bqx_eurusd | Statistical regression features (mean, std, slope, etc.) |
| Lag | lag_ | lag_eurusd | lag_bqx_eurusd | Historical lagged values at multiple intervals |
| Regime | regime_ | regime_eurusd | regime_bqx_eurusd | Market regime classifications (trend, volatility) |
| Aggregation | agg_ | agg_eurusd | agg_bqx_eurusd | Aggregated statistics over windows |
| Alignment | align_ | align_eurusd | align_bqx_eurusd | Cross-timeframe alignment signals |
| Correlation | corr_ | corr_eurusd | corr_bqx_eurusd | Inter-feature correlation patterns |
| Momentum | mom_ | mom_eurusd | mom_bqx_eurusd | Momentum and rate-of-change indicators |
| Volatility | vol_ | vol_eurusd | vol_bqx_eurusd | Volatility measures and bands |

### 6 Centrics (ALL must be included for each pair)
| Centric | IDX Tables | BQX Tables | Description | Rationale |
|---------|------------|------------|-------------|-----------|
| Primary | reg_eurusd, agg_eurusd, mom_eurusd, vol_eurusd, align_eurusd, lag_eurusd, regime_eurusd | reg_bqx_eurusd, agg_bqx_eurusd, mom_bqx_eurusd, vol_bqx_eurusd, align_bqx_eurusd, lag_bqx_eurusd, regime_bqx_eurusd | Pair-specific features | Direct pair dynamics |
| Variant | var_*_eur, var_*_usd | var_*_bqx_eur, var_*_bqx_usd | Currency family features | EUR and USD behavior across all pairs |
| Covariant | cov_*_eurusd_* | cov_*_bqx_eurusd_* | Cross-pair relationships | How EURUSD relates to other pairs |
| Triangulation | tri_*_eur_usd_* | tri_*_bqx_eur_usd_* | Arbitrage triangles | EUR-USD-X triangle dynamics |
| Secondary | csi_*_eur, csi_*_usd | csi_*_bqx_eur, csi_*_bqx_usd | Currency strength indices | Overall EUR and USD strength |
| Tertiary | mkt_* | mkt_*_bqx | Global market features | Market-wide conditions |

**Total per centric**: Include BOTH IDX and BQX variants for comprehensive coverage.

**Rationale for 6 Centrics**:
- Primary captures pair-specific dynamics
- Variant captures currency family patterns (e.g., EUR behavior across EURUSD, EURGBP, EURJPY)
- Covariant captures cross-pair relationships (e.g., EURUSD vs GBPUSD correlation)
- Triangulation captures arbitrage opportunities (e.g., EUR→USD→JPY→EUR)
- Secondary captures overall currency strength
- Tertiary captures global market conditions

---

## DETAILED IMPLEMENTATION STEPS

### Step 1: Identify All Feature Tables for EURUSD

Query to get all relevant tables:
```sql
-- PRIMARY (pair-specific)
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE '%_eurusd' OR table_id LIKE '%_bqx_eurusd'

-- VARIANT (currency family)
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'var_%_eur' OR table_id LIKE 'var_%_bqx_eur'
   OR table_id LIKE 'var_%_usd' OR table_id LIKE 'var_%_bqx_usd'

-- COVARIANT (cross-pair)
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'cov_%_eurusd_%' OR table_id LIKE 'cov_%_bqx_eurusd_%'

-- TRIANGULATION
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'tri_%' AND (table_id LIKE '%eur%' OR table_id LIKE '%usd%')

-- SECONDARY (CSI)
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'csi_%_eur' OR table_id LIKE 'csi_%_bqx_eur'
   OR table_id LIKE 'csi_%_usd' OR table_id LIKE 'csi_%_bqx_usd'

-- TERTIARY (market-wide)
SELECT table_id FROM `bqx-ml.bqx_ml_v3_features.__TABLES__`
WHERE table_id LIKE 'mkt_%'
```

### Step 2: Create Target Table with LEAD Values

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.targets_eurusd` AS
SELECT
  interval_time,
  pair,
  -- Current BQX values (for reference only)
  bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880,

  -- TARGETS: bqx_45 at each horizon
  LEAD(bqx_45, 15) OVER w AS target_bqx45_h15,
  LEAD(bqx_45, 30) OVER w AS target_bqx45_h30,
  LEAD(bqx_45, 45) OVER w AS target_bqx45_h45,
  LEAD(bqx_45, 60) OVER w AS target_bqx45_h60,
  LEAD(bqx_45, 75) OVER w AS target_bqx45_h75,
  LEAD(bqx_45, 90) OVER w AS target_bqx45_h90,
  LEAD(bqx_45, 105) OVER w AS target_bqx45_h105,

  -- TARGETS: bqx_90 at each horizon
  LEAD(bqx_90, 15) OVER w AS target_bqx90_h15,
  LEAD(bqx_90, 30) OVER w AS target_bqx90_h30,
  LEAD(bqx_90, 45) OVER w AS target_bqx90_h45,
  LEAD(bqx_90, 60) OVER w AS target_bqx90_h60,
  LEAD(bqx_90, 75) OVER w AS target_bqx90_h75,
  LEAD(bqx_90, 90) OVER w AS target_bqx90_h90,
  LEAD(bqx_90, 105) OVER w AS target_bqx90_h105,

  -- Continue for bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
  -- (7 BQX × 7 horizons = 49 target columns total)
  ...

FROM `bqx-ml.bqx_ml_v3_features.eurusd_bqx`
WHERE pair = 'EURUSD'
WINDOW w AS (ORDER BY interval_time)
```

### Step 3: Calculate Correlations for Each Feature Table

For each feature table, correlate all numeric columns against all 49 targets:

```sql
-- Example for reg_eurusd table against target_bqx45_h15
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h15` AS
WITH feature_correlations AS (
  SELECT
    'reg_eurusd' AS feature_table,
    'PRIMARY' AS centric,
    'IDX' AS variant,
    'reg_mean_45' AS feature_name,
    CORR(f.reg_mean_45, t.target_bqx45_h15) AS correlation
  FROM `bqx-ml.bqx_ml_v3_analytics.targets_eurusd` t
  JOIN `bqx-ml.bqx_ml_v3_features.reg_eurusd` f
    ON t.interval_time = f.interval_time
  WHERE t.target_bqx45_h15 IS NOT NULL

  UNION ALL

  SELECT
    'reg_eurusd' AS feature_table,
    'PRIMARY' AS centric,
    'IDX' AS variant,
    'reg_std_45' AS feature_name,
    CORR(f.reg_std_45, t.target_bqx45_h15) AS correlation
  FROM `bqx-ml.bqx_ml_v3_analytics.targets_eurusd` t
  JOIN `bqx-ml.bqx_ml_v3_features.reg_eurusd` f
    ON t.interval_time = f.interval_time
  WHERE t.target_bqx45_h15 IS NOT NULL

  -- Continue for all feature columns...
  -- Include reg_bqx_eurusd (BQX variant)
  -- Include all other tables from all 6 centrics
)
SELECT
  feature_table,
  centric,
  variant,
  feature_name,
  correlation,
  ABS(correlation) AS abs_correlation,
  ROW_NUMBER() OVER (ORDER BY ABS(correlation) DESC) AS rank
FROM feature_correlations
WHERE correlation IS NOT NULL
ORDER BY abs_correlation DESC
```

### Step 4: Repeat for All 49 Targets
Create one correlation table per target:
```
bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h15
bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h30
bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h45
...
bqx_ml_v3_analytics.target_corr_eurusd_bqx2880_h105
(49 tables total for EURUSD pilot)
```

### Step 5: Generate Summary Report

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_analytics.feature_correlation_summary_eurusd` AS
SELECT
  feature_table,
  centric,
  variant,
  feature_name,
  AVG(abs_correlation) AS avg_abs_correlation,
  MAX(abs_correlation) AS max_abs_correlation,
  MIN(abs_correlation) AS min_abs_correlation,
  COUNT(*) AS targets_count,
  COUNTIF(abs_correlation > 0.3) AS strong_correlations,
  COUNTIF(abs_correlation > 0.5) AS very_strong_correlations
FROM (
  SELECT * FROM `bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h15`
  UNION ALL SELECT * FROM `bqx_ml_v3_analytics.target_corr_eurusd_bqx45_h30`
  -- UNION ALL for all 49 target tables
)
GROUP BY feature_table, centric, variant, feature_name
ORDER BY avg_abs_correlation DESC
```

---

## OUTPUT FORMAT

### Per-Target Correlation Table Schema
| Column | Type | Description |
|--------|------|-------------|
| feature_table | STRING | Source table (e.g., reg_eurusd, reg_bqx_eurusd) |
| centric | STRING | PRIMARY / VARIANT / COVARIANT / TRIANGULATION / SECONDARY / TERTIARY |
| variant | STRING | IDX or BQX |
| feature_name | STRING | Name of the feature column |
| correlation | FLOAT64 | Pearson correlation with target (-1 to +1) |
| abs_correlation | FLOAT64 | Absolute correlation (for ranking) |
| rank | INT64 | Rank by abs_correlation (1 = highest) |

### Summary Table Schema
| Column | Type | Description |
|--------|------|-------------|
| feature_table | STRING | Source table |
| centric | STRING | Centric classification |
| variant | STRING | IDX or BQX |
| feature_name | STRING | Feature column name |
| avg_abs_correlation | FLOAT64 | Average absolute correlation across all targets |
| max_abs_correlation | FLOAT64 | Maximum absolute correlation |
| min_abs_correlation | FLOAT64 | Minimum absolute correlation |
| targets_count | INT64 | Number of targets (should be 49) |
| strong_correlations | INT64 | Count of targets with |corr| > 0.3 |
| very_strong_correlations | INT64 | Count of targets with |corr| > 0.5 |

---

## EXPECTED OUTCOMES

### What Good Results Look Like
- Top features should have avg_abs_correlation > 0.2
- Different BQX components may favor different features
- Shorter horizons (H15, H30) may have higher correlations than longer horizons
- BQX variant features may correlate differently than IDX variant features

### Red Flags to Watch For
- All correlations near zero → Data issue or misaligned intervals
- All correlations near 1.0 → Data leakage (target info in features)
- Many NULL correlations → Missing data or join issues
- Only one centric showing correlations → Other centrics may have join issues

---

## MANDATE COMPLIANCE

- **BQX_PARADIGM:** ALL bqx_* components as targets ✓
- **DATA_LEAKAGE_PREVENTION:** Features=current values, Targets=LEAD (future values) ✓
- **PERFORMANCE_FIRST:** ALL 8 feature types × ALL 6 centrics × BOTH variants ✓
- **INTERVAL_CENTRIC:** Row-based LEAD operations, no time references ✓
- **DUAL_VARIANT:** Both IDX and BQX feature tables included ✓

---

## DELIVERABLES

1. **Target table**: `bqx_ml_v3_analytics.targets_eurusd` (49 target columns)
2. **49 correlation tables**: `bqx_ml_v3_analytics.target_corr_eurusd_bqx{X}_h{Y}`
3. **Summary table**: `bqx_ml_v3_analytics.feature_correlation_summary_eurusd`
4. **Report**: Top 50 features per target, top 100 features overall
5. **STOP**: Await CE/User approval before scaling to all 28 pairs

---

## QUESTIONS?

If any clarification needed, report back BEFORE proceeding.

Key questions to consider:
- Are all 6 centrics correctly identified for EURUSD?
- Are BOTH IDX and BQX variants included for each feature type?
- Is the interval_time join working correctly across all tables?

---

Chief Engineer (CE)
