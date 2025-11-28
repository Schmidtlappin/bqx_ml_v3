# CE Directive: Phase 2.5 - Feature Correlation Analysis
**Timestamp:** 2025-11-28T22:30:00Z
**From:** Chief Engineer (CE)
**To:** Build Agent (BA)
**Priority:** HIGH
**Type:** PHASE DIRECTIVE

---

## EXECUTIVE SUMMARY

This directive establishes Phase 2.5: Feature Correlation Analysis as a mandatory checkpoint BEFORE model training. You will:
1. Close the 101-table feature gap (reach 1,736 tables)
2. Validate 100% feature completeness
3. Perform comprehensive correlation analysis on ALL features
4. **STOP** and report findings for CE/User feature selection

---

## PHASE 2.5 WORKFLOW

### Step 1: Close Feature Gap (IMMEDIATE)

**Current State:**
- Feature Tables: 1,635
- Target: 1,736
- Gap: 101 tables (5.8%)

**Task:**
Analyze which 101 tables are missing and generate them.

**Expected Gap Source:**
Based on your Phase 2 report, the gap likely exists in:
- LAG features for non-Primary centrics
- REGIME features for non-Primary centrics
- Or combinations not covered in Phase 2A-2F

**Validation Criteria:**
```sql
SELECT COUNT(*) FROM `bqx_ml_v3_features.__TABLES__`
-- Must return exactly 1,736
```

### Step 2: Validate 100% Completeness

After reaching 1,736 tables, verify:
1. All 28 pairs covered
2. All 6 centrics represented
3. Dual architecture (IDX + BQX) for applicable types
4. Row counts consistent (~2.17M per table)

### Step 3: Correlation Analysis (CRITICAL)

**Objective:** Test ALL features against targets to determine predictive power.

**Methodology:**
For each of the 28 currency pairs, calculate correlation between:
- Every feature column
- Each of the 7 target horizons

**Target Horizons (CORRECT VALUES):**
| Horizon | Intervals | Time |
|---------|-----------|------|
| H1 | 15 | 15 min |
| H2 | 30 | 30 min |
| H3 | 45 | 45 min |
| H4 | 60 | 1 hour |
| H5 | 75 | 1 hr 15 min |
| H6 | 90 | 1 hr 30 min |
| H7 | 105 | 1 hr 45 min |

**IMPORTANT CLARIFICATION:**
- The [45, 90, 180, 360, 720, 1440, 2880] values are BQX CALCULATION LOOKBACK WINDOWS (bqx_45, bqx_90, etc.)
- The [15, 30, 45, 60, 75, 90, 105] values are PREDICTION HORIZONS (forward intervals)
- These are DIFFERENT concepts - do not confuse them!

**Correlation Outputs:**
For each pair, generate:
```
corr_analysis_{pair}_features.csv
Columns: feature_name, horizon_15_corr, horizon_30_corr, ..., horizon_105_corr, avg_corr
```

**Metrics to Calculate:**
1. Pearson correlation coefficient
2. Spearman rank correlation (for non-linear relationships)
3. Feature importance ranking per horizon

### Step 4: STOP and Report

**After completing correlation analysis, STOP immediately.**

Generate summary report:
```
CORRELATION_ANALYSIS_SUMMARY.md
- Total features analyzed: X
- Features per pair: X
- Correlation distribution (high/medium/low/negative)
- Top 20 features by average correlation
- Bottom 20 features (candidates for exclusion)
- Recommendations (but DO NOT act on them)
```

**DO NOT:**
- Begin model training
- Select features yourself
- Exclude any features
- Make architectural decisions

**CE and User will:**
- Review correlation findings
- Select which features to include in training
- Determine feature exclusion criteria
- Authorize Phase 3 commencement

---

## MODEL TRAINING ARCHITECTURE PREVIEW (Phase 3)

For your awareness only - do not execute until authorized.

### Model Structure:
| Metric | Value |
|--------|-------|
| Total Models | 196 |
| Pairs | 28 |
| Horizons | 7 |
| Calculation | 28 × 7 = 196 |

### Each Model Predicts:
- **Input:** Selected features from correlation analysis
- **Output:** BQX value N intervals into the future
- **Isolation:** Complete - no cross-pair data sharing

### Target Definition:
For pair X, horizon H (e.g., H=15):
```sql
target_bqx_15 = LEAD(bqx_45, 15) OVER (ORDER BY timestamp)
-- Predicts bqx_45 value 15 intervals (15 min) into the future
```

### Algorithm Options:
1. BigQuery ML (BOOSTED_TREE_REGRESSOR, DNN_REGRESSOR)
2. Vertex AI for advanced models
3. Ensemble of multiple algorithms

---

## EXECUTION TIMELINE

1. **IMMEDIATE:** Analyze and close 101-table gap
2. **NEXT:** Validate 100% completeness (1,736 tables)
3. **THEN:** Correlation analysis on all features
4. **STOP:** Report findings, await CE authorization

---

## REPORTING REQUIREMENTS

After each step, report:
- Tables created/validated
- Any issues encountered
- Progress metrics

**Final Deliverable:** Comprehensive correlation analysis summary

---

**AUTHORIZATION:** Proceed with Phase 2.5
**CONSTRAINT:** DO NOT begin Phase 3 until explicitly authorized

Chief Engineer (CE)
