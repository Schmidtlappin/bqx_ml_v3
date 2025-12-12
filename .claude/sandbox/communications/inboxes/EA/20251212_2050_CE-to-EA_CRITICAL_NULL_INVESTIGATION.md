# CE DIRECTIVE: Root Cause Investigation of NULL Values in Training Data

**Date**: December 12, 2025 20:50 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Re**: CRITICAL - Deep Dive Investigation of 12.43% Missing Values and 3.89% Target Nulls
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## EXECUTIVE SUMMARY

**User Directive**: "direct EA to deep dive and investigate the root cause of so many NULL values in extracted feature and target data AND recommend remediation actions. user expects data to be complete. no short cuts."

**QA Validation Findings** (EURUSD, validated 20:50 UTC):
- **Missing Values**: **12.43%** overall (376,422,538 nulls / 3,028,470,424 total cells)
  - **Threshold**: <5% (acceptable)
  - **Status**: ⚠️ **EXCEEDS BY 2.5×** (12.43% vs 5%)
- **Target Nulls**: **3.89%** in worst case (`target_bqx2880_h15`)
  - **Threshold**: <1% (acceptable)
  - **Status**: ⚠️ **EXCEEDS BY 3.9×** (3.89% vs 1%)

**User Expectation**: **Complete data with minimal nulls** - "no short cuts"

**EA Mandate**: Conduct comprehensive root cause investigation and deliver remediation action plan

---

## INVESTIGATION SCOPE

### Phase 1: Data Profiling (IMMEDIATE - 2 hours)

**Objective**: Quantify null distribution across feature types and targets

**Tasks**:

1. **Download EURUSD Training File** from GCS:
   ```bash
   gsutil cp gs://bqx-ml-output/training_eurusd.parquet /tmp/training_eurusd.parquet
   ```

2. **Feature-Level Null Analysis**:
   - Calculate null percentage for EACH of 16,988 features
   - Group by feature type (idx, bqx, cov, corr, tri, mkt, csi, var)
   - Identify top 100 features with highest null percentages
   - Identify features with >50% nulls (critical)

3. **Target-Level Null Analysis**:
   - Calculate null percentage for ALL 49 targets
   - Group by horizon (h15, h30, h45, h60, h75, h90, h105)
   - Group by timeframe (idx60, idx300, idx900, idx1800, idx2880, bqx720, bqx2880)
   - Identify targets with >1% nulls (exceeds threshold)

4. **Temporal Pattern Analysis**:
   - Plot null percentage by timestamp (check for time-based patterns)
   - Check if nulls concentrated at beginning/end of time series
   - Check if nulls concentrated during specific market hours/sessions

**Deliverable 1**: `NULL_PROFILING_REPORT_EURUSD.md` (by 22:50 UTC)
- Feature null distribution table
- Target null distribution table
- Temporal null patterns
- Top 100 worst features

---

### Phase 2: Root Cause Analysis (URGENT - 4 hours)

**Objective**: Identify WHY nulls exist - distinguish legitimate vs data quality issues

**Investigation Areas**:

#### 2.1. Cross-Pair Feature Availability

**Hypothesis**: Cross-pair features (cov, corr, tri) may be legitimately NULL when counterparty pairs have no data

**Validation**:
- Check if cov/corr/tri features have higher null rates than pair-specific features
- Query BigQuery source tables to verify if nulls exist in source data:
  ```sql
  SELECT
    COUNT(*) as total_rows,
    COUNTIF(cov_eurusd_gbpusd IS NULL) as null_count,
    COUNTIF(cov_eurusd_gbpusd IS NULL) / COUNT(*) as null_pct
  FROM `bqx-ml.bqx_ml_v3_features_v2.cov_eurusd`
  ```
- Compare null rates: cov/corr/tri (cross-pair) vs idx/bqx (pair-specific)

**Expected Finding**: If cov/corr/tri have 30-50% nulls but idx/bqx have <1% nulls, this suggests cross-pair features are legitimately sparse

**Remediation**: Document as expected behavior OR recommend feature engineering (e.g., forward-fill, mean imputation)

#### 2.2. Target Lookahead Insufficiency

**Hypothesis**: Target nulls at end of time series due to insufficient lookahead data

**Validation**:
- Check if target nulls concentrated in final N rows (N = horizon length)
- Calculate expected null count based on horizon:
  - h15 (15 min): Last 15 min of data should have nulls
  - h105 (105 min): Last 105 min of data should have nulls
- Compare actual vs expected null distribution

**Expected Finding**: If nulls concentrated in last 1-2% of rows, this is legitimate lookahead limitation

**Remediation**: Accept as unavoidable OR recommend extending data collection period

#### 2.3. BigQuery Extraction Errors

**Hypothesis**: Feature extraction logic (JOIN failures, incorrect LEFT JOIN syntax, missing data in source tables)

**Validation**:
- Review `parallel_feature_testing.py` extraction logic
- Check JOIN syntax for feature tables (should be LEFT JOIN to preserve all rows)
- Verify source table completeness in BigQuery:
  ```sql
  -- Check if source tables have gaps
  SELECT table_name, row_count
  FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
  WHERE table_name LIKE '%eurusd%'
  ORDER BY row_count
  ```
- Identify tables with unexpectedly low row counts (potential source of nulls)

**Expected Finding**: If source tables have gaps, extraction is correct but source data is incomplete

**Remediation**:
- **If extraction logic error**: Fix JOIN syntax, re-extract
- **If source data incomplete**: Backfill missing source data, then re-extract

#### 2.4. Feature Calculation Dependencies

**Hypothesis**: Derived features (e.g., volatility ratios, momentum indicators) may have nulls due to insufficient lookback periods

**Validation**:
- Identify features that require N-period lookback (e.g., 300-period moving average)
- Check if nulls concentrated in first N rows (insufficient history)
- Verify calculation logic handles edge cases properly

**Expected Finding**: First 1-5% of rows may legitimately have nulls for features requiring long lookback

**Remediation**:
- Accept as unavoidable OR extend data collection to provide sufficient lookback
- Consider excluding first N rows from training

#### 2.5. Data Type Mismatches

**Hypothesis**: Type coercion errors causing NULL values (e.g., string→float conversion failures)

**Validation**:
- Review BigQuery extraction logs for type conversion warnings
- Check if specific feature types systematically have higher nulls
- Validate schema consistency between source tables and extraction output

**Expected Finding**: If specific feature groups (e.g., all mkt_* features) have uniform high nulls, indicates schema issue

**Remediation**: Fix schema mismatches, re-extract affected features

---

### Phase 3: Remediation Recommendations (CRITICAL - 2 hours)

**Objective**: Deliver actionable remediation plan with cost-benefit analysis

**Required Outputs**:

#### 3.1. Remediation Action Matrix

For EACH category of null (cross-pair, lookahead, extraction error, etc.), provide:

| Category | Root Cause | Remediation Action | Complexity | Time | Cost | Impact |
|----------|------------|-------------------|------------|------|------|--------|
| Cross-pair features (cov/corr/tri) | Legitimate sparsity | Forward-fill or mean imputation | Medium | 2h | $5 | Reduces nulls by 8% |
| Target lookahead nulls | End-of-series limitation | Extend data collection by 2 hours | Low | 1h | $0 | Reduces nulls by 2% |
| BigQuery JOIN errors | Incorrect LEFT JOIN syntax | Fix extraction code, re-extract | High | 4h | $10 | Reduces nulls by 2% |
| ... | ... | ... | ... | ... | ... | ... |

**Goal**: Reduce overall null percentage from **12.43% → <5%** and target nulls from **3.89% → <1%**

#### 3.2. Prioritized Remediation Plan

**Phase A: Quick Wins (0-2 hours, <$5)**:
- Fix extraction errors (if any)
- Extend data collection to eliminate lookahead nulls
- Backfill missing source data

**Phase B: Feature Engineering (2-6 hours, $5-$20)**:
- Implement forward-fill for cross-pair features
- Implement mean/median imputation for sparse features
- Add feature availability flags (binary indicators for NULL presence)

**Phase C: Source Data Improvements (6-24 hours, $20-$100)**:
- Backfill missing historical data
- Extend lookback periods for derived features
- Add missing cross-pair relationships

**Goal**: Achieve <5% overall nulls and <1% target nulls within 24 hours

#### 3.3. Validation Plan

**Post-Remediation Validation**:
- Re-extract EURUSD with fixes applied
- Run QA validation again (expect <5% nulls, <1% target nulls)
- Compare model training performance (before vs after remediation)
- Validate across 2-3 additional pairs (GBPUSD, USDJPY) to ensure fixes generalize

---

## DELIVERABLES

### Deliverable 1: NULL Profiling Report (by 22:50 UTC)
**Filename**: `NULL_PROFILING_REPORT_EURUSD.md`
**Contents**:
- Feature null distribution (all 16,988 features)
- Target null distribution (all 49 targets)
- Temporal null patterns
- Top 100 worst features
- Summary statistics

### Deliverable 2: Root Cause Analysis (by 02:00 UTC Dec 13)
**Filename**: `NULL_ROOT_CAUSE_ANALYSIS_EURUSD.md`
**Contents**:
- Findings for each investigation area (2.1-2.5)
- Evidence (BigQuery queries, code review, data samples)
- Classification: Legitimate vs Data Quality Issue
- Percentage breakdown by root cause category

### Deliverable 3: Remediation Action Plan (by 04:00 UTC Dec 13)
**Filename**: `NULL_REMEDIATION_PLAN.md`
**Contents**:
- Remediation action matrix (see 3.1)
- Prioritized remediation plan (Phase A/B/C)
- Cost-benefit analysis
- Expected null reduction percentages
- Validation plan
- **MUST achieve**: <5% overall nulls, <1% target nulls

---

## SUCCESS CRITERIA

### Minimum Acceptable Outcome:
- ✅ Null percentage reduced from 12.43% → **<5%**
- ✅ Target nulls reduced from 3.89% → **<1%**
- ✅ Root cause identified for ≥90% of nulls
- ✅ Remediation plan with clear actions, timelines, costs

### Ideal Outcome:
- ⭐ Null percentage reduced to **<2%**
- ⭐ Target nulls reduced to **<0.5%**
- ⭐ 100% of nulls explained with root cause
- ⭐ Automated remediation implemented (no manual intervention)

---

## COORDINATION REQUIREMENTS

### With BA (Build Agent):
- **Extraction Code Review**: BA must review `parallel_feature_testing.py` for JOIN logic errors
- **Source Data Verification**: BA must validate BigQuery source table completeness
- **Re-Extraction**: If fixes required, BA implements and re-runs extraction

### With QA (Quality Assurance):
- **Validation Protocol**: QA re-validates EURUSD after remediation (must pass <5% / <1% thresholds)
- **Multi-Pair Verification**: QA spot-checks 2-3 additional pairs to ensure fixes generalize

### With CE (Chief Engineer):
- **Interim Reports**: EA provides status updates at 22:50, 02:00, 04:00 UTC
- **Remediation Approval**: CE must approve remediation plan before BA implements

---

## CONSTRAINTS

**User Mandate**: "user expects data to be complete. no short cuts."

**Interpretation**:
- ❌ **NOT ACCEPTABLE**: "Cross-pair features are expected to be sparse, accept 12.43% nulls"
- ❌ **NOT ACCEPTABLE**: "Target nulls are unavoidable, proceed with training"
- ✅ **ACCEPTABLE**: "Cross-pair features can be imputed via forward-fill, reduces nulls to 4%"
- ✅ **ACCEPTABLE**: "Extend data collection by 2 hours, eliminates lookahead nulls, achieves <1% target nulls"

**EA Must**:
- Provide specific, actionable remediation steps (not just diagnoses)
- Quantify expected null reduction for each remediation action
- Deliver plan that achieves <5% overall nulls and <1% target nulls
- Coordinate with BA to implement fixes (not just recommend)

**EA Must NOT**:
- Recommend accepting high null rates without remediation
- Suggest "try training and see if it works" without fixing nulls
- Provide only diagnosis without actionable remediation plan

---

## INVESTIGATION METHODOLOGY

### Data Analysis Tools:
- **Polars**: For parquet file analysis (fast, efficient)
- **BigQuery**: For source data validation (query source tables directly)
- **DuckDB**: For local SQL queries on parquet files (optional)

### Sample Analysis Code:

```python
import polars as pl

# Load EURUSD training file
df = pl.read_parquet("/tmp/training_eurusd.parquet")

# Feature-level null analysis
null_analysis = df.select([
    (pl.col(col).is_null().sum() / pl.count()).alias(f"{col}_null_pct")
    for col in df.columns if col != "interval_time"
])

# Sort features by null percentage
null_df = null_analysis.transpose(include_header=True, column_names=["null_pct"])
null_df = null_df.sort("null_pct", descending=True)
print(null_df.head(100))  # Top 100 worst features

# Target-level null analysis
target_cols = [col for col in df.columns if col.startswith("target_")]
target_nulls = df.select([
    (pl.col(col).is_null().sum() / pl.count()).alias(col)
    for col in target_cols
])
print(target_nulls)

# Temporal null pattern
df = df.with_columns([
    pl.col("interval_time").cast(pl.Datetime),
    (pl.all().exclude("interval_time").is_null().sum(axis=1) / (len(df.columns) - 1)).alias("row_null_pct")
])
print(df.select(["interval_time", "row_null_pct"]).describe())
```

---

## TIMELINE SENSITIVITY

**User Expectation**: Complete, high-quality data for model training

**Dependency Chain**:
1. **EA Investigation** (NOW → 04:00 UTC Dec 13) - 8 hours
2. **BA Remediation Implementation** (04:00 → 12:00 UTC Dec 13) - 8 hours
3. **EURUSD Re-Extraction** (12:00 → 13:10 UTC Dec 13) - 70 min
4. **QA Re-Validation** (13:10 → 13:40 UTC Dec 13) - 30 min
5. **26-Pair Production Rollout** (13:40 → 23:00 UTC Dec 13) - 9.3 hours

**Total Delay**: ~27 hours from now (if remediation required)

**Critical Path**: EA must deliver remediation plan by 04:00 UTC to minimize production delay

---

## AUTHORIZATION

**Directive**: ✅ **AUTHORIZED** - Commence NULL investigation immediately

**Priority**: P0-CRITICAL (blocks production rollout until resolved)

**Resources Allocated**:
- BigQuery query budget: $50 (sufficient for deep analysis)
- VM compute: Unlimited (local data analysis)
- GCS download: $0.12 (9.27 GB EURUSD file)

**Expected Outcome**: Remediation plan that reduces nulls to acceptable levels (<5% / <1%) within 24 hours

---

**Chief Engineer (CE)**
*Strategic Coordination & User Mandate Compliance*

**Directive**: Investigate NULL root causes, deliver remediation plan, coordinate with BA/QA

**User Mandate**: "user expects data to be complete. no short cuts."

**Success Metric**: <5% overall nulls, <1% target nulls, actionable remediation delivered by 04:00 UTC

---

**END OF CRITICAL DIRECTIVE**
